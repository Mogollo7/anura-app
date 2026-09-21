package me.juanlabs.anura.core.data

import java.time.Instant
import java.time.LocalDateTime
import java.time.ZoneId
import java.time.format.DateTimeFormatter
import java.util.Locale
import kotlin.math.abs

private val EsCo: Locale = Locale.forLanguageTag("es-CO")
private val DateFormatter: DateTimeFormatter =
    DateTimeFormatter.ofPattern("d MMM yyyy", EsCo)
private val DateTimeFormatterFull: DateTimeFormatter =
    DateTimeFormatter.ofPattern("d MMM yyyy · HH:mm", EsCo)
private val TimeFormatter: DateTimeFormatter =
    DateTimeFormatter.ofPattern("HH:mm", EsCo)

fun dayPeriodFromHour(hour: Int): String = when (hour) {
    in 5..7 -> PeriodDawn
    in 8..16 -> PeriodDay
    in 17..18 -> PeriodDusk
    else -> PeriodNight
}

fun formatObservationWhen(epochMs: Long?): String? {
    if (epochMs == null) return null
    val local = LocalDateTime.ofInstant(Instant.ofEpochMilli(epochMs), ZoneId.systemDefault())
    return local.format(DateTimeFormatterFull)
}

fun formatObservationDate(epochMs: Long?): String? {
    if (epochMs == null) return null
    val local = LocalDateTime.ofInstant(Instant.ofEpochMilli(epochMs), ZoneId.systemDefault())
    return local.format(DateFormatter)
}

fun formatClock(epochMs: Long?): String? {
    if (epochMs == null) return null
    val local = LocalDateTime.ofInstant(Instant.ofEpochMilli(epochMs), ZoneId.systemDefault())
    return local.format(TimeFormatter)
}

fun formatCoordinates(latitude: Double?, longitude: Double?): String? {
    if (latitude == null || longitude == null) return null
    val latHem = if (latitude >= 0) "N" else "S"
    val lonHem = if (longitude >= 0) "E" else "O"
    return String.format(
        EsCo,
        "%.4f°%s %.4f°%s",
        abs(latitude),
        latHem,
        abs(longitude),
        lonHem,
    )
}

fun formatElapsed(startedAtEpochMs: Long, nowEpochMs: Long = System.currentTimeMillis()): String {
    val totalSeconds = ((nowEpochMs - startedAtEpochMs).coerceAtLeast(0L) / 1000L).toInt()
    val hours = totalSeconds / 3600
    val minutes = (totalSeconds % 3600) / 60
    val seconds = totalSeconds % 60
    return String.format(EsCo, "%d:%02d:%02d", hours, minutes, seconds)
}

fun formatElapsedShort(startedAtEpochMs: Long, nowEpochMs: Long = System.currentTimeMillis()): String {
    val totalMinutes = ((nowEpochMs - startedAtEpochMs).coerceAtLeast(0L) / 60_000L).toInt()
    val hours = totalMinutes / 60
    val minutes = totalMinutes % 60
    return if (hours > 0) "${hours} h ${minutes} min" else "${minutes} min"
}

fun formatAudioDuration(durationMs: Long?): String? {
    if (durationMs == null || durationMs <= 0L) return null
    val totalSeconds = (durationMs / 1000L).toInt()
    val minutes = totalSeconds / 60
    val seconds = totalSeconds % 60
    return String.format(EsCo, "%02d:%02d", minutes, seconds)
}

fun habitatLabel(habitat: String?): String? = when (habitat) {
    HabitatLeafLitter -> "Hojarasca"
    HabitatLowVegetation -> "Vegetación baja"
    HabitatWaterBody -> "Cuerpo de agua"
    HabitatRock -> "Roca"
    else -> habitat
}

fun periodLabel(period: String?): String? = when (period) {
    PeriodDawn -> "Amanecer"
    PeriodDay -> "Día"
    PeriodDusk -> "Atardecer"
    PeriodNight -> "Noche"
    else -> period
}
