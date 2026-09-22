package me.juanlabs.anura.designsystem.component

import android.Manifest
import android.annotation.SuppressLint
import android.content.Context
import android.content.pm.PackageManager
import android.location.Location
import android.location.LocationManager
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalLifecycleOwner
import androidx.core.content.ContextCompat
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.LifecycleEventObserver

enum class AnuraPermissionKind {
    Camera,
    Microphone,
    Location,
}

fun AnuraPermissionKind.manifestPermissions(): Array<String> = when (this) {
    AnuraPermissionKind.Camera -> arrayOf(Manifest.permission.CAMERA)
    AnuraPermissionKind.Microphone -> arrayOf(Manifest.permission.RECORD_AUDIO)
    AnuraPermissionKind.Location -> arrayOf(
        Manifest.permission.ACCESS_FINE_LOCATION,
        Manifest.permission.ACCESS_COARSE_LOCATION,
    )
}

/**
 * Última ubicación conocida (GPS o red, la más reciente de las dos), sin pedir una actualización
 * nueva ni mostrar UI — para usarse en flujos cortos como Foto ID que no pasan por el Paso 1 del
 * wizard. Requiere permiso ya concedido ([AnuraPermissionKind.Location.isGranted]); null si no
 * hay permiso, no hay proveedor disponible, o nunca se registró una ubicación en el dispositivo.
 */
@SuppressLint("MissingPermission")
fun lastKnownLocation(context: Context): Location? {
    if (!AnuraPermissionKind.Location.isGranted(context)) return null
    val manager = context.getSystemService(Context.LOCATION_SERVICE) as? LocationManager ?: return null
    val gps = runCatching { manager.getLastKnownLocation(LocationManager.GPS_PROVIDER) }.getOrNull()
    val network = runCatching { manager.getLastKnownLocation(LocationManager.NETWORK_PROVIDER) }.getOrNull()
    return when {
        gps != null && network != null -> if (gps.time >= network.time) gps else network
        else -> gps ?: network
    }
}

fun AnuraPermissionKind.isGranted(context: Context): Boolean {
    val permissions = manifestPermissions()
    return if (this == AnuraPermissionKind.Location) {
        permissions.any { permission ->
            ContextCompat.checkSelfPermission(context, permission) ==
                PackageManager.PERMISSION_GRANTED
        }
    } else {
        permissions.all { permission ->
            ContextCompat.checkSelfPermission(context, permission) ==
                PackageManager.PERMISSION_GRANTED
        }
    }
}

/**
 * Pide el permiso con el diálogo del sistema, sin rationale de Penpot.
 * Se lanza al entrar a la actividad que lo necesita, una sola vez por visita.
 */
@Composable
fun rememberSystemPermissionGranted(kind: AnuraPermissionKind): Boolean {
    val context = LocalContext.current
    var granted by rememberSaveable(kind) { mutableStateOf(kind.isGranted(context)) }
    var asked by rememberSaveable(kind) { mutableStateOf(false) }
    val launcher = rememberLauncherForActivityResult(
        ActivityResultContracts.RequestMultiplePermissions(),
    ) {
        granted = kind.isGranted(context)
    }

    LaunchedEffect(kind) {
        if (!granted && !asked) {
            asked = true
            launcher.launch(kind.manifestPermissions())
        }
    }

    val lifecycleOwner = LocalLifecycleOwner.current
    DisposableEffect(lifecycleOwner, kind) {
        val observer = LifecycleEventObserver { _, event ->
            if (event == Lifecycle.Event.ON_RESUME) {
                granted = kind.isGranted(context)
            }
        }
        lifecycleOwner.lifecycle.addObserver(observer)
        onDispose { lifecycleOwner.lifecycle.removeObserver(observer) }
    }

    return granted
}
