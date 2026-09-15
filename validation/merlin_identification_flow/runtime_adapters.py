"""Runtime adapters that read frozen ANURA artifacts without modifying them."""
from __future__ import annotations

import csv
import hashlib
import json
import time
from pathlib import Path
from typing import Any, Iterable, Mapping

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
ONNX_PATH = ROOT / "bioclip/checkpoints/encoder_anura_fp16.onnx"
ONNX_SHA256 = "219e860e6fa9a80fb30a59fc8f61911421bbd53a4537dca831803d3ab446b2ad"
PYTORCH_CHECKPOINT = ROOT / "bioclip/checkpoints/bioclip_anura_mejor.pt"
PYTORCH_SHA256 = "98a6c54d6edb27e2b0344b8bbbaebd2ab749b1bf5136991ff73b37f66ee2c1ac"


def canonical_name(name: str) -> str:
    value = name.replace("_", " ").strip()
    return "Pristimantis achatinus" if value == "Pristimantis acanthinus" else value


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


class BioClipOnnxAdapter:
    """Runs the Fase-9 frozen FP16 ONNX encoder with the Fase-13 preprocess."""

    def __init__(self) -> None:
        import onnxruntime as ort
        import open_clip

        actual = sha256(ONNX_PATH)
        if actual != ONNX_SHA256:
            raise RuntimeError("Frozen ONNX SHA256 mismatch")
        if sha256(PYTORCH_CHECKPOINT) != PYTORCH_SHA256:
            raise RuntimeError("Source PyTorch checkpoint SHA256 mismatch")
        # This is the exact preprocessing constructor used by Fase 9/13.
        _, _, self.preprocess = open_clip.create_model_and_transforms("hf-hub:imageomics/bioclip")
        self.session = ort.InferenceSession(str(ONNX_PATH), providers=["CPUExecutionProvider"])
        self.input_name = self.session.get_inputs()[0].name

    def embed_image(self, image_path: Path) -> tuple[np.ndarray, dict[str, Any]]:
        from PIL import Image

        start = time.perf_counter()
        with Image.open(image_path).convert("RGB") as image:
            tensor = self.preprocess(image).unsqueeze(0).numpy().astype(np.float32)
        embedding = self.session.run(None, {self.input_name: tensor})[0][0].astype(np.float32)
        norm = float(np.linalg.norm(embedding))
        if not np.isfinite(norm) or norm == 0:
            raise RuntimeError("Invalid encoder embedding")
        # Exported encoder already normalizes; this check detects a contract break.
        if not np.isclose(norm, 1.0, atol=1e-3):
            raise RuntimeError(f"ONNX output is not L2 normalized: {norm}")
        return embedding, {
            "encoder_id": "bioclip_anura_v1",
            "runtime_code_version": "merlin-runtime-adapters/v0.2.0",
            "encoder_file": str(ONNX_PATH.relative_to(ROOT)),
            "encoder_sha256": ONNX_SHA256,
            "source_checkpoint_sha256": PYTORCH_SHA256,
            "embedding_dim": int(embedding.shape[0]),
            "normalization": "L2",
            "preprocessing": "open_clip.create_model_and_transforms(hf-hub:imageomics/bioclip)",
            "provider": self.session.get_providers()[0],
            "dtype": str(embedding.dtype),
            "inference_ms": round((time.perf_counter() - start) * 1000, 3),
        }


class VisualRankingAdapter:
    """Reads Fase-13 embeddings and applies GEO-6 stage-1 visual normalization."""

    def __init__(self) -> None:
        ref = np.load(ROOT / "evaluation/fase13/embeddings/reference_embeddings.npz")
        train = np.load(ROOT / "evaluation/fase13/embeddings/train_embeddings.npz")
        ref_y = np.array([canonical_name(str(x)) for x in ref["species"]])
        train_y = np.array([canonical_name(str(x)) for x in train["species"]])
        # Exact GEO-6 policy: REFERENCE centroid only when its class also exists
        # in TRAIN; then add TRAIN-only classes. This avoids changing the 41 pool.
        train_centroids = {name: train["embeddings"][train_y == name].mean(axis=0) for name in np.unique(train_y)}
        centroids = {
            name: ref["embeddings"][ref_y == name].mean(axis=0)
            for name in np.unique(ref_y) if name in train_centroids
        }
        for name, centroid in train_centroids.items():
            centroids.setdefault(name, centroid)
        self.names = sorted(centroids)
        self.centroids = np.asarray([centroids[name] for name in self.names], dtype=np.float32)
        if len(self.names) != 41:
            raise RuntimeError(f"Expected GEO-6 pool of 41 centroids, got {len(self.names)}")

    def rank_visual(
        self, embedding: np.ndarray, active_names: Iterable[str] | None = None
    ) -> tuple[list[tuple[str, float]], dict[str, Any]]:
        """Ranking restringido al CATALOGO ACTIVO.

        ``active_names is None`` significa "sin gestor de paquetes conectado":
        se usa el pool historico completo (comportamiento previo, preservado
        para los tests deterministas existentes). Cuando se pasa el catalogo
        activo, una especie inactiva NO aparece en el ranking NI participa en
        la normalizacion min-max.
        """
        if active_names is None:
            indices = list(range(len(self.names)))
            scope = "FULL_RELEASE_POOL"
        else:
            allowed = set(active_names)
            indices = [i for i, name in enumerate(self.names) if name in allowed]
            scope = "ACTIVE_CATALOG"
        if not indices:
            return [], {
                "candidate_pool": 0,
                "pool_scope": scope,
                "visual_metric": "negative_euclidean_distance_row_minmax",
                "nearest_distance": None,
                "reason": "NO_ACTIVE_SPECIES_IN_CATALOG",
            }
        names = [self.names[i] for i in indices]
        centroids = self.centroids[indices]
        distances = np.linalg.norm(centroids - embedding[None, :], axis=1)
        similarity = -distances
        lo, hi = float(similarity.min()), float(similarity.max())
        normalized = np.zeros_like(similarity) if hi - lo < 1e-12 else (similarity - lo) / (hi - lo)
        rows = list(zip(names, [float(value) for value in normalized]))
        return rows, {
            "candidate_pool": len(names),
            "pool_scope": scope,
            "release_pool_size": len(self.names),
            "visual_metric": "negative_euclidean_distance_row_minmax",
            "nearest_distance": float(distances.min()),
        }


class GeographicAdapter:
    """Frozen GEO-6 species-prior lookup. No location means no geographic signal."""

    def __init__(self) -> None:
        map_path = ROOT / "COLOMBIA_ANURA/ANTIOQUIA/zones/cell_zone_map_v1.csv"
        prior_path = ROOT / "validation/fase23a_geographic_context/prior_zone_taxon_v2_clean.csv"
        manifest = json.loads((ROOT / "validation/fase23a_geographic_context/prior_zone_taxon_v2_clean_manifest.json").read_text(encoding="utf-8"))
        self.cell_zone: dict[str, str] = {}
        with map_path.open(encoding="utf-8", newline="") as source:
            for row in csv.DictReader(source):
                if row["in_department"].lower() == "true" and row["zone_final"]:
                    self.cell_zone[row["cell_id"]] = row["zone_final"]
        self.prior: dict[tuple[str, str], float] = {}
        self.zone_effective: dict[str, float] = {}
        with prior_path.open(encoding="utf-8", newline="") as source:
            for row in csv.DictReader(source):
                self.prior[(row["zone_id"], canonical_name(row["scientific_name"]))] = float(row["p"])
                self.zone_effective[row["zone_id"]] = self.zone_effective.get(row["zone_id"], 0.0) + float(row["n_effective"])
        self.alpha, self.k = float(manifest["alpha_selected"]), int(manifest["K_taxa"])
        self.neutral = 1.0 / self.k

    def scores(self, names: list[str], latitude: float | None, longitude: float | None) -> tuple[dict[str, float], dict[str, Any]]:
        if latitude is None or longitude is None:
            return {}, {"available": False, "reason": "LOCATION_UNAVAILABLE"}
        cell_id = f"G025_{int(round(latitude / 0.25))}_{int(round(longitude / 0.25))}"
        zone = self.cell_zone.get(cell_id)
        if zone is None:
            return {}, {"available": False, "reason": "LOCATION_OUTSIDE_GEO_COVERAGE", "cell_id": cell_id}
        raw = []
        for name in names:
            raw.append(self.prior.get((zone, canonical_name(name)), self.alpha / (self.zone_effective[zone] + self.alpha * self.k)))
        lo, hi = min(raw), max(raw)
        normalized = [0.0] * len(raw) if hi - lo < 1e-12 else [(value - lo) / (hi - lo) for value in raw]
        return dict(zip(names, normalized)), {"available": True, "zone_id": zone, "cell_id": cell_id, "prior": "prior_zone_taxon_v2_clean", "normalization": "GEO6_row_minmax"}


class OpenSetReleaseAdapter:
    """Versioned Mahalanobis release; does not use GEO-6 batch-normalized score."""

    def __init__(self) -> None:
        catalog = json.loads((ROOT / "visual_catalog/v1.0.0/manifest.json").read_text(encoding="utf-8"))
        covariance_manifest = json.loads((ROOT / "covariance/v1.0.0/manifest.json").read_text(encoding="utf-8"))
        threshold_manifest = json.loads((ROOT / "threshold/v1.0.0/manifest.json").read_text(encoding="utf-8"))
        expected = ONNX_SHA256
        if not all(item == expected for item in [catalog["encoder_sha256"], covariance_manifest["encoder_contract"]["encoder_sha256"], threshold_manifest["encoder_contract"]["encoder_sha256"]]):
            raise RuntimeError("Open Set release encoder contract is incompatible")
        registry = json.loads((ROOT / "taxonomy/species/species_registry.json").read_text(encoding="utf-8"))
        by_name = {item["scientific_name"]: item["species_id"] for item in registry["species"]}
        ref, train = np.load(ROOT / "evaluation/fase13/embeddings/reference_embeddings.npz"), np.load(ROOT / "evaluation/fase13/embeddings/train_embeddings.npz")
        ref_y = np.array([canonical_name(str(x)) for x in ref["species"]])
        train_y = np.array([canonical_name(str(x)) for x in train["species"]])
        allowed = set(catalog["species_ids"])
        means: dict[str, np.ndarray] = {}
        for name in np.unique(ref_y):
            if by_name.get(name) in allowed:
                means[by_name[name]] = ref["embeddings"][ref_y == name].mean(axis=0)
        for name in np.unique(train_y):
            if by_name.get(name) in allowed and by_name[name] not in means:
                means[by_name[name]] = train["embeddings"][train_y == name].mean(axis=0)
        if set(means) != allowed:
            raise RuntimeError("Open Set centroid release is incomplete")
        # BUGFIX DYNAMIC_REMOVE_SPECIES_FAIL: se conserva el mapeo
        # species_id -> centroide. Antes se hacia `list(means.values())`, lo
        # que descartaba la identidad de cada centroide y hacia imposible
        # filtrar por catalogo activo o reportar la especie mas cercana.
        self.release_species_ids: list[str] = sorted(means)
        self.centroid_by_species: dict[str, np.ndarray] = {
            species_id: np.asarray(means[species_id], dtype=np.float32) for species_id in self.release_species_ids
        }
        self.centroids = np.stack([self.centroid_by_species[s] for s in self.release_species_ids])
        self.precision = np.load(ROOT / "covariance/v1.0.0/covariance_matrix.npz")["precision"].astype(np.float32)
        self.threshold = float(threshold_manifest["threshold"])
        self.release = threshold_manifest["threshold_release"]

    def _active_matrix(
        self,
        active_species_ids: Iterable[str] | None,
        active_prototypes: Mapping[str, np.ndarray] | None,
    ) -> tuple[list[str], np.ndarray, str]:
        """Resuelve QUE centroides participan. La fuente de verdad es el catalogo activo."""
        if active_prototypes is not None:
            ids = sorted(active_prototypes)
            if active_species_ids is not None:
                allowed = set(active_species_ids)
                ids = [s for s in ids if s in allowed]
            if not ids:
                return [], np.zeros((0, self.centroids.shape[1]), dtype=np.float32), "ACTIVE_PACKAGE_PROTOTYPES"
            matrix = np.stack([np.asarray(active_prototypes[s], dtype=np.float32) for s in ids])
            return ids, matrix, "ACTIVE_PACKAGE_PROTOTYPES"
        if active_species_ids is not None:
            ids = [s for s in self.release_species_ids if s in set(active_species_ids)]
            if not ids:
                return [], np.zeros((0, self.centroids.shape[1]), dtype=np.float32), "ACTIVE_CATALOG_FILTERED_RELEASE"
            return ids, np.stack([self.centroid_by_species[s] for s in ids]), "ACTIVE_CATALOG_FILTERED_RELEASE"
        # Sin gestor de paquetes conectado: pool historico completo (compat).
        return list(self.release_species_ids), self.centroids, "FULL_RELEASE_POOL"

    def _declared_membership(
        self,
        active_species_ids: Iterable[str] | None,
        active_prototypes: Mapping[str, np.ndarray] | None,
    ) -> tuple[frozenset[str] | None, str]:
        """Catalogo contra el que se verifica PERTENENCIA, independiente de los centroides.

        - ``active_species_ids`` declarado -> ese es el catalogo activo.
        - Sin gestor de paquetes (ambos None) -> catalogo del release congelado
          (modo historico, sin cambio de comportamiento).
        - Prototipos sin catalogo declarado -> pertenencia desconocida (fail-closed).
        """
        if active_species_ids is not None:
            return frozenset(active_species_ids), "ACTIVE_CATALOG"
        if active_prototypes is None:
            return frozenset(self.release_species_ids), "FROZEN_RELEASE_CATALOG_NO_PACKAGE_MANAGER"
        return None, "UNDECLARED"

    def assess(
        self,
        embedding: np.ndarray,
        active_species_ids: Iterable[str] | None = None,
        active_prototypes: Mapping[str, np.ndarray] | None = None,
    ) -> tuple[str, dict[str, Any]]:
        """Evalua Open Set SOLO contra los prototipos del catalogo activo.

        Flujo: paquetes instalados -> paquetes activos -> especies activas ->
        prototipos activos -> centroide mas cercano -> PERTENENCIA al catalogo
        activo -> threshold. La pertenencia es una precondicion independiente
        del threshold: un centroide residual/ajeno al catalogo nunca llega a
        compararse con el threshold. La matriz de precision y el threshold
        siguen viniendo del release historico congelado (sin recalibrar).
        """
        membership, membership_source = self._declared_membership(active_species_ids, active_prototypes)
        ids, matrix, source = self._active_matrix(active_species_ids, active_prototypes)
        base = {
            "status": "RELEASE_THRESHOLD",
            "decision_basis": "Mahalanobis min-distance to nearest ACTIVE catalog centroid",
            "centroid_source": source,
            "active_centroid_count": len(ids),
            "release_centroid_count": len(self.release_species_ids),
            "threshold": self.threshold,
            "threshold_release": self.release,
            "thresholds_production_ready": False,
            "rejected_means": "NO_CONCLUYENTE; NO_REGISTRADA is not asserted",
            "catalog_membership": {
                "source": membership_source,
                "declared_species_count": None if membership is None else len(membership),
                "checked_before_threshold": True,
            },
        }
        if membership is None:
            base.update({"score": None, "nearest_species_id": None, "reason": "CATALOG_MEMBERSHIP_UNDECLARED"})
            return "NO_CONCLUYENTE", base
        if not ids:
            # Sin especies activas NUNCA se puede afirmar ESPECIE_CONOCIDA.
            base.update(
                {
                    "score": None,
                    "nearest_species_id": None,
                    "reason": "NO_ACTIVE_SPECIES_IN_CATALOG",
                }
            )
            return "NO_CONCLUYENTE", base
        diffs = matrix - embedding[None, :]
        distances = np.sqrt(np.maximum(0.0, np.einsum("kd,de,ke->k", diffs, self.precision, diffs)))
        index = int(np.argmin(distances))
        score = float(distances[index])
        nearest = ids[index]
        base.update(
            {
                "score": score,
                "nearest_species_id": nearest,
                "excluded_centroid_count": len(self.release_species_ids) - len(ids),
            }
        )
        base["catalog_membership"]["nearest_in_catalog"] = nearest in membership
        if nearest not in membership:
            # Centroide residual/ajeno: se rechaza ANTES del threshold, sin importar su distancia.
            base.update({"score": None, "nearest_species_id": None, "reason": "NEAREST_CENTROID_NOT_IN_ACTIVE_CATALOG"})
            base["catalog_membership"].update({"rejected_species_id": nearest, "rejected_score": score})
            return "NO_CONCLUYENTE", base
        return ("ESPECIE_CONOCIDA" if score <= self.threshold else "NO_CONCLUYENTE"), base
