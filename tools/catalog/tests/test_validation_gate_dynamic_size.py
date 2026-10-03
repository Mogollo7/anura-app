"""
test_validation_gate_dynamic_size.py — Verifica que validation_gate.py YA NO depende de la
constante 41: centroid_validation debe derivarse de la consistencia interna del propio
centroid_audit (group_a_count + group_b_count == total_centroids), para cualquier N.

Prueba con:
  - 41 especies (retrofit real de Fase 13 — regresion, debe seguir comportandose igual)
  - 42 especies (sintetico, consistente -> debe dar PASS en centroid_validation)
  - 100 especies (sintetico, consistente -> debe dar PASS en centroid_validation)
  - 42 especies (sintetico, INCONSISTENTE -> debe dar FAIL, demostrando que valida
    consistencia real y no solo "es distinto de 41")
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TOOLS = ROOT / "tools" / "catalog"
OUT_DIR = ROOT / "validation" / "new_species_test" / "_gate_size_tests"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def run_gate(centroid_audit_path, metrics_path, frozen_config_path, out_path):
    result = subprocess.run(
        [sys.executable, str(TOOLS / "validation_gate.py"), "--mode", "retrofit",
         "--metrics-json", str(metrics_path),
         "--centroid-audit", str(centroid_audit_path),
         "--frozen-config", str(frozen_config_path),
         "--out", str(out_path)],
        cwd=str(ROOT), capture_output=True, text=True
    )
    print(result.stdout)
    with open(out_path, encoding="utf-8") as f:
        return json.load(f)


def make_synthetic_audit(total, group_a, group_b, path):
    data = {"total_centroids": total, "group_a_count": group_a, "group_b_count": group_b,
            "species_details": {f"Species_{i}": {"group": "A" if i < group_a else "B"} for i in range(total)}}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


REAL_METRICS = ROOT / "evaluation/fase13/final_evaluation/FASE13_FINAL_METRICS.json"
REAL_FROZEN = ROOT / "evaluation/fase13/selection/frozen_rejection_config.json"


def main():
    print("=== TEST 1: N=41 (real, retrofit Fase 13) — regresion ===")
    real_audit = ROOT / "evaluation/fase13/final_evaluation/centroid_source_audit.json"
    r1 = run_gate(real_audit, REAL_METRICS, REAL_FROZEN, OUT_DIR / "gate_n41.json")
    assert r1["steps"]["centroid_validation"] == "PASS", "FALLO: N=41 real deberia dar PASS en centroid_validation"
    print("[PASS] N=41 (real) -> centroid_validation=PASS (sin cambio de comportamiento)\n")

    print("=== TEST 2: N=42 sintetico CONSISTENTE (9+33=42) ===")
    audit42 = OUT_DIR / "synthetic_audit_42.json"
    make_synthetic_audit(42, 9, 33, audit42)
    r2 = run_gate(audit42, REAL_METRICS, REAL_FROZEN, OUT_DIR / "gate_n42.json")
    assert r2["steps"]["centroid_validation"] == "PASS", "FALLO: N=42 consistente deberia dar PASS"
    print("[PASS] N=42 (sintetico, consistente) -> centroid_validation=PASS\n")

    print("=== TEST 3: N=100 sintetico CONSISTENTE (20+80=100) ===")
    audit100 = OUT_DIR / "synthetic_audit_100.json"
    make_synthetic_audit(100, 20, 80, audit100)
    r3 = run_gate(audit100, REAL_METRICS, REAL_FROZEN, OUT_DIR / "gate_n100.json")
    assert r3["steps"]["centroid_validation"] == "PASS", "FALLO: N=100 consistente deberia dar PASS"
    print("[PASS] N=100 (sintetico, consistente) -> centroid_validation=PASS\n")

    print("=== TEST 4: N=42 sintetico INCONSISTENTE (total=42 pero 9+32=41) ===")
    audit_bad = OUT_DIR / "synthetic_audit_inconsistent.json"
    make_synthetic_audit(42, 9, 32, audit_bad)  # 9+32=41 != 42 declarado
    r4 = run_gate(audit_bad, REAL_METRICS, REAL_FROZEN, OUT_DIR / "gate_bad.json")
    assert r4["steps"]["centroid_validation"] == "FAIL", \
        "FALLO: inconsistencia interna deberia dar FAIL (esto demuestra que NO es solo '!=41')"
    print("[PASS] N=42 con inconsistencia interna -> centroid_validation=FAIL "
          "(demuestra que valida CONSISTENCIA, no una constante)\n")

    print("=" * 70)
    print("TEST VALIDATION_GATE DYNAMIC SIZE: PASS (41, 42, 100, e inconsistente todos correctos)")
    print("=" * 70)


if __name__ == "__main__":
    main()
