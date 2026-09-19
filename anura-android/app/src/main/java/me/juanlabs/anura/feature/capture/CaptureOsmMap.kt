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
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.viewinterop.AndroidView
import java.io.File
import org.osmdroid.config.Configuration
import org.osmdroid.tileprovider.tilesource.TileSourceFactory
import org.osmdroid.util.GeoPoint
import org.osmdroid.views.MapView
import org.osmdroid.views.overlay.Marker

/** Centro de Colombia (Caldas) hasta que haya un fix GPS. */
private val DefaultMapPoint = GeoPoint(5.0689, -75.5174)
private const val DefaultZoomWithoutFix = 6.0
private const val DefaultZoomWithFix = 16.0

/**
 * Mapa OSM interactivo del Paso 1: pan, zoom y marcador arrastrable.
 * El GPS solo se escucha si [locationEnabled] es verdadero.
 */
@Composable
fun CaptureOsmMap(
    locationEnabled: Boolean,
    onLocationChanged: (Location) -> Unit,
    modifier: Modifier = Modifier,
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
            controller.setZoom(DefaultZoomWithoutFix)
            controller.setCenter(DefaultMapPoint)
        }
    }
    val marker = remember(mapView) {
        Marker(mapView).apply {
            position = DefaultMapPoint
            setAnchor(Marker.ANCHOR_CENTER, Marker.ANCHOR_BOTTOM)
            isDraggable = true
        }.also { mapView.overlays.add(it) }
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
                    val point = GeoPoint(location.latitude, location.longitude)
                    marker.position = point
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
