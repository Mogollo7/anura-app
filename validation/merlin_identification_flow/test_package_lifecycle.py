"""Ciclo de vida de paquete: 13 pasos obligatorios, reproducible.

El paso 7 (los centroides de un paquete desactivado dejan de participar en
Open Set) es exactamente el que fallaba antes del bugfix
DYNAMIC_REMOVE_SPECIES_FAIL.

No se pasa ninguna etiqueta al runtime: la imagen se elige por ruta y su
especie real solo se usa DESPUES para interpretar el resultado.
"""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

from package_manager import (  # noqa: E402
    FilesystemPackageSource,
    LocalPackageManager,
    PackageError,
    PackageValidationError,
)
from runtime_adapters import BioClipOnnxAdapter, OpenSetReleaseAdapter, VisualRankingAdapter  # noqa: E402

REPOSITORY = HERE / "package_repository"
PACKAGE_A = "anura_antioquia_visual"
PACKAGE_B = "anura_cauca_visual"
TRUNCATUS_ID = "ANU_COL_DEND_TRU_001"
TRUNCATUS_NAME = "Dendrobates truncatus"
IMAGE = ROOT / "data cleaned/Dendrobates_truncatus/col_obs_135615735_photo_231331908.jpg"

STEPS: list[dict] = []


def record(step: float, name: str, ok: bool, detail: dict) -> None:
    STEPS.append({"step": step, "name": name, "status": "PASS" if ok else "FAIL", **detail})
    if not ok:
        raise AssertionError(f"Paso {step} ({name}) FAIL: {detail}")


def observe(step: float, name: str, detail: dict) -> None:
    """Registra un hecho medido SIN convertirlo en PASS/FAIL del ciclo de vida.

    Se usa para separar lo que el bugfix garantiza (arquitectura de catalogo)
    de lo que NO puede garantizar (calidad del threshold Open Set congelado).
    """
    STEPS.append({"step": step, "name": name, "status": "OBSERVED", **detail})


def main() -> None:
    workdir = Path(tempfile.mkdtemp(prefix="anura_pkg_lifecycle_"))
    manager = LocalPackageManager(workdir / "packages_root")
    source = FilesystemPackageSource(REPOSITORY)
    ranking = VisualRankingAdapter()
    open_set = OpenSetReleaseAdapter()

    assert IMAGE.exists(), IMAGE
    embedding, _ = BioClipOnnxAdapter().embed_image(IMAGE)

    refs = {ref.key: ref for ref in source.list_available()}
    ref_a = refs[f"{PACKAGE_A}@v1.0.0"]
    ref_b = refs[f"{PACKAGE_B}@v1.0.0"]

    def snapshot() -> dict:
        ids = manager.active_species()
        proto_ids, matrix = manager.active_prototypes()
        prototypes = {sid: matrix[i] for i, sid in enumerate(proto_ids)}
        names = [
            item["scientific_name"]
            for sid, item in manager.active_species_metadata().items()
            if sid in set(ids)
        ]
        rows, rank_meta = ranking.rank_visual(embedding, names)
        decision, evidence = open_set.assess(embedding, active_species_ids=ids, active_prototypes=prototypes)
        rows.sort(key=lambda item: -item[1])
        return {
            "active_species_count": len(ids),
            "in_ranking": TRUNCATUS_NAME in [name for name, _ in rows],
            "ranking_top1": rows[0][0] if rows else None,
            "ranking_pool": rank_meta["candidate_pool"],
            "open_set_decision": decision,
            "open_set_score": evidence["score"],
            "nearest_species_id": evidence["nearest_species_id"],
            "active_centroid_count": evidence["active_centroid_count"],
            "truncatus_centroid_participates": TRUNCATUS_ID in prototypes,
        }

    # Contexto: B siempre instalado y activo, para que la desactivacion de A
    # no se confunda con "catalogo vacio".
    manager.install(source, ref_b)
    manager.activate(PACKAGE_B)

    # 1 -------------------------------------------------------------------
    package = manager.install(source, ref_a)
    installed = {row["package_id"] + "@" + row["package_version"] for row in manager.list_installed()}
    record(1, "install(A)", f"{PACKAGE_A}@v1.0.0" in installed,
           {"installed": sorted(installed), "species_count": len(package.species_ids),
            "payload_sha256": package.manifest["checksum"]["payload_sha256"][:16] + "..."})

    # Integridad: un payload manipulado debe ser rechazado.
    tampered = workdir / "tampered" / PACKAGE_A / "v1.0.0"
    shutil.copytree(REPOSITORY / PACKAGE_A / "v1.0.0", tampered)
    (tampered / "species.json").write_text("{\"species\": []}", encoding="utf-8")
    try:
        manager.validate(tampered)
        integrity_ok = False
    except PackageValidationError:
        integrity_ok = True
    record(1.5, "sha256 integrity rejects tampered payload", integrity_ok, {})

    # Versionado: reinstalar la misma version exacta se rechaza.
    try:
        manager.install(source, ref_a)
        duplicate_rejected = False
    except PackageError:
        duplicate_rejected = True
    # v1.0.1 convive con v1.0.0 sin sobrescribirla.
    manager.install(source, refs[f"{PACKAGE_A}@v1.0.1"])
    versions = sorted(
        row["package_version"] for row in manager.list_installed() if row["package_id"] == PACKAGE_A
    )
    record(1.6, "versioning: no silent overwrite", duplicate_rejected and versions == ["v1.0.0", "v1.0.1"],
           {"duplicate_rejected": duplicate_rejected, "versions_side_by_side": versions})

    # 2 -------------------------------------------------------------------
    activated = manager.activate(PACKAGE_A, "v1.0.0")
    record(2, "activate(A)", activated == "v1.0.0" and manager.active_version(PACKAGE_A) == "v1.0.0",
           {"active_version": activated})

    # 3 -------------------------------------------------------------------
    state = snapshot()
    record(3, "species of A appear in ranking", state["in_ranking"] is True,
           {"ranking_pool": state["ranking_pool"], "top1": state["ranking_top1"],
            "active_species_count": state["active_species_count"]})

    # 4 -------------------------------------------------------------------
    record(4, "centroids of A participate in Open Set",
           state["truncatus_centroid_participates"] and state["nearest_species_id"] == TRUNCATUS_ID
           and state["open_set_decision"] == "ESPECIE_CONOCIDA",
           {"open_set_decision": state["open_set_decision"], "score": state["open_set_score"],
            "nearest_species_id": state["nearest_species_id"],
            "active_centroid_count": state["active_centroid_count"]})
    score_active = state["open_set_score"]

    # 5 -------------------------------------------------------------------
    manager.deactivate(PACKAGE_A)
    record(5, "deactivate(A)", manager.active_version(PACKAGE_A) is None,
           {"active_packages": [p.key for p in manager.active_packages()]})

    # 6 -------------------------------------------------------------------
    off = snapshot()
    record(6, "species of A disappear from ranking", off["in_ranking"] is False,
           {"ranking_pool": off["ranking_pool"], "top1": off["ranking_top1"],
            "active_species_count": off["active_species_count"]})

    # 7 -------------------------------------------------------------------  <-- el que fallaba
    # El invariante que el bugfix GARANTIZA: el centroide de la especie
    # desactivada ya no entra en la matriz, la especie mas cercana ya no es
    # ella, y el score sube porque su centroide dejo de estar disponible.
    record(7, "centroids of A stop participating in Open Set",
           off["truncatus_centroid_participates"] is False
           and off["nearest_species_id"] != TRUNCATUS_ID
           and off["open_set_score"] > score_active,
           {"open_set_score_before_deactivation": score_active,
            "open_set_score_after_deactivation": off["open_set_score"],
            "score_increase": round(off["open_set_score"] - score_active, 4),
            "nearest_species_id": off["nearest_species_id"],
            "active_centroid_count": off["active_centroid_count"],
            "truncatus_centroid_participates": off["truncatus_centroid_participates"]})

    # Hecho medido, NO maquillado: el threshold historico (39.354) sigue
    # aceptando la imagen por el centroide de OTRA especie activa.
    observe(7.1, "decision-level outcome after deactivation (residual Open Set defect)",
            {"open_set_decision": off["open_set_decision"],
             "score": off["open_set_score"],
             "threshold": 39.35406371422803,
             "attributed_to_species_id": off["nearest_species_id"],
             "verdict": "ESPECIE_CONOCIDA persiste por un centroide AJENO, no por fuga de catalogo",
             "root_cause": "THRESHOLD_TOO_PERMISSIVE_NOT_CATALOG_LEAKAGE",
             "note": "No se recalibra el threshold (regla dura del proyecto)."})

    # Caso limite: sin ninguna especie activa no puede haber ESPECIE_CONOCIDA.
    manager.deactivate(PACKAGE_B)
    empty = snapshot()
    record(7.5, "empty active catalog -> NO_CONCLUYENTE",
           empty["active_species_count"] == 0 and empty["open_set_decision"] == "NO_CONCLUYENTE"
           and empty["open_set_score"] is None,
           {"decision": empty["open_set_decision"], "active_centroid_count": empty["active_centroid_count"]})
    manager.activate(PACKAGE_B)

    # 8 -------------------------------------------------------------------
    manager.activate(PACKAGE_A, "v1.0.0")
    record(8, "reactivate(A)", manager.active_version(PACKAGE_A) == "v1.0.0", {})

    # 9 -------------------------------------------------------------------
    back = snapshot()
    record(9, "species and centroids come back",
           back["in_ranking"] and back["nearest_species_id"] == TRUNCATUS_ID
           and abs(back["open_set_score"] - score_active) < 1e-6,
           {"score": back["open_set_score"], "score_when_first_active": score_active,
            "deterministic": abs(back["open_set_score"] - score_active) < 1e-6})

    # 10 ------------------------------------------------------------------
    removed = manager.uninstall(PACKAGE_A, force=True)
    record(10, "uninstall(A)", not manager.is_installed(PACKAGE_A),
           {"removed_versions": removed})

    # 11 ------------------------------------------------------------------
    gone = snapshot()
    local_dir_gone = not (manager.installed_dir / PACKAGE_A).exists()
    record(11, "A no longer available locally",
           local_dir_gone and not manager.is_installed(PACKAGE_A)
           and PACKAGE_A not in manager.state["packages"]
           and gone["in_ranking"] is False
           and gone["truncatus_centroid_participates"] is False,
           {"dir_removed": local_dir_gone,
            "state_json_has_package": PACKAGE_A in manager.state["packages"],
            "open_set_decision": gone["open_set_decision"]})

    # 12 ------------------------------------------------------------------
    manager.install(source, ref_a)
    manager.activate(PACKAGE_A, "v1.0.0")
    record(12, "reinstall(A)", manager.is_installed(PACKAGE_A, "v1.0.0"),
           {"active_version": manager.active_version(PACKAGE_A)})

    # 13 ------------------------------------------------------------------
    final = snapshot()
    record(13, "A works again identically",
           final["in_ranking"] and final["nearest_species_id"] == TRUNCATUS_ID
           and final["open_set_decision"] == "ESPECIE_CONOCIDA"
           and abs(final["open_set_score"] - score_active) < 1e-6,
           {"score": final["open_set_score"], "decision": final["open_set_decision"],
            "bit_identical_to_first_activation": abs(final["open_set_score"] - score_active) < 1e-6})

    report = {"status": "PASS", "image": str(IMAGE), "step_count": len(STEPS), "steps": STEPS}
    (HERE / "package_lifecycle_result.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(json.dumps(report, indent=2, ensure_ascii=False))
    shutil.rmtree(workdir, ignore_errors=True)


if __name__ == "__main__":
    main()
