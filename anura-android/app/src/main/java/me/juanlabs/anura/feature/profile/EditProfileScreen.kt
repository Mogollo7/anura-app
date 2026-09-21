package me.juanlabs.anura.feature.profile

import android.content.Intent
import android.graphics.BitmapFactory
import android.net.Uri
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.PickVisualMediaRequest
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.ImageBitmap
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.text.input.VisualTransformation
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import me.juanlabs.anura.R
import me.juanlabs.anura.designsystem.component.AnuraFormButton
import me.juanlabs.anura.designsystem.component.AnuraFormButtonStyle
import me.juanlabs.anura.designsystem.component.AnuraSectionLabel
import me.juanlabs.anura.designsystem.component.AnuraTextField
import me.juanlabs.anura.designsystem.component.AnuraTopBar
import me.juanlabs.anura.designsystem.icon.AnuraIcons
import me.juanlabs.anura.designsystem.preview.AnuraPreviews
import me.juanlabs.anura.designsystem.theme.AnuraDimens
import me.juanlabs.anura.designsystem.theme.AnuraTheme
import me.juanlabs.anura.designsystem.theme.AnuraThemeMode

private val EditAvatarSize = 80.dp
private val EditAvatarBadgeSize = 28.dp

/**
 * `EDIT` (§4.1) — avatar, usuario, nombre y cambio de contraseña.
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun EditProfileScreen(
    onBackClick: () -> Unit,
) {
    val context = LocalContext.current
    val mockUsername = stringResource(R.string.home_user_username_mock)
    val mockName = stringResource(R.string.edit_profile_full_name_mock)
    var username by rememberSaveable { mutableStateOf(mockUsername) }
    var name by rememberSaveable { mutableStateOf(mockName) }
    var currentPassword by rememberSaveable { mutableStateOf("") }
    var newPassword by rememberSaveable { mutableStateOf("") }
    var confirmPassword by rememberSaveable { mutableStateOf("") }
    var photoUri by rememberSaveable { mutableStateOf<String?>(null) }
    val photoBitmap = rememberProfilePhoto(photoUri)

    val gallery = rememberLauncherForActivityResult(
        ActivityResultContracts.PickVisualMedia(),
    ) { uri ->
        if (uri == null) return@rememberLauncherForActivityResult
        runCatching {
            context.contentResolver.takePersistableUriPermission(
                uri,
                Intent.FLAG_GRANT_READ_URI_PERMISSION,
            )
        }
        photoUri = uri.toString()
    }

    fun openGallery() {
        gallery.launch(
            PickVisualMediaRequest(ActivityResultContracts.PickVisualMedia.ImageOnly),
        )
    }

    Scaffold(
        containerColor = AnuraTheme.extendedColors.boardBackground,
        topBar = {
            AnuraTopBar(
                title = stringResource(R.string.edit_profile_title),
                onBackClick = onBackClick,
                centerTitle = true,
            )
        },
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .verticalScroll(rememberScrollState())
                .padding(horizontal = AnuraDimens.spaceGutter)
                .padding(bottom = AnuraDimens.spaceSection),
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            Box(contentAlignment = Alignment.BottomEnd) {
                Box(
                    modifier = Modifier
                        .size(EditAvatarSize)
                        .clip(CircleShape)
                        .background(MaterialTheme.colorScheme.surfaceVariant)
                        .clickable(
                            role = Role.Button,
                            onClick = ::openGallery,
                        ),
                    contentAlignment = Alignment.Center,
                ) {
                    if (photoBitmap != null) {
                        Image(
                            bitmap = photoBitmap,
                            contentDescription = stringResource(R.string.edit_profile_photo_cd),
                            modifier = Modifier.fillMaxSize(),
                            contentScale = ContentScale.Crop,
                        )
                    } else {
                        Icon(
                            imageVector = AnuraIcons.Person,
                            contentDescription = stringResource(R.string.edit_profile_photo_cd),
                            tint = MaterialTheme.colorScheme.onSurfaceVariant,
                            modifier = Modifier.size(40.dp),
                        )
                    }
                }
                Box(
                    modifier = Modifier
                        .offset(x = 4.dp, y = 4.dp)
                        .size(AnuraDimens.sizeTouch)
                        .clickable(role = Role.Button, onClick = ::openGallery),
                    contentAlignment = Alignment.Center,
                ) {
                    Box(
                        modifier = Modifier
                            .size(EditAvatarBadgeSize)
                            .clip(CircleShape)
                            .background(AnuraTheme.extendedColors.accentInk),
                        contentAlignment = Alignment.Center,
                    ) {
                        Icon(
                            imageVector = AnuraIcons.Edit,
                            contentDescription = stringResource(R.string.edit_profile_pick_photo),
                            tint = MaterialTheme.colorScheme.onPrimary,
                            modifier = Modifier.size(16.dp),
                        )
                    }
                }
            }
            Spacer(modifier = Modifier.height(AnuraDimens.spaceSection))
            AnuraTextField(
                value = username,
                onValueChange = { username = it },
                label = stringResource(R.string.edit_profile_username_label),
                modifier = Modifier.fillMaxWidth(),
                leadingIcon = AnuraIcons.Person,
            )
            Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))
            AnuraTextField(
                value = name,
                onValueChange = { name = it },
                label = stringResource(R.string.edit_profile_full_name_label),
                modifier = Modifier.fillMaxWidth(),
                leadingIcon = AnuraIcons.Person,
            )
            Spacer(modifier = Modifier.height(AnuraDimens.spaceSection))
            AnuraSectionLabel(
                text = stringResource(R.string.edit_profile_password_section),
                modifier = Modifier.fillMaxWidth(),
            )
            Spacer(modifier = Modifier.height(AnuraDimens.spaceLabelToContent))
            EditPasswordField(
                value = currentPassword,
                onValueChange = { currentPassword = it },
                label = stringResource(R.string.edit_profile_current_password),
            )
            Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))
            EditPasswordField(
                value = newPassword,
                onValueChange = { newPassword = it },
                label = stringResource(R.string.edit_profile_new_password),
                placeholder = stringResource(R.string.sign_up_password_placeholder),
            )
            Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))
            EditPasswordField(
                value = confirmPassword,
                onValueChange = { confirmPassword = it },
                label = stringResource(R.string.edit_profile_confirm_password),
                placeholder = stringResource(R.string.edit_profile_confirm_placeholder),
            )
            Spacer(modifier = Modifier.height(AnuraDimens.spaceSection))
            AnuraFormButton(
                text = stringResource(R.string.edit_profile_save),
                onClick = onBackClick,
                style = AnuraFormButtonStyle.Primary,
            )
        }
    }
}

@Composable
private fun EditPasswordField(
    value: String,
    onValueChange: (String) -> Unit,
    label: String,
    placeholder: String? = null,
) {
    var visible by rememberSaveable { mutableStateOf(false) }
    AnuraTextField(
        value = value,
        onValueChange = onValueChange,
        label = label,
        placeholder = placeholder,
        modifier = Modifier.fillMaxWidth(),
        leadingIcon = AnuraIcons.Lock,
        trailingIcon = if (visible) AnuraIcons.VisibilityOff else AnuraIcons.Visibility,
        trailingIconContentDescription = stringResource(
            if (visible) {
                R.string.sign_in_hide_password_cd
            } else {
                R.string.sign_in_show_password_cd
            },
        ),
        onTrailingIconClick = { visible = !visible },
        keyboardType = KeyboardType.Password,
        visualTransformation = if (visible) {
            VisualTransformation.None
        } else {
            PasswordVisualTransformation()
        },
    )
}

@Composable
private fun rememberProfilePhoto(uriString: String?): ImageBitmap? {
    val context = LocalContext.current
    val uri = uriString?.let(Uri::parse)
    return remember(uriString) {
        if (uri == null) {
            null
        } else {
            context.contentResolver.openInputStream(uri)?.use { stream ->
                BitmapFactory.decodeStream(stream)?.asImageBitmap()
            }
        }
    }
}

@AnuraPreviews
@Composable
private fun EditProfilePreview() {
    AnuraTheme { EditProfileScreen(onBackClick = {}) }
}

@Preview(name = "Luz roja", group = "modo", showBackground = true)
@Composable
private fun EditProfilePreviewRedLight() {
    AnuraTheme(AnuraThemeMode.LuzRoja) { EditProfileScreen(onBackClick = {}) }
}
