package me.juanlabs.anura.feature.capture

import android.graphics.BitmapFactory
import android.net.Uri
import android.os.Build
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.wrapContentHeight
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.blur
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.ImageBitmap
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import me.juanlabs.anura.R
import me.juanlabs.anura.designsystem.component.AnuraBottomSheet
import me.juanlabs.anura.designsystem.component.AnuraFormButton
import me.juanlabs.anura.designsystem.component.AnuraFormButtonStyle
import me.juanlabs.anura.designsystem.component.AnuraLoadingState
import me.juanlabs.anura.designsystem.icon.AnuraIcons
import me.juanlabs.anura.designsystem.theme.AnuraDimens
import me.juanlabs.anura.designsystem.theme.AnuraTheme
import me.juanlabs.anura.designsystem.theme.anuraMediaTint

@OptIn(ExperimentalMaterial3Api::class)
@Composable
internal fun CaptureBlurryPhotoSheet(
    imageToken: String,
    onRetake: () -> Unit,
    onAccept: () -> Unit,
    onDismiss: () -> Unit,
) {
    AnuraBottomSheet(onDismissRequest = onDismiss) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .wrapContentHeight()
                .padding(horizontal = AnuraDimens.spaceGutter),
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            Icon(
                imageVector = AnuraIcons.Warning,
                contentDescription = null,
                tint = AnuraTheme.extendedColors.warning,
            )
            Text(
                text = stringResource(R.string.photo_blurry_title),
                style = MaterialTheme.typography.headlineSmall.copy(fontWeight = FontWeight.Bold),
                color = MaterialTheme.colorScheme.onSurface,
                textAlign = TextAlign.Center,
                modifier = Modifier.padding(vertical = AnuraDimens.spaceGap),
            )
            CapturePhotoPreview(
                token = imageToken,
                processing = false,
                blurred = true,
                modifier = Modifier
                    .fillMaxWidth()
                    .aspectRatio(16f / 9f),
            )
            Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))
            Text(
                text = stringResource(R.string.photo_blurry_body),
                style = MaterialTheme.typography.titleMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                textAlign = TextAlign.Center,
            )
            Spacer(modifier = Modifier.height(AnuraDimens.spaceSheetBodyToActions))
            Column(verticalArrangement = Arrangement.spacedBy(AnuraDimens.spaceActionGap)) {
                AnuraFormButton(
                    text = stringResource(R.string.photo_blurry_retake),
                    onClick = onRetake,
                    style = AnuraFormButtonStyle.Primary,
                )
                AnuraFormButton(
                    text = stringResource(R.string.photo_blurry_accept),
                    onClick = onAccept,
                    style = AnuraFormButtonStyle.Outline,
                )
            }
            Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))
        }
    }
}

@Composable
internal fun CapturePhotoPreview(
    token: String,
    processing: Boolean,
    modifier: Modifier = Modifier,
    blurred: Boolean = false,
) {
    Box(
        modifier = modifier
            .clip(RoundedCornerShape(AnuraDimens.radiusCard))
            .anuraMediaTint(),
        contentAlignment = Alignment.Center,
    ) {
        val imageModifier = Modifier
            .fillMaxSize()
            .then(
                if (blurred && Build.VERSION.SDK_INT >= 31) Modifier.blur(18.dp) else Modifier,
            )
        when {
            token.startsWith("uri:") -> {
                val bitmap = rememberUriImage(Uri.parse(token.removePrefix("uri:")))
                if (bitmap != null) {
                    Image(
                        bitmap = bitmap,
                        contentDescription = stringResource(R.string.photo_capture_preview_cd),
                        modifier = imageModifier,
                        contentScale = ContentScale.Crop,
                    )
                } else {
                    CapturePhotoPlaceholder()
                }
            }
            token.startsWith("file:") -> {
                val path = token.removePrefix("file:")
                val bitmap = remember(path) {
                    BitmapFactory.decodeFile(path)?.asImageBitmap()
                }
                if (bitmap != null) {
                    Image(
                        bitmap = bitmap,
                        contentDescription = stringResource(R.string.photo_capture_preview_cd),
                        modifier = imageModifier,
                        contentScale = ContentScale.Crop,
                    )
                } else {
                    CapturePhotoPlaceholder()
                }
            }
            else -> CapturePhotoPlaceholder()
        }
        if (blurred && Build.VERSION.SDK_INT < 31) {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .background(MaterialTheme.colorScheme.scrim.copy(alpha = 0.28f)),
            )
        }
        if (processing) {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .background(MaterialTheme.colorScheme.scrim.copy(alpha = 0.45f)),
                contentAlignment = Alignment.Center,
            ) {
                AnuraLoadingState(label = stringResource(R.string.photo_capture_processing))
            }
        }
    }
}

@Composable
private fun CapturePhotoPlaceholder() {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.surfaceVariant),
        contentAlignment = Alignment.Center,
    ) {
        Icon(
            imageVector = AnuraIcons.PhotoId,
            contentDescription = null,
            tint = AnuraTheme.extendedColors.accentInk.copy(alpha = 0.45f),
            modifier = Modifier.size(40.dp),
        )
    }
}

@Composable
internal fun rememberUriImage(uri: Uri): ImageBitmap? {
    val context = LocalContext.current
    return remember(uri) {
        context.contentResolver.openInputStream(uri)?.use { stream ->
            BitmapFactory.decodeStream(stream)?.asImageBitmap()
        }
    }
}

@Composable
internal fun rememberGalleryPicker(onPicked: (List<Uri>) -> Unit) =
    rememberLauncherForActivityResult(ActivityResultContracts.PickMultipleVisualMedia()) { uris ->
        onPicked(uris)
    }
