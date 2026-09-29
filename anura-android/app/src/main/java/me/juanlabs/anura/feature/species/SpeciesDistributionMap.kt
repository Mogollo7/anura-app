package me.juanlabs.anura.feature.species

import android.content.Context
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.viewinterop.AndroidView
import androidx.core.content.ContextCompat
import java.io.File
import me.juanlabs.anura.R
import me.juanlabs.anura.feature.map.MapDensityAccentColor
import me.juanlabs.anura.feature.map.drawDensityGrid
import me.juanlabs.anura.feature.map.usesDensityCells
import org.osmdroid.config.Configuration
import org.osmdroid.events.MapListener
import org.osmdroid.events.ScrollEvent
import org.osmdroid.events.ZoomEvent
import org.osmdroid.tileprovider.tilesource.TileSourceFactory
import org.osmdroid.util.BoundingBox
import org.osmdroid.util.GeoPoint
import org.osmdroid.views.MapView
import org.osmdroid.views.overlay.Marker
import org.osmdroid.views.overlay.Polygon

private val DistributionMapDefaultCenter = GeoPoint(5.0689, -75.5174)
private const val DistributionMapDefaultZoom = 8.0
private const val DistributionMapSinglePointZoom = 11.0

/**
 * Mapa de distribución de una ficha técnica — mismo criterio visual que el mapa de la web
 * (`SpeciesDistributionLayers.jsx`): cuadros de densidad que cambian de tamaño según el zoom
 * (ver `feature/map/GridDensityOverlay.kt`), y pines individuales cuando el zoom ya separa los
 * puntos (≥14). De la especie si la ficha es de especie, de todas las especies del género o de
 * la familia si la ficha es de género/familia. Solo lectura: sin GPS, sin arrastre — nada más
 * del mapa cambia.
 */
@Composable
fun SpeciesDistributionMap(
    points: List<Pair<Double, Double>>,
    modifier: Modifier = Modifier,
) {
    val context = LocalContext.current
    val accentColor = MapDensityAccentColor
    val mapView = remember {
        configureDistributionOsmdroid(context)
        MapView(context).apply {
            setTileSource(TileSourceFactory.MAPNIK)
            setMultiTouchControls(true)
            isTilesScaledToDpi = true
            setOnTouchListener { view, _ ->
                view.parent?.requestDisallowInterceptTouchEvent(true)
                false
            }
            minZoomLevel = 4.0
            maxZoomLevel = 19.0
            controller.setZoom(DistributionMapDefaultZoom)
            controller.setCenter(DistributionMapDefaultCenter)
        }
    }
    var latestPoints by remember { mutableStateOf(points) }

    fun redraw(map: MapView) {
        val zoom = map.zoomLevelDouble
        if (usesDensityCells(zoom)) {
            map.overlays.removeAll { it is Marker }
            map.drawDensityGrid(latestPoints, zoom, accentColor)
        } else {
            map.overlays.removeAll { it is Polygon || it is Marker }
            latestPoints.forEach { (lat, lon) ->
                map.overlays.add(
                    Marker(map).apply {
                        position = GeoPoint(lat, lon)
                        icon = ContextCompat.getDrawable(context, R.drawable.ic_map_pin_square_orange)
                        setAnchor(Marker.ANCHOR_CENTER, Marker.ANCHOR_CENTER)
                        isDraggable = false
                    },
                )
            }
            map.invalidate()
        }
    }

    DisposableEffect(mapView) {
        mapView.onResume()
        val listener = object : MapListener {
            override fun onScroll(event: ScrollEvent?): Boolean {
                redraw(mapView)
                return true
            }

            override fun onZoom(event: ZoomEvent?): Boolean {
                redraw(mapView)
                return true
            }
        }
        mapView.addMapListener(listener)
        onDispose {
            mapView.removeMapListener(listener)
            mapView.onPause()
        }
    }

    AndroidView(
        factory = { mapView },
        modifier = modifier.fillMaxSize(),
        update = { map ->
            latestPoints = points
            val geoPoints = points.map { (lat, lon) -> GeoPoint(lat, lon) }
            redraw(map)
            when {
                geoPoints.size == 1 -> {
                    map.controller.setCenter(geoPoints.first())
                    map.controller.setZoom(DistributionMapSinglePointZoom)
                }
                geoPoints.size > 1 -> map.post {
                    runCatching {
                        map.zoomToBoundingBox(BoundingBox.fromGeoPoints(geoPoints), false, 64)
                    }
                }
            }
        },
    )
}

private fun configureDistributionOsmdroid(context: Context) {
    val base = File(context.cacheDir, "osmdroid")
    Configuration.getInstance().apply {
        osmdroidBasePath = base
        osmdroidTileCache = File(base, "tiles")
        userAgentValue = context.packageName
        load(context, context.getSharedPreferences("osmdroid", Context.MODE_PRIVATE))
    }
}
