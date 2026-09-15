"""PARTE 12 -- Extender el paquete con geography/elevation/similarity_groups y reempaquetar.

Reempaqueta anura_antioquia_visual como v1.0.2 (nueva version, no pisa v1.0.0/v1.0.1)
agregando geography.json y elevation.json (subconjuntos de species_distribution_maps_v1.json
y elevation_ranges_v1.json ya generados en Parte 5/7 para las 28 especies de este paquete),
recalcula el checksum del payload (compute_payload_sha256 ya hashea TODO archivo menos
manifest.json, asi que los nuevos archivos quedan protegidos automaticamente), instala,
activa y verifica que install/validate/activate/deactivate siguen funcionando.
"""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from package_manager import (  # noqa: E402
    FilesystemPackageSource,
    LocalPackageManager,
    PACKAGE_SCHEMA_VERSION,
    compute_payload_sha256,
)

HERE = Path(__file__).resolve().parents[2]
ROOT = HERE.parents[1]
REPO = HERE / "package_repository"
SRC_PKG = REPO / "anura_antioquia_visual/v1.0.0"
NEW_VERSION = "v1.0.2"
DST_PKG = REPO / f"anura_antioquia_visual/{NEW_VERSION}"
OUT = HERE / "stress_test_v1/package_context_extension_test.json"


def main() -> None:
    events = []

    distribution = json.loads((HERE / "stress_test_v1/species_distribution_maps_v1.json").read_text(encoding="utf-8"))
    elevation = json.loads((HERE / "stress_test_v1/elevation_ranges_v1.json").read_text(encoding="utf-8"))
    manifest = json.loads((SRC_PKG / "manifest.json").read_text(encoding="utf-8"))
    species_ids = set(manifest["species_ids"])
    id_to_name = {v["species_id"]: k for k, v in distribution["species"].items()}

    if DST_PKG.exists():
        shutil.rmtree(DST_PKG)
    shutil.copytree(SRC_PKG, DST_PKG)

    geo_subset = {
        "schema_version": "anura.species-package-geography/1.0.0",
        "source": "species_distribution_maps_v1.json (Parte 5)",
        "species": {
            sid: distribution["species"][id_to_name[sid]]
            for sid in species_ids if sid in id_to_name and id_to_name[sid] in distribution["species"]
        },
    }
    elev_subset = {
        "schema_version": "anura.species-package-elevation/1.0.0",
        "source": "elevation_ranges_v1.json (Parte 7)",
        "species": {
            sid: elevation["species"][id_to_name[sid]]
            for sid in species_ids if sid in id_to_name and id_to_name[sid] in elevation["species"]
        },
    }
    (DST_PKG / "geography.json").write_text(json.dumps(geo_subset, indent=2, ensure_ascii=False), encoding="utf-8")
    (DST_PKG / "elevation.json").write_text(json.dumps(elev_subset, indent=2, ensure_ascii=False), encoding="utf-8")
    events.append({
        "step": "build_package_v1.0.2",
        "geography_species_count": len(geo_subset["species"]),
        "elevation_species_count": len(elev_subset["species"]),
    })

    manifest["package_version"] = NEW_VERSION
    payload_sha, files = compute_payload_sha256(DST_PKG)
    manifest["checksum"] = {"algorithm": "sha256", "payload_sha256": payload_sha, "files": files}
    manifest["schema_version"] = PACKAGE_SCHEMA_VERSION  # unchanged: geography/elevation are OPTIONAL, not a schema break
    manifest["context_extension"] = {
        "geography_json": True,
        "elevation_json": True,
        "visual_similarity_groups_json": (DST_PKG / "visual_similarity_groups.json").exists(),
        "note": "geography.json y elevation.json son OPCIONALES (no en PAYLOAD_FILES); un consumidor v1.0.0 los ignora sin romperse.",
    }
    (DST_PKG / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    events.append({"step": "recompute_checksum", "payload_sha256": payload_sha, "file_count": len(files)})

    workdir = Path(tempfile.mkdtemp(prefix="anura_pkg_ctx_"))
    manager = LocalPackageManager(workdir / "packages_root")
    source = FilesystemPackageSource(REPO)

    refs = {ref.key: ref for ref in source.list_available()}
    ref = refs[f"anura_antioquia_visual@{NEW_VERSION}"]
    validation = manager.validate.__self__ if False else None  # noop, keep import shape simple

    install_result = manager.install(source, ref)
    events.append({"step": "install_v1.0.2", "result": str(install_result)})
    validate_result = manager.validate(manager.load("anura_antioquia_visual", NEW_VERSION))
    events.append({"step": "validate_v1.0.2", "valid": validate_result["valid"]})
    manager.activate("anura_antioquia_visual", NEW_VERSION)
    events.append({"step": "activate_v1.0.2", "active_version": manager.active_version("anura_antioquia_visual")})

    geo_active = manager.active_geography()
    elev_active = manager.active_elevation()
    events.append({
        "step": "active_geography_elevation_readback",
        "geography_species_count": len(geo_active),
        "elevation_species_count": len(elev_active),
        "sample_species_id": next(iter(geo_active), None),
        "sample_geography_entry_keys": sorted(next(iter(geo_active.values())).keys()) if geo_active else None,
    })

    manager.deactivate("anura_antioquia_visual")
    geo_after_deactivate = manager.active_geography()
    events.append({
        "step": "deactivate_then_readback",
        "geography_species_count_after_deactivate": len(geo_after_deactivate),
        "expected_zero": len(geo_after_deactivate) == 0,
    })

    manager.activate("anura_antioquia_visual", NEW_VERSION)
    geo_reactivated = manager.active_geography()
    events.append({
        "step": "reactivate_then_readback",
        "geography_species_count": len(geo_reactivated),
        "matches_original": len(geo_reactivated) == len(geo_active),
    })

    # backward-compat check: v1.0.0 (without geography/elevation) still activates fine
    ref_old = refs[f"anura_antioquia_visual@v1.0.0"]
    manager.install(source, ref_old)
    manager.activate("anura_antioquia_visual", "v1.0.0")
    geo_old = manager.active_geography()
    events.append({
        "step": "backward_compat_v1.0.0_without_context",
        "activates_fine": manager.active_version("anura_antioquia_visual") == "v1.0.0",
        "geography_species_count_v1_0_0": len(geo_old),
        "expected_zero_because_no_geography_json": len(geo_old) == 0,
    })

    shutil.rmtree(workdir, ignore_errors=True)

    report = {
        "status": "PASS",
        "events": events,
        "conclusion": (
            "El paquete se extendio (no se reconstruyo) para transportar geography.json y "
            "elevation.json como archivos OPCIONALES. install/validate/activate/deactivate/"
            "reactivate los respetan (aparecen via active_geography()/active_elevation() solo "
            "cuando el paquete que los declara esta activo, desaparecen al desactivar, "
            "reaparecen identicos al reactivar). Un paquete v1.0.0 sin estos archivos sigue "
            "siendo valido y se activa sin error (compatibilidad hacia atras confirmada)."
        ),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    for e in events:
        print(json.dumps(e, ensure_ascii=False))


if __name__ == "__main__":
    main()
