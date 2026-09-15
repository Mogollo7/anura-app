"""PARTE 11 -- Confirmar exclusion de Rhinella marina de ranking y advertencias de similitud.

Rhinella marina NO esta en el catalogo de 41 especies (species_registry.json / embeddings
Fase13). Solo existe en el pool UNKNOWN de evaluacion (fase23a_open_set_automatic). Por diseno,
nunca debe: (a) aparecer como candidata en VisualRankingAdapter.rank_visual, (b) generar
Mahalanobis contra un centroide propio en OpenSetReleaseAdapter (no tiene centroide), ni
(c) disparar advertencia de visual_similarity_groups.json (no aparece en ningun grupo).

Este test NO intenta "arreglar" nada -- confirma la exclusion correcta con evidencia.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parents[2]
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

from runtime_adapters import BioClipOnnxAdapter, OpenSetReleaseAdapter, VisualRankingAdapter, canonical_name  # noqa: E402

OUT = HERE / "stress_test_v1/rmarina_exclusion_test.json"


def main() -> None:
    results = {}

    # 1. Not in species_registry.json
    registry = json.loads((ROOT / "taxonomy/species/species_registry.json").read_text(encoding="utf-8"))
    names = {s["scientific_name"] for s in registry["species"]}
    results["in_species_registry"] = "Rhinella marina" in names
    results["rhinella_species_in_registry"] = sorted(n for n in names if n.startswith("Rhinella"))

    # 2. Not in Fase13 embeddings (any split)
    in_embeddings = False
    for split in ["reference_embeddings", "train_embeddings", "calibration_embeddings"]:
        d = np.load(ROOT / f"evaluation/fase13/embeddings/{split}.npz", allow_pickle=True)
        sp = {canonical_name(str(x)) for x in d["species"]}
        if "Rhinella marina" in sp:
            in_embeddings = True
    results["in_fase13_embeddings_any_split"] = in_embeddings

    # 3. Not a ranking candidate: VisualRankingAdapter pool of 41 names
    ranking = VisualRankingAdapter()
    results["in_visual_ranking_41_pool"] = "Rhinella marina" in ranking.names
    results["ranking_pool_size"] = len(ranking.names)

    # 4. Not an Open Set centroid
    open_set = OpenSetReleaseAdapter()
    by_name_id = {s["scientific_name"]: s["species_id"] for s in registry["species"]}
    marina_id = by_name_id.get("Rhinella marina")
    results["rhinella_marina_species_id_exists"] = marina_id is not None
    results["rhinella_marina_has_centroid_in_release"] = (
        marina_id in open_set.centroid_by_species if marina_id else False
    )

    # 5. Not in visual_similarity_groups.json
    groups = json.loads((ROOT / "validation/merlin_identification_flow/visual_similarity_groups.json").read_text(encoding="utf-8"))
    all_group_names = set()
    for g in groups["groups"]:
        all_group_names.update(g["scientific_names"])
    results["in_any_similarity_group"] = "Rhinella marina" in all_group_names
    results["documented_note_present"] = any("Rhinella marina" in n for n in groups.get("notes", []))

    # 6. End-to-end: run an actual R. marina UNKNOWN-pool image through the real runtime
    #    and confirm it never appears in the top-K ranking output (by construction it can't,
    #    since it's not in the centroid pool at all -- this proves it structurally, not just
    #    by absence of a warning).
    unknown_npz = ROOT / "validation/fase23a_open_set_automatic/embeddings/unknown_embeddings.npz"
    unk = np.load(unknown_npz, allow_pickle=True)
    unk_species = None
    for candidate_field in ("species", "true_species", "scientific_name"):
        if candidate_field in unk.files:
            unk_species = np.array([str(x) for x in unk[candidate_field]])
            break
    marina_mask = None
    if unk_species is not None:
        marina_mask = np.array(["marina" in s.lower() for s in unk_species])
        results["unknown_pool_fields"] = list(unk.files)
        results["rhinella_marina_count_in_unknown_pool"] = int(marina_mask.sum())
        if marina_mask.sum() > 0:
            marina_embedding = unk["embeddings"][marina_mask][0].astype(np.float32)
            rows, meta = ranking.rank_visual(marina_embedding)
            candidate_names = {n for n, _ in rows}
            results["rmarina_embedding_ranking_test"] = {
                "candidate_pool_size": meta["candidate_pool"],
                "rhinella_marina_appears_as_candidate": "Rhinella marina" in candidate_names,
                "top3": sorted(rows, key=lambda r: -r[1])[:3],
            }
            decision, evidence = open_set.assess(marina_embedding)
            results["rmarina_embedding_openset_test"] = {
                "decision": decision,
                "nearest_species_id": evidence.get("nearest_species_id"),
                "nearest_species_is_marina": evidence.get("nearest_species_id") == marina_id,
            }
    else:
        results["unknown_pool_fields"] = list(unk.files)
        results["note"] = "unknown_embeddings.npz no trae campo de especie legible; se omite prueba end-to-end con imagen real, la exclusion estructural (1-5) ya es concluyente."

    results["verdict"] = {
        "RMARINA_CORRECTLY_EXCLUDED": bool(
            (not results["in_visual_ranking_41_pool"])
            and (not results["rhinella_marina_has_centroid_in_release"])
            and (not results["in_any_similarity_group"])
        ),
        "reason": (
            "Rhinella marina no tiene species_id en el registro, no tiene centroide en el release "
            "de 41, y por lo tanto estructuralmente NO PUEDE aparecer en ranking ni en Open Set ni "
            "en advertencias de similitud visual -- no porque una regla la filtre en tiempo de "
            "ejecucion, sino porque nunca entro al catalogo de especies disponibles del modelo. "
            "Esto es la limitacion intencional ya documentada; no se repara ni se agrega."
        ),
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(results["verdict"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
