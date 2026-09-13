"""Fase 6 — señales de embeddings y k-NN para Open Set.

Genera embeddings únicamente para las imágenes ya evaluadas en Fase 3/Fase 4,
consulta el paquete SQLite-vec existente y calcula métricas retrospectivas.
No modifica el paquete, el modelo ni el pipeline de producción.
"""

import csv
import hashlib
import json
import math
import platform
import sqlite3
import struct
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import open_clip
import sqlite_vec
import torch
from PIL import Image
from sklearn.metrics import auc, roc_auc_score, roc_curve
from scipy.stats import pearsonr, spearmanr
from torch.utils.data import DataLoader, Dataset


ROOT = Path(r"D:\Anura")
DATA_ROOT = ROOT / "data cleaned"
CHECKPOINT = ROOT / "bioclip" / "checkpoints" / "bioclip_anura_mejor.pt"
VOCABULARY = ROOT / "bioclip" / "checkpoints" / "vocabulario.json"
PACKAGE = ROOT / "bioclip" / "paquetes_regionales" / "antioquia_v1.sqlite"
F3_RESULTS = ROOT / "evaluation" / "open_set_v1" / "closed_set" / "closed_set_results.json"
F4_RESULTS = ROOT / "evaluation" / "open_set_v1" / "open_set" / "open_set_results.json"
F5_METRICS = ROOT / "evaluation" / "open_set_v1" / "metrics" / "open_set_discrimination_metrics.json"
OUTPUT = ROOT / "evaluation" / "open_set_v1" / "knn"
PLOTS = OUTPUT / "plots"
MODEL_NAME = "hf-hub:imageomics/bioclip"
K = 5
EMBEDDING_DIM = 512


class EncoderVisual(torch.nn.Module):
    def __init__(self, visual_encoder):
        super().__init__()
        self.visual = visual_encoder

    def forward(self, inputs):
        embedding = self.visual(inputs)
        return torch.nn.functional.normalize(embedding, dim=-1)


class ImageDataset(Dataset):
    def __init__(self, rows, preprocess):
        self.rows = rows
        self.preprocess = preprocess

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, index):
        row = self.rows[index]
        path = DATA_ROOT / Path(row["path"])
        with Image.open(path).convert("RGB") as image:
            return self.preprocess(image), index


def read_json(path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_inputs(known, unknown, f5):
    if len(known) != 766 or len(unknown) != 56:
        raise RuntimeError(f"STATUS: BLOCKED — F3={len(known)}, F4={len(unknown)}")
    if set(row["true_species"] for row in unknown) != {
        "Hyloxalus_picachos", "Sachatamia_electrops"
    }:
        raise RuntimeError("STATUS: BLOCKED — especies UNKNOWN inesperadas")
    if len({row["image_id"] for row in known + unknown}) != 822:
        raise RuntimeError("STATUS: BLOCKED — IDs duplicados entre F3/F4")
    for row in known + unknown:
        path = DATA_ROOT / Path(row["path"])
        if not path.exists():
            raise FileNotFoundError(path)
    for key in ("auroc_known_positive",):
        if key not in f5:
            raise RuntimeError("STATUS: BLOCKED — artefacto Fase 5 incompleto")


def package_metadata(connection):
    values = dict(connection.execute("SELECT clave, valor FROM manifest").fetchall())
    decoded = {}
    for key, value in values.items():
        try:
            decoded[key] = json.loads(value)
        except json.JSONDecodeError:
            decoded[key] = value
    count = connection.execute("SELECT count(*) FROM referencias").fetchone()[0]
    dimension = int(decoded["dimension_embedding"])
    if count != int(decoded["n_vectores"]) or dimension != EMBEDDING_DIM:
        raise RuntimeError("STATUS: BLOCKED — metadatos del paquete inconsistentes")
    return decoded, count


def query_neighbors(connection, embedding):
    packed = struct.pack(f"{len(embedding)}f", *embedding.tolist())
    rows = connection.execute(
        "SELECT rowid, distance FROM vec_referencias "
        "WHERE embedding MATCH ? AND k = ? ORDER BY distance",
        (packed, K),
    ).fetchall()
    if len(rows) != K:
        raise RuntimeError(f"Consulta k-NN devolvió {len(rows)} vecinos, se esperaban {K}")
    neighbors = []
    for rowid, distance in rows:
        metadata = connection.execute(
            "SELECT especie, genero, familia, ruta_foto, grupo_individuo "
            "FROM referencias WHERE id = ?",
            (rowid,),
        ).fetchone()
        if metadata is None:
            raise RuntimeError(f"Vecino {rowid} no tiene metadata")
        neighbors.append({
            "rowid": int(rowid),
            "distance": float(distance),
            "similarity": float(1.0 - distance),
            "species": metadata[0],
            "genus": metadata[1],
            "family": metadata[2],
            "path": metadata[3],
            "individual_id": metadata[4],
        })
    return neighbors


@torch.no_grad()
def generate_embeddings(rows, device):
    clip_model, _, preprocess = open_clip.create_model_and_transforms(MODEL_NAME)
    checkpoint = torch.load(CHECKPOINT, map_location="cpu", weights_only=False)
    clip_model.visual.load_state_dict(checkpoint["visual_state_dict"])
    encoder = EncoderVisual(clip_model.visual).to(device).eval()
    loader = DataLoader(
        ImageDataset(rows, preprocess), batch_size=32, num_workers=0, shuffle=False
    )
    embeddings = np.empty((len(rows), EMBEDDING_DIM), dtype=np.float32)
    for batch, indices in loader:
        batch = batch.to(device, non_blocking=True)
        with torch.autocast(device_type="cuda" if device == "cuda" else "cpu"):
            encoded = encoder(batch).float().cpu().numpy()
        embeddings[indices.numpy()] = encoded
    return embeddings


def distribution(values):
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


def calculate_metrics(records, softmax_reference):
    known = [row for row in records if row["known_unknown"] == "KNOWN"]
    unknown = [row for row in records if row["known_unknown"] == "UNKNOWN"]
    signal_names = ["max_similarity", "mean_top5_similarity", "species_vote_count"]
    scores = {
        name: (
            np.array([row[name] for row in known], dtype=float),
            np.array([row[name] for row in unknown], dtype=float),
        )
        for name in signal_names
    }
    labels = np.r_[np.ones(len(known)), np.zeros(len(unknown))]
    aurocs = {
        name: float(roc_auc_score(labels, np.r_[values[0], values[1]]))
        for name, values in scores.items()
    }
    best_signal = max(aurocs, key=aurocs.get)
    best_known, best_unknown = scores[best_signal]
    fpr, tpr, thresholds = roc_curve(
        labels, np.r_[best_known, best_unknown]
    )
    candidates = np.flatnonzero(tpr >= 0.95)
    if candidates.size == 0:
        fpr95 = {"threshold": None, "tpr": None, "fpr": None}
    else:
        index = candidates[0]
        threshold = thresholds[index]
        fpr95 = {
            "threshold": float(threshold),
            "tpr": float(tpr[index]),
            "fpr": float(fpr[index]),
            "known_accepted": int(np.sum(best_known >= threshold)),
            "unknown_accepted": int(np.sum(best_unknown >= threshold)),
        }

    low = float(min(best_known.min(), best_unknown.min()))
    high = float(max(best_known.max(), best_unknown.max()))
    grid = np.linspace(low, high, 21)
    threshold_rows = []
    for threshold in grid:
        accepted_known = int(np.sum(best_known >= threshold))
        accepted_unknown = int(np.sum(best_unknown >= threshold))
        threshold_rows.append({
            "signal": best_signal,
            "threshold": float(threshold),
            "known_acceptance_rate": accepted_known / len(best_known),
            "unknown_detection_rate": 1 - accepted_unknown / len(best_unknown),
            "false_acceptance_rate": accepted_unknown / len(best_unknown),
            "known_accepted": accepted_known,
            "unknown_accepted": accepted_unknown,
        })

    correlations = {}
    for knn_name in ("max_similarity", "mean_top5_similarity"):
        correlations[knn_name] = {}
        for softmax_name in ("softmax_top1", "softmax_margin"):
            x = np.array([row[knn_name] for row in records], dtype=float)
            y = np.array([row[softmax_name] for row in records], dtype=float)
            correlations[knn_name][softmax_name] = {
                "pearson_r": float(pearsonr(x, y).statistic),
                "spearman_rho": float(spearmanr(x, y).statistic),
            }

    distributions = {}
    for signal in signal_names:
        distributions[signal] = {
            "KNOWN": distribution([row[signal] for row in known]),
            "UNKNOWN": distribution([row[signal] for row in unknown]),
            "Hyloxalus_picachos": distribution(
                [row[signal] for row in unknown if row["true_species"] == "Hyloxalus_picachos"]
            ),
            "Sachatamia_electrops": distribution(
                [row[signal] for row in unknown if row["true_species"] == "Sachatamia_electrops"]
            ),
        }

    target_rows = {
        "approximately_5_percent_far": min(
            threshold_rows, key=lambda row: abs(row["false_acceptance_rate"] - 0.05)
        ),
        "approximately_1_percent_far": min(
            threshold_rows, key=lambda row: abs(row["false_acceptance_rate"] - 0.01)
        ),
    }
    unknown_species_analysis = {}
    for species in ("Hyloxalus_picachos", "Sachatamia_electrops"):
        species_rows = [row for row in unknown if row["true_species"] == species]
        unknown_species_analysis[species] = {
            "n": len(species_rows),
            "max_similarity": distribution([row["max_similarity"] for row in species_rows]),
            "mean_top5_similarity": distribution(
                [row["mean_top5_similarity"] for row in species_rows]
            ),
            "species_vote_count": distribution(
                [row["species_vote_count"] for row in species_rows]
            ),
            "predicted_species_counts": dict(
                Counter(row["predicted_species"] for row in species_rows)
            ),
        }
    top_false_accepts = {
        "by_max_similarity": sorted(
            unknown, key=lambda row: row["max_similarity"], reverse=True
        )[:10],
        "by_mean_top5_similarity": sorted(
            unknown, key=lambda row: row["mean_top5_similarity"], reverse=True
        )[:10],
        "consensus_5_of_5": [
            row for row in unknown if row["species_vote_count"] == 5
        ],
        "consensus_4_of_5": [
            row for row in unknown if row["species_vote_count"] == 4
        ],
        "predicted_species_counts": dict(
            Counter(row["predicted_species"] for row in unknown)
        ),
    }
    conclusion = (
        "VECTORIAL_PROMETEDORA"
        if aurocs[best_signal] > max(
            softmax_reference["top1_probability"],
            softmax_reference["margin_top1_top2"],
        ) + 0.05 and fpr95.get("fpr", 1.0) < 0.892857
        else "VECTORIAL_NO_MEJORA"
    )
    return {
        "known_n": len(known),
        "unknown_n": len(unknown),
        "signals": signal_names,
        "distributions": distributions,
        "auroc_known_positive": aurocs,
        "best_vectorial_signal": best_signal,
        "fpr_at_95_tpr": fpr95,
        "threshold_grid": threshold_rows,
        "far_target_rows": target_rows,
        "unknown_species_analysis": unknown_species_analysis,
        "top_false_accepts": top_false_accepts,
        "softmax_reference": softmax_reference,
        "correlations_all_images": correlations,
        "conclusion": conclusion,
        "geographic_filter": {
            "applied": True,
            "package": str(PACKAGE),
            "package_region": "Antioquia bbox materialized in antioquia_v1.sqlite",
        },
    }


def plot_distributions(records):
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return False
    PLOTS.mkdir(parents=True, exist_ok=True)
    known = [row for row in records if row["known_unknown"] == "KNOWN"]
    unknown = [row for row in records if row["known_unknown"] == "UNKNOWN"]
    for signal, filename, title in (
        ("max_similarity", "max_similarity_known_vs_unknown.png", "Max similarity"),
        ("mean_top5_similarity", "mean_top5_similarity_known_vs_unknown.png", "Mean Top-5 similarity"),
        ("species_vote_count", "species_vote_count_known_vs_unknown.png", "Species vote count"),
    ):
        plt.figure(figsize=(8, 5))
        plt.hist(
            [[row[signal] for row in known], [row[signal] for row in unknown]],
            bins=20,
            label=["KNOWN", "UNKNOWN"],
            alpha=0.7,
        )
        plt.xlabel(signal)
        plt.ylabel("Images")
        plt.title(title)
        plt.legend()
        plt.tight_layout()
        plt.savefig(PLOTS / filename, dpi=150)
        plt.close()
    return True


def runtime_metadata(inputs, package_manifest, device):
    try:
        branch = subprocess.check_output(
            ["git", "-C", str(ROOT), "branch", "--show-current"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        commit = subprocess.check_output(
            ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        status = subprocess.check_output(
            ["git", "-C", str(ROOT), "status", "--short"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        branch = commit = status = "NOT_A_GIT_REPOSITORY"
    return {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "python": sys.version,
        "platform": platform.platform(),
        "numpy": np.__version__,
        "sklearn": __import__("sklearn").__version__,
        "torch": torch.__version__,
        "open_clip": getattr(open_clip, "__version__", "unknown"),
        "sqlite_vec": getattr(sqlite_vec, "__version__", "unknown"),
        "device": device,
        "git_branch": branch,
        "git_commit": commit,
        "git_status": status,
        "input_sha256": {str(path): sha256(path) for path in inputs},
        "package_sha256": sha256(PACKAGE),
        "package_manifest": package_manifest,
    }


def build_report(metrics, metadata, records):
    fpr95 = metrics["fpr_at_95_tpr"]
    report = [
        "# Fase 6 — Embeddings, k-NN y señales Open Set",
        "",
        f"**Estado:** `FASE_6_COMPLETE`",
        "",
        "## Pipeline reproducido",
        "",
        "- Encoder: visual del checkpoint `bioclip_anura_mejor.pt`.",
        "- Dimensión observada: 512; el artefacto existente no produce 768 dimensiones.",
        "- Normalización: L2; se verificó norma media y máxima desviación en los embeddings guardados.",
        "- Métrica: similitud coseno mediante distancia sqlite-vec; `similarity = 1 - distance`.",
        "- k: 5.",
        "- Paquete: `antioquia_v1.sqlite`, filtro geográfico Antioquia ya materializado.",
        f"- Vectores consultados: {metadata['package_manifest']['n_vectores']}.",
        "",
        "## Comparación de señales",
        "",
    ]
    report += [
        f"- Softmax Top-1: AUROC {metrics['softmax_reference']['top1_probability']:.6f}.",
        f"- Softmax Margin: AUROC {metrics['softmax_reference']['margin_top1_top2']:.6f}.",
    ]
    for signal, value in metrics["auroc_known_positive"].items():
        report.append(f"- k-NN {signal}: AUROC **{value:.6f}**.")
    report += [
        "",
        f"Mejor señal vectorial: **{metrics['best_vectorial_signal']}**.",
        f"FPR/FAR @ 95% TPR: **{fpr95['fpr']:.6f}**, threshold analítico **{fpr95['threshold']:.6f}**.",
        f"KNOWN aceptados: {fpr95['known_accepted']}; UNKNOWN aceptados: {fpr95['unknown_accepted']}.",
        "",
        "## Consenso",
        "",
        "El consenso es el número máximo de los cinco vecinos que pertenecen a la misma especie; "
        "no se combinó con Softmax ni con ningún prior.",
        "",
        "## Correlación",
        "",
    ]
    for knn_name, values in metrics["correlations_all_images"].items():
        for softmax_name, correlation in values.items():
            report.append(
                f"- {knn_name} vs {softmax_name}: Pearson {correlation['pearson_r']:.6f}; "
                f"Spearman {correlation['spearman_rho']:.6f}."
            )
    report += [
        "",
        "## UNKNOWN",
        "",
        "- El conjunto UNKNOWN contiene 56 imágenes de solo 2 especies.",
        "- Las listas completas de vecinos y los casos de mayor similitud/consenso están en el JSON.",
        "- Los resultados son piloto y pueden reflejar sesgo de cobertura del catálogo y similitud visual real.",
        "",
        "### Resumen por especie",
        "",
    ]
    for species, values in metrics["unknown_species_analysis"].items():
        report.append(
            f"- **{species}** ({values['n']}): max similarity media "
            f"{values['max_similarity']['mean']:.6f}; mean Top-5 media "
            f"{values['mean_top5_similarity']['mean']:.6f}; consenso medio "
            f"{values['species_vote_count']['mean']:.3f}; predicciones "
            + ", ".join(
                f"{name}={count}"
                for name, count in sorted(
                    values["predicted_species_counts"].items(),
                    key=lambda item: item[1],
                    reverse=True,
                )
            )
            + "."
        )
    report += [
        "",
        "### Casos vectoriales destacados",
        "",
        f"- UNKNOWN con consenso 5/5: {len(metrics['top_false_accepts']['consensus_5_of_5'])}.",
        f"- UNKNOWN con consenso 4/5: {len(metrics['top_false_accepts']['consensus_4_of_5'])}.",
        "- Los 10 casos con mayor similitud máxima y media Top-5 están en los artefactos JSON.",
        "",
        f"## Conclusión: `{metrics['conclusion']}`",
        "",
        "k-NN no constituye por sí mismo un detector Open Set. No se creó score combinado, no se aplicó "
        "threshold y no se modificó el catálogo ni SQLite-vec.",
    ]
    return "\n".join(report) + "\n"


def main():
    known = read_json(F3_RESULTS)
    unknown = read_json(F4_RESULTS)
    phase5 = read_json(F5_METRICS)
    validate_inputs(known, unknown, phase5)
    rows = [
        *[dict(row, known_unknown="KNOWN") for row in known],
        *[dict(row, known_unknown="UNKNOWN") for row in unknown],
    ]
    device = "cuda" if torch.cuda.is_available() else "cpu"
    embeddings = generate_embeddings(rows, device)
    norms = np.linalg.norm(embeddings, axis=1)
    if float(np.max(np.abs(norms - 1.0))) > 1e-3:
        raise RuntimeError("STATUS: BLOCKED — embeddings no están L2-normalizados")

    connection = sqlite3.connect(str(PACKAGE))
    connection.enable_load_extension(True)
    sqlite_vec.load(connection)
    connection.enable_load_extension(False)
    package_manifest, vector_count = package_metadata(connection)
    records = []
    for index, row in enumerate(rows):
        neighbors = query_neighbors(connection, embeddings[index])
        species_counts = Counter(item["species"] for item in neighbors)
        predicted_species, vote_count = species_counts.most_common(1)[0]
        records.append({
            "image_id": row["image_id"],
            "path": row["path"],
            "true_species": row["true_species"],
            "known_unknown": row["known_unknown"],
            "embedding_dimension": int(embeddings.shape[1]),
            "embedding_norm": float(norms[index]),
            "softmax_top1": row["top1_probability"],
            "softmax_margin": row["margin_top1_top2"],
            "max_similarity": neighbors[0]["similarity"],
            "min_distance": neighbors[0]["distance"],
            "mean_top5_similarity": float(np.mean([item["similarity"] for item in neighbors])),
            "mean_top5_distance": float(np.mean([item["distance"] for item in neighbors])),
            "predicted_species": predicted_species,
            "species_vote_count": int(vote_count),
            "neighbors": neighbors,
            "geographic_filter_applied": True,
            "geographic_region": "Antioquia",
            "candidate_vector_count": vector_count,
            "k": K,
            "metric": "cosine",
        })
    connection.close()
    np.savez_compressed(OUTPUT / "knn_embeddings.npz", embeddings=embeddings)

    softmax_reference = {
        "top1_probability": phase5["auroc_known_positive"]["top1_probability"],
        "margin_top1_top2": phase5["auroc_known_positive"]["margin_top1_top2"],
    }
    metrics = calculate_metrics(records, softmax_reference)
    inputs = [F3_RESULTS, F4_RESULTS, F5_METRICS, CHECKPOINT]
    metadata = runtime_metadata(inputs, package_manifest, device)
    metadata["embedding_norm_mean"] = float(np.mean(norms))
    metadata["embedding_norm_max_abs_error"] = float(np.max(np.abs(norms - 1.0)))
    metrics["reproducibility"] = metadata
    metrics["status"] = "FASE_6_COMPLETE"
    metrics["constraints"] = {
        "model_modified": False,
        "training_done": False,
        "package_modified": False,
        "catalog_modified": False,
        "prior_used": False,
        "threshold_applied": False,
        "rejection_implemented": False,
        "combined_score_created": False,
        "segmentation_used": False,
    }

    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / "knn_open_set_results.json").write_text(
        json.dumps({
            "status": "FASE_6_COMPLETE",
            "n_records": len(records),
            "package": str(PACKAGE),
            "records": records,
        }, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (OUTPUT / "knn_discrimination_metrics.json").write_text(
        json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    with (OUTPUT / "knn_threshold_analysis.csv").open("w", newline="", encoding="utf-8") as handle:
        fieldnames = metrics["threshold_grid"][0].keys()
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(metrics["threshold_grid"])
    plots_created = plot_distributions(records)
    metrics["reproducibility"]["plots_created"] = plots_created
    (OUTPUT / "knn_discrimination_metrics.json").write_text(
        json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (OUTPUT / "knn_open_set_report.md").write_text(
        build_report(metrics, metadata, records), encoding="utf-8"
    )

    print("========================================")
    print("ANURA / SITRana — FASE 6")
    print("EMBEDDINGS + k-NN OPEN SET")
    print("========================================")
    print("")
    print("STATUS: FASE_6_COMPLETE")
    print("")
    print("KNOWN: 766")
    print("UNKNOWN: 56")
    print("")
    print(f"AUROC SOFTMAX TOP1: {softmax_reference['top1_probability']:.6f}")
    print(f"AUROC SOFTMAX MARGIN: {softmax_reference['margin_top1_top2']:.6f}")
    print(f"AUROC kNN MAX SIMILARITY: {metrics['auroc_known_positive']['max_similarity']:.6f}")
    print(f"AUROC kNN MEAN TOP5: {metrics['auroc_known_positive']['mean_top5_similarity']:.6f}")
    print(f"AUROC kNN CONSENSUS: {metrics['auroc_known_positive']['species_vote_count']:.6f}")
    print("")
    print(f"BEST VECTORIAL SIGNAL: {metrics['best_vectorial_signal']}")
    print(f"FPR@95TPR: {metrics['fpr_at_95_tpr']['fpr']:.6f}")
    print(f"FAR@95TPR: {metrics['fpr_at_95_tpr']['fpr']:.6f}")
    print("")
    print(f"CONCLUSION: {metrics['conclusion']}")
    print("")
    print("RESULTS:")
    print("evaluation/open_set_v1/knn/")
    print("")
    print("NO SE MODIFICÓ EL MODELO.")
    print("NO SE APLICÓ NINGÚN THRESHOLD.")
    print("NO SE IMPLEMENTÓ RECHAZO.")
    print("NO SE CREÓ SCORE COMBINADO.")


if __name__ == "__main__":
    main()
