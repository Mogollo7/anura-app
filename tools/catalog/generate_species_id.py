"""
generate_species_id.py — Genera species_id estables a partir de datos taxonomicos YA CONOCIDOS.

NO inventa taxonomia. Toma nombre cientifico + genero + familia de una fuente real
(por defecto: training/taxonomia.py) y produce un identificador determinista:

    ANU_COL_<GENERO_4>_<ESPECIE_3>_<seq>

El seq (001, 002, ...) solo se usa para desambiguar colisiones (mismo prefijo genero+especie),
nunca para indicar orden de importancia.

Uso:
    python generate_species_id.py --source training/taxonomia.py --out taxonomy/species/species_registry.json

Es SEGURO ejecutar esto contra las 41 especies existentes: los datos (nombre, genero, familia)
ya estan verificados en taxonomia.py, esto solo les asigna un ID estable, no crea taxonomia nueva.

Para especies NUEVAS: este script se puede reutilizar, pero requiere que scientific_name/genus/
family ya esten verificados por una fuente taxonomica real antes de invocarlo. Este script NO
verifica taxonomia, solo formaliza IDs sobre datos ya verificados.

LIFECYCLE (corregido — ver SPECIES_LIFECYCLE.md):
Una especie NUNCA se marca automaticamente como DEPLOYED por el simple hecho de recibir un
species_id. El estado inicial correcto para una especie nueva es DISCOVERED.

Para preservar el lifecycle de especies YA DEPLOYADAS (las 41 historicas via v1.0.0), este
script AUTO-DETECTA si `--out` ya existe: si existe, hereda el `visual_lifecycle_status` de
cada especie que ya estuviera presente (por species_id), y asigna DISCOVERED unicamente a las
especies que sean nuevas respecto de ese archivo previo. Esto significa que regenerar
taxonomy/species/species_registry.json (que ya tiene las 41 en DEPLOYED) produce el MISMO
resultado que antes para esas 41 — el comportamiento solo cambia para especies nuevas.

Usar --no-inherit-lifecycle para forzar DISCOVERED en todas (util para tests aislados).
Usar --previous-registry para heredar explicitamente desde OTRO archivo distinto de --out.
"""
import argparse
import importlib.util
import json
from pathlib import Path


def load_taxonomia_module(path: Path):
    spec = importlib.util.spec_from_file_location("taxonomia", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def species_code(scientific_name_underscored: str) -> tuple[str, str]:
    genero, *resto = scientific_name_underscored.split("_")
    especie_epiteto = "_".join(resto) if resto else genero
    genero_code = genero[:4].upper()
    especie_code = especie_epiteto[:3].upper()
    return genero_code, especie_code


def load_previous_lifecycle(previous_path: Path) -> dict:
    """Devuelve {species_id: visual_lifecycle_status} de un registry previo, o {} si no existe."""
    if not previous_path or not previous_path.exists():
        return {}
    with open(previous_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {s["species_id"]: s.get("visual_lifecycle_status", "DISCOVERED") for s in data.get("species", [])}


def build_registry(taxonomia_mod, source_label: str, previous_lifecycle: dict) -> list[dict]:
    especies = sorted(taxonomia_mod.ESPECIES)
    seen_codes: dict[str, int] = {}
    registry = []
    new_species_ids = []

    for especie in especies:
        genero = taxonomia_mod.genero_de(especie)
        familia = taxonomia_mod.familia_de(especie)
        genero_code, especie_code = species_code(especie)
        base_code = f"ANU_COL_{genero_code}_{especie_code}"
        seen_codes[base_code] = seen_codes.get(base_code, 0) + 1
        seq = seen_codes[base_code]
        species_id = f"{base_code}_{seq:03d}"

        # Lifecycle: heredar si ya existia (preserva historia), DISCOVERED si es especie nueva.
        # NUNCA se asigna DEPLOYED aqui — solo un catalog_release FROZEN + regional_package
        # puede llevar una especie a DEPLOYED (ver SPECIES_LIFECYCLE.md).
        if species_id in previous_lifecycle:
            lifecycle_status = previous_lifecycle[species_id]
        else:
            lifecycle_status = "DISCOVERED"
            new_species_ids.append(species_id)

        registry.append({
            "species_id": species_id,
            "scientific_name": especie.replace("_", " "),
            "family": familia,
            "genus": genero,
            "authority": None,
            "synonyms": [k for k, v in taxonomia_mod.ALIAS.items() if v == especie],
            "taxonomic_status": "ACCEPTED",
            "source": source_label,
            "verified_at": None,
            "visual_lifecycle_status": lifecycle_status
        })

    return registry, new_species_ids


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", default="training/taxonomia.py",
                     help="Ruta al modulo taxonomia.py (fuente de verdad ya existente)")
    ap.add_argument("--out", default="taxonomy/species/species_registry.json")
    ap.add_argument("--previous-registry", default=None,
                     help="Registry previo del cual heredar visual_lifecycle_status. "
                          "Por defecto se autodetecta usando --out si ya existe.")
    ap.add_argument("--no-inherit-lifecycle", action="store_true",
                     help="Ignora cualquier registry previo; todas las especies inician en DISCOVERED. "
                          "Util para tests aislados que no deben heredar estado historico.")
    args = ap.parse_args()

    source_path = Path(args.source).resolve()
    mod = load_taxonomia_module(source_path)

    if args.no_inherit_lifecycle:
        previous_lifecycle = {}
    else:
        previous_path = Path(args.previous_registry) if args.previous_registry else Path(args.out)
        previous_lifecycle = load_previous_lifecycle(previous_path)

    registry, new_species_ids = build_registry(mod, source_label=str(args.source), previous_lifecycle=previous_lifecycle)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({
            "generated_from": str(args.source),
            "species_count": len(registry),
            "species": registry
        }, f, indent=2, ensure_ascii=False)

    print(f"[OK] {len(registry)} species_id generados desde {args.source}")
    print(f"[OK] Guardado en {out_path}")
    print(f"[OK] Especies con lifecycle heredado (preservado): {len(registry) - len(new_species_ids)}")
    print(f"[OK] Especies NUEVAS iniciadas en DISCOVERED (nunca DEPLOYED automatico): {len(new_species_ids)}")
    for sid in new_species_ids:
        print(f"     - {sid}")

    codes = [s["species_id"] for s in registry]
    if len(codes) != len(set(codes)):
        print("[ERROR] Colisiones de species_id detectadas tras desambiguacion — revisar manualmente")
    else:
        print("[OK] Sin colisiones de species_id")


if __name__ == "__main__":
    main()
