#!/usr/bin/env python3
"""
FASE 22.1 — Download and Audit Phase
Downloads candidate species with controlled caps and applies quality filters
"""

import os
import sys
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Mock the download phase for now - in production would use iNaturalist API
# This demonstrates the pipeline logic

candidates_to_download = [
    {"species": "Boana_albifrons", "relation": "SAME_GENUS", "replacement_for": None, "priority": 1},
    {"species": "Boana_faber", "relation": "SAME_GENUS", "replacement_for": None, "priority": 1},
    {"species": "Pristimantis_brevirostris", "relation": "SAME_GENUS", "replacement_for": None, "priority": 2},
    {"species": "Pristimantis_elegans", "relation": "SAME_GENUS", "replacement_for": None, "priority": 2},
    {"species": "Pristimantis_occultator", "relation": "SAME_GENUS", "replacement_for": None, "priority": 2},
]

replacement_targets = {
    "Boana_geographica": "SAME_GENUS",
    "Pristimantis_nervicus": "SAME_GENUS",
}

OUTPUT_DIR = Path("D:/Anura/data/unknown_open_set_v2")

def main():
    print("FASE 22.1 — DOWNLOAD AND AUDIT PHASE")
    print("=" * 70)
    print("")
    print("STATUS: This phase would download images from iNaturalist API")
    print("")
    print("Replacement strategy:")
    print("  Boana_geographica (2 images, FAIL) <-- Boana_albifrons OR Boana_faber")
    print("  Pristimantis_nervicus (3 images, FAIL) <-- Pristimantis_brevirostris, elegans, or occultator")
    print("")
    print("Pipeline steps:")
    print("  1. Query iNaturalist for each candidate")
    print("  2. Download up to 110 candidate images per species")
    print("  3. Apply quality filters (resolution, blur, brightness, contrast, visibility)")
    print("  4. Stop at 80 valid images per species")
    print("  5. Log rejections (quality, leakage, duplicates)")
    print("  6. Accept species only if >=70 valid images")
    print("  7. Auto-select replacement if primary candidate fails")
    print("")
    print("NOTE: Actual download/audit implemented as extension of fase22_download_and_audit.py")
    print("      This is a control-flow demonstration.")

if __name__ == "__main__":
    main()
