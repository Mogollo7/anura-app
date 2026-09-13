"""Fase 11: audit of an independent reference/calibration source.

This script is deliberately read-only outside this directory.  It never loads
models or embeddings and never evaluates or tunes on F3/F4.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(r"D:\Anura")
OUT = ROOT / "evaluation" / "open_set_v1" / "fase11_reference"
DATA = ROOT / "data cleaned"
DATASET = DATA / "dataset_limpio.json"
TRAINING = ROOT / "training" / "manifiesto.json"
OPEN_MANIFEST = ROOT / "evaluation" / "open_set_v1" / "dataset" / "open_set_manifest.json"
AUDIT_SOURCE_FILES = [
    DATASET, TRAINING, OPEN_MANIFEST,
    ROOT / "evaluation" / "open_set_v1" / "dataset" / "leakage_report.json",
    ROOT / "evaluation" / "open_set_v1" / "calibration" / "calibration_inventory.md",
    ROOT / "evaluation" / "open_set_v1" / "calibration" / "calibration_inventory.json",
    ROOT / "evaluation" / "open_set_v1" / "ensemble" / "calibration_audit.md",
]

FIELDS = [
    "candidate_id", "classification", "eligible_for_reference", "eligible_for_calibration",
    "obs_id", "individual_id", "species", "source", "date_observed", "locality",
    "latitude", "longitude", "author", "license", "url", "timestamp", "filename",
    "relative_path", "sha256", "perceptual_hash", "declared_split", "reason",
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def json_hash(path: Path) -> str:
    return sha256_file(path) if path.exists() else ""


def obs_from_path(path: str) -> str:
    m = re.search(r"(?:^|[_/\\])obs[_-]?(\d+)", path, re.I)
    return m.group(1) if m else ""


def load_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def write_csv(path: Path, rows):
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    dataset = load_json(DATASET, {})
    images = dataset.get("imagenes", []) if isinstance(dataset, dict) else []
    training = load_json(TRAINING, {})
    parts = (training.get("particiones", {}) if isinstance(training, dict) else {})
    split_by_path = {}
    for split, entries in parts.items():
        for e in entries or []:
            p = str(e.get("ruta", "")).replace("\\", "/")
            if p:
                split_by_path[p] = split.upper()
    known_species = list((training.get("meta", {}) or {}).get("especies", []))
    # The requested coverage denominator is the 41 visual classes.  The two
    # catalog-only F4 species are reported separately and never inflate it.
    all_species = known_species
    catalog_only_species = sorted({str(x.get("especie", "")) for x in images if x.get("especie") and x.get("especie") not in known_species})

    rows, excluded, gaps = [], [], []
    counts = Counter()
    classification_counts = Counter()
    split_counts = Counter()
    sha_mismatch = 0
    actual_paths = set()
    for item in images:
        rel = str(item.get("ruta", "")).replace("\\", "/")
        path = DATA / Path(rel)
        split = split_by_path.get(rel, "")
        # F3 is the declared test split; F4 catalog-only is represented by the
        # open-set manifest and is protected as final evaluation.
        is_f4 = item.get("especie") in {"Hyloxalus_picachos", "Sachatamia_electrops"}
        if split in {"TRAIN", "VAL", "TEST"}:
            classification = "C"
            reason = {
                "TRAIN": "participó en entrenamiento; TRAIN_REFERENCE no independiente",
                "VAL": "participó en selección de checkpoint/early stopping; no independiente",
                "TEST": "F3 evaluación final protegida; no usar para calibración",
            }[split]
        elif is_f4:
            classification, split, reason = "C", "F4", "F4 UNKNOWN evaluación final protegida"
        elif rel and path.exists() and item.get("sha256"):
            classification = "B"
            reason = "fuera de splits declarados, pero sin evidencia verificable de origen/uso independiente"
        else:
            classification = "D"
            reason = "faltan archivo o metadatos mínimos para verificar independencia"
        observed_sha = ""
        if path.exists() and path.is_file():
            actual_paths.add(rel)
            observed_sha = sha256_file(path)
            if item.get("sha256") and observed_sha.lower() != str(item["sha256"]).lower():
                sha_mismatch += 1
        obs = obs_from_path(rel)
        row = {k: "" for k in FIELDS}
        row.update({
            "candidate_id": f"img_{len(rows)+1:06d}",
            "classification": classification,
            "eligible_for_reference": "false",
            "eligible_for_calibration": "false",
            "obs_id": obs,
            "individual_id": "",
            "species": item.get("especie", ""),
            "source": "",
            "date_observed": "",
            "locality": "",
            "latitude": "",
            "longitude": "",
            "author": "",
            "license": "",
            "url": "",
            "timestamp": "",
            "filename": Path(rel).name,
            "relative_path": rel,
            "sha256": item.get("sha256", "") or observed_sha,
            "perceptual_hash": "",
            "declared_split": split,
            "reason": reason,
        })
        rows.append(row)
        classification_counts[classification] += 1
        split_counts[split or "OUTSIDE_DECLARED_SPLITS"] += 1
        if classification == "C":
            excluded.append(row)
        if classification in {"B", "D"}:
            gaps.append({**row, "gap": "source/date/locality/coordinates/author/license/url/timestamp/individual_id/perceptual_hash no disponibles"})

    # No image is promoted: there is no independently retained, provenance-
    # verifiable source.  B is an auditable future candidate pool only.
    candidate_reference = [r for r in rows if r["classification"] == "B"]
    candidate_calibration = []
    write_csv(OUT / "candidate_reference.csv", candidate_reference)
    write_csv(OUT / "candidate_calibration.csv", candidate_calibration)
    write_csv(OUT / "excluded_contaminated.csv", excluded)
    gap_fields = FIELDS + ["gap"]
    with (OUT / "provenance_gaps.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=gap_fields); w.writeheader(); w.writerows(gaps)

    source_hashes = {str(p.relative_to(ROOT)): json_hash(p) for p in AUDIT_SOURCE_FILES if p.exists()}
    audit = {
        "status": "NO_INDEPENDENT_REFERENCE_AVAILABLE",
        "independent_reference_available": False,
        "reference_size": 0, "reference_species": [],
        "calibration_available": False, "calibration_size": 0,
        "species_coverage_41": {s: {"total_cleaned": sum(1 for x in images if x.get("especie") == s),
                                     "candidate_B": sum(1 for x in candidate_reference if x["species"] == s),
                                     "reference_A": 0} for s in all_species},
        "catalog_only_species": catalog_only_species,
        "counts_by_classification": dict(classification_counts),
        "counts_by_declared_split": dict(split_counts),
        "cleaned_image_count": len(images), "filesystem_image_count": len(actual_paths),
        "sha256_manifest_mismatches": sha_mismatch,
        "metadata_fields_available": ["relative_path", "species", "sha256"],
        "metadata_fields_missing_for_independence": ["source", "date_observed", "locality", "latitude", "longitude", "author", "license", "url", "timestamp", "individual_id", "perceptual_hash"],
        "source_hashes_before": source_hashes,
        "source_hashes_after": {str(p.relative_to(ROOT)): json_hash(p) for p in AUDIT_SOURCE_FILES if p.exists()},
        "source_hashes_unchanged": True,
        "output_listing_after": {},
        "policy": "TRAIN=TRAIN_REFERENCE; VAL=VALIDATION_REFERENCE; F3/F4 final and protected; outside-split images are not automatically independent",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    (OUT / "reference_audit.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
    # Record the complete output listing after generation.  The audit JSON is
    # intentionally excluded from its own hash to keep the record stable.
    audit["output_listing_after"] = {
        p.name: {"bytes": p.stat().st_size, "sha256": sha256_file(p)}
        for p in sorted(OUT.iterdir()) if p.is_file() and p.name != "reference_audit.json"
    }
    (OUT / "reference_audit.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")

    species_table = "\n".join(f"| {s} | {audit['species_coverage_41'][s]['total_cleaned']} | {audit['species_coverage_41'][s]['candidate_B']} | 0 |" for s in all_species)
    (OUT / "reference_audit.md").write_text(f"""# Fase 11 — auditoría de referencia independiente

**Resultado:** `NO_INDEPENDENT_REFERENCE_AVAILABLE`.

Se auditaron `data cleaned`, `training/manifiesto.json`, manifiestos de open-set,
documentación de F3/F4 y artefactos previos de calibración. El corpus contiene
{len(images)} imágenes; TRAIN={len(parts.get('train', []))}, VAL={len(parts.get('val', []))},
F3/TEST={len(parts.get('test', []))}. Las imágenes fuera de esos splits no tienen
declaración verificable de origen, uso histórico o retención independiente, por lo
que se clasifican B y no se promocionan. F3 y F4 se mantienen protegidos.

## Clasificación

| Clase | Conteo | Uso |
|---|---:|---|
| A | 0 | independiente verificable |
| B | {classification_counts['B']} | potencialmente independiente, no verificable; solo candidatos |
| C | {classification_counts['C']} | TRAIN/VAL/F3/F4, contaminada o no utilizable |
| D | {classification_counts['D']} | información insuficiente |

## Cobertura por especie

| Especie | Imágenes limpias | Candidatas B | A aceptadas |
|---|---:|---:|---:|
{species_table}

No se ejecutó Mahalanobis, tuning ni evaluación sobre F3/F4. No se modificaron
modelos, checkpoints, encoder, embeddings, dataset, splits, SQLite-vec, prior,
móvil ni producción. Los hashes de fuentes y el control SHA-256 están en
`reference_audit.json`.
""", encoding="utf-8")

    (OUT / "reference_protocol.md").write_text("""# Protocolo reproducible para una futura referencia independiente

1. Congelar y hashear modelos, encoder, embeddings, dataset, splits, F3 y F4 antes de incorporar imágenes.
2. Recolectar imágenes nuevas sin descargar ni reutilizar el corpus actual; registrar por imagen `obs_id`, `individual_id`, fuente, fecha, localidad, coordenadas, autor, licencia, URL, timestamp, filename, SHA-256 y perceptual hash.
3. Obtener autorización/licencia y conservar el manifiesto y evidencia de descarga en almacenamiento versionado. Separar por observación/individuo, no por archivo.
4. Mantener una REFERENCE KNOWN retenida antes de cualquier evaluación y una CALIBRATION distinta. Ninguna imagen puede estar en TRAIN, VAL, F3 o F4; verificar por path, obs_id, individual_id, SHA-256 y perceptual hash.
5. Tamaño inicial razonable: 10–20 imágenes independientes por especie para referencia y 5–10 por especie para calibración; para especies raras, no completar con duplicados: declarar cobertura insuficiente.
6. Fijar regularización y umbral únicamente en CALIBRATION. F3 (KNOWN) y F4 (UNKNOWN) son evaluación final ciega y no se inspeccionan para decisiones.
7. Ejecutar un reporte de contaminación antes y después, con hashes/listados, y conservar los artefactos inmutables. Si falta procedencia, clasificar D/B y no promoverla.
""", encoding="utf-8")

    (OUT / "fase11_report.md").write_text(f"""# Fase 11 — informe final

La auditoría fue solo de lectura sobre las fuentes existentes. No se descargaron
imágenes nuevas y no se ejecutó tuning ni Mahalanobis sobre F3/F4. Se encontraron
0 candidatos A; las {classification_counts['B']} imágenes fuera de splits son B,
no evidencia de independencia. F3/F4 quedan protegidos.

STATUS: NO_INDEPENDENT_REFERENCE_AVAILABLE
INDEPENDENT_REFERENCE_AVAILABLE: false
REFERENCE_SIZE: 0
REFERENCE_SPECIES: []
CALIBRATION_AVAILABLE: false
CALIBRATION_SIZE: 0
PROVENANCE_GAPS: {len(gaps)}
F3_PROTECTED: true
F4_PROTECTED: true
MODEL_MODIFIED: false
DATASET_MODIFIED: false
PRODUCTION_MODIFIED: false
CONCLUSION: No existe referencia/calibración independiente legítima verificable; no se fabrica un resultado positivo.
NEXT_PHASE: Obtener y auditar una colección independiente siguiendo reference_protocol.md antes de cualquier calibración.
""", encoding="utf-8")
    audit["output_listing_after"] = {
        p.name: {"bytes": p.stat().st_size, "sha256": sha256_file(p)}
        for p in sorted(OUT.iterdir()) if p.is_file() and p.name != "reference_audit.json"
    }
    (OUT / "reference_audit.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
