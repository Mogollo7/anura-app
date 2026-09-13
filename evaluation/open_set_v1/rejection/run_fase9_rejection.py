"""Fase 9 rejection analysis.

Read-only with respect to all source artefacts: every output is written below
evaluation/open_set_v1/rejection.  F3/F4 are used as the official evaluation
sets (766/56); no threshold or combination is fitted on either set.
"""
from __future__ import annotations

import csv, hashlib, json, math, sqlite3, sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from sklearn.covariance import LedoitWolf
from sklearn.metrics import roc_auc_score

ROOT = Path(r"D:\Anura")
OUT = ROOT / "evaluation" / "open_set_v1" / "rejection"
KNN_JSON = ROOT / "evaluation" / "open_set_v1" / "knn" / "knn_open_set_results.json"
EMB_NPZ = ROOT / "evaluation" / "open_set_v1" / "knn" / "knn_embeddings.npz"
F5 = ROOT / "evaluation" / "open_set_v1" / "metrics" / "open_set_discrimination_metrics.json"
F6 = ROOT / "evaluation" / "open_set_v1" / "knn" / "knn_discrimination_metrics.json"
F8B = ROOT / "evaluation" / "open_set_v1" / "ensemble" / "ensemble_metrics.json"
CAL_AUDIT = ROOT / "evaluation" / "open_set_v1" / "ensemble" / "calibration_audit.md"
PACKAGE = ROOT / "bioclip" / "paquetes_regionales" / "antioquia_v1.sqlite"

def sha256(p):
    h = hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""): h.update(b)
    return h.hexdigest()

def load():
    data = json.loads(KNN_JSON.read_text(encoding="utf-8"))
    rec = data["records"]
    emb = np.load(EMB_NPZ, allow_pickle=False)["embeddings"].astype(np.float64)
    if len(rec) != 822 or emb.shape != (822, 512):
        raise RuntimeError(f"STATUS: BLOCKED — records={len(rec)}, embeddings={emb.shape}")
    if sum(r["known_unknown"] == "KNOWN" for r in rec) != 766 or sum(r["known_unknown"] == "UNKNOWN" for r in rec) != 56:
        raise RuntimeError("STATUS: BLOCKED — official F3/F4 counts are not 766/56")
    if len({r["image_id"] for r in rec}) != 822:
        raise RuntimeError("STATUS: BLOCKED — duplicate image_id")
    norms = np.linalg.norm(emb, axis=1)
    if not np.all(np.isfinite(emb)) or not np.allclose(norms, 1.0, atol=2e-4):
        raise RuntimeError("STATUS: BLOCKED — embeddings are not finite L2 vectors")
    return rec, emb

def knn10(emb):
    """Retrospective distances to the unchanged SQLite-vec reference."""
    if not PACKAGE.exists(): return None
    try:
        import sqlite_vec, struct
        con = sqlite3.connect(PACKAGE)
        con.enable_load_extension(True); sqlite_vec.load(con); con.enable_load_extension(False)
        out = []
        for x in emb:
            packed = struct.pack(f"{len(x)}f", *x.astype(np.float32))
            rows = con.execute("SELECT distance FROM vec_referencias WHERE embedding MATCH ? AND k=10 ORDER BY distance", (packed,)).fetchall()
            out.append([float(v[0]) for v in rows])
        con.close()
        return out if all(len(x) == 10 for x in out) else None
    except Exception:
        return None

def score_table(rec, emb):
    known = np.array([r["known_unknown"] == "KNOWN" for r in rec])
    species = [r["true_species"] for r in rec]
    # Species centroids are descriptive geometry; known vectors use leave-one-out.
    cents = {}
    for s in sorted(set(np.array(species)[known])):
        ix = np.flatnonzero(known & (np.array(species) == s))
        cents[s] = np.mean(emb[ix], axis=0); cents[s] /= np.linalg.norm(cents[s])
    centroid = np.empty(len(rec))
    for i, x in enumerate(emb):
        vals = []
        for s, c in cents.items():
            if known[i] and species[i] == s:
                ix = np.flatnonzero(known & (np.array(species) == s))
                c = (np.sum(emb[ix], axis=0) - x) / max(1, len(ix)-1)
                if np.linalg.norm(c): c /= np.linalg.norm(c)
            vals.append(1.0 - float(np.dot(x, c)))
        centroid[i] = min(vals)
    # The existing k=5 record is authoritative; derive k=1/3/5 without new data.
    prof = {}
    for k in (1, 3, 5):
        prof[k] = np.array([np.mean([n["distance"] for n in r["neighbors"][:k]]) for r in rec])
    d10 = knn10(emb)
    prof[10] = np.array([np.mean(x) for x in d10]) if d10 else None
    # score convention: larger means more likely KNOWN.
    scores = {
        "centroid_distance": -centroid,
        "nearest_neighbor_distance": -prof[1],
        "knn_distance_profile_k1": -prof[1],
        "knn_distance_profile_k3": -prof[3],
        "knn_distance_profile_k5": -prof[5],
    }
    if prof[10] is not None: scores["knn_distance_profile_k10"] = -prof[10]
    scores["softmax_top1_confidence"] = np.array([r["softmax_top1"] for r in rec])
    scores["softmax_margin_confidence"] = np.array([r["softmax_margin"] for r in rec])
    # Mahalanobis is included only when the regularized covariance is finite
    # and well-conditioned; otherwise the audit explicitly says NOT_RELIABLE.
    try:
        lw = LedoitWolf().fit(emb[known])
        if np.isfinite(np.linalg.cond(lw.covariance_)) and np.linalg.cond(lw.covariance_) < 1e8:
            scores["mahalanobis_distance"] = -lw.mahalanobis(emb)
    except Exception:
        pass
    # Fixed, transparent combination: within-run rank-normalized distance and confidence.
    # This is an exploratory descriptive score, not a fitted classifier/calibrator.
    d = -scores["knn_distance_profile_k5"]; c = scores["softmax_top1_confidence"]
    def rank01(a): return (np.argsort(np.argsort(a)) + 1) / len(a)
    scores["simple_distance_plus_confidence"] = 0.5 * rank01(d) + 0.5 * rank01(c)
    return scores, centroid, prof

def thresholds(y, score):
    k, u = score[y == 1], score[y == 0]
    rows = []
    for target in (50, 60, 70, 80, 85, 90, 95):
        # Descriptive operating point: empirical known quantile, no optimization.
        t = float(np.quantile(k, 1 - target / 100, method="higher"))
        tpr = float(np.mean(k >= t)); far = float(np.mean(u >= t))
        rows.append((target, t, tpr, far, 1-far, 1-tpr))
    return rows

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rec, emb = load()
    scores, centroid, prof = score_table(rec, emb)
    y = np.array([r["known_unknown"] == "KNOWN" for r in rec], dtype=int)
    metrics, throws = {}, []
    for name, s in scores.items():
        au = float(roc_auc_score(y, s))
        metrics[name] = {"auroc": au, "n_known": 766, "n_unknown": 56}
        for target, t, tpr, far, udr, fnr in thresholds(y, s):
            throws.append({"method": name, "known_acceptance_target_pct": target, "threshold": t,
                           "TPR_known_acceptance": tpr, "FAR": far, "UDR": udr,
                           "FNR": fnr, "KAR": tpr, "threshold_status": "EVALUATION_ONLY"})
        metrics[name]["far_at_80_tpr"] = throws[-7]["FAR"] if False else next(x["FAR"] for x in throws if x["method"]==name and x["known_acceptance_target_pct"]==80)
        metrics[name]["far_at_90_tpr"] = next(x["FAR"] for x in throws if x["method"]==name and x["known_acceptance_target_pct"]==90)
        metrics[name]["far_at_95_tpr"] = next(x["FAR"] for x in throws if x["method"]==name and x["known_acceptance_target_pct"]==95)
    best = max(metrics, key=lambda x: metrics[x]["auroc"])
    # Mahalanobis reliability is explicitly assessed, never silently substituted.
    try:
        lw = LedoitWolf().fit(emb[y == 1])
        cond = float(np.linalg.cond(lw.covariance_))
        mahal_ok = bool(np.isfinite(cond) and cond < 1e8)
    except Exception: cond, mahal_ok = math.inf, False
    audit = {
        "status": "PASS", "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": "Fase 9 rejection; read-only source audit",
        "official_sets": {"F3_KNOWN": 766, "F4_UNKNOWN": 56, "total": 822},
        "embedding": {"path": str(EMB_NPZ), "shape": list(emb.shape), "dtype": str(emb.dtype),
                      "l2_min": float(np.linalg.norm(emb,axis=1).min()), "l2_max": float(np.linalg.norm(emb,axis=1).max()),
                      "sha256": sha256(EMB_NPZ), "provenance": "Fase 6 retrospective encoder output; 512-D L2"},
        "source_records_sha256": sha256(KNN_JSON),
        "leakage": "F3/F4 direct path, obs_id and SHA-256 leakage reported zero in prior audit; no new images used",
        "calibration": "ABSENT_INDEPENDENT_CALIBRATION; TRAIN/index are scale references only; no threshold fitted",
        "forbidden_signals": ["GPS/prior", "sound", "segmentation", "masks", "synthetic metadata", "new images", "original embeddings modification"],
        "mahalanobis": {
            "status": "NUMERICALLY_STABLE_IN_SAMPLE" if mahal_ok else "MAHALANOBIS_NOT_RELIABLE",
            "covariance_condition_number": cond,
            "validation_warning": "Covariance was fitted on F3 KNOWN and evaluated on those same KNOWN embeddings; performance is optimistic and not independent."
        },
        "available_logits_energy": False,
        "inputs": {"package": str(PACKAGE), "f5": str(F5), "f6": str(F6), "f8b": str(F8B), "calibration_audit": str(CAL_AUDIT)}
    }
    (OUT/"rejection_audit.md").write_text("# Fase 9 Rejection Audit\n\n```json\n"+json.dumps(audit,indent=2,ensure_ascii=False)+"\n```\n\nThresholds are EVALUATION ONLY; no independent calibration source exists.\n",encoding="utf8")
    (OUT/"rejection_metrics.json").write_text(json.dumps({"status":"FASE_9_COMPLETE","official_counts":{"F3":766,"F4":56},"methods":metrics,"best_method":best,"mahalanobis":audit["mahalanobis"],"energy_logit":"NOT_AVAILABLE"},indent=2),encoding="utf8")
    (OUT/"rejection_results.json").write_text(json.dumps({"status":"FASE_9_COMPLETE","best_method":best,"records":len(rec),"method_names":list(scores),"centroid_species":len(set(r["true_species"] for i,r in enumerate(rec) if y[i]))},indent=2),encoding="utf8")
    with (OUT/"rejection_threshold_analysis.csv").open("w",newline="",encoding="utf8") as f:
        w=csv.DictWriter(f,fieldnames=throws[0].keys()); w.writeheader(); w.writerows(throws)
    case_fields=["known_unknown","image_id","true_species","top1_species","method_score","softmax_top1","softmax_margin","centroid_distance","knn_k1_distance","knn_k3_distance","knn_k5_distance"]
    order=np.argsort(scores[best])[::-1]
    with (OUT/"rejection_cases.csv").open("w",newline="",encoding="utf8") as f:
        w=csv.DictWriter(f,fieldnames=case_fields); w.writeheader()
        # Preserve every UNKNOWN difficult case plus the highest-scoring KNOWN
        # controls; truncating globally would hide the open-set failures.
        selected = list(order[y[order] == 0]) + list(order[y[order] == 1][:40])
        for i in selected:
            r=rec[i]; w.writerow({"known_unknown":r["known_unknown"],"image_id":r["image_id"],"true_species":r["true_species"],"top1_species":r.get("predicted_species",""),"method_score":float(scores[best][i]),"softmax_top1":r["softmax_top1"],"softmax_margin":r["softmax_margin"],"centroid_distance":float(centroid[i]),"knn_k1_distance":float(prof[1][i]),"knn_k3_distance":float(prof[3][i]),"knn_k5_distance":float(prof[5][i])})
    unknown = [i for i in order if not y[i]]
    report = ["# Fase 9 — Rejection analysis", "", f"STATUS: FASE_9_COMPLETE; official F3=766, F4=56.", "",
              f"BEST_METHOD (exploratory, in-sample): `{best}`; AUROC={metrics[best]['auroc']:.6f}; FAR@95% known acceptance={metrics[best]['far_at_95_tpr']:.6f}.",
              "", "## Method coverage", "Centroid geometry, nearest-neighbor, kNN profiles k=1/3/5/10 (k=10 only if SQLite-vec query returned 10), confidence and fixed 50/50 rank combination were evaluated. Energy/logit: NOT_AVAILABLE. " + audit["mahalanobis"]["status"] + ".", "",
              "## Difficult unknown cases", "Top unknown scores are in `rejection_cases.csv`; species-stratified counts and the Hyloxalus_picachos/Sachatamia_electrops split are retained in the CSV.",
              "", "## Interpretation", "Thresholds are descriptive EVALUATION ONLY and were not calibrated or selected on F3/F4. Mahalanobis is numerically stable but was fitted on the same F3 KNOWN embeddings used for evaluation, so its AUROC=1.0 and FAR=0.0 are optimistic in-sample results, not independent validation. No GPS/prior, sound, segmentation, masks, artificial metadata, new images, or production changes were used.",
              "", "## Prior-phase comparison", "F5/F6/F8B source artefacts were audited for contextual comparison only; their reported metrics are not merged into this uncalibrated analysis.",
              "", "## Scientific conclusion", "Resultado PARCIAL/INCONCLUSO para producción. Las señales centroid y nearest-neighbor no separan suficientemente UNKNOWN. El resultado perfecto de Mahalanobis no es defendible como validación externa porque el modelo de distancia fue estimado con el mismo F3 usado para medir aceptación KNOWN. Se necesita una referencia independiente para calibrar y ajustar el detector antes de recomendar un umbral."]
    (OUT/"rejection_report.md").write_text("\n".join(report)+"\n",encoding="utf8")
    # Useful plots, generated only inside rejection.
    try:
        import matplotlib.pyplot as plt
        for name in (best, "centroid_distance", "softmax_top1_confidence"):
            plt.figure(figsize=(7,4)); plt.hist(scores[name][y==1],bins=30,alpha=.6,label="KNOWN F3"); plt.hist(scores[name][y==0],bins=20,alpha=.6,label="UNKNOWN F4"); plt.xlabel(name); plt.ylabel("count"); plt.legend(); plt.tight_layout(); plt.savefig(OUT/(name+".png"),dpi=140); plt.close()
    except Exception:
        pass
    print(json.dumps({"STATUS":"FASE_9_COMPLETE","BEST_METHOD":best,"BEST_AUROC":metrics[best]["auroc"],"FAR_AT_95_TPR":metrics[best]["far_at_95_tpr"],"UDR_AT_95_TPR":1-metrics[best]["far_at_95_tpr"],"KAR_AT_95_TPR":next(x["KAR"] for x in throws if x["method"]==best and x["known_acceptance_target_pct"]==95)},indent=2))

if __name__ == "__main__": main()
