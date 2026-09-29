package me.juanlabs.anura.feature.fieldsession

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.key
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import me.juanlabs.anura.R
import me.juanlabs.anura.core.data.rememberAmbientTemperatureLabel
import me.juanlabs.anura.core.data.rememberAnuraRepository
import me.juanlabs.anura.feature.capture.AudioDemoNotice
import me.juanlabs.anura.designsystem.component.AnuraCard
import me.juanlabs.anura.designsystem.component.AnuraSectionLabel
import me.juanlabs.anura.designsystem.component.AnuraTopBar
import me.juanlabs.anura.designsystem.icon.AnuraIcons
import me.juanlabs.anura.designsystem.preview.AnuraPreviews
import me.juanlabs.anura.designsystem.theme.AnuraDimens
import me.juanlabs.anura.designsystem.theme.AnuraTheme
import me.juanlabs.anura.designsystem.theme.AnuraThemeMode
import me.juanlabs.anura.feature.capture.CaptureLiveSpectrogramSession

private data class NightSoundCall(
    val speciesRes: Int,
    val typeRes: Int,
    val percentRes: Int,
    val contribution: Float,
)

private val NightSoundCalls = listOf(
    NightSoundCall(
        speciesRes = R.string.field_session_sp_truncatus,
        typeRes = R.string.night_sounds_call_territorial,
        percentRes = R.string.night_sounds_percent_68,
        contribution = 0.68f,
    ),
    NightSoundCall(
        speciesRes = R.string.night_sounds_sp_pugnax,
        typeRes = R.string.night_sounds_call_mating,
        percentRes = R.string.night_sounds_percent_22,
        contribution = 0.22f,
    ),
)

/**
 * `Sonidos nocturnos de la salida` (§4.1). Reutiliza el espectrograma de captura
 * sin botones del wizard (analizar / siguiente paso).
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun NightSoundsScreen(
    sessionId: String,
    onBackClick: () -> Unit,
) {
    val repository = rememberAnuraRepository()
    val snapshot by repository.state.collectAsState()
    val session = snapshot.fieldSessions.find { it.id == sessionId }
    val temperature = rememberAmbientTemperatureLabel(session?.latitude, session?.longitude)
    Scaffold(
        containerColor = AnuraTheme.extendedColors.boardBackground,
        topBar = {
            AnuraTopBar(
                title = stringResource(R.string.night_sounds_title),
                onBackClick = onBackClick,
                centerTitle = true,
            )
        },
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .verticalScroll(rememberScrollState())
                .padding(horizontal = AnuraDimens.spaceGutter)
                .padding(bottom = AnuraDimens.spaceSection),
        ) {
            AudioDemoNotice()
            Spacer(modifier = Modifier.height(AnuraDimens.spaceSection))
            NightSoundsMetadataChip(temperature = temperature)
            Spacer(modifier = Modifier.height(AnuraDimens.spaceSection))
            key(sessionId) {
                CaptureLiveSpectrogramSession(
                    onAnalyzeAudio = onBackClick,
                    showAnalyzeActions = false,
                    recordingHint = stringResource(R.string.night_sounds_hint),
                    saveLabel = stringResource(R.string.night_sounds_save),
                    onSaveClip = onBackClick,
                )
            }
            Spacer(modifier = Modifier.height(AnuraDimens.spaceSection))
            AnuraSectionLabel(text = stringResource(R.string.night_sounds_identified))
            Spacer(modifier = Modifier.height(AnuraDimens.spaceLabelToContent))
            Column(verticalArrangement = Arrangement.spacedBy(AnuraDimens.spaceGap)) {
                NightSoundCalls.forEach { call ->
                    NightSoundCallRow(call = call)
                }
            }
        }
    }
}

@Composable
private fun NightSoundsMetadataChip(temperature: String) {
    AnuraCard(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(AnuraDimens.radiusCapsule),
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(
                    horizontal = AnuraDimens.spaceCardInsetHorizontal,
                    vertical = AnuraDimens.spaceLabelToContent,
                ),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(AnuraDimens.spaceLabelToContent),
        ) {
            Icon(
                imageVector = AnuraIcons.FieldSession,
                contentDescription = null,
                tint = AnuraTheme.extendedColors.accentInk,
                modifier = Modifier.size(24.dp),
            )
            Text(
                text = stringResource(R.string.night_sounds_metadata, temperature),
                style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.SemiBold),
                color = MaterialTheme.colorScheme.onSurface,
                modifier = Modifier.weight(1f),
            )
        }
    }
}

@Composable
private fun NightSoundCallRow(call: NightSoundCall) {
    AnuraCard(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(AnuraDimens.radiusCard),
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(
                    horizontal = AnuraDimens.spaceCardInsetHorizontal,
                    vertical = AnuraDimens.spaceCardInsetVertical,
                ),
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Box(
                    modifier = Modifier
                        .size(14.dp)
                        .clip(CircleShape)
                        .background(AnuraTheme.extendedColors.accentInk),
                )
                Spacer(modifier = Modifier.size(AnuraDimens.spaceLabelToContent))
                Text(
                    text = stringResource(call.speciesRes),
                    style = MaterialTheme.typography.titleSmall.copy(
                        fontWeight = FontWeight.SemiBold,
                        fontStyle = FontStyle.Italic,
                    ),
                    color = MaterialTheme.colorScheme.onSurface,
                    modifier = Modifier.weight(1f),
                )
                Text(
                    text = stringResource(call.percentRes),
                    style = MaterialTheme.typography.titleSmall.copy(fontWeight = FontWeight.SemiBold),
                    color = AnuraTheme.extendedColors.accentInk,
                )
            }
            Text(
                text = stringResource(call.typeRes),
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                modifier = Modifier.padding(start = 22.dp, top = AnuraDimens.spaceLabelToContent),
            )
            Spacer(modifier = Modifier.height(AnuraDimens.spaceLabelToContent))
            LinearProgressIndicator(
                progress = { call.contribution },
                modifier = Modifier
                    .fillMaxWidth()
                    .height(6.dp)
                    .clip(RoundedCornerShape(3.dp)),
                color = AnuraTheme.extendedColors.accentInk,
                trackColor = MaterialTheme.colorScheme.surfaceVariant,
            )
        }
    }
}

@AnuraPreviews
@Composable
private fun NightSoundsPreview() {
    AnuraTheme {
        NightSoundsScreen(sessionId = "session-001", onBackClick = {})
    }
}

@Preview(name = "Luz roja", group = "modo", showBackground = true)
@Composable
private fun NightSoundsPreviewRedLight() {
    AnuraTheme(AnuraThemeMode.LuzRoja) {
        NightSoundsScreen(sessionId = "session-001", onBackClick = {})
    }
}
