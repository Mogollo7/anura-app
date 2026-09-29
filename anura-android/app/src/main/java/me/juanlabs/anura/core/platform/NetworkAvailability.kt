package me.juanlabs.anura.core.platform

import android.content.Context
import android.net.ConnectivityManager
import android.net.Network
import android.net.NetworkCapabilities
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.platform.LocalContext

@Composable
fun rememberNetworkAvailable(): Boolean {
    val context = LocalContext.current
    var online by remember { mutableStateOf(isNetworkAvailable(context)) }
    DisposableEffect(context) {
        val appContext = context.applicationContext
        val cm = appContext.getSystemService(ConnectivityManager::class.java)
        if (cm == null) {
            return@DisposableEffect onDispose { }
        }
        val callback = object : ConnectivityManager.NetworkCallback() {
            private fun refresh() {
                appContext.mainExecutor.execute {
                    online = isNetworkAvailable(appContext)
                }
            }

            override fun onAvailable(network: Network) = refresh()

            override fun onLost(network: Network) = refresh()

            override fun onCapabilitiesChanged(
                network: Network,
                networkCapabilities: NetworkCapabilities,
            ) = refresh()
        }
        cm.registerDefaultNetworkCallback(callback)
        online = isNetworkAvailable(appContext)
        onDispose { cm.unregisterNetworkCallback(callback) }
    }
    return online
}

fun isNetworkAvailable(context: Context): Boolean {
    val cm = context.getSystemService(ConnectivityManager::class.java) ?: return false
    val network = cm.activeNetwork ?: return false
    val caps = cm.getNetworkCapabilities(network) ?: return false
    return caps.hasCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET)
}
