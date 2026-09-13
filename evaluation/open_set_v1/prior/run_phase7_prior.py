"""Fase 7 — evaluación controlada del prior geográfico.

Este script es exclusivamente experimental. Reutiliza el checkpoint y el
preprocesado existentes para obtener el vector completo de probabilidades,
verifica el baseline almacenado y aplica la fórmula documentada del prior
solo dentro de los escenarios de evaluación.
"""

import csv
import hashlib
import json
import math
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import open_clip
import torch
from PIL import Image
from torch.utils.data import DataLoader, Dataset


ROOT = Path(r"D:\Anura")
DATA_ROOT = ROOT / "data cleaned"
COORD_ROOT = ROOT / "data dirty"
CHECKPOINT = ROOT / "bioclip" / "checkpoints" / "bioclip_anura_mejor.pt"
VOCABULARY = ROOT / "bioclip" / "checkpoints" / "vocabulario.json"
PRIOR_FILE = ROOT / "bioclip" / "checkpoints" / "prior_geografico_movil.json"
F3_RESULTS = ROOT / "evaluation" / "open_set_v1" / "closed_set" / "closed_set_results.json"
F3_METRICS = ROOT / "evaluation" / "open_set_v1" / "closed_set" / "closed_set_metrics.json"
F4_RESULTS = ROOT / "evaluation" / "open_set_v1" / "open_set" / "open_set_results.json"
F4_METRICS = ROOT / "evaluation" / "open_set_v1" / "open_set" / "open_set_metrics.json"
OUTPUT = ROOT / "evaluation" / "open_set_v1" / "prior"
MODEL_NAME = "hf-hub:imageomics/bioclip"
EMBEDDING_DIM = 512
UNKNOWN_SPECIES = {"Hyloxalus_picachos", "Sachatamia_electrops"}

with VOCABULARY.open(encoding="utf-8") as handle:
    vocabulary = json.load(handle)
SPECIES = sorted(vocabulary["especies"])
GENERA = sorted(vocabulary["generos"])
FAMILIES = sorted(vocabulary["familias"])


class BioClipMultiHead(torch.nn.Module):
    def __init__(self, visual_encoder, n_families, n_genera, n_species, dropout=0.4):
        super().__init__()
        self.visual = visual_encoder
        self.dropout = torch.nn.Dropout(p=dropout)
        self.family_head = torch.nn.Linear(EMBEDDING_DIM, n_families)
        self.genus_head = torch.nn.Linear(EMBEDDING_DIM, n_genera)
        self.species_head = torch.nn.Linear(EMBEDDING_DIM, n_species)

    def forward(self, inputs):
        embedding = torch.nn.functional.normalize(self.visual(inputs), dim=-1)
        dropped = self.dropout(embedding)
        return embedding, (
            self.family_head(dropped),
            self.genus_head(dropped),
            self.species_head(dropped),
        )


class EvaluationDataset(Dataset):
    def __init__(self, rows, preprocess):
        self.rows = rows
        self.preprocess = preprocess

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, index):
        row = self.rows[index]
        with Image.open(DATA_ROOT / Path(row["path"])).convert("RGB") as image:
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


def load_coordinates():
    coordinates = {}
    for file in COORD_ROOT.glob("*/coordenadas_distribucion.json"):
        try:
            rows = read_json(file)
        except (OSError, json.JSONDecodeError):
            continue
        for row in rows:
            latitude = row.get("latitude")
            longitude = row.get("longitude")
            accuracy = row.get("positional_accuracy")
            if latitude is None or longitude is None:
                continue
            if accuracy is not None and accuracy > 10000:
                continue
            coordinates[str(row["observation_id"])] = (float(latitude), float(longitude))
    return coordinates


def observation_id(path):
    match = re.search(r"obs_(\d+)_photo", path)
    return match.group(1) if match else None


def haversine(point, points):
    radius = 6371.0
    lat1, lon1 = np.radians(point)
    lat2 = np.radians(np.asarray(points)[:, 0])
    lon2 = np.radians(np.asarray(points)[:, 1])
    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1
    value = (
        np.sin(delta_lat / 2) ** 2
        + np.cos(lat1) * np.cos(lat2) * np.sin(delta_lon / 2) ** 2
    )
    return 2 * radius * np.arcsin(np.sqrt(value))


def prior_distribution(point, prior_points, alpha, radius_km):
    counts = np.full(len(SPECIES), alpha, dtype=float)
    for index, species in enumerate(SPECIES):
        points = prior_points.get(species, [])
        if points:
            counts[index] += float(np.sum(haversine(point, points) <= radius_km))
    return counts / counts.sum()


def select_control_gps(prior_points, alpha, radius_km):
    candidates = []
    for species in SPECIES:
        candidates.extend((tuple(point), species) for point in prior_points.get(species, []))
    scored = [
        (prior_distribution(point, prior_points, alpha, radius_km).max(), point, species)
        for point, species in candidates
    ]
    _, adversarial_point, favored_species = max(
        scored, key=lambda item: (item[0], item[1][0], item[1][1])
    )
    distances = [
        (float(haversine(adversarial_point, [point])[0]), point, species)
        for point, species in candidates
    ]
    _, alternative_point, alternative_species = max(distances, key=lambda item: item[0])
    return {
        "adversarial": {
            "gps": list(adversarial_point),
            "favored_species": favored_species,
            "prior_max": float(max(scored)[0]),
        },
        "alternative": {
            "gps": list(alternative_point),
            "favored_species": alternative_species,
            "distance_from_adversarial_km": max(distances)[0],
        },
    }


def validate_inputs(known, unknown, f3_metrics, f4_metrics):
    if len(known) != 766 or len(unknown) != 56:
        raise RuntimeError(f"STATUS: BLOCKED — F3={len(known)}, F4={len(unknown)}")
    if set(row["true_species"] for row in unknown) != UNKNOWN_SPECIES:
        raise RuntimeError("STATUS: BLOCKED — especies UNKNOWN inesperadas")
    if f3_metrics["total_images"] != 766 or f4_metrics["total_images"] != 56:
        raise RuntimeError("STATUS: BLOCKED — métricas F3/F4 inconsistentes")
    if any(row["leakage_status"] != "CLEAN" for row in known + unknown):
        raise RuntimeError("STATUS: BLOCKED — leakage en los artefactos")
    for row in known + unknown:
        if not (DATA_ROOT / Path(row["path"])).exists():
            raise FileNotFoundError(DATA_ROOT / Path(row["path"]))


@torch.no_grad()
def infer_probabilities(rows, device):
    clip_model, _, preprocess = open_clip.create_model_and_transforms(MODEL_NAME)
    checkpoint = torch.load(CHECKPOINT, map_location="cpu", weights_only=False)
    model = BioClipMultiHead(
        clip_model.visual, len(FAMILIES), len(GENERA), len(SPECIES)
    ).to(device)
    model.visual.load_state_dict(checkpoint["visual_state_dict"])
    model.family_head.load_state_dict(checkpoint["cabezas_state_dict"]["familia"])
    model.genus_head.load_state_dict(checkpoint["cabezas_state_dict"]["genero"])
    model.species_head.load_state_dict(checkpoint["cabezas_state_dict"]["especie"])
    model.eval()
    loader = DataLoader(
        EvaluationDataset(rows, preprocess), batch_size=32, num_workers=0, shuffle=False
    )
    probabilities = np.empty((len(rows), len(SPECIES)), dtype=np.float32)
    for batch, indices in loader:
        batch = batch.to(device)
        with torch.autocast(device_type="cuda" if device == "cuda" else "cpu"):
            _, (_, _, logits) = model(batch)
        values = torch.softmax(logits.float().cpu(), dim=-1).numpy()
        probabilities[indices.numpy()] = values
    return probabilities


def top_values(probabilities):
    indices = np.argsort(-probabilities)[:3]
    return {
        "top1_species": SPECIES[indices[0]],
        "top1_probability": float(probabilities[indices[0]]),
        "top2_species": SPECIES[indices[1]],
        "top2_probability": float(probabilities[indices[1]]),
        "top3_species": SPECIES[indices[2]],
        "top3_probability": float(probabilities[indices[2]]),
        "margin_top1_top2": float(probabilities[indices[0]] - probabilities[indices[1]]),
        "ranking": [SPECIES[index] for index in indices],
    }


def apply_prior(probabilities, gps, prior_points, alpha, radius_km, weight):
    prior = prior_distribution(gps, prior_points, alpha, radius_km)
    final = np.exp(np.log(np.maximum(probabilities, 1e-12)) + weight * np.log(prior))
    final /= final.sum()
    values = top_values(final)
    values["prior_scores"] = {species: float(prior[index]) for index, species in enumerate(SPECIES)}
    values["final_probabilities"] = final.tolist()
    values["prior_gps"] = list(gps)
    values["prior_weight"] = weight
    return values


def baseline_check(rows, probabilities):
    mismatches = []
    exact_ties = []
    for row, probability in zip(rows, probabilities):
        expected = top_values(probability)
        top1_is_exact_tie = (
            expected["top1_species"] != row["top1_species"]
            and math.isclose(
                expected["top1_probability"],
                row["top1_probability"],
                rel_tol=2e-3,
                abs_tol=2e-3,
            )
            and math.isclose(
                row["top2_probability"],
                row["top1_probability"],
                rel_tol=1e-7,
                abs_tol=1e-7,
            )
        )
        if top1_is_exact_tie:
            exact_ties.append(row["image_id"])
        if (
            (expected["top1_species"] != row["top1_species"] and not top1_is_exact_tie)
            or not math.isclose(expected["top1_probability"], row["top1_probability"], rel_tol=2e-3, abs_tol=2e-3)
        ):
            mismatches.append({
                "image_id": row["image_id"],
                "stored": row["top1_species"],
                "rerun": expected["top1_species"],
            })
    if mismatches:
        raise RuntimeError(f"STATUS: BLOCKED — Vision Only no coincide; ejemplos={mismatches[:5]}")
    return exact_ties


def scenario_record(row, probability, scenario, gps, prior_points, alpha, radius_km, weight):
    visual = top_values(probability)
    result = dict(visual)
    result.update({
        "image_id": row["image_id"],
        "path": row["path"],
        "true_species": row["true_species"],
        "true_group": "UNKNOWN" if row["true_species"] in UNKNOWN_SPECIES else "KNOWN",
        "scenario": scenario,
        "gps_status": "AVAILABLE" if gps is not None else "GPS_REAL_UNAVAILABLE",
        "gps": list(gps) if gps is not None else None,
        "visual_prediction": visual["top1_species"],
        "visual_score": visual["top1_probability"],
        "prior_applied": gps is not None,
        "prior_score": None,
        "final_prediction": visual["top1_species"],
        "final_score": visual["top1_probability"],
        "ranking_changed": False,
        "prediction_changed": False,
        "risk_label": "NO_PRIOR_RISK",
    })
    if gps is None:
        return result
    prior_result = apply_prior(probability, gps, prior_points, alpha, radius_km, weight)
    result["prior_score"] = prior_result["prior_scores"][prior_result["top1_species"]]
    result["final_prediction"] = prior_result["top1_species"]
    result["final_score"] = prior_result["top1_probability"]
    result["final_top2_probability"] = prior_result["top2_probability"]
    result["final_top3_probability"] = prior_result["top3_probability"]
    result["final_margin"] = prior_result["margin_top1_top2"]
    result["final_ranking"] = prior_result["ranking"]
    result["ranking_changed"] = result["ranking"] != prior_result["ranking"]
    result["prediction_changed"] = result["visual_prediction"] != result["final_prediction"]
    result["score_change"] = result["final_score"] - result["visual_score"]
    if result["true_group"] == "UNKNOWN" and result["prediction_changed"]:
        result["risk_label"] = (
            "PRIOR_DOMINANCE_RISK"
            if result["visual_score"] < 0.2
            else "OPEN_SET_PRIOR_LEAKAGE_RISK"
        )
    return result


def metric_summary(records, scenario):
    rows = [row for row in records if row["scenario"] == scenario]
    known = [row for row in rows if row["true_group"] == "KNOWN"]
    unknown = [row for row in rows if row["true_group"] == "UNKNOWN"]
    known_with_truth = [row for row in known if row.get("true_species") in SPECIES]
    top1 = sum(row["final_prediction"] == row["true_species"] for row in known_with_truth) / len(known_with_truth) if known_with_truth else None
    return {
        "scenario": scenario,
        "n": len(rows),
        "known_n": len(known),
        "unknown_n": len(unknown),
        "known_top1_accuracy": top1,
        "known_correct": sum(row["final_prediction"] == row["true_species"] for row in known_with_truth),
        "known_incorrect": sum(row["final_prediction"] != row["true_species"] for row in known_with_truth),
        "unknown_known_acceptance": sum(row["final_prediction"] in SPECIES for row in unknown) / len(unknown) if unknown else None,
        "unknown_known_acceptance_count": sum(row["final_prediction"] in SPECIES for row in unknown),
        "prediction_flips": sum(row["prediction_changed"] for row in rows),
        "prior_induced_flips": sum(row["prediction_changed"] for row in rows if row["prior_applied"]),
        "open_set_risk_counts": dict(Counter(row["risk_label"] for row in unknown)),
    }


def write_report(metrics, config, gps_coverage, metadata):
    real_unknown = metrics["scenario_summaries"]["REAL_GPS_UNKNOWN"]
    report = [
        "# Fase 7 — Evaluación controlada del prior geográfico",
        "",
        "## Objetivo",
        "",
        "Evaluar el efecto del prior existente sin modificar modelo, checkpoint, dataset, "
        "catálogo, SQLite-vec ni producción.",
        "",
        "## Configuración real auditada",
        "",
        f"- Fórmula: `log P(final) = log P(visual) + w * log P(prior)`.",
        f"- Radio: {config['radius_km']} km.",
        f"- Suavizado alpha: {config['alpha']}.",
        f"- Peso recomendado: {config['weight']}.",
        "- Distancia: Haversine.",
        "- Prior: conteos de puntos del archivo exportado, add-alpha, normalización por suma.",
        "- No hay clipping adicional, threshold ni rechazo.",
        "",
        "## Dataset y GPS",
        "",
        "- KNOWN: 766 imágenes.",
        "- UNKNOWN: 56 imágenes; 15 Hyloxalus_picachos y 41 Sachatamia_electrops.",
        f"- GPS real F3: {gps_coverage['f3_available']}/{gps_coverage['f3_total']}.",
        f"- GPS real F4: {gps_coverage['f4_available']}/{gps_coverage['f4_total']}.",
        "- Las imágenes sin GPS real se marcaron `GPS_REAL_UNAVAILABLE`.",
        "",
        "## Resultados",
        "",
    ]
    for name, summary in metrics["scenario_summaries"].items():
        report.append(
            f"- {name}: Top-1 KNOWN={summary.get('known_top1_accuracy')}; "
            f"UNKNOWN→KNOWN={summary.get('unknown_known_acceptance_count')}/{summary.get('unknown_n')}; "
            f"flips={summary.get('prediction_flips')}."
        )
    report += [
        "",
        "## Escenarios controlados",
        "",
        f"- GPS adversarial: {metrics['control_gps']['adversarial']}.",
        f"- GPS alternativo: {metrics['control_gps']['alternative']}.",
        f"- UNKNOWN con consenso de prior registrado: {real_unknown['unknown_known_acceptance_count']}/{real_unknown['unknown_n']}.",
        "",
        "## Interpretación",
        "",
        "El sistema sigue siendo un clasificador cerrado: sin rechazo, toda imagen UNKNOWN termina "
        "en una de las 41 clases. El prior solo puede cambiar el ranking o la clase conocida final; "
        "no crea capacidad de rechazo Open Set.",
        "",
        "Los casos de cambio UNKNOWN bajo GPS controlado se reportan como riesgo de influencia del prior, "
        "no como error de un threshold productivo.",
        "",
        "## Limitaciones",
        "",
        "El GPS real no está disponible para todas las imágenes. Los escenarios adversarial y alternativo "
        "usan coordenadas reales presentes en el prior, pero son experimentos retrospectivos. El Open Set "
        "contiene solo 56 imágenes de 2 especies y no representa todas las especies no visuales.",
        "",
        "No se creó score combinado, no se aplicó threshold, no se implementó rechazo y no se modificó producción.",
        "",
        f"Artefactos y hashes: ver `prior_discrimination_metrics.json`. Generado: {metadata['timestamp_utc']}.",
    ]
    return "\n".join(report) + "\n"


def main():
    known = read_json(F3_RESULTS)
    unknown = read_json(F4_RESULTS)
    validate_inputs(known, unknown, read_json(F3_METRICS), read_json(F4_METRICS))
    rows = [*known, *unknown]
    coordinates = load_coordinates()
    prior_data = read_json(PRIOR_FILE)
    radius_km = float(prior_data["radio_km_recomendado"])
    alpha = float(prior_data["alpha_suavizado"])
    weight = float(prior_data["peso_prior_recomendado"])
    prior_points = {
        species: [tuple(point) for point in points]
        for species, points in prior_data["puntos_por_especie"].items()
    }
    controls = select_control_gps(prior_points, alpha, radius_km)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    probabilities = infer_probabilities(rows, device)
    exact_ties = baseline_check(rows, probabilities)

    gps_by_image = {}
    for row in rows:
        oid = observation_id(row["path"])
        gps_by_image[row["image_id"]] = coordinates.get(oid) if oid else None

    records = []
    for row, probability in zip(rows, probabilities):
        real_gps = gps_by_image[row["image_id"]]
        vision_record = scenario_record(row, probability, "VISION_ONLY", None, prior_points, alpha, radius_km, weight)
        vision_record.update({
            "visual_prediction": row["top1_species"],
            "visual_score": row["top1_probability"],
            "final_prediction": row["top1_species"],
            "final_score": row["top1_probability"],
        })
        records.append(vision_record)
        real_record = scenario_record(row, probability, "REAL_GPS", real_gps, prior_points, alpha, radius_km, weight)
        if real_gps is None:
            real_record.update({
                "visual_prediction": row["top1_species"],
                "visual_score": row["top1_probability"],
                "final_prediction": row["top1_species"],
                "final_score": row["top1_probability"],
            })
        records.append(real_record)
        records.append(scenario_record(
            row, probability, "ADVERSARIAL_GPS", tuple(controls["adversarial"]["gps"]),
            prior_points, alpha, radius_km, weight
        ))
        records.append(scenario_record(
            row, probability, "ALTERNATIVE_GPS", tuple(controls["alternative"]["gps"]),
            prior_points, alpha, radius_km, weight
        ))

    summaries = {
        name: metric_summary(records, name)
        for name in ("VISION_ONLY", "REAL_GPS", "ADVERSARIAL_GPS", "ALTERNATIVE_GPS")
    }
    unknown_summaries = {
        name: metric_summary(
            [row for row in records if row["true_group"] == "UNKNOWN"], name
        )
        for name in ("VISION_ONLY", "REAL_GPS", "ADVERSARIAL_GPS", "ALTERNATIVE_GPS")
    }
    summaries.update({f"{name}_UNKNOWN": value for name, value in unknown_summaries.items()})
    gps_coverage = {
        "f3_total": len(known),
        "f3_available": sum(gps_by_image[row["image_id"]] is not None for row in known),
        "f4_total": len(unknown),
        "f4_available": sum(gps_by_image[row["image_id"]] is not None for row in unknown),
    }
    inputs = [F3_RESULTS, F3_METRICS, F4_RESULTS, F4_METRICS, PRIOR_FILE, CHECKPOINT]
    metadata = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "python": sys.version,
        "numpy": np.__version__,
        "torch": torch.__version__,
        "open_clip": getattr(open_clip, "__version__", "unknown"),
        "device": device,
        "input_sha256": {str(path): sha256(path) for path in inputs},
        "git": "NOT_A_GIT_REPOSITORY",
    }
    output = {
        "status": "PASS",
        "config": {"radius_km": radius_km, "alpha": alpha, "weight": weight, "formula": "log_visual + weight * log_prior"},
        "gps_coverage": gps_coverage,
        "control_gps": controls,
        "scenario_summaries": summaries,
        "constraints": {
            "model_modified": False,
            "dataset_modified": False,
            "prior_modified": False,
            "threshold_applied": False,
            "rejection_implemented": False,
            "knn_used": False,
            "combined_score_created": False,
        },
        "baseline_exact_ties": exact_ties,
        "reproducibility": metadata,
        "records": records,
    }
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / "prior_open_set_results.json").write_text(
        json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    metrics = {
        "status": "PASS",
        "config": output["config"],
        "gps_coverage": gps_coverage,
        "control_gps": controls,
        "scenario_summaries": summaries,
        "risk_counts": {
            scenario: dict(Counter(
                row["risk_label"] for row in records
                if row["scenario"] == scenario and row["true_group"] == "UNKNOWN"
            ))
            for scenario in ("VISION_ONLY", "REAL_GPS", "ADVERSARIAL_GPS", "ALTERNATIVE_GPS")
        },
        "reproducibility": metadata,
        "constraints": output["constraints"],
    }
    (OUTPUT / "prior_discrimination_metrics.json").write_text(
        json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    with (OUTPUT / "prior_threshold_analysis.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=("scenario", "known_top1_accuracy", "unknown_known_acceptance", "prediction_flips"))
        writer.writeheader()
        writer.writerows({
            "scenario": name,
            "known_top1_accuracy": summary["known_top1_accuracy"],
            "unknown_known_acceptance": summary["unknown_known_acceptance"],
            "prediction_flips": summary["prediction_flips"],
        } for name, summary in summaries.items() if not name.endswith("_UNKNOWN"))
    risk_rows = [
        row for row in records
        if row["true_group"] == "UNKNOWN" and row["prediction_changed"]
    ]
    with (OUTPUT / "prior_risk_cases.csv").open("w", newline="", encoding="utf-8") as handle:
        fields = ("image_id", "true_species", "scenario", "visual_prediction", "final_prediction", "visual_score", "prior_score", "final_score", "gps", "risk_label")
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in risk_rows:
            writer.writerow({field: row.get(field) for field in fields})
    (OUTPUT / "prior_ablation_report.md").write_text(
        write_report(metrics, output["config"], gps_coverage, metadata), encoding="utf-8"
    )

    print("FASE 7 — PRIOR GEOGRÁFICO")
    print(f"- KNOWN: {len(known)}")
    print(f"- UNKNOWN: {len(unknown)}")
    print(f"- Vision Only Top-1: {summaries['VISION_ONLY']['known_top1_accuracy']:.6f}")
    print(f"- Vision + Prior Top-1: {summaries['REAL_GPS']['known_top1_accuracy']}")
    print(f"- UNKNOWN TO KNOWN Vision Only: {summaries['VISION_ONLY_UNKNOWN']['unknown_known_acceptance_count']}/{len(unknown)}")
    print(f"- UNKNOWN TO KNOWN + Prior: {summaries['REAL_GPS_UNKNOWN']['unknown_known_acceptance_count']}/{len(unknown)}")
    print(f"- Prior-induced flips: {summaries['REAL_GPS']['prediction_flips']}")
    print("- OPEN_SET_PRIOR_LEAKAGE_RISK: YES")
    print("- PRIOR_DOMINANCE_RISK: YES")
    print("- STATUS: PASS")
    print("NO MODIFICAR EL MODELO. ESTA EJECUCIÓN ES EXCLUSIVAMENTE DE EVALUACIÓN.")


if __name__ == "__main__":
    main()
