package me.juanlabs.anura.feature.capture

import androidx.compose.animation.animateColorAsState
import androidx.compose.animation.core.tween
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.role
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter
import java.util.Locale
import me.juanlabs.anura.R
import me.juanlabs.anura.designsystem.component.AnuraCard
import me.juanlabs.anura.designsystem.component.AnuraDatePicker
import me.juanlabs.anura.designsystem.component.AnuraSectionLabel
import me.juanlabs.anura.designsystem.component.AnuraTimePicker
import me.juanlabs.anura.designsystem.icon.AnuraIcons
import me.juanlabs.anura.designsystem.preview.AnuraPreviews
import me.juanlabs.anura.designsystem.theme.AnuraDimens
import me.juanlabs.anura.designsystem.theme.AnuraMotion
import me.juanlabs.anura.designsystem.theme.AnuraTheme
import me.juanlabs.anura.designsystem.theme.AnuraThemeMode

private val CaptureEsCo = Locale.forLanguageTag("es-CO")
private val CaptureMockDateTime = LocalDateTime.of(2026, 9, 7, 21, 47)
private val CaptureDayChipSize = 80.dp

private enum class CaptureDayPeriod {
    Dawn,
    Day,
    Dusk,
    Night,
}

/** `Paso 2: cuándo la viste` (§4.1). Estados: contenido mock (fecha/hora/clima). */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CaptureStep2Screen(
    onBackClick: () -> Unit,
    onNext: () -> Unit,
    onSkip: () -> Unit = onNext,
    fromReview: Boolean = false,
    onSave: () -> Unit = onNext,
    onCancel: () -> Unit = onBackClick,
    onCloseClick: () -> Unit = onBackClick,
) {
    var dateTime by rememberSaveable { mutableStateOf(CaptureMockDateTime.toString()) }
    val parsed = remember(dateTime) { LocalDateTime.parse(dateTime) }
    var period by rememberSaveable { mutableStateOf(CaptureDayPeriod.Night) }
    var showDatePicker by remember { mutableStateOf(false) }
    var showTimePicker by remember { mutableStateOf(false) }

    val dateLine = remember(parsed) {
        parsed.format(DateTimeFormatter.ofPattern("EEEE d 'de' MMMM", CaptureEsCo))
            .replaceFirstChar { if (it.isLowerCase()) it.titlecase(CaptureEsCo) else it.toString() }
    }
    val yearLine = parsed.year.toString()
    val timeLine = stringResource(
        R.string.capture_step2_time_local,
        parsed.format(DateTimeFormatter.ofPattern("HH:mm")),
    )

    CaptureWizardScaffold(
        appBarTitle = stringResource(R.string.capture_step2_appbar),
        step = 2,
        onBackClick = onBackClick,
        onCloseClick = onCloseClick,
        unsavedChanges = fromReview,
        showSkipNote = !fromReview,
    ) {
        CaptureWizardHeading(
            title = stringResource(R.string.capture_step2_title),
            subtitle = stringResource(R.string.capture_step2_subtitle),
        )

        val dateCd = stringResource(R.string.capture_step2_date_cd)
        val timeCd = stringResource(R.string.capture_step2_time_cd)
        AnuraCard(modifier = Modifier.fillMaxWidth()) {
            Column(
                modifier = Modifier.padding(
                    horizontal = AnuraDimens.spaceCardInsetHorizontal,
                    vertical = AnuraDimens.spaceCardInsetVertical,
                ),
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .semantics { contentDescription = dateCd }
                        .clickable(role = Role.Button, onClick = { showDatePicker = true }),
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    Icon(
                        imageVector = AnuraIcons.Calendar,
                        contentDescription = null,
                        tint = AnuraTheme.extendedColors.accentInk,
                        modifier = Modifier.size(32.dp),
                    )
                    Spacer(modifier = Modifier.size(16.dp))
                    Column {
                        Text(
                            text = dateLine,
                            style = MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.SemiBold),
                            color = MaterialTheme.colorScheme.onSurface,
                            maxLines = 1,
                            overflow = TextOverflow.Ellipsis,
                        )
                        Text(
                            text = yearLine,
                            style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.Normal),
                            color = MaterialTheme.colorScheme.onSurface,
                        )
                    }
                }
                Spacer(modifier = Modifier.height(12.dp))
                HorizontalDivider(color = MaterialTheme.colorScheme.outlineVariant)
                Spacer(modifier = Modifier.height(8.dp))
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .semantics { contentDescription = timeCd }
                        .clickable(role = Role.Button, onClick = { showTimePicker = true }),
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    Box(
                        modifier = Modifier.size(32.dp),
                        contentAlignment = Alignment.Center,
                    ) {
                        Icon(
                            imageVector = AnuraIcons.Schedule,
                            contentDescription = null,
                            tint = MaterialTheme.colorScheme.onSurfaceVariant,
                            modifier = Modifier.size(22.dp),
                        )
                    }
                    Spacer(modifier = Modifier.size(16.dp))
                    Text(
                        text = timeLine,
                        style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.Normal),
                        color = MaterialTheme.colorScheme.onSurface,
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(20.dp))

        AnuraSectionLabel(stringResource(R.string.capture_step2_day_period))
        Spacer(modifier = Modifier.height(AnuraDimens.spaceLabelToContent))
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(10.dp),
        ) {
            CaptureDayPeriod.entries.forEach { option ->
                CaptureDayPeriodChip(
                    period = option,
                    selected = period == option,
                    onClick = { period = option },
                    modifier = Modifier.weight(1f),
                )
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        CaptureWeatherCard()

        Spacer(modifier = Modifier.height(CaptureContentToFooterGap))

        CaptureWizardStepFooter(
            fromReview = fromReview,
            onSkip = onSkip,
            onNext = onNext,
            onSave = onSave,
            onCancel = onCancel,
        )
    }

    if (showDatePicker) {
        AnuraDatePicker(
            initialDate = parsed.toLocalDate(),
            onDismissRequest = { showDatePicker = false },
            onConfirm = { selected ->
                dateTime = parsed.with(selected).toString()
                showDatePicker = false
            },
        )
    }
    if (showTimePicker) {
        AnuraTimePicker(
            initialTime = parsed.toLocalTime(),
            onDismissRequest = { showTimePicker = false },
            onConfirm = { selected ->
                dateTime = parsed.with(selected).toString()
                showTimePicker = false
            },
        )
    }
}

@Composable
private fun CaptureDayPeriodChip(
    period: CaptureDayPeriod,
    selected: Boolean,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val (labelRes, icon) = when (period) {
        CaptureDayPeriod.Dawn -> R.string.capture_step2_dawn to AnuraIcons.Dawn
        CaptureDayPeriod.Day -> R.string.capture_step2_day to AnuraIcons.Day
        CaptureDayPeriod.Dusk -> R.string.capture_step2_dusk to AnuraIcons.Dusk
        CaptureDayPeriod.Night -> R.string.capture_step2_night to AnuraIcons.Night
    }
    val container by animateColorAsState(
        targetValue = if (selected) AnuraTheme.extendedColors.accentInk else MaterialTheme.colorScheme.surface,
        animationSpec = tween(AnuraMotion.DurationShort),
        label = "CaptureDayPeriodChipContainer",
    )
    val content by animateColorAsState(
        targetValue = if (selected) MaterialTheme.colorScheme.onPrimary else MaterialTheme.colorScheme.onSurface,
        animationSpec = tween(AnuraMotion.DurationShort),
        label = "CaptureDayPeriodChipContent",
    )
    Surface(
        selected = selected,
        onClick = onClick,
        modifier = modifier
            .height(CaptureDayChipSize)
            .semantics { role = Role.RadioButton },
        shape = RoundedCornerShape(AnuraDimens.radiusCard),
        color = container,
        shadowElevation = 0.dp,
        tonalElevation = 0.dp,
    ) {
        Column(
            modifier = Modifier.padding(top = 16.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            Icon(
                imageVector = icon,
                contentDescription = null,
                tint = content,
                modifier = Modifier.size(24.dp),
            )
            Text(
                text = stringResource(labelRes),
                style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.SemiBold),
                color = content,
                textAlign = TextAlign.Center,
                maxLines = 1,
                overflow = TextOverflow.Ellipsis,
            )
        }
    }
}

@Composable
private fun CaptureWeatherCard() {
    AnuraCard(modifier = Modifier.fillMaxWidth(), bordered = true) {
        Column(
            modifier = Modifier.padding(
                horizontal = AnuraDimens.spaceCardInsetHorizontal,
                vertical = AnuraDimens.spaceCardInsetVertical,
            ),
        ) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(
                    imageVector = AnuraIcons.Info,
                    contentDescription = null,
                    tint = MaterialTheme.colorScheme.onSurfaceVariant,
                    modifier = Modifier.size(20.dp),
                )
                Spacer(modifier = Modifier.size(8.dp))
                Text(
                    text = stringResource(R.string.capture_step2_weather_auto),
                    style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.SemiBold),
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
            Spacer(modifier = Modifier.height(10.dp))
            Row(modifier = Modifier.fillMaxWidth()) {
                CaptureWeatherStat(
                    label = stringResource(R.string.capture_step2_temp_label),
                    value = stringResource(R.string.capture_step2_temp_value),
                    modifier = Modifier.weight(1f),
                )
                CaptureWeatherStat(
                    label = stringResource(R.string.capture_step2_humidity_label),
                    value = stringResource(R.string.capture_step2_humidity_value),
                    modifier = Modifier.weight(1f),
                )
                CaptureWeatherStat(
                    label = stringResource(R.string.capture_step2_precip_label),
                    value = stringResource(R.string.capture_step2_precip_value),
                    modifier = Modifier.weight(1f),
                )
            }
        }
    }
}

@Composable
private fun CaptureWeatherStat(
    label: String,
    value: String,
    modifier: Modifier = Modifier,
) {
    Column(modifier = modifier) {
        Text(
            text = label,
            style = MaterialTheme.typography.labelSmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        Text(
            text = value,
            style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.SemiBold),
            color = MaterialTheme.colorScheme.onSurface,
            maxLines = 1,
            overflow = TextOverflow.Ellipsis,
        )
    }
}

@AnuraPreviews
@Composable
private fun CaptureStep2Preview() {
    AnuraTheme { CaptureStep2Screen(onBackClick = {}, onNext = {}) }
}

@Preview(name = "Luz roja", group = "modo", showBackground = true)
@Composable
private fun CaptureStep2PreviewRedLight() {
    AnuraTheme(AnuraThemeMode.LuzRoja) { CaptureStep2Screen(onBackClick = {}, onNext = {}) }
}
