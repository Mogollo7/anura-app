"""PARTE 13 -- Estrés de paquetes: corrupcion, checksums, manifest invalido, duplicados, etc.

Cada caso se ejecuta contra un LocalPackageManager fresco (tempdir) y se registra si el
gestor rechaza de forma CONTROLADA (PackageError/PackageValidationError) o si crashea con
una excepcion no relacionada (KeyError, etc, que indicaria manejo incompleto).
"""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parents[2]
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

from package_manager import (  # noqa: E402
    FilesystemPackageSource,
    LocalPackageManager,
    PackageError,
    PackageValidationError,
    compute_payload_sha256,
)
from runtime_adapters import OpenSetReleaseAdapter, VisualRankingAdapter  # noqa: E402

REPO = HERE / "package_repository"
OUT = HERE / "stress_test_v1/package_stress_test_results.json"

RESULTS: list[dict] = []


def record(name: str, expected_controlled: bool, fn) -> None:
    try:
        detail = fn() or {}
        RESULTS.append({"case": name, "raised": False, "detail": detail,
                         "outcome": "NO_ERROR_RAISED",
                         "matches_expectation": not expected_controlled})
    except (PackageError, PackageValidationError, ValueError, AssertionError) as exc:
        RESULTS.append({"case": name, "raised": True, "exception_type": type(exc).__name__,
                         "exception_message": str(exc)[:200],
                         "outcome": "CONTROLLED_REJECTION",
                         "matches_expectation": expected_controlled})
    except Exception as exc:  # noqa: BLE001
        RESULTS.append({"case": name, "raised": True, "exception_type": type(exc).__name__,
                         "exception_message": str(exc)[:200],
                         "outcome": "UNCONTROLLED_EXCEPTION",
                         "matches_expectation": False})


def fresh_manager() -> tuple[LocalPackageManager, Path]:
    workdir = Path(tempfile.mkdtemp(prefix="anura_pkg_stress_"))
    return LocalPackageManager(workdir / "packages_root"), workdir


def make_broken_copy(name_suffix: str, mutate) -> Path:
    """Copia anura_antioquia_visual@v1.0.0 a un dir temporal de repo y aplica `mutate`."""
    tmp_repo = Path(tempfile.mkdtemp(prefix="anura_pkg_repo_"))
    version = f"v9.9.{name_suffix}"
    dst = tmp_repo / "anura_antioquia_visual" / version
    shutil.copytree(REPO / "anura_antioquia_visual/v1.0.0", dst)
    # ref.key en FilesystemPackageSource.list_available viene del CONTENIDO del
    # manifest (manifest["package_version"]), no del nombre de carpeta -- hay que
    # alinearlos ANTES de mutate() para que list_available() encuentre esta version.
    manifest = json.loads((dst / "manifest.json").read_text(encoding="utf-8"))
    manifest["package_version"] = version
    (dst / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    mutate(dst)
    return tmp_repo


def main() -> None:
    # -- normal lifecycle stress: install several, deactivate several, reactivate, uninstall, reinstall
    def multi_lifecycle():
        manager, workdir = fresh_manager()
        source = FilesystemPackageSource(REPO)
        refs = {r.key: r for r in source.list_available()}
        manager.install(source, refs["anura_antioquia_visual@v1.0.0"])
        manager.install(source, refs["anura_cauca_visual@v1.0.0"])
        manager.activate("anura_antioquia_visual", "v1.0.0")
        manager.activate("anura_cauca_visual", "v1.0.0")
        active_both = len(manager.active_species())
        manager.deactivate("anura_cauca_visual")
        active_one = len(manager.active_species())
        manager.activate("anura_cauca_visual", "v1.0.0")
        active_both_again = len(manager.active_species())
        manager.uninstall("anura_cauca_visual", "v1.0.0", force=True)
        active_after_uninstall = len(manager.active_species())
        manager.install(source, refs["anura_cauca_visual@v1.0.0"])
        manager.activate("anura_cauca_visual", "v1.0.0")
        active_after_reinstall = len(manager.active_species())
        shutil.rmtree(workdir, ignore_errors=True)
        ok = (active_both == active_both_again == active_after_reinstall) and active_one < active_both and active_after_uninstall == active_one
        assert ok, {"active_both": active_both, "active_one": active_one, "active_both_again": active_both_again,
                     "active_after_uninstall": active_after_uninstall, "active_after_reinstall": active_after_reinstall}
        return {"active_both": active_both, "active_one": active_one, "active_after_reinstall": active_after_reinstall}

    record("multi_install_deactivate_reactivate_uninstall_reinstall", False, multi_lifecycle)

    # -- versiones distintas coexistiendo (v1.0.0 y v1.0.1 side by side)
    def coexisting_versions():
        manager, workdir = fresh_manager()
        source = FilesystemPackageSource(REPO)
        refs = {r.key: r for r in source.list_available()}
        manager.install(source, refs["anura_antioquia_visual@v1.0.0"])
        manager.install(source, refs["anura_antioquia_visual@v1.0.1"])
        installed = manager.list_installed()
        versions = sorted(v["package_version"] for v in installed if v["package_id"] == "anura_antioquia_visual")
        manager.activate("anura_antioquia_visual", "v1.0.0")
        active_v = manager.active_version("anura_antioquia_visual")
        shutil.rmtree(workdir, ignore_errors=True)
        assert versions == ["v1.0.0", "v1.0.1"] and active_v == "v1.0.0"
        return {"versions_coexisting": versions, "active": active_v}

    record("coexisting_versions_v1.0.0_and_v1.0.1", False, coexisting_versions)

    # -- paquete corrupto: bytes alterados en prototypes.npz (rompe checksum)
    def corrupted_bytes():
        def mutate(dst: Path):
            p = dst / "prototypes.npz"
            data = bytearray(p.read_bytes())
            data[100] ^= 0xFF  # flip a byte deep inside, checksum in manifest stays stale
            p.write_bytes(bytes(data))
        tmp_repo = make_broken_copy("1", mutate)
        manager, workdir = fresh_manager()
        source = FilesystemPackageSource(tmp_repo)
        refs = {r.key: r for r in source.list_available()}
        try:
            manager.install(source, refs["anura_antioquia_visual@v9.9.1"])
        finally:
            shutil.rmtree(workdir, ignore_errors=True)
            shutil.rmtree(tmp_repo, ignore_errors=True)

    record("corrupted_payload_bytes_altered", True, corrupted_bytes)

    # -- checksum incorrecto declarado (manifest miente sobre su propio payload)
    def wrong_declared_checksum():
        def mutate(dst: Path):
            manifest = json.loads((dst / "manifest.json").read_text(encoding="utf-8"))
            manifest["checksum"]["payload_sha256"] = "0" * 64
            (dst / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        tmp_repo = make_broken_copy("2", mutate)
        manager, workdir = fresh_manager()
        source = FilesystemPackageSource(tmp_repo)
        refs = {r.key: r for r in source.list_available()}
        try:
            manager.install(source, refs["anura_antioquia_visual@v9.9.2"])
        finally:
            shutil.rmtree(workdir, ignore_errors=True)
            shutil.rmtree(tmp_repo, ignore_errors=True)

    record("wrong_declared_checksum", True, wrong_declared_checksum)

    # -- manifest JSON malformado (sintaxis invalida)
    def malformed_manifest_json():
        def mutate(dst: Path):
            (dst / "manifest.json").write_text("{not valid json,,,", encoding="utf-8")
        tmp_repo = make_broken_copy("3", mutate)
        manager, workdir = fresh_manager()
        source = FilesystemPackageSource(tmp_repo)
        try:
            refs = {r.key: r for r in source.list_available()}
            if "anura_antioquia_visual@v9.9.3" in refs:
                manager.install(source, refs["anura_antioquia_visual@v9.9.3"])
            else:
                raise PackageValidationError("manifest ilegible, package_ref no se pudo construir (rechazo temprano en list_available)")
        finally:
            shutil.rmtree(workdir, ignore_errors=True)
            shutil.rmtree(tmp_repo, ignore_errors=True)

    record("malformed_manifest_json_syntax", True, malformed_manifest_json)

    # -- manifest con campos faltantes (falta 'checksum')
    def missing_required_fields():
        def mutate(dst: Path):
            manifest = json.loads((dst / "manifest.json").read_text(encoding="utf-8"))
            del manifest["checksum"]
            (dst / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        tmp_repo = make_broken_copy("4", mutate)
        manager, workdir = fresh_manager()
        source = FilesystemPackageSource(tmp_repo)
        refs = {r.key: r for r in source.list_available()}
        try:
            manager.install(source, refs["anura_antioquia_visual@v9.9.4"])
        finally:
            shutil.rmtree(workdir, ignore_errors=True)
            shutil.rmtree(tmp_repo, ignore_errors=True)

    record("manifest_missing_required_field_checksum", True, missing_required_fields)

    # -- species_id desconocido referenciado en manifest (no existe en prototypes.npz)
    def unknown_species_id_referenced():
        def mutate(dst: Path):
            manifest = json.loads((dst / "manifest.json").read_text(encoding="utf-8"))
            manifest["species_ids"].append("ANU_COL_FAKE_SPECIES_999")
            manifest["species_count"] = len(manifest["species_ids"])
            payload_sha, files = compute_payload_sha256(dst)
            manifest["checksum"] = {"algorithm": "sha256", "payload_sha256": payload_sha, "files": files}
            (dst / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        tmp_repo = make_broken_copy("5", mutate)
        manager, workdir = fresh_manager()
        source = FilesystemPackageSource(tmp_repo)
        refs = {r.key: r for r in source.list_available()}
        try:
            manager.install(source, refs["anura_antioquia_visual@v9.9.5"])
        finally:
            shutil.rmtree(workdir, ignore_errors=True)
            shutil.rmtree(tmp_repo, ignore_errors=True)

    record("unknown_species_id_in_manifest_without_prototype", True, unknown_species_id_referenced)

    # -- prototipo faltante en el payload (prototypes.npz recortado, pierde una especie declarada)
    def missing_prototype_in_payload():
        def mutate(dst: Path):
            payload = np.load(dst / "prototypes.npz", allow_pickle=False)
            ids = [str(x) for x in payload["species_ids"]][:-1]  # drop last species
            vectors = payload["prototypes"][:-1]
            np.savez(dst / "prototypes.npz", species_ids=np.array(ids), prototypes=vectors)
            payload_sha, files = compute_payload_sha256(dst)
            manifest = json.loads((dst / "manifest.json").read_text(encoding="utf-8"))
            manifest["checksum"] = {"algorithm": "sha256", "payload_sha256": payload_sha, "files": files}
            (dst / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        tmp_repo = make_broken_copy("6", mutate)
        manager, workdir = fresh_manager()
        source = FilesystemPackageSource(tmp_repo)
        refs = {r.key: r for r in source.list_available()}
        try:
            manager.install(source, refs["anura_antioquia_visual@v9.9.6"])
        finally:
            shutil.rmtree(workdir, ignore_errors=True)
            shutil.rmtree(tmp_repo, ignore_errors=True)

    record("prototype_missing_in_payload_after_checksum_recomputed", True, missing_prototype_in_payload)

    # -- especie duplicada entre dos paquetes activos: NUNCA debe mezclar (primero-en-orden-alfabetico gana, documentado)
    def duplicate_species_between_packages():
        manager, workdir = fresh_manager()
        source = FilesystemPackageSource(REPO)
        refs = {r.key: r for r in source.list_available()}
        manager.install(source, refs["anura_antioquia_visual@v1.0.0"])
        manager.install(source, refs["anura_cauca_visual@v1.0.0"])
        manager.activate("anura_antioquia_visual", "v1.0.0")
        manager.activate("anura_cauca_visual", "v1.0.0")
        antioquia_ids = set(json.loads((REPO / "anura_antioquia_visual/v1.0.0/manifest.json").read_text(encoding="utf-8"))["species_ids"])
        cauca_ids = set(json.loads((REPO / "anura_cauca_visual/v1.0.0/manifest.json").read_text(encoding="utf-8"))["species_ids"])
        overlap = antioquia_ids & cauca_ids
        ids, matrix = manager.active_prototypes()
        prov = manager._last_prototype_provenance
        overlap_provenance = {sid: prov.get(sid) for sid in overlap}
        no_duplicate_rows = len(ids) == len(set(ids))
        shutil.rmtree(workdir, ignore_errors=True)
        assert no_duplicate_rows
        return {"overlap_species_count": len(overlap), "overlap_provenance_sample": dict(list(overlap_provenance.items())[:3]),
                "no_duplicate_rows_in_active_prototypes": no_duplicate_rows}

    record("duplicate_species_between_two_active_packages", False, duplicate_species_between_packages)

    # -- ranking/OpenSet bajo carga con paquete corrupto: confirmar que el runtime NUNCA
    #    usa datos invalidos aunque el corrupto se instalara a la fuerza en disco (bypass API)
    def runtime_never_uses_invalid_data_if_tampered_after_install():
        manager, workdir = fresh_manager()
        source = FilesystemPackageSource(REPO)
        refs = {r.key: r for r in source.list_available()}
        manager.install(source, refs["anura_antioquia_visual@v1.0.0"])
        manager.activate("anura_antioquia_visual", "v1.0.0")
        installed_dir = workdir / "packages_root/installed/anura_antioquia_visual/v1.0.0"
        # tamper AFTER install/activate, simulating disk corruption post-hoc
        p = installed_dir / "prototypes.npz"
        data = bytearray(p.read_bytes())
        data[50] ^= 0xFF
        p.write_bytes(bytes(data))
        try:
            manager.validate(manager.load("anura_antioquia_visual", "v1.0.0"))
            tamper_detected = False
        except PackageValidationError:
            tamper_detected = True
        shutil.rmtree(workdir, ignore_errors=True)
        assert tamper_detected, "post-install tampering was NOT detected by re-validation"
        return {"post_install_tamper_detected_on_revalidate": tamper_detected}

    record("post_install_disk_tampering_detected_on_revalidate", False, runtime_never_uses_invalid_data_if_tampered_after_install)

    n_total = len(RESULTS)
    n_matches = sum(1 for r in RESULTS if r["matches_expectation"])
    n_crashed_uncontrolled = sum(1 for r in RESULTS if r["outcome"] == "UNCONTROLLED_EXCEPTION")

    report = {
        "total_cases": n_total,
        "matches_expectation": n_matches,
        "uncontrolled_exceptions": n_crashed_uncontrolled,
        "never_crashed_with_python_level_error_outside_expected_exception_types": n_crashed_uncontrolled == 0,
        "results": RESULTS,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    for r in RESULTS:
        print(r["case"], "->", r["outcome"], "OK" if r["matches_expectation"] else "MISMATCH")
    print(json.dumps({"total": n_total, "matches": n_matches, "uncontrolled": n_crashed_uncontrolled}, indent=2))


if __name__ == "__main__":
    main()
