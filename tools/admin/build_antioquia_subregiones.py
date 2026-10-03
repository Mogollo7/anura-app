"""
Municipios de Antioquia con su subregión y su código DANE, para Admin → Regiones.

Fuentes (todas reales, ya en el repo):
- geo/antioquia_municipios.geojson: los 125 polígonos DANE (MPIO_CCNCT, MPIO_CNMBR). El nombre
  de subregion.json es el de uso común, no siempre igual al oficial del DANE — ver ALIAS_DANE.
- COLOMBIA_ANURA/ANTIOQUIA/SUBREGIONS/*/subregion.json: qué municipios forman cada subregión.
- COLOMBIA_ANURA/ANTIOQUIA/MUNICIPALITIES/<codigo>_<NOMBRE>/: código DANE por nombre (115).

Salida:
- D:/server/Anura/services/geo-service/data/municipios_05.geojson (coordenadas a 4 decimales
  ≈ 11 m, suficiente para dibujar y para point-in-polygon).
- D:/server/Anura/infrastructure/postgres/seed_regiones_antioquia.sql (región y subregiones).

No inventa asignaciones: un municipio que no aparece en ninguna subregion.json queda sin
subregión y el script lo dice. Para los demás departamentos ver build_municipios_geojson.py.
"""
import json
import re
import unicodedata
from pathlib import Path

from nombres import titulo_espanol

ROOT = Path(r"D:\Anura")
GEO = ROOT / "geo" / "antioquia_municipios.geojson"
ANT = ROOT / "COLOMBIA_ANURA" / "ANTIOQUIA"
OUT_GEO = Path(r"D:\server\Anura\services\geo-service\data\municipios_05.geojson")
OUT_SQL = Path(r"D:\server\Anura\infrastructure\postgres\seed_regiones_antioquia.sql")

ORDEN = ["VALLE_DE_ABURRA", "ORIENTE", "SUROESTE", "OCCIDENTE", "NORTE", "NORDESTE", "MAGDALENA_MEDIO", "BAJO_CAUCA", "URABA"]
NOMBRE_SUB = {
    "VALLE_DE_ABURRA": "Valle de Aburrá", "ORIENTE": "Oriente", "SUROESTE": "Suroeste", "OCCIDENTE": "Occidente",
    "NORTE": "Norte", "NORDESTE": "Nordeste", "MAGDALENA_MEDIO": "Magdalena Medio", "BAJO_CAUCA": "Bajo Cauca", "URABA": "Urabá",
}

# Nombre de uso común (subregion.json) → código DANE, cuando el nombre oficial es otro.
ALIAS_DANE = {
    "El Peñol": "05541",                # DANE: Peñol
    "El Retiro": "05607",                # DANE: Retiro
    "San Vicente": "05674",              # DANE: San Vicente Ferrer
    "Carolina del Príncipe": "05150",    # DANE: Carolina
    "San Andrés de Cuerquia": "05647",   # DANE: San Andrés de Cuerquía
}


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^A-Z0-9]", "", s.upper())


def main():
    geo = json.loads(GEO.read_bytes().decode("utf-8"))
    feats = {f["properties"]["MPIO_CCNCT"]: f for f in geo["features"]}

    por_nombre = {}
    for d in (ANT / "MUNICIPALITIES").iterdir():
        codigo, _, nombre = d.name.partition("_")
        por_nombre[norm(nombre)] = codigo
    # No todos los municipios tienen carpeta en MUNICIPALITIES (esa solo se crea si el scraper
    # encontró registros); para esos, el nombre propio del DANE es la segunda fuente.
    por_nombre_dane = {norm(f["properties"]["MPIO_CNMBR"]): codigo for codigo, f in feats.items()}

    asignacion, nombres, sin_codigo = {}, {}, []
    for sub in ORDEN:
        data = json.loads((ANT / "SUBREGIONS" / sub / "subregion.json").read_text(encoding="utf-8"))
        for m in data["municipalities"]:
            codigo = ALIAS_DANE.get(m) or por_nombre.get(norm(m)) or por_nombre_dane.get(norm(m))
            if not codigo:
                sin_codigo.append((sub, m))
                continue
            asignacion[codigo] = sub
            nombres[codigo] = m

    sin_sub = sorted(c for c in feats if c not in asignacion)
    for codigo in sin_sub:
        nombres[codigo] = titulo_espanol(feats[codigo]["properties"]["MPIO_CNMBR"])

    def redondear(coords):
        if isinstance(coords[0], (int, float)):
            return [round(coords[0], 4), round(coords[1], 4)]
        return [redondear(c) for c in coords]

    salida = {"type": "FeatureCollection", "features": []}
    for codigo, f in sorted(feats.items()):
        salida["features"].append({
            "type": "Feature",
            "properties": {"codigo": codigo, "nombre": nombres[codigo], "departamento": "05"},
            "geometry": {"type": f["geometry"]["type"], "coordinates": redondear(f["geometry"]["coordinates"])},
        })
    OUT_GEO.write_text(json.dumps(salida, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    lineas = [
        "-- Generado por D:/Anura/tools/admin/build_antioquia_subregiones.py — no editar a mano.",
        "-- Antioquia y sus 9 subregiones (COLOMBIA_ANURA/ANTIOQUIA/SUBREGIONS/*/subregion.json).",
        "INSERT INTO dataset.region (codigo_dane, nombre, estado) VALUES ('05', 'Antioquia', 'activa') ON CONFLICT DO NOTHING;",
    ]
    for i, sub in enumerate(ORDEN, 1):
        lineas.append(
            f"INSERT INTO dataset.subregion (region, numero, clave, nombre) VALUES ('05', {i}, '{sub}', '{NOMBRE_SUB[sub]}') "
            "ON CONFLICT (region, clave) DO NOTHING;"
        )
    for codigo, sub in sorted(asignacion.items()):
        lineas.append(
            "INSERT INTO dataset.subregion_municipio (municipio_dane, subregion_id) "
            f"SELECT '{codigo}', id FROM dataset.subregion WHERE region = '05' AND clave = '{sub}' ON CONFLICT DO NOTHING;"
        )
    OUT_SQL.write_text("\n".join(lineas) + "\n", encoding="utf-8")

    print(f"{len(feats)} municipios en el geojson; {len(asignacion)} con subregión")
    if sin_codigo:
        print("Sin código DANE:", sin_codigo)
    if sin_sub:
        print("Sin subregión:", sin_sub)


if __name__ == "__main__":
    main()
