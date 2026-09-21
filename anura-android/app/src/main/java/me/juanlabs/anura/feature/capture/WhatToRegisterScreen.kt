package me.juanlabs.anura.feature.capture

import android.graphics.Color as AndroidColor
import android.graphics.drawable.ColorDrawable
import android.os.Build
import androidx.compose.foundation.clickable
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.navigationBars
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.windowInsetsBottomHeight
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.SideEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalView
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.DialogWindowProvider
import androidx.core.view.WindowCompat
import me.juanlabs.anura.R
import me.juanlabs.anura.designsystem.component.AnuraFormButton
import me.juanlabs.anura.designsystem.component.AnuraFormButtonStyle
import me.juanlabs.anura.designsystem.component.AnuraSheetHandle
import me.juanlabs.anura.designsystem.icon.AnuraIcons
import me.juanlabs.anura.designsystem.preview.AnuraPreviews
import me.juanlabs.anura.designsystem.theme.AnuraDimens
import me.juanlabs.anura.designsystem.theme.AnuraTheme
import me.juanlabs.anura.designsystem.theme.AnuraThemeMode

/** Misma holgura inferior de contenido que el sheet de bienvenida/auth. */
private val WhatToRegisterContentBottomPadding = AnuraDimens.spaceSection

/**
 * `Pop-up del botón "+": qué registrar` (§4.1/§4.2).
 *
 * Tras «Iniciar salida de campo» el mismo sheet pide iniciar o continuar.
 */
@Composable
fun WhatToRegisterContent(
    onStartFieldSession: () -> Unit,
    onContinueFieldSession: () -> Unit,
    onTakeQuickSample: () -> Unit,
    onRecordSound: () -> Unit,
    onDismiss: () -> Unit,
) {
    val view = LocalView.current
    SideEffect {
        val window = (view.parent as? DialogWindowProvider)?.window ?: return@SideEffect
        WindowCompat.setDecorFitsSystemWindows(window, false)
        window.setBackgroundDrawable(ColorDrawable(AndroidColor.TRANSPARENT))
        window.statusBarColor = AndroidColor.TRANSPARENT
        window.navigationBarColor = AndroidColor.TRANSPARENT
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            window.isNavigationBarContrastEnforced = false
        }
    }

    Column(modifier = Modifier.fillMaxSize()) {
        Box(
            modifier = Modifier
                .weight(1f)
                .fillMaxWidth()
                .clickable(
                    interactionSource = remember { MutableInteractionSource() },
                    indication = null,
                    onClick = onDismiss,
                ),
        )
        WhatToRegisterSheet(
            onStartFieldSession = onStartFieldSession,
            onContinueFieldSession = onContinueFieldSession,
            onTakeQuickSample = onTakeQuickSample,
            onRecordSound = onRecordSound,
            onDismiss = onDismiss,
        )
    }
}

@Composable
private fun WhatToRegisterSheet(
    onStartFieldSession: () -> Unit,
    onContinueFieldSession: () -> Unit,
    onTakeQuickSample: () -> Unit,
    onRecordSound: () -> Unit,
    onDismiss: () -> Unit,
) {
    var choosingFieldSession by rememberSaveable { mutableStateOf(false) }
    Surface(
        modifier = Modifier.fillMaxWidth(),
        color = MaterialTheme.colorScheme.surface,
        shape = RoundedCornerShape(
            topStart = AnuraDimens.radiusSheet,
            topEnd = AnuraDimens.radiusSheet,
        ),
        shadowElevation = 0.dp,
        tonalElevation = 0.dp,
    ) {
        Column(
            modifier = Modifier.fillMaxWidth(),
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            AnuraSheetHandle()

            Text(
                text = stringResource(
                    if (choosingFieldSession) {
                        R.string.what_to_register_field_session_choice_title
                    } else {
                        R.string.what_to_register_title
                    },
                ),
                style = MaterialTheme.typography.headlineMedium,
                color = MaterialTheme.colorScheme.onSurface,
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = AnuraDimens.spacePopupInset),
            )

            Spacer(modifier = Modifier.height(AnuraDimens.spaceSheetTitleToBody))

            if (!choosingFieldSession) {
                Text(
                    text = stringResource(R.string.what_to_register_body),
                    style = MaterialTheme.typography.titleMedium.copy(
                        fontWeight = FontWeight.Normal,
                        lineHeight = 22.sp,
                    ),
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = AnuraDimens.spacePopupInset),
                )
                Spacer(modifier = Modifier.height(AnuraDimens.spaceSheetBodyToActions))
            }

            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = AnuraDimens.spacePopupInset),
                verticalArrangement = Arrangement.spacedBy(AnuraDimens.spaceActionGap),
            ) {
                if (choosingFieldSession) {
                    AnuraFormButton(
                        text = stringResource(R.string.what_to_register_start_field_session),
                        onClick = onStartFieldSession,
                        style = AnuraFormButtonStyle.Primary,
                        icon = AnuraIcons.FieldSession,
                    )
                    AnuraFormButton(
                        text = stringResource(R.string.what_to_register_continue_field_session),
                        onClick = onContinueFieldSession,
                        style = AnuraFormButtonStyle.Secondary,
                        icon = AnuraIcons.FieldSession,
                    )
                    AnuraFormButton(
                        text = stringResource(R.string.what_to_register_cancel),
                        onClick = { choosingFieldSession = false },
                        style = AnuraFormButtonStyle.Outline,
                    )
                } else {
                    AnuraFormButton(
                        text = stringResource(R.string.what_to_register_start_field_session),
                        onClick = { choosingFieldSession = true },
                        style = AnuraFormButtonStyle.Primary,
                        icon = AnuraIcons.FieldSession,
                    )
                    AnuraFormButton(
                        text = stringResource(R.string.what_to_register_quick_sample),
                        onClick = onTakeQuickSample,
                        style = AnuraFormButtonStyle.Secondary,
                        icon = AnuraIcons.PhotoId,
                    )
                    AnuraFormButton(
                        text = stringResource(R.string.what_to_register_record_sound),
                        onClick = onRecordSound,
                        style = AnuraFormButtonStyle.Secondary,
                        icon = AnuraIcons.AudioId,
                    )
                    AnuraFormButton(
                        text = stringResource(R.string.what_to_register_cancel),
                        onClick = onDismiss,
                        style = AnuraFormButtonStyle.Outline,
                    )
                }
            }

            Spacer(modifier = Modifier.height(WhatToRegisterContentBottomPadding))
            Spacer(modifier = Modifier.windowInsetsBottomHeight(WindowInsets.navigationBars))
        }
    }
}

@AnuraPreviews
@Composable
private fun WhatToRegisterPreview() {
    AnuraTheme {
        WhatToRegisterSheet(
            onStartFieldSession = {},
            onContinueFieldSession = {},
            onTakeQuickSample = {},
            onRecordSound = {},
            onDismiss = {},
        )
    }
}

@Preview(name = "Luz roja", group = "modo", showBackground = true)
@Composable
private fun WhatToRegisterPreviewRedLight() {
    AnuraTheme(AnuraThemeMode.LuzRoja) {
        WhatToRegisterSheet(
            onStartFieldSession = {},
            onContinueFieldSession = {},
            onTakeQuickSample = {},
            onRecordSound = {},
            onDismiss = {},
        )
    }
}
