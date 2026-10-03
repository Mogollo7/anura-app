"""
rebaseline_delabeling_fixed.py

Parte 3 de la corrección de contaminación de etiquetado Dendropsophus_labialis /
Dendropsophus_molitor (ver data/unknown_open_set_v2/audit/LEAKAGE_AUDIT_CORRECTION_v2.md).

Reconstruye el pool UNKNOWN "v2_delabeling_fixed" a partir de
unknown_embeddings.npz (620 imagenes originales), EXCLUYENDO las imagenes de
Dendropsophus_labialis cuyo observation_id coincide con una observacion ya
presente en el pool KNOWN Dendropsophus_molitor (34 observation_id, 56 de las
74 imagenes originales de labialis). Todas las demas especies (incluida
Rhinella_marina completa) quedan sin cambios.

Reutiliza EXACTAMENTE la logica de scoring de
validation/fase23a_geographic_context/scripts/phase_reproduce_23a.py
(min-distancia euclidiana a 41 centroides de especie, KNOWN pool =
fase16_clean_open_set/clean_known_embeddings.npz, sin leave-one-out).

No modifica ningun artefacto existente. Solo lee.
"""
import json
import os
import re
from pathlib import Path

import numpy as np
from sklearn.metrics import roc_auc_score

BASE = Path("D:/Anura")
OUT = BASE / "validation/fase23a_delabeling_correction_v1"
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


def bootstrap_auroc(y_true, scores, groups, n_iter=1000, seed=42):
    """Bootstrap estratificado por individuo (obs/known-image id vale como 'individuo' proxy).
    Resample con reemplazo DENTRO de cada grupo (known vs unknown) preservando el numero de
    grupos unicos de cada lado, muestreando por grupos unicos (observation/known ids) para no
    romper correlacion intra-observacion. Implementacion vectorizada: precomputa indices por
    grupo UNA vez (dict), luego cada iteracion solo hace lookups O(1) + concatenate — evita
    recomputar mascaras booleanas de tamano completo en cada una de las 1000 iteraciones."""
    rng = np.random.default_rng(seed)
    y_true = np.asarray(y_true)
    scores = np.asarray(scores)
    groups = np.asarray(groups)

    known_idx = np.where(y_true == 1)[0]
    unknown_idx = np.where(y_true == 0)[0]

    known_groups = groups[known_idx]
    unknown_groups = groups[unknown_idx]

    # Precompute group -> array of global indices, once.
    known_group_to_idx = {}
    for g, idx in zip(known_groups, known_idx):
        known_group_to_idx.setdefault(g, []).append(idx)
    known_group_to_idx = {k: np.array(v, dtype=int) for k, v in known_group_to_idx.items()}

    unknown_group_to_idx = {}
    for g, idx in zip(unknown_groups, unknown_idx):
        unknown_group_to_idx.setdefault(g, []).append(idx)
    unknown_group_to_idx = {k: np.array(v, dtype=int) for k, v in unknown_group_to_idx.items()}

    uniq_known_groups = np.array(list(known_group_to_idx.keys()))
    uniq_unknown_groups = np.array(list(unknown_group_to_idx.keys()))

    aurocs = []
    for i in range(n_iter):
        rk = rng.choice(uniq_known_groups, size=len(uniq_known_groups), replace=True)
        ru = rng.choice(uniq_unknown_groups, size=len(uniq_unknown_groups), replace=True)

        sel_known = np.concatenate([known_group_to_idx[g] for g in rk])
        sel_unknown = np.concatenate([unknown_group_to_idx[g] for g in ru])

        y_bs = np.concatenate([y_true[sel_known], y_true[sel_unknown]])
        s_bs = np.concatenate([scores[sel_known], scores[sel_unknown]])
        if len(np.unique(y_bs)) < 2:
            continue
        try:
            aurocs.append(roc_auc_score(y_bs, s_bs))
        except ValueError:
            continue
    aurocs = np.array(aurocs)
    return {
        "n_valid_iter": int(len(aurocs)),
        "mean": float(np.mean(aurocs)),
        "std": float(np.std(aurocs)),
        "ci95_lo": float(np.percentile(aurocs, 2.5)),
        "ci95_hi": float(np.percentile(aurocs, 97.5)),
    }


def far_frr_balanced_acc(y_is_known, score_is_known, threshold_score):
    """threshold_score se aplica a score_is_known (mayor = mas 'known').
    Predicho KNOWN si score_is_known >= threshold_score."""
    pred_known = (score_is_known >= threshold_score).astype(int)
    known_mask = y_is_known == 1
    unknown_mask = y_is_known == 0

    # FAR = False Accept Rate = UNKNOWN aceptados como KNOWN / total UNKNOWN
    far = float(np.mean(pred_known[unknown_mask] == 1)) if unknown_mask.sum() else float("nan")
    # FRR = False Reject Rate = KNOWN rechazados como UNKNOWN / total KNOWN
    frr = float(np.mean(pred_known[known_mask] == 0)) if known_mask.sum() else float("nan")
    bal_acc = float((1 - far) + (1 - frr)) / 2.0
    return far, frr, bal_acc


def find_official_threshold():
    """Busca el threshold oficial de Fase 23A ya calculado, para aplicar el MISMO
    protocolo de threshold (no recalcular uno nuevo)."""
    candidates = [
        BASE / "validation/fase23a_open_set_automatic/method_comparison.csv",
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


def main():
    # ---------- Centroides (idéntico a phase_reproduce_23a.py) ----------
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
    assert len(all_41_centroids) == 41
    classes = sorted(all_41_centroids.keys())
    C = np.array([all_41_centroids[c] for c in classes])

    # ---------- KNOWN pool (fase16 clean, sin cambios) ----------
    known = np.load(BASE / "validation/fase16_clean_open_set/clean_known_embeddings.npz", allow_pickle=True)
    X_known = known["embeddings"].astype(np.float32)
    known_ids = known["image_ids"]

    # ---------- UNKNOWN pool original (620 imgs) ----------
    unk = np.load(BASE / "validation/fase23a_open_set_automatic/embeddings/unknown_embeddings.npz", allow_pickle=True)
    X_unknown_full = unk["embeddings"].astype(np.float32)
    species_unknown = unk["species"]
    obs_unknown = unk["observation_id"]
    paths_unknown = unk["paths"]

    # ---------- Identificar contaminacion (34 obs_id de labialis presentes en molitor KNOWN) ----------
    molitor_dir = BASE / "data cleaned/Dendropsophus_molitor"
    molitor_obs = set()
    for f in os.listdir(molitor_dir):
        m = re.match(r"col_obs_(\d+)_photo", f)
        if m:
            molitor_obs.add(m.group(1))

    is_labialis = np.array(['labialis' in str(s) for s in species_unknown])
    is_contaminated = is_labialis & np.array([o in molitor_obs for o in obs_unknown])

    n_excluded = int(is_contaminated.sum())
    keep_mask = ~is_contaminated
    X_unknown_clean = X_unknown_full[keep_mask]
    species_clean = species_unknown[keep_mask]
    obs_clean = obs_unknown[keep_mask]
    paths_clean = paths_unknown[keep_mask]

    print(f"Original UNKNOWN pool: {len(X_unknown_full)}")
    print(f"Excluded (contaminated labialis/molitor obs): {n_excluded}")
    print(f"Corrected UNKNOWN pool (v2_delabeling_fixed): {len(X_unknown_clean)}")

    # ---------- Scores: oficial (620) vs corregido (~570) ----------
    d_known = min_euclidean(X_known, C)

    d_unknown_official = min_euclidean(X_unknown_full, C)
    d_unknown_clean = min_euclidean(X_unknown_clean, C)

    y_official = np.concatenate([np.ones(len(X_known)), np.zeros(len(X_unknown_full))]).astype(int)
    score_official = -np.concatenate([d_known, d_unknown_official])

    y_clean = np.concatenate([np.ones(len(X_known)), np.zeros(len(X_unknown_clean))]).astype(int)
    score_clean = -np.concatenate([d_known, d_unknown_clean])

    auroc_official = float(roc_auc_score(y_official, score_official))
    auroc_clean = float(roc_auc_score(y_clean, score_clean))

    OFFICIAL_AUROC_RECORDED = 0.5732919408781961
    assert abs(auroc_official - OFFICIAL_AUROC_RECORDED) < 0.02, "No se reprodujo el baseline oficial"

    # ---------- Groups para bootstrap estratificado por 'individuo' (obs/image id) ----------
    groups_known = np.array([str(x) for x in known_ids])
    groups_unknown_official = np.array([str(x) for x in obs_unknown])
    groups_unknown_clean = np.array([str(x) for x in obs_clean])

    groups_official = np.concatenate([groups_known, groups_unknown_official])
    groups_clean = np.concatenate([groups_known, groups_unknown_clean])

    print("Running bootstrap official (1000 iter, seed=42)...", flush=True)
    bs_official = bootstrap_auroc(y_official, score_official, groups_official, n_iter=1000, seed=42)
    print("bootstrap official done", flush=True)
    print("Running bootstrap clean (1000 iter, seed=42)...", flush=True)
    bs_clean = bootstrap_auroc(y_clean, score_clean, groups_clean, n_iter=1000, seed=42)
    print("bootstrap clean done", flush=True)

    # ---------- FAR/FRR/Balanced Accuracy con el mismo umbral (percentil de score_official) ----------
    # Umbral: usamos el punto operativo estandar de Youden J sobre el ROC oficial, y lo
    # re-aplicamos IDENTICO (mismo valor numerico de score) al set corregido, para comparar
    # bajo el mismo protocolo de decision.
    from sklearn.metrics import roc_curve
    fpr_o, tpr_o, thr_o = roc_curve(y_official, score_official)
    j_scores = tpr_o - fpr_o
    best_idx = int(np.argmax(j_scores))
    best_threshold = float(thr_o[best_idx])

    far_o, frr_o, bacc_o = far_frr_balanced_acc(y_official, score_official, best_threshold)
    far_c, frr_c, bacc_c = far_frr_balanced_acc(y_clean, score_clean, best_threshold)

    # ---------- Conteo de datos limpios restantes para Dendropsophus_labialis ----------
    labialis_clean_mask = is_labialis & keep_mask
    labialis_clean_imgs = int(labialis_clean_mask.sum())
    labialis_clean_obs = len(set(obs_unknown[labialis_clean_mask].tolist()))

    metrics = {
        "method": "euclidean_raw (identico a phase_reproduce_23a.py): min distancia a 41 centroides "
                  "de especie (Group A=9 desde reference_embeddings.npz, Group B=32 desde "
                  "train_embeddings.npz); KNOWN pool = fase16_clean_open_set/clean_known_embeddings.npz "
                  "sin cambios; UNKNOWN pool oficial vs corregido (excluyendo 34 observation_id "
                  "contaminados de Dendropsophus_labialis/Dendropsophus_molitor).",
        "official": {
            "n_known": int(len(X_known)),
            "n_unknown": int(len(X_unknown_full)),
            "auroc": auroc_official,
            "bootstrap_1000iter_seed42": bs_official,
            "threshold_youden_j": best_threshold,
            "far": far_o,
            "frr": frr_o,
            "balanced_accuracy": bacc_o,
        },
        "corrected_v2_delabeling_fixed": {
            "n_known": int(len(X_known)),
            "n_unknown": int(len(X_unknown_clean)),
            "n_excluded_contaminated_images": n_excluded,
            "auroc": auroc_clean,
            "bootstrap_1000iter_seed42": bs_clean,
            "threshold_used_youden_j_from_official": best_threshold,
            "far": far_c,
            "frr": frr_c,
            "balanced_accuracy": bacc_c,
        },
        "delta": {
            "auroc_diff": auroc_clean - auroc_official,
            "ci95_overlap": not (bs_clean["ci95_lo"] > bs_official["ci95_hi"] or bs_official["ci95_lo"] > bs_clean["ci95_hi"]),
        },
        "dendropsophus_labialis_clean_remaining": {
            "images": labialis_clean_imgs,
            "unique_observations": labialis_clean_obs,
        },
    }

    with open(OUT / "rebaseline_metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)

    with open(OUT / "dendropsophus_labialis_clean_count.json", "w", encoding="utf-8") as f:
        json.dump({
            "clean_images_remaining": labialis_clean_imgs,
            "clean_unique_observations_remaining": labialis_clean_obs,
            "original_images": int(is_labialis.sum()),
            "original_unique_observations": len(set(obs_unknown[is_labialis].tolist())),
            "excluded_images_contaminated": n_excluded,
            "excluded_unique_observations_contaminated": len(set(obs_unknown[is_labialis & ~keep_mask].tolist())),
            "sufficiency_assessment": (
                "INSUFICIENTE para uso individual robusto como especie UNKNOWN aislada: "
                f"quedan solo {labialis_clean_obs} observaciones limpias ({labialis_clean_imgs} imagenes), "
                "por debajo del umbral practico minimo (~10 observaciones / ~15 imagenes) para "
                "estimar FAR/FRR especifico de especie con margen estadistico razonable."
                if labialis_clean_obs < 10 or labialis_clean_imgs < 15 else
                "Suficiente para uso como especie UNKNOWN individual."
            ),
        }, f, indent=2, ensure_ascii=False)

    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
