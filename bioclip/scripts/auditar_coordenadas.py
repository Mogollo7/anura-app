"""Audita la calidad de las coordenadas usadas en el prior geográfico (Fase 6c)
antes de confiar en el resultado. Un radio de 50 km no significa nada si la
`positional_accuracy` de la observación ya es de decenas de km, y una
coordenada fuera de Colombia (o en (0,0), error clásico de scraping) puede
inflar o corromper el prior.

Genera un archivo de exclusión (obs_id con problema) para que Fase 6c pueda
filtrarlas y reportar el número limpio.

Uso:
    python bioclip/scripts/auditar_coordenadas.py
"""

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RAIZ_COORDS = Path(r"D:\Anura\data dirty")
SALIDA = Path(r"D:\Anura\bioclip\evaluation\coordenadas_auditoria.json")

# Bounding box de Colombia continental + insular, con margen
LAT_MIN, LAT_MAX = -4.5, 13.5
LON_MIN, LON_MAX = -82.0, -66.0

UMBRAL_ACCURACY_M = 10_000  # > 10 km de imprecisión invalida el uso en radio de 50km


def main():
    print(f"{'='*78}\nAUDITORÍA DE COORDENADAS\n{'='*78}")

    total = 0
    problemas = {
        "cero_o_nulo": [],
        "fuera_de_colombia": [],
        "accuracy_excesiva": [],
        "accuracy_ausente": 0,
        "duplicado_exacto": 0,
    }
    vistos = set()
    limpias = []
    accuracies = []

    for archivo in RAIZ_COORDS.glob("*/coordenadas_distribucion.json"):
        especie = archivo.parent.name
        try:
            registros = json.loads(archivo.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue

        for r in registros:
            total += 1
            oid = str(r.get("observation_id"))
            lat, lon = r.get("latitude"), r.get("longitude")
            acc = r.get("positional_accuracy")

            if lat is None or lon is None:
                continue

            lat, lon = float(lat), float(lon)

            if abs(lat) < 1e-6 and abs(lon) < 1e-6:
                problemas["cero_o_nulo"].append((especie, oid))
                continue

            if not (LAT_MIN <= lat <= LAT_MAX and LON_MIN <= lon <= LON_MAX):
                problemas["fuera_de_colombia"].append((especie, oid, lat, lon))
                continue

            if acc is None:
                problemas["accuracy_ausente"] += 1
            elif acc > UMBRAL_ACCURACY_M:
                problemas["accuracy_excesiva"].append((especie, oid, acc))
                continue
            else:
                accuracies.append(acc)

            clave = (lat, lon, oid)
            if clave in vistos:
                problemas["duplicado_exacto"] += 1
                continue
            vistos.add(clave)

            limpias.append({"especie": especie, "observation_id": oid, "lat": lat, "lon": lon,
                             "accuracy_m": acc})

    print(f"Registros totales leídos: {total:,}\n")
    print(f"{'PROBLEMA':<35}{'N':>10}")
    print("-" * 45)
    print(f"{'(0,0) o nulo':<35}{len(problemas['cero_o_nulo']):>10}")
    print(f"{'fuera del bounding box Colombia':<35}{len(problemas['fuera_de_colombia']):>10}")
    print(f"{'accuracy > '+str(UMBRAL_ACCURACY_M)+' m':<35}{len(problemas['accuracy_excesiva']):>10}")
    print(f"{'sin accuracy reportada':<35}{problemas['accuracy_ausente']:>10}")
    print(f"{'duplicado exacto (misma obs)':<35}{problemas['duplicado_exacto']:>10}")
    print("-" * 45)
    print(f"{'Coordenadas limpias utilizables':<35}{len(limpias):>10}  ({len(limpias)/total:.1%})")

    if accuracies:
        import statistics
        print(f"\npositional_accuracy (m) sobre las limpias:")
        print(f"  mediana = {statistics.median(accuracies):.0f}   "
              f"p90 = {sorted(accuracies)[int(len(accuracies)*0.9)]:.0f}   "
              f"máx = {max(accuracies):.0f}")

    if problemas["fuera_de_colombia"]:
        print(f"\nEjemplos fuera de Colombia (primeros 5):")
        for especie, oid, lat, lon in problemas["fuera_de_colombia"][:5]:
            print(f"  {especie:<28} obs_{oid}  lat={lat:.4f} lon={lon:.4f}")

    if problemas["accuracy_excesiva"]:
        print(f"\nEjemplos con accuracy excesiva (primeros 5):")
        for especie, oid, acc in sorted(problemas["accuracy_excesiva"], key=lambda x: -x[2])[:5]:
            print(f"  {especie:<28} obs_{oid}  accuracy={acc:.0f} m")

    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    SALIDA.write_text(json.dumps({
        "total": total,
        "n_limpias": len(limpias),
        "n_cero_o_nulo": len(problemas["cero_o_nulo"]),
        "n_fuera_de_colombia": len(problemas["fuera_de_colombia"]),
        "n_accuracy_excesiva": len(problemas["accuracy_excesiva"]),
        "n_accuracy_ausente": problemas["accuracy_ausente"],
        "n_duplicado_exacto": problemas["duplicado_exacto"],
        "obs_ids_excluir": sorted(set(
            [oid for _, oid in problemas["cero_o_nulo"]]
            + [oid for _, oid, *_ in problemas["fuera_de_colombia"]]
            + [oid for _, oid, _ in problemas["accuracy_excesiva"]]
        )),
        "coordenadas_limpias": limpias,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nGuardado en {SALIDA}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
