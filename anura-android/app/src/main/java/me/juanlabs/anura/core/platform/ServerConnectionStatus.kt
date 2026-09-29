package me.juanlabs.anura.core.platform

import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow

/**
 * Si la última llamada real de [me.juanlabs.anura.core.data.AnuraApi] llegó a hablar con el
 * servidor de ANURA (aunque haya devuelto un error de negocio, p. ej. 401) o no pudo ni
 * conectarse. `null` = todavía no se ha intentado ninguna desde que se abrió la app.
 *
 * Distinto de [rememberNetworkAvailable] ("el teléfono tiene internet"): esta es la señal que de
 * verdad le importa al usuario — "el servidor de ANURA responde" — y la que lee el indicador
 * sutil de conexión en la barra de navegación.
 */
object ServerConnectionStatus {
    private val _connected = MutableStateFlow<Boolean?>(null)
    val connected: StateFlow<Boolean?> = _connected

    fun update(reachable: Boolean) {
        _connected.value = reachable
    }
}
