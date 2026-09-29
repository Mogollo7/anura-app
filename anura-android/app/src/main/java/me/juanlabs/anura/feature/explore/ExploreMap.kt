package me.juanlabs.anura.feature.explore

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
import org.osmdroid.util.GeoPoint
import org.osmdroid.views.MapView
import org.osmdroid.views.overlay.Marker
import org.osmdroid.views.overlay.Polygon

private val ExploreMapCenter = GeoPoint(5.0689, -75.5174)
private const val ExploreMapZoom = 12.0

data class ExploreMapPin(
    val id: String,
    val latitude: Double,
    val longitude: Double,
    val title: String,
)

/**
 * Mapa OSM del board `explorar` (cluster de observaciones) — mismo criterio visual que el mapa de
 * la web (`SpeciesDistributionLayers.jsx`, ver `feature/map/GridDensityOverlay.kt`): cuadros de
 * densidad que cambian de tamaño según el zoom, pines individuales clicables cuando el zoom ya
 * separa los puntos (≥14). Pan y zoom; sin GPS en esta pantalla.
 */
@Composable
fun ExploreOsmMap(
    pins: List<ExploreMapPin>,
    onPinClick: (String) -> Unit,
    modifier: Modifier = Modifier,
) {
    val context = LocalContext.current
    val accentColor = MapDensityAccentColor
    val mapView = remember {
        configureExploreOsmdroid(context)
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
            controller.setZoom(ExploreMapZoom)
            controller.setCenter(ExploreMapCenter)
        }
    }
    var latestPins by remember { mutableStateOf(pins) }

    fun redraw(map: MapView) {
        val zoom = map.zoomLevelDouble
        if (usesDensityCells(zoom)) {
            map.overlays.removeAll { it is Marker }
            map.drawDensityGrid(latestPins.map { it.latitude to it.longitude }, zoom, accentColor)
        } else {
            map.overlays.removeAll { it is Polygon || it is Marker }
            latestPins.forEach { pin ->
                map.overlays.add(
                    Marker(map).apply {
                        position = GeoPoint(pin.latitude, pin.longitude)
                        title = pin.title
                        icon = ContextCompat.getDrawable(context, R.drawable.ic_map_pin_square_orange)
                        setAnchor(Marker.ANCHOR_CENTER, Marker.ANCHOR_CENTER)
                        isDraggable = false
                        setOnMarkerClickListener { _, _ ->
                            onPinClick(pin.id)
                            true
                        }
                    },
                )
            }
        }
        map.invalidate()
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
            latestPins = pins
            redraw(map)
        },
    )
}

private fun configureExploreOsmdroid(context: Context) {
    val base = File(context.cacheDir, "osmdroid")
    Configuration.getInstance().apply {
        osmdroidBasePath = base
        osmdroidTileCache = File(base, "tiles")
        userAgentValue = context.packageName
        load(context, context.getSharedPreferences("osmdroid", Context.MODE_PRIVATE))
    }
}
