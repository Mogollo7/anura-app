package me.juanlabs.anura.designsystem.component

import androidx.compose.foundation.border
import androidx.compose.foundation.gestures.snapping.SnapLayoutInfoProvider
import androidx.compose.foundation.gestures.snapping.SnapPosition
import androidx.compose.foundation.gestures.snapping.rememberSnapFlingBehavior
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ColumnScope
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.wrapContentHeight
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyListState
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.DatePicker
import androidx.compose.material3.DatePickerDefaults
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.SelectableDates
import androidx.compose.material3.Text
import androidx.compose.material3.rememberDatePickerState
import androidx.compose.material3.rememberModalBottomSheetState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.runtime.snapshotFlow
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlin.math.abs
import java.time.Instant
import java.time.LocalDate
import java.time.LocalTime
import java.time.ZoneOffset
import me.juanlabs.anura.R
import me.juanlabs.anura.designsystem.theme.AnuraDimens
import me.juanlabs.anura.designsystem.theme.AnuraTheme

private val PickerSheetInset = AnuraDimens.spaceGutter
private val RouletteItemHeight = AnuraDimens.sizeTouch
private const val RouletteVisibleItems = 5
private const val RouletteRepeat = 10_000

/**
 * Calendario reutilizable (`Pop-up de cambiar fecha`).
 * Misma jerarquía de botones e inset que Sign Up / Login (56 dp, [AnuraFormButton]).
 * Solo actualiza la fecha; no toca la hora.
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AnuraDatePicker(
    initialDate: LocalDate,
    onDismissRequest: () -> Unit,
    onConfirm: (LocalDate) -> Unit,
    confirmLabel: String = stringResource(R.string.anura_datetime_confirm),
    cancelLabel: String = stringResource(R.string.anura_cancel),
) {
    val dateState = rememberDatePickerState(
        initialSelectedDateMillis = initialDate
            .atStartOfDay(ZoneOffset.UTC)
            .toInstant()
            .toEpochMilli(),
        selectableDates = object : SelectableDates {
            override fun isSelectableDate(utcTimeMillis: Long): Boolean = true
        },
    )
    AnuraPickerSheet(
        onDismissRequest = onDismissRequest,
        confirmLabel = confirmLabel,
        cancelLabel = cancelLabel,
        onConfirm = {
            val millis = dateState.selectedDateMillis
            if (millis != null) {
                onConfirm(
                    Instant.ofEpochMilli(millis).atZone(ZoneOffset.UTC).toLocalDate(),
                )
            } else {
                onDismissRequest()
            }
        },
    ) {
        val sheetColor = MaterialTheme.colorScheme.surface
        val selectedGreen = AnuraTheme.extendedColors.accentInk
        DatePicker(
            state = dateState,
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = PickerSheetInset),
            title = null,
            headline = null,
            showModeToggle = false,
            colors = DatePickerDefaults.colors(
                containerColor = sheetColor,
                selectedDayContainerColor = selectedGreen,
                selectedDayContentColor = MaterialTheme.colorScheme.onPrimary,
                selectedYearContainerColor = selectedGreen,
                selectedYearContentColor = MaterialTheme.colorScheme.onPrimary,
                todayContentColor = selectedGreen,
                todayDateBorderColor = selectedGreen,
                currentYearContentColor = selectedGreen,
            ),
        )
    }
}

/**
 * Selector de hora reutilizable en rodillo vertical (ruleta).
 * Independiente del calendario: no modifica la fecha.
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AnuraTimePicker(
    initialTime: LocalTime,
    onDismissRequest: () -> Unit,
    onConfirm: (LocalTime) -> Unit,
    confirmLabel: String = stringResource(R.string.anura_datetime_confirm),
    cancelLabel: String = stringResource(R.string.anura_cancel),
) {
    var hour by remember { mutableIntStateOf(initialTime.hour) }
    var minute by remember { mutableIntStateOf(initialTime.minute) }
    val timeCd = stringResource(R.string.capture_step2_time_cd)
    AnuraPickerSheet(
        onDismissRequest = onDismissRequest,
        confirmLabel = confirmLabel,
        cancelLabel = cancelLabel,
        scrollable = false,
        onConfirm = { onConfirm(LocalTime.of(hour, minute)) },
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = PickerSheetInset)
                .semantics { contentDescription = timeCd },
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.Center,
        ) {
            AnuraVerticalRoulette(
                valueCount = 24,
                selected = hour,
                onSelected = { hour = it },
                modifier = Modifier.weight(1f),
            )
            Text(
                text = ":",
                style = MaterialTheme.typography.headlineSmall.copy(fontWeight = FontWeight.SemiBold),
                color = AnuraTheme.extendedColors.accentInk,
                modifier = Modifier.padding(horizontal = AnuraDimens.spaceGap),
            )
            AnuraVerticalRoulette(
                valueCount = 60,
                selected = minute,
                onSelected = { minute = it },
                modifier = Modifier.weight(1f),
            )
        }
    }
}

@Composable
private fun AnuraVerticalRoulette(
    valueCount: Int,
    selected: Int,
    onSelected: (Int) -> Unit,
    modifier: Modifier = Modifier,
) {
    val startIndex = remember(valueCount, selected) {
        rouletteStartIndex(valueCount, selected)
    }
    val visibleSide = (RouletteVisibleItems - 1) / 2
    val listState = rememberLazyListState(
        initialFirstVisibleItemIndex = startIndex.coerceAtLeast(0),
    )
    val snapLayout = remember(listState) {
        SnapLayoutInfoProvider(
            lazyListState = listState,
            snapPosition = SnapPosition.Center,
        )
    }
    val fling = rememberSnapFlingBehavior(snapLayout)
    val selectedGreen = AnuraTheme.extendedColors.accentInk
    val muted = MaterialTheme.colorScheme.onSurfaceVariant
    val density = LocalDensity.current
    val itemHeightPx = with(density) { RouletteItemHeight.toPx() }
    val wheelHeight = RouletteItemHeight * RouletteVisibleItems

    LaunchedEffect(listState) {
        snapshotFlow { listState.isScrollInProgress }
            .collect { scrolling ->
                if (!scrolling) {
                    val centered = centeredRouletteIndex(listState, itemHeightPx)
                    if (centered != null) {
                        onSelected(centered % valueCount)
                    }
                }
            }
    }

    Box(
        modifier = modifier.height(wheelHeight),
        contentAlignment = Alignment.Center,
    ) {
        LazyColumn(
            state = listState,
            flingBehavior = fling,
            modifier = Modifier.fillMaxWidth(),
            contentPadding = PaddingValues(vertical = RouletteItemHeight * visibleSide),
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            items(RouletteRepeat) { index ->
                val value = index % valueCount
                val distance = rouletteDistanceFromCenter(listState, index, itemHeightPx)
                val selectedItem = distance < 0.5f
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(RouletteItemHeight),
                    contentAlignment = Alignment.Center,
                ) {
                    Text(
                        text = value.toString().padStart(2, '0'),
                        modifier = Modifier
                            .wrapContentHeight(align = Alignment.CenterVertically)
                            .graphicsLayer {
                                alpha = (1.15f - distance * 0.5f).coerceIn(0.22f, 1f)
                                scaleX = (1.06f - distance * 0.08f).coerceIn(0.86f, 1f)
                                scaleY = scaleX
                            },
                        textAlign = TextAlign.Center,
                        style = MaterialTheme.typography.titleLarge.copy(
                            fontWeight = if (selectedItem) FontWeight.SemiBold else FontWeight.Normal,
                            fontSize = if (selectedItem) 22.sp else 16.sp,
                            lineHeight = 24.sp,
                        ),
                        color = if (selectedItem) selectedGreen else muted,
                    )
                }
            }
        }
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .height(RouletteItemHeight)
                .border(
                    width = 2.dp,
                    color = selectedGreen,
                    shape = RoundedCornerShape(AnuraDimens.radiusButton),
                ),
        )
    }
}

private fun rouletteStartIndex(valueCount: Int, selected: Int): Int {
    val mid = RouletteRepeat / 2
    return mid - (mid % valueCount) + selected.coerceIn(0, valueCount - 1)
}

private fun centeredRouletteIndex(state: LazyListState, itemHeightPx: Float): Int? {
    val info = state.layoutInfo
    if (info.visibleItemsInfo.isEmpty()) return null
    val viewportCenter = (info.viewportStartOffset + info.viewportEndOffset) / 2f
    return info.visibleItemsInfo.minByOrNull { item ->
        abs((item.offset + item.size / 2f) - viewportCenter)
    }?.index
}

private fun rouletteDistanceFromCenter(
    state: LazyListState,
    index: Int,
    itemHeightPx: Float,
): Float {
    val info = state.layoutInfo
    val viewportCenter = (info.viewportStartOffset + info.viewportEndOffset) / 2f
    val item = info.visibleItemsInfo.firstOrNull { it.index == index } ?: return 2f
    return abs((item.offset + item.size / 2f) - viewportCenter) / itemHeightPx
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun AnuraPickerSheet(
    onDismissRequest: () -> Unit,
    confirmLabel: String,
    cancelLabel: String,
    onConfirm: () -> Unit,
    scrollable: Boolean = true,
    content: @Composable ColumnScope.() -> Unit,
) {
    val sheetState = rememberModalBottomSheetState(skipPartiallyExpanded = true)
    val sheetColor = MaterialTheme.colorScheme.surface
    AnuraBottomSheet(
        onDismissRequest = onDismissRequest,
        sheetState = sheetState,
        containerColor = sheetColor,
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .then(if (scrollable) Modifier.verticalScroll(rememberScrollState()) else Modifier),
        ) {
            content()
            Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = PickerSheetInset),
                verticalArrangement = Arrangement.spacedBy(AnuraDimens.spaceActionGap),
            ) {
                AnuraFormButton(
                    text = confirmLabel,
                    onClick = onConfirm,
                    style = AnuraFormButtonStyle.Primary,
                )
                AnuraFormButton(
                    text = cancelLabel,
                    onClick = onDismissRequest,
                    style = AnuraFormButtonStyle.Outline,
                )
            }
            Spacer(modifier = Modifier.height(AnuraDimens.spaceSection))
        }
    }
}
