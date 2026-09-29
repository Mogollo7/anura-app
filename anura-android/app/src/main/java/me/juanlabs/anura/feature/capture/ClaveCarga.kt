package me.juanlabs.anura.feature.capture

import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import me.juanlabs.anura.core.data.RegionalPackageStatus
import me.juanlabs.anura.core.data.rememberAnuraRepository
import me.juanlabs.anura.core.key.ClaveDocumento
import me.juanlabs.anura.core.platform.rememberNetworkAvailable

// ---------------------------------------------------------------------------------------------
// Carga de la clave del paquete activo (la usa el Paso 3 para contar especies compatibles con la medida)
// ---------------------------------------------------------------------------------------------

/** En qué punto está la clave del paquete instalado. Cada caso menos [Lista] tiene su texto guía. */
internal sealed interface ClaveCarga {
    /** Este teléfono no tiene un paquete activo instalado. */
    data object SinPaquete : ClaveCarga

    data object Cargando : ClaveCarga

    /** Con red, el servidor ya no publica este paquete: hay que bajar el vigente. */
    data object Obsoleta : ClaveCarga

    /** Sin red y sin la clave guardada: se descarga al conectarse. */
    data object SinClave : ClaveCarga

    data object SinEspecies : ClaveCarga

    data class Lista(val documento: ClaveDocumento) : ClaveCarga
}

internal class ClaveCargaEstado(val carga: ClaveCarga, val reintentar: () -> Unit)

/**
 * La clave del paquete activo: primero la guardada junto al paquete (funciona sin señal) y, si hay
 * red, se refresca desde el servidor. Nunca una clave de ejemplo.
 */
@Composable
internal fun rememberClaveCarga(): ClaveCargaEstado {
    val repository = rememberAnuraRepository()
    val snapshot by repository.state.collectAsState()
    val pack = snapshot.packages.firstOrNull {
        it.active && it.status == RegionalPackageStatus.Installed && !it.localPath.isNullOrBlank()
    }
    val packId = pack?.id
    val version = pack?.version ?: "1"
    var clave by remember(packId, version) {
        mutableStateOf(packId?.let { repository.cachedClave(it, version) })
    }
    var intento by rememberSaveable(packId, version) { mutableIntStateOf(0) }
    var cargando by remember(packId, version) { mutableStateOf(packId != null && clave == null) }
    LaunchedEffect(packId, version, intento) {
        if (packId == null) return@LaunchedEffect
        if (clave == null) cargando = true
        val fresca = repository.refreshClave(packId, version)
        if (fresca != null) clave = fresca
        cargando = false
    }
    val online = rememberNetworkAvailable()
    val documento = clave
    val carga = when {
        packId == null -> ClaveCarga.SinPaquete
        documento == null && cargando -> ClaveCarga.Cargando
        documento == null && online -> ClaveCarga.Obsoleta
        documento == null -> ClaveCarga.SinClave
        documento.especies.isEmpty() -> ClaveCarga.SinEspecies
        else -> ClaveCarga.Lista(documento)
    }
    return ClaveCargaEstado(carga, reintentar = { intento++ })
}
