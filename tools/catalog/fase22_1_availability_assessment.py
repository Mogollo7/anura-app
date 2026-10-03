#!/usr/bin/env python3
"""
FASE 22.1 — Availability Assessment Phase
Pre-evaluates 20-30 candidate species using iNaturalist API
Filters candidates by estimated_usable_images >= 85
Outputs: species_candidate_availability.csv
"""

import requests
import csv
import json
import time
from pathlib import Path
from typing import List, Dict, Tuple
from collections import defaultdict
import sys

# Configuration
INATURALIST_API = "https://api.inaturalist.org/v1"
COLOMBIA_PLACE_ID = 6  # iNaturalist place_id for Colombia
BATCH_DELAY = 1  # seconds between API calls to respect rate limits
OUTPUT_DIR = Path("D:/Anura/data/unknown_open_set_v2/candidates")
OUTPUT_CSV = OUTPUT_DIR / "species_candidate_availability.csv"

# Known species from registry (to exclude from candidates)
KNOWN_SPECIES = {
    "Aromobates_haematodactylus",
    "Boana_boans", "Boana_cinerascens", "Boana_lanciformis", "Boana_platanera",
    "Boana_pugnax", "Boana_punctata", "Boana_rosenbergi", "Boana_xerophylla",
    "Rhinella_marina", "Rhinella_granulosa", "Rhinella_margaritifer",
    "Craugastor_fitzingeri",
    "Dendrobates_lehmanni", "Phyllomedusa_azurea", "Phyllomedusa_vaillantii",
    "Hyloscirtus_larinopygius",
    "Pithecopus_hypochondrialis",
    "Engystomops_coloradorum",
    "Leptodactylus_colombiensis", "Leptodactylus_pentadactylus",
}

# Already have as UNKNOWN (from Fase 22)
EXISTING_UNKNOWN = {
    "Hyloxalus_picachos",  # historical
    "Sachatamia_electrops",  # historical
    "Dendropsophus_labialis",
    "Dendropsophus_minutus",
    "Pristimantis_w_nigrum",
    "Pristimantis_nervicus",  # ← NEEDS REPLACEMENT (<70 images)
    "Rhinella_marina",  # already here!
    "Leptodactylus_fragilis",
    "Boana_geographica",  # ← NEEDS REPLACEMENT (<70 images)
    "Smilisca_phaeota",
    "Espadarana_prosoblepon",
}

# Target candidates for replacement
REPLACEMENT_NEEDED = {
    "Boana_geographica": "SAME_GENUS",  # Boana (8 known + need new)
    "Pristimantis_nervicus": "SAME_GENUS",  # Pristimantis (11 known)
}

# Candidate species to evaluate (20-30 total)
# Prioritize: SAME_GENUS > SAME_FAMILY > DIFFERENT_FAMILY
CANDIDATES_TO_EVALUATE = [
    # SAME_GENUS replacements for Boana_geographica (Hylidae/Boana)
    ("Boana_albifrons", "SAME_GENUS"),
    ("Boana_aurantiaca", "SAME_GENUS"),
    ("Boana_barnesi", "SAME_GENUS"),
    ("Boana_boliviana", "SAME_GENUS"),
    ("Boana_calypsa", "SAME_GENUS"),
    ("Boana_chrysoscelis", "SAME_GENUS"),
    ("Boana_dentium", "SAME_GENUS"),
    ("Boana_dimidiata", "SAME_GENUS"),
    ("Boana_faber", "SAME_GENUS"),
    ("Boana_granosa", "SAME_GENUS"),
    ("Boana_leptolineata", "SAME_GENUS"),
    ("Boana_parviceps", "SAME_GENUS"),
    ("Boana_picturata", "SAME_GENUS"),
    ("Boana_raniceps", "SAME_GENUS"),
    ("Boana_thalassina", "SAME_GENUS"),

    # SAME_GENUS replacements for Pristimantis_nervicus (Craugastoridae/Pristimantis)
    ("Pristimantis_achatinus", "SAME_GENUS"),
    ("Pristimantis_altamazonicus", "SAME_GENUS"),
    ("Pristimantis_brevirostris", "SAME_GENUS"),
    ("Pristimantis_caryophyllaceus", "SAME_GENUS"),
    ("Pristimantis_devillei", "SAME_GENUS"),
    ("Pristimantis_elegans", "SAME_GENUS"),
    ("Pristimantis_erythropleura", "SAME_GENUS"),
    ("Pristimantis_maculatus", "SAME_GENUS"),
    ("Pristimantis_occultator", "SAME_GENUS"),
    ("Pristimantis_platydactylus", "SAME_GENUS"),
    ("Pristimantis_risor", "SAME_GENUS"),
]


def clean_species_name(name: str) -> str:
    """Normalize species name (underscores to spaces, first letter only capitalized)."""
    return name.replace("_", " ").title()


def query_inaturalist_species(genus: str, species: str, place_id: int = COLOMBIA_PLACE_ID) -> Dict:
    """
    Query iNaturalist for species observations.
    Returns: {observed, with_photos, with_cc_license, estimated_individuals}
    """
    try:
        # Construct search query
        taxon_name = f"{genus} {species}"

        # Step 1: Get taxon ID
        taxon_response = requests.get(
            f"{INATURALIST_API}/taxa",
            params={"q": taxon_name, "limit": 1},
            timeout=10
        )
        taxon_response.raise_for_status()

        if not taxon_response.json()["results"]:
            return {
                "status": "NOT_FOUND",
                "observed": 0,
                "with_photos": 0,
                "with_cc_license": 0,
                "estimated_individuals": 0,
            }

        taxon_id = taxon_response.json()["results"][0]["id"]

        # Step 2: Query observations in Colombia
        obs_response = requests.get(
            f"{INATURALIST_API}/observations",
            params={
                "taxon_id": taxon_id,
                "place_id": place_id,
                "photos": True,
                "quality_grade": "research",
                "per_page": 1,
            },
            timeout=10
        )
        obs_response.raise_for_status()

        total_count = obs_response.json()["total_results"]

        if total_count == 0:
            return {
                "status": "NO_OBSERVATIONS",
                "observed": 0,
                "with_photos": 0,
                "with_cc_license": 0,
                "estimated_individuals": 0,
            }

        # Step 3: Sample observations to estimate CC license percentage
        sample_response = requests.get(
            f"{INATURALIST_API}/observations",
            params={
                "taxon_id": taxon_id,
                "place_id": place_id,
                "photos": True,
                "quality_grade": "research",
                "per_page": 50,
            },
            timeout=10
        )
        sample_response.raise_for_status()

        sample_obs = sample_response.json()["results"]

        # Count CC-licensed photos in sample
        cc_photos = 0
        total_photos = 0
        unique_individuals = set()

        for obs in sample_obs:
            user_id = obs.get("user", {}).get("id")
            if user_id:
                unique_individuals.add(user_id)

            for photo in obs.get("photos", []):
                total_photos += 1
                license_code = photo.get("license_code")
                if license_code and license_code.startswith("cc"):
                    cc_photos += 1

        # Estimate CC license percentage
        cc_fraction = cc_photos / total_photos if total_photos > 0 else 0
        estimated_cc_photos = int(total_count * cc_fraction)
        estimated_individuals = max(len(unique_individuals), int(total_count / 5))

        return {
            "status": "FOUND",
            "taxon_id": taxon_id,
            "observed": total_count,
            "with_photos": total_count,  # Assuming most have photos
            "with_cc_license": estimated_cc_photos,
            "estimated_individuals": estimated_individuals,
            "cc_fraction": cc_fraction,
        }

    except requests.exceptions.RequestException as e:
        print(f"  API error for {genus} {species}: {e}")
        return {
            "status": "API_ERROR",
            "observed": 0,
            "with_photos": 0,
            "with_cc_license": 0,
            "estimated_individuals": 0,
        }


def estimate_usable_images(cc_licensed: int) -> int:
    """
    Estimate number of usable images after quality audit.
    Assume 80-85% pass quality filters (blur, brightness, contrast, visibility, composition).
    """
    return int(cc_licensed * 0.82)


def main():
    print("FASE 22.1 — AVAILABILITY ASSESSMENT")
    print("=" * 70)

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Collect availability data
    candidates_data = []

    print(f"\nEvaluating {len(CANDIDATES_TO_EVALUATE)} candidate species...")
    print("-" * 70)

    for i, (species_name, relation) in enumerate(CANDIDATES_TO_EVALUATE, 1):
        genus, sp = species_name.replace("_", " ").split()

        print(f"[{i:2d}/{len(CANDIDATES_TO_EVALUATE)}] {species_name:40s} ({relation:20s})", end=" ... ")
        sys.stdout.flush()

        # Query iNaturalist
        result = query_inaturalist_species(genus, sp)

        usable = estimate_usable_images(result.get("with_cc_license", 0))
        status = "PASS" if usable >= 85 else "FAIL"

        print(f"[{status:4s}] obs={result['observed']:4d} cc_lic={result['with_cc_license']:3d} est_usable={usable:3d}")

        candidates_data.append({
            "species": species_name,
            "genus": genus,
            "family": None,  # Will be filled from registry if needed
            "taxon_id": result.get("taxon_id", None),
            "relation_to_known": relation,
            "available_observations": result["observed"],
            "available_images": result["with_photos"],
            "cc_license_images": result["with_cc_license"],
            "estimated_individuals": result.get("estimated_individuals", 0),
            "estimated_usable_images": usable,
            "quality_grade_distribution": "not_queried",
            "candidate_status": "PASS" if usable >= 85 else "FAIL_LOW_AVAILABILITY",
            "rejection_reason": None if usable >= 85 else f"estimated_usable_images={usable} < 85",
        })

        time.sleep(BATCH_DELAY)

    # Write CSV
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "species", "genus", "family", "taxon_id",
            "relation_to_known", "available_observations", "available_images",
            "cc_license_images", "estimated_individuals", "estimated_usable_images",
            "quality_grade_distribution", "candidate_status", "rejection_reason"
        ])
        writer.writeheader()
        writer.writerows(candidates_data)

    # Summary
    passed = sum(1 for c in candidates_data if c["candidate_status"] == "PASS")
    print("\n" + "=" * 70)
    print(f"\nSUMMARY:")
    print(f"  Total candidates evaluated: {len(candidates_data)}")
    print(f"  Candidates PASS (>=85 usable): {passed}")
    print(f"  Candidates FAIL (<85 usable): {len(candidates_data) - passed}")
    print(f"\nOutput: {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
