package me.juanlabs.anura.feature.explore

import androidx.compose.runtime.Composable
import me.juanlabs.anura.navigation.MockNavAction
import me.juanlabs.anura.navigation.MockScreenScaffold

/** `explorar` (§4.1) — top-level, tab 2. */
@Composable
fun ExploreScreen(
    onOpenSpeciesByTaxon: (String) -> Unit,
    onOpenSpeciesSheet: (String) -> Unit,
) {
    MockScreenScaffold(
        title = "Explorar",
        actions = listOf(
            MockNavAction("Ver especies del género/familia") { onOpenSpeciesByTaxon("taxon-anura") },
            MockNavAction("Ver ficha de especie") { onOpenSpeciesSheet("ANU_COL_PRIS_PAI_001") },
        ),
    )
}

/** `explorar → Especies del género o familia` (§4.1, argumento `taxonId`). */
@Composable
fun SpeciesByTaxonScreen(
    taxonId: String,
    onBackClick: () -> Unit,
    onOpenSpeciesSheet: (String) -> Unit,
) {
    MockScreenScaffold(
        title = "Especies de $taxonId",
        onBackClick = onBackClick,
        actions = listOf(
            MockNavAction("Ver ficha de especie") { onOpenSpeciesSheet("ANU_COL_PRIS_PAI_001") },
        ),
    )
}
