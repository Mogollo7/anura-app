"""Open Set calibration v1: frozen encoder, independent calibration, Fase 23A blind.

This is a diagnostic/release-selection protocol. It never writes outside this folder and
does not modify model weights, source data, historical thresholds, or Fase 23A artifacts.
"""
from __future__ import annotations

import csv
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image
from sklearn.covariance import LedoitWolf
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import roc_auc_score

ROOT = Path(r"D:\Anura")
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "validation" / "merlin_identification_flow"))
from runtime_adapters import BioClipOnnxAdapter, canonical_name  # noqa: E402

SEED = 20260914
TARGET_FAR = 0.05
CAL_MANIFEST = ROOT / "validation/fase18_clean_calibration/calibration_manifest.json"
CLEAN_KNOWN = ROOT / "validation/fase16_clean_open_set/clean_known_embeddings.npz"
# The supplementary_historical directories are metadata-only. Their 130 physical historical
# files reside in images/final; these four species are absent from Fase23A primary/blind.
FINAL_UNKNOWN = ROOT / "data/unknown_open_set_v2/images/final"
CALIBRATION_UNKNOWN_SPECIES = {
    "Hyloxalus_picachos", "Dendropsophus_minutus", "Pristimantis_w_nigrum", "Sachatamia_electrops",
}
F23_UNKNOWN = ROOT / "validation/fase23a_open_set_automatic/embeddings/unknown_embeddings.npz"


def json_dump(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding="utf-8")


def stats(values: np.ndarray) -> dict[str, float]:
    values = np.asarray(values, dtype=float)
    return {key: float(fn(values)) for key, fn in {
        "min": np.min, "p05": lambda x: np.percentile(x, 5), "p25": lambda x: np.percentile(x, 25),
        "median": np.median, "p75": lambda x: np.percentile(x, 75), "p95": lambda x: np.percentile(x, 95),
        "max": np.max, "mean": np.mean, "std": np.std,
    }.items()}


def quality(path: Path) -> dict[str, float]:
    """Image-only quality signals; no class label or model score is used."""
    with Image.open(path).convert("L") as image:
        array = np.asarray(image.resize((min(256, image.width), max(1, round(image.height * min(256, image.width) / image.width)))), dtype=np.float32)
        h, w = array.shape
        lap = -4 * array[1:-1, 1:-1] + array[:-2, 1:-1] + array[2:, 1:-1] + array[1:-1, :-2] + array[1:-1, 2:]
        return {
            "brightness": float(array.mean()), "contrast": float(array.std()),
            "blur_laplacian_variance": float(lap.var()) if lap.size else 0.0,
            "min_dimension": float(min(image.width, image.height)), "pixel_count": float(image.width * image.height),
        }


def species_from_path(path: Path) -> str:
    return path.parent.name.replace("_", " ")


def collect_supplementary() -> list[dict[str, Any]]:
    rows = []
    for path in sorted(FINAL_UNKNOWN.rglob("*")):
        if path.suffix.lower() not in {".jpg", ".jpeg", ".png"}:
            continue
        if path.parent.name not in CALIBRATION_UNKNOWN_SPECIES:
            continue
        species = species_from_path(path)
        if species == "Hyloxalus picachos":
            stratum = "SAME_FAMILY_GENUS_ABSENT"
        elif species == "Sachatamia electrops":
            stratum = "FAMILY_ABSENT"
        else:
            stratum = "SAME_GENUS_CATALOG_PRESENT"
        rows.append({"path": path, "species": species, "stratum": stratum})
    assert len(rows) == 130, f"Expected 130 historical calibration images, found {len(rows)}"
    return rows


def load_or_embed_unknown(rows: list[dict[str, Any]]) -> np.ndarray:
    output = OUT / "supplementary_unknown_embeddings.npz"
    path_strings = np.array([str(row["path"]) for row in rows])
    if output.exists():
        loaded = np.load(output, allow_pickle=True)
        if np.array_equal(loaded["paths"], path_strings):
            return loaded["embeddings"].astype(np.float32)
    adapter = BioClipOnnxAdapter()
    embeddings = []
    for index, row in enumerate(rows, start=1):
        embedding, _ = adapter.embed_image(row["path"])
        embeddings.append(embedding)
        print(f"[embed] {index}/{len(rows)}", flush=True)
    matrix = np.asarray(embeddings, dtype=np.float32)
    np.savez_compressed(output, embeddings=matrix, paths=path_strings,
                        species=np.array([row["species"] for row in rows]),
                        stratum=np.array([row["stratum"] for row in rows]))
    return matrix


def build_centroids() -> tuple[np.ndarray, list[str], dict[str, np.ndarray], dict[str, float]]:
    registry = json.loads((ROOT / "taxonomy/species/species_registry.json").read_text(encoding="utf-8"))
    release = json.loads((ROOT / "visual_catalog/v1.0.0/manifest.json").read_text(encoding="utf-8"))
    allowed = set(release["species_ids"])
    species_id = {item["scientific_name"]: item["species_id"] for item in registry["species"]}
    ref = np.load(ROOT / "evaluation/fase13/embeddings/reference_embeddings.npz")
    train = np.load(ROOT / "evaluation/fase13/embeddings/train_embeddings.npz")
    ref_names = np.array([canonical_name(str(name)) for name in ref["species"]])
    train_names = np.array([canonical_name(str(name)) for name in train["species"]])
    ref_centroids = {name: ref["embeddings"][ref_names == name].mean(axis=0) for name in np.unique(ref_names)}
    train_centroids = {name: train["embeddings"][train_names == name].mean(axis=0) for name in np.unique(train_names)}
    centroids: dict[str, np.ndarray] = {}
    samples: dict[str, np.ndarray] = {}
    for name, centroid in ref_centroids.items():
        if name in train_centroids and species_id.get(name) in allowed:
            centroids[name] = centroid
            samples[name] = ref["embeddings"][ref_names == name]
    for name, centroid in train_centroids.items():
        if species_id.get(name) in allowed and name not in centroids:
            centroids[name] = centroid
            samples[name] = train["embeddings"][train_names == name]
    names = sorted(centroids)
    assert len(names) == 41, len(names)
    dispersion = {name: float(np.percentile(np.linalg.norm(samples[name] - centroids[name], axis=1), 95)) for name in names}
    return np.asarray([centroids[name] for name in names], dtype=np.float32), names, samples, dispersion


def features(x: np.ndarray, centers: np.ndarray, names: list[str], dispersion: dict[str, float]) -> dict[str, np.ndarray]:
    distances = np.linalg.norm(x[:, None, :] - centers[None, :, :], axis=2)
    order = np.argsort(distances, axis=1)
    first, second = order[:, 0], order[:, 1]
    d1 = distances[np.arange(len(x)), first]
    d2 = distances[np.arange(len(x)), second]
    selected = np.asarray([names[index] for index in first])
    return {"d1": d1, "d2": d2, "margin": d2 - d1, "selected": selected,
            "consistency": np.asarray([d1[i] / max(dispersion[selected[i]], 1e-8) for i in range(len(x))])}


def multiple_prototype_centers(samples: dict[str, np.ndarray], names: list[str]) -> tuple[np.ndarray, np.ndarray]:
    centers, labels = [], []
    for name in names:
        data = samples[name]
        if len(data) >= 20:
            # Registered before evaluation: exactly two prototypes, fixed seed, source-only fit.
            fitted = KMeans(n_clusters=2, n_init=20, random_state=SEED).fit(data)
            centers.extend(fitted.cluster_centers_)
            labels.extend([name, name])
        else:
            centers.append(data.mean(axis=0)); labels.append(name)
    return np.asarray(centers, dtype=np.float32), np.asarray(labels)


def prototype_features(x: np.ndarray, proto_centers: np.ndarray, proto_labels: np.ndarray, names: list[str], dispersion: dict[str, float]) -> dict[str, np.ndarray]:
    d = np.linalg.norm(x[:, None, :] - proto_centers[None, :, :], axis=2)
    species_dist = np.stack([d[:, proto_labels == name].min(axis=1) for name in names], axis=1)
    order = np.argsort(species_dist, axis=1); first, second = order[:, 0], order[:, 1]
    d1 = species_dist[np.arange(len(x)), first]; d2 = species_dist[np.arange(len(x)), second]
    selected = np.asarray([names[index] for index in first])
    return {"d1": d1, "d2": d2, "margin": d2 - d1, "selected": selected,
            "consistency": np.asarray([d1[i] / max(dispersion[selected[i]], 1e-8) for i in range(len(x))])}


def mahalanobis_features(x: np.ndarray, centers: np.ndarray, reference: np.ndarray, mode: str) -> np.ndarray:
    if mode == "diagonal":
        variance = np.maximum(reference.var(axis=0), 1e-6)
        return np.sqrt(((x[:, None, :] - centers[None, :, :]) ** 2 / variance[None, None, :]).sum(axis=2)).min(axis=1)
    if mode == "shrinkage":
        precision = LedoitWolf().fit(reference).precision_
        diff = x[:, None, :] - centers[None, :, :]
        return np.sqrt(np.maximum(0, np.einsum("nkd,de,nke->nk", diff, precision, diff))).min(axis=1)
    # PCA dimension was registered before evaluation: 64 < 10% of 798 reference rows.
    pca = PCA(n_components=64, random_state=SEED).fit(reference)
    ref_p, x_p, c_p = pca.transform(reference), pca.transform(x), pca.transform(centers)
    precision = LedoitWolf().fit(ref_p).precision_
    diff = x_p[:, None, :] - c_p[None, :, :]
    return np.sqrt(np.maximum(0, np.einsum("nkd,de,nke->nk", diff, precision, diff))).min(axis=1)


def select_rule(known: dict[str, np.ndarray], unknown: dict[str, np.ndarray], mode: str, quality_gate: dict[str, float] | None = None) -> dict[str, Any]:
    """Select strictly on calibration: maximize KAR subject to FAR <= target."""
    kd, ud = known["d1"], unknown["d1"]
    km, um = known["margin"], unknown["margin"]
    kc, uc = known["consistency"], unknown["consistency"]
    d_grid = np.unique(np.quantile(np.concatenate([kd, ud]), np.linspace(0, 1, 101)))
    m_grid = np.array([0.0]) if mode == "distance" else np.unique(np.quantile(np.concatenate([km, um]), np.linspace(0, 0.9, 31)))
    c_grid = np.array([math.inf]) if mode != "consistency" else np.unique(np.quantile(np.concatenate([kc, uc]), np.linspace(0.1, 1, 31)))
    best = None
    for threshold_d in d_grid:
        for threshold_m in m_grid:
            for threshold_c in c_grid:
                accept_known = (kd <= threshold_d) & (km >= threshold_m) & (kc <= threshold_c)
                accept_unknown = (ud <= threshold_d) & (um >= threshold_m) & (uc <= threshold_c)
                if quality_gate:
                    for field, threshold in quality_gate.items():
                        accept_known &= known[field] >= threshold
                        accept_unknown &= unknown[field] >= threshold
                far, kar = float(accept_unknown.mean()), float(accept_known.mean())
                candidate = (far <= TARGET_FAR, kar, -far, threshold_d, threshold_m, threshold_c)
                if best is None or candidate > best[0]:
                    best = (candidate, {"distance_threshold": float(threshold_d), "margin_threshold": float(threshold_m),
                                        "consistency_threshold": None if math.isinf(threshold_c) else float(threshold_c),
                                        "far": far, "udr": 1 - far, "kar": kar, "frr": 1 - kar,
                                        "far_constraint_met": far <= TARGET_FAR})
    return best[1]


def metrics(known: dict[str, np.ndarray], unknown: dict[str, np.ndarray], rule: dict[str, Any], quality_gate: dict[str, float] | None = None) -> dict[str, Any]:
    def accepted(value: dict[str, np.ndarray]) -> np.ndarray:
        result = ((value["d1"] <= rule["distance_threshold"]) & (value["margin"] >= rule["margin_threshold"]))
        if rule["consistency_threshold"] is not None:
            result &= value["consistency"] <= rule["consistency_threshold"]
        if quality_gate:
            for field, threshold in quality_gate.items(): result &= value[field] >= threshold
        return result
    ak, au = accepted(known), accepted(unknown)
    score = np.concatenate([known["d1"], unknown["d1"]])
    labels = np.concatenate([np.zeros(len(known["d1"])), np.ones(len(unknown["d1"]))])
    return {"far": float(au.mean()), "udr": float(1 - au.mean()), "kar": float(ak.mean()), "frr": float(1 - ak.mean()),
            "balanced_accuracy": float(((1 - au.mean()) + ak.mean()) / 2), "auroc_d1": float(roc_auc_score(labels, score)),
            "known_accepted": int(ak.sum()), "unknown_false_accepted": int(au.sum()), "accepted_unknown_mask": au}


def attach_quality(feature: dict[str, np.ndarray], rows: list[dict[str, Any]]) -> None:
    columns = defaultdict(list)
    for row in rows:
        for key, value in row["quality"].items(): columns[key].append(value)
    for key, values in columns.items(): feature[key] = np.asarray(values, dtype=float)


def write_false_accepts(rows: list[dict[str, Any]], feature: dict[str, np.ndarray], accepted: np.ndarray) -> None:
    fields = ["unknown_id", "true_species", "stratum", "predicted_species", "top1_distance", "top2_distance", "margin", "prototype_consistency", "brightness", "contrast", "blur_laplacian_variance", "min_dimension", "pixel_count", "image_path"]
    with (OUT / "fase23a_false_accepts_frozen.csv").open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=fields); writer.writeheader()
        for index in np.flatnonzero(accepted):
            row = rows[index]
            writer.writerow({"unknown_id": str(index), "true_species": row["species"], "stratum": row["stratum"],
                             "predicted_species": str(feature["selected"][index]), "top1_distance": float(feature["d1"][index]),
                             "top2_distance": float(feature["d2"][index]), "margin": float(feature["margin"][index]),
                             "prototype_consistency": float(feature["consistency"][index]), **row["quality"], "image_path": str(row["path"])})


def main() -> None:
    np.random.seed(SEED)
    OUT.mkdir(exist_ok=True)
    (OUT / "progress.txt").write_text("started\n", encoding="utf-8")
    # Calibration known comes from an already independent Fase18 subset; Fase23A is never read here until blind evaluation.
    manifest = json.loads(CAL_MANIFEST.read_text(encoding="utf-8"))
    clean = np.load(CLEAN_KNOWN, allow_pickle=True)
    by_id = {str(identifier): index for index, identifier in enumerate(clean["image_ids"])}
    known_rows = []
    for record in manifest["known"]:
        index = by_id[str(record["image_id"])]
        path = ROOT / "data cleaned" / record["path"]
        if not path.exists(): raise FileNotFoundError(path)
        known_rows.append({"path": path, "species": record["scientific_name"], "individual_id": record["individual_id"], "quality": quality(path), "index": index})
    (OUT / "progress.txt").write_text("known_quality_complete\n", encoding="utf-8")
    known_x = clean["embeddings"][[row["index"] for row in known_rows]].astype(np.float32)
    unknown_rows = collect_supplementary()
    for row in unknown_rows: row["quality"] = quality(row["path"])
    (OUT / "progress.txt").write_text("unknown_quality_complete\n", encoding="utf-8")
    unknown_x = load_or_embed_unknown(unknown_rows)
    (OUT / "progress.txt").write_text("unknown_embeddings_complete\n", encoding="utf-8")

    centers, names, source_samples, dispersion = build_centroids()
    known_feature, unknown_feature = features(known_x, centers, names, dispersion), features(unknown_x, centers, names, dispersion)
    attach_quality(known_feature, known_rows); attach_quality(unknown_feature, unknown_rows)

    # Quality is tested only as a pre-registered image-only gate based on known lower-tail quality.
    quality_gate = {field: float(np.percentile(known_feature[field], 5)) for field in ("blur_laplacian_variance", "contrast", "min_dimension")}
    accepted_by_d1 = unknown_feature["d1"] <= 0.6804759117215698  # historical F21 diagnostic only, not selected here
    quality_effect = {field: {"accepted_median": float(np.median(unknown_feature[field][accepted_by_d1])), "rejected_median": float(np.median(unknown_feature[field][~accepted_by_d1]))} for field in quality_gate}
    quality_supported = all(value["accepted_median"] < value["rejected_median"] for value in quality_effect.values())

    experiments: list[tuple[str, dict[str, np.ndarray], dict[str, np.ndarray], str, dict[str, float] | None]] = [
        ("A_euclidean", known_feature, unknown_feature, "distance", None),
        ("B_euclidean_margin", known_feature, unknown_feature, "margin", None),
        ("C_euclidean_quality", known_feature, unknown_feature, "distance", quality_gate if quality_supported else None),
        ("D_euclidean_margin_quality", known_feature, unknown_feature, "margin", quality_gate if quality_supported else None),
        ("E_euclidean_margin_prototype_consistency", known_feature, unknown_feature, "consistency", None),
    ]
    proto_centers, proto_labels = multiple_prototype_centers(source_samples, names)
    pk, pu = prototype_features(known_x, proto_centers, proto_labels, names, dispersion), prototype_features(unknown_x, proto_centers, proto_labels, names, dispersion)
    attach_quality(pk, known_rows); attach_quality(pu, unknown_rows)
    experiments.append(("F_multiple_prototypes_k2_margin", pk, pu, "margin", None))

    reference = np.load(ROOT / "evaluation/fase13/embeddings/reference_embeddings.npz")["embeddings"].astype(np.float32)
    for variant in ("diagonal", "shrinkage", "pca64_shrinkage"):
        kd = mahalanobis_features(known_x, centers, reference, variant)
        ud = mahalanobis_features(unknown_x, centers, reference, variant)
        kf, uf = {"d1": kd, "margin": np.full(len(kd), np.inf), "consistency": np.zeros(len(kd)), "selected": np.full(len(kd), "N/A")}, {"d1": ud, "margin": np.full(len(ud), np.inf), "consistency": np.zeros(len(ud)), "selected": np.full(len(ud), "N/A")}
        attach_quality(kf, known_rows); attach_quality(uf, unknown_rows)
        experiments.append((f"G_mahalanobis_{variant}", kf, uf, "distance", None))

    results = []
    frozen_name, frozen_rule, frozen_quality, frozen_feature = None, None, None, None
    # Registration: select the highest-KAR method satisfying calibration FAR <=5%; if tied prefer the simpler method order above.
    for name, kf, uf, mode, qgate in experiments:
        rule = select_rule(kf, uf, mode, qgate)
        outcome = metrics(kf, uf, rule, qgate)
        result = {"method": name, "score": "d1" if mode == "distance" else "d1+margin" if mode == "margin" else "d1+margin+prototype_consistency",
                  "quality_gate_used": bool(qgate), "calibration_known_images": len(kf["d1"]), "calibration_unknown_images": len(uf["d1"]),
                  "calibration_unknown_species": len(set(row["species"] for row in unknown_rows)), **rule, **{key: value for key, value in outcome.items() if key != "accepted_unknown_mask"}}
        results.append(result)
        if frozen_rule is None or (result["far_constraint_met"], result["kar"], -result["far"]) > (frozen_rule["far_constraint_met"], frozen_rule["kar"], -frozen_rule["far"]):
            frozen_name, frozen_rule, frozen_quality, frozen_feature = name, result, qgate, kf

    # Fase23A is opened only after method/rule selection. It cannot alter the frozen selection.
    f23 = np.load(F23_UNKNOWN, allow_pickle=True)
    f23_rows = []
    for index, source in enumerate(f23["paths"]):
        raw = Path(str(source)); image = ROOT / "data/unknown_open_set_v2/images/primary" / str(f23["species"][index]) / raw.name
        if not image.exists():
            candidates = list((ROOT / "data/unknown_open_set_v2/images/primary").rglob(raw.name)); image = candidates[0] if candidates else raw
        f23_rows.append({"path": image, "species": str(f23["species"][index]).replace("_", " "), "stratum": "PHASE23A_BLIND", "quality": quality(image)})
    f23_feature = features(f23["embeddings"].astype(np.float32), centers, names, dispersion)
    attach_quality(f23_feature, f23_rows)
    # Recover the matching selected feature family to avoid applying an unselected experimental representation.
    matching = next(item for item in experiments if item[0] == frozen_name)
    if frozen_name.startswith("F_multiple"):
        f23_feature = prototype_features(f23["embeddings"].astype(np.float32), proto_centers, proto_labels, names, dispersion); attach_quality(f23_feature, f23_rows)
    elif frozen_name.startswith("G_mahalanobis_"):
        variant = frozen_name.removeprefix("G_mahalanobis_")
        d = mahalanobis_features(f23["embeddings"].astype(np.float32), centers, reference, variant)
        f23_feature = {"d1": d, "margin": np.full(len(d), np.inf), "consistency": np.zeros(len(d)), "selected": np.full(len(d), "N/A")}; attach_quality(f23_feature, f23_rows)
    frozen_rule_min = {key: frozen_rule[key] for key in ("distance_threshold", "margin_threshold", "consistency_threshold")}
    blind = metrics({key: value for key, value in f23_feature.items()}, {key: value for key, value in f23_feature.items()}, frozen_rule_min, frozen_quality)
    accepted = blind["accepted_unknown_mask"]
    write_false_accepts(f23_rows, f23_feature, accepted)
    by_true, by_pred = Counter(), Counter()
    for index in np.flatnonzero(accepted):
        by_true[f23_rows[index]["species"]] += 1; by_pred[str(f23_feature["selected"][index])] += 1
    margins = {"false_accept_median": float(np.median(f23_feature["margin"][accepted])) if accepted.any() else None,
               "rejected_median": float(np.median(f23_feature["margin"][~accepted])) if (~accepted).any() else None}

    rows_out = []
    for item in results:
        rows_out.append({key: value for key, value in item.items() if key not in {"quality_gate_used"}})
    with (OUT / "calibration_experiment_results.csv").open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=list(rows_out[0])); writer.writeheader(); writer.writerows(rows_out)

    calibration_audit = {
        "protocol": "Calibration uses the four historical supplementary species physically stored in images/final; Fase23A primary is opened after freeze only.", "seed": SEED,
        "known": {"images": len(known_rows), "individuals": len(set(row["individual_id"] for row in known_rows)), "source": str(CAL_MANIFEST)},
        "unknown": {"images": len(unknown_rows), "species": dict(Counter(row["species"] for row in unknown_rows)), "strata": dict(Counter(row["stratum"] for row in unknown_rows))},
        "f23a_not_used_for_selection": True, "quality_gate": {"supported_by_calibration": quality_supported, "thresholds_from_known_p05": quality_gate, "historical_d1_check": quality_effect},
        "encoder_weights_modified": False, "threshold_release_modified": False, "dataset_modified": False,
    }
    json_dump(OUT / "calibration_manifest.json", calibration_audit)
    summary = {"baseline_fase21_euclidean_raw_auroc": 0.5990683229813665, "calibration_distance_statistics": {"known_d1": stats(known_feature["d1"]), "unknown_d1": stats(unknown_feature["d1"])},
               "experiments": results, "frozen": {"method": frozen_name, "selection_rule": "maximum calibration KAR subject to FAR <= 5%; Fase23A excluded", "parameters": frozen_rule, "quality_gate": frozen_quality},
               "fase23a_blind": {"unknown_images": len(f23_rows), "false_accepted": int(accepted.sum()), "far": float(accepted.mean()), "udr": float(1 - accepted.mean()), "by_true_species": dict(by_true), "by_predicted_catalog_species": dict(by_pred), "margin": margins,
                                  "false_accepts_csv": "fase23a_false_accepts_frozen.csv"}}
    json_dump(OUT / "summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except BaseException as error:
        import traceback
        (OUT / "failure.txt").write_text(traceback.format_exc(), encoding="utf-8")
        raise
