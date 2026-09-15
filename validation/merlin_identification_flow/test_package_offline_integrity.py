"""Offline, integridad y frontera del encoder para el gestor de paquetes.

Verifica de verdad (no por afirmacion) que, una vez instalado, ninguna
operacion de catalogo abre un socket: se parchea `socket.socket` para que
lance, y se ejecuta el ciclo completo de catalogo.
"""
from __future__ import annotations

import json
import shutil
import socket
import sys
import tempfile
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from package_manager import (  # noqa: E402
    FilesystemPackageSource,
    LocalPackageManager,
    PackageValidationError,
    compute_payload_sha256,
)
from runtime_adapters import OpenSetReleaseAdapter, VisualRankingAdapter  # noqa: E402

REPOSITORY = HERE / "package_repository"
RESULTS: list[dict] = []


def check(name: str, ok: bool, detail: dict) -> None:
    RESULTS.append({"check": name, "status": "PASS" if ok else "FAIL", **detail})
    if not ok:
        raise AssertionError(f"{name} FAIL: {detail}")


class NoNetwork(RuntimeError):
    pass


def main() -> None:
    workdir = Path(tempfile.mkdtemp(prefix="anura_pkg_offline_"))
    manager = LocalPackageManager(workdir / "packages_root")
    source = FilesystemPackageSource(REPOSITORY)
    refs = {ref.key: ref for ref in source.list_available()}

    # Los adaptadores pesados se construyen ANTES de cortar la red, porque el
    # encoder/preprocess es un artefacto compartido, no parte del paquete.
    ranking = VisualRankingAdapter()
    open_set = OpenSetReleaseAdapter()
    rng = np.random.default_rng(20260914)
    embedding = rng.normal(size=512).astype(np.float32)
    embedding /= np.linalg.norm(embedding)

    for key in ("anura_antioquia_visual@v1.0.0", "anura_cauca_visual@v1.0.0"):
        manager.install(source, refs[key])

    # -- integridad --------------------------------------------------------
    tampered = workdir / "tampered"
    shutil.copytree(REPOSITORY / "anura_antioquia_visual/v1.0.0", tampered)
    payload = np.load(tampered / "prototypes.npz", allow_pickle=False)
    vectors = payload["prototypes"].copy()
    vectors[0] += 0.5  # alteracion silenciosa de un prototipo
    np.savez(tampered / "prototypes.npz", species_ids=payload["species_ids"], prototypes=vectors)
    try:
        manager.validate(tampered)
        rejected = False
        error = None
    except PackageValidationError as exc:
        rejected, error = True, str(exc)
    check("sha256 rejects a silently modified prototype", rejected, {"error": error})

    recomputed, _ = compute_payload_sha256(REPOSITORY / "anura_antioquia_visual/v1.0.0")
    declared = json.loads(
        (REPOSITORY / "anura_antioquia_visual/v1.0.0/manifest.json").read_text(encoding="utf-8")
    )["checksum"]["payload_sha256"]
    check("payload sha256 is deterministic and matches manifest", recomputed == declared,
          {"payload_sha256": recomputed})

    # -- frontera del encoder ---------------------------------------------
    package = manager.load("anura_antioquia_visual", "v1.0.0")
    files = sorted(p.name for p in package.path.rglob("*") if p.is_file())
    has_encoder = any(name.endswith((".onnx", ".pt", ".pth", ".bin", ".safetensors")) for name in files)
    check("package contains NO encoder artifact",
          not has_encoder and package.manifest["contains_encoder"] is False,
          {"files": files, "encoder_contract": package.manifest["encoder_contract"]["encoder_id"]})

    # -- offline ------------------------------------------------------------
    original_socket = socket.socket

    def blocked(*args, **kwargs):
        raise NoNetwork("Se intento abrir un socket durante una operacion de catalogo offline")

    socket.socket = blocked  # type: ignore[assignment]
    try:
        offline = LocalPackageManager(workdir / "packages_root")
        offline.activate("anura_antioquia_visual", "v1.0.0")
        offline.activate("anura_cauca_visual", "v1.0.0")
        installed = offline.list_installed()
        species = offline.active_species()
        ids, matrix = offline.active_prototypes()
        names = offline.active_scientific_names()
        groups = offline.active_visual_similarity_groups(HERE / "visual_similarity_groups.json")
        rows, rank_meta = ranking.rank_visual(embedding, names)
        decision, evidence = open_set.assess(
            embedding, active_species_ids=species, active_prototypes={s: matrix[i] for i, s in enumerate(ids)}
        )
        offline.deactivate("anura_antioquia_visual")
        offline.validate(offline.load("anura_cauca_visual", "v1.0.0"))
        network_used = False
    except NoNetwork as exc:
        network_used, installed, species, rows, decision = True, [], [], [], str(exc)
        rank_meta, groups, evidence = {}, [], {}
    finally:
        socket.socket = original_socket  # type: ignore[assignment]

    check("all catalog operations run with sockets disabled", not network_used,
          {"installed_count": len(installed), "active_species_count": len(species),
           "ranking_pool": rank_meta.get("candidate_pool"), "groups": len(groups),
           "open_set_decision": decision, "active_centroid_count": evidence.get("active_centroid_count"),
           "operations": ["list_installed", "activate", "active_species", "active_prototypes",
                          "active_visual_similarity_groups", "rank_visual", "open_set.assess",
                          "deactivate", "validate"]})

    report = {"status": "PASS", "check_count": len(RESULTS), "checks": RESULTS}
    (HERE / "package_offline_integrity_result.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(json.dumps(report, indent=2, ensure_ascii=False))
    shutil.rmtree(workdir, ignore_errors=True)


if __name__ == "__main__":
    main()
