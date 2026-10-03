"""
test_open_set_evaluation_regression.py — Verifica que run_open_set_evaluation.py, usando
artefactos VERSIONADOS (covariance_release, threshold_release), reproduce EXACTAMENTE las
metricas oficiales de FASE13_FINAL_METRICS.json (calculadas originalmente con recalculo
ad-hoc). Esto demuestra que formalizar la covarianza/threshold como artefactos no cambio
el resultado cientifico — solo la trazabilidad.
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TOOLS = ROOT / "tools" / "catalog"
OUT = ROOT / "validation" / "new_species_test" / "_test_open_set_regression.json"


def main():
    result = subprocess.run(
        [sys.executable, str(TOOLS / "run_open_set_evaluation.py"),
         "--catalog-release-manifest", str(ROOT / "visual_catalog/v1.0.0/manifest.json"),
         "--covariance-release-manifest", str(ROOT / "covariance/v1.0.0/manifest.json"),
         "--covariance-npz", str(ROOT / "covariance/v1.0.0/covariance_matrix.npz"),
         "--threshold-release-manifest", str(ROOT / "threshold/v1.0.0/manifest.json"),
         "--reference-embeddings", str(ROOT / "evaluation/fase13/embeddings/reference_embeddings.npz"),
         "--train-embeddings", str(ROOT / "evaluation/fase13/embeddings/train_embeddings.npz"),
         "--eval-embeddings", str(ROOT / "evaluation/open_set_v1/knn/knn_embeddings.npz"),
         "--eval-labels", str(ROOT / "evaluation/open_set_v1/knn/knn_open_set_results.json"),
         "--out", str(OUT)],
        cwd=str(ROOT), capture_output=True, text=True
    )
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
        raise RuntimeError("run_open_set_evaluation.py fallo")

    with open(OUT, encoding="utf-8") as f:
        reproduced = json.load(f)
    with open(ROOT / "evaluation/fase13/final_evaluation/FASE13_FINAL_METRICS.json", encoding="utf-8") as f:
        official = json.load(f)

    checks = [
        ("auroc", reproduced["metrics"]["auroc"], official["auroc_out_of_sample"]),
        ("kar", reproduced["metrics"]["kar"], official["kar_known_total"]),
        ("udr", reproduced["metrics"]["udr"], official["udr_unknown_total"]),
        ("far", reproduced["metrics"]["far"], official["far_unknown_total"]),
    ]

    all_pass = True
    for name, rep, off in checks:
        match = abs(rep - off) < 1e-6
        all_pass = all_pass and match
        print(f"  [{'PASS' if match else 'FAIL'}] {name}: reproducido={rep:.6f} vs oficial={off:.6f}")

    assert all_pass, "FALLO: la evaluacion usando artefactos versionados NO reproduce las metricas oficiales de Fase 13"

    OUT.unlink(missing_ok=True)
    print("\n" + "=" * 70)
    print("TEST OPEN SET EVALUATION REGRESSION: PASS")
    print("Usar covariance/threshold PERSISTIDOS reproduce EXACTAMENTE el resultado historico.")
    print("=" * 70)


if __name__ == "__main__":
    main()
