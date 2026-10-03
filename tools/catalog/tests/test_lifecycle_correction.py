"""
test_lifecycle_correction.py — Verifica que generate_species_id.py:
  1. NUNCA marca una especie nueva como DEPLOYED automaticamente (debe ser DISCOVERED).
  2. Preserva EXACTAMENTE el lifecycle_status de las 41 especies historicas (no las toca).

Uso:
    python tools/catalog/tests/test_lifecycle_correction.py
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TOOLS = ROOT / "tools" / "catalog"
OUT_DIR = ROOT / "validation" / "new_species_test"


def run(args):
    result = subprocess.run([sys.executable, str(TOOLS / "generate_species_id.py")] + args,
                             cwd=str(ROOT), capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
        raise RuntimeError("generate_species_id.py fallo")


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def main():
    print("=== TEST: regresion — 41 historicas no cambian ===")
    out_a = OUT_DIR / "_test_regression_41.json"
    run(["--source", "training/taxonomia.py",
         "--previous-registry", "taxonomy/species/species_registry.json",
         "--out", str(out_a)])

    real = load(ROOT / "taxonomy" / "species" / "species_registry.json")
    regenerated = load(out_a)
    assert real == regenerated, "FALLO: regenerar el registry historico produjo un resultado distinto"
    print("[PASS] Regenerar el registry de las 41 especies historicas es byte-identico\n")

    print("=== TEST: especie nueva inicia en DISCOVERED, no DEPLOYED ===")
    out_b = OUT_DIR / "_test_new_species_lifecycle.json"
    run(["--source", str(OUT_DIR / "fixture" / "taxonomia_v1_1_0_candidate.py"),
         "--previous-registry", "taxonomy/species/species_registry.json",
         "--out", str(out_b)])

    candidate = load(out_b)
    by_id = {s["species_id"]: s for s in candidate["species"]}

    new_species = by_id["ANU_COL_TEST_SYN_001"]
    assert new_species["visual_lifecycle_status"] == "DISCOVERED", \
        f"FALLO: especie nueva tiene status={new_species['visual_lifecycle_status']}, esperado DISCOVERED"
    print("[PASS] Especie nueva (ANU_COL_TEST_SYN_001) inicia en DISCOVERED, no DEPLOYED")

    old_species = by_id["ANU_COL_DEND_TRU_001"]
    assert old_species["visual_lifecycle_status"] == "DEPLOYED", \
        f"FALLO: especie historica cambio a status={old_species['visual_lifecycle_status']}"
    print("[PASS] Especie historica (ANU_COL_DEND_TRU_001) preserva DEPLOYED\n")

    out_a.unlink(missing_ok=True)
    out_b.unlink(missing_ok=True)

    print("=" * 60)
    print("TEST LIFECYCLE CORRECTION: PASS")
    print("=" * 60)


if __name__ == "__main__":
    main()
