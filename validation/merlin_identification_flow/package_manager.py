"""Gestor de paquetes de especies para el runtime Merlin.

Frontera explicita:
    - Un paquete NUNCA contiene el encoder BioCLIP. El encoder
      (``bioclip/checkpoints/encoder_anura_fp16.onnx``) es un artefacto
      independiente y compartido por todos los paquetes. Lo unico que el
      paquete declara sobre el encoder es un *contrato* (encoder_id +
      encoder_sha256) que se valida en la instalacion y en la carga.
    - Un paquete contiene: manifest, metadata de especies, prototipos
      (centroides), metadata taxonomica, grupos de similitud visual y
      assets opcionales.

Flujo de diseno:
    PackageSource -> fetch/staging -> validate (sha256) -> LocalPackageManager

Todo es offline una vez instalado: este modulo no importa ni usa red.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from types import MappingProxyType
from typing import Any, Iterable, Mapping

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DEFAULT_PACKAGES_ROOT = HERE / "packages_root"

PACKAGE_SCHEMA_VERSION = "anura.species-package/1.0.0"
STATE_SCHEMA_VERSION = "anura.package-state/1.0.0"
MANAGER_VERSION = "merlin-package-manager/1.0.0"

# Contrato de encoder compartido (el paquete NO lo contiene, solo lo referencia).
ENCODER_ID = "bioclip_anura_v1"
ENCODER_SHA256 = "219e860e6fa9a80fb30a59fc8f61911421bbd53a4537dca831803d3ab446b2ad"

PAYLOAD_FILES = ("species.json", "prototypes.npz", "taxonomy.json", "visual_similarity_groups.json")


class PackageError(RuntimeError):
    """Error generico del gestor de paquetes."""


class PackageValidationError(PackageError):
    """El paquete no supera la validacion de integridad o de contrato."""


class PackageNotFound(PackageError):
    """El paquete pedido no esta instalado / no esta disponible en la fuente."""


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def compute_payload_sha256(package_dir: Path) -> tuple[str, dict[str, str]]:
    """Hash determinista del payload (todo menos ``manifest.json``).

    Se construye como sha256 sobre la lista ordenada ``<relpath>:<sha256>\\n``,
    de modo que el resultado no depende del orden del filesystem.
    """
    files: dict[str, str] = {}
    for path in sorted(package_dir.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(package_dir).as_posix()
        if rel == "manifest.json":
            continue
        files[rel] = _sha256_file(path)
    blob = "".join(f"{rel}:{digest}\n" for rel, digest in sorted(files.items()))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest(), files


# --------------------------------------------------------------------------
# Fuentes de paquetes
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class PackageRef:
    """Referencia a un paquete disponible en una fuente."""

    package_id: str
    package_version: str
    source_name: str
    locator: str
    species_count: int | None = None

    @property
    def key(self) -> str:
        return f"{self.package_id}@{self.package_version}"


class PackageSource(ABC):
    """Interfaz generica de fuente de paquetes.

    Implementaciones futuras (HTTP, GitHub Releases, Drive, S3) solo tienen que
    implementar ``list_available`` y ``fetch``. El resto del pipeline
    (validacion, instalacion, activacion) no conoce el transporte.
    ``fetch`` debe dejar en ``staging_dir`` un DIRECTORIO de paquete ya
    expandido; el transporte decide como (copia, descarga+unzip, etc.).
    """

    name: str = "abstract"

    @abstractmethod
    def list_available(self) -> list[PackageRef]:
        ...

    @abstractmethod
    def fetch(self, ref: PackageRef, staging_dir: Path) -> Path:
        ...

    def supports_offline(self) -> bool:
        return False


class FilesystemPackageSource(PackageSource):
    """Fuente local. Layout esperado: ``<root>/<package_id>/<package_version>/``."""

    name = "filesystem"

    def __init__(self, root: Path) -> None:
        self.root = Path(root)

    def list_available(self) -> list[PackageRef]:
        refs: list[PackageRef] = []
        if not self.root.exists():
            return refs
        for manifest_path in sorted(self.root.glob("*/*/manifest.json")):
            try:
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            refs.append(
                PackageRef(
                    package_id=manifest["package_id"],
                    package_version=manifest["package_version"],
                    source_name=self.name,
                    locator=str(manifest_path.parent),
                    species_count=len(manifest.get("species_ids", [])),
                )
            )
        return refs

    def fetch(self, ref: PackageRef, staging_dir: Path) -> Path:
        origin = Path(ref.locator)
        if not (origin / "manifest.json").exists():
            raise PackageNotFound(f"No hay manifest en {origin}")
        target = staging_dir / f"{ref.package_id}__{ref.package_version}"
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(origin, target)
        return target

    def supports_offline(self) -> bool:
        return True


# --------------------------------------------------------------------------
# Paquete instalado
# --------------------------------------------------------------------------
@dataclass
class InstalledPackage:
    package_id: str
    package_version: str
    path: Path
    manifest: dict[str, Any]
    _prototypes: tuple[list[str], np.ndarray] | None = field(default=None, repr=False)

    @property
    def key(self) -> str:
        return f"{self.package_id}@{self.package_version}"

    @property
    def species_ids(self) -> list[str]:
        return list(self.manifest["species_ids"])

    def species_metadata(self) -> dict[str, dict[str, Any]]:
        data = json.loads((self.path / "species.json").read_text(encoding="utf-8"))
        return {item["species_id"]: item for item in data["species"]}

    def taxonomy(self) -> dict[str, Any]:
        return json.loads((self.path / "taxonomy.json").read_text(encoding="utf-8"))

    def visual_similarity_groups(self) -> list[dict[str, Any]]:
        path = self.path / "visual_similarity_groups.json"
        if not path.exists():
            return []
        return json.loads(path.read_text(encoding="utf-8")).get("groups", [])

    # -- PARTE 12: extension de contexto (geografia/elevacion) ------------
    # Archivos OPCIONALES (no forman parte de PAYLOAD_FILES): un paquete
    # v1.0.0 sin estos archivos sigue siendo valido (compatibilidad hacia
    # atras). Cuando existen, se cuentan igual dentro de compute_payload_sha256
    # (que hashea "todo menos manifest.json"), asi que su integridad SI queda
    # protegida por el checksum del paquete aunque no sean obligatorios.
    def geography(self) -> dict[str, Any] | None:
        """distribution_area por especie del paquete (subconjunto de
        species_distribution_maps_v1.json), si el paquete la declara."""
        path = self.path / "geography.json"
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def elevation(self) -> dict[str, Any] | None:
        """Rangos de elevacion por especie del paquete (subconjunto de
        elevation_ranges_v1.json), si el paquete la declara."""
        path = self.path / "elevation.json"
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def prototypes(self) -> tuple[list[str], np.ndarray]:
        """(species_ids, matriz [n, d]) alineados por indice."""
        if self._prototypes is None:
            payload = np.load(self.path / "prototypes.npz", allow_pickle=False)
            ids = [str(x) for x in payload["species_ids"]]
            vectors = payload["prototypes"].astype(np.float32)
            if vectors.shape[0] != len(ids):
                raise PackageValidationError(f"{self.key}: prototipos desalineados")
            self._prototypes = (ids, vectors)
        return self._prototypes


@dataclass(frozen=True, eq=False)
class ActiveCatalogSnapshot:
    """Catalogo activo INMUTABLE construido desde UNA lectura de ``state.json``.

    Es la fuente de verdad de una inferencia: paquetes activos -> especies
    activas -> prototipos activos. Nada fuera de ``species_ids`` aporta
    centroide, metadata ni candidato. Una instantanea nunca se actualiza: si
    cambia el conjunto de paquetes activos se construye otra.
    """

    manager_version: str
    packages_root: str
    installed: tuple[str, ...]
    packages: tuple[InstalledPackage, ...]
    disabled_species: frozenset[str]
    species_ids: tuple[str, ...]
    prototype_ids: tuple[str, ...]
    prototype_matrix: np.ndarray
    prototype_provenance: Mapping[str, str]
    species_metadata: Mapping[str, dict[str, Any]]
    fingerprint: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "_membership", frozenset(self.species_ids))

    def contains(self, species_id: str) -> bool:
        return species_id in self._membership  # type: ignore[attr-defined]

    @property
    def package_keys(self) -> list[str]:
        return [package.key for package in self.packages]

    @property
    def scientific_names(self) -> list[str]:
        return sorted(item["scientific_name"] for item in self.species_metadata.values())

    def prototype_map(self) -> dict[str, np.ndarray]:
        return {species_id: self.prototype_matrix[index] for index, species_id in enumerate(self.prototype_ids)}

    def summary(self) -> dict[str, Any]:
        return {
            "manager_version": self.manager_version,
            "packages_root": self.packages_root,
            "installed": list(self.installed),
            "active_packages": self.package_keys,
            "active_species_count": len(self.species_ids),
            "disabled_species": sorted(self.disabled_species),
            "network_required": False,
        }


# --------------------------------------------------------------------------
# Gestor local
# --------------------------------------------------------------------------
class LocalPackageManager:
    """Estado local persistente de paquetes instalados/activos.

    Politica de versionado (explicita):
        - Instalar ``v1.0.1`` NO borra ni sobrescribe ``v1.0.0``: conviven
          lado a lado bajo ``installed/<package_id>/<version>/``.
        - Instalar una version YA instalada se RECHAZA con
          ``PackageError`` salvo que se pase ``allow_reinstall=True``,
          que reemplaza esa version exacta de forma explicita.
        - Solo UNA version de un mismo ``package_id`` puede estar activa a la
          vez. ``activate`` cambia la version activa, nunca acumula.
        - Desinstalar una version activa se rechaza salvo ``force=True``
          (que primero desactiva).
    """

    def __init__(self, packages_root: Path = DEFAULT_PACKAGES_ROOT) -> None:
        self.root = Path(packages_root)
        self.installed_dir = self.root / "installed"
        self.staging_dir = self.root / ".staging"
        self.state_path = self.root / "state.json"
        self.installed_dir.mkdir(parents=True, exist_ok=True)
        self.staging_dir.mkdir(parents=True, exist_ok=True)
        self.state = self._load_state()

    # -- estado -----------------------------------------------------------
    def _load_state(self) -> dict[str, Any]:
        if self.state_path.exists():
            state = json.loads(self.state_path.read_text(encoding="utf-8"))
            state.setdefault("packages", {})
            state.setdefault("disabled_species", [])
            return state
        return {
            "schema_version": STATE_SCHEMA_VERSION,
            "manager_version": MANAGER_VERSION,
            "packages": {},
            "disabled_species": [],
        }

    def _refresh_state(self) -> None:
        """Relee ``state.json``: la fuente de verdad es el estado PERSISTIDO.

        Sin esto, una instancia que sobrevive a una desactivacion hecha desde
        otra instancia/proceso seguiria usando -- y al escribir, reactivando --
        paquetes ya desactivados.
        """
        self.state = self._load_state()

    def _save_state(self) -> None:
        self.state["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        self.state_path.write_text(
            json.dumps(self.state, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8"
        )

    # -- consulta ---------------------------------------------------------
    def list_available(self, source: PackageSource) -> list[PackageRef]:
        return source.list_available()

    def list_installed(self) -> list[dict[str, Any]]:
        self._refresh_state()
        rows: list[dict[str, Any]] = []
        for package_id, entry in sorted(self.state["packages"].items()):
            for version in sorted(entry["versions"]):
                rows.append(
                    {
                        "package_id": package_id,
                        "package_version": version,
                        "active": entry.get("active_version") == version,
                        "path": str(self.installed_dir / package_id / version),
                        "species_count": entry["versions"][version]["species_count"],
                        "payload_sha256": entry["versions"][version]["payload_sha256"],
                    }
                )
        return rows

    def is_installed(self, package_id: str, version: str | None = None) -> bool:
        self._refresh_state()
        entry = self.state["packages"].get(package_id)
        if entry is None:
            return False
        return True if version is None else version in entry["versions"]

    def active_version(self, package_id: str) -> str | None:
        self._refresh_state()
        return self.state["packages"].get(package_id, {}).get("active_version")

    def load(self, package_id: str, version: str | None = None) -> InstalledPackage:
        self._refresh_state()
        return self._load_from_state(package_id, version)

    def _load_from_state(self, package_id: str, version: str | None = None) -> InstalledPackage:
        """Como ``load`` pero sobre ``self.state`` ya leido (sin volver a disco)."""
        entry = self.state["packages"].get(package_id)
        if entry is None:
            raise PackageNotFound(f"Paquete no instalado: {package_id}")
        version = version or entry.get("active_version") or sorted(entry["versions"])[-1]
        if version not in entry["versions"]:
            raise PackageNotFound(f"Version no instalada: {package_id}@{version}")
        path = self.installed_dir / package_id / version
        manifest = json.loads((path / "manifest.json").read_text(encoding="utf-8"))
        return InstalledPackage(package_id, version, path, manifest)

    def active_packages(self) -> list[InstalledPackage]:
        self._refresh_state()
        return self._active_packages_from_state()

    def _active_packages_from_state(self) -> list[InstalledPackage]:
        out: list[InstalledPackage] = []
        for package_id, entry in sorted(self.state["packages"].items()):
            version = entry.get("active_version")
            if version:
                out.append(self._load_from_state(package_id, version))
        return out

    # -- validacion -------------------------------------------------------
    def validate(self, package: Path | InstalledPackage) -> dict[str, Any]:
        """Valida estructura, contrato de encoder e integridad SHA-256."""
        path = package.path if isinstance(package, InstalledPackage) else Path(package)
        manifest_path = path / "manifest.json"
        if not manifest_path.exists():
            raise PackageValidationError(f"Falta manifest.json en {path}")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

        required = {"package_id", "package_version", "schema_version", "species_ids", "checksum"}
        missing = required - set(manifest)
        if missing:
            raise PackageValidationError(f"Manifest incompleto, faltan: {sorted(missing)}")
        if manifest["schema_version"] != PACKAGE_SCHEMA_VERSION:
            raise PackageValidationError(
                f"schema_version incompatible: {manifest['schema_version']} != {PACKAGE_SCHEMA_VERSION}"
            )
        for name in PAYLOAD_FILES:
            if not (path / name).exists():
                raise PackageValidationError(f"Falta archivo de payload: {name}")

        contract = manifest.get("encoder_contract", {})
        if contract.get("encoder_sha256") != ENCODER_SHA256 or contract.get("encoder_id") != ENCODER_ID:
            raise PackageValidationError("Contrato de encoder incompatible con el encoder compartido")
        if manifest.get("contains_encoder", False):
            raise PackageValidationError("Un paquete de especies NO puede contener el encoder")

        actual, per_file = compute_payload_sha256(path)
        declared = manifest["checksum"]["payload_sha256"]
        if actual != declared:
            raise PackageValidationError(
                f"SHA-256 del payload no coincide: declarado={declared} calculado={actual}"
            )

        payload = np.load(path / "prototypes.npz", allow_pickle=False)
        ids = [str(x) for x in payload["species_ids"]]
        vectors = payload["prototypes"]
        if sorted(ids) != sorted(manifest["species_ids"]):
            raise PackageValidationError("prototypes.npz no cubre exactamente species_ids del manifest")
        if vectors.shape[0] != len(ids):
            raise PackageValidationError("prototypes.npz desalineado")
        if int(vectors.shape[1]) != int(contract.get("embedding_dim", vectors.shape[1])):
            raise PackageValidationError("Dimension de prototipo incompatible con el contrato")

        return {
            "valid": True,
            "package_id": manifest["package_id"],
            "package_version": manifest["package_version"],
            "species_count": len(manifest["species_ids"]),
            "payload_sha256": actual,
            "file_count": len(per_file),
            "embedding_dim": int(vectors.shape[1]),
            "encoder_contract_ok": True,
            "contains_encoder": False,
        }

    # -- ciclo de vida ----------------------------------------------------
    def install(
        self,
        source: PackageSource | Path | str,
        ref: PackageRef | None = None,
        *,
        allow_reinstall: bool = False,
    ) -> InstalledPackage:
        """Instala un paquete desde una fuente (o desde un directorio directo)."""
        if isinstance(source, (str, Path)):
            origin = Path(source)
            manifest = json.loads((origin / "manifest.json").read_text(encoding="utf-8"))
            ref = PackageRef(manifest["package_id"], manifest["package_version"], "direct", str(origin))
            source = FilesystemPackageSource(origin.parent.parent)
        if ref is None:
            available = source.list_available()
            if len(available) != 1:
                raise PackageError("Se requiere `ref` cuando la fuente expone != 1 paquete")
            ref = available[0]

        staged = source.fetch(ref, self.staging_dir)
        try:
            report = self.validate(staged)  # integridad ANTES de instalar
            package_id, version = report["package_id"], report["package_version"]
            if package_id != ref.package_id or version != ref.package_version:
                raise PackageValidationError("El manifest no concuerda con la referencia pedida")
            target = self.installed_dir / package_id / version
            if target.exists() or self.is_installed(package_id, version):
                if not allow_reinstall:
                    raise PackageError(
                        f"{package_id}@{version} ya esta instalado. "
                        "Instala otra version o usa allow_reinstall=True (reemplazo explicito)."
                    )
                shutil.rmtree(target, ignore_errors=True)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(staged, target)
        finally:
            shutil.rmtree(staged, ignore_errors=True)

        self._refresh_state()
        entry = self.state["packages"].setdefault(package_id, {"versions": {}, "active_version": None})
        entry["versions"][version] = {
            "installed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "species_count": report["species_count"],
            "payload_sha256": report["payload_sha256"],
            "source": ref.source_name,
        }
        self._save_state()
        return self.load(package_id, version)

    def activate(self, package_id: str, version: str | None = None) -> str:
        self._refresh_state()
        entry = self.state["packages"].get(package_id)
        if entry is None:
            raise PackageNotFound(f"Paquete no instalado: {package_id}")
        version = version or sorted(entry["versions"])[-1]
        if version not in entry["versions"]:
            raise PackageNotFound(f"Version no instalada: {package_id}@{version}")
        entry["active_version"] = version
        self._save_state()
        return version

    def deactivate(self, package_id: str) -> None:
        self._refresh_state()
        entry = self.state["packages"].get(package_id)
        if entry is None:
            raise PackageNotFound(f"Paquete no instalado: {package_id}")
        entry["active_version"] = None
        self._save_state()

    def uninstall(self, package_id: str, version: str | None = None, *, force: bool = False) -> list[str]:
        self._refresh_state()
        entry = self.state["packages"].get(package_id)
        if entry is None:
            raise PackageNotFound(f"Paquete no instalado: {package_id}")
        versions = [version] if version else sorted(entry["versions"])
        for item in versions:
            if item not in entry["versions"]:
                raise PackageNotFound(f"Version no instalada: {package_id}@{item}")
            if entry.get("active_version") == item:
                if not force and version is not None:
                    raise PackageError(
                        f"{package_id}@{item} esta activo. Desactiva primero o usa force=True."
                    )
                entry["active_version"] = None
            shutil.rmtree(self.installed_dir / package_id / item, ignore_errors=True)
            del entry["versions"][item]
        if not entry["versions"]:
            del self.state["packages"][package_id]
            shutil.rmtree(self.installed_dir / package_id, ignore_errors=True)
        self._save_state()
        return versions

    # -- flags de especie (capa por encima de la activacion de paquete) ----
    def set_species_enabled(self, species_id: str, enabled: bool) -> None:
        self._refresh_state()
        disabled = set(self.state.get("disabled_species", []))
        disabled.discard(species_id) if enabled else disabled.add(species_id)
        self.state["disabled_species"] = sorted(disabled)
        self._save_state()

    def disabled_species(self) -> set[str]:
        self._refresh_state()
        return set(self.state.get("disabled_species", []))

    # -- catalogo activo --------------------------------------------------
    def active_catalog_snapshot(self) -> ActiveCatalogSnapshot:
        """Fuente de verdad del catalogo activo, construida desde UNA lectura del estado persistido.

        Invariantes:
            - especies activas = union de paquetes activos menos flags apagados;
            - un prototipo/metadata solo entra si su especie esta activa Y
              declarada en el manifest del paquete que lo aporta;
            - si dos paquetes activos aportan la misma especie gana el primero
              en orden alfabetico de ``package_id`` (determinista y documentado).
        """
        self._refresh_state()
        packages = tuple(self._active_packages_from_state())
        disabled = frozenset(self.state.get("disabled_species", []))
        active: set[str] = set()
        for package in packages:
            active.update(species_id for species_id in package.species_ids if species_id not in disabled)

        chosen: dict[str, np.ndarray] = {}
        provenance: dict[str, str] = {}
        metadata: dict[str, dict[str, Any]] = {}
        for package in packages:
            declared = set(package.species_ids)
            ids, vectors = package.prototypes()
            for species_id, vector in zip(ids, vectors):
                if species_id not in active or species_id not in declared or species_id in chosen:
                    continue
                chosen[species_id] = vector
                provenance[species_id] = package.key
            for species_id, meta in package.species_metadata().items():
                if species_id not in active or species_id not in declared or species_id in metadata:
                    continue
                metadata[species_id] = meta

        ordered = sorted(chosen)
        matrix = (
            np.stack([chosen[key] for key in ordered]).astype(np.float32)
            if ordered
            else np.zeros((0, 512), dtype=np.float32)
        )
        matrix.setflags(write=False)
        versions = {
            package.key: self.state["packages"][package.package_id]["versions"][package.package_version]["payload_sha256"]
            for package in packages
        }
        fingerprint = hashlib.sha256(
            json.dumps({"active_packages": versions, "disabled_species": sorted(disabled)}, sort_keys=True).encode("utf-8")
        ).hexdigest()
        return ActiveCatalogSnapshot(
            manager_version=MANAGER_VERSION,
            packages_root=str(self.root),
            installed=tuple(
                f"{package_id}@{version}"
                for package_id, entry in sorted(self.state["packages"].items())
                for version in sorted(entry["versions"])
            ),
            packages=packages,
            disabled_species=disabled,
            species_ids=tuple(sorted(active)),
            prototype_ids=tuple(ordered),
            prototype_matrix=matrix,
            prototype_provenance=MappingProxyType({key: provenance[key] for key in ordered}),
            species_metadata=MappingProxyType(metadata),
            fingerprint=fingerprint,
        )

    def active_species(self) -> list[str]:
        """species_id activos = union de paquetes activos menos flags apagados."""
        return list(self.active_catalog_snapshot().species_ids)

    def active_prototypes(self) -> tuple[list[str], np.ndarray]:
        """Prototipos activos (species_id -> centroide), deduplicados. Ver ``active_catalog_snapshot``."""
        snapshot = self.active_catalog_snapshot()
        if not snapshot.prototype_ids:
            return [], np.zeros((0, 512), dtype=np.float32)
        self._last_prototype_provenance = dict(snapshot.prototype_provenance)
        return list(snapshot.prototype_ids), snapshot.prototype_matrix.copy()

    def active_species_metadata(self) -> dict[str, dict[str, Any]]:
        return dict(self.active_catalog_snapshot().species_metadata)

    def active_scientific_names(self) -> list[str]:
        return sorted(item["scientific_name"] for item in self.active_species_metadata().values())

    def active_visual_similarity_groups(
        self, extra_config: Path | None = None, packages: Iterable[InstalledPackage] | None = None
    ) -> list[dict[str, Any]]:
        """Grupos de los paquetes activos (o de ``packages`` de una instantanea) + config global opcional."""
        groups: dict[str, dict[str, Any]] = {}
        for package in (self.active_packages() if packages is None else packages):
            for group in package.visual_similarity_groups():
                groups.setdefault(group["group_id"], group)
        if extra_config and Path(extra_config).exists():
            data = json.loads(Path(extra_config).read_text(encoding="utf-8"))
            for group in data.get("groups", []):
                groups[group["group_id"]] = group
        return [groups[key] for key in sorted(groups)]

    def active_geography(self) -> dict[str, dict[str, Any]]:
        """species_id -> distribution_area, solo para especies ACTIVAS que declaran geography.json.

        Especies sin geography.json en su paquete simplemente no aparecen en el
        resultado (no se inventa dato geografico). Esto es evidencia AUXILIAR de
        reranking/contextualizacion -- nunca entra a Open Set ni modifica el
        embedding (ver PARTE 5/8/9 del stress test para el uso real).
        """
        disabled = self.disabled_species()
        out: dict[str, dict[str, Any]] = {}
        for package in self.active_packages():
            geo = package.geography()
            if not geo:
                continue
            for species_id, area in geo.get("species", {}).items():
                if species_id in disabled or species_id not in set(package.species_ids):
                    continue
                out.setdefault(species_id, area)
        return out

    def active_elevation(self) -> dict[str, dict[str, Any]]:
        """species_id -> rango de elevacion, solo para especies ACTIVAS que declaran elevation.json."""
        disabled = self.disabled_species()
        out: dict[str, dict[str, Any]] = {}
        for package in self.active_packages():
            elev = package.elevation()
            if not elev:
                continue
            for species_id, rng in elev.get("species", {}).items():
                if species_id in disabled or species_id not in set(package.species_ids):
                    continue
                out.setdefault(species_id, rng)
        return out

    def catalog_state_summary(self) -> dict[str, Any]:
        active = self.active_packages()
        return {
            "manager_version": MANAGER_VERSION,
            "packages_root": str(self.root),
            "installed": [row["package_id"] + "@" + row["package_version"] for row in self.list_installed()],
            "active_packages": [package.key for package in active],
            "active_species_count": len(self.active_species()),
            "disabled_species": sorted(self.disabled_species()),
            "network_required": False,
        }


def build_package(
    target_dir: Path,
    *,
    package_id: str,
    package_version: str,
    species: list[dict[str, Any]],
    prototypes: dict[str, np.ndarray],
    prototype_version: str,
    visual_similarity_groups: list[dict[str, Any]] | None = None,
    dependencies: list[str] | None = None,
    minimum_app_version: str = "0.1.0",
    source_artifacts: dict[str, Any] | None = None,
) -> Path:
    """Escribe un paquete distribuible completo (payload + manifest firmado)."""
    target_dir = Path(target_dir)
    if target_dir.exists():
        shutil.rmtree(target_dir)
    target_dir.mkdir(parents=True)
    species_ids = sorted(item["species_id"] for item in species)
    if sorted(prototypes) != species_ids:
        raise PackageError("prototypes y species deben cubrir exactamente los mismos species_id")

    (target_dir / "species.json").write_text(
        json.dumps({"species": sorted(species, key=lambda x: x["species_id"])}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    matrix = np.stack([np.asarray(prototypes[key], dtype=np.float32) for key in species_ids])
    np.savez(target_dir / "prototypes.npz", species_ids=np.array(species_ids), prototypes=matrix)
    taxonomy = {
        "families": sorted({item.get("family") for item in species if item.get("family")}),
        "genera": sorted({item.get("genus") for item in species if item.get("genus")}),
        "by_species": {
            item["species_id"]: {"family": item.get("family"), "genus": item.get("genus")} for item in species
        },
    }
    (target_dir / "taxonomy.json").write_text(json.dumps(taxonomy, indent=2, ensure_ascii=False), encoding="utf-8")
    (target_dir / "visual_similarity_groups.json").write_text(
        json.dumps({"groups": visual_similarity_groups or []}, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    payload_sha, per_file = compute_payload_sha256(target_dir)
    manifest = {
        "package_id": package_id,
        "package_version": package_version,
        "schema_version": PACKAGE_SCHEMA_VERSION,
        "species_ids": species_ids,
        "species_count": len(species_ids),
        "prototype_version": prototype_version,
        "encoder_contract": {
            "encoder_id": ENCODER_ID,
            "encoder_sha256": ENCODER_SHA256,
            "embedding_dim": int(matrix.shape[1]),
            "normalization": "L2",
        },
        "contains_encoder": False,
        "encoder_distribution_note": "El encoder BioCLIP NO viaja en el paquete; es compartido e independiente.",
        "dependencies": dependencies or [],
        "minimum_app_version": minimum_app_version,
        "checksum": {"algorithm": "sha256", "payload_sha256": payload_sha, "files": per_file},
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "source_artifacts": source_artifacts or {},
    }
    (target_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return target_dir
