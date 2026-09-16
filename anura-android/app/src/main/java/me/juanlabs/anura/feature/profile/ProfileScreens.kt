package me.juanlabs.anura.feature.profile

import androidx.compose.runtime.Composable
import me.juanlabs.anura.navigation.MockNavAction
import me.juanlabs.anura.navigation.MockScreenScaffold

/** `profile` (propia/ajena, §4.1, argumento `userId?`). `userId == null` = propio. */
@Composable
fun ProfileScreen(
    userId: String?,
    onBackClick: () -> Unit,
    onOpenEditProfile: () -> Unit,
    onOpenConnections: (String) -> Unit,
    onOpenOtherProfile: (String) -> Unit,
) {
    val isOwn = userId == null
    MockScreenScaffold(
        title = if (isOwn) "Mi perfil" else "Perfil de $userId",
        onBackClick = onBackClick,
        actions = buildList {
            if (isOwn) {
                add(MockNavAction("Editar perfil", onOpenEditProfile))
                add(MockNavAction("Ver seguidores/seguidos/favoritos") { onOpenConnections("me") })
                add(MockNavAction("Ver perfil de otro usuario") { onOpenOtherProfile("user-002") })
            } else {
                add(MockNavAction("Ver seguidores/seguidos/favoritos") { onOpenConnections(userId) })
            }
        },
    )
}

/** `EDIT` (§4.1). Hoja del árbol. */
@Composable
fun EditProfileScreen(
    onBackClick: () -> Unit,
) {
    MockScreenScaffold(
        title = "Editar perfil",
        onBackClick = onBackClick,
    )
}

/** `Seguidos, seguidores y favoritos` (§4.1, argumento `userId`). */
@Composable
fun ConnectionsScreen(
    userId: String,
    onBackClick: () -> Unit,
    onOpenProfile: (String) -> Unit,
) {
    MockScreenScaffold(
        title = "Conexiones de $userId",
        onBackClick = onBackClick,
        actions = listOf(
            MockNavAction("Ver perfil de un seguidor") { onOpenProfile("user-003") },
        ),
    )
}
