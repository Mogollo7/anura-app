"""Aislamiento estricto de paquetes en Open Set (OPEN_SET_PACKAGE_ISOLATION).

Regla bajo prueba:
    Una especie solo puede resultar ESPECIE_CONOCIDA si pertenece al catalogo
    ACTIVO (persistido) en el momento de la inferencia. Desactivar un paquete
    elimina su capacidad de producir ESPECIE_CONOCIDA, incluso tras reload /
    rebuild y aunque existan centroides, indices o estado previamente cargado.

"X aparece como ESPECIE_CONOCIDA" se define de forma estricta como:
    decision == ESPECIE_CONOCIDA  Y  (especie aceptada por Open Set == X
                                      O X esta entre los candidatos).
Que la imagen de X sea aceptada como OTRA especie que SI pertenece al catalogo
activo NO es una violacion de pertenencia (es la permisividad del threshold
historico, que no se recalibra); se registra por separado y se verifica que la
especie aceptada pertenezca al catalogo activo.

La VERDAD del catalogo activo se lee siempre de disco con un gestor nuevo, no
del objeto que usa el runtime. Ninguna etiqueta llega al runtime: la especie
real de cada imagen se usa solo para interpretar.

Uso:
    python test_open_set_package_isolation.py [--out <archivo.json>]
Sale con codigo 1 si algun caso FALLA.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
import types
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

import merlin_flow  # noqa: E402
import merlin_runtime_pipeline  # noqa: E402
import package_manager  # noqa: E402
import runtime_adapters  # noqa: E402
import visual_similarity  # noqa: E402
from merlin_runtime_pipeline import MerlinRuntimePipeline  # noqa: E402
from package_manager import FilesystemPackageSource, LocalPackageManager  # noqa: E402

REPOSITORY = HERE / "package_repository"
PKG_A, PKG_B = "anura_antioquia_visual", "anura_cauca_visual"
VERSION = "v1.0.0"
THRESHOLD = 39.35406371422803

X_ID, X_NAME = "ANU_COL_DEND_TRU_001", "Dendrobates truncatus"  # solo en A
X_IMAGE = ROOT / "data cleaned/Dendrobates_truncatus/col_obs_135615735_photo_231331908.jpg"
Y_ID, Y_NAME = "ANU_COL_BOAN_CIN_001", "Boana cinerascens"  # solo en B
Y_IMAGE = ROOT / "data cleaned/Boana_cinerascens/col_obs_103034322_photo_172357955.jpg"
S_ID = "ANU_COL_BOAN_BOA_001"  # compartida A y B
S_IMAGE = ROOT / "data cleaned/Boana_boans/col_obs_306856679_photo_553414811.jpg"

RESULTS: list[dict] = []


def record(test: str, expected: str, ok: bool, actual: dict, status: str | None = None) -> None:
    RESULTS.append({"test": test, "expected": expected, "actual": actual,
                    "status": status or ("PASS" if ok else "FAIL")})


# --------------------------------------------------------------------------
def truth_catalog(root: Path) -> set[str]:
    """Catalogo activo PERSISTIDO, leido con un gestor nuevo desde disco."""
    return set(LocalPackageManager(root).active_species())


def install_all(manager: LocalPackageManager) -> None:
    source = FilesystemPackageSource(REPOSITORY)
    refs = {ref.key: ref for ref in source.list_available()}
    for package_id in (PKG_A, PKG_B):
        manager.install(source, refs[f"{package_id}@{VERSION}"])


def set_active(manager: LocalPackageManager, active: tuple[str, ...]) -> None:
    for package_id in (PKG_A, PKG_B):
        if package_id in active:
            manager.activate(package_id, VERSION)
        else:
            manager.deactivate(package_id)


class OpenSetSpy:
    """Registra QUE centroides entran realmente a Open Set (sin alterar nada)."""

    def __init__(self, pipeline: MerlinRuntimePipeline) -> None:
        self.original = pipeline.open_set.assess
        self.last_ids: list[str] | None = None
        self.last_prototype_ids: list[str] | None = None
        pipeline.open_set.assess = self  # type: ignore[assignment]

    def __call__(self, embedding, active_species_ids=None, active_prototypes=None):
        self.last_ids = None if active_species_ids is None else sorted(active_species_ids)
        self.last_prototype_ids = None if active_prototypes is None else sorted(active_prototypes)
        return self.original(embedding, active_species_ids=active_species_ids, active_prototypes=active_prototypes)


def observe(pipeline: MerlinRuntimePipeline, spy: OpenSetSpy | None, image: Path, species_id: str,
            truth: set[str]) -> dict:
    result = pipeline.identify_image(
        image, "isolation:" + species_id, is_anuran=True,
        anuran_evidence={"source": "isolation_test", "ground_truth_used": False},
    )
    evidence = result["open_set_evidence"]
    candidate_ids = [c["species_id"] for c in result["candidates"]]
    accepted = evidence.get("nearest_species_id") if result["decision"] == "ESPECIE_CONOCIDA" else None
    return {
        "decision": result["decision"],
        "accepted_species_id": accepted,
        "open_set_score": evidence.get("score"),
        "nearest_species_id": evidence.get("nearest_species_id"),
        "active_centroid_count": evidence.get("active_centroid_count"),
        "candidate_ids": candidate_ids,
        "species_in_candidates": species_id in candidate_ids,
        "species_centroid_participates": (species_id in (spy.last_prototype_ids or [])) if spy else None,
        "species_in_true_active_catalog": species_id in truth,
        "species_known": result["decision"] == "ESPECIE_CONOCIDA"
        and (accepted == species_id or species_id in candidate_ids),
        "accepted_in_true_active_catalog": None if accepted is None else accepted in truth,
        "all_candidates_in_true_active_catalog": all(c in truth for c in candidate_ids),
        "runtime_reported_active_packages": result["catalog_state"].get("active_packages"),
        "limitations": result["limitations"],
    }


def no_violation(obs: dict) -> bool:
    """Invariante global: nada fuera del catalogo activo real puede ser aceptado ni listado."""
    return (obs["accepted_in_true_active_catalog"] in (None, True)
            and obs["all_candidates_in_true_active_catalog"])


def known_as_itself(obs: dict, species_id: str) -> bool:
    return (obs["decision"] == "ESPECIE_CONOCIDA" and obs["accepted_species_id"] == species_id
            and obs["species_in_candidates"] and no_violation(obs))


def not_known(obs: dict) -> bool:
    return (not obs["species_known"] and not obs["species_in_candidates"]
            and obs["species_centroid_participates"] in (False, None) and no_violation(obs))


# --------------------------------------------------------------------------
def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=str(HERE / "open_set_package_isolation_result.json"))
    args = parser.parse_args()

    for image in (X_IMAGE, Y_IMAGE, S_IMAGE):
        assert image.exists(), image
    ids_a = set(json.loads((REPOSITORY / PKG_A / VERSION / "manifest.json").read_text(encoding="utf-8"))["species_ids"])
    ids_b = set(json.loads((REPOSITORY / PKG_B / VERSION / "manifest.json").read_text(encoding="utf-8"))["species_ids"])
    preconditions = {"X_only_in_A": X_ID in ids_a and X_ID not in ids_b,
                     "Y_only_in_B": Y_ID in ids_b and Y_ID not in ids_a,
                     "S_in_A_and_B": S_ID in ids_a and S_ID in ids_b}
    assert all(preconditions.values()), preconditions

    workdir = Path(tempfile.mkdtemp(prefix="anura_isolation_"))
    root = workdir / "packages_root"
    try:
        m1 = LocalPackageManager(root)
        install_all(m1)
        set_active(m1, (PKG_A,))
        pipeline = MerlinRuntimePipeline(m1)
        spy = OpenSetSpy(pipeline)

        # 1 / Caso A -- enable -> identify ------------------------------------
        o1 = observe(pipeline, spy, X_IMAGE, X_ID, truth_catalog(root))
        score_x_active = o1["open_set_score"]
        record("1_enable_A_identify_X (Caso A)",
               "ESPECIE_CONOCIDA aceptada como X; X en candidatos, catalogo y centroides",
               known_as_itself(o1, X_ID) and o1["species_centroid_participates"], o1)

        # 2 / Caso B -- disable -> identify (misma instancia) ----------------
        m1.deactivate(PKG_A)
        o2 = observe(pipeline, spy, X_IMAGE, X_ID, truth_catalog(root))
        record("2_disable_A_identify_X_same_instance (Caso B)",
               "X no conocida; sin catalogo activo -> NO_CONCLUYENTE, 0 centroides",
               not_known(o2) and o2["decision"] == "NO_CONCLUYENTE" and o2["active_centroid_count"] == 0, o2)

        # 3a -- disable desde OTRA instancia -> el runtime vivo debe verlo ----
        m1.activate(PKG_A, VERSION)
        m1.activate(PKG_B, VERSION)
        o3_before = observe(pipeline, spy, X_IMAGE, X_ID, truth_catalog(root))
        other = LocalPackageManager(root)  # p.ej. pantalla de ajustes u otro proceso
        other.deactivate(PKG_A)
        truth = truth_catalog(root)
        o3a = observe(pipeline, spy, X_IMAGE, X_ID, truth)
        record("3a_disable_A_from_other_instance_long_lived_runtime (reload de estado)",
               "El runtime vivo refleja el estado persistido: X no conocida, catalog_state sin A",
               known_as_itself(o3_before, X_ID) and not_known(o3a)
               and o3a["runtime_reported_active_packages"] == [f"{PKG_B}@{VERSION}"],
               {"before": {k: o3_before[k] for k in ("decision", "accepted_species_id", "active_centroid_count")},
                "after": o3a})

        # 3b -- disable -> rebuild completo del runtime -----------------------
        rebuilt = MerlinRuntimePipeline(LocalPackageManager(root))
        rebuilt_spy = OpenSetSpy(rebuilt)
        o3b = observe(rebuilt, rebuilt_spy, X_IMAGE, X_ID, truth_catalog(root))
        record("3b_disable_A_rebuild_runtime_identify_X (Caso B rebuild)",
               "Runtime reconstruido desde disco: X no conocida",
               not_known(o3b), o3b)
        del rebuilt, rebuilt_spy

        # 3c -- una instancia obsoleta NO puede reactivar A al escribir -------
        m1.set_species_enabled(Y_ID, True)  # mutacion no relacionada desde la instancia vieja
        persisted_a = json.loads((root / "state.json").read_text(encoding="utf-8"))["packages"][PKG_A]["active_version"]
        o3c = observe(pipeline, spy, X_IMAGE, X_ID, truth_catalog(root))
        record("3c_stale_instance_write_does_not_reactivate_A",
               "state.json conserva A inactivo tras escribir desde la instancia vieja; X no conocida",
               persisted_a is None and not_known(o3c),
               {"state_json_A_active_version": persisted_a, "observation": o3c})

        # 4 -- A+B -> solo A --------------------------------------------------
        set_active(m1, (PKG_A, PKG_B))
        set_active(m1, (PKG_A,))
        truth = truth_catalog(root)
        o4y = observe(pipeline, spy, Y_IMAGE, Y_ID, truth)
        o4x = observe(pipeline, spy, X_IMAGE, X_ID, truth)
        record("4_switch_A+B_to_only_A",
               "Y (solo B) no conocida; X (A) sigue conocida como X",
               not_known(o4y) and known_as_itself(o4x, X_ID), {"Y": o4y, "X": o4x})

        # 5 / Casos C y E -- A -> solo B ---------------------------------------
        set_active(m1, (PKG_B,))
        truth = truth_catalog(root)
        o5x = observe(pipeline, spy, X_IMAGE, X_ID, truth)
        o5y = observe(pipeline, spy, Y_IMAGE, Y_ID, truth)
        record("5_switch_A_to_only_B (Caso E: especie legitima de B sigue funcionando)",
               "X no conocida; Y conocida como Y",
               not_known(o5x) and known_as_itself(o5y, Y_ID), {"X": o5x, "Y": o5y})
        record("5b_X_image_accepted_as_other_active_species (threshold, no pertenencia)",
               "Si la imagen de X se acepta, la especie aceptada pertenece al catalogo activo y no es X",
               o5x["accepted_species_id"] != X_ID and o5x["accepted_in_true_active_catalog"] in (None, True),
               {"decision": o5x["decision"], "accepted_species_id": o5x["accepted_species_id"],
                "open_set_score": o5x["open_set_score"], "threshold": THRESHOLD},
               status="OBSERVED" if o5x["decision"] == "ESPECIE_CONOCIDA" and o5x["accepted_species_id"] != X_ID
               and o5x["accepted_in_true_active_catalog"] else None)

        # 6 / Caso D -- ninguno activo ----------------------------------------
        set_active(m1, ())
        truth = truth_catalog(root)
        o6 = {sid: observe(pipeline, spy, image, sid, truth)
              for sid, image in ((X_ID, X_IMAGE), (Y_ID, Y_IMAGE), (S_ID, S_IMAGE))}
        record("6_no_active_packages (Caso D)",
               "Ninguna especie conocida: NO_CONCLUYENTE, 0 candidatos, 0 centroides",
               all(not_known(o) and o["decision"] == "NO_CONCLUYENTE" and o["candidate_ids"] == []
                   and o["active_centroid_count"] == 0 for o in o6.values()), o6)

        # 7 -- volver a activar A ----------------------------------------------
        set_active(m1, (PKG_A,))
        o7 = observe(pipeline, spy, X_IMAGE, X_ID, truth_catalog(root))
        record("7_reactivate_A",
               "X vuelve a ser conocida como X con score bit-identico al caso 1",
               known_as_itself(o7, X_ID) and o7["open_set_score"] == score_x_active,
               {**o7, "score_case_1": score_x_active})

        # 8 / Caso C -- multiples paquetes activos simultaneamente -------------
        set_active(m1, (PKG_A, PKG_B))
        truth = truth_catalog(root)
        o8 = {sid: observe(pipeline, spy, image, sid, truth)
              for sid, image in ((X_ID, X_IMAGE), (Y_ID, Y_IMAGE), (S_ID, S_IMAGE))}
        m1.deactivate(PKG_A)
        truth = truth_catalog(root)
        o8_off_x = observe(pipeline, spy, X_IMAGE, X_ID, truth)
        o8_off_y = observe(pipeline, spy, Y_IMAGE, Y_ID, truth)
        o8_off_s = observe(pipeline, spy, S_IMAGE, S_ID, truth)
        record("8_multiple_active_A+B_then_disable_A (Caso C)",
               "A+B: X, Y y compartida conocidas como si mismas (34 centroides); sin A: X no conocida, Y y compartida siguen",
               all(known_as_itself(o8[sid], sid) for sid in (X_ID, Y_ID, S_ID))
               and o8[X_ID]["active_centroid_count"] == 34
               and not_known(o8_off_x) and known_as_itself(o8_off_y, Y_ID) and known_as_itself(o8_off_s, S_ID),
               {"A+B": o8, "B_only": {"X": o8_off_x, "Y": o8_off_y, "shared": o8_off_s}})

        # ------------------------------------------------------------------
        # FASE 5 -- inyeccion de fugas con solo B activo
        # ------------------------------------------------------------------
        set_active(m1, (PKG_B,))
        truth = truth_catalog(root)
        embedding, _ = pipeline.bioclip.embed_image(X_IMAGE)
        adapter = spy.original.__self__  # OpenSetReleaseAdapter real

        # L1 -- centroide residual del release inyectado en la matriz activa
        original_matrix = adapter._active_matrix

        def leaky_matrix(self, active_species_ids, active_prototypes):
            ids, matrix, source = original_matrix(active_species_ids, active_prototypes)
            if X_ID not in ids:
                ids = list(ids) + [X_ID]
                matrix = np.vstack([matrix, self.centroid_by_species[X_ID][None, :]])
            return ids, matrix, source + "+INJECTED_RESIDUAL"

        adapter._active_matrix = types.MethodType(leaky_matrix, adapter)
        try:
            l1 = observe(pipeline, spy, X_IMAGE, X_ID, truth)
            d_direct, e_direct = adapter.assess(embedding, active_species_ids=sorted(truth),
                                                active_prototypes=dict(zip(*_protos(m1))))
        finally:
            adapter._active_matrix = original_matrix
        record("L1_residual_release_centroid_injected_into_open_set_matrix",
               "El centroide residual de X (mas cercano, bajo threshold) NO produce ESPECIE_CONOCIDA",
               not l1["species_known"] and no_violation(l1) and d_direct == "NO_CONCLUYENTE",
               {"pipeline": l1, "adapter_direct": {"decision": d_direct,
                                                   "nearest_species_id": e_direct.get("nearest_species_id"),
                                                   "score": e_direct.get("score"),
                                                   "reason": e_direct.get("reason")}})

        # L2 -- decision Open Set corrupta/obsoleta que llega al flow
        def stale_decision(embedding, active_species_ids=None, active_prototypes=None):
            return "ESPECIE_CONOCIDA", {"status": "RELEASE_THRESHOLD", "score": 25.0126,
                                        "nearest_species_id": X_ID, "active_centroid_count": 34}

        pipeline.open_set.assess = stale_decision  # type: ignore[assignment]
        try:
            l2 = observe(pipeline, None, X_IMAGE, X_ID, truth)
        finally:
            pipeline.open_set.assess = spy  # type: ignore[assignment]
        record("L2_stale_open_set_decision_for_inactive_species_reaches_flow",
               "MerlinFlow rechaza aceptar una especie fuera del catalogo activo",
               l2["decision"] == "NO_CONCLUYENTE" and not l2["species_known"], l2)

        # L3 -- indice visual obsoleto que ignora el catalogo activo
        original_rank = pipeline.ranking.rank_visual
        pipeline.ranking.rank_visual = lambda emb, active_names=None: original_rank(emb, None)  # type: ignore
        try:
            l3 = observe(pipeline, spy, X_IMAGE, X_ID, truth)
        finally:
            pipeline.ranking.rank_visual = original_rank  # type: ignore[assignment]
        record("L3_stale_visual_index_full_pool_ignores_active_catalog",
               "Ningun candidato fuera del catalogo activo llega al resultado",
               not l3["species_in_candidates"] and no_violation(l3), l3)

        # L4 -- API directa: prototipos obsoletos sin catalogo declarado
        stale_ids, stale_matrix = _protos_for(root, (PKG_A, PKG_B), workdir)
        d4, e4 = adapter.assess(embedding, active_species_ids=None,
                                active_prototypes=dict(zip(stale_ids, stale_matrix)))
        record("L4_adapter_stale_prototypes_without_declared_catalog",
               "Prototipos sin catalogo activo declarado nunca producen ESPECIE_CONOCIDA",
               d4 == "NO_CONCLUYENTE",
               {"decision": d4, "nearest_species_id": e4.get("nearest_species_id"), "reason": e4.get("reason")})

        # L5 -- archivos huerfanos / temporales de A en disco
        orphan = root / "installed" / PKG_A / "v9.9.9"
        shutil.copytree(REPOSITORY / PKG_A / VERSION, orphan)
        shutil.copytree(REPOSITORY / PKG_A / VERSION, root / ".staging" / f"{PKG_A}__{VERSION}")
        l5 = observe(pipeline, spy, X_IMAGE, X_ID, truth_catalog(root))
        installed_dir_kept = (root / "installed" / PKG_A / VERSION).exists()
        record("L5_deactivated_and_orphan_files_on_disk_do_not_participate",
               "Archivos de A (desactivado, huerfano v9.9.9 y staging) presentes en disco pero X no conocida",
               installed_dir_kept and not_known(l5),
               {"deactivated_install_dir_on_disk": installed_dir_kept, "orphan_dir": str(orphan.relative_to(workdir)),
                "observation": l5})

        # L6 -- objetos persistentes: paquete A cargado y cacheado antes de desactivar
        m1.activate(PKG_A, VERSION)
        held_package = m1.load(PKG_A, VERSION)
        held_package.prototypes()  # llena la cache _prototypes del objeto
        held_state = json.loads(json.dumps(m1.state))
        m1.deactivate(PKG_A)
        attributes_before = sorted(vars(pipeline))
        l6 = observe(pipeline, spy, X_IMAGE, X_ID, truth_catalog(root))
        attributes_after = sorted(vars(pipeline))
        record("L6_cached_package_objects_and_previous_results_do_not_leak",
               "Objeto InstalledPackage con cache viva y estado previo retenido no reintroducen X; el pipeline no guarda estado por inferencia",
               not_known(l6) and attributes_before == attributes_after
               and held_package._prototypes is not None and held_state["packages"][PKG_A]["active_version"] == VERSION,
               {"pipeline_attributes": attributes_after, "observation": l6})

        # L7 -- variables globales de modulo
        leaks = {}
        for module in (merlin_flow, merlin_runtime_pipeline, package_manager, runtime_adapters, visual_similarity):
            for name, value in vars(module).items():
                if isinstance(value, (dict, list, set, tuple)) and not name.startswith("__"):
                    try:
                        blob = json.dumps(value, default=str)
                    except (TypeError, ValueError):
                        blob = str(value)
                    if X_ID in blob or X_NAME in blob:
                        leaks[f"{module.__name__}.{name}"] = type(value).__name__
        record("L7_no_module_level_catalog_state",
               "Ningun global de modulo contiene la especie/catalogo",
               not leaks, {"globals_referencing_X": leaks})

        # Residuos en memoria que EXISTEN por diseno (release congelado) y que las
        # pruebas L1-L3 demuestran incapaces de producir ESPECIE_CONOCIDA.
        record("L8_frozen_release_structures_still_in_memory",
               "Documentar residuos congelados que contienen X",
               True,
               {"open_set.centroid_by_species_has_X": X_ID in adapter.centroid_by_species,
                "ranking.names_has_X": X_NAME in pipeline.ranking.names,
                "flow.catalog_registry_has_X": X_NAME in pipeline.flow.catalog},
               status="OBSERVED")
    finally:
        shutil.rmtree(workdir, ignore_errors=True)

    summary = {
        "status": "PASS" if not any(r["status"] == "FAIL" for r in RESULTS) else "FAIL",
        "pass": sum(r["status"] == "PASS" for r in RESULTS),
        "fail": sum(r["status"] == "FAIL" for r in RESULTS),
        "observed": sum(r["status"] == "OBSERVED" for r in RESULTS),
        "threshold_used": THRESHOLD,
        "threshold_recalibrated": False,
        "preconditions": preconditions,
        "results": RESULTS,
    }
    Path(args.out).write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    for row in RESULTS:
        print(f"{row['status']:9s} {row['test']}")
    print(json.dumps({k: summary[k] for k in ("status", "pass", "fail", "observed")}))
    return 1 if summary["fail"] else 0


def _protos(manager: LocalPackageManager) -> tuple[list[str], np.ndarray]:
    return manager.active_prototypes()


def _protos_for(root: Path, active: tuple[str, ...], workdir: Path) -> tuple[list[str], np.ndarray]:
    """Prototipos de un catalogo pasado (A+B), capturados en otro root temporal."""
    other_root = workdir / "stale_snapshot_root"
    manager = LocalPackageManager(other_root)
    install_all(manager)
    set_active(manager, active)
    return manager.active_prototypes()


if __name__ == "__main__":
    raise SystemExit(main())
