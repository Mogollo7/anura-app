package me.juanlabs.anura.feature.notifications

import android.content.Intent
import android.net.Uri
import androidx.compose.foundation.Image
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import me.juanlabs.anura.R
import me.juanlabs.anura.core.auth.AnuraServerConfig
import me.juanlabs.anura.core.data.AvisoCompleto
import me.juanlabs.anura.core.data.NotificationsRemote
import me.juanlabs.anura.core.data.formatIsoWhen
import me.juanlabs.anura.core.platform.rememberRemotePhotoPainter
import me.juanlabs.anura.designsystem.component.AnuraCard
import me.juanlabs.anura.designsystem.component.AnuraErrorState
import me.juanlabs.anura.designsystem.component.AnuraTopBar
import me.juanlabs.anura.designsystem.theme.AnuraDimens
import me.juanlabs.anura.designsystem.theme.AnuraTheme

/**
 * El aviso rico se dibuja aquí, dentro de la app. El JSON es el mismo que
 * `GET /api/notifications/public/:token` (título, cuerpo, imagen y botones).
 * No abre el navegador ni una pestaña personalizada.
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AvisoDetalleScreen(token: String, onBackClick: () -> Unit) {
    var aviso by remember(token) { mutableStateOf<AvisoCompleto?>(null) }
    var fallo by remember(token) { mutableStateOf(false) }
    var intento by remember(token) { mutableStateOf(0) }
    LaunchedEffect(token, intento) {
        fallo = false
        aviso = null
        val cargado = NotificationsRemote.fetchCompleto(token)
        if (cargado == null || cargado.titulo.isBlank()) fallo = true else aviso = cargado
    }
    Scaffold(
        containerColor = AnuraTheme.extendedColors.boardBackground,
        topBar = {
            AnuraTopBar(
                title = stringResource(R.string.notifications_full_title),
                onBackClick = onBackClick,
                centerTitle = true,
            )
        },
    ) { innerPadding ->
        when {
            fallo -> AnuraErrorState(
                title = stringResource(R.string.notifications_full_error),
                actionLabel = stringResource(R.string.notifications_full_retry),
                onAction = { intento += 1 },
                modifier = Modifier
                    .fillMaxSize()
                    .padding(innerPadding),
            )
            aviso == null -> Text(
                text = stringResource(R.string.notifications_full_loading),
                style = MaterialTheme.typography.bodyLarge,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                modifier = Modifier
                    .padding(innerPadding)
                    .padding(AnuraDimens.spaceGutter),
            )
            else -> AvisoCompletoCuerpo(
                aviso = aviso!!,
                modifier = Modifier
                    .fillMaxSize()
                    .padding(innerPadding),
            )
        }
    }
}

@Composable
private fun AvisoCompletoCuerpo(aviso: AvisoCompleto, modifier: Modifier = Modifier) {
    val context = LocalContext.current
    val imagen = aviso.imagen?.let { raw ->
        if (raw.startsWith("http")) raw else AnuraServerConfig.AUTH_BASE_URL + raw
    }
    Column(
        modifier = modifier.verticalScroll(rememberScrollState()),
        verticalArrangement = Arrangement.spacedBy(AnuraDimens.spaceGap),
    ) {
        AnuraCard(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = AnuraDimens.spaceGutter)
                .padding(top = AnuraDimens.spaceGap, bottom = AnuraDimens.spaceSection),
        ) {
            if (!imagen.isNullOrBlank()) {
                Image(
                    painter = rememberRemotePhotoPainter(imagen),
                    contentDescription = null,
                    contentScale = ContentScale.Crop,
                    modifier = Modifier
                        .fillMaxWidth()
                        .heightIn(min = 160.dp, max = 280.dp),
                )
            }
            Column(
                modifier = Modifier.padding(
                    horizontal = AnuraDimens.spaceCardInsetHorizontal,
                    vertical = AnuraDimens.spaceCardInsetVertical,
                ),
                verticalArrangement = Arrangement.spacedBy(AnuraDimens.spaceGap),
            ) {
                Text(
                    text = aviso.titulo,
                    style = MaterialTheme.typography.headlineSmall.copy(fontWeight = FontWeight.SemiBold),
                    color = MaterialTheme.colorScheme.onSurface,
                )
                val meta = listOfNotNull(
                    formatIsoWhen(aviso.enviado),
                    aviso.autor?.trim()?.takeIf { it.isNotEmpty() },
                ).joinToString(" · ")
                if (meta.isNotEmpty()) {
                    Text(
                        text = meta,
                        style = MaterialTheme.typography.labelMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }
                aviso.cuerpo.trim().split(Regex("\\n{2,}"))
                    .map { it.trim() }
                    .filter { it.isNotEmpty() }
                    .forEach { parrafo ->
                        Text(
                            text = parrafo,
                            style = MaterialTheme.typography.bodyLarge,
                            color = MaterialTheme.colorScheme.onSurface,
                        )
                    }
                aviso.enlaces.filter { it.url.startsWith("https://") && it.texto.isNotBlank() }
                    .forEach { enlace ->
                        Button(
                            onClick = {
                                context.startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(enlace.url)))
                            },
                            contentPadding = PaddingValues(horizontal = 18.dp, vertical = 10.dp),
                        ) {
                            Text(enlace.texto)
                        }
                    }
            }
        }
    }
}
