package me.juanlabs.anura.feature.map

import android.graphics.Color
import android.graphics.Paint
import kotlin.math.floor
import org.osmdroid.util.GeoPoint
import org.osmdroid.views.MapView
import org.osmdroid.views.overlay.Polygon

/**
 * Puerto a osmdroid del `GridDensityLayer` de la web
 * (`D:\server\Anura\frontend\src\maps\SpeciesDistributionLayers.jsx`): cuadros que cambian de
 * tamaño según el zoom para mostrar densidad de puntos, en vez de un pin por punto. Algoritmo
 * propio (no un plugin de Leaflet ni de osmdroid) — mismo criterio en los dos lados: tabla
 * zoom→tamaño de celda en grados, cada punto cae en una celda por `floor(coord/cellSize)`,
 * opacidad según cuántos puntos caen en esa celda. Por debajo del zoom 14 no hay celda
 * (demasiado pocos puntos juntos): se ven puntos individuales.
 */
private fun cellSizeForZoom(zoom: Double): Double = when {
    zoom <= 3 -> 4.0
    zoom <= 4 -> 2.0
    zoom <= 5 -> 1.0
    zoom <= 6 -> 0.5
    zoom <= 7 -> 0.25
    zoom <= 8 -> 0.1
    zoom <= 9 -> 0.05
    zoom <= 10 -> 0.02
    zoom <= 11 -> 0.01
    zoom <= 12 -> 0.005
    zoom <= 13 -> 0.002
    else -> 0.0 // sin celda: puntos individuales (ver `usesDensityCells`)
}

/** false a partir de zoom 14 — el llamador debe volver a dibujar marcadores individuales. */
fun usesDensityCells(zoom: Double): Boolean = cellSizeForZoom(zoom) > 0.0

private data class DensityCell(val minLat: Double, val minLon: Double, val cellSize: Double, val count: Int)

private fun binPoints(points: List<Pair<Double, Double>>, cellSize: Double): List<DensityCell> {
    val counts = LinkedHashMap<Pair<Double, Double>, Int>()
    points.forEach { (lat, lon) ->
        val key = floor(lat / cellSize) * cellSize to floor(lon / cellSize) * cellSize
        counts[key] = (counts[key] ?: 0) + 1
    }
    return counts.map { (key, count) -> DensityCell(key.first, key.second, cellSize, count) }
}

/**
 * Reemplaza cualquier [Polygon] de densidad ya dibujado por celdas nuevas para [points] al
 * [zoom] actual. El llamador es responsable de los marcadores individuales (zoom ≥ 14): esta
 * función no los toca, solo limpia y agrega sus propios `Polygon`.
 */
fun MapView.drawDensityGrid(occurrences: List<Pair<Double, Double>>, zoom: Double, accentColor: Int) {
    overlays.removeAll { it is Polygon && it.id == DensityOverlayId }
    val cellSize = cellSizeForZoom(zoom)
    if (cellSize <= 0.0 || occurrences.isEmpty()) {
        invalidate()
        return
    }
    val cells = binPoints(occurrences, cellSize)
    val maxCount = cells.maxOf { it.count }
    cells.forEach { cell ->
        val alpha = (0.3f + (cell.count.toFloat() / maxCount) * 0.55f).coerceIn(0f, 1f)
        val fillColor = Color.argb((alpha * 255).toInt(), Color.red(accentColor), Color.green(accentColor), Color.blue(accentColor))
        val corners = listOf(
            GeoPoint(cell.minLat, cell.minLon),
            GeoPoint(cell.minLat, cell.minLon + cell.cellSize),
            GeoPoint(cell.minLat + cell.cellSize, cell.minLon + cell.cellSize),
            GeoPoint(cell.minLat + cell.cellSize, cell.minLon),
        )
        val polygon = Polygon(this).apply {
            id = DensityOverlayId
            setPoints(corners)
            fillPaint.color = fillColor
            fillPaint.style = Paint.Style.FILL
            outlinePaint.color = Color.argb(80, Color.red(accentColor), Color.green(accentColor), Color.blue(accentColor))
            outlinePaint.strokeWidth = 1f
        }
        overlays.add(polygon)
    }
    invalidate()
}

private const val DensityOverlayId = "anura-density-cell"

/** Mismo naranja de `ic_map_pin_square_orange.xml` (#FF7A1A) — un solo acento para todo el mapa. */
val MapDensityAccentColor: Int = Color.parseColor("#FF7A1A")
