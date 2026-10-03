"""
Límites municipales de Colombia por departamento, para Admin → Regiones (pintar municipios
en subregiones de cualquier departamento, no solo Antioquia).

Fuente: DANE, Marco Geoestadístico Nacional (MGN) 2018, división político-administrativa.
El geojson de origen (`geo/colombia_municipios.geojson`, 1.122 municipios, campos
DPTO_CCDGO/MPIO_CCDGO/MPIO_CCNCT/MPIO_CNMBR/DPTO_CNMBR — mismo esquema que
`geo/antioquia_municipios.geojson`, ya usado y verificado en el proyecto) es una conversión a
GeoJSON del shapefile oficial del DANE publicada en
https://github.com/caticoa3/colombia_mapa (co_2018_MGN_MPIO_POLITICO.geojson). Se verificó
contra el archivo de Antioquia que el proyecto ya traía: los 125 códigos DANE y la geometría
(cajas delimitadoras) coinciden exactamente, así que es la misma fuente.

Antioquia (05) NO se regenera aquí: sigue su propio script
(`build_antioquia_subregiones.py`), que usa los nombres de uso común de
`COLOMBIA_ANURA/ANTIOQUIA/SUBREGIONS/*/subregion.json`. Este script cubre los otros 32
departamentos con el nombre oficial del DANE (en mayúsculas en el archivo de origen; aquí solo
se les da capitalización de título en español — nada se inventa, es la misma cadena del DANE).

Esto NO crea subregiones: solo deja el mapa de municipios disponible para que un administrador
las cree y las reparta a mano en Admin → Regiones (Pintar municipios), igual que ya se puede
hacer con Antioquia.

Salida: D:/server/Anura/services/geo-service/data/municipios_<DPTO>.geojson, uno por
departamento (excepto 05).
"""
import json
from pathlib import Path

from nombres import titulo_espanol

SRC = Path(r"D:\Anura\geo\colombia_municipios.geojson")
OUT_DIR = Path(r"D:\server\Anura\services\geo-service\data")
OMITIR = {"05"}  # Antioquia: la genera build_antioquia_subregiones.py con sus propios nombres.


def redondear(coords):
    if isinstance(coords[0], (int, float)):
        return [round(coords[0], 4), round(coords[1], 4)]
    return [redondear(c) for c in coords]


def main():
    geo = json.loads(SRC.read_bytes().decode("utf-8"))
    por_depto: dict[str, list] = {}
    for f in geo["features"]:
        por_depto.setdefault(f["properties"]["DPTO_CCDGO"], []).append(f)

    for depto, feats in sorted(por_depto.items()):
        if depto in OMITIR:
            continue
        salida = {"type": "FeatureCollection", "features": []}
        for f in sorted(feats, key=lambda f: f["properties"]["MPIO_CCNCT"]):
            p = f["properties"]
            salida["features"].append({
                "type": "Feature",
                "properties": {
                    "codigo": p["MPIO_CCNCT"],
                    "nombre": titulo_espanol(p["MPIO_CNMBR"]),
                    "departamento": depto,
                },
                "geometry": {"type": f["geometry"]["type"], "coordinates": redondear(f["geometry"]["coordinates"])},
            })
        (OUT_DIR / f"municipios_{depto}.geojson").write_text(
            json.dumps(salida, ensure_ascii=False, separators=(",", ":")), encoding="utf-8"
        )
        print(f"{depto} {feats[0]['properties']['DPTO_CNMBR'].title()}: {len(feats)} municipios")

    print(f"\n{sum(len(v) for k, v in por_depto.items() if k not in OMITIR)} municipios en "
          f"{len(por_depto) - len(OMITIR & por_depto.keys())} departamentos (Antioquia aparte).")


if __name__ == "__main__":
    main()
