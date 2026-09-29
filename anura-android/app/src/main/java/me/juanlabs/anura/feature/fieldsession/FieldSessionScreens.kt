package me.juanlabs.anura.feature.fieldsession

import androidx.activity.compose.BackHandler
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.ime
import androidx.compose.foundation.layout.imePadding
import androidx.compose.foundation.layout.navigationBarsPadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
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
import androidx.compose.runtime.mutableLongStateOf
import androidx.compose.runtime.mutableStateMapOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import kotlinx.coroutines.delay
import me.juanlabs.anura.core.data.ObservationRecord
import me.juanlabs.anura.core.data.rememberAmbientConditions
import me.juanlabs.anura.core.data.SpeciesCatalog
import me.juanlabs.anura.core.data.formatClock
import me.juanlabs.anura.core.data.formatCoordinates
import me.juanlabs.anura.core.data.formatElapsed
import me.juanlabs.anura.core.data.rememberAnuraRepository
import me.juanlabs.anura.designsystem.component.AnuraEmptyState
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.text.font.FontStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import java.time.LocalTime
import java.time.format.DateTimeFormatter
import me.juanlabs.anura.R
import me.juanlabs.anura.designsystem.component.AnuraCard
import me.juanlabs.anura.designsystem.component.AnuraFormButton
import me.juanlabs.anura.designsystem.component.AnuraFormButtonStyle
import me.juanlabs.anura.designsystem.component.AnuraTopBar
import me.juanlabs.anura.designsystem.component.AnuraToxicityChip
import me.juanlabs.anura.designsystem.component.AnuraToxicityChipVariant
import me.juanlabs.anura.designsystem.icon.AnuraIcons
import me.juanlabs.anura.designsystem.preview.AnuraPreviews
import me.juanlabs.anura.designsystem.theme.AnuraDimens
import me.juanlabs.anura.designsystem.theme.AnuraTheme
import me.juanlabs.anura.designsystem.theme.AnuraThemeMode
import me.juanlabs.anura.feature.home.HomeQuickActions

private const val FieldSessionNoteMaxChars = 500

/**
 * `Salida de campo en curso` (§4.1, argumento `sessionId`).
 *
 * Board Penpot: cronómetro, variables ambientales, registros, identificación
 * y sonidos nocturnos.
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun FieldSessionScreen(
    sessionId: String,
    onBackClick: () -> Unit,
    onOpenNightSounds: (String) -> Unit,
    onOpenNotes: (String) -> Unit,
    onPhotoId: () -> Unit,
    onAudioId: () -> Unit,
    onStepByStep: () -> Unit,
    onOpenRegister: (String) -> Unit,
    onCloseSession: () -> Unit,
) {
    val repository = rememberAnuraRepository()
    val snapshot by repository.state.collectAsState()
    val session = snapshot.fieldSessions.find { it.id == sessionId }
    var now by remember { mutableLongStateOf(System.currentTimeMillis()) }
    LaunchedEffect(sessionId) {
        while (true) {
            now = System.currentTimeMillis()
            delay(1_000)
        }
    }
    val missing = stringResource(R.string.anura_value_missing)
    val climate = rememberAmbientConditions(session?.latitude, session?.longitude)
    val locationLabel = session?.placeLabel
        ?: formatCoordinates(session?.latitude, session?.longitude)
        ?: stringResource(R.string.field_session_location_missing)
    val elapsed = session?.let { formatElapsed(it.startedAtEpochMs, now) } ?: "00:00:00"
    val registers = snapshot.observations.filter { it.fieldSessionId == sessionId }
    Scaffold(
        containerColor = AnuraTheme.extendedColors.boardBackground,
        topBar = {
            AnuraTopBar(
                title = stringResource(R.string.field_session_title),
                onBackClick = onBackClick,
                centerTitle = true,
                actions = {
                    IconButton(
                        onClick = { onOpenNotes(sessionId) },
                        modifier = Modifier.size(AnuraDimens.sizeTouch),
                    ) {
                        Icon(
                            imageVector = AnuraIcons.Notes,
                            contentDescription = stringResource(R.string.field_session_notes_cd),
                            tint = AnuraTheme.extendedColors.accentInk,
                        )
                    }
                },
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
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(AnuraDimens.spaceLabelToContent),
            ) {
                Box(
                    modifier = Modifier
                        .size(12.dp)
                        .clip(CircleShape)
                        .background(AnuraTheme.extendedColors.accentInk),
                )
                Text(
                    text = locationLabel,
                    style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.SemiBold),
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis,
                    modifier = Modifier.weight(1f),
                )
            }
            Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(AnuraDimens.spaceLabelToContent),
            ) {
                Text(
                    text = elapsed,
                    style = MaterialTheme.typography.headlineMedium.copy(fontWeight = FontWeight.Bold),
                    color = MaterialTheme.colorScheme.onSurface,
                    modifier = Modifier.weight(1f),
                )
                Button(
                    onClick = onCloseSession,
                    modifier = Modifier.heightIn(min = AnuraDimens.sizeTouch),
                    shape = RoundedCornerShape(AnuraDimens.radiusButton),
                    colors = ButtonDefaults.buttonColors(
                        containerColor = AnuraTheme.extendedColors.accentInk,
                        contentColor = MaterialTheme.colorScheme.onPrimary,
                    ),
                    contentPadding = PaddingValues(horizontal = AnuraDimens.spaceGap),
                ) {
                    Text(
                        text = stringResource(R.string.field_session_end),
                        style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.SemiBold),
                    )
                }
            }
            Spacer(modifier = Modifier.height(AnuraDimens.spaceSection))
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(AnuraDimens.spaceLabelToContent),
            ) {
                FieldSessionVariableCard(
                    value = climate.temperature,
                    label = stringResource(R.string.field_session_temp_label),
                    modifier = Modifier.weight(1f),
                )
                FieldSessionVariableCard(
                    value = climate.humidity,
                    label = stringResource(R.string.field_session_humidity_label),
                    modifier = Modifier.weight(1f),
                )
                FieldSessionVariableCard(
                    value = session?.altitudeLabel ?: missing,
                    label = stringResource(R.string.field_session_altitude_label),
                    modifier = Modifier.weight(1f),
                )
                FieldSessionVariableCard(
                    value = climate.precipitation,
                    label = stringResource(R.string.field_session_rain_label),
                    modifier = Modifier.weight(1f),
                )
            }
            Spacer(modifier = Modifier.height(AnuraDimens.spaceSection))
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Text(
                    text = stringResource(R.string.field_session_registers),
                    style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.SemiBold),
                    color = MaterialTheme.colorScheme.onSurface,
                    modifier = Modifier.weight(1f),
                )
                Text(
                    text = stringResource(R.string.field_session_registers_count, registers.size),
                    style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.SemiBold),
                    color = AnuraTheme.extendedColors.accentInk,
                    textAlign = TextAlign.End,
                )
            }
            Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))
            if (registers.isEmpty()) {
                AnuraEmptyState(
                    title = stringResource(R.string.field_session_empty_registers),
                    description = stringResource(R.string.observations_empty_body),
                )
            } else {
                Column(verticalArrangement = Arrangement.spacedBy(AnuraDimens.spaceGap)) {
                    registers.forEach { observation ->
                        FieldSessionObservationRow(
                            observation = observation,
                            onOpen = { onOpenRegister(observation.id) },
                        )
                    }
                }
            }
            Spacer(modifier = Modifier.height(AnuraDimens.spaceSection))
            HomeQuickActions(
                onStepByStep = onStepByStep,
                onPhotoId = onPhotoId,
                onAudioId = onAudioId,
                modifier = Modifier.fillMaxWidth(),
            )
            Spacer(modifier = Modifier.height(AnuraDimens.spaceActionGap))
            AnuraFormButton(
                text = stringResource(R.string.field_session_night_sounds),
                onClick = { onOpenNightSounds(sessionId) },
                style = AnuraFormButtonStyle.Outline,
                icon = AnuraIcons.AudioId,
            )
        }
    }
}

@Composable
private fun FieldSessionVariableCard(
    value: String,
    label: String,
    modifier: Modifier = Modifier,
) {
    AnuraCard(
        modifier = modifier,
        shape = RoundedCornerShape(AnuraDimens.radiusModal),
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(
                    horizontal = AnuraDimens.spaceLabelToContent,
                    vertical = AnuraDimens.spaceGap,
                ),
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            Text(
                text = value,
                style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.SemiBold),
                color = MaterialTheme.colorScheme.onSurface,
                textAlign = TextAlign.Center,
                maxLines = 1,
                overflow = TextOverflow.Ellipsis,
            )
            Text(
                text = label,
                style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.Medium),
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                textAlign = TextAlign.Center,
                maxLines = 1,
                overflow = TextOverflow.Ellipsis,
            )
        }
    }
}

@Composable
private fun FieldSessionObservationRow(
    observation: ObservationRecord,
    onOpen: () -> Unit,
) {
    val species = SpeciesCatalog.find(observation.speciesId)
    val unidentified = stringResource(R.string.observation_unidentified_scientific)
    val openCd = stringResource(R.string.field_session_register_open_cd)
    val time = formatClock(observation.observedAtEpochMs)
        ?: formatClock(observation.createdAtEpochMs)
        ?: "—"
    val name = observation.scientificName ?: species?.scientificName ?: unidentified
    val media = buildString {
        if (observation.photoTokens.isNotEmpty() || observation.photoUrl != null) append("Foto")
        if (observation.audioPath != null) {
            if (isNotEmpty()) append(" · ")
            append("Audio")
        }
    }.ifBlank { stringResource(R.string.anura_value_missing) }
    val toxic = species?.toxicity == AnuraToxicityChipVariant.Toxic
    AnuraCard(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(
                role = Role.Button,
                onClickLabel = openCd,
                onClick = onOpen,
            ),
        shape = RoundedCornerShape(AnuraDimens.radiusButton),
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(
                    horizontal = AnuraDimens.spaceCardInsetHorizontal,
                    vertical = AnuraDimens.spaceCardInsetVertical,
                ),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(AnuraDimens.spaceGap),
        ) {
            Text(
                text = time,
                style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.SemiBold),
                color = AnuraTheme.extendedColors.accentInk,
            )
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = name,
                    style = MaterialTheme.typography.titleMedium.copy(fontStyle = FontStyle.Italic),
                    color = MaterialTheme.colorScheme.onSurface,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis,
                )
                Text(
                    text = media,
                    style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.Medium),
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis,
                )
            }
            if (toxic) {
                AnuraToxicityChip(variant = AnuraToxicityChipVariant.Toxic)
            }
            Icon(
                imageVector = AnuraIcons.ChevronRight,
                contentDescription = null,
                tint = AnuraTheme.extendedColors.accentInk,
                modifier = Modifier.size(24.dp),
            )
        }
    }
}

@AnuraPreviews
@Composable
private fun FieldSessionPreview() {
    AnuraTheme {
        FieldSessionScreen(
            sessionId = "session-001",
            onBackClick = {},
            onOpenNightSounds = {},
            onOpenNotes = {},
            onPhotoId = {},
            onAudioId = {},
            onStepByStep = {},
            onOpenRegister = {},
            onCloseSession = {},
        )
    }
}

@Preview(name = "Luz roja", group = "modo", showBackground = true)
@Composable
private fun FieldSessionPreviewRedLight() {
    AnuraTheme(AnuraThemeMode.LuzRoja) {
        FieldSessionScreen(
            sessionId = "session-001",
            onBackClick = {},
            onOpenNightSounds = {},
            onOpenNotes = {},
            onPhotoId = {},
            onAudioId = {},
            onStepByStep = {},
            onOpenRegister = {},
            onCloseSession = {},
        )
    }
}

/** `Notas de la salida de campo` (§4.1, argumento `sessionId`). */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun FieldSessionNotesScreen(
    sessionId: String,
    onBackClick: () -> Unit,
) {
    val repository = rememberAnuraRepository()
    val snapshot by repository.state.collectAsState()
    val registers = snapshot.observations.filter { it.fieldSessionId == sessionId }
    var selectedObservationId by rememberSaveable(sessionId) { mutableStateOf<String?>(null) }
    val selected = selectedObservationId?.let { id -> registers.find { it.id == id } }
    BackHandler(enabled = selected != null) { selectedObservationId = null }
    val imeVisible = WindowInsets.ime.getBottom(LocalDensity.current) > 0
    Scaffold(
        containerColor = AnuraTheme.extendedColors.boardBackground,
        contentWindowInsets = WindowInsets(0, 0, 0, 0),
        topBar = {
            AnuraTopBar(
                title = stringResource(R.string.field_session_notes_title),
                onBackClick = {
                    if (selectedObservationId != null) {
                        selectedObservationId = null
                    } else {
                        onBackClick()
                    }
                },
                centerTitle = true,
            )
        },
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .then(
                    if (imeVisible) {
                        Modifier.imePadding()
                    } else {
                        Modifier.navigationBarsPadding()
                    },
                )
                .verticalScroll(rememberScrollState())
                .padding(horizontal = AnuraDimens.spaceGutter)
                .padding(top = AnuraDimens.spaceTopBarToContent)
                .padding(bottom = if (imeVisible) 0.dp else AnuraDimens.spaceSection),
        ) {
            if (selected == null) {
                Text(
                    text = stringResource(R.string.field_session_notes_pick),
                    style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.SemiBold),
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
                Spacer(modifier = Modifier.height(AnuraDimens.spaceLabelToContent))
                if (registers.isEmpty()) {
                    AnuraEmptyState(title = stringResource(R.string.field_session_empty_registers))
                } else {
                    Column(verticalArrangement = Arrangement.spacedBy(AnuraDimens.spaceGap)) {
                        registers.forEach { observation ->
                            FieldSessionObservationRow(
                                observation = observation,
                                onOpen = { selectedObservationId = observation.id },
                            )
                        }
                    }
                }
            } else {
                FieldSessionObservationRow(
                    observation = selected,
                    onOpen = { selectedObservationId = null },
                )
                Spacer(modifier = Modifier.height(AnuraDimens.spaceLabelToContent))
                Text(
                    text = stringResource(R.string.field_session_notes_change),
                    style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.Medium),
                    color = AnuraTheme.extendedColors.accentInk,
                )
                Spacer(modifier = Modifier.height(AnuraDimens.spaceSection))
                FieldSessionRecordNotes(
                    observationId = selected.id,
                    sessionId = sessionId,
                )
            }
        }
    }
}

@Composable
internal fun FieldSessionRecordNotes(
    observationId: String,
    sessionId: String? = null,
    modifier: Modifier = Modifier,
) {
    val repository = rememberAnuraRepository()
    val snapshot by repository.state.collectAsState()
    var draft by rememberSaveable(observationId) { mutableStateOf("") }
    val resolvedSessionId = sessionId
        ?: snapshot.observations.find { it.id == observationId }?.fieldSessionId
    val notes = snapshot.sessionNotes.filter {
        it.observationId == observationId || (it.sessionId == resolvedSessionId && it.observationId == observationId)
    }
    val placeholder = stringResource(R.string.field_session_notes_placeholder)
    Column(modifier = modifier.fillMaxWidth()) {
        AnuraCard(
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(AnuraDimens.radiusCard),
        ) {
            BasicTextField(
                value = draft,
                onValueChange = { if (it.length <= FieldSessionNoteMaxChars) draft = it },
                modifier = Modifier
                    .fillMaxWidth()
                    .heightIn(min = 140.dp)
                    .padding(
                        horizontal = AnuraDimens.spaceCardInsetHorizontal,
                        vertical = AnuraDimens.spaceCardInsetVertical,
                    ),
                textStyle = MaterialTheme.typography.titleLarge.copy(
                    fontWeight = FontWeight.Normal,
                    color = MaterialTheme.colorScheme.onSurface,
                ),
                cursorBrush = SolidColor(MaterialTheme.colorScheme.onSurface),
                decorationBox = { inner ->
                    if (draft.isEmpty()) {
                        Text(
                            text = placeholder,
                            style = MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.Normal),
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                        )
                    }
                    inner()
                },
            )
        }
        Spacer(modifier = Modifier.height(AnuraDimens.spaceLabelToContent))
        Text(
            text = stringResource(
                R.string.field_session_notes_counter,
                draft.length,
                FieldSessionNoteMaxChars,
            ),
            style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.Normal),
            color = MaterialTheme.colorScheme.onSurface,
            textAlign = TextAlign.End,
            modifier = Modifier.fillMaxWidth(),
        )
        Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))
        AnuraFormButton(
            text = stringResource(R.string.field_session_notes_save),
            onClick = {
                val body = draft.trim()
                if (body.isEmpty()) return@AnuraFormButton
                resolvedSessionId?.let { repository.addSessionNote(it, body, observationId) }
                draft = ""
            },
            enabled = draft.trim().isNotEmpty(),
        )
        Spacer(modifier = Modifier.height(AnuraDimens.spaceSection))
        Text(
            text = stringResource(R.string.field_session_notes_saved),
            style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.SemiBold),
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        Spacer(modifier = Modifier.height(AnuraDimens.spaceLabelToContent))
        if (notes.isEmpty()) {
            Text(
                text = stringResource(R.string.field_session_notes_empty),
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        } else {
            Column(verticalArrangement = Arrangement.spacedBy(AnuraDimens.spaceGap)) {
                notes.forEach { note ->
                    FieldSessionSavedNoteCard(
                        time = formatClock(note.createdAtEpochMs) ?: "",
                        body = note.body,
                    )
                }
            }
        }
    }
}

@Composable
private fun FieldSessionSavedNoteCard(time: String, body: String) {
    AnuraCard(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(AnuraDimens.radiusButton),
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(
                    horizontal = AnuraDimens.spaceCardInsetHorizontal,
                    vertical = AnuraDimens.spaceGap,
                ),
        ) {
            Text(
                text = time,
                style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.Normal),
                color = AnuraTheme.extendedColors.accentInk,
            )
            Text(
                text = body,
                style = MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.Normal),
                color = MaterialTheme.colorScheme.onSurface,
            )
        }
    }
}

@AnuraPreviews
@Composable
private fun FieldSessionNotesPreview() {
    AnuraTheme {
        FieldSessionNotesScreen(sessionId = "session-001", onBackClick = {})
    }
}

@Preview(name = "Luz roja", group = "modo", showBackground = true)
@Composable
private fun FieldSessionNotesPreviewRedLight() {
    AnuraTheme(AnuraThemeMode.LuzRoja) {
        FieldSessionNotesScreen(sessionId = "session-001", onBackClick = {})
    }
}
