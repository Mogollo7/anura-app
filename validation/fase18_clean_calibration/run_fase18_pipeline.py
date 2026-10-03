"""
run_fase18_pipeline.py — FASE 18: calibracion sobre CALIBRATION_18 (Euclidean vs Cosine,
SIN mirar BLIND_F18), seleccion de candidato, freeze, y ejecucion del blind test.
"""
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from sklearn.metrics import roc_auc_score, precision_score, recall_score, f1_score, balanced_accuracy_score

ROOT = Path(r"D:\Anura")
sys.path.insert(0, str(ROOT / "tools" / "catalog"))
from taxonomic_resolution import SpeciesResolver

OUT = ROOT / "validation" / "fase18_clean_calibration"
DATA_CLEANED = ROOT / "data cleaned"


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def compute_centroids(X, y):
    return {c: np.mean(X[y == c], axis=0) for c in np.unique(y)}


def score_euclidean(X, centroids):
    classes = list(centroids.keys())
    C = np.array([centroids[c] for c in classes])
    d = np.linalg.norm(X[:, None, :] - C[None, :, :], axis=2)
    idx = np.argmin(d, axis=1)
    return -d[np.arange(len(X)), idx], d[np.arange(len(X)), idx], [classes[i] for i in idx]


def score_cosine(X, centroids):
    classes = list(centroids.keys())
    C = np.array([centroids[c] for c in classes])
    C_norm = C / np.linalg.norm(C, axis=1, keepdims=True)
    sims = X @ C_norm.T
    idx = np.argmax(sims, axis=1)
    return sims[np.arange(len(X)), idx], 1 - sims[np.arange(len(X)), idx], [classes[i] for i in idx]


def wilson_ci(k, n, z=1.96):
    if n == 0:
        return (None, None)
    p = k / n
    denom = 1 + z**2 / n
    center = (p + z**2 / (2 * n)) / denom
    margin = (z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))) / denom
    return (max(0.0, center - margin), min(1.0, center + margin))


def main():
    resolver = SpeciesResolver(ROOT / "training/taxonomia.py", ROOT / "taxonomy/species/species_registry.json")

    # ── Centroides: REFERENCE (Group A) + TRAIN (Group B), identicos a Fase 13/16/17, no BLIND ──
    ref = np.load(ROOT / "evaluation/fase13/embeddings/reference_embeddings.npz")
    train = np.load(ROOT / "evaluation/fase13/embeddings/train_embeddings.npz")
    ref_canon = np.array([resolver.resolve(n)["canonical_name"] for n in ref["species"]])
    train_canon = np.array([resolver.resolve(n)["canonical_name"] for n in train["species"]])
    ref_centroids = compute_centroids(ref["embeddings"], ref_canon)
    train_centroids = compute_centroids(train["embeddings"], train_canon)

    with open(ROOT / "visual_catalog/v1.0.0/manifest.json", encoding="utf-8") as f:
        catalog = json.load(f)
    release_ids = set(catalog["species_ids"])

    all_centroids, id_to_name, centroid_source = {}, {}, {}
    for name, c in ref_centroids.items():
        sid = resolver.resolve(name.replace("_", " "))["species_id"]
        if sid in release_ids:
            all_centroids[sid] = c
            id_to_name[sid] = name
            centroid_source[sid] = {"source": "REFERENCE", "images": int((ref_canon == name).sum())}
    for name, c in train_centroids.items():
        sid = resolver.resolve(name.replace("_", " "))["species_id"]
        if sid in release_ids and sid not in all_centroids:
            all_centroids[sid] = c
            id_to_name[sid] = name
            centroid_source[sid] = {"source": "TRAIN", "images": int((train_canon == name).sum())}

    with open(OUT / "centroid_documentation.json", "w", encoding="utf-8") as f:
        json.dump({
            "species_count": len(all_centroids),
            "per_species": {id_to_name[sid]: {**info, "species_id": sid} for sid, info in centroid_source.items()}
        }, f, indent=2, ensure_ascii=False)
    print(f"Centroides: {len(all_centroids)} (Group A REFERENCE + Group B TRAIN, sin tocar BLIND)")

    # ── Cargar CALIBRATION_18 y BLIND_F18 manifests ──
    with open(OUT / "calibration_manifest.json", encoding="utf-8") as f:
        cal_manifest = json.load(f)
    with open(OUT / "blind_manifest.json", encoding="utf-8") as f:
        blind_manifest = json.load(f)

    # Necesitamos embeddings. KNOWN ya extraidos en Fase 16 (clean_known_embeddings.npz).
    # UNKNOWN ya extraido en F4 (knn_embeddings.npz). Reutilizamos por image_id, NO reextraemos
    # (mismo encoder congelado, mismo resultado).
    clean_emb_data = np.load(ROOT / "validation/fase16_clean_open_set/clean_known_embeddings.npz")
    clean_embeddings_arr = clean_emb_data["embeddings"]  # cargar UNA vez, no dentro de un loop
    clean_image_ids_arr = clean_emb_data["image_ids"]
    image_id_to_idx = {iid: i for i, iid in enumerate(clean_image_ids_arr)}

    f4_emb_all = np.load(ROOT / "evaluation/open_set_v1/knn/knn_embeddings.npz")["embeddings"].astype(np.float32)
    with open(ROOT / "evaluation/open_set_v1/knn/knn_open_set_results.json", encoding="utf-8") as f:
        f3f4_records = json.load(f)["records"]
    path_to_idx = {r["path"]: i for i, r in enumerate(f3f4_records)}

    def get_known_embeddings(records):
        return np.array([clean_embeddings_arr[image_id_to_idx[r["image_id"]]] for r in records])

    def get_unknown_embeddings(records):
        return np.array([f4_emb_all[path_to_idx[r["path"]]] for r in records])

    X_cal_known = get_known_embeddings(cal_manifest["known"])
    X_cal_unknown = get_unknown_embeddings(cal_manifest["unknown"])
    X_blind_known = get_known_embeddings(blind_manifest["known"])
    X_blind_unknown = get_unknown_embeddings(blind_manifest["unknown"])

    print(f"CALIBRATION_18: KNOWN={len(X_cal_known)}, UNKNOWN={len(X_cal_unknown)}")
    print(f"BLIND_F18:      KNOWN={len(X_blind_known)}, UNKNOWN={len(X_blind_unknown)}")

    # ══════════════════════════════════════════════════════════════
    # CALIBRACION (secciones 5-8): SOLO sobre CALIBRATION_18
    # ══════════════════════════════════════════════════════════════
    print("\n=== CALIBRACION (sin mirar BLIND_F18) ===")

    calibration_results = {}
    for method_name, score_fn in [("EUCLIDEAN", score_euclidean), ("COSINE", score_cosine)]:
        s_known, d_known, _ = score_fn(X_cal_known, all_centroids)
        s_unknown, d_unknown, _ = score_fn(X_cal_unknown, all_centroids)

        # Regla de seleccion de threshold: DEFINIDA ANTES de mirar blind.
        # Igual que Fase 13 (target operating point KAR=95% sobre KNOWN de calibracion),
        # usando la metrica NATIVA del metodo (distancia para Euclidean, similitud para Cosine).
        if method_name == "EUCLIDEAN":
            tau = float(np.percentile(d_known, 95))  # 95% de KNOWN debe quedar <= tau (distancia)
            decision_known = d_known <= tau
            decision_unknown = d_unknown <= tau
        else:  # COSINE: score alto = mas KNOWN, se acepta si similarity >= umbral
            tau = float(np.percentile(s_known, 5))  # 95% de KNOWN queda >= tau
            decision_known = s_known >= tau
            decision_unknown = s_unknown >= tau

        kar = float(np.mean(decision_known))
        frr = float(1 - kar)
        far = float(np.mean(decision_unknown))
        udr_cal = float(1 - far)

        y_true = np.concatenate([np.zeros(len(X_cal_known)), np.ones(len(X_cal_unknown))])
        y_score = np.concatenate([-s_known if method_name == "COSINE" else d_known,
                                   -s_unknown if method_name == "COSINE" else d_unknown])
        auroc = float(roc_auc_score(y_true, y_score))

        y_pred_unknown = np.concatenate([(~decision_known).astype(int), (~decision_unknown).astype(int)])
        precision = float(precision_score(y_true, y_pred_unknown, zero_division=0))
        recall = float(recall_score(y_true, y_pred_unknown, zero_division=0))
        f1 = float(f1_score(y_true, y_pred_unknown, zero_division=0))
        bal_acc = float(balanced_accuracy_score(y_true, y_pred_unknown))

        calibration_results[method_name] = {
            "threshold": tau, "selection_rule": "95th percentile of CALIBRATION KNOWN native metric "
                                                  "(distance for Euclidean, similarity for Cosine), "
                                                  "defined BEFORE observing BLIND_F18",
            "calibration_n": len(X_cal_known) + len(X_cal_unknown),
            "known_n": len(X_cal_known), "unknown_n": len(X_cal_unknown),
            "KAR_calibration": kar, "FRR_calibration": frr,
            "FAR_calibration": far, "UDR_calibration": udr_cal,
            "balanced_accuracy_calibration": bal_acc,
            "precision_calibration": precision, "recall_calibration": recall, "f1_calibration": f1,
            "AUROC_calibration_diagnostic_only": auroc,
        }
        print(f"\n[{method_name}] threshold={tau:.4f}")
        print(f"  KAR_cal={kar:.4f} FAR_cal={far:.4f} bal_acc={bal_acc:.4f} AUROC(diag)={auroc:.4f}")

    with open(OUT / "calibration_results.json", "w", encoding="utf-8") as f:
        json.dump(calibration_results, f, indent=2, ensure_ascii=False)

    # ══════════════════════════════════════════════════════════════
    # SELECCION DE CANDIDATO (seccion 9) — ANTES de blind
    # ══════════════════════════════════════════════════════════════
    print("\n=== SELECCION DE CANDIDATO ===")
    eucl = calibration_results["EUCLIDEAN"]
    cos = calibration_results["COSINE"]

    # Criterio: balanced accuracy en calibracion (no solo AUROC), luego simplicidad movil como desempate
    if abs(eucl["balanced_accuracy_calibration"] - cos["balanced_accuracy_calibration"]) < 0.02:
        selected = "EUCLIDEAN"  # mas simple (no requiere normalizar centroides en runtime si embeddings ya normalizados)
        selection_reason = ("balanced_accuracy similar entre ambos metodos (diferencia <0.02); "
                             "se elige Euclidean por ligera ventaja de simplicidad de implementacion "
                             "(no requiere normalizar centroides en cada consulta, aunque el costo "
                             "computacional es practicamente identico a Cosine)")
    elif eucl["balanced_accuracy_calibration"] > cos["balanced_accuracy_calibration"]:
        selected = "EUCLIDEAN"
        selection_reason = "mayor balanced_accuracy en calibracion"
    else:
        selected = "COSINE"
        selection_reason = "mayor balanced_accuracy en calibracion"

    print(f"Candidato seleccionado: {selected}")
    print(f"Razon: {selection_reason}")

    method_selection = {
        "selected_candidate": selected,
        "selection_reason": selection_reason,
        "selection_based_on": "CALIBRATION_18 only, BLIND_F18 not observed at this point",
        "comparison": {
            "EUCLIDEAN_balanced_accuracy": eucl["balanced_accuracy_calibration"],
            "COSINE_balanced_accuracy": cos["balanced_accuracy_calibration"],
        }
    }
    with open(OUT / "method_selection.json", "w", encoding="utf-8") as f:
        json.dump(method_selection, f, indent=2, ensure_ascii=False)

    selected_tau = calibration_results[selected]["threshold"]
    score_fn = score_euclidean if selected == "EUCLIDEAN" else score_cosine

    # ══════════════════════════════════════════════════════════════
    # FREEZE (seccion 10)
    # ══════════════════════════════════════════════════════════════
    print("\n=== FREEZE ===")
    freeze = {
        "phase": "18_freeze",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "selected_method": selected,
        "selected_threshold": selected_tau,
        "encoder_sha256": "219e860e6fa9a80fb30a59fc8f61911421bbd53a4537dca831803d3ab446b2ad",
        "catalog_release": "visual_catalog_1.0.0",
        "centroid_count": len(all_centroids),
        "hashes": {
            "reference_embeddings": sha256_file(ROOT / "evaluation/fase13/embeddings/reference_embeddings.npz"),
            "train_embeddings": sha256_file(ROOT / "evaluation/fase13/embeddings/train_embeddings.npz"),
            "calibration_manifest": sha256_file(OUT / "calibration_manifest.json"),
            "blind_manifest": sha256_file(OUT / "blind_manifest.json"),
            "calibration_results": sha256_file(OUT / "calibration_results.json"),
            "method_selection": sha256_file(OUT / "method_selection.json"),
        },
        "note": "A partir de este punto, threshold/centroides/calibration/metodo NO deben modificarse. "
                "El blind test se ejecuta DESPUES de este freeze."
    }
    with open(OUT / "fase18_freeze_manifest.json", "w", encoding="utf-8") as f:
        json.dump(freeze, f, indent=2, ensure_ascii=False)
    print(f"Freeze: method={selected}, threshold={selected_tau:.4f}")

    # ══════════════════════════════════════════════════════════════
    # BLIND TEST (secciones 11-14)
    # ══════════════════════════════════════════════════════════════
    print("\n=== BLIND TEST (BLIND_F18) ===")

    s_blind_known, d_blind_known, nearest_known = score_fn(X_blind_known, all_centroids)
    s_blind_unknown, d_blind_unknown, nearest_unknown = score_fn(X_blind_unknown, all_centroids)

    if selected == "EUCLIDEAN":
        accept_known = d_blind_known <= selected_tau
        accept_unknown = d_blind_unknown <= selected_tau
        metric_known, metric_unknown = d_blind_known, d_blind_unknown
    else:
        accept_known = s_blind_known >= selected_tau
        accept_unknown = s_blind_unknown >= selected_tau
        metric_known, metric_unknown = s_blind_known, s_blind_unknown

    known_accepted = int(accept_known.sum())
    known_rejected = int((~accept_known).sum())
    unknown_rejected = int((~accept_unknown).sum())
    unknown_false_accepted = int(accept_unknown.sum())

    kar = known_accepted / len(X_blind_known)
    frr = known_rejected / len(X_blind_known)
    far = unknown_false_accepted / len(X_blind_unknown) if len(X_blind_unknown) else None
    udr = unknown_rejected / len(X_blind_unknown) if len(X_blind_unknown) else None

    y_true = np.concatenate([np.zeros(len(X_blind_known)), np.ones(len(X_blind_unknown))])
    y_score_auroc = np.concatenate([
        d_blind_known if selected == "EUCLIDEAN" else -s_blind_known,
        d_blind_unknown if selected == "EUCLIDEAN" else -s_blind_unknown
    ])
    auroc = float(roc_auc_score(y_true, y_score_auroc))
    y_pred_unknown = np.concatenate([(~accept_known).astype(int), (~accept_unknown).astype(int)])
    precision = float(precision_score(y_true, y_pred_unknown, zero_division=0))
    recall = float(recall_score(y_true, y_pred_unknown, zero_division=0))
    f1 = float(f1_score(y_true, y_pred_unknown, zero_division=0))
    bal_acc = float(balanced_accuracy_score(y_true, y_pred_unknown))

    far_ci = wilson_ci(unknown_false_accepted, len(X_blind_unknown))
    kar_ci = wilson_ci(known_accepted, len(X_blind_known))

    blind_results = {
        "phase": "18_blind_test",
        "method": selected, "threshold": selected_tau,
        "n_known": len(X_blind_known), "n_unknown": len(X_blind_unknown),
        "n_known_individuals": blind_manifest["n_known_individuals"],
        "n_unknown_individuals": blind_manifest["n_unknown_individuals"],
        "n_known_species": blind_manifest["n_known_species"],
        "n_unknown_species": blind_manifest["n_unknown_species"],
        "classification_counts": {
            "KNOWN_ACCEPTED": known_accepted, "KNOWN_REJECTED": known_rejected,
            "UNKNOWN_REJECTED": unknown_rejected, "UNKNOWN_FALSE_ACCEPTED": unknown_false_accepted,
        },
        "metrics": {
            "KAR": kar, "KAR_95CI": kar_ci, "FRR": frr,
            "FAR": far, "FAR_95CI": far_ci, "UDR": udr,
            "precision_unknown": precision, "recall_unknown": recall, "f1_unknown": f1,
            "balanced_accuracy": bal_acc, "AUROC": auroc,
        }
    }
    with open(OUT / "blind_results.json", "w", encoding="utf-8") as f:
        json.dump(blind_results, f, indent=2, ensure_ascii=False)

    print(f"\nMetodo: {selected}, threshold={selected_tau:.4f}")
    print(f"KAR={kar:.4f} (95%CI {kar_ci}) FRR={frr:.4f}")
    print(f"FAR={far:.4f} (95%CI {far_ci}) UDR={udr:.4f}")
    print(f"AUROC={auroc:.4f} balanced_accuracy={bal_acc:.4f} F1={f1:.4f}")

    # ══════════════════════════════════════════════════════════════
    # ANALISIS POR ESPECIE (seccion 14)
    # ══════════════════════════════════════════════════════════════
    print("\n=== ANALISIS POR ESPECIE ===")
    species_level = {"unknown": {}, "known": {}}

    for sp in set(r["true_species"] for r in blind_manifest["unknown"]):
        idxs = [i for i, r in enumerate(blind_manifest["unknown"]) if r["true_species"] == sp]
        mask = np.array([i in idxs for i in range(len(blind_manifest["unknown"]))])
        n = int(mask.sum())
        fa = int(accept_unknown[mask].sum())
        nearest_counts = {}
        for i in np.where(mask)[0]:
            n_name = id_to_name.get(nearest_unknown[i], nearest_unknown[i])
            nearest_counts[n_name] = nearest_counts.get(n_name, 0) + 1
        species_level["unknown"][sp] = {
            "n_images": n, "false_accepts": fa, "FAR": fa / n if n else None,
            "nearest_known_species_counts": nearest_counts,
            "metric_mean": float(metric_unknown[mask].mean()) if n else None,
        }
        print(f"  UNKNOWN {sp}: n={n}, false_accepts={fa}, FAR={fa/n if n else None}")

    known_species_ids_blind = [r["species_id"] for r in blind_manifest["known"]]
    for sid in set(known_species_ids_blind):
        mask = np.array([s == sid for s in known_species_ids_blind])
        n = int(mask.sum())
        acc = int(accept_known[mask].sum())
        rej = n - acc
        name = id_to_name.get(sid, sid)
        species_level["known"][name] = {
            "species_id": sid, "n_images": n, "accepts": acc, "rejects": rej,
            "FRR": rej / n if n else None,
        }

    with open(OUT / "species_level_results.json", "w", encoding="utf-8") as f:
        json.dump(species_level, f, indent=2, ensure_ascii=False)

    # ══════════════════════════════════════════════════════════════
    # COMPARACION (seccion 15)
    # ══════════════════════════════════════════════════════════════
    with open(ROOT / "evaluation/fase13/final_evaluation/FASE13_FINAL_METRICS.json", encoding="utf-8") as f:
        f13 = json.load(f)
    with open(ROOT / "validation/fase16_clean_open_set/fase16_blind_test_results.json", encoding="utf-8") as f:
        f16 = json.load(f)
    with open(ROOT / "validation/fase17_open_set_methods/fase17_conclusion.json", encoding="utf-8") as f:
        f17 = json.load(f)

    comparison = {
        "fase13_mahalanobis_CONTAMINATED": {
            "AUROC": f13["auroc_out_of_sample"], "KAR": f13["kar_known_total"], "FAR": f13["far_unknown_total"],
            "status": "COMPROMISED_BY_LEAKAGE (F3 KNOWN subset of TRAIN)"
        },
        "fase16_mahalanobis_CLEAN_diagnostic": {
            "AUROC": f16["metrics"]["auroc"], "KAR": f16["metrics"]["known_acceptance_rate_KAR"],
            "FAR": f16["metrics"]["unknown_false_acceptance_rate_FAR"],
            "status": "CLEAN but full pool used as diagnostic blind"
        },
        "fase17_diagnostic_method_selection_blind": {
            "cosine_AUROC": f17["cosine_auroc"], "euclidean_AUROC": f17["euclidean_auroc"],
            "mahalanobis_AUROC": f17["mahalanobis_auroc"],
            "status": "METHOD_SELECTION_BLIND -- not reused for threshold selection here"
        },
        "fase18_selected_candidate_INDEPENDENT_BLIND": {
            "method": selected, "threshold": selected_tau,
            "AUROC": auroc, "KAR": kar, "FAR": far, "balanced_accuracy": bal_acc,
            "status": "Calibrated on CALIBRATION_18, evaluated on disjoint BLIND_F18. "
                      "NOTE: BLIND_F18 KNOWN pool overlaps with Fase16/17 diagnostic exposure "
                      "(see leakage_audit.json) -- not a fully virgin blind."
        },
        "never_mixed": "Estos 4 resultados se reportan por separado, nunca promediados ni combinados."
    }
    with open(OUT / "fase18_comparison.json", "w", encoding="utf-8") as f:
        json.dump(comparison, f, indent=2, ensure_ascii=False)

    print("\n[OK] Todos los artefactos de Fase 18 generados.")


if __name__ == "__main__":
    main()
