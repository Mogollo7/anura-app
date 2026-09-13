"""Fase 5 — análisis retrospectivo de discriminación Open Set.

Lee únicamente los resultados ya producidos por Fase 3 y Fase 4. No ejecuta
inferencia, no modifica el modelo y no aplica ningún threshold al pipeline.
"""

import csv
import hashlib
import json
import math
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from sklearn.metrics import auc, roc_auc_score, roc_curve


ROOT = Path(r"D:\Anura")
F3_RESULTS = ROOT / "evaluation" / "open_set_v1" / "closed_set" / "closed_set_results.json"
F3_METRICS = ROOT / "evaluation" / "open_set_v1" / "closed_set" / "closed_set_metrics.json"
F4_RESULTS = ROOT / "evaluation" / "open_set_v1" / "open_set" / "open_set_results.json"
F4_METRICS = ROOT / "evaluation" / "open_set_v1" / "open_set" / "open_set_metrics.json"
OUTPUT = ROOT / "evaluation" / "open_set_v1" / "metrics"
PLOTS = OUTPUT / "plots"
UNKNOWN_SPECIES = {"Hyloxalus_picachos", "Sachatamia_electrops"}
SCORES = ("top1_probability", "top2_probability", "top3_probability", "margin_top1_top2")


def read_json(path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate(f3, f4, f3_metrics, f4_metrics):
    expected_f3 = 766
    expected_f4 = 56
    if len(f3) != expected_f3 or len(f4) != expected_f4:
        raise RuntimeError(
            f"STATUS: BLOCKED — conteos inesperados: F3={len(f3)}, F4={len(f4)}"
        )
    if len({row["image_id"] for row in f3}) != len(f3):
        raise RuntimeError("STATUS: BLOCKED — IDs duplicados en F3")
    if len({row["image_id"] for row in f4}) != len(f4):
        raise RuntimeError("STATUS: BLOCKED — IDs duplicados en F4")
    if len({row["true_species"] for row in f3}) != 41:
        raise RuntimeError("STATUS: BLOCKED — F3 no contiene 41 especies")
    if set(row["true_species"] for row in f4) != UNKNOWN_SPECIES:
        raise RuntimeError("STATUS: BLOCKED — especies UNKNOWN inesperadas")
    if any(row["leakage_status"] != "CLEAN" for row in f3 + f4):
        raise RuntimeError("STATUS: BLOCKED — se detectó leakage")
    for dataset_name, rows in (("F3", f3), ("F4", f4)):
        for row in rows:
            for score in SCORES:
                value = row.get(score)
                if value is None or not math.isfinite(float(value)):
                    raise RuntimeError(f"STATUS: BLOCKED — {dataset_name} score inválido: {score}")
            if not 0 <= row["top1_probability"] <= 1:
                raise RuntimeError(f"STATUS: BLOCKED — {dataset_name} top1 fuera de rango")
            if not 0 <= row["top3_probability"] <= row["top2_probability"] <= row["top1_probability"] <= 1:
                raise RuntimeError(f"STATUS: BLOCKED — orden/rango de probabilidades inválido en {dataset_name}")
            expected_margin = row["top1_probability"] - row["top2_probability"]
            if not math.isclose(row["margin_top1_top2"], expected_margin, rel_tol=1e-5, abs_tol=1e-6):
                raise RuntimeError(f"STATUS: BLOCKED — margin inconsistente en {dataset_name}")
    for metric_name, metric, expected in (
        ("F3", f3_metrics, 766),
        ("F4", f4_metrics, 56),
    ):
        if metric.get("total_images") != expected:
            raise RuntimeError(f"STATUS: BLOCKED — métrica {metric_name} inconsistente")


def summary(values):
    values = np.asarray(values, dtype=float)
    return {
        "n": int(values.size),
        "mean": float(np.mean(values)),
        "median": float(np.median(values)),
        "std": float(np.std(values, ddof=1)),
        "min": float(np.min(values)),
        "max": float(np.max(values)),
        "p05": float(np.percentile(values, 5)),
        "p25": float(np.percentile(values, 25)),
        "p50": float(np.percentile(values, 50)),
        "p75": float(np.percentile(values, 75)),
        "p95": float(np.percentile(values, 95)),
    }


def threshold_rows(known_scores, unknown_scores):
    rows = []
    for threshold in np.linspace(0, 0.95, 20):
        known_accepted = int(np.sum(known_scores >= threshold))
        unknown_accepted = int(np.sum(unknown_scores >= threshold))
        rows.append({
            "threshold": float(threshold),
            "known_acceptance_rate": known_accepted / len(known_scores),
            "unknown_detection_rate": 1 - unknown_accepted / len(unknown_scores),
            "false_acceptance_rate": unknown_accepted / len(unknown_scores),
            "known_accepted": known_accepted,
            "unknown_accepted": unknown_accepted,
        })
    return rows


def fpr_at_95_tpr(known_scores, unknown_scores):
    y = np.concatenate([np.ones(len(known_scores)), np.zeros(len(unknown_scores))])
    scores = np.concatenate([known_scores, unknown_scores])
    fpr, tpr, thresholds = roc_curve(y, scores)
    eligible = np.flatnonzero(tpr >= 0.95)
    if eligible.size == 0:
        return {"threshold": None, "tpr": None, "fpr": None}
    index = eligible[0]
    threshold = thresholds[index]
    return {
        "threshold": float(threshold),
        "tpr": float(tpr[index]),
        "fpr": float(fpr[index]),
        "known_accepted": int(np.sum(known_scores >= threshold)),
        "unknown_accepted": int(np.sum(unknown_scores >= threshold)),
    }


def oscr(known_scores, known_correct, unknown_scores):
    # Standard confidence-ranked OSCR: CCR=correct known / N_known,
    # FPR=accepted unknown / N_unknown.
    scores = np.concatenate([known_scores, unknown_scores])
    labels = np.concatenate([np.ones(len(known_scores)), np.zeros(len(unknown_scores))])
    correct = np.concatenate([known_correct.astype(int), np.zeros(len(unknown_scores), dtype=int)])
    order = np.argsort(-scores, kind="stable")
    cumulative_correct = np.cumsum(correct[order])
    cumulative_unknown = np.cumsum((labels[order] == 0).astype(int))
    x = np.concatenate([[0.0], cumulative_unknown / len(unknown_scores)])
    y = np.concatenate([[0.0], cumulative_correct / len(known_scores)])
    return {
        "definition": "Standard OSCR: x=FPR of UNKNOWN, y=CCR of KNOWN; confidence-ranked threshold sweep.",
        "score": "top1_probability",
        "known_n": len(known_scores),
        "unknown_n": len(unknown_scores),
        "area_under_curve": float(auc(x, y)),
        "max_correct_classification_rate": float(np.max(y)),
    }


def ece(confidence, correct, bins=10):
    edges = np.linspace(0, 1, bins + 1)
    rows = []
    total_error = 0.0
    for index in range(bins):
        left, right = edges[index], edges[index + 1]
        mask = (confidence >= left) & (
            confidence < right if index < bins - 1 else confidence <= right
        )
        count = int(np.sum(mask))
        if count:
            accuracy = float(np.mean(correct[mask]))
            mean_confidence = float(np.mean(confidence[mask]))
            total_error += count / len(confidence) * abs(accuracy - mean_confidence)
        else:
            accuracy = None
            mean_confidence = None
        rows.append({
            "bin": index,
            "lower": float(left),
            "upper": float(right),
            "n": count,
            "accuracy": accuracy,
            "mean_confidence": mean_confidence,
        })
    return float(total_error), rows


def plot_distributions(known, unknown):
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return False
    PLOTS.mkdir(parents=True, exist_ok=True)
    for score, filename, title in (
        ("top1_probability", "top1_probability_known_vs_unknown.png", "Top-1 probability"),
        ("margin_top1_top2", "margin_known_vs_unknown.png", "Top-1 minus Top-2 margin"),
    ):
        plt.figure(figsize=(8, 5))
        plt.hist(
            [[row[score] for row in known], [row[score] for row in unknown]],
            bins=20,
            label=["KNOWN", "UNKNOWN"],
            alpha=0.7,
        )
        plt.xlabel(score)
        plt.ylabel("Images")
        plt.title(title)
        plt.legend()
        plt.tight_layout()
        plt.savefig(PLOTS / filename, dpi=150)
        plt.close()
    return True


def runtime_metadata(inputs):
    try:
        git_branch = subprocess.check_output(
            ["git", "-C", str(ROOT), "branch", "--show-current"], text=True, stderr=subprocess.DEVNULL
        ).strip()
        git_status = subprocess.check_output(
            ["git", "-C", str(ROOT), "status", "--short"], text=True, stderr=subprocess.DEVNULL
        ).strip()
        git_commit = subprocess.check_output(
            ["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        git_branch = git_status = git_commit = "NOT_A_GIT_REPOSITORY"
    return {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "python": sys.version,
        "platform": platform.platform(),
        "numpy": np.__version__,
        "sklearn": __import__("sklearn").__version__,
        "git_branch": git_branch,
        "git_commit": git_commit,
        "git_status": git_status,
        "input_sha256": {str(path): sha256(path) for path in inputs},
    }


def main():
    f3, f4 = read_json(F3_RESULTS), read_json(F4_RESULTS)
    f3_metrics, f4_metrics = read_json(F3_METRICS), read_json(F4_METRICS)
    validate(f3, f4, f3_metrics, f4_metrics)

    known = f3
    unknown = f4
    known_scores = {score: np.array([row[score] for row in known]) for score in SCORES}
    unknown_scores = {score: np.array([row[score] for row in unknown]) for score in SCORES}
    summaries = {
        score: {
            "KNOWN": summary(known_scores[score]),
            "UNKNOWN": summary(unknown_scores[score]),
            **{
                species: summary([row[score] for row in unknown if row["true_species"] == species])
                for species in sorted(UNKNOWN_SPECIES)
            },
        }
        for score in SCORES
    }

    y = np.concatenate([np.ones(len(known)), np.zeros(len(unknown))])
    auroc = {
        score: float(roc_auc_score(y, np.concatenate([known_scores[score], unknown_scores[score]])))
        for score in SCORES
    }
    primary = known_scores["top1_probability"]
    primary_unknown = unknown_scores["top1_probability"]
    thresholds = threshold_rows(primary, primary_unknown)
    far_targets = {
        "approximately_5_percent": min(
            thresholds, key=lambda row: abs(row["false_acceptance_rate"] - 0.05)
        ),
        "approximately_1_percent": min(
            thresholds, key=lambda row: abs(row["false_acceptance_rate"] - 0.01)
        ),
    }
    fpr95 = fpr_at_95_tpr(primary, primary_unknown)
    known_correct = np.array([bool(row["is_correct_top1"]) for row in known])
    oscr_result = oscr(primary, known_correct, primary_unknown)
    ece_value, ece_bins = ece(primary, known_correct)

    high_confidence = {
        str(level): [
            {
                "image_id": row["image_id"],
                "true_species": row["true_species"],
                "predicted_species": row["top1_species"],
                "top1_probability": row["top1_probability"],
                "top2_probability": row["top2_probability"],
                "top3_probability": row["top3_probability"],
                "margin": row["margin_top1_top2"],
                "path": row.get("path"),
                "classification": "HIGH_CONFIDENCE_OPEN_SET_PREDICTION",
            }
            for row in unknown if row["top1_probability"] >= level
        ]
        for level in (0.90, 0.80, 0.70)
    }
    prediction_counts = {}
    for species in sorted(UNKNOWN_SPECIES):
        prediction_counts[species] = {}
        for row in unknown:
            if row["true_species"] == species:
                prediction_counts[species][row["top1_species"]] = (
                    prediction_counts[species].get(row["top1_species"], 0) + 1
                )
    top_false_accepts = {
        "by_top1_probability": sorted(unknown, key=lambda row: row["top1_probability"], reverse=True)[:10],
        "by_margin": sorted(unknown, key=lambda row: row["margin_top1_top2"], reverse=True)[:10],
        "top1_prediction_counts": {
            species: count
            for species, count in sorted(
                ((row["top1_species"], sum(item["top1_species"] == row["top1_species"] for item in unknown))
                 for row in unknown),
                key=lambda pair: pair[1],
                reverse=True,
            )
        },
    }

    OUTPUT.mkdir(parents=True, exist_ok=True)
    inputs = [F3_RESULTS, F3_METRICS, F4_RESULTS, F4_METRICS]
    metrics = {
        "status": "FASE_5_COMPLETE",
        "known_n": len(known),
        "unknown_n": len(unknown),
        "unknown_species_n": len(UNKNOWN_SPECIES),
        "unknown_species": sorted(UNKNOWN_SPECIES),
        "available_scores": list(SCORES),
        "unavailable_scores": {
            "entropy": "NOT COMPUTABLE: no están disponibles las probabilidades completas de 41 clases",
            "distance": "NOT COMPUTABLE: no hay embedding_distance/cosine_distance",
            "brier_multiclass": "NOT COMPUTABLE: no están disponibles las probabilidades completas de 41 clases",
        },
        "distributions": summaries,
        "auroc_known_positive": auroc,
        "fpr_at_95_tpr": fpr95,
        "threshold_grid": thresholds,
        "far_target_rows": far_targets,
        "oscr": oscr_result,
        "ece_known": {"n_bins": 10, "ece": ece_value, "bins": ece_bins},
        "brier_known": "NOT COMPUTABLE with current artifacts",
        "high_confidence_unknown": high_confidence,
        "unknown_prediction_counts": prediction_counts,
        "top_false_accepts": top_false_accepts,
        "reproducibility": runtime_metadata(inputs),
        "constraints": {
            "inference_rerun": False,
            "model_modified": False,
            "threshold_applied_to_pipeline": False,
            "rejection_implemented": False,
            "knn_used": False,
            "prior_used": False,
            "training_done": False,
        },
    }
    (OUTPUT / "open_set_discrimination_metrics.json").write_text(
        json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    with (OUTPUT / "open_set_threshold_analysis.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=thresholds[0].keys())
        writer.writeheader()
        writer.writerows(thresholds)

    plots_created = plot_distributions(known, unknown)
    metrics["reproducibility"]["plots_created"] = plots_created
    (OUTPUT / "open_set_discrimination_metrics.json").write_text(
        json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    report = build_report(metrics)
    (OUTPUT / "open_set_metrics_report.md").write_text(report, encoding="utf-8")
    print("========================================")
    print("ANURA / SITRana — FASE 5")
    print("MÉTRICAS OPEN SET")
    print("========================================")
    print("")
    print("STATUS: FASE_5_COMPLETE")
    print("")
    print(f"KNOWN: {len(known)}")
    print(f"UNKNOWN: {len(unknown)}")
    print(f"UNKNOWN SPECIES: {len(UNKNOWN_SPECIES)}")
    print("")
    print(f"AUROC TOP1: {auroc['top1_probability']:.6f}")
    print(f"AUROC MARGIN: {auroc['margin_top1_top2']:.6f}")
    print("AUROC DISTANCE: NOT COMPUTABLE")
    print("")
    print(f"FPR@95TPR: {fpr95['fpr']:.6f} (threshold={fpr95['threshold']:.6f})")
    print("")
    print("BEST ANALYTICAL SIGNAL: " + max(auroc, key=auroc.get))
    print(f"HIGH-CONFIDENCE UNKNOWN >= 0.90: {len(high_confidence['0.9'])}")
    print(f"ECE KNOWN: {ece_value:.6f}")
    print("BRIER KNOWN: NOT COMPUTABLE")
    print(f"OSCR: {oscr_result['area_under_curve']:.6f}")
    print("")
    print("RESULTS:")
    print("evaluation/open_set_v1/metrics/")
    print("")
    print("NO SE MODIFICÓ EL MODELO.")
    print("NO SE APLICÓ NINGÚN THRESHOLD.")
    print("NO SE IMPLEMENTÓ RECHAZO.")


def build_report(metrics):
    fpr95 = metrics["fpr_at_95_tpr"]
    unknown = metrics["unknown_prediction_counts"]
    report = [
        "# Fase 5 — Métricas y discriminación Open Set",
        "",
        f"**Estado:** `{metrics['status']}`",
        "",
        "## Alcance y fuentes",
        "",
        "- KNOWN: 766 imágenes de Fase 3, pertenecientes a 41 especies visuales.",
        "- UNKNOWN: 56 imágenes de Fase 4, de 2 especies no visuales.",
        "- Fuentes: `closed_set_results.json`, `closed_set_metrics.json`, `open_set_results.json`, `open_set_metrics.json`.",
        "- No se volvió a ejecutar inferencia.",
        "",
        "## Validación",
        "",
        "F3=766, F4=56, UNKNOWN=56, UNKNOWN species=2, leakage=0. "
        "No hubo duplicados, nulos ni valores fuera de rango en los scores disponibles.",
        "",
        "## Scores disponibles",
        "",
        "Se analizaron `top1_probability`, `top2_probability`, `top3_probability` y `margin_top1_top2`. "
        "No se calcularon entropía ni distancia porque los artefactos no contienen probabilidades completas "
        "ni embeddings/distancias.",
        "",
        "## AUROC",
        "",
    ]
    for score, value in metrics["auroc_known_positive"].items():
        report.append(f"- {score}: **{value:.6f}** (KNOWN es la clase positiva; score alto = más KNOWN).")
    report += [
        "",
        "## FPR @ 95% TPR",
        "",
        f"- Threshold analítico: **{fpr95['threshold']:.6f}**.",
        f"- TPR: **{fpr95['tpr']:.6f}**; FPR/FAR: **{fpr95['fpr']:.6f}**.",
        f"- KNOWN aceptados: {fpr95['known_accepted']}/{metrics['known_n']}.",
        f"- UNKNOWN aceptados: {fpr95['unknown_accepted']}/{metrics['unknown_n']}.",
        "- Este threshold es retrospectivo y no se aplicó al sistema.",
        "",
        "## FAR en la cuadrícula analítica",
        "",
        f"- FAR más cercana a 5%: threshold **{metrics['far_target_rows']['approximately_5_percent']['threshold']:.2f}**, "
        f"FAR **{metrics['far_target_rows']['approximately_5_percent']['false_acceptance_rate']:.2%}**, "
        f"Known Acceptance **{metrics['far_target_rows']['approximately_5_percent']['known_acceptance_rate']:.2%}**.",
        f"- FAR más cercana a 1%: threshold **{metrics['far_target_rows']['approximately_1_percent']['threshold']:.2f}**, "
        f"FAR **{metrics['far_target_rows']['approximately_1_percent']['false_acceptance_rate']:.2%}**, "
        f"Known Acceptance **{metrics['far_target_rows']['approximately_1_percent']['known_acceptance_rate']:.2%}**.",
        "- Son puntos de análisis retrospectivo; no son thresholds productivos.",
        "",
        "## OSCR",
        "",
        f"- Área OSCR: **{metrics['oscr']['area_under_curve']:.6f}**.",
        "- Definición: eje X = FPR de UNKNOWN; eje Y = CCR de KNOWN correctamente clasificados; "
        "barrido por `top1_probability` descendente.",
        "",
        "## Calibración",
        "",
        f"- ECE KNOWN: **{metrics['ece_known']['ece']:.6f}**, 10 bins uniformes en [0,1].",
        "- Brier multiclase KNOWN: **NOT COMPUTABLE**; no están disponibles las probabilidades completas.",
        "",
        "## UNKNOWN de alta confianza",
        "",
        f"- `top1_probability >= 0.90`: {len(metrics['high_confidence_unknown']['0.9'])}.",
        f"- `top1_probability >= 0.80`: {len(metrics['high_confidence_unknown']['0.8'])}.",
        f"- `top1_probability >= 0.70`: {len(metrics['high_confidence_unknown']['0.7'])}.",
        "Estos casos se denominan `HIGH_CONFIDENCE_OPEN_SET_PREDICTION`; no son errores de threshold oficial.",
        "",
        "## UNKNOWN por especie",
        "",
    ]
    for species, counts in unknown.items():
        report.append(f"- **{species}**: " + ", ".join(f"`{label}`={count}" for label, count in sorted(counts.items(), key=lambda item: -item[1])))
    report += [
        "",
        "## Interpretación",
        "",
        f"La mejor señal univariada por AUROC fue `{max(metrics['auroc_known_positive'], key=metrics['auroc_known_positive'].get)}`. "
        "Esto indica separación estadística en este experimento, pero no constituye un detector Open Set ni autoriza "
        "un threshold productivo.",
        f"Con TPR aproximadamente 95% de KNOWN, la FAR observada fue {fpr95['fpr']:.2%}.",
        "",
        "El conjunto Open Set actual contiene únicamente 56 imágenes de 2 especies UNKNOWN. "
        "Por tanto, los resultados son una evaluación piloto y no permiten afirmar generalización a todas las "
        "especies no visuales de Colombia.",
        "",
        "No se modificó el modelo, no se entrenó, no se aplicó threshold, no se implementó rechazo, "
        "no se utilizó k-NN ni prior geográfico.",
    ]
    return "\n".join(report) + "\n"


if __name__ == "__main__":
    main()
