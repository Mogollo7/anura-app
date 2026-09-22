package me.juanlabs.anura.core.inference

import android.content.Context
import android.content.pm.ApplicationInfo
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.os.Debug
import android.os.SystemClock
import android.util.Log
import java.io.File
import kotlin.math.pow
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import kotlinx.coroutines.withContext
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.jsonArray
import kotlinx.serialization.json.jsonObject
import kotlinx.serialization.json.jsonPrimitive

enum class IdentificationFailure { NoPhoto, NoActivePackage, EngineError }

sealed interface IdentificationOutcome {
    data class Identified(
        val taxonId: String,
        val scientificName: String,
        val accepted: Boolean,
        val openSet: OpenSetScore,
        val neighbors: List<Neighbor>,
        /** Ordenadas por voto; la primera es la especie identificada. */
        val candidates: List<Candidate>,
    ) : IdentificationOutcome

    /**
     * Rechazado, y no como especie desconocida dentro de Anura: la distancia de Mahalanobis supera
     * [AnuraIdentifier.NotAnuroTau], el umbral provisional que separa "rana no catalogada" de
     * "la foto no contiene un anuro" (ver evaluación en Second Brain — nota "Umbral rana/no-rana").
     */
    data class NotAnuro(val openSet: OpenSetScore) : IdentificationOutcome

    data class Failed(val reason: IdentificationFailure, val detail: String) : IdentificationOutcome
}

/**
 * Pipeline de identificación por imagen en el teléfono, igual al de PC:
 * foto → preprocesado open_clip → encoder ONNX → k-NN (k=5, voto ponderado) en el paquete activo
 * vía sqlite-vec → rechazo Open Set por Mahalanobis. El encoder y el Open Set se cargan una vez.
 */
class AnuraIdentifier(private val context: Context) {
    private val mutex = Mutex()
    private var encoder: ImageEncoder? = null
    private var openSet: OpenSetModel? = null
    private var index: PackageVectorIndex? = null
    private var indexFileStamp = 0L
    private var allowedByPackage: Map<String, Set<String>>? = null
    private val debuggable = context.applicationInfo.flags and ApplicationInfo.FLAG_DEBUGGABLE != 0

    suspend fun identify(
        photo: File,
        packagePath: String,
        packageId: String,
        latitude: Double? = null,
        longitude: Double? = null,
    ): IdentificationOutcome =
        withContext(Dispatchers.Default) {
            mutex.withLock {
                runCatching { identifyLocked(photo, packagePath, packageId, latitude, longitude) }.getOrElse { error ->
                    Log.e(Tag, "Fallo en la identificación", error)
                    IdentificationOutcome.Failed(IdentificationFailure.EngineError, error.message ?: error.javaClass.simpleName)
                }
            }
        }

    private fun identifyLocked(
        photo: File,
        packagePath: String,
        packageId: String,
        latitude: Double?,
        longitude: Double?,
    ): IdentificationOutcome {
        val encoder = encoder ?: loadEncoder().also { encoder = it }
        val openSet = openSet ?: context.assets.open(OpenSetAsset).use(OpenSetModel::read).also { openSet = it }
        val allowed = (allowedByPackage ?: loadAllowedByPackage().also { allowedByPackage = it })[packageId]
        // Un paquete desinstalado y vuelto a instalar deja la conexión apuntando al archivo borrado.
        val stamp = File(packagePath).lastModified()
        val index = index?.takeIf { it.packagePath == packagePath && indexFileStamp == stamp } ?: run {
            index?.close()
            PackageVectorIndex.open(context, packagePath).also {
                index = it
                indexFileStamp = stamp
                Log.i(Tag, "paquete abierto $packagePath sqlite-vec=${it.vecVersion()}")
            }
        }

        val t0 = SystemClock.elapsedRealtime()
        val bitmap = BitmapFactory.decodeFile(photo.path, BitmapFactory.Options().apply {
            inPreferredConfig = Bitmap.Config.ARGB_8888
        }) ?: return IdentificationOutcome.Failed(IdentificationFailure.NoPhoto, "No se pudo decodificar ${photo.path}")
        val width = bitmap.width
        val height = bitmap.height
        val pixels = IntArray(width * height).also { bitmap.getPixels(it, 0, width, 0, 0, width, height) }
        bitmap.recycle()
        val chw = ClipPreprocessor.preprocess(pixels, width, height)
        val t1 = SystemClock.elapsedRealtime()
        val embedding = encoder.encode(chw)
        val t2 = SystemClock.elapsedRealtime()
        // Prior geográfico por zona (pipeline_dataset/paquetes_zonales.py, validado con control de
        // fuga: Top-1 62.9%→72.5%). Sin coordenadas o fuera de la cobertura del paquete, geoPrior
        // queda null y el voto es puramente visual — la decisión nunca se descarta por esto.
        val geoPrior = if (latitude != null && longitude != null) {
            index.zoneIdFor(latitude, longitude)?.let(index::zonePrior)
        } else {
            null
        }
        // Clima actual vía Open-Meteo (evaluation/geo_weather_v1: Top-1 61.2%→65.1%, n=129, peso
        // congelado en el paquete). Llamada de red bloqueante con timeout corto (4s): si falla o
        // no hay ubicación, weatherMultiplier queda null y el voto sigue siendo puramente visual —
        // igual que sin coordenadas, nunca bloquea la identificación offline.
        val weatherMultiplier = buildWeatherMultiplier(index, latitude, longitude)
        // k=5: la misma cantidad de vecinos con la que PC calibró y congeló el método (Fase 8/13).
        // La decisión (especie + aceptar/rechazar) sale de aquí, no del k más amplio de abajo.
        val neighbors = index.nearest(embedding, KNeighbors)
        val official = KnnVote.candidates(neighbors, geoPrior, weatherMultiplier)
        val top = official.firstOrNull()
            ?: return IdentificationOutcome.Failed(IdentificationFailure.EngineError, "El paquete no devolvió vecinos")
        val taxonId = top.taxonId
        val t3 = SystemClock.elapsedRealtime()
        val score = openSet.score(embedding, allowed)
        val t4 = SystemClock.elapsedRealtime()

        if (!score.accepted && score.mahalanobis > NotAnuroTau) {
            Log.i(Tag, "identify ${photo.name} maha=${"%.3f".format(score.mahalanobis)} > notAnuroTau=$NotAnuroTau NOT_ANURO")
            return IdentificationOutcome.NotAnuro(score)
        }

        // Candidatas para mostrar: mismo ganador oficial (k=5) + hasta 3 alternativas de un vecindario
        // más amplio, solo para que la UI tenga con qué comparar — no cambia la decisión de arriba.
        val broader = if (DisplayNeighbors > KNeighbors) index.nearest(embedding, DisplayNeighbors) else neighbors
        val candidates = KnnVote.displayCandidates(top, KnnVote.candidates(broader, geoPrior, weatherMultiplier), DisplayCandidateCount)

        val name = top.scientificName
        Log.i(
            Tag,
            "identify ${photo.name} ${width}x$height pred=$name share=${"%.3f".format(top.share)} maha=${"%.3f".format(score.mahalanobis)} " +
                "tau=${"%.3f".format(openSet.tau)} allowed=${allowed?.size ?: "todas"} ${if (score.accepted) "ACCEPT" else "REJECT"} " +
                "geoZone=${geoPrior?.zoneId ?: "sin_ubicacion_o_fuera_de_cobertura"} " +
                "clima=${if (weatherMultiplier != null) "ok" else "sin_dato"} " +
                "preprocess=${t1 - t0}ms encode=${t2 - t1}ms knn=${t3 - t2}ms openset=${t4 - t3}ms",
        )
        logMemory("after_identify")
        if (debuggable) writeDebugRecord(photo, width, height, embedding, neighbors, taxonId, score, longArrayOf(t1 - t0, t2 - t1, t3 - t2, t4 - t3))
        return IdentificationOutcome.Identified(taxonId, name, score.accepted, score, neighbors, candidates)
    }

    /**
     * Clima actual (Open-Meteo) × peso congelado en el paquete (`weather_prior_meta`), ya elevado
     * a la potencia y listo para multiplicar el voto — ver [KnnVote.candidates]. Cualquier fallo
     * (sin ubicación, sin red, sin tabla en el paquete, especie sin cobertura de clima en train)
     * devuelve null/omite esa especie: nunca bloquea ni penaliza por falta de dato.
     */
    private fun buildWeatherMultiplier(index: PackageVectorIndex, latitude: Double?, longitude: Double?): Map<String, Double>? {
        if (latitude == null || longitude == null) return null
        val stats = index.weatherPrior() ?: return null
        val weight = index.weatherPriorWeight() ?: return null
        val obs = OpenMeteoClient.fetchCurrent(latitude, longitude) ?: return null
        return stats.mapValues { (_, s) -> s.likelihood(obs).pow(weight) }
    }

    private fun loadAllowedByPackage(): Map<String, Set<String>> = runCatching {
        val json = Json.parseToJsonElement(context.assets.open(AllowedByPackageAsset).bufferedReader().readText())
        json.jsonObject.mapValues { (_, ids) -> ids.jsonArray.map { it.jsonPrimitive.content }.toSet() }
    }.getOrElse {
        Log.w(Tag, "No se pudo cargar $AllowedByPackageAsset, Open Set sin restringir por paquete", it)
        emptyMap()
    }

    private fun loadEncoder(): ImageEncoder {
        logMemory("before_encoder_load")
        val start = SystemClock.elapsedRealtime()
        val loaded = ImageEncoder.load(context)
        Log.i(Tag, "encoder cargado en ${SystemClock.elapsedRealtime() - start}ms")
        logMemory("after_encoder_load")
        return loaded
    }

    private fun logMemory(label: String) {
        val info = Debug.MemoryInfo().also(Debug::getMemoryInfo)
        val rssKb = runCatching {
            File("/proc/self/status").readLines().first { it.startsWith("VmRSS:") }.filter(Char::isDigit).toLong()
        }.getOrDefault(-1L)
        Log.i(
            Tag,
            "memory $label rss=${rssKb / 1024}MB pss=${info.totalPss / 1024}MB " +
                "nativeHeap=${Debug.getNativeHeapAllocatedSize() / (1024 * 1024)}MB " +
                "javaHeap=${(Runtime.getRuntime().totalMemory() - Runtime.getRuntime().freeMemory()) / (1024 * 1024)}MB",
        )
    }

    @Serializable
    private data class DebugRecord(
        val file: String,
        val width: Int,
        val height: Int,
        val embedding: List<Float>,
        val neighbors: List<DebugNeighbor>,
        val predictedTaxonId: String,
        val mahalanobis: Double,
        val nearestCentroid: String,
        val decision: String,
        val timingsMs: List<Long>,
    )

    @Serializable
    private data class DebugNeighbor(val taxonId: String, val scientificName: String, val distance: Double)

    private fun writeDebugRecord(
        photo: File, width: Int, height: Int, embedding: FloatArray, neighbors: List<Neighbor>,
        taxonId: String, score: OpenSetScore, timings: LongArray,
    ) {
        val record = DebugRecord(
            file = photo.name, width = width, height = height, embedding = embedding.toList(),
            neighbors = neighbors.map { DebugNeighbor(it.taxonId, it.scientificName, it.distance) },
            predictedTaxonId = taxonId, mahalanobis = score.mahalanobis, nearestCentroid = score.nearestCentroidId,
            decision = if (score.accepted) "ACCEPT" else "REJECT", timingsMs = timings.toList(),
        )
        val dir = File(context.filesDir, "inference_debug").apply { mkdirs() }
        File(dir, "last_identification.json").writeText(Json.encodeToString(DebugRecord.serializer(), record))
    }

    companion object {
        const val Tag = "AnuraInference"
        private const val OpenSetAsset = "openset/openset_v1.1.0_clean.bin"
        private const val AllowedByPackageAsset = "openset/allowed_by_package.json"
        private const val KNeighbors = 5
        private const val DisplayNeighbors = 15
        private const val DisplayCandidateCount = 4

        /**
         * Umbral provisional para "la foto no contiene un anuro" (distinto del [OpenSetModel.tau]
         * congelado en PC, que separa especie conocida de especie desconocida DENTRO de Anura).
         * Calibrado con una primera evaluación exploratoria: 30 imágenes no-rana genéricas
         * (Wikimedia Commons) puntuaron Mahalanobis 49.99–74.10, mientras que la única especie de
         * rana desconocida con datos de Fase 13 (Hyloxalus_picachos, n=15) puntuó 27.22–46.65 — sin
         * solape. Valor elegido a medio camino con margen hacia el lado "no-rana" para minimizar
         * falsos NOT_ANURO sobre especies nuevas reales. NO viene del artefacto congelado de PC:
         * requiere recalibración con más especies desconocidas y más negativos antes de v1 (ver nota
         * "Umbral rana/no-rana — primera evaluación" en Second Brain).
         */
        const val NotAnuroTau = 48.0
    }
}
