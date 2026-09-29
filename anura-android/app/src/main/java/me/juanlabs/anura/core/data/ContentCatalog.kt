package me.juanlabs.anura.core.data

import android.content.Context
import android.graphics.BitmapFactory
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.produceState
import androidx.compose.runtime.setValue
import androidx.compose.ui.graphics.ImageBitmap
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.graphics.painter.BitmapPainter
import androidx.compose.ui.graphics.painter.Painter
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import kotlinx.coroutines.withContext
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json
import me.juanlabs.anura.R
import me.juanlabs.anura.core.auth.AnuraServerConfig
import me.juanlabs.anura.core.platform.rememberPhotoPlaceholderPainter
import java.io.File
import java.net.HttpURLConnection
import java.net.URL
import java.security.MessageDigest

/**
 * Catálogo de contenido publicado: las fichas que el herpetólogo aprobó en Admin → Contenido y
 * los destacados del carrusel de inicio. Es la ÚNICA fuente de especies de la app — el APK no
 * trae ninguna especie, foto ni nombre de respaldo. Lo sirve dataset-service en
 * `/api/dataset/publico/catalogo`, sin sesión, con solo la copia publicada y solo fotos con
 * licencia CC.
 *
 * - Se guarda en `filesDir/content/catalogo.json` y las fotos en `filesDir/content/fotos/`:
 *   después de la primera sincronización las fichas, el carrusel y Explorar funcionan sin red.
 *   Nada de esto vive en `cacheDir` (el sistema lo puede vaciar y la app quedaría sin fotos
 *   en el campo).
 * - Sin catálogo guardado y sin servidor, la app no inventa nada: las pantallas muestran
 *   «Conéctate para cargar las especies» ([availability]).
 * - Si el servidor borra especies, el catálogo nuevo las quita también del teléfono (y sus fotos
 *   se borran del disco en la siguiente sincronización).
 * - La URL del servidor es una preferencia, no una constante (19_ADMIN/Plan del Backend Real,
 *   L1). Sin preferencia se prueba el puerto de dataset-service en 127.0.0.1 (teléfono por USB
 *   con `adb reverse tcp:3008 tcp:3008`) y después el dominio público.
 * - K2: antes de aceptar un catálogo nuevo se verifica su manifiesto (`/publico/manifiesto`):
 *   firma Ed25519 con la clave del canal ([ContentManifestVerifier]) y que el sha256 de lo
 *   descargado sea el mismo que el manifiesto firmó. Si algo no cuadra, se descarta y se sigue
 *   con el catálogo que ya había (nunca a medias ni sin verificar).
 * - Se sincroniza al abrir la app (MainActivity) y en segundo plano con [ContentSyncWorker].
 */
object ContentCatalog {
    private const val Prefs = "anura_server"
    private const val PrefBaseUrl = "content_base_url"
    private val DefaultBaseUrls = listOf("http://127.0.0.1:3008", AnuraServerConfig.AUTH_BASE_URL)
    private const val CatalogPath = "/api/dataset/publico/catalogo"
    private const val ManifestPath = "/api/dataset/publico/manifiesto"

    /** Ancho de las miniaturas (tarjetas de 2 columnas, similares, menciones). */
    const val ThumbWidth = 640

    /** Ancho de la foto grande (carrusel de inicio, ficha, visor). */
    const val FullWidth = 1080

    // coerceInputValues: un campo nuevo o nulo en el servidor no tumba todo el catálogo.
    private val json = Json {
        ignoreUnknownKeys = true
        coerceInputValues = true
    }
    private val syncLock = Mutex()

    /** Estado observable: leerlo dentro de un @Composable recompone cuando llega un catálogo nuevo. */
    var catalog by mutableStateOf<PublishedCatalog?>(null)
        private set

    /** Servidor que respondió la última vez (para armar las URLs de fotos). */
    var baseUrl by mutableStateOf<String?>(null)
        private set

    /** Resultado de la última sincronización; con [catalog] decide qué estado vacío mostrar. */
    var syncState by mutableStateOf(CatalogSyncState.NotStarted)
        private set

    fun byTaxonId(taxonId: String): PublishedSpecies? = catalog?.especies?.firstOrNull { it.taxon_id == taxonId }

    fun byScientificName(name: String): PublishedSpecies? =
        catalog?.especies?.firstOrNull { it.nombre_cientifico.equals(name, ignoreCase = true) }

    /** Qué puede mostrar la app ahora mismo. Nunca "listo" con especies que no vinieron del servidor. */
    val availability: CatalogAvailability
        get() {
            val current = catalog
            if (current != null) {
                return if (current.especies.isEmpty()) CatalogAvailability.Empty else CatalogAvailability.Ready
            }
            return when (syncState) {
                CatalogSyncState.Offline -> CatalogAvailability.NoConnection
                CatalogSyncState.Unverified -> CatalogAvailability.Unverified
                CatalogSyncState.NotStarted, CatalogSyncState.Syncing, CatalogSyncState.UpToDate -> CatalogAvailability.Loading
            }
        }

    fun setBaseUrl(context: Context, url: String?) {
        context.getSharedPreferences(Prefs, Context.MODE_PRIVATE).edit().apply {
            if (url.isNullOrBlank()) remove(PrefBaseUrl) else putString(PrefBaseUrl, url.trimEnd('/'))
        }.apply()
    }

    private fun candidates(context: Context): List<String> {
        val pref = context.getSharedPreferences(Prefs, Context.MODE_PRIVATE).getString(PrefBaseUrl, null)
        return listOfNotNull(pref) + DefaultBaseUrls
    }

    private fun cacheFile(context: Context) = File(context.filesDir, "content/catalogo.json")

    private fun photoDir(context: Context) = File(context.filesDir, "content/fotos")

    private fun photoFile(context: Context, sha256: String, width: Int) = File(photoDir(context), "${sha256}_$width.jpg")

    /** Lo guardado en el teléfono de una sincronización anterior. El APK no trae catálogo. */
    suspend fun loadLocal(context: Context) = withContext(Dispatchers.IO) {
        val cached = cacheFile(context).takeIf { it.exists() }?.readText()?.let { parse(it) }
        if (cached != null) {
            withContext(Dispatchers.Main) {
                if (catalog == null) catalog = cached
                if (baseUrl == null) baseUrl = cached.servidor
            }
        }
    }

    /**
     * Lo que hacen la app al abrirse y [ContentSyncWorker]: lo guardado primero (si todavía no se
     * leyó), luego el servidor, y por último las fotos que falten en disco. Seguro de llamar
     * varias veces a la vez: un solo recorrido corre en cada momento.
     */
    suspend fun sync(context: Context) {
        if (catalog == null) loadLocal(context)
        refresh(context)
        prefetchPhotos(context)
    }

    /**
     * Pide el manifiesto al primer servidor que responda; si trae una versión nueva, verifica su
     * firma, baja el catálogo y comprueba que su sha256 sea el que el manifiesto firmó — recién
     * ahí lo acepta. Devuelve true si hubo un catálogo nuevo (verificado) de verdad.
     */
    suspend fun refresh(context: Context): Boolean = syncLock.withLock {
        withContext(Dispatchers.Main) { syncState = CatalogSyncState.Syncing }
        val (result, accepted) = withContext(Dispatchers.IO) { fetchVerifiedCatalog(context) }
        withContext(Dispatchers.Main) { syncState = result }
        accepted
    }

    /** (estado final, true si se aceptó un catálogo nuevo). */
    private suspend fun fetchVerifiedCatalog(context: Context): Pair<CatalogSyncState, Boolean> {
        var reachedServer = false
        for (base in candidates(context)) {
            val manifiestoTexto = fetchText(base + ManifestPath) ?: continue
            reachedServer = true
            val manifiesto = runCatching { json.decodeFromString(ContentManifest.serializer(), manifiestoTexto) }.getOrNull() ?: continue
            withContext(Dispatchers.Main) { baseUrl = base }

            if (manifiesto.version == catalog?.version) return CatalogSyncState.UpToDate to false

            if (!ContentManifestVerifier.verificar(manifiesto.sha256.toByteArray(Charsets.US_ASCII), manifiesto.firma)) {
                // Firma inválida o ausente: nunca se usa un catálogo que no se pueda verificar.
                // El servidor sin CONTENT_MANIFEST_PRIVATE_KEY_B64 configurada cae aquí también
                // (a propósito: es preferible no actualizar a aceptar contenido sin firmar).
                continue
            }
            val cuerpo = fetchText(base + manifiesto.url) ?: continue
            if (sha256Hex(cuerpo) != manifiesto.sha256) continue // no es el texto que se firmó

            val parsed = parse(cuerpo)?.copy(servidor = base) ?: continue
            cacheFile(context).apply { parentFile?.mkdirs() }.writeText(cuerpo)
            withContext(Dispatchers.Main) {
                catalog = parsed
                baseUrl = base
            }
            return CatalogSyncState.UpToDate to true
        }
        return (if (reachedServer) CatalogSyncState.Unverified else CatalogSyncState.Offline) to false
    }

    /**
     * Baja a disco las fotos publicadas que falten (principal en los dos anchos que usa la app,
     * galería en el grande) y borra las que ya no están en el catálogo — así, lo que se ve con
     * red se sigue viendo sin red, y lo que el servidor quitó desaparece también del teléfono.
     */
    suspend fun prefetchPhotos(context: Context) = withContext(Dispatchers.IO) {
        val current = catalog ?: return@withContext
        val wanted = buildSet {
            current.especies.forEach { species ->
                species.foto_principal?.sha256?.let {
                    add(it to ThumbWidth)
                    add(it to FullWidth)
                }
                species.galeria.forEach { add(it.sha256 to FullWidth) }
            }
        }
        val keep = wanted.map { (sha, width) -> photoFile(context, sha, width).name }.toSet()
        photoDir(context).listFiles()?.forEach { file ->
            if (file.name !in keep) file.delete()
        }
        wanted.forEach { (sha, width) -> downloadPhoto(context, sha, width) }
    }

    private fun fetchText(url: String): String? = runCatching {
        val conn = (URL(url).openConnection() as HttpURLConnection).apply {
            connectTimeout = 2_500
            readTimeout = 8_000
        }
        try {
            if (conn.responseCode != HttpURLConnection.HTTP_OK) return null
            conn.inputStream.bufferedReader().use { it.readText() }
        } finally {
            conn.disconnect()
        }
    }.getOrNull()

    private fun sha256Hex(texto: String): String =
        MessageDigest.getInstance("SHA-256").digest(texto.toByteArray(Charsets.UTF_8)).joinToString("") { "%02x".format(it) }

    private fun parse(text: String): PublishedCatalog? =
        runCatching { json.decodeFromString(PublishedCatalog.serializer(), text) }.getOrNull()

    fun photoUrl(sha256: String, width: Int = FullWidth): String? =
        baseUrl?.let { "$it/api/dataset/publico/fotos/$sha256?ancho=$width" }

    /** Descarga una foto publicada si no está en disco. Devuelve el archivo, o null si no se pudo. */
    private fun downloadPhoto(context: Context, sha256: String, width: Int): File? {
        val file = photoFile(context, sha256, width)
        if (file.exists()) return file
        val url = photoUrl(sha256, width) ?: return null
        return runCatching {
            val conn = (URL(url).openConnection() as HttpURLConnection).apply {
                connectTimeout = 2_500
                readTimeout = 15_000
            }
            try {
                if (conn.responseCode != HttpURLConnection.HTTP_OK) return@runCatching null
                file.parentFile?.mkdirs()
                val tmp = File(file.parentFile, file.name + ".part")
                conn.inputStream.use { input -> tmp.outputStream().use { input.copyTo(it) } }
                if (tmp.renameTo(file)) file else null
            } finally {
                conn.disconnect()
            }
        }.getOrNull()
    }

    /** Foto publicada guardada en disco: una vez bajada, se ve sin red. */
    internal suspend fun loadPhoto(context: Context, sha256: String, width: Int): ImageBitmap? = withContext(Dispatchers.IO) {
        val file = downloadPhoto(context, sha256, width) ?: return@withContext null
        runCatching { BitmapFactory.decodeFile(file.path)?.asImageBitmap() }.getOrNull()
    }
}

/** Cómo terminó la última sincronización del catálogo. */
enum class CatalogSyncState {
    /** Todavía no se intentó en esta ejecución. */
    NotStarted,
    Syncing,

    /** El servidor respondió y el catálogo del teléfono es el vigente. */
    UpToDate,

    /** Ningún servidor respondió. */
    Offline,

    /** El servidor respondió, pero su catálogo no pasó la verificación de firma/sha256. */
    Unverified,
}

@Composable
fun catalogGapTitle(): String = stringResource(
    when (ContentCatalog.availability) {
        CatalogAvailability.Empty, CatalogAvailability.Ready -> R.string.catalog_empty_title
        CatalogAvailability.NoConnection, CatalogAvailability.Unverified -> R.string.catalog_offline_title
        CatalogAvailability.Loading -> R.string.catalog_loading_title
    },
)

@Composable
fun catalogGapBody(): String? = when (ContentCatalog.availability) {
    CatalogAvailability.Empty, CatalogAvailability.Ready -> stringResource(R.string.catalog_empty_body)
    CatalogAvailability.NoConnection, CatalogAvailability.Unverified -> stringResource(R.string.catalog_offline_body)
    CatalogAvailability.Loading -> null
}

/** Lo que la interfaz puede mostrar de especies en este momento. */
enum class CatalogAvailability {
    /** Hay especies publicadas (guardadas o recién bajadas). */
    Ready,

    /** El servidor no tiene ninguna especie publicada todavía. */
    Empty,

    /** Primera carga en curso, sin nada guardado. */
    Loading,

    /** Sin red y sin catálogo guardado. */
    NoConnection,

    /** Sin catálogo guardado y el del servidor no se pudo verificar. */
    Unverified,
}

/**
 * Foto publicada de una especie, bajada por su sha256 (con caché en disco). Mientras baja, o si la
 * especie no tiene foto publicada, se ve un hueco neutro: el APK no trae fotos de especies y una de
 * ejemplo haría pasar una especie por otra.
 */
@Composable
fun rememberSpeciesPhotoPainter(
    photoSha256: String?,
    width: Int = ContentCatalog.FullWidth,
): Painter {
    val placeholder = rememberPhotoPlaceholderPainter()
    if (photoSha256.isNullOrBlank()) return placeholder
    val context = LocalContext.current
    val bitmap by produceState<ImageBitmap?>(initialValue = null, photoSha256, width, ContentCatalog.baseUrl) {
        value = ContentCatalog.loadPhoto(context, photoSha256, width)
    }
    return bitmap?.let { BitmapPainter(it) } ?: placeholder
}

/** `GET /api/dataset/publico/manifiesto` — K2: manifest + sha256 + firma Ed25519. */
@Serializable
data class ContentManifest(
    val formato: Int = 1,
    val canal: String,
    val version: String,
    val sha256: String,
    val tamano: Int = 0,
    val generado: String? = null,
    val firma: String? = null,
    val url: String,
)

@Serializable
data class PublishedCatalog(
    val formato: Int = 1,
    val version: String,
    val generado: String? = null,
    val especies: List<PublishedSpecies> = emptyList(),
    val destacados: List<PublishedFeatured> = emptyList(),
    /** Servidor del que salió (lo añade la app al guardarlo, no viene del servidor). */
    val servidor: String? = null,
)

@Serializable
data class PublishedFeatured(val fecha: String, val categoria: String, val taxon_id: String)

@Serializable
data class PublishedSpecies(
    val taxon_id: String,
    val nombre_cientifico: String,
    val autoria: String? = null,
    val genero: String? = null,
    val familia: String? = null,
    val nombre_comun: String? = null,
    val otros_nombres: List<String> = emptyList(),
    val sinonimos: List<String> = emptyList(),
    val uicn: PublishedIucn? = null,
    val toxicidad: PublishedToxicity? = null,
    val endemismo: PublishedEndemism? = null,
    val amenazas: PublishedThreats? = null,
    val descripcion: String? = null,
    val actividad: String? = null,
    val dieta: String? = null,
    val reproduccion: String? = null,
    val distribucion: String? = null,
    val altitud_literatura: PublishedRange? = null,
    val habitat: String? = null,
    val lhc: PublishedRange? = null,
    val morfologia: PublishedMorphology? = null,
    val especies_confusion: List<String> = emptyList(),
    val dato_curioso: PublishedFact? = null,
    val foto_principal: PublishedPhoto? = null,
    val galeria: List<PublishedPhoto> = emptyList(),
    val fotos_referencia: Int? = null,
    val version: Int = 0,
)

@Serializable
data class PublishedIucn(val categoria: String, val anio: Int? = null, val fuente: String? = null)

@Serializable
data class PublishedToxicity(val nivel: String, val nota: String? = null, val fuente: String? = null)

@Serializable
data class PublishedEndemism(val endemica: Boolean, val alcance: String? = null, val fuente: String? = null)

@Serializable
data class PublishedThreats(val lista: List<String> = emptyList(), val fuente: String? = null)

@Serializable
data class PublishedRange(val min: Double? = null, val max: Double? = null, val fuente: String? = null)

@Serializable
data class PublishedFact(val valor: String, val fuente: String? = null)

@Serializable
data class PublishedPhoto(val sha256: String, val licencia: String? = null, val atribucion: String? = null, val url_origen: String? = null)

@Serializable
data class PublishedMorphology(
    val timpano: String? = null,
    val discos: String? = null,
    val pliegues: String? = null,
    val patron_dorsal: String? = null,
    val patron_ventral: String? = null,
    val membranas: String? = null,
    val diagnosticos: List<String> = emptyList(),
)
