package me.juanlabs.anura.feature.capture

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.semantics.LiveRegionMode
import androidx.compose.ui.semantics.liveRegion
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.font.FontStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import me.juanlabs.anura.R
import me.juanlabs.anura.core.data.RegionalPackageStatus
import me.juanlabs.anura.core.data.SpeciesCatalog
import me.juanlabs.anura.core.data.rememberAnuraRepository
import me.juanlabs.anura.core.key.ClaveActividad
import me.juanlabs.anura.core.key.ClaveAltitud
import me.juanlabs.anura.core.key.ClaveCaracter
import me.juanlabs.anura.core.key.ClaveDatos
import me.juanlabs.anura.core.key.ClaveDocumento
import me.juanlabs.anura.core.key.ClaveEspecie
import me.juanlabs.anura.core.key.ClaveRespuesta
import me.juanlabs.anura.core.key.ClaveResolucion
import me.juanlabs.anura.core.key.ClaveSustrato
import me.juanlabs.anura.core.key.ClaveTamano
import me.juanlabs.anura.core.key.codificarRespuestas
import me.juanlabs.anura.core.key.decodificarRespuestas
import me.juanlabs.anura.core.key.especiesQueQuedan
import me.juanlabs.anura.core.key.manualesSinPrevias
import me.juanlabs.anura.core.key.resolver
import me.juanlabs.anura.core.key.respuestasPrevias
import me.juanlabs.anura.core.platform.rememberNetworkAvailable
import me.juanlabs.anura.designsystem.component.AnuraCard
import me.juanlabs.anura.designsystem.component.AnuraEmptyState
import me.juanlabs.anura.designsystem.component.AnuraFormButton
import me.juanlabs.anura.designsystem.component.AnuraFormButtonStyle
import me.juanlabs.anura.designsystem.component.AnuraLoadingState
import me.juanlabs.anura.designsystem.component.AnuraTopBar
import me.juanlabs.anura.designsystem.icon.AnuraIcons
import me.juanlabs.anura.designsystem.preview.AnuraPreviews
import me.juanlabs.anura.designsystem.theme.AnuraDimens
import me.juanlabs.anura.designsystem.theme.AnuraTheme

// ---------------------------------------------------------------------------------------------
// Carga de la clave del paquete activo (compartida por «Ayuda para identificar» y la clave suelta)
// ---------------------------------------------------------------------------------------------

/** En qué punto está la clave del paquete instalado. Cada caso menos [Lista] tiene su texto guía. */
internal sealed interface ClaveCarga {
    /** Este teléfono no tiene un paquete activo instalado. */
    data object SinPaquete : ClaveCarga

    data object Cargando : ClaveCarga

    /** Con red, el servidor ya no publica este paquete: hay que bajar el vigente. */
    data object Obsoleta : ClaveCarga

    /** Sin red y sin la clave guardada: se descarga al conectarse. */
    data object SinClave : ClaveCarga

    data object SinEspecies : ClaveCarga

    data class Lista(val documento: ClaveDocumento) : ClaveCarga
}

internal class ClaveCargaEstado(val carga: ClaveCarga, val reintentar: () -> Unit)

/**
 * La clave del paquete activo: primero la guardada junto al paquete (funciona sin señal) y, si hay
 * red, se refresca desde el servidor. Nunca una clave de ejemplo.
 */
@Composable
internal fun rememberClaveCarga(): ClaveCargaEstado {
    val repository = rememberAnuraRepository()
    val snapshot by repository.state.collectAsState()
    val pack = snapshot.packages.firstOrNull {
        it.active && it.status == RegionalPackageStatus.Installed && !it.localPath.isNullOrBlank()
    }
    val packId = pack?.id
    val version = pack?.version ?: "1"
    var clave by remember(packId, version) {
        mutableStateOf(packId?.let { repository.cachedClave(it, version) })
    }
    var intento by rememberSaveable(packId, version) { mutableIntStateOf(0) }
    var cargando by remember(packId, version) { mutableStateOf(packId != null && clave == null) }
    LaunchedEffect(packId, version, intento) {
        if (packId == null) return@LaunchedEffect
        if (clave == null) cargando = true
        val fresca = repository.refreshClave(packId, version)
        if (fresca != null) clave = fresca
        cargando = false
    }
    val online = rememberNetworkAvailable()
    val documento = clave
    val carga = when {
        packId == null -> ClaveCarga.SinPaquete
        documento == null && cargando -> ClaveCarga.Cargando
        documento == null && online -> ClaveCarga.Obsoleta
        documento == null -> ClaveCarga.SinClave
        documento.especies.isEmpty() -> ClaveCarga.SinEspecies
        else -> ClaveCarga.Lista(documento)
    }
    return ClaveCargaEstado(carga, reintentar = { intento++ })
}

// ---------------------------------------------------------------------------------------------
// Pantallas
// ---------------------------------------------------------------------------------------------

/**
 * Cómo se comporta la clave cuando va dentro del asistente «Paso a paso»: prerrellena con lo que
 * ya se capturó, se puede omitir y termina en «Continuar» en vez de en «Empezar de nuevo».
 */
internal class ClaveAsistente(
    val datos: ClaveDatos,
    val fromReview: Boolean,
    val onContinuar: () -> Unit,
    val onOmitir: () -> Unit,
)

/**
 * La clave sola, sin el asistente. Misma cromática del asistente ([CaptureWizardScaffold]); las
 * preguntas salen del JSON del paquete, no de una lista fija.
 */
@Composable
fun ClaveScreen(
    onBackClick: () -> Unit,
    onCloseClick: () -> Unit,
    onOpenPackages: () -> Unit,
    onOpenSpecies: (String) -> Unit,
) {
    var encoded by rememberSaveable { mutableStateOf("") }
    ClaveFlujo(
        encoded = encoded,
        onEncodedChange = { encoded = it },
        asistente = null,
        onBackClick = onBackClick,
        onCloseClick = onCloseClick,
        onOpenPackages = onOpenPackages,
        onOpenSpecies = onOpenSpecies,
    )
}

/**
 * Paso opcional «Ayuda para identificar» del asistente (entre el Paso 5 y el resumen). Las
 * respuestas manuales viven en el borrador de la observación; lo que ya se capturó en los pasos 1 a 3
 * (altitud del GPS, tamaño, microhábitat, franja del día) contesta las preguntas correspondientes.
 */
@Composable
fun CaptureClaveScreen(
    onBackClick: () -> Unit,
    onNext: () -> Unit,
    onSkip: () -> Unit = onNext,
    fromReview: Boolean = false,
    onSave: () -> Unit = onNext,
    onCloseClick: () -> Unit = onBackClick,
    onOpenPackages: () -> Unit = {},
    onOpenSpecies: (String) -> Unit = {},
) {
    val repository = rememberAnuraRepository()
    val snapshot by repository.state.collectAsState()
    val draft = snapshot.draft
    ClaveFlujo(
        encoded = draft.claveAnswers.orEmpty(),
        onEncodedChange = { value -> repository.updateDraft { it.copy(claveAnswers = value) } },
        asistente = ClaveAsistente(
            datos = ClaveDatos(
                altitudM = draft.altitudeMeters,
                tamanoMm = draft.svlMm,
                habitat = draft.habitat,
                periodo = draft.period,
            ),
            fromReview = fromReview,
            onContinuar = {
                // «usó la ayuda» aunque solo haya aceptado lo que ya sabía de los pasos anteriores
                if (draft.claveAnswers == null) repository.updateDraft { it.copy(claveAnswers = "") }
                if (fromReview) onSave() else onNext()
            },
            onOmitir = {
                repository.updateDraft { it.copy(claveAnswers = null) }
                onSkip()
            },
        ),
        onBackClick = onBackClick,
        onCloseClick = onCloseClick,
        onOpenPackages = onOpenPackages,
        onOpenSpecies = onOpenSpecies,
    )
}

@Composable
private fun ClaveFlujo(
    encoded: String,
    onEncodedChange: (String) -> Unit,
    asistente: ClaveAsistente?,
    onBackClick: () -> Unit,
    onCloseClick: () -> Unit,
    onOpenPackages: () -> Unit,
    onOpenSpecies: (String) -> Unit,
) {
    val estado = rememberClaveCarga()
    val onSkip = asistente?.onOmitir
    when (val carga = estado.carga) {
        ClaveCarga.SinPaquete -> ClaveMessage(
            title = stringResource(R.string.clave_no_package_title),
            body = stringResource(R.string.clave_no_package_body),
            action = stringResource(R.string.clave_open_packages),
            onAction = onOpenPackages,
            onBackClick = onBackClick,
            onCloseClick = onCloseClick,
            onSkip = onSkip,
        )
        ClaveCarga.Cargando -> ClaveMessage(
            title = stringResource(R.string.clave_loading),
            body = null,
            action = null,
            onAction = null,
            onBackClick = onBackClick,
            onCloseClick = onCloseClick,
            loading = true,
            onSkip = onSkip,
        )
        // Con red y sin clave: el servidor ya no publica este paquete (o aún no lo publicó).
        // Reintentar no lo arregla; hay que bajar el paquete vigente desde Paquetes.
        ClaveCarga.Obsoleta -> ClaveMessage(
            title = stringResource(R.string.clave_stale_title),
            body = stringResource(R.string.clave_stale_body),
            action = stringResource(R.string.clave_open_packages),
            onAction = onOpenPackages,
            onBackClick = onBackClick,
            onCloseClick = onCloseClick,
            onSkip = onSkip,
        )
        ClaveCarga.SinClave -> ClaveMessage(
            title = stringResource(R.string.clave_no_key_title),
            body = stringResource(R.string.clave_no_key_body),
            action = stringResource(R.string.clave_retry),
            onAction = estado.reintentar,
            onBackClick = onBackClick,
            onCloseClick = onCloseClick,
            onSkip = onSkip,
        )
        ClaveCarga.SinEspecies -> ClaveMessage(
            title = stringResource(R.string.clave_no_species_title),
            body = stringResource(R.string.clave_no_species_body),
            action = null,
            onAction = null,
            onBackClick = onBackClick,
            onCloseClick = onCloseClick,
            onSkip = onSkip,
        )
        is ClaveCarga.Lista -> {
            val documento = carga.documento
            val previas = remember(documento, asistente?.datos) {
                asistente?.datos?.let { respuestasPrevias(documento, it) }.orEmpty()
            }
            val manuales = remember(encoded, previas) {
                manualesSinPrevias(previas, decodificarRespuestas(encoded))
            }
            // Respuestas guardadas de otra versión del paquete: no encajan con esta clave, se descartan.
            val valida = remember(documento, previas, manuales) {
                especiesQueQuedan(documento, previas + manuales) != null
            }
            if (!valida) {
                LaunchedEffect(documento) { onEncodedChange("") }
                return
            }
            ClaveRecorrido(
                clave = documento,
                previas = previas,
                respuestas = manuales,
                onResponder = { respuesta -> onEncodedChange(codificarRespuestas(manuales + respuesta)) },
                onCorregir = { onEncodedChange(codificarRespuestas(manuales.dropLast(1))) },
                onReiniciar = { onEncodedChange("") },
                onBackClick = {
                    if (manuales.isNotEmpty()) onEncodedChange(codificarRespuestas(manuales.dropLast(1)))
                    else onBackClick()
                },
                onCloseClick = onCloseClick,
                onOpenSpecies = onOpenSpecies,
                asistente = asistente,
            )
        }
    }
}

@Composable
private fun ClaveRecorrido(
    clave: ClaveDocumento,
    previas: List<ClaveRespuesta>,
    respuestas: List<ClaveRespuesta>,
    onResponder: (ClaveRespuesta) -> Unit,
    onCorregir: () -> Unit,
    onReiniciar: () -> Unit,
    onBackClick: () -> Unit,
    onCloseClick: () -> Unit,
    onOpenSpecies: (String) -> Unit,
    asistente: ClaveAsistente?,
) {
    val resolucion = resolver(clave, previas + respuestas)
    val enAsistente = asistente != null
    // En el asistente lo principal es continuar; empezar de nuevo pasa a ser secundario.
    val estiloReiniciar = if (enAsistente) AnuraFormButtonStyle.Outline else AnuraFormButtonStyle.Primary
    val pie: @Composable () -> Unit = {
        ClavePrevias(clave, previas)
        if (asistente != null) {
            val hayAlgo = previas.isNotEmpty() || respuestas.isNotEmpty()
            val terminado = resolucion !is ClaveResolucion.Pregunta
            if (hayAlgo || terminado) {
                Spacer(modifier = Modifier.height(CaptureContentToFooterGap))
                AnuraFormButton(
                    text = when {
                        asistente.fromReview -> stringResource(R.string.capture_clave_save)
                        terminado -> stringResource(R.string.capture_clave_continue_result)
                        else -> stringResource(R.string.capture_clave_continue)
                    },
                    onClick = asistente.onContinuar,
                    style = AnuraFormButtonStyle.Primary,
                )
            }
            Spacer(modifier = Modifier.height(AnuraDimens.spaceActionGap))
            AnuraFormButton(
                text = stringResource(R.string.capture_wizard_skip),
                onClick = asistente.onOmitir,
                style = AnuraFormButtonStyle.Outline,
            )
        }
    }
    CaptureWizardScaffold(
        appBarTitle = stringResource(if (enAsistente) R.string.capture_clave_appbar else R.string.clave_appbar),
        step = 5,
        showProgress = false,
        onBackClick = onBackClick,
        onCloseClick = onCloseClick,
    ) {
        when (resolucion) {
            is ClaveResolucion.Pregunta -> {
                val caracter = clave.caracteres.first { it.id == resolucion.siguiente }
                CaptureWizardHeading(title = caracter.pregunta, subtitle = caracter.ayuda)
                Text(
                    text = stringResource(R.string.clave_remaining, resolucion.especies.size),
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    modifier = Modifier.semantics { liveRegion = LiveRegionMode.Polite },
                )
                Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))
                caracter.opciones.forEach { opcion ->
                    AnuraFormButton(
                        text = opcion.etiqueta,
                        onClick = { onResponder(ClaveRespuesta(caracter.id, opcion.id)) },
                        style = AnuraFormButtonStyle.Outline,
                    )
                    Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))
                }
                AnuraFormButton(
                    text = stringResource(R.string.clave_unknown),
                    onClick = { onResponder(ClaveRespuesta(caracter.id, null)) },
                    style = AnuraFormButtonStyle.Secondary,
                )
                if (respuestas.isNotEmpty()) {
                    Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))
                    AnuraFormButton(
                        text = stringResource(R.string.clave_correct),
                        onClick = onCorregir,
                        style = AnuraFormButtonStyle.OutlineNeutral,
                    )
                }
                Spacer(modifier = Modifier.height(AnuraDimens.spaceSection))
                pie()
            }
            is ClaveResolucion.Una -> {
                ClaveResultadoUna(
                    clave = clave,
                    especie = clave.especies.first { it.taxon_id == resolucion.taxonId },
                    onOpenSpecies = onOpenSpecies,
                    onReiniciar = onReiniciar,
                    estiloReiniciar = AnuraFormButtonStyle.Outline,
                )
                Spacer(modifier = Modifier.height(AnuraDimens.spaceSection))
                pie()
            }
            is ClaveResolucion.Varias -> {
                ClaveResultadoVarias(
                    clave = clave,
                    resolucion = resolucion,
                    onOpenSpecies = onOpenSpecies,
                    onReiniciar = onReiniciar,
                    onCorregir = onCorregir,
                    estiloReiniciar = estiloReiniciar,
                    puedeCorregir = respuestas.isNotEmpty(),
                )
                Spacer(modifier = Modifier.height(AnuraDimens.spaceSection))
                pie()
            }
            ClaveResolucion.Ninguna -> {
                CaptureWizardHeading(
                    title = stringResource(R.string.clave_none_title),
                    subtitle = stringResource(
                        if (previas.isNotEmpty()) R.string.capture_clave_none_prefilled else R.string.clave_none_body,
                    ),
                )
                Spacer(modifier = Modifier.height(CaptureContentToFooterGap))
                if (respuestas.isNotEmpty()) {
                    AnuraFormButton(
                        text = stringResource(R.string.clave_correct),
                        onClick = onCorregir,
                        style = AnuraFormButtonStyle.Outline,
                    )
                    Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))
                }
                AnuraFormButton(
                    text = stringResource(R.string.clave_restart),
                    onClick = onReiniciar,
                    style = estiloReiniciar,
                )
                Spacer(modifier = Modifier.height(AnuraDimens.spaceSection))
                pie()
            }
        }
    }
}

/** Lo que los pasos anteriores ya contestaron, con la opción que le tocó a cada pregunta. */
@Composable
private fun ClavePrevias(clave: ClaveDocumento, previas: List<ClaveRespuesta>) {
    val filas = previas.mapNotNull { respuesta ->
        val caracter = clave.caracteres.firstOrNull { it.id == respuesta.caracter } ?: return@mapNotNull null
        val opcion = caracter.opciones.firstOrNull { it.id == respuesta.opcion } ?: return@mapNotNull null
        stringResource(R.string.capture_clave_prefilled_row, etiquetaCaracter(caracter), opcion.etiqueta)
    }
    if (filas.isEmpty()) return
    Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))
    AnuraCard(modifier = Modifier.fillMaxWidth(), bordered = true) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(
                    horizontal = AnuraDimens.spaceCardInsetHorizontal,
                    vertical = AnuraDimens.spaceCardInsetVertical,
                ),
            verticalArrangement = Arrangement.spacedBy(4.dp),
        ) {
            Text(
                text = stringResource(R.string.capture_clave_prefilled_title),
                style = MaterialTheme.typography.titleSmall.copy(fontWeight = FontWeight.SemiBold),
                color = MaterialTheme.colorScheme.onSurface,
            )
            filas.forEach { fila ->
                Text(
                    text = fila,
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurface,
                )
            }
            Text(
                text = stringResource(R.string.capture_clave_prefilled_hint),
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
    }
}

@Composable
private fun etiquetaCaracter(caracter: ClaveCaracter): String = when (caracter.id) {
    ClaveAltitud -> stringResource(R.string.capture_clave_label_altitud)
    ClaveTamano -> stringResource(R.string.capture_clave_label_tamano)
    ClaveSustrato -> stringResource(R.string.capture_clave_label_sustrato)
    ClaveActividad -> stringResource(R.string.capture_clave_label_actividad)
    "morfo" -> stringResource(R.string.capture_clave_label_morfo)
    else -> caracter.pregunta
}

@Composable
private fun ClaveResultadoUna(
    clave: ClaveDocumento,
    especie: ClaveEspecie,
    onOpenSpecies: (String) -> Unit,
    onReiniciar: () -> Unit,
    estiloReiniciar: AnuraFormButtonStyle,
) {
    CaptureWizardHeading(
        title = stringResource(R.string.clave_one_title),
        subtitle = especie.familia,
    )
    ClaveEspecieCard(especie, clave)
    Spacer(modifier = Modifier.height(CaptureContentToFooterGap))
    // La ficha solo se ofrece si la especie está en el catálogo publicado (no hay ficha que abrir si no).
    val ficha = SpeciesCatalog.find(especie.taxon_id) ?: SpeciesCatalog.find(especie.nombre_cientifico)
    if (ficha != null) {
        AnuraFormButton(
            text = stringResource(R.string.clave_open_sheet),
            onClick = { onOpenSpecies(ficha.id) },
            style = AnuraFormButtonStyle.Primary,
        )
        Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))
    }
    AnuraFormButton(
        text = stringResource(R.string.clave_restart),
        onClick = onReiniciar,
        style = estiloReiniciar,
    )
}

@Composable
private fun ClaveResultadoVarias(
    clave: ClaveDocumento,
    resolucion: ClaveResolucion.Varias,
    onOpenSpecies: (String) -> Unit,
    onReiniciar: () -> Unit,
    onCorregir: () -> Unit,
    estiloReiniciar: AnuraFormButtonStyle,
    puedeCorregir: Boolean,
) {
    val nota = if (resolucion.indistinguibles) {
        stringResource(R.string.clave_several_same)
    } else {
        val preguntas = resolucion.pendientes.mapNotNull { id ->
            clave.caracteres.firstOrNull { it.id == id }?.pregunta
        }
        stringResource(R.string.clave_several_pending, preguntas.joinToString(" · "))
    }
    CaptureWizardHeading(
        title = stringResource(R.string.clave_several_title),
        subtitle = nota,
    )
    val especies = resolucion.especies.mapNotNull { id -> clave.especies.firstOrNull { it.taxon_id == id } }
    val separan = caracteresQueSeparan(especies)
    especies.forEach { especie ->
        ClaveEspecieCard(especie, clave, separan)
        val conocida = SpeciesCatalog.find(especie.taxon_id) ?: SpeciesCatalog.find(especie.nombre_cientifico)
        if (conocida != null) {
            Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))
            AnuraFormButton(
                text = stringResource(R.string.clave_open_sheet),
                onClick = { onOpenSpecies(conocida.id) },
                style = AnuraFormButtonStyle.Outline,
            )
        }
        Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))
    }
    if (resolucion.pendientes.isNotEmpty() && puedeCorregir) {
        AnuraFormButton(
            text = stringResource(R.string.clave_correct),
            onClick = onCorregir,
            style = AnuraFormButtonStyle.Outline,
        )
        Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))
    }
    AnuraFormButton(
        text = stringResource(R.string.clave_restart),
        onClick = onReiniciar,
        style = estiloReiniciar,
    )
}

/**
 * Una especie compatible. Todo va en una [Column]: [AnuraCard] es una superficie que apila sus hijos
 * unos sobre otros, así que sin columna el nombre, el nombre científico y el resumen se pintaban
 * encima entre sí. Cada dato del resumen es su propia línea, con su carácter delante, y crece con
 * la fuente grande.
 */
@Composable
private fun ClaveEspecieCard(especie: ClaveEspecie, clave: ClaveDocumento, solo: Set<String>? = null) {
    AnuraCard(modifier = Modifier.fillMaxWidth(), bordered = true) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(
                    horizontal = AnuraDimens.spaceCardInsetHorizontal,
                    vertical = AnuraDimens.spaceCardInsetVertical,
                ),
            verticalArrangement = Arrangement.spacedBy(4.dp),
        ) {
            Text(
                text = especie.nombre_comun ?: especie.nombre_cientifico,
                style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.SemiBold),
                color = MaterialTheme.colorScheme.onSurface,
            )
            if (especie.nombre_comun != null) {
                Text(
                    text = especie.nombre_cientifico,
                    style = MaterialTheme.typography.bodyMedium.copy(fontStyle = FontStyle.Italic),
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
            val lineas = especie.resumen.filterKeys { solo == null || it in solo }
            if (lineas.isNotEmpty()) {
                Spacer(modifier = Modifier.height(4.dp))
                lineas.forEach { (id, texto) ->
                    val caracter = clave.caracteres.firstOrNull { it.id == id }
                    Text(
                        text = if (caracter != null) {
                            stringResource(R.string.capture_clave_prefilled_row, etiquetaCaracter(caracter), texto)
                        } else {
                            texto
                        },
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }
            }
        }
    }
}

/**
 * Aviso de la clave: sin paquete, cargando, sin clave, sin especies. Con [onSkip] (dentro del
 * asistente) se dibuja con el marco del asistente y ofrece «Omitir este paso»; sin él, a pantalla
 * completa como estado vacío.
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun ClaveMessage(
    title: String,
    body: String?,
    action: String?,
    onAction: (() -> Unit)?,
    onBackClick: () -> Unit,
    onCloseClick: () -> Unit,
    loading: Boolean = false,
    onSkip: (() -> Unit)? = null,
) {
    if (onSkip != null) {
        CaptureWizardScaffold(
            appBarTitle = stringResource(R.string.capture_clave_appbar),
            step = 5,
            showProgress = false,
            onBackClick = onBackClick,
            onCloseClick = onCloseClick,
        ) {
            // el mensaje se anuncia solo cuando cambia (de «cargando» a «sin clave», por ejemplo)
            Column(modifier = Modifier.semantics(mergeDescendants = true) { liveRegion = LiveRegionMode.Polite }) {
                CaptureWizardHeading(title = title, subtitle = body ?: stringResource(R.string.capture_clave_optional_subtitle))
            }
            if (loading) {
                AnuraLoadingState(label = title, modifier = Modifier.fillMaxWidth().height(96.dp))
            }
            if (action != null && onAction != null) {
                AnuraFormButton(text = action, onClick = onAction, style = AnuraFormButtonStyle.Primary)
                Spacer(modifier = Modifier.height(AnuraDimens.spaceActionGap))
            }
            AnuraFormButton(
                text = stringResource(R.string.capture_wizard_skip),
                onClick = onSkip,
                style = AnuraFormButtonStyle.Outline,
            )
        }
        return
    }
    Scaffold(
        containerColor = AnuraTheme.extendedColors.boardBackground,
        topBar = {
            AnuraTopBar(
                title = stringResource(R.string.clave_appbar),
                onBackClick = onBackClick,
                centerTitle = true,
                actions = {
                    IconButton(
                        onClick = onCloseClick,
                        modifier = Modifier.size(AnuraDimens.sizeTouch),
                    ) {
                        Icon(
                            imageVector = AnuraIcons.Close,
                            contentDescription = stringResource(R.string.capture_wizard_close_cd),
                        )
                    }
                },
            )
        },
    ) { padding ->
        if (loading) {
            AnuraLoadingState(
                label = title,
                modifier = Modifier
                    .fillMaxSize()
                    .padding(padding),
            )
        } else {
            AnuraEmptyState(
                title = title,
                description = body,
                actionLabel = action,
                onAction = onAction,
                modifier = Modifier
                    .fillMaxSize()
                    .padding(padding),
            )
        }
    }
}

private fun caracteresQueSeparan(especies: List<ClaveEspecie>): Set<String> =
    especies.flatMap { it.resumen.keys }
        .distinct()
        .filter { clave -> especies.map { it.resumen[clave] }.toSet().size > 1 }
        .toSet()

@AnuraPreviews
@Composable
private fun ClaveScreenPreview() {
    AnuraTheme {
        ClaveScreen(onBackClick = {}, onCloseClick = {}, onOpenPackages = {}, onOpenSpecies = {})
    }
}
