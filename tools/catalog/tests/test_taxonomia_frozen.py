"""
test_taxonomia_frozen.py — Congela training/taxonomia.py contra cambios silenciosos
durante evaluaciones cientificas activas. Motivo: este archivo fue modificado
externamente en 2026-09-13 durante Fase 16, perdiendo ALIAS/canonico() (regresion real,
corregida) y agregando Hyloxalus_picachos (preservado, decision no revertida).

Este test NO impide editar taxonomia.py — impide que un cambio pase DESAPERCIBIDO.
Si el hash cambia legitimamente, actualizar FROZEN_SHA256 en este archivo explicitamente,
como parte de un commit consciente, no como efecto colateral de otra tarea.
"""
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TAXONOMIA_PATH = ROOT / "training" / "taxonomia.py"

# Hash congelado tras la correccion de 2026-09-13 (ALIAS/canonico restaurados,
# Hyloxalus_picachos preservado en ESPECIES, familia_de() fail-loud restaurado).
FROZEN_SHA256 = "97f32b8063790eef9d58ace1cb7067db33eb7ff9f0b25905edf03a0897a67fbf"


def sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def main():
    current_hash = sha256_of_file(TAXONOMIA_PATH)
    print(f"SHA256 actual de training/taxonomia.py: {current_hash}")

    # Verificacion funcional (mas importante que el hash en si): los mecanismos
    # criticos deben existir y comportarse correctamente.
    import importlib.util
    spec = importlib.util.spec_from_file_location("taxonomia", TAXONOMIA_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    checks = []
    checks.append(("hasattr canonico", hasattr(mod, "canonico")))
    checks.append(("ALIAS no vacio", len(getattr(mod, "ALIAS", {})) > 0))
    checks.append(("canonico resuelve acanthinus->achatinus",
                    getattr(mod, "canonico", lambda x: None)("Pristimantis acanthinus") == "Pristimantis_achatinus"))
    checks.append(("ESPECIES no vacio", len(mod.ESPECIES) > 0))

    try:
        mod.familia_de("__ESPECIE_INEXISTENTE_PARA_TEST__")
        checks.append(("familia_de falla ante especie desconocida (fail-loud)", False))
    except KeyError:
        checks.append(("familia_de falla ante especie desconocida (fail-loud)", True))

    all_pass = all(ok for _, ok in checks)
    for name, ok in checks:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")

    if FROZEN_SHA256 is not None and current_hash != FROZEN_SHA256:
        print(f"\n[WARNING] Hash distinto al congelado ({FROZEN_SHA256}). "
              f"Si el cambio es intencional, actualizar FROZEN_SHA256 explicitamente.")

    if not all_pass:
        print("\nRESULTADO: FAIL — mecanismos criticos de taxonomia.py rotos")
        sys.exit(1)
    print("\nRESULTADO: PASS")


if __name__ == "__main__":
    main()
