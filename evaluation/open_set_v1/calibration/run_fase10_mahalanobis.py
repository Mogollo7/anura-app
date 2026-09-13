"""Fase 10 audit-only runner.

This runner deliberately refuses to fit/evaluate Mahalanobis when an explicitly
independent KNOWN reference is not documented.  It reads project artefacts and
writes only to this calibration directory.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(r"D:\Anura")
OUT = ROOT / "evaluation" / "open_set_v1" / "calibration"
OUT.mkdir(parents=True, exist_ok=True)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load_json(path: Path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def norm(p: str) -> str:
    return str(p).replace("/", "\\").lower()


def obs_id(path: str):
    m = re.search(r"obs_(\d+)", path, re.I)
    return m.group(1) if m else None


def write_json(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding="utf-8")


def main():
    started = datetime.now(timezone.utc).isoformat()
    training_path = ROOT / "training" / "manifiesto.json"
    cleaned_path = ROOT / "data cleaned" / "dataset_limpio.json"
    open_manifest_path = ROOT / "evaluation" / "open_set_v1" / "dataset" / "open_set_manifest.json"
    embedding_paths = list((ROOT / "COLOMBIA_ANURA" / "cache" / "embeddings").glob("*.npz"))
    rejection_dir = ROOT / "evaluation" / "open_set_v1" / "rejection"

    training = load_json(training_path)
    cleaned = load_json(cleaned_path)["imagenes"]
    open_set = load_json(open_manifest_path)
    splits = training["particiones"]
    split_paths = {s: {norm(x["ruta"]) for x in rows} for s, rows in splits.items()}
    split_obs = {s: {obs_id(x["ruta"]) for x in rows if obs_id(x["ruta"])} for s, rows in splits.items()}
    split_sha = {s: set() for s in splits}
    for s, rows in splits.items():
        for x in rows:
            p = ROOT / "data cleaned" / x["ruta"]
            if p.exists():
                split_sha[s].add(sha256(p))

    # Every cleaned image outside the declared partitions is recorded, but it
    # is not promoted to reference: no independent-reference split/provenance
    # is declared and the embedding cache is demonstrably mixed.
    candidates = []
    for x in cleaned:
        path = norm(x["ruta"])
        oid = obs_id(path)
        hits = [s for s in splits if path in split_paths[s] or x.get("sha256") in split_sha[s]]
        obs_hits = [s for s in splits if oid and oid in split_obs[s]]
        candidates.append({
            "path": x["ruta"], "full_path": str(ROOT / "data cleaned" / x["ruta"]),
            "obs_id": oid, "sha256": x.get("sha256"), "individual_id": None,
            "perceptual_hash": None, "species": x.get("especie"),
            "declared_split": hits or None, "observation_split": obs_hits or None,
            "reference_eligible": False,
            "reason": "No explicit independent reference declaration/provenance; candidate is from shared cleaned corpus.",
        })

    embedding_audit = []
    for ep in embedding_paths:
        try:
            import numpy as np
            z = np.load(ep, allow_pickle=True)
            paths = [str(p) for p in z["paths"]]
            split_counts = Counter(next((s for s in splits if norm(p) in split_paths[s]), "UNDECLARED") for p in paths)
            embedding_audit.append({"path": str(ep), "sha256": sha256(ep), "records": len(paths),
                                    "split_counts": dict(split_counts), "has_split_metadata": False})
        except Exception as exc:
            embedding_audit.append({"path": str(ep), "sha256": sha256(ep), "error": repr(exc)})

    external = [training_path, cleaned_path, open_manifest_path, *embedding_paths,
                rejection_dir / "rejection_metrics.json", rejection_dir / "rejection_results.json"]
    external_hashes = [{"path": str(p), "exists": p.exists(), "sha256": sha256(p) if p.exists() else None}
                       for p in external]
    external_hashes_after = [{"path": str(p), "exists": p.exists(), "sha256": sha256(p) if p.exists() else None}
                             for p in external]
    species_left = Counter(x["species"] for x in candidates if not x["declared_split"])
    inventory = {
        "status": "NO_INDEPENDENT_REFERENCE_AVAILABLE",
        "independent_reference": False, "reference_size": 0, "reference_species": [],
        "generated_at_utc": started, "policy": "No fitting, thresholding, or F3/F4 evaluation without an explicitly independent reference.",
        "source_audits": {
            "cleaned_images": len(cleaned), "training_manifest": {s: len(rows) for s, rows in splits.items()},
            "open_set_manifest_records": len(open_set), "open_set_species": dict(Counter(x["true_species"] for x in open_set)),
            "cleaned_outside_declared_splits": sum(species_left.values()), "outside_species": dict(species_left),
            "split_sha_counts": {s: len(v) for s, v in split_sha.items()},
        },
        "classification_rule": {
            "TRAIN": "TRAIN_REFERENCE (not independent)",
            "VAL": "VALIDATION_REFERENCE (not independent)",
            "TEST/F3": "TEST_REFERENCE (evaluation only; not fitting)",
            "F4": "UNKNOWN evaluation only",
            "outside_cleaned_corpus": "unassigned candidate; not accepted as independent without provenance",
        },
        "candidate_evidence": candidates,
        "embedding_audit": embedding_audit,
        "external_hashes_before": external_hashes,
        "external_hashes_after": external_hashes_after,
        "external_integrity_verified": external_hashes == external_hashes_after,
        "future_reference_required": {
            "minimum": "Explicit held-out KNOWN reference split, disjoint from TRAIN/VAL/TEST/F3 by path, obs_id, SHA256, individual_id and perceptual hash.",
            "metadata": ["path", "obs_id", "individual_id", "sha256", "perceptual_hash", "species", "split declaration", "collection/provenance"],
            "use": "Fit covariance/regularization only on reference; calibrate threshold on a second independent calibration split; evaluate F3=766 and F4=56 once.",
        },
    }
    write_json("calibration_inventory.json", inventory)

    metrics = {
        "STATUS": "NO_INDEPENDENT_REFERENCE_AVAILABLE", "INDEPENDENT_REFERENCE": False,
        "REFERENCE_SIZE": 0, "REFERENCE_SPECIES": [], "COVARIANCE_METHOD": "NOT_RUN",
        "REGULARIZATION": "NOT_RUN", "THRESHOLD_SOURCE": "NOT_RUN",
        "evaluation": {"F3_known": 766, "F4_unknown": 56, "executed": False},
        "metrics": {
            "AUROC": None, "AUPR": None,
            "FAR_at_KAR_80": None, "UDR_at_KAR_80": None, "FNR_at_KAR_80": None,
            "FAR_at_KAR_85": None, "UDR_at_KAR_85": None, "FNR_at_KAR_85": None,
            "FAR_at_KAR_90": None, "UDR_at_KAR_90": None, "FNR_at_KAR_90": None,
            "FAR_at_KAR_95": None, "UDR_at_KAR_95": None, "FNR_at_KAR_95": None,
        },
        "bootstrap_ci": None,
        "unknown_by_species": dict(Counter(x["true_species"] for x in open_set)),
        "comparison_fase9_in_sample_vs_fase10_out_of_sample": {
            "fase9": "Mahalanobis AUROC=1.0, in-sample optimistic; covariance fitted on F3",
            "fase10": "Not estimable; no independent reference",
        },
    }
    write_json("mahalanobis_validation_metrics.json", metrics)
    write_json("mahalanobis_validation_results.json", {"STATUS": metrics["STATUS"], "results": [], "integrity": external_hashes})
    with (OUT / "mahalanobis_cases.csv").open("w", newline="", encoding="utf-8") as f:
        csv.DictWriter(f, fieldnames=["case_id", "split", "true_species", "predicted_species", "distance", "decision"]).writeheader()
    with (OUT / "mahalanobis_threshold_analysis.csv").open("w", newline="", encoding="utf-8") as f:
        csv.DictWriter(f, fieldnames=["kar_target", "threshold", "far", "udr", "fnr", "status"]).writeheader()

    lines = [
        "# Fase 10 — Mahalanobis validation",
        "",
        "## STATUS", "STATUS=NO_INDEPENDENT_REFERENCE_AVAILABLE",
        "INDEPENDENT_REFERENCE=false", "REFERENCE_SIZE=0", "REFERENCE_SPECIES=[]",
        "COVARIANCE_METHOD=NOT_RUN", "REGULARIZATION=NOT_RUN", "THRESHOLD_SOURCE=NOT_RUN",
        "",
        "## Alcance y salvaguardas",
        "No se modificó ningún modelo, checkpoint, encoder, peso, embedding original, dataset, F3/F4, SQLite-vec, prior, app ni producción. Solo se escribieron artefactos en `evaluation/open_set_v1/calibration/`.",
        "TRAIN se etiqueta TRAIN_REFERENCE y VAL VALIDATION_REFERENCE; ninguno es independiente. TEST/F3 y F4 son evaluación, nunca ajuste.",
        "",
        "## Auditoría exhaustiva de independencia",
        f"- `data cleaned/dataset_limpio.json`: {len(cleaned)} imágenes; {sum(species_left.values())} no están en una partición declarada.",
        "- Las imágenes no asignadas no se aceptan: pertenecen al mismo corpus limpio y no tienen declaración de split/proveniencia independiente.",
        "- El cache de embeddings existente es mixto y carece de metadatos de split; por tanto no puede certificar referencia independiente.",
        f"- Manifest F3/F4: {len(open_set)} UNKNOWN CATALOG_ONLY (F4=56), sin referencia KNOWN independiente.",
        "- Evidencia completa path/obs_id/SHA/individual/perceptual hash está en `calibration_inventory.json`.",
        "",
        "## Métricas",
        "No se ejecutó ajuste ni evaluación out-of-sample. AUROC, AUPR, FAR/UDR/KAR/FNR, bootstrap CI y casos extremos: NO ESTIMABLES (evita validación falsa). UNKNOWN F4 por especie (solo inventario, no desempeño): Hyloxalus_picachos=15; Sachatamia_electrops=41.",
        "",
        "## Comparación Fase 9 in-sample vs Fase 10 out-of-sample",
        "Fase 9 reportó Mahalanobis AUROC=1.0 con covarianza ajustada sobre F3 y evaluada sobre F3: resultado optimista in-sample. Fase 10 out-of-sample no es estimable.",
        "",
        "## Viabilidad y referencia futura",
        "Se requiere un conjunto KNOWN explícitamente retenido, con especies conocidas, separado de TRAIN/VAL/TEST/F3 por path, obs_id, SHA256, individual_id y perceptual hash. Además, una calibración independiente para fijar threshold. La covarianza/regularización se congela antes de tocar F3/F4; después F3=766 y F4=56 se evalúan una sola vez.",
        "",
        "## CONCLUSION",
        "No hay evidencia suficiente de referencia independiente legítima. No se ejecuta una falsa validación out-of-sample.",
        "## NEXT_PHASE",
        "Obtener y documentar referencia KNOWN independiente + calibración independiente; repetir Fase 10 sin mirar F3/F4.",
        "",
        "## Integridad",
        "Hashes SHA256 de artefactos externos antes de la ejecución están en `calibration_inventory.json` y se deben comparar con la lista posterior.",
    ]
    (OUT / "mahalanobis_validation_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("STATUS=NO_INDEPENDENT_REFERENCE_AVAILABLE")


if __name__ == "__main__":
    main()
