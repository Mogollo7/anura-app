package me.juanlabs.anura.feature.capture

import android.annotation.SuppressLint
import android.content.Context
import android.location.Location
import android.location.LocationListener
import android.location.LocationManager
import android.os.Bundle
import android.os.Looper
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberUpdatedState
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.viewinterop.AndroidView
import androidx.core.content.ContextCompat
import java.io.File
import java.util.concurrent.atomic.AtomicBoolean
import me.juanlabs.anura.R
import org.osmdroid.config.Configuration
import org.osmdroid.events.MapEventsReceiver
import org.osmdroid.tileprovider.tilesource.TileSourceFactory
import org.osmdroid.util.GeoPoint
import org.osmdroid.views.MapView
import org.osmdroid.views.overlay.MapEventsOverlay
import org.osmdroid.views.overlay.Marker

/** Centro de Colombia (Caldas) hasta que haya un fix GPS. */
private val DefaultMapPoint = GeoPoint(5.0689, -75.5174)
private const val DefaultZoomWithoutFix = 6.0
private const val DefaultZoomWithFix = 16.0

/**
 * Mapa OSM interactivo del Paso 1: pan, zoom y marcador arrastrable.
 * El GPS solo se escucha si [locationEnabled] es verdadero. Hasta que haya un punto real
 * (GPS, toque o arrastre, o [initialPoint] de una visita anterior) no se dibuja marcador:
 * el centro de Colombia solo es la vista inicial, no una ubicación.
 */
@Composable
fun CaptureOsmMap(
    locationEnabled: Boolean,
    onLocationChanged: (Location) -> Unit,
    modifier: Modifier = Modifier,
    initialPoint: Pair<Double, Double>? = null,
) {
    val context = LocalContext.current
    val mapView = remember {
        configureOsmdroid(context)
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
            if (initialPoint != null) {
                controller.setZoom(DefaultZoomWithFix)
                controller.setCenter(GeoPoint(initialPoint.first, initialPoint.second))
            } else {
                controller.setZoom(DefaultZoomWithoutFix)
                controller.setCenter(DefaultMapPoint)
            }
        }
    }
    val marker = remember(mapView) {
        Marker(mapView).apply {
            position = initialPoint?.let { GeoPoint(it.first, it.second) } ?: DefaultMapPoint
            icon = ContextCompat.getDrawable(context, R.drawable.ic_map_pin_square_orange)
            setAnchor(Marker.ANCHOR_CENTER, Marker.ANCHOR_CENTER)
            isDraggable = true
            // sin punto real no se dibuja ni se puede arrastrar
            isEnabled = initialPoint != null
        }.also { mapView.overlays.add(it) }
    }

    // Una vez que la persona marca el punto (toque o arrastre), el GPS deja de moverlo.
    val placedByHand = remember { AtomicBoolean(false) }

    // El marcador es arrastrable (isDraggable=true arriba) pero, sin este listener, el
    // ajuste manual del usuario no tenía ningún efecto en el estado de la app (auditoría
    // Fase 0-9, P1 #11). Se reporta como un `Location` sintético para reusar el mismo
    // callback que ya consume el GPS real, sin cambiar su firma.
    DisposableEffect(marker, onLocationChanged) {
        marker.setOnMarkerDragListener(object : Marker.OnMarkerDragListener {
            override fun onMarkerDrag(marker: Marker) = Unit
            override fun onMarkerDragStart(marker: Marker) = Unit
            override fun onMarkerDragEnd(marker: Marker) {
                placedByHand.set(true)
                val dragged = Location("manual-drag").apply {
                    latitude = marker.position.latitude
                    longitude = marker.position.longitude
                }
                onLocationChanged(dragged)
            }
        })
        onDispose { marker.setOnMarkerDragListener(null) }
    }

    // Tocar el mapa marca el lugar a mano (sin GPS o con el permiso negado).
    val currentOnLocationChanged by rememberUpdatedState(onLocationChanged)
    DisposableEffect(mapView, marker) {
        val tapOverlay = MapEventsOverlay(object : MapEventsReceiver {
            override fun singleTapConfirmedHelper(p: GeoPoint): Boolean {
                placedByHand.set(true)
                marker.position = p
                marker.isEnabled = true
                mapView.invalidate()
                currentOnLocationChanged(
                    Location("manual-tap").apply {
                        latitude = p.latitude
                        longitude = p.longitude
                    },
                )
                return true
            }

            override fun longPressHelper(p: GeoPoint): Boolean = false
        })
        mapView.overlays.add(0, tapOverlay)
        onDispose { mapView.overlays.remove(tapOverlay) }
    }

    DisposableEffect(mapView) {
        mapView.onResume()
        onDispose { mapView.onPause() }
    }

    DisposableEffect(locationEnabled, mapView, marker) {
        if (!locationEnabled) {
            onDispose { }
        } else {
            val manager = context.getSystemService(Context.LOCATION_SERVICE) as LocationManager
            val listener = object : LocationListener {
                override fun onLocationChanged(location: Location) {
                    if (placedByHand.get()) return
                    val point = GeoPoint(location.latitude, location.longitude)
                    marker.position = point
                    marker.isEnabled = true
                    mapView.controller.animateTo(point)
                    mapView.controller.setZoom(DefaultZoomWithFix)
                    mapView.invalidate()
                    onLocationChanged(location)
                }

                @Deprecated("Deprecated in Java")
                override fun onStatusChanged(provider: String?, status: Int, extras: Bundle?) = Unit

                override fun onProviderEnabled(provider: String) = Unit

                override fun onProviderDisabled(provider: String) = Unit
            }
            @SuppressLint("MissingPermission")
            fun requestUpdates() {
                val last = lastKnownLocation(manager)
                if (last != null) listener.onLocationChanged(last)
                val providers = buildList {
                    if (manager.isProviderEnabled(LocationManager.GPS_PROVIDER)) {
                        add(LocationManager.GPS_PROVIDER)
                    }
                    if (manager.isProviderEnabled(LocationManager.NETWORK_PROVIDER)) {
                        add(LocationManager.NETWORK_PROVIDER)
                    }
                }
                providers.forEach { provider ->
                    manager.requestLocationUpdates(
                        provider,
                        2_000L,
                        5f,
                        listener,
                        Looper.getMainLooper(),
                    )
                }
            }
            requestUpdates()
            onDispose { manager.removeUpdates(listener) }
        }
    }

    AndroidView(
        factory = { mapView },
        modifier = modifier.fillMaxSize(),
        update = { it.invalidate() },
    )
}

@SuppressLint("MissingPermission")
private fun lastKnownLocation(manager: LocationManager): Location? {
    val gps = runCatching { manager.getLastKnownLocation(LocationManager.GPS_PROVIDER) }.getOrNull()
    val network = runCatching {
        manager.getLastKnownLocation(LocationManager.NETWORK_PROVIDER)
    }.getOrNull()
    return when {
        gps != null && network != null -> if (gps.time >= network.time) gps else network
        else -> gps ?: network
    }
}

private fun configureOsmdroid(context: Context) {
    val base = File(context.cacheDir, "osmdroid")
    Configuration.getInstance().apply {
        osmdroidBasePath = base
        osmdroidTileCache = File(base, "tiles")
        userAgentValue = context.packageName
        load(context, context.getSharedPreferences("osmdroid", Context.MODE_PRIVATE))
    }
}
