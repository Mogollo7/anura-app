"""End-to-end integration: image -> frozen runtime adapters -> IdentificationResult.

Cadena de catalogo (post-bugfix DYNAMIC_REMOVE_SPECIES_FAIL y
OPEN_SET_PACKAGE_ISOLATION):
    estado persistido -> paquetes activos -> especies activas ->
    prototipos activos -> ranking visual + Open Set -> pertenencia -> decision.

Cada inferencia usa UNA instantanea inmutable del catalogo activo leida del
estado persistido (``LocalPackageManager.active_catalog_snapshot``). Ninguna
especie fuera de esa instantanea puede ser candidata ni ESPECIE_CONOCIDA.

El release historico (visual_catalog/threshold/covariance v1.0.0) se sigue
leyendo para la matriz de precision, el threshold y el contrato de encoder,
pero YA NO decide que centroides participan.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from merlin_flow import MerlinFlow, VisualCandidate
from package_manager import ActiveCatalogSnapshot, LocalPackageManager
from runtime_adapters import BioClipOnnxAdapter, GeographicAdapter, OpenSetReleaseAdapter, VisualRankingAdapter


class MerlinRuntimePipeline:
    def __init__(self, package_manager: LocalPackageManager | None = None) -> None:
        self.bioclip = BioClipOnnxAdapter()
        self.ranking = VisualRankingAdapter()
        self.geographic = GeographicAdapter()
        self.open_set = OpenSetReleaseAdapter()
        self.flow = MerlinFlow()
        self.packages = package_manager

    def _active_catalog(self) -> tuple[list[str] | None, dict[str, Any] | None, list[str] | None, dict[str, Any]]:
        """Devuelve (species_ids activos, prototipos activos, nombres activos, estado)."""
        return self._active_catalog_with_snapshot()[:4]

    def _active_catalog_with_snapshot(
        self,
    ) -> tuple[list[str] | None, dict[str, Any] | None, list[str] | None, dict[str, Any], ActiveCatalogSnapshot | None]:
        """Como ``_active_catalog`` + la instantanea de la que sale todo.

        Con gestor, todo sale de UNA instantanea construida desde el estado
        persistido en el momento de la inferencia; el pipeline no la conserva.
        """
        if self.packages is None:
            return None, None, None, {
                "source": "STATIC_SPECIES_REGISTRY",
                "package_manager_connected": False,
                "note": "Sin gestor de paquetes: se usa el pool historico completo.",
            }, None
        snapshot = self.packages.active_catalog_snapshot()
        state = snapshot.summary()
        state.update({
            "source": "PACKAGE_MANAGER",
            "package_manager_connected": True,
            "catalog_fingerprint": snapshot.fingerprint,
        })
        return list(snapshot.species_ids), snapshot.prototype_map(), snapshot.scientific_names, state, snapshot

    def identify_image(
        self,
        image_path: Path,
        observation_id: str,
        *,
        is_anuran: bool | None,
        anuran_evidence: dict[str, Any],
        latitude: float | None = None,
        longitude: float | None = None,
        top_k: int = 3,
    ) -> dict[str, Any]:
        embedding, model_metadata = self.bioclip.embed_image(image_path)
        active_ids, active_prototypes, active_names, catalog_state, snapshot = self._active_catalog_with_snapshot()

        visual_rows, visual_metadata = self.ranking.rank_visual(embedding, active_names)
        # No ground truth, filename-derived species, or test labels enter this path.
        # El registro taxonomico es metadata; con gestor, ademas debe pertenecer al catalogo activo.
        known_visual_rows = [
            (name, score)
            for name, score in visual_rows
            if name in self.flow.catalog
            and (snapshot is None or snapshot.contains(self.flow.catalog[name]["species_id"]))
        ]
        geo_scores, geo_metadata = self.geographic.scores([name for name, _ in known_visual_rows], latitude, longitude)
        open_set_decision, open_set_evidence = self.open_set.assess(
            embedding, active_species_ids=active_ids, active_prototypes=active_prototypes
        )
        groups = (
            self.packages.active_visual_similarity_groups(
                Path(__file__).parent / "visual_similarity_groups.json", packages=snapshot.packages
            )
            if snapshot is not None
            else None
        )
        input_metadata = {
            "image_path": str(image_path),
            "runtime": {"bioclip": model_metadata, "visual_ranking": visual_metadata, "geographic": geo_metadata},
        }
        result = self.flow.identify(
            observation_id=observation_id,
            input_metadata=input_metadata,
            is_anuran=is_anuran,
            anuran_evidence=anuran_evidence,
            visual_candidates=[VisualCandidate(name, score) for name, score in known_visual_rows],
            geographic_scores=geo_scores,
            geographic_context_available=bool(geo_metadata["available"]),
            open_set_decision=open_set_decision,
            open_set_evidence_override=open_set_evidence,
            visual_similarity_groups=groups,
            catalog_state=catalog_state,
            active_species_ids=active_ids,
            top_k=top_k,
            model_version="bioclip_anura_v1/encoder_anura_fp16.onnx",
        )
        result["experimental_flags"].append("GEO6_OPEN_SET_NOT_USED_FOR_SINGLE_SAMPLE_INFERENCE")
        return result
