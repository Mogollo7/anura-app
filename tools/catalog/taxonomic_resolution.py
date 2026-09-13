"""
taxonomic_resolution.py — Módulo compartido de resolución nombre científico → species_id.

Este módulo existe para que la normalización taxonómica ocurra en UN SOLO LUGAR,
reutilizando el mecanismo de alias que YA EXISTE en training/taxonomia.py (incluye
"Pristimantis acanthinus" -> "Pristimantis_achatinus"), en vez de que cada script
reimplemente su propia función de normalización local (ese fue exactamente el bug
de Fase 13: fase13_final_evaluation.py reimplementó canonical_species_name() sin
importar taxonomia.py).

Flujo que este modulo materializa:

    fuente historica (nombre en cualquier grafia/alias)
        |
        v
    taxonomia.canonico()          <- normalizacion taxonomica (YA EXISTENTE, reutilizada)
        |
        v
    species_registry.json         <- keyed por canonical_underscored_name
        |
        v
    species_id                    <- identificador estable

Cualquier script que necesite resolver un nombre a species_id debe importar
`resolve_species_id` de este modulo, no reimplementar su propia normalizacion.
"""
import importlib.util
import json
from pathlib import Path


def load_taxonomia_module(path: Path):
    spec = importlib.util.spec_from_file_location("taxonomia", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class SpeciesResolver:
    """Resuelve nombre cientifico (cualquier grafia/alias conocido) -> species_id.

    Usa taxonomia.canonico() para normalizar (incluye el ALIAS dict existente),
    luego busca en species_registry.json por nombre canonico underscored.
    """

    def __init__(self, taxonomia_path: Path, species_registry_path: Path):
        self.taxonomia = load_taxonomia_module(Path(taxonomia_path))

        with open(species_registry_path, "r", encoding="utf-8") as f:
            registry_data = json.load(f)

        # species_registry.json guarda scientific_name con espacio: "Genero especie"
        # taxonomia.canonico() devuelve underscored: "Genero_especie"
        # Normalizamos ambos lados a underscored para el lookup.
        self._by_canonical: dict[str, dict] = {}
        for sp in registry_data["species"]:
            canonical_underscored = sp["scientific_name"].replace(" ", "_")
            self._by_canonical[canonical_underscored] = sp

        self.registry_species_count = len(registry_data["species"])

    def resolve(self, raw_name: str) -> dict:
        """Devuelve {species_id, canonical_name, resolution_status} para un nombre crudo.

        resolution_status:
          RESOLVED             -> encontrado en species_registry via canonico()
          UNRESOLVED_NOT_IN_REGISTRY -> canonico() normalizo el nombre pero no esta en el registry
                                         (ej. especie excluida del catalogo visual, como Sachatamia)
        """
        canonical = self.taxonomia.canonico(raw_name)
        entry = self._by_canonical.get(canonical)
        if entry:
            return {
                "raw_name": raw_name,
                "canonical_name": canonical,
                "species_id": entry["species_id"],
                "resolution_status": "RESOLVED",
            }
        return {
            "raw_name": raw_name,
            "canonical_name": canonical,
            "species_id": None,
            "resolution_status": "UNRESOLVED_NOT_IN_REGISTRY",
        }
