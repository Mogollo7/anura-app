"""
phase_reproduce_23a.py — GATE de reproduccion del scoring oficial de Fase 23A.

Objetivo: reproducir EXACTAMENTE el metodo `euclidean_raw` de
validation/fase23a_open_set_automatic/method_comparison.csv (AUROC oficial =
0.5732919408781961), usando la MISMA logica que el script original que genero
ese CSV (recuperado desde el scratchpad de la sesion anterior:
fase23a_run.py). No se modifica NINGUN artefacto de fase23a_open_set_automatic/,
fase16_clean_open_set/, ni los embeddings/encoder existentes. Solo lectura.

Metodologia reproducida (idéntica al script original):
  1. Centroides de 41 especies construidos desde
     evaluation/fase13/embeddings/reference_embeddings.npz (Group A, interseccion
     con train) y evaluation/fase13/embeddings/train_embeddings.npz (Group B,
     el resto). 9 Group A + 32 Group B.
  2. KNOWN pool = validation/fase16_clean_open_set/clean_known_embeddings.npz
     (NO leave-one-out: los centroides vienen de reference/train, un conjunto
     DISTINTO al KNOWN pool evaluado -> no hay contaminacion circular).
  3. UNKNOWN pool = validation/fase23a_open_set_automatic/embeddings/unknown_embeddings.npz
     (620 imagenes).
  4. Score = distancia euclidiana minima de cada embedding a los 41 centroides.
  5. AUROC calculado sobre y_is_known (1=KNOWN, 0=UNKNOWN) vs score_is_known=-distancia,
     es decir TODOS los KNOWN (7475) + TODOS los UNKNOWN (620) entran juntos al roc_auc_score
     (no split adicional, no submuestreo).
"""
import json
from pathlib import Path

import numpy as np
from sklearn.metrics import roc_auc_score

BASE = Path("D:/Anura")
OUT = BASE / "validation/fase23a_geographic_context"
OUT.mkdir(parents=True, exist_ok=True)


def canonical(name):
    n = name.replace('_', ' ').strip()
    if n == "Pristimantis acanthinus":
        n = "Pristimantis achatinus"
    return n


def compute_centroids(X, y):
    out = {}
    for c in np.unique(y):
        out[c] = np.mean(X[y == c], axis=0)
    return out


def min_euclidean(X, C):
    d = np.linalg.norm(X[:, None, :] - C[None, :, :], axis=2)
    return np.min(d, axis=1)


def main():
    # ---------- 1. Centroides de 41 especies (Group A / Group B) ----------
    ref_data = np.load(BASE / "evaluation/fase13/embeddings/reference_embeddings.npz")
    X_ref, y_ref = ref_data["embeddings"], np.array([canonical(s) for s in ref_data["species"]])
    ref_centroids = compute_centroids(X_ref, y_ref)

    train_data = np.load(BASE / "evaluation/fase13/embeddings/train_embeddings.npz")
    X_train, y_train = train_data["embeddings"], np.array([canonical(s) for s in train_data["species"]])
    train_centroids = compute_centroids(X_train, y_train)

    all_41_centroids = {}
    group_a, group_b = set(), set()
    for sp, c in ref_centroids.items():
        if sp in train_centroids:
            all_41_centroids[sp] = c
            group_a.add(sp)
    for sp, c in train_centroids.items():
        if sp not in all_41_centroids:
            all_41_centroids[sp] = c
            group_b.add(sp)

    assert len(all_41_centroids) == 41, len(all_41_centroids)
    assert len(group_a) == 9, len(group_a)
    assert len(group_b) == 32, len(group_b)
    classes = sorted(all_41_centroids.keys())
    C = np.array([all_41_centroids[c] for c in classes])
    print(f"Centroids built: {len(all_41_centroids)} (GroupA={len(group_a)}, GroupB={len(group_b)})")

    # ---------- 2. KNOWN pool (fase16 clean, NO leave-one-out) ----------
    known = np.load(BASE / "validation/fase16_clean_open_set/clean_known_embeddings.npz", allow_pickle=True)
    X_known = known["embeddings"].astype(np.float32)
    print("KNOWN pool:", X_known.shape)

    # ---------- 3. UNKNOWN pool (fase23a, real BioCLIP inference, ya existente) ----------
    unk = np.load(BASE / "validation/fase23a_open_set_automatic/embeddings/unknown_embeddings.npz", allow_pickle=True)
    X_unknown = unk["embeddings"].astype(np.float32)
    print("UNKNOWN pool:", X_unknown.shape)

    assert X_known.shape[1] == 512 and X_unknown.shape[1] == 512
    assert not np.isnan(X_known).any() and not np.isnan(X_unknown).any()

    # ---------- 4. Scores = distancia euclidiana minima a los 41 centroides ----------
    d_known = min_euclidean(X_known, C)
    d_unknown = min_euclidean(X_unknown, C)
    d_all = np.concatenate([d_known, d_unknown])

    y_is_known = np.concatenate([np.ones(len(X_known)), np.zeros(len(X_unknown))]).astype(int)
    score_is_known = -d_all  # mayor score = mas probable known

    auroc = float(roc_auc_score(y_is_known, score_is_known))

    OFFICIAL_AUROC = 0.5732919408781961
    diff = abs(auroc - OFFICIAL_AUROC)
    TOLERANCE = 0.02
    passed = diff <= TOLERANCE

    result = {
        "gate": "reproduce_fase23a_euclidean_raw",
        "official_auroc": OFFICIAL_AUROC,
        "reproduced_auroc": auroc,
        "abs_diff": diff,
        "tolerance": TOLERANCE,
        "gate_passed": passed,
        "n_known": int(len(X_known)),
        "n_unknown": int(len(X_unknown)),
        "n_official_known": 7475,
        "n_official_unknown": 620,
        "n_known_matches_official": int(len(X_known)) == 7475,
        "n_unknown_matches_official": int(len(X_unknown)) == 620,
        "method": "euclidean_raw (min distance to 41 species centroids; centroids from "
                  "reference_embeddings.npz + train_embeddings.npz, KNOWN pool = "
                  "fase16_clean_open_set/clean_known_embeddings.npz, no leave-one-out, "
                  "no additional subsampling)",
        "sources": {
            "reference_embeddings": "evaluation/fase13/embeddings/reference_embeddings.npz",
            "train_embeddings": "evaluation/fase13/embeddings/train_embeddings.npz",
            "known_pool": "validation/fase16_clean_open_set/clean_known_embeddings.npz",
            "unknown_pool": "validation/fase23a_open_set_automatic/embeddings/unknown_embeddings.npz",
            "recovered_original_script": "fase23a_run.py (recovered from prior session scratchpad, "
                                          "not present in repo; logic replicated verbatim in this script)",
        },
    }

    out_path = OUT / "baseline_reproduction_v2.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    # Persist scores for downstream reuse (Problem 3) without recomputation
    np.savez_compressed(
        OUT / "reproduced_scores_v2.npz",
        d_known=d_known,
        d_unknown=d_unknown,
        y_is_known=y_is_known,
        species_known=known["species_ids"],
        image_known=known["image_ids"],
        species_unknown=unk["species"],
        obs_unknown=unk["observation_id"],
    )

    print(json.dumps(result, indent=2))
    print("\nGATE PASSED" if passed else "\nGATE FAILED")


if __name__ == "__main__":
    main()
