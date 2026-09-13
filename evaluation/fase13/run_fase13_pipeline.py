import os
import sys
import subprocess
from pathlib import Path

def run_step(step_name, script_path):
    print(f"\n==================================================", flush=True)
    print(f" EJECUTANDO: {step_name}", flush=True)
    print(f"==================================================", flush=True)
    cmd = [sys.executable, "-u", str(script_path)]
    res = subprocess.run(cmd, cwd=r"D:\Anura")
    if res.returncode != 0:
        print(f"ERROR: {step_name} falló con código {res.returncode}", flush=True)
        sys.exit(res.returncode)

def main():
    base_dir = Path(r"D:\Anura\evaluation\fase13")

    # Step 0: Pre-Audit
    run_step("0. PRE-AUDITORÍA", base_dir / "fase13_pre_audit.py")

    # Step 1: Embeddings Computation
    run_step("1. FASE A: CÓMPUTO DE EMBEDDINGS (REFERENCE & CALIBRATION)", base_dir / "fase13_compute_embeddings.py")

    # Step 2: 5-Fold Cross Validation on REFERENCE
    run_step("2. FASE B: 5-FOLD CROSS VALIDATION EN REFERENCE", base_dir / "fase13_cv_reference.py")

    # Step 3: Calibrate & Freeze on CALIBRATION
    run_step("3. FASE C & D: CALIBRACIÓN Y CONGELAMIENTO EN CALIBRATION", base_dir / "fase13_calibrate_selection.py")

    # Step 4: Final Evaluation on F3 + F4
    run_step("4. FASE E: EVALUACIÓN FINAL CIEGA EN F3 Y F4", base_dir / "fase13_final_evaluation.py")

    print("\n==================================================")
    print(" PIPELINE DE FASE 13 COMPLETADO EXITOSAMENTE ")
    print("==================================================")

if __name__ == "__main__":
    main()
