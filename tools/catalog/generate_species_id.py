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


def build_registry(taxonomia_mod, source_label: str) -> list[dict]:
    especies = sorted(taxonomia_mod.ESPECIES)
    seen_codes: dict[str, int] = {}
    registry = []

    for especie in especies:
        genero = taxonomia_mod.genero_de(especie)
        familia = taxonomia_mod.familia_de(especie)
        genero_code, especie_code = species_code(especie)
        base_code = f"ANU_COL_{genero_code}_{especie_code}"
        seen_codes[base_code] = seen_codes.get(base_code, 0) + 1
        seq = seen_codes[base_code]
        species_id = f"{base_code}_{seq:03d}"

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
            "visual_lifecycle_status": "DEPLOYED"
        })

    return registry


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source", default="training/taxonomia.py",
                     help="Ruta al modulo taxonomia.py (fuente de verdad ya existente)")
    ap.add_argument("--out", default="taxonomy/species/species_registry.json")
    args = ap.parse_args()

    source_path = Path(args.source).resolve()
    mod = load_taxonomia_module(source_path)
    registry = build_registry(mod, source_label=str(args.source))

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

    codes = [s["species_id"] for s in registry]
    if len(codes) != len(set(codes)):
        print("[ERROR] Colisiones de species_id detectadas tras desambiguacion — revisar manualmente")
    else:
        print("[OK] Sin colisiones de species_id")


if __name__ == "__main__":
    main()
