package me.juanlabs.anura.feature.capture

import androidx.annotation.StringRes
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import me.juanlabs.anura.R
import me.juanlabs.anura.designsystem.icon.AnuraIcons
import me.juanlabs.anura.designsystem.theme.AnuraDimens

/**
 * Audio ID y Sonidos nocturnos no tienen modelo todavía (excepción aceptada, igual que C3):
 * todo lo que muestran es una demostración y cada pantalla lo dice con este aviso.
 */
@Composable
internal fun AudioDemoNotice(
    modifier: Modifier = Modifier,
    @StringRes text: Int = R.string.audio_demo_notice,
) {
    Row(
        modifier = modifier
            .fillMaxWidth()
            .background(MaterialTheme.colorScheme.tertiaryContainer, RoundedCornerShape(AnuraDimens.radiusCard))
            .padding(horizontal = AnuraDimens.spaceCardInsetHorizontal, vertical = AnuraDimens.spaceGap),
        horizontalArrangement = Arrangement.spacedBy(AnuraDimens.spaceGap),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Icon(
            imageVector = AnuraIcons.AudioId,
            contentDescription = null,
            tint = MaterialTheme.colorScheme.onTertiaryContainer,
            modifier = Modifier.size(20.dp),
        )
        Text(
            text = stringResource(text),
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onTertiaryContainer,
        )
    }
}
