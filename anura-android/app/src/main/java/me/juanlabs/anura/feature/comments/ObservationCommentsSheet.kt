package me.juanlabs.anura.feature.comments

import androidx.activity.compose.BackHandler
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.gestures.detectVerticalDragGestures
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxWithConstraints
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.ime
import androidx.compose.foundation.layout.imePadding
import androidx.compose.foundation.layout.navigationBarsPadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableFloatStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import me.juanlabs.anura.core.data.rememberAnuraRepository
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.focus.onFocusChanged
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.platform.LocalFocusManager
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.role
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.font.FontStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import me.juanlabs.anura.R
import me.juanlabs.anura.designsystem.component.AnuraCard
import me.juanlabs.anura.designsystem.component.AnuraSheetHandle
import me.juanlabs.anura.designsystem.icon.AnuraIcons
import me.juanlabs.anura.designsystem.theme.AnuraDimens
import me.juanlabs.anura.designsystem.theme.AnuraTheme

private const val SheetHalf = 0.50f
private const val SheetFull = 0.92f
private const val SheetDismissBelow = 0.36f
private const val SheetSnapFullAbove = 0.72f

@Composable
fun ObservationCommentsOverlay(
    observationId: String,
    onDismiss: () -> Unit,
    modifier: Modifier = Modifier,
    media: @Composable () -> Unit,
) {
    val density = LocalDensity.current
    val focusManager = LocalFocusManager.current
    val imeBottom = WindowInsets.ime.getBottom(density)
    val imeVisible = imeBottom > 0
    val repository = rememberAnuraRepository()
    val snapshot by repository.state.collectAsState()
    var sheetFraction by rememberSaveable(observationId) { mutableFloatStateOf(0f) }
    var composerFocused by rememberSaveable { mutableStateOf(false) }
    val comments = snapshot.comments.filter { it.observationId == observationId }.map { record ->
        ObservationComment(
            id = record.id,
            username = record.authorName,
            body = record.body,
            stance = CommentStance.Neutral,
            own = record.authorUserId == snapshot.session.userId,
        )
    }
    var draft by rememberSaveable { mutableStateOf("") }
    var replyTo by remember { mutableStateOf<ObservationComment?>(null) }
    var pendingProposal by remember { mutableStateOf<TaxonProposal?>(null) }
    var expandedThreadIds by rememberSaveable { mutableStateOf(listOf<String>()) }
    val query = mentionQuery(draft)
    val suggestions = if (query != null) filterTaxa(query) else emptyList()

    BackHandler {
        focusManager.clearFocus()
        onDismiss()
    }
    LaunchedEffect(observationId) {
        sheetFraction = SheetHalf
    }

    val target = when {
        imeVisible || composerFocused -> 1f
        else -> sheetFraction
    }
    val animated by animateFloatAsState(targetValue = target, label = "comment-sheet")

    BoxWithConstraints(
        modifier = modifier
            .fillMaxSize()
            .background(AnuraTheme.extendedColors.boardBackground),
    ) {
        val sheetHeight = maxHeight * animated
        val mediaHeight = (maxHeight - sheetHeight).coerceAtLeast(0.dp)
        val maxPx = with(density) { maxHeight.toPx() }
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .height(mediaHeight)
                .align(Alignment.TopCenter),
        ) {
            media()
        }
        Surface(
            modifier = Modifier
                .align(Alignment.BottomCenter)
                .fillMaxWidth()
                .then(
                    if (imeVisible) {
                        Modifier.imePadding()
                    } else {
                        Modifier.navigationBarsPadding()
                    },
                )
                .fillMaxHeight(animated),
            color = MaterialTheme.colorScheme.surface,
            shape = RoundedCornerShape(
                topStart = AnuraDimens.radiusModal,
                topEnd = AnuraDimens.radiusModal,
            ),
            tonalElevation = 0.dp,
            shadowElevation = 0.dp,
        ) {
            Column(
                modifier = Modifier.fillMaxSize(),
            ) {
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .pointerInput(maxPx) {
                            detectVerticalDragGestures(
                                onDragEnd = {
                                    composerFocused = false
                                    focusManager.clearFocus()
                                    when {
                                        sheetFraction < SheetDismissBelow -> onDismiss()
                                        sheetFraction > SheetSnapFullAbove -> sheetFraction = SheetFull
                                        else -> sheetFraction = SheetHalf
                                    }
                                },
                            ) { _, dragAmount ->
                                val delta = dragAmount / maxPx
                                sheetFraction = (sheetFraction - delta).coerceIn(0.18f, SheetFull)
                            }
                        },
                    contentAlignment = Alignment.Center,
                ) {
                    AnuraSheetHandle()
                }
                Text(
                    text = stringResource(R.string.comments_title),
                    style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.SemiBold),
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = AnuraDimens.spaceGutter),
                )
                Spacer(modifier = Modifier.height(AnuraDimens.spaceLabelToContent))
                LazyColumn(
                    modifier = Modifier
                        .weight(1f)
                        .fillMaxWidth(),
                    contentPadding = PaddingValues(
                        horizontal = AnuraDimens.spaceGutter,
                        vertical = AnuraDimens.spaceGap,
                    ),
                    verticalArrangement = Arrangement.spacedBy(AnuraDimens.spaceSection),
                ) {
                    if (comments.isEmpty()) {
                        item {
                            Text(
                                text = stringResource(R.string.comments_empty),
                                style = MaterialTheme.typography.bodyMedium,
                                color = MaterialTheme.colorScheme.onSurfaceVariant,
                            )
                        }
                    }
                    items(comments, key = { it.id }) { comment ->
                        CommentThread(
                            comment = comment,
                            expanded = expandedThreadIds.contains(comment.id),
                            onToggleReplies = {
                                expandedThreadIds = if (expandedThreadIds.contains(comment.id)) {
                                    expandedThreadIds - comment.id
                                } else {
                                    expandedThreadIds + comment.id
                                }
                            },
                            onReply = { target ->
                                replyTo = target
                                pendingProposal = null
                            },
                        )
                    }
                }
                if (suggestions.isNotEmpty()) {
                    TaxonMentionList(
                        suggestions = suggestions,
                        onPick = { taxon ->
                            draft = insertTaxonMention(draft, taxon)
                            pendingProposal = TaxonProposal(taxon)
                        },
                    )
                }
                CommentComposer(
                    value = draft,
                    replyTo = replyTo,
                    proposal = pendingProposal,
                    imeVisible = imeVisible,
                    onValueChange = { draft = it },
                    onFocusChange = { composerFocused = it },
                    onCancelReply = { replyTo = null },
                    onSend = {
                        val text = draft.trim()
                        val mention = pendingProposal?.taxon?.scientificName
                        val payload = buildString {
                            if (replyTo != null) append("@${replyTo?.username} ")
                            if (!mention.isNullOrBlank()) append("@$mention ")
                            append(text)
                        }.trim()
                        if (payload.isEmpty()) return@CommentComposer
                        repository.addComment(observationId, payload)
                        draft = ""
                        pendingProposal = null
                        replyTo = null
                    },
                )
            }
        }
    }
}

@Composable
private fun CommentThread(
    comment: ObservationComment,
    expanded: Boolean,
    onToggleReplies: () -> Unit,
    onReply: (ObservationComment) -> Unit,
) {
    Column(modifier = Modifier.fillMaxWidth()) {
        CommentRow(comment = comment, onReply = { onReply(comment) })
        if (comment.replies.isNotEmpty()) {
            TextButton(onClick = onToggleReplies) {
                Text(
                    text = if (expanded) {
                        stringResource(R.string.comments_hide_replies)
                    } else {
                        stringResource(R.string.comments_reply_count, comment.replies.size)
                    },
                )
            }
            if (expanded) {
                Column(
                    modifier = Modifier.padding(start = AnuraDimens.spaceSection),
                    verticalArrangement = Arrangement.spacedBy(AnuraDimens.spaceGap),
                ) {
                    comment.replies.forEach { reply ->
                        CommentRow(comment = reply, onReply = { onReply(reply) })
                    }
                }
            }
        }
    }
}

@Composable
private fun CommentRow(
    comment: ObservationComment,
    onReply: () -> Unit,
) {
    val agreeCd = stringResource(R.string.comments_agree_cd)
    val disagreeCd = stringResource(R.string.comments_disagree_cd)
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.spacedBy(AnuraDimens.spaceGap),
    ) {
        Box(
            modifier = Modifier
                .size(36.dp)
                .clip(CircleShape)
                .background(MaterialTheme.colorScheme.surfaceVariant),
            contentAlignment = Alignment.Center,
        ) {
            Icon(
                imageVector = AnuraIcons.Person,
                contentDescription = null,
                tint = MaterialTheme.colorScheme.onSurfaceVariant,
                modifier = Modifier.size(20.dp),
            )
        }
        Column(modifier = Modifier.weight(1f)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(
                    text = comment.username,
                    style = MaterialTheme.typography.titleSmall.copy(fontWeight = FontWeight.SemiBold),
                )
                if (comment.stance == CommentStance.Disagree) {
                    Text(
                        text = " · ${stringResource(R.string.comments_refute_badge)}",
                        style = MaterialTheme.typography.labelMedium,
                        color = MaterialTheme.colorScheme.error,
                    )
                }
            }
            if (comment.body.isNotBlank()) {
                Text(
                    text = comment.body,
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurface,
                )
            }
            comment.proposal?.let { DisagreementProposalCard(it) }
            TextButton(
                onClick = onReply,
                contentPadding = PaddingValues(horizontal = 0.dp, vertical = 0.dp),
            ) {
                Icon(
                    imageVector = AnuraIcons.Reply,
                    contentDescription = null,
                    modifier = Modifier.size(16.dp),
                )
                Spacer(modifier = Modifier.width(AnuraDimens.spaceLabelToContent))
                Text(text = stringResource(R.string.comments_reply))
            }
        }
        val stanceIcon = when (comment.stance) {
            CommentStance.Agree -> AnuraIcons.Check
            CommentStance.Disagree -> AnuraIcons.Close
            CommentStance.Neutral -> null
        }
        if (stanceIcon != null) {
            Box(
                modifier = Modifier
                    .size(AnuraDimens.sizeTouch)
                    .semantics {
                        contentDescription = if (comment.stance == CommentStance.Agree) {
                            agreeCd
                        } else {
                            disagreeCd
                        }
                    },
                contentAlignment = Alignment.Center,
            ) {
                Icon(
                    imageVector = stanceIcon,
                    contentDescription = null,
                    tint = if (comment.stance == CommentStance.Agree) {
                        AnuraTheme.extendedColors.success
                    } else {
                        MaterialTheme.colorScheme.error
                    },
                )
            }
        }
    }
}

@Composable
private fun DisagreementProposalCard(proposal: TaxonProposal) {
    val taxon = proposal.taxon
    val thumbCd = stringResource(R.string.comments_proposal_thumb_cd, taxon.scientificName)
    val rank = stringResource(
        when (taxon.rank) {
            TaxonRank.Species -> R.string.comments_rank_species
            TaxonRank.Genus -> R.string.comments_rank_genus
            TaxonRank.Family -> R.string.comments_rank_family
        },
    )
    AnuraCard(
        modifier = Modifier
            .fillMaxWidth()
            .padding(top = AnuraDimens.spaceLabelToContent),
        shape = RoundedCornerShape(AnuraDimens.radiusButton),
        bordered = true,
        color = MaterialTheme.colorScheme.surfaceVariant,
    ) {
        Row(
            modifier = Modifier.padding(
                horizontal = AnuraDimens.spaceGap,
                vertical = AnuraDimens.spaceLabelToContent,
            ),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(AnuraDimens.spaceGap),
        ) {
            Image(
                painter = painterResource(taxon.photoRes),
                contentDescription = thumbCd,
                modifier = Modifier
                    .size(56.dp)
                    .clip(RoundedCornerShape(AnuraDimens.radiusThumb)),
                contentScale = ContentScale.Crop,
                colorFilter = AnuraTheme.mediaColorFilter,
            )
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = stringResource(R.string.comments_proposal_label),
                    style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.Medium),
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
                Text(
                    text = taxon.scientificName,
                    style = MaterialTheme.typography.titleSmall.copy(
                        fontWeight = FontWeight.SemiBold,
                        fontStyle = FontStyle.Italic,
                    ),
                )
                Text(
                    text = "$rank · ${taxon.commonName}",
                    style = MaterialTheme.typography.labelSmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
                Text(
                    text = stringResource(proposal.statusRes),
                    style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.Medium),
                    color = AnuraTheme.extendedColors.accentInk,
                )
            }
        }
    }
}

@Composable
private fun TaxonMentionList(
    suggestions: List<TaxonSuggestion>,
    onPick: (TaxonSuggestion) -> Unit,
) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .background(MaterialTheme.colorScheme.surface)
            .padding(horizontal = AnuraDimens.spaceGutter, vertical = AnuraDimens.spaceLabelToContent),
        verticalArrangement = Arrangement.spacedBy(AnuraDimens.spaceLabelToContent),
    ) {
        Text(
            text = stringResource(R.string.comments_mention_hint),
            style = MaterialTheme.typography.labelSmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        suggestions.forEach { taxon ->
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(AnuraDimens.radiusButton))
                    .clickable { onPick(taxon) }
                    .padding(vertical = AnuraDimens.spaceLabelToContent)
                    .semantics { role = Role.Button },
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(AnuraDimens.spaceGap),
            ) {
                Image(
                    painter = painterResource(taxon.photoRes),
                    contentDescription = null,
                    modifier = Modifier
                        .size(40.dp)
                        .clip(RoundedCornerShape(AnuraDimens.radiusThumb)),
                    contentScale = ContentScale.Crop,
                    colorFilter = AnuraTheme.mediaColorFilter,
                )
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = "@${taxon.scientificName}",
                        style = MaterialTheme.typography.titleSmall.copy(
                            fontWeight = FontWeight.SemiBold,
                            fontStyle = FontStyle.Italic,
                        ),
                    )
                    Text(
                        text = taxon.commonName,
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }
            }
        }
    }
}

@Composable
private fun CommentComposer(
    value: String,
    replyTo: ObservationComment?,
    proposal: TaxonProposal?,
    imeVisible: Boolean,
    onValueChange: (String) -> Unit,
    onFocusChange: (Boolean) -> Unit,
    onCancelReply: () -> Unit,
    onSend: () -> Unit,
) {
    val placeholder = if (replyTo == null) {
        stringResource(R.string.comments_composer_placeholder)
    } else {
        stringResource(R.string.comments_composer_reply, replyTo.username)
    }
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(
                start = AnuraDimens.spaceGutter,
                end = AnuraDimens.spaceGutter,
                top = AnuraDimens.spaceGap,
                bottom = if (imeVisible) AnuraDimens.spaceLabelToContent else AnuraDimens.spaceGap,
            ),
    ) {
        if (replyTo != null) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(
                    text = stringResource(R.string.comments_composer_reply, replyTo.username),
                    style = MaterialTheme.typography.labelSmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    modifier = Modifier.weight(1f),
                )
                IconButton(
                    onClick = onCancelReply,
                    modifier = Modifier.size(AnuraDimens.sizeTouch),
                ) {
                    Icon(
                        imageVector = AnuraIcons.Close,
                        contentDescription = stringResource(R.string.comments_cancel_reply_cd),
                    )
                }
            }
        }
        proposal?.let { DisagreementProposalCard(it) }
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(AnuraDimens.radiusButton))
                .background(MaterialTheme.colorScheme.surfaceVariant)
                .padding(horizontal = AnuraDimens.spaceGap, vertical = AnuraDimens.spaceLabelToContent),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Box(
                modifier = Modifier
                    .size(32.dp)
                    .clip(CircleShape)
                    .background(MaterialTheme.colorScheme.surface),
                contentAlignment = Alignment.Center,
            ) {
                Icon(
                    imageVector = AnuraIcons.Person,
                    contentDescription = null,
                    modifier = Modifier.size(18.dp),
                )
            }
            Spacer(modifier = Modifier.width(AnuraDimens.spaceGap))
            BasicTextField(
                value = value,
                onValueChange = onValueChange,
                modifier = Modifier
                    .weight(1f)
                    .onFocusChanged { onFocusChange(it.isFocused) },
                textStyle = MaterialTheme.typography.bodyLarge.copy(
                    color = MaterialTheme.colorScheme.onSurface,
                ),
                cursorBrush = SolidColor(MaterialTheme.colorScheme.primary),
                decorationBox = { inner ->
                    if (value.isEmpty()) {
                        Text(
                            text = placeholder,
                            style = MaterialTheme.typography.bodyLarge,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                        )
                    }
                    inner()
                },
            )
            IconButton(
                onClick = onSend,
                enabled = value.isNotBlank() || proposal != null,
                modifier = Modifier.size(AnuraDimens.sizeTouch),
            ) {
                Icon(
                    imageVector = AnuraIcons.Send,
                    contentDescription = stringResource(R.string.comments_send_cd),
                    tint = AnuraTheme.extendedColors.accentInk,
                )
            }
        }
    }
}
