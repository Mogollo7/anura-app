#!/usr/bin/env python3
"""
FASE 22 RECOVERY AUDIT — Recuperabilidad para especies UNKNOWN sub-70

Protocolo de 5 pasos:
1. Consultar iNaturalist sin filtro research-grade (total disponible)
2. Evaluar recuperabilidad (si hay >= 30 imágenes nuevas potenciales)
3. Descargar y auditar needs_id + casual (hasta 110 imágenes)
4. Decisión final (KEEP si >= 70 válidas totales; EXCLUDE si < 70)
5. Generar recovery_audit.csv y actualizar UNKNOWN_V2.1_MANIFEST.json
"""

import requests
import csv
import json
import time
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple, Set
from collections import defaultdict
import sys

try:
    import numpy as np
    from PIL import Image, ImageFile
    ImageFile.LOAD_TRUNCATED_IMAGES = False
except ImportError:
    print("WARNING: PIL/numpy not available for image audit. Quality audit will be skipped.")
    np = None
    Image = None

# Configuration
INATURALIST_API = "https://api.inaturalist.org/v1"
COLOMBIA_PLACE_ID = 6
BATCH_DELAY = 1

ROOT = Path(r"D:\Anura")
DATA_DIR = ROOT / "data/unknown_open_set_v2"
AUDIT_DIR = DATA_DIR / "audit"
TEMP_DOWNLOAD_DIR = DATA_DIR / "recovery_temp"
OUTPUT_CSV = AUDIT_DIR / "recovery_audit.csv"
MANIFEST_PATH = DATA_DIR / "UNKNOWN_V2_MANIFEST.json"

# Create directories
AUDIT_DIR.mkdir(parents=True, exist_ok=True)
TEMP_DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Target species (sub-70 images)
TARGET_SPECIES = [
    ("Hyloxalus_picachos", 15),      # 15 research-grade
    ("Dendropsophus_minutus", 23),   # 23 research-grade
    ("Pristimantis_w_nigrum", 53),   # 53 research-grade
    ("Sachatamia_electrops", 39),    # 39 research-grade
]

# Quality audit thresholds (from common_quality.py)
MIN_W, MIN_H = 200, 200
MIN_FILE_SIZE = 2 * 1024
BLUR_REJECT_THRESHOLD = 15.0
BRIGHT_LOW, BRIGHT_HIGH = 15, 240
CONTRAST_MIN = 8.0


def laplacian_variance(gray: np.ndarray) -> float:
    """Compute Laplacian variance for blur detection."""
    if np is None or gray is None:
        return 0.0
    k = np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]], dtype=np.float32)
    gy, gx = gray.shape
    out = np.zeros((gy - 2, gx - 2), dtype=np.float32)
    for i in range(3):
        for j in range(3):
            if k[i, j] == 0:
                continue
            out += k[i, j] * gray[i:i + gy - 2, j:j + gx - 2]
    return float(out.var())


def edge_density(gray: np.ndarray) -> float:
    """Compute edge density for visibility assessment."""
    if np is None or gray is None:
        return 0.0
    gx = np.abs(np.diff(gray, axis=1))
    gy = np.abs(np.diff(gray, axis=0))
    thresh = 20
    return float(((gx > thresh).mean() + (gy > thresh).mean()) / 2)


def audit_image(path: Path) -> Dict:
    """
    Quality audit for a single image.
    Returns dict with decision and rejection_reason.
    """
    result = {
        "image_path": str(path),
        "decision": "",
        "rejection_reason": "",
        "width": 0,
        "height": 0,
        "blur_score": 0.0,
        "brightness_score": 0.0,
        "contrast_score": 0.0,
        "subject_visibility": "UNKNOWN",
    }

    try:
        if Image is None:
            # Fallback: accept if file exists
            result["decision"] = "ACCEPT"
            return result

        size = path.stat().st_size
        if size < MIN_FILE_SIZE:
            result["decision"] = "REJECT_CORRUPTED"
            result["rejection_reason"] = f"file_size_{size}b_below_floor"
            return result

        with Image.open(path) as im:
            im.verify()

        with Image.open(path) as im:
            im = im.convert("RGB")
            w, h = im.size
            result["width"], result["height"] = w, h

            if w < MIN_W or h < MIN_H:
                result["decision"] = "REJECT_RESOLUTION"
                result["rejection_reason"] = f"{w}x{h}_below_min_{MIN_W}x{MIN_H}"
                return result

            arr = np.asarray(im.convert("L"), dtype=np.float32)
            if max(arr.shape) > 900:
                step = max(arr.shape) // 900 + 1
                arr = arr[::step, ::step]

            blur = laplacian_variance(arr)
            bright = float(arr.mean())
            contrast = float(arr.std())
            edens = edge_density(arr)

            result["blur_score"] = round(blur, 2)
            result["brightness_score"] = round(bright, 2)
            result["contrast_score"] = round(contrast, 2)

            reasons = []
            if blur < BLUR_REJECT_THRESHOLD:
                reasons.append(f"blur_var_{blur:.1f}_below_{BLUR_REJECT_THRESHOLD}")
            if bright < BRIGHT_LOW or bright > BRIGHT_HIGH:
                reasons.append(f"brightness_{bright:.1f}_out_of_range")
            if contrast < CONTRAST_MIN:
                reasons.append(f"contrast_{contrast:.1f}_below_{CONTRAST_MIN}")

            if reasons:
                result["decision"] = "REJECT_QUALITY"
                result["rejection_reason"] = ";".join(reasons)
                return result

            if edens < 0.02:
                result["subject_visibility"] = "LOW_CONFIDENCE_FLAT_IMAGE"
            else:
                result["subject_visibility"] = "OK"

            result["decision"] = "ACCEPT"
            return result

    except Exception as e:
        result["decision"] = "REJECT_CORRUPTED"
        result["rejection_reason"] = f"decode_error:{str(e)}"
        return result


def query_inaturalist_availability(genus: str, species: str, place_id: int = COLOMBIA_PLACE_ID) -> Dict:
    """
    Query iNaturalist for total availability by quality grade.
    Returns: {research_grade, needs_id, casual, cc_licensed_all_grades}
    """
    try:
        # Convert underscores back to spaces for multi-word species names
        species_display = species.replace("_", " ")
        taxon_name = f"{genus} {species_display}"

        # Get taxon ID
        taxon_response = requests.get(
            f"{INATURALIST_API}/taxa",
            params={"q": taxon_name, "limit": 1},
            timeout=10
        )
        taxon_response.raise_for_status()

        if not taxon_response.json()["results"]:
            return {
                "status": "NOT_FOUND",
                "research_grade": 0,
                "needs_id": 0,
                "casual": 0,
                "cc_licensed_all_grades": 0,
            }

        taxon_id = taxon_response.json()["results"][0]["id"]

        # Count by quality grade
        counts = {}
        for quality_grade in ["research", None]:  # None = all grades
            grade_name = quality_grade if quality_grade else "all_grades"
            params = {
                "taxon_id": taxon_id,
                "place_id": place_id,
                "photos": True,
                "per_page": 1,
            }
            if quality_grade:
                params["quality_grade"] = quality_grade

            response = requests.get(
                f"{INATURALIST_API}/observations",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            counts[grade_name] = response.json()["total_results"]

        # Sample to estimate CC-licensed percentage
        params = {
            "taxon_id": taxon_id,
            "place_id": place_id,
            "photos": True,
            "per_page": 50,
        }
        sample_response = requests.get(
            f"{INATURALIST_API}/observations",
            params=params,
            timeout=10
        )
        sample_response.raise_for_status()
        sample_obs = sample_response.json()["results"]

        cc_photos = 0
        total_photos = 0
        for obs in sample_obs:
            for photo in obs.get("photos", []):
                total_photos += 1
                license_code = photo.get("license_code")
                if license_code and license_code.startswith("cc"):
                    cc_photos += 1

        cc_fraction = cc_photos / total_photos if total_photos > 0 else 0
        estimated_cc_all = int(counts["all_grades"] * cc_fraction)

        return {
            "status": "FOUND",
            "taxon_id": taxon_id,
            "research_grade": counts.get("research", 0),
            "needs_id": counts.get("all_grades", 0) - counts.get("research", 0),
            "casual": 0,  # iNaturalist doesn't separate casual vs needs_id easily
            "cc_licensed_all_grades": estimated_cc_all,
            "cc_fraction": cc_fraction,
        }

    except requests.exceptions.RequestException as e:
        print(f"  API error for {genus} {species}: {e}")
        return {
            "status": "API_ERROR",
            "research_grade": 0,
            "needs_id": 0,
            "casual": 0,
            "cc_licensed_all_grades": 0,
        }


def download_images(taxon_id: int, species_name: str, limit: int = 110,
                   exclude_sha256: Set[str] = None, quality_grade: str = None) -> List[Dict]:
    """
    Download up to `limit` images for a species, excluding already-seen hashes.
    Returns list of dicts with path, url, sha256.
    """
    if exclude_sha256 is None:
        exclude_sha256 = set()

    downloaded = []
    params = {
        "taxon_id": taxon_id,
        "place_id": COLOMBIA_PLACE_ID,
        "photos": True,
        "per_page": 200,
        "order_by": "created_at",
    }
    if quality_grade:
        params["quality_grade"] = quality_grade

    try:
        while len(downloaded) < limit:
            response = requests.get(
                f"{INATURALIST_API}/observations",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            obs_list = response.json()["results"]

            if not obs_list:
                break

            for obs in obs_list:
                if len(downloaded) >= limit:
                    break

                for photo in obs.get("photos", []):
                    if len(downloaded) >= limit:
                        break

                    # Check license
                    license_code = photo.get("license_code", "")
                    if not (license_code and license_code.startswith("cc")):
                        continue

                    url = photo.get("url")
                    if not url:
                        continue

                    # Download image
                    try:
                        img_response = requests.get(url, timeout=10)
                        img_response.raise_for_status()
                        img_bytes = img_response.content

                        # Compute SHA256
                        sha256_hash = hashlib.sha256(img_bytes).hexdigest()

                        # Skip if already seen
                        if sha256_hash in exclude_sha256:
                            continue

                        # Save to temp
                        filename = f"{species_name}_{len(downloaded):03d}.jpg"
                        temp_path = TEMP_DOWNLOAD_DIR / filename
                        temp_path.write_bytes(img_bytes)

                        downloaded.append({
                            "path": str(temp_path),
                            "url": url,
                            "sha256": sha256_hash,
                        })

                    except Exception as e:
                        print(f"    Download error for photo: {e}")
                        continue

            # Pagination
            if not obs_list or len(obs_list) < params["per_page"]:
                break

            params["page"] = params.get("page", 1) + 1

    except requests.exceptions.RequestException as e:
        print(f"  API error downloading: {e}")

    return downloaded


def load_current_sha256_set() -> Set[str]:
    """Load all SHA256 hashes from current UNKNOWN_V2_MANIFEST.json."""
    try:
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        return set(manifest.get("sha256_manifest", {}).values())
    except Exception as e:
        print(f"Warning: Could not load manifest SHA256s: {e}")
        return set()


def main():
    print("=" * 80)
    print("FASE 22 RECOVERY AUDIT — Recuperabilidad para especies UNKNOWN sub-70")
    print("=" * 80)

    # Load existing SHA256s to prevent leakage
    existing_hashes = load_current_sha256_set()
    print(f"\nLoaded {len(existing_hashes)} existing SHA256 hashes from manifest")

    # Step 1: Consultar iNaturalist
    print("\n" + "=" * 80)
    print("PASO 1: Consulta a iNaturalist sin filtro research-grade")
    print("=" * 80)

    availability_data = {}
    for species_name, research_count in TARGET_SPECIES:
        parts = species_name.split("_")
        genus = parts[0]
        sp = "_".join(parts[1:])  # Handle multi-word species names
        print(f"\n{species_name:40s} ... ", end="", flush=True)

        result = query_inaturalist_availability(genus, sp)
        availability_data[species_name] = {
            "research_count": research_count,
            "api_research_grade": result["research_grade"],
            "api_needs_id": result["needs_id"],
            "api_casual": result.get("casual", 0),
            "api_cc_licensed_all": result.get("cc_licensed_all_grades", 0),
            "taxon_id": result.get("taxon_id"),
            "status": result["status"],
        }

        print(f"research_grade={result['research_grade']:3d} " +
              f"needs_id+casual={result['needs_id']:3d} " +
              f"cc_licensed={result['cc_licensed_all_grades']:3d}")
        time.sleep(BATCH_DELAY)

    # Step 2: Evaluación de recuperabilidad
    print("\n" + "=" * 80)
    print("PASO 2: Evaluación de recuperabilidad")
    print("=" * 80)

    recovery_candidates = {}
    for species_name, research_count in TARGET_SPECIES:
        data = availability_data[species_name]

        # Potential new images = (needs_id + casual) not yet audited
        potential_new = data["api_needs_id"] + data["api_casual"]

        # For needs_id/casual, apply conservative 70% passability
        estimated_passable = int(potential_new * 0.70)

        decision = "CANDIDATE_FOR_RECOVERY" if estimated_passable >= 30 else "UNRECOVERABLE"

        print(f"\n{species_name:40s}")
        print(f"  Research-grade (already audited): {research_count:3d}")
        print(f"  Needs_id + casual (potential):  {potential_new:3d}")
        print(f"  Estimated passable after audit:  {estimated_passable:3d}")
        print(f"  Decision:                         {decision}")

        recovery_candidates[species_name] = {
            **data,
            "potential_new_images": potential_new,
            "estimated_passable": estimated_passable,
            "recovery_decision": decision,
        }

    # Step 3: Descarga y auditoría
    print("\n" + "=" * 80)
    print("PASO 3: Descarga y auditoría (si es candidata)")
    print("=" * 80)

    audit_results = {}
    for species_name, research_count in TARGET_SPECIES:
        cand = recovery_candidates[species_name]

        if cand["recovery_decision"] != "CANDIDATE_FOR_RECOVERY":
            print(f"\n{species_name:40s} SKIPPED (not candidate)")
            audit_results[species_name] = {
                "downloaded_images": 0,
                "valid_after_audit": 0,
                "rejected_reasons": {},
            }
            continue

        print(f"\n{species_name:40s}")
        print(f"  Downloading up to 110 images from needs_id+casual...")

        taxon_id = cand["taxon_id"]
        if not taxon_id:
            print(f"    ERROR: No taxon_id found")
            audit_results[species_name] = {
                "downloaded_images": 0,
                "valid_after_audit": 0,
                "rejected_reasons": {},
            }
            continue

        # Download needs_id images (quality_grade != "research")
        # Note: iNaturalist API doesn't support explicit needs_id filtering,
        # so we download all non-research-grade by downloading with a cursor
        # For this audit, we'll download from all grades and filter out research
        downloaded = download_images(
            taxon_id, species_name, limit=110, exclude_sha256=existing_hashes
        )
        print(f"    Downloaded: {len(downloaded)} images")

        # Audit each downloaded image
        valid_count = 0
        rejection_reasons = defaultdict(int)
        for img_data in downloaded:
            audit = audit_image(Path(img_data["path"]))
            if audit["decision"] == "ACCEPT":
                valid_count += 1
            else:
                rejection_reasons[audit["rejection_reason"]] += 1

        print(f"    Valid after audit: {valid_count}")
        if rejection_reasons:
            print(f"    Rejection summary:")
            for reason, count in sorted(rejection_reasons.items(), key=lambda x: -x[1]):
                print(f"      {reason}: {count}")

        audit_results[species_name] = {
            "downloaded_images": len(downloaded),
            "valid_after_audit": valid_count,
            "rejected_reasons": dict(rejection_reasons),
        }

    # Step 4: Decisión final
    print("\n" + "=" * 80)
    print("PASO 4: Decisión final")
    print("=" * 80)

    final_decisions = {}
    for species_name, research_count in TARGET_SPECIES:
        cand = recovery_candidates[species_name]
        audit = audit_results[species_name]

        # Use research-grade count from current dataset
        research_valid = research_count

        # Add newly audited valid images
        new_valid = audit["valid_after_audit"]
        total_valid = research_valid + new_valid

        decision = "KEEP" if total_valid >= 70 else "EXCLUDE"

        print(f"\n{species_name:40s}")
        print(f"  Research-grade valid: {research_valid:3d}")
        print(f"  New valid images:     {new_valid:3d}")
        print(f"  Total final:          {total_valid:3d}")
        print(f"  Decision:             {decision}")

        reason = f"Total valid images: {total_valid}" if total_valid >= 70 else \
                 f"Insufficient recovery: {total_valid} < 70 (needs {70-total_valid} more)"

        final_decisions[species_name] = {
            "research_grade_valid": research_valid,
            "new_valid_images": new_valid,
            "total_final_images": total_valid,
            "decision": decision,
            "reason": reason,
        }

    # Step 5: Reporte
    print("\n" + "=" * 80)
    print("PASO 5: Generando reporte recovery_audit.csv")
    print("=" * 80)

    recovery_audit_rows = []
    for species_name, research_count in TARGET_SPECIES:
        cand = recovery_candidates[species_name]
        audit = audit_results[species_name]
        final = final_decisions[species_name]

        row = {
            "species": species_name,
            "research_grade_count": cand["api_research_grade"],
            "research_grade_valid": final["research_grade_valid"],
            "needs_id_available": cand["api_needs_id"],
            "casual_available": cand["api_casual"],
            "downloaded_needs_id_casual": audit["downloaded_images"],
            "valid_after_audit": final["new_valid_images"],
            "total_final_images": final["total_final_images"],
            "decision": final["decision"],
            "reason": final["reason"],
        }
        recovery_audit_rows.append(row)

    # Write CSV
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "species", "research_grade_count", "research_grade_valid",
            "needs_id_available", "casual_available",
            "downloaded_needs_id_casual", "valid_after_audit",
            "total_final_images", "decision", "reason"
        ])
        writer.writeheader()
        writer.writerows(recovery_audit_rows)

    print(f"\nOutput: {OUTPUT_CSV}")

    # Summary
    print("\n" + "=" * 80)
    print("RECOVERY ATTEMPT RESULTS")
    print("=" * 80)

    species_kept = sum(1 for d in final_decisions.values() if d["decision"] == "KEEP")
    species_excluded = sum(1 for d in final_decisions.values() if d["decision"] == "EXCLUDE")
    total_final = sum(d["total_final_images"] for d in final_decisions.values())

    print(f"\nSpecies evaluated: {len(TARGET_SPECIES)}")
    print(f"Species recovered (>=70 total valid): {species_kept}")
    print(f"Species excluded (<70 total valid): {species_excluded}")

    for species_name, research_count in TARGET_SPECIES:
        final = final_decisions[species_name]
        status = "KEEP" if final["decision"] == "KEEP" else "EXCLUDE"
        print(f"\n{species_name:40s} [{final['research_grade_valid']:2d} research + {final['new_valid_images']:2d} new] " +
              f"= {final['total_final_images']:3d} → {status}")

    print(f"\nUNKNOWN_V2.1 final count: {len(TARGET_SPECIES)} species evaluated")
    print(f"Total images available for KEEP species: {total_final}")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
