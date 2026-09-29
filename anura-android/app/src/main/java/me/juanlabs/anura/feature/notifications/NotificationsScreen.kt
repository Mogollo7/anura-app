package me.juanlabs.anura.feature.notifications

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FilterChip
import androidx.compose.material3.FilterChipDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import me.juanlabs.anura.R
import me.juanlabs.anura.core.data.AppNotification
import me.juanlabs.anura.core.data.formatIsoWhen
import me.juanlabs.anura.core.data.notificationOpenRequests
import me.juanlabs.anura.core.data.rememberAnuraRepository
import me.juanlabs.anura.designsystem.component.AnuraCard
import me.juanlabs.anura.designsystem.component.AnuraEmptyState
import me.juanlabs.anura.designsystem.component.AnuraTopBar
import me.juanlabs.anura.designsystem.component.LocalAnuraTabBarInset
import me.juanlabs.anura.designsystem.icon.AnuraIcons
import me.juanlabs.anura.designsystem.preview.AnuraPreviews
import me.juanlabs.anura.designsystem.theme.AnuraDimens
import me.juanlabs.anura.designsystem.theme.AnuraTheme

private enum class NotificationFilter { All, Unread, Read }

/**
 * `avisos` — entrada desde Ajustes y desde la campana flotante de [me.juanlabs.anura.navigation.AnuraScaffold]
 * (§4.1, no está en el `Mockup Final` de Penpot: pantalla nueva de C5). Lista `GET /api/notifications`
 * con un filtro Todos/No leídos/Leídos; tocar un aviso lo marca leído
 * (`POST /api/notifications/:id/leido`) y se puede eliminar (`DELETE /api/notifications/:id`),
 * igual que en la web.
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun NotificationsScreen(onBackClick: () -> Unit) {
    val repository = rememberAnuraRepository()
    val snapshot by repository.state.collectAsState()
    val context = LocalContext.current
    LaunchedEffect(Unit) { repository.hydrateNotifications(context) }
    var filter by rememberSaveable { mutableStateOf(NotificationFilter.All) }
    var expandedId by rememberSaveable { mutableStateOf<String?>(null) }
    val openedFromNotification by notificationOpenRequests.collectAsState()
    LaunchedEffect(openedFromNotification?.token) {
        val id = openedFromNotification?.id ?: return@LaunchedEffect
        expandedId = id
        filter = NotificationFilter.All
        repository.markNotificationRead(id)
    }
    val filtered = when (filter) {
        NotificationFilter.All -> snapshot.notifications
        NotificationFilter.Unread -> snapshot.notifications.filterNot { it.is_read }
        NotificationFilter.Read -> snapshot.notifications.filter { it.is_read }
    }
    Scaffold(
        containerColor = AnuraTheme.extendedColors.boardBackground,
        topBar = {
            AnuraTopBar(
                title = stringResource(R.string.notifications_title),
                onBackClick = onBackClick,
                centerTitle = true,
            )
        },
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding),
        ) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .horizontalScroll(rememberScrollState())
                    .padding(horizontal = AnuraDimens.spaceGutter)
                    .padding(top = AnuraDimens.spaceGap, bottom = AnuraDimens.spaceGap),
                horizontalArrangement = Arrangement.spacedBy(AnuraDimens.spaceGap),
            ) {
                NotificationFilterChip(
                    label = stringResource(R.string.notifications_filter_all),
                    selected = filter == NotificationFilter.All,
                    onClick = { filter = NotificationFilter.All },
                )
                NotificationFilterChip(
                    label = stringResource(R.string.notifications_filter_unread),
                    selected = filter == NotificationFilter.Unread,
                    onClick = { filter = NotificationFilter.Unread },
                )
                NotificationFilterChip(
                    label = stringResource(R.string.notifications_filter_read),
                    selected = filter == NotificationFilter.Read,
                    onClick = { filter = NotificationFilter.Read },
                )
            }
            if (filtered.isEmpty()) {
                AnuraEmptyState(
                    title = stringResource(
                        when (filter) {
                            NotificationFilter.All -> R.string.notifications_empty_title
                            NotificationFilter.Unread -> R.string.notifications_empty_unread_title
                            NotificationFilter.Read -> R.string.notifications_empty_read_title
                        },
                    ),
                    description = stringResource(R.string.notifications_empty_body),
                    modifier = Modifier.fillMaxSize(),
                )
            } else {
                LazyColumn(
                    modifier = Modifier.fillMaxSize(),
                    contentPadding = PaddingValues(
                        start = AnuraDimens.spaceGutter,
                        end = AnuraDimens.spaceGutter,
                        bottom = AnuraDimens.spaceGap + LocalAnuraTabBarInset.current,
                    ),
                    verticalArrangement = Arrangement.spacedBy(AnuraDimens.spaceGap),
                ) {
                    items(filtered, key = { it.id }) { notification ->
                        NotificationRow(
                            notification = notification,
                            expanded = expandedId == notification.id,
                            onClick = {
                                expandedId = if (expandedId == notification.id) null else notification.id
                                repository.markNotificationRead(notification.id)
                            },
                            onDelete = { repository.deleteNotification(notification.id) },
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun NotificationFilterChip(label: String, selected: Boolean, onClick: () -> Unit) {
    FilterChip(
        selected = selected,
        onClick = onClick,
        label = { Text(label) },
        colors = FilterChipDefaults.filterChipColors(
            selectedContainerColor = AnuraTheme.extendedColors.accentInk,
            selectedLabelColor = MaterialTheme.colorScheme.onPrimary,
        ),
    )
}

@Composable
private fun NotificationRow(
    notification: AppNotification,
    expanded: Boolean,
    onClick: () -> Unit,
    onDelete: () -> Unit,
) {
    AnuraCard(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(role = Role.Button, onClick = onClick),
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(
                    horizontal = AnuraDimens.spaceCardInsetHorizontal,
                    vertical = AnuraDimens.spaceCardInsetVertical,
                ),
            horizontalArrangement = Arrangement.spacedBy(AnuraDimens.spaceGap),
            verticalAlignment = Alignment.Top,
        ) {
            if (!notification.is_read) {
                Box(
                    modifier = Modifier
                        .padding(top = 6.dp)
                        .size(8.dp)
                        .background(MaterialTheme.colorScheme.error, CircleShape),
                )
            } else {
                Box(modifier = Modifier.size(8.dp))
            }
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = notification.title,
                    style = MaterialTheme.typography.titleMedium.copy(
                        fontWeight = if (notification.is_read) FontWeight.Normal else FontWeight.SemiBold,
                    ),
                    color = MaterialTheme.colorScheme.onSurface,
                )
                val body = notification.body?.trim().orEmpty()
                if (body.isNotEmpty()) {
                    Text(
                        text = body,
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                        maxLines = if (expanded) Int.MAX_VALUE else 2,
                        overflow = TextOverflow.Ellipsis,
                        modifier = Modifier.padding(top = 2.dp),
                    )
                }
                if (!expanded && body.length > 80) {
                    Text(
                        text = stringResource(R.string.notifications_expand_hint),
                        style = MaterialTheme.typography.labelSmall,
                        color = AnuraTheme.extendedColors.accentInk,
                        modifier = Modifier.padding(top = 4.dp),
                    )
                }
                formatIsoWhen(notification.created_at)?.let { whenText ->
                    Text(
                        text = whenText,
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                        modifier = Modifier.padding(top = 6.dp),
                    )
                }
            }
            IconButton(onClick = onDelete, modifier = Modifier.size(AnuraDimens.sizeTouch)) {
                Icon(
                    imageVector = AnuraIcons.Delete,
                    contentDescription = stringResource(R.string.notifications_delete_cd),
                    tint = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
        }
    }
}

@AnuraPreviews
@Composable
private fun NotificationsPreview() {
    AnuraTheme {
        NotificationsScreen(onBackClick = {})
    }
}
