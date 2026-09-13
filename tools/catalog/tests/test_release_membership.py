"""
test_release_membership.py — TEST 3: demuestra que el join por species_id respeta membership
por release específico, no solo "está en el registry global".

Escenario simulado (aislado, NO toca datos reales de COLOMBIA_ANURA/ANTIOQUIA ni visual_catalog/):
  - Se toma el release REAL visual_catalog_1.0.0 (41 species_ids) como referencia de "hoy".
  - Se construye un release SIMULADO visual_catalog_1.1.0 = 41 reales + 1 especie nueva
    (Sachatamia_electrops, ya conocida en el proyecto — excluida hoy del catálogo visual real,
    pero con family/genus ya documentados en taxonomia.py — no se inventa taxonomía).
  - Se construye una resolución regional simulada donde Sachatamia_electrops SÍ tiene species_id
    (como si en el futuro se hubiera re-incorporado tras pasar el validation gate).

Aserciones:
  ASSERT 1: contra visual_catalog_1.0.0 (real), Sachatamia_electrops NO debe aparecer en
            visual_classifier_scope.species_ids (debe caer en 'fuera de este release').
  ASSERT 2: contra visual_catalog_1.1.0 (simulado), Sachatamia_electrops SÍ debe aparecer en
            visual_classifier_scope.species_ids.

Esto es lo que demuestra que el problema de membership-por-release fue realmente resuelto,
no solo que el código funciona con los datos de hoy.

Uso:
    python tools/catalog/tests/test_release_membership.py
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]  # D:\Anura
TOOLS = ROOT / "tools" / "catalog"
FIXTURES = Path(__file__).resolve().parent / "fixtures"

SIMULATED_SPECIES_ID = "ANU_COL_SACH_ELE_001_SIMULATED"


def load_json(p: Path):
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def dump_json(p: Path, data):
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def build_fixtures():
    real_v100 = load_json(ROOT / "visual_catalog" / "v1.0.0" / "manifest.json")
    real_species_ids = set(real_v100["species_ids"])

    assert SIMULATED_SPECIES_ID not in real_species_ids, \
        "El ID simulado no debe coincidir con ninguno real — si esto falla, cambiar el ID simulado."

    # ── Fixture: visual_catalog_1.1.0 SIMULADO (41 reales + 1 especie nueva) ──
    v110_simulated = dict(real_v100)
    v110_simulated["catalog_release"] = "visual_catalog_1.1.0_SIMULATED_TEST"
    v110_simulated["species_ids"] = sorted(real_species_ids | {SIMULATED_SPECIES_ID})
    v110_simulated["species_count"] = len(v110_simulated["species_ids"])
    v110_simulated["status"] = "TEST_SIMULATION"
    v110_simulated["supersedes"] = "visual_catalog_1.0.0"
    dump_json(FIXTURES / "visual_catalog_v1.1.0_simulated" / "manifest.json", v110_simulated)

    # ── Fixture: paquete regional ANTIOQUIA simulado, con Sachatamia YA resuelta ──
    real_pkg = load_json(ROOT / "COLOMBIA_ANURA" / "ANTIOQUIA" / "metadata" / "package.json")
    dump_json(FIXTURES / "ANTIOQUIA_sim" / "metadata" / "package.json", real_pkg)

    real_resolution = load_json(ROOT / "COLOMBIA_ANURA" / "ANTIOQUIA" / "metadata" / "species_id_resolution.json")
    sim_resolution = json.loads(json.dumps(real_resolution))  # deep copy
    found = False
    for r in sim_resolution["resolutions"]:
        if r["scientific_name"] == "Sachatamia electrops":
            r["species_id"] = SIMULATED_SPECIES_ID
            r["resolution_status"] = "RESOLVED"
            found = True
    assert found, "Sachatamia electrops debe existir en la resolucion real de ANTIOQUIA para simular esto"
    sim_resolution["resolved_count"] += 1
    sim_resolution["unresolved_count"] -= 1
    dump_json(FIXTURES / "ANTIOQUIA_sim" / "metadata" / "species_id_resolution.json", sim_resolution)

    return real_v100


def run_build(catalog_release_label, manifest_path, colombia_root, output_dir):
    result = subprocess.run(
        [sys.executable, str(TOOLS / "build_regional_package.py"),
         "--department", "ANTIOQUIA",
         "--catalog-release", catalog_release_label,
         "--visual-catalog-manifest", str(manifest_path),
         "--colombia-anura-root", str(colombia_root),
         "--output", str(output_dir)],
        cwd=str(ROOT), capture_output=True, text=True
    )
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
        raise RuntimeError(f"build_regional_package.py fallo (exit {result.returncode})")
    return load_json(Path(output_dir) / "manifest.json")


def main():
    print("=== TEST 3: MEMBERSHIP POR RELEASE ESPECIFICO (simulacion aislada) ===\n")
    real_v100 = build_fixtures()

    colombia_root_sim = FIXTURES  # contiene ANTIOQUIA_sim/ pero build_regional_package espera {root}/{DEPT}
    # build_regional_package.py construye root/DEPARTMENT — renombramos para que calce:
    dept_alias = FIXTURES / "ANTIOQUIA"
    if dept_alias.exists():
        shutil.rmtree(dept_alias)
    shutil.copytree(FIXTURES / "ANTIOQUIA_sim", dept_alias)

    print("--- Sub-test A: contra visual_catalog_1.0.0 REAL (Sachatamia NO debe aparecer) ---")
    out_a = FIXTURES / "_out_test_a"
    result_a = run_build(
        "visual_catalog_1.0.0",
        ROOT / "visual_catalog" / "v1.0.0" / "manifest.json",
        FIXTURES, out_a
    )
    ids_a = set(result_a["visual_classifier_scope"]["species_ids"])
    assert SIMULATED_SPECIES_ID not in ids_a, \
        f"FALLO ASSERT 1: {SIMULATED_SPECIES_ID} aparecio en release 1.0.0 y NO deberia"
    print("[PASS] ASSERT 1: species_id simulado ausente en visual_catalog_1.0.0 (correcto)\n")

    print("--- Sub-test B: contra visual_catalog_1.1.0 SIMULADO (Sachatamia SI debe aparecer) ---")
    out_b = FIXTURES / "_out_test_b"
    result_b = run_build(
        "visual_catalog_1.1.0_SIMULATED_TEST",
        FIXTURES / "visual_catalog_v1.1.0_simulated" / "manifest.json",
        FIXTURES, out_b
    )
    ids_b = set(result_b["visual_classifier_scope"]["species_ids"])
    assert SIMULATED_SPECIES_ID in ids_b, \
        f"FALLO ASSERT 2: {SIMULATED_SPECIES_ID} NO aparecio en release 1.1.0 simulado y deberia"
    print("[PASS] ASSERT 2: species_id simulado presente en visual_catalog_1.1.0 simulado (correcto)\n")

    # limpieza de directorios de salida y alias (dejamos los fixtures fuente como evidencia)
    shutil.rmtree(out_a, ignore_errors=True)
    shutil.rmtree(out_b, ignore_errors=True)
    shutil.rmtree(dept_alias, ignore_errors=True)

    print("=" * 70)
    print("TEST 3 COMPLETO: PASS — membership por release especifico funciona correctamente.")
    print("El sistema NO confunde 'esta en el registry global' con 'esta en este release'.")
    print("=" * 70)


if __name__ == "__main__":
    main()
