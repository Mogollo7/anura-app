package me.juanlabs.anura.feature.capture

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
import me.juanlabs.anura.core.key.ClaveDocumento
import me.juanlabs.anura.core.key.ClaveEspecie
import me.juanlabs.anura.core.key.ClaveRespuesta
import me.juanlabs.anura.core.key.ClaveResolucion
import me.juanlabs.anura.core.key.resolver
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

/**
 * «Paso a paso» con la clave del paquete instalado. Misma cromática del asistente
 * ([CaptureWizardScaffold]); las preguntas salen del JSON, no de una lista fija.
 */
@Composable
fun ClaveScreen(
    onBackClick: () -> Unit,
    onCloseClick: () -> Unit,
    onOpenPackages: () -> Unit,
    onOpenSpecies: (String) -> Unit,
) {
    val repository = rememberAnuraRepository()
    val snapshot by repository.state.collectAsState()
    val pack = snapshot.packages.firstOrNull {
        it.active && it.status == RegionalPackageStatus.Installed && !it.localPath.isNullOrBlank()
    }
    if (pack == null) {
        ClaveMessage(
            title = stringResource(R.string.clave_no_package_title),
            body = stringResource(R.string.clave_no_package_body),
            action = stringResource(R.string.clave_open_packages),
            onAction = onOpenPackages,
            onBackClick = onBackClick,
            onCloseClick = onCloseClick,
        )
        return
    }
    val version = pack.version ?: "1"
    var clave by remember(pack.id, version) { mutableStateOf(repository.cachedClave(pack.id, version)) }
    var intento by rememberSaveable(pack.id, version) { mutableIntStateOf(0) }
    var cargando by remember(pack.id, version) { mutableStateOf(clave == null) }
    var encoded by rememberSaveable(pack.id, version) { mutableStateOf("") }
    val respuestas = remember(encoded) { decodeRespuestas(encoded) }

    LaunchedEffect(pack.id, version, intento) {
        if (clave == null) cargando = true
        val fresca = repository.refreshClave(pack.id, version)
        if (fresca != null) clave = fresca
        cargando = false
    }

    val documento = clave
    when {
        documento == null && cargando -> ClaveMessage(
            title = stringResource(R.string.clave_loading),
            body = null,
            action = null,
            onAction = null,
            onBackClick = onBackClick,
            onCloseClick = onCloseClick,
            loading = true,
        )
        documento == null -> ClaveMessage(
            title = stringResource(R.string.clave_no_key_title),
            body = stringResource(R.string.clave_no_key_body),
            action = stringResource(R.string.clave_retry),
            onAction = { intento++ },
            onBackClick = onBackClick,
            onCloseClick = onCloseClick,
        )
        documento.especies.isEmpty() -> ClaveMessage(
            title = stringResource(R.string.clave_no_species_title),
            body = stringResource(R.string.clave_no_species_body),
            action = null,
            onAction = null,
            onBackClick = onBackClick,
            onCloseClick = onCloseClick,
        )
        else -> ClaveRecorrido(
            clave = documento,
            respuestas = respuestas,
            onResponder = { respuesta -> encoded = encodeRespuestas(respuestas + respuesta) },
            onCorregir = {
                encoded = encodeRespuestas(respuestas.dropLast(1))
            },
            onReiniciar = { encoded = "" },
            onBackClick = {
                if (respuestas.isNotEmpty()) encoded = encodeRespuestas(respuestas.dropLast(1))
                else onBackClick()
            },
            onCloseClick = onCloseClick,
            onOpenSpecies = onOpenSpecies,
        )
    }
}

@Composable
private fun ClaveRecorrido(
    clave: ClaveDocumento,
    respuestas: List<ClaveRespuesta>,
    onResponder: (ClaveRespuesta) -> Unit,
    onCorregir: () -> Unit,
    onReiniciar: () -> Unit,
    onBackClick: () -> Unit,
    onCloseClick: () -> Unit,
    onOpenSpecies: (String) -> Unit,
) {
    val resolucion = resolver(clave, respuestas)
    CaptureWizardScaffold(
        appBarTitle = stringResource(R.string.clave_appbar),
        step = 1,
        showProgress = false,
        onBackClick = onBackClick,
        onCloseClick = onCloseClick,
    ) {
        when (resolucion) {
            is ClaveResolucion.Pregunta -> {
                val caracter = clave.caracteres.first { it.id == resolucion.siguiente }
                CaptureWizardHeading(title = caracter.pregunta, subtitle = caracter.ayuda)
                Spacer(modifier = Modifier.height(CaptureSubtitleToContentGap))
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
            }
            is ClaveResolucion.Una -> ClaveResultadoUna(
                especie = clave.especies.first { it.taxon_id == resolucion.taxonId },
                onOpenSpecies = onOpenSpecies,
                onReiniciar = onReiniciar,
            )
            is ClaveResolucion.Varias -> ClaveResultadoVarias(
                clave = clave,
                resolucion = resolucion,
                onOpenSpecies = onOpenSpecies,
                onReiniciar = onReiniciar,
                onCorregir = onCorregir,
            )
            ClaveResolucion.Ninguna -> {
                CaptureWizardHeading(
                    title = stringResource(R.string.clave_none_title),
                    subtitle = stringResource(R.string.clave_none_body),
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
                    style = AnuraFormButtonStyle.Primary,
                )
            }
        }
    }
}

@Composable
private fun ClaveResultadoUna(
    especie: ClaveEspecie,
    onOpenSpecies: (String) -> Unit,
    onReiniciar: () -> Unit,
) {
    CaptureWizardHeading(
        title = stringResource(R.string.clave_one_title),
        subtitle = especie.familia,
    )
    Spacer(modifier = Modifier.height(CaptureSubtitleToContentGap))
    ClaveEspecieCard(especie)
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
        style = AnuraFormButtonStyle.Outline,
    )
}

@Composable
private fun ClaveResultadoVarias(
    clave: ClaveDocumento,
    resolucion: ClaveResolucion.Varias,
    onOpenSpecies: (String) -> Unit,
    onReiniciar: () -> Unit,
    onCorregir: () -> Unit,
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
    Spacer(modifier = Modifier.height(CaptureSubtitleToContentGap))
    val especies = resolucion.especies.mapNotNull { id -> clave.especies.firstOrNull { it.taxon_id == id } }
    val separan = caracteresQueSeparan(especies)
    especies.forEach { especie ->
        ClaveEspecieCard(especie, separan)
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
    if (resolucion.pendientes.isNotEmpty()) {
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
        style = AnuraFormButtonStyle.Primary,
    )
}

@Composable
private fun ClaveEspecieCard(especie: ClaveEspecie, solo: Set<String>? = null) {
    AnuraCard(modifier = Modifier.fillMaxWidth(), bordered = true) {
        Text(
            text = especie.nombre_comun ?: especie.nombre_cientifico,
            style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.SemiBold),
            color = MaterialTheme.colorScheme.onSurface,
            modifier = Modifier.padding(horizontal = AnuraDimens.spaceCardInsetHorizontal, vertical = AnuraDimens.spaceCardInsetVertical),
        )
        if (especie.nombre_comun != null) {
            Text(
                text = especie.nombre_cientifico,
                style = MaterialTheme.typography.bodyMedium.copy(fontStyle = FontStyle.Italic),
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                modifier = Modifier.padding(horizontal = AnuraDimens.spaceCardInsetHorizontal),
            )
        }
        val lineas = especie.resumen.filterKeys { solo == null || it in solo }.values
        if (lineas.isNotEmpty()) {
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = lineas.joinToString("\n"),
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                modifier = Modifier.padding(
                    horizontal = AnuraDimens.spaceCardInsetHorizontal,
                    vertical = AnuraDimens.spaceCardInsetVertical,
                ),
            )
        }
    }
}

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
) {
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

private fun encodeRespuestas(respuestas: List<ClaveRespuesta>): String =
    respuestas.joinToString("\n") { "${it.caracter}\t${it.opcion.orEmpty()}" }

private fun decodeRespuestas(raw: String): List<ClaveRespuesta> =
    raw.split('\n').filter { it.isNotEmpty() }.map { linea ->
        val partes = linea.split('\t', limit = 2)
        ClaveRespuesta(partes[0], partes.getOrNull(1)?.ifEmpty { null })
    }

@AnuraPreviews
@Composable
private fun ClaveScreenPreview() {
    AnuraTheme {
        ClaveScreen(onBackClick = {}, onCloseClick = {}, onOpenPackages = {}, onOpenSpecies = {})
    }
}
