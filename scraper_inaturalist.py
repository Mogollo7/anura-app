#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
ANURA iNaturalist Extractor & Scraper
==============================================================================
Herramienta integral para extracción de:
 1. Árbol taxonómico en JSON (Familia, Género, Especie y nombres comunes).
 2. Muestras de audio a nivel global (meta mínima de 70 o todas las disponibles).
 3. Fotos registradas en Colombia (mínimo 70, con fallback regional/global si falta).
 4. Coordenadas de avistamiento en Colombia y mapas de distribución interactivos (HTML/Leaflet).
 5. Auditoría de especies con déficit de datos (fotos < 70 o audios < 70).

Todo se almacena organizado en la carpeta especificada (por defecto: 'data dirty').
==============================================================================
"""

import os
import sys
import time
import json
import csv
import argparse
import re
from typing import Dict, List, Any, Optional, Tuple
from urllib.parse import quote

# Asegurar codificación utf-8 en terminal de Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import requests
from tqdm import tqdm



# Constantes y Configuración
INAT_API_BASE = "https://api.inaturalist.org/v1"
COLOMBIA_PLACE_ID = 7196
DEFAULT_USER_AGENT = "AnuraScraper/1.0 (Amphibian Research Pipeline - Colombia; contact@anura.org)"
DEFAULT_OUTPUT_DIR = "data dirty"


def sanitize_filename(name: str) -> str:
    """Convierte un nombre de especie en un nombre de carpeta seguro."""
    return re.sub(r'[\\/*?:"<>| ]', '_', name.strip())


def is_tadpole_observation(observation: Dict[str, Any]) -> bool:
    """Detecta la anotación controlada de etapa de vida renacuajo."""
    for annotation in observation.get("annotations", []):
        attribute = annotation.get("controlled_attribute", {})
        value = annotation.get("controlled_value", {})
        attribute_text = str(attribute.get("label", "")).lower()
        value_text = str(value.get("label", "")).lower()
        if attribute_text in {"life stage", "etapa de vida", "stage"} and value_text in {
            "tadpole", "renacuajo", "larva", "larvae"
        }:
            return True
    return False


def observation_sex(observation: Dict[str, Any]) -> Optional[str]:
    """Obtiene el sexo controlado por iNaturalist sin inferirlo visualmente."""
    sex = observation.get("sex")
    if sex:
        return str(sex)
    for annotation in observation.get("annotations", []):
        attribute = annotation.get("controlled_attribute", {})
        value = annotation.get("controlled_value", {})
        if str(attribute.get("label", "")).lower() in {"sex", "sexo"}:
            label = value.get("label")
            if label:
                return str(label)
    return None


class INaturalistScraper:
    def __init__(
        self,
        output_dir: str = DEFAULT_OUTPUT_DIR,
        min_photos: int = 70,
        min_sounds: int = 70,
        max_photos: Optional[int] = None,
        max_sounds: Optional[int] = None,
        request_delay: float = 1.0,
        dry_run: bool = False,
        user_agent: str = DEFAULT_USER_AGENT,
        skip_audio: bool = False,
        quality_grade: Optional[str] = "research"
    ):
        self.output_dir = output_dir
        self.min_photos = min_photos
        self.min_sounds = min_sounds
        self.max_photos = max_photos
        self.max_sounds = max_sounds
        self.request_delay = request_delay
        self.dry_run = dry_run
        self.skip_audio = skip_audio
        if quality_grade not in {None, "research", "needs_id", "casual"}:
            raise ValueError("quality_grade debe ser research, needs_id, casual o None")
        self.quality_grade = quality_grade
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": user_agent})

        os.makedirs(self.output_dir, exist_ok=True)

    def _api_get(self, endpoint: str, params: Optional[Dict[str, Any]] = None, max_retries: int = 4) -> Optional[Dict[str, Any]]:
        """Realiza peticiones GET a la API con reintentos y respeto de rate-limits."""
        url = f"{INAT_API_BASE}/{endpoint.lstrip('/')}"
        params = params or {}
        
        for attempt in range(max_retries):
            try:
                time.sleep(self.request_delay)
                response = self.session.get(url, params=params, timeout=30)
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:
                    wait_sec = (attempt + 1) * 3
                    print(f"  [!] Rate limit de iNaturalist alcanzado (429). Pausando {wait_sec}s...")
                    time.sleep(wait_sec)
                elif response.status_code >= 500:
                    wait_sec = (attempt + 1) * 2
                    print(f"  [!] Error servidor iNaturalist ({response.status_code}). Reintentando en {wait_sec}s...")
                    time.sleep(wait_sec)
                else:
                    print(f"  [!] Error {response.status_code} al consultar {url}: {response.text[:120]}")
                    return None
            except requests.RequestException as e:
                wait_sec = (attempt + 1) * 2
                print(f"  [!] Error de red ({e}). Reintentando en {wait_sec}s...")
                time.sleep(wait_sec)
                
        return None

    def _download_file(self, url: str, dest_path: str) -> bool:
        """Descarga un archivo si no existe ya localmente."""
        if self.dry_run:
            return True
            
        if os.path.exists(dest_path) and os.path.getsize(dest_path) > 0:
            return True  # Ya descargado previamente

        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        
        try:
            with self.session.get(url, stream=True, timeout=30) as r:
                if r.status_code == 200:
                    with open(dest_path, "wb") as f:
                        for chunk in r.iter_content(chunk_size=32768):
                            if chunk:
                                f.write(chunk)
                    return True
                elif r.status_code == 404:
                    return False
        except Exception as e:
            print(f"    [!] Error descargando {url}: {e}")
            if os.path.exists(dest_path):
                try:
                    os.remove(dest_path)
                except OSError:
                    pass
        return False

    def search_taxon(self, species_name: str) -> Optional[Dict[str, Any]]:
        """Busca el taxón por nombre científico, extrayendo detalles y ancestros."""
        print(f"\n[*] Buscando taxón: '{species_name}'...")
        res = self._api_get("taxa", params={"q": species_name, "rank": "species", "locale": "es"})
        
        if not res or not res.get("results"):
            # Intento de búsqueda general sin restricción estricta de rango
            res = self._api_get("taxa", params={"q": species_name, "locale": "es"})
            if not res or not res.get("results"):
                print(f"  [-] No se encontró el taxón '{species_name}' en iNaturalist.")
                return None

        # Priorizar coincidencia exacta de nombre
        matched = None
        for t in res["results"]:
            if t.get("name", "").lower() == species_name.lower():
                matched = t
                break
        if not matched:
            matched = res["results"][0]

        taxon_id = matched["id"]
        # Obtener detalle completo para asegurar lista exhaustiva de ancestros
        detail = self._api_get(f"taxa/{taxon_id}", params={"locale": "es"})
        if detail and detail.get("results"):
            return detail["results"][0]
        return matched

    def parse_taxonomy(self, taxon: Dict[str, Any]) -> Dict[str, Any]:
        """Extrae el orden, familia, género y especie con nombres científicos y comunes."""
        ancestors = taxon.get("ancestors", [])
        
        family_sci = None
        family_com = None
        genus_sci = None
        genus_com = None
        order_sci = None
        order_com = None

        for a in ancestors:
            rank = a.get("rank")
            if rank == "order":
                order_sci = a.get("name")
                order_com = a.get("preferred_common_name")
            elif rank == "family":
                family_sci = a.get("name")
                family_com = a.get("preferred_common_name")
            elif rank == "genus":
                genus_sci = a.get("name")
                genus_com = a.get("preferred_common_name")

        # Si el género no estaba en ancestros pero es detectable por el binomio
        if not genus_sci and taxon.get("name"):
            parts = taxon.get("name").split()
            if len(parts) >= 2:
                genus_sci = parts[0]

        species_sci = taxon.get("name")
        species_com = taxon.get("preferred_common_name") or taxon.get("english_common_name")

        return {
            "taxon_id": taxon.get("id"),
            "scientific_name": species_sci,
            "species_common_name": species_com,
            "genus_scientific_name": genus_sci,
            "genus_common_name": genus_com,
            "family_scientific_name": family_sci,
            "family_common_name": family_com,
            "order_scientific_name": order_sci or "Anura",
            "order_common_name": order_com or "Ranas y sapos",
            "iconic_taxon_name": taxon.get("iconic_taxon_name"),
            "observations_count": taxon.get("observations_count", 0),
            "wikipedia_url": taxon.get("wikipedia_url")
        }

    def fetch_sounds(self, taxon_id: int, species_dir: str) -> Tuple[int, List[Dict[str, Any]]]:
        """Descarga todos los audios posibles a nivel global (objetivo >= min_sounds)."""
        print(f"  [+] Extrayendo audios (ámbito global)...")
        sounds_dir = os.path.join(species_dir, "sonidos")
        os.makedirs(sounds_dir, exist_ok=True)
        
        sound_records = []
        page = 1
        per_page = 50
        downloaded = 0
        total_available = 0

        while True:
            params = {
                "taxon_id": taxon_id,
                "has[]": "sounds",
                "per_page": per_page,
                "page": page,
                "order_by": "id",
                "order": "desc"
            }
            if self.quality_grade:
                params["quality_grade"] = self.quality_grade
            res = self._api_get("observations", params=params)
            if not res or not res.get("results"):
                break
                
            total_available = res.get("total_results", 0)
            results = res["results"]
            
            for obs in results:
                obs_id = obs.get("id")
                if is_tadpole_observation(obs):
                    continue
                location_str = obs.get("location")
                place_guess = obs.get("place_guess", "")
                
                for s in obs.get("sounds", []):
                    sound_id = s.get("id")
                    file_url = s.get("file_url")
                    if not file_url:
                        continue
                        
                    ext = ".mp3"
                    if "audio/wav" in str(s.get("file_content_type")):
                        ext = ".wav"
                    elif "audio/mp4" in str(s.get("file_content_type")) or "m4a" in file_url:
                        ext = ".m4a"
                        
                    filename = f"obs_{obs_id}_sound_{sound_id}{ext}"
                    dest_path = os.path.join(sounds_dir, filename)
                    
                    success = self._download_file(file_url, dest_path)
                    if success:
                        downloaded += 1
                        sound_records.append({
                            "sound_id": sound_id,
                            "observation_id": obs_id,
                            "file_name": filename,
                            "file_url": file_url,
                            "content_type": s.get("file_content_type"),
                            "license": s.get("license_code"),
                            "attribution": s.get("attribution"),
                            "place_guess": place_guess,
                            "location": location_str,
                            "observed_on": obs.get("observed_on")
                        })
                    
                    if self.max_sounds and downloaded >= self.max_sounds:
                        break
                if self.max_sounds and downloaded >= self.max_sounds:
                    break

            if len(results) < per_page:
                break
            page += 1

        # Guardar metadatos de audios
        meta_file = os.path.join(species_dir, "sonidos_metadata.json")
        with open(meta_file, "w", encoding="utf-8") as f:
            json.dump({
                "total_available_in_inaturalist": total_available,
                "total_downloaded": downloaded,
                "sounds": sound_records
            }, f, indent=2, ensure_ascii=False)

        print(f"  [✓] Audios descargados: {downloaded} (Disponibles globales: {total_available})")
        return downloaded, sound_records

    def fetch_photos_and_coordinates(
        self, taxon_id: int, species_dir: str
    ) -> Tuple[int, int, List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Descarga fotos de Colombia y extrae coordenadas para distribución.
        Si en Colombia hay menos de min_photos, amplía la búsqueda globalmente.
        """
        photos_dir = os.path.join(species_dir, "fotos")
        os.makedirs(photos_dir, exist_ok=True)
        
        coordinates_list: List[Dict[str, Any]] = []
        photo_records: List[Dict[str, Any]] = []
        colombia_photos_count = 0
        seen_obs_ids = set()

        # 1. BÚSQUEDA EN COLOMBIA
        print(f"  [+] Extrayendo fotos y coordenadas en Colombia (place_id={COLOMBIA_PLACE_ID})...")
        page = 1
        per_page = 50

        while True:
            params = {
                "taxon_id": taxon_id,
                "place_id": COLOMBIA_PLACE_ID,
                "has[]": "photos",
                "per_page": per_page,
                "page": page,
                "order_by": "id",
                "order": "desc"
            }
            if self.quality_grade:
                params["quality_grade"] = self.quality_grade
            res = self._api_get("observations", params=params)
            if not res or not res.get("results"):
                break
                
            results = res["results"]
            
            for obs in results:
                obs_id = obs.get("id")
                seen_obs_ids.add(obs_id)
                
                # Extraer coordenadas geográficas para mapa de distribución
                loc_str = obs.get("location")
                if loc_str and "," in loc_str:
                    try:
                        lat_val, lng_val = map(float, loc_str.split(","))
                        coordinates_list.append({
                            "observation_id": obs_id,
                            "latitude": lat_val,
                            "longitude": lng_val,
                            "positional_accuracy": obs.get("positional_accuracy"),
                            "observed_on": obs.get("observed_on"),
                            "place_guess": obs.get("place_guess", ""),
                            "user_login": obs.get("user", {}).get("login", ""),
                            "url": obs.get("uri")
                        })
                    except (ValueError, TypeError):
                        pass

                # Descargar fotos de esta observación en Colombia (si aún no alcanzamos el límite deseado)
                need_more_photos = (self.max_photos is None) or (len(photo_records) < self.max_photos)
                if need_more_photos:
                    for p in obs.get("photos", []):
                        if self.max_photos and len(photo_records) >= self.max_photos:
                            break
                        photo_id = p.get("id")
                        sq_url = p.get("url")
                        if not sq_url:
                            continue
                        
                        # Probar original -> large -> medium
                        best_url = sq_url.replace("/square.", "/original.")
                        dest_file = f"col_obs_{obs_id}_photo_{photo_id}.jpg"
                        dest_path = os.path.join(photos_dir, dest_file)
                        
                        success = self._download_file(best_url, dest_path)
                        if not success:
                            best_url = sq_url.replace("/square.", "/large.")
                            success = self._download_file(best_url, dest_path)
                        if not success:
                            best_url = sq_url.replace("/square.", "/medium.")
                            success = self._download_file(best_url, dest_path)
                            
                        if success:
                            colombia_photos_count += 1
                            photo_records.append({
                                "photo_id": photo_id,
                                "observation_id": obs_id,
                                "file_name": dest_file,
                                "url": best_url,
                                "origin": "Colombia",
                                "attribution": p.get("attribution"),
                                "license_code": p.get("license_code"),
                                "place_guess": obs.get("place_guess"),
                                "observed_on": obs.get("observed_on"),
                                "sexo": observation_sex(obs),
                                "life_stage": "adult_or_unannotated"
                            })

            if len(results) < per_page or page >= 20:
                break
            page += 1

        print(f"  [✓] Fotos obtenidas en Colombia: {colombia_photos_count} (Coordenadas registradas: {len(coordinates_list)})")

        # 2. FALLBACK SI NO SE ALCANZA EL MÍNIMO REQUERIDO
        fallback_count = 0
        target_goal = self.min_photos
        if self.max_photos is not None and self.max_photos < target_goal:
            target_goal = self.max_photos

        if len(photo_records) < target_goal:
            print(f"  [!] Fotos en Colombia ({colombia_photos_count}) < {target_goal}. Activando fallback regional/global para alcanzar {target_goal}...")
            
            f_page = 1
            while len(photo_records) < target_goal:
                params = {
                    "taxon_id": taxon_id,
                    "has[]": "photos",
                    "per_page": 50,
                    "page": f_page,
                    "order_by": "id",
                    "order": "desc"
                }
                if self.quality_grade:
                    params["quality_grade"] = self.quality_grade
                res = self._api_get("observations", params=params)
                if not res or not res.get("results"):
                    break
                    
                results = res["results"]
                for obs in results:
                    obs_id = obs.get("id")
                    if is_tadpole_observation(obs):
                        continue
                    if obs_id in seen_obs_ids:
                        continue  # Ya procesada en Colombia
                    seen_obs_ids.add(obs_id)
                    
                    for p in obs.get("photos", []):
                        photo_id = p.get("id")
                        sq_url = p.get("url")
                        if not sq_url:
                            continue
                            
                        best_url = sq_url.replace("/square.", "/large.")
                        dest_file = f"fallback_obs_{obs_id}_photo_{photo_id}.jpg"
                        dest_path = os.path.join(photos_dir, dest_file)
                        
                        success = self._download_file(best_url, dest_path)
                        if success:
                            fallback_count += 1
                            photo_records.append({
                                "photo_id": photo_id,
                                "observation_id": obs_id,
                                "file_name": dest_file,
                                "url": best_url,
                                "origin": "Fallback_Internacional",
                                "attribution": p.get("attribution"),
                                "license_code": p.get("license_code"),
                                "place_guess": obs.get("place_guess"),
                                "observed_on": obs.get("observed_on"),
                                "sexo": observation_sex(obs),
                                "life_stage": "adult_or_unannotated"
                            })
                            
                        if len(photo_records) >= target_goal:
                            break
                    if len(photo_records) >= target_goal:
                        break

                if len(results) < 50:
                    break
                f_page += 1

            print(f"  [✓] Fotos adicionales obtenidas por fallback: {fallback_count} (Total fotos: {len(photo_records)})")

        # Guardar metadatos de fotos
        meta_photos = os.path.join(species_dir, "fotos_metadata.json")
        with open(meta_photos, "w", encoding="utf-8") as f:
            json.dump({
                "fotos_colombia": colombia_photos_count,
                "fotos_fallback": fallback_count,
                "total_fotos": len(photo_records),
                "photos": photo_records
            }, f, indent=2, ensure_ascii=False)

        # Guardar coordenadas de distribución
        coord_json = os.path.join(species_dir, "coordenadas_distribucion.json")
        with open(coord_json, "w", encoding="utf-8") as f:
            json.dump(coordinates_list, f, indent=2, ensure_ascii=False)

        coord_csv = os.path.join(species_dir, "coordenadas_distribucion.csv")
        if coordinates_list:
            keys = ["observation_id", "latitude", "longitude", "positional_accuracy", "observed_on", "place_guess", "user_login", "url"]
            with open(coord_csv, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(coordinates_list)

        return colombia_photos_count, len(photo_records), photo_records, coordinates_list

    def generate_species_map(self, species_name: str, coordinates: List[Dict[str, Any]], species_dir: str):
        """Genera un mapa HTML interactivo usando Leaflet para la especie en Colombia."""
        map_path = os.path.join(species_dir, "mapa_distribucion.html")
        
        points_js = json.dumps(coordinates, ensure_ascii=False)
        
        html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mapa de Distribución - {species_name}</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
        body, html {{ margin: 0; padding: 0; height: 100%; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }}
        #header {{
            background: #1b4332;
            color: white;
            padding: 12px 20px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        #header h1 {{ margin: 0; font-size: 1.2rem; font-style: italic; }}
        #header .badge {{
            background: #40916c;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 0.85rem;
            font-style: normal;
        }}
        #map {{ height: calc(100% - 50px); width: 100%; }}
        .leaflet-popup-content {{ font-size: 0.9rem; line-height: 1.4; }}
        .popup-title {{ font-weight: bold; color: #2d6a4f; margin-bottom: 4px; }}
    </style>
</head>
<body>
    <div id="header">
        <h1>Mapa de Distribución: {species_name}</h1>
        <span class="badge">{len(coordinates)} registros en Colombia</span>
    </div>
    <div id="map"></div>

    <script>
        var map = L.map('map').setView([4.5709, -74.2973], 6);

        L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
            maxZoom: 18,
            attribution: '© OpenStreetMap contributors | iNaturalist'
        }}).addTo(map);

        var points = {points_js};
        var markers = [];

        points.forEach(function(pt) {{
            if (pt.latitude && pt.longitude) {{
                var marker = L.circleMarker([pt.latitude, pt.longitude], {{
                    radius: 6,
                    fillColor: "#e63946",
                    color: "#ffffff",
                    weight: 1.5,
                    opacity: 1,
                    fillOpacity: 0.85
                }});

                var popupContent = '<div class="popup-title">' + (pt.place_guess || 'Avistamiento') + '</div>' +
                    '<b>Lat:</b> ' + pt.latitude.toFixed(4) + '<br>' +
                    '<b>Lng:</b> ' + pt.longitude.toFixed(4) + '<br>' +
                    '<b>Fecha:</b> ' + (pt.observed_on || 'Desconocida') + '<br>' +
                    '<b>Usuario:</b> ' + (pt.user_login || 'N/A') + '<br>' +
                    (pt.url ? '<a href="' + pt.url + '" target="_blank">Ver en iNaturalist</a>' : '');

                marker.bindPopup(popupContent);
                marker.addTo(map);
                markers.push([pt.latitude, pt.longitude]);
            }}
        }});

        if (markers.length > 0) {{
            var bounds = L.latLngBounds(markers);
            map.fitBounds(bounds, {{ padding: [30, 30] }});
        }}
    </script>
</body>
</html>
"""
        with open(map_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"  [✓] Mapa generado: {map_path}")

    def generate_master_map(self, all_species_data: List[Dict[str, Any]]):
        """Genera un mapa interactivo consolidado con capas seleccionables para todas las especies."""
        master_path = os.path.join(self.output_dir, "mapa_distribucion_general.html")
        
        # Paleta de colores atractiva para distinguir especies
        colors = [
            "#e63946", "#1d3557", "#2a9d8f", "#f4a261", "#e76f51",
            "#7209b7", "#3a0ca3", "#4361ee", "#4cc9f0", "#06d6a0",
            "#ffb703", "#fb8500", "#6b705c", "#b5838d", "#6d597a"
        ]

        species_layers = []
        for idx, sp in enumerate(all_species_data):
            coords = sp.get("coordinates", [])
            color = colors[idx % len(colors)]
            species_layers.append({
                "species_name": sp["scientific_name"],
                "common_name": sp.get("common_name", ""),
                "color": color,
                "count": len(coords),
                "points": coords
            })

        layers_json = json.dumps(species_layers, ensure_ascii=False)

        html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mapa General de Distribución de Anuros - Colombia</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
        body, html {{ margin: 0; padding: 0; height: 100%; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }}
        #header {{
            background: #0f2027;
            background: linear-gradient(to right, #2c5364, #203a43, #0f2027);
            color: white;
            padding: 12px 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        #header h1 {{ margin: 0; font-size: 1.3rem; }}
        #map {{ height: calc(100% - 55px); width: 100%; }}
        .leaflet-control-layers {{ font-size: 0.9rem; }}
    </style>
</head>
<body>
    <div id="header">
        <h1>🐸 Distribución de Anuros en Colombia (iNaturalist)</h1>
        <span>Total Especies: {len(all_species_data)}</span>
    </div>
    <div id="map"></div>

    <script>
        var map = L.map('map').setView([4.5709, -74.2973], 6);

        var osm = L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
            maxZoom: 18,
            attribution: '© OpenStreetMap contributors'
        }}).addTo(map);

        var topo = L.tileLayer('https://{{s}}.tile.opentopomap.org/{{z}}/{{x}}/{{y}}.png', {{
            maxZoom: 17,
            attribution: '© OpenTopoMap contributors'
        }});

        var baseMaps = {{
            "OpenStreetMap": osm,
            "Topográfico": topo
        }};

        var overlayMaps = {{}};
        var data = {layers_json};
        var allMarkers = [];

        data.forEach(function(sp) {{
            var group = L.layerGroup();
            sp.points.forEach(function(pt) {{
                if (pt.latitude && pt.longitude) {{
                    var marker = L.circleMarker([pt.latitude, pt.longitude], {{
                        radius: 5,
                        fillColor: sp.color,
                        color: "#ffffff",
                        weight: 1,
                        opacity: 1,
                        fillOpacity: 0.8
                    }});
                    var popup = '<b><i>' + sp.species_name + '</i></b> (' + sp.common_name + ')<br>' +
                                '<b>Lugar:</b> ' + (pt.place_guess || 'N/A') + '<br>' +
                                '<b>Fecha:</b> ' + (pt.observed_on || 'N/A') + '<br>' +
                                (pt.url ? '<a href="' + pt.url + '" target="_blank">Ver Registro</a>' : '');
                    marker.bindPopup(popup);
                    group.addLayer(marker);
                    allMarkers.push([pt.latitude, pt.longitude]);
                }}
            }});
            group.addTo(map);
            var label = '<span style="color:' + sp.color + '">●</span> <i>' + sp.species_name + '</i> (' + sp.count + ')';
            overlayMaps[label] = group;
        }});

        L.control.layers(baseMaps, overlayMaps, {{ collapsed: false }}).addTo(map);

        if (allMarkers.length > 0) {{
            map.fitBounds(L.latLngBounds(allMarkers), {{ padding: [30, 30] }});
        }}
    </script>
</body>
</html>
"""
        with open(master_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"\n[✓] Mapa general interactivo guardado en: {master_path}")

    def build_taxonomic_tree_json(self, species_taxonomies: List[Dict[str, Any]]):
        """
        Construye y guarda el árbol taxonómico completo consolidado:
        Order Anura -> Families -> Genera -> Species (con nombres científicos y comunes).
        """
        tree = {
            "order": "Anura",
            "common_name": "Ranas y sapos",
            "total_species": len(species_taxonomies),
            "families": {}
        }

        for tax in species_taxonomies:
            fam_sci = tax.get("family_scientific_name") or "Familia no determinada"
            fam_com = tax.get("family_common_name")
            gen_sci = tax.get("genus_scientific_name") or "Género no determinado"
            gen_com = tax.get("genus_common_name")
            sp_sci = tax.get("scientific_name")
            sp_com = tax.get("species_common_name")
            t_id = tax.get("taxon_id")

            if fam_sci not in tree["families"]:
                tree["families"][fam_sci] = {
                    "scientific_name": fam_sci,
                    "common_name": fam_com,
                    "genera": {}
                }

            if gen_sci not in tree["families"][fam_sci]["genera"]:
                tree["families"][fam_sci]["genera"][gen_sci] = {
                    "scientific_name": gen_sci,
                    "common_name": gen_com,
                    "species": []
                }

            tree["families"][fam_sci]["genera"][gen_sci]["species"].append({
                "scientific_name": sp_sci,
                "common_name": sp_com,
                "taxon_id": t_id
            })

        tree_path = os.path.join(self.output_dir, "arbol_taxonomico.json")
        with open(tree_path, "w", encoding="utf-8") as f:
            json.dump(tree, f, indent=2, ensure_ascii=False)
        print(f"\n[✓] Árbol taxonómico consolidado guardado en: {tree_path}")

    def _detect_persistent_tree_errors(self) -> List[Dict[str, Any]]:
        """Compara el árbol consolidado con los metadatos individuales."""
        tree_path = os.path.join(self.output_dir, "arbol_taxonomico.json")
        if not os.path.exists(tree_path):
            return []

        with open(tree_path, "r", encoding="utf-8") as f:
            tree = json.load(f)

        errors: List[Dict[str, Any]] = []
        for family in tree.get("families", {}).values():
            for genus in family.get("genera", {}).values():
                for species in genus.get("species", []):
                    scientific_name = species.get("scientific_name")
                    species_dir = os.path.join(
                        self.output_dir, sanitize_filename(scientific_name or "")
                    )
                    taxon_path = os.path.join(species_dir, "taxon_info.json")
                    if not os.path.exists(taxon_path):
                        errors.append({
                            "tipo": "DATOS_DE_ESPECIE_AUSENTES",
                            "especie": scientific_name,
                            "detalle": "La especie está en el árbol taxonómico pero no tiene carpeta de datos."
                        })
                        continue

                    with open(taxon_path, "r", encoding="utf-8") as f:
                        taxon = json.load(f)

                    if species.get("taxon_id") != taxon.get("taxon_id"):
                        errors.append({
                            "tipo": "CLAVE_TAXONOMICA_INCONSISTENTE",
                            "especie": scientific_name,
                            "ruta_datos": os.path.abspath(species_dir),
                            "detalle": (
                                "La clave del árbol taxonómico no coincide con taxon_info.json: "
                                f"árbol={species.get('taxon_id')}, datos={taxon.get('taxon_id')}."
                            )
                        })

                    if not species.get("common_name") and not taxon.get("species_common_name"):
                        errors.append({
                            "tipo": "NOMBRE_COMUN_AUSENTE",
                            "especie": scientific_name,
                            "ruta_datos": os.path.abspath(species_dir),
                            "detalle": "No hay nombre común disponible en el árbol ni en taxon_info.json."
                        })

        return errors

    def generate_audit_report(self, audit_records: List[Dict[str, Any]]):
        """
        Genera un reporte de auditoría legible con los campos requeridos por especie.
        Una especie cumple cuando el taxón es válido y alcanza los umbrales de fotos
        totales y audios. Los errores persistentes son inconsistencias estructurales de
        los datos, no simples déficits temporales de contenido.
        """
        persistent_tree_errors = self._detect_persistent_tree_errors()
        persistent_tree_errors_by_species = {}
        for error in persistent_tree_errors:
            species_name = error.get("especie")
            if species_name:
                persistent_tree_errors_by_species.setdefault(species_name, []).append(error)
        audit_views = []

        for record in audit_records:
            taxonomy = record.get("taxonomy") or {}
            data_path = record.get("data_path") or ""
            scientific_name = record.get("scientific_name") or taxonomy.get("scientific_name") or "N/A"
            common_name = record.get("common_name") or taxonomy.get("species_common_name")
            family = record.get("family") or taxonomy.get("family_scientific_name")
            family_common = taxonomy.get("family_common_name")
            genus = record.get("genus") or taxonomy.get("genus_scientific_name")
            genus_common = taxonomy.get("genus_common_name")
            taxon_id = taxonomy.get("taxon_id")
            observations_count = taxonomy.get("observations_count", 0)
            photos_colombia = int(record.get("photos_colombia") or 0)
            photos_fallback = int(record.get("photos_fallback") or 0)
            photos_total = int(record.get("photos_total") or 0)
            audio_count = int(record.get("audio_count") or 0)
            coordinates_count = int(record.get("coordinates_count") or 0)
            status = record.get("status") or "NOT_FOUND"

            persistent_errors = list(record.get("persistent_errors") or [])
            persistent_errors.extend(record.get("metadata_errors") or [])
            for tree_error in persistent_tree_errors_by_species.get(scientific_name, []):
                persistent_errors.append(tree_error.get("detalle") or tree_error.get("tipo"))
            if status != "OK":
                persistent_errors.append(f"Estado del taxón: {status}")
            if not data_path:
                persistent_errors.append("Ruta de datos no disponible")
            if not taxon_id:
                persistent_errors.append("Clave taxonómica ausente")
            if not scientific_name or scientific_name == "N/A":
                persistent_errors.append("Nombre científico ausente")
            if not family:
                persistent_errors.append("Familia ausente")
            if not genus:
                persistent_errors.append("Género ausente")
            if not common_name:
                persistent_errors.append("Nombre común ausente")

            persistent_errors = list(dict.fromkeys(persistent_errors))
            cumple = (
                status == "OK"
                and photos_total >= self.min_photos
                and audio_count >= self.min_sounds
            )
            problems = []
            if status != "OK":
                problems.append(f"Taxón no encontrado o estado inválido ({status})")
            if audio_count == 0:
                problems.append("Sin audios (0)")
            elif audio_count < self.min_sounds:
                problems.append(f"Audios insuficientes ({audio_count}/{self.min_sounds})")
            if photos_colombia < self.min_photos:
                problems.append(
                    f"Fotos de Colombia insuficientes ({photos_colombia}/{self.min_photos}); "
                    "se usó fallback internacional"
                )
            if photos_total < self.min_photos:
                problems.append(f"Fotos totales insuficientes ({photos_total}/{self.min_photos})")
            if persistent_errors:
                problems.append("Error persistente: " + "; ".join(persistent_errors))

            view = dict(record)
            view.update({
                "ruta_datos": os.path.abspath(data_path) if data_path else None,
                "nombre_especie": scientific_name,
                "clave_taxonomica": taxon_id,
                "familia": family,
                "familia_nombre_comun": family_common,
                "genero": genus,
                "genero_nombre_comun": genus_common,
                "especie_nombre_cientifico": scientific_name,
                "especie_nombre_comun": common_name,
                "numero_individuos": observations_count,
                "numero_fotos": photos_total,
                "numero_fotos_colombia": photos_colombia,
                "numero_fotos_fallback": photos_fallback,
                "numero_audios": audio_count,
                "numero_puntos_distribucion": coordinates_count,
                "cumple": cumple,
                "estado": "CUMPLE" if cumple else "NO_CUMPLE",
                "error_persistente": bool(persistent_errors),
                "errores_persistentes": persistent_errors,
                "problemas_detectados": problems,
                "has_deficiencies": not cumple
            })
            audit_views.append(view)

        problematic_species = [
            view for view in audit_views
            if not view["cumple"] or view["error_persistente"]
        ]
        persistent_species = [view for view in audit_views if view["error_persistente"]]
        persistent_species_names = {
            view["nombre_especie"] for view in persistent_species
        }
        persistent_species_names.update(
            error["especie"]
            for error in persistent_tree_errors
            if error.get("especie")
        )

        report_data = {
            "criterios": {
                "minimo_fotos": self.min_photos,
                "minimo_audios": self.min_sounds,
                "ambito_fotos": "Colombia (con fallback internacional)",
                "ambito_audios": "Global",
                "numero_individuos": "observations_count de taxon_info.json"
            },
            "resumen_general": {
                "total_especies_consultadas": len(audit_views),
                "especies_con_datos_completos": sum(
                    1 for view in audit_views if view["cumple"] and not view["error_persistente"]
                ),
                "especies_con_deficiencias": sum(1 for view in audit_views if not view["cumple"]),
                "especies_con_error_persistente": len(persistent_species_names),
                "errores_persistentes_globales": persistent_tree_errors
            },
            "auditoria_especies": audit_views
        }

        json_path = os.path.join(self.output_dir, "reporte_especies_problematicas.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

        md_path = os.path.join(self.output_dir, "reporte_especies_problematicas.md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("# Reporte de Auditoría: Disponibilidad de Datos en iNaturalist\n\n")
            f.write(f"- **Mínimo requerido de fotos:** {self.min_photos}\n")
            f.write(f"- **Mínimo requerido de audios:** {self.min_sounds}\n")
            f.write(f"- **Total de especies procesadas:** {len(audit_views)}\n")
            f.write(f"- **Especies que cumplen:** {sum(1 for v in audit_views if v['cumple'])}\n")
            f.write(f"- **Especies que no cumplen:** {sum(1 for v in audit_views if not v['cumple'])}\n")
            f.write(f"- **Especies con error persistente:** {len(persistent_species_names)}\n\n")
            f.write("El campo **Número de individuos** corresponde a `observations_count` de `taxon_info.json`. "
                    "El conteo de fotos usa el total consolidado (Colombia + fallback internacional).\n\n")

            f.write("## Especies con déficit o error persistente\n\n")
            f.write("| Ruta de datos | Especie | Clave taxonómica | Familia | Género | Nombre científico | Nombre común | Individuos | Fotos | Audios | Cumple | Error persistente | Problemas |\n")
            f.write("|---|---|---:|---|---|---|---|---:|---:|---:|---|---|---|\n")
            if not problematic_species:
                f.write("| N/A | N/A | N/A | N/A | N/A | N/A | N/A | 0 | 0 | 0 | Sí | No | Sin problemas |\n")
            else:
                for sp in problematic_species:
                    f.write(
                        f"| `{sp['ruta_datos'] or 'N/A'}` | {sp['nombre_especie']} | "
                        f"{sp['clave_taxonomica'] if sp['clave_taxonomica'] is not None else 'N/A'} | "
                        f"{sp['familia'] or 'N/A'} | {sp['genero'] or 'N/A'} | "
                        f"*{sp['especie_nombre_cientifico']}* | {sp['especie_nombre_comun'] or 'N/A'} | "
                        f"{sp['numero_individuos']} | {sp['numero_fotos']} | {sp['numero_audios']} | "
                        f"{'Sí' if sp['cumple'] else 'No'} | "
                        f"{'Sí' if sp['error_persistente'] else 'No'} | "
                        f"{'; '.join(sp['problemas_detectados']) or 'Sin problemas'} |\n"
                    )

            f.write("\n## Tabla completa de especies analizadas\n\n")
            f.write("| Ruta de datos | Especie | Clave taxonómica | Familia | Género | Nombre científico | Nombre común | Individuos | Fotos | Audios | Cumple | Error persistente |\n")
            f.write("|---|---|---:|---|---|---|---|---:|---:|---:|---|---|\n")
            for sp in audit_views:
                f.write(
                    f"| `{sp['ruta_datos'] or 'N/A'}` | {sp['nombre_especie']} | "
                    f"{sp['clave_taxonomica'] if sp['clave_taxonomica'] is not None else 'N/A'} | "
                    f"{sp['familia'] or 'N/A'} | {sp['genero'] or 'N/A'} | "
                    f"*{sp['especie_nombre_cientifico']}* | {sp['especie_nombre_comun'] or 'N/A'} | "
                    f"{sp['numero_individuos']} | {sp['numero_fotos']} | {sp['numero_audios']} | "
                    f"{'Sí' if sp['cumple'] else 'No'} | "
                    f"{'Sí' if sp['error_persistente'] else 'No'} |\n"
                )

            f.write("\n## Errores persistentes\n\n")
            persistent_error_entries = {}
            for sp in persistent_species:
                for error in sp["errores_persistentes"]:
                    key = (sp["nombre_especie"], error)
                    persistent_error_entries[key] = (
                        f"- **{sp['nombre_especie']}** "
                        f"(`{sp['ruta_datos'] or 'ruta no disponible'}): {error}"
                    )
            for error in persistent_tree_errors:
                species_name = error.get("especie") or "Especie no identificada"
                detail = error.get("detalle") or error.get("tipo")
                key = (species_name, detail)
                persistent_error_entries[key] = f"- **{species_name}**: {detail}"
            if persistent_error_entries:
                f.write("\n".join(persistent_error_entries.values()) + "\n")
            else:
                f.write("No se detectaron errores persistentes.\n")

        print(f"\n[✓] Reporte de auditoría guardado en:")
        print(f"    - JSON: {json_path}")
        print(f"    - Markdown: {md_path}")

        print("\n" + "=" * 80)
        print("RESUMEN DE AUDITORÍA: ESPECIES CON PROBLEMAS DE DATOS")
        print("=" * 80)
        for sp in audit_views:
            status_flag = "[DÉFICIT]" if not sp["cumple"] else "[OK]"
            print(
                f" {status_flag:9} {sp['scientific_name']:<28} | "
                f"Individuos: {sp['numero_individuos']:<6} | Audios: {sp['numero_audios']:<3} | "
                f"Fotos: {sp['numero_fotos']:<3} | Persistente: {sp['error_persistente']}"
            )
        print("=" * 80 + "\n")

    def process_species(self, species_name: str) -> Optional[Dict[str, Any]]:
        """Procesa una especie individual: taxonomía, audios, fotos, coordenadas y mapas."""
        clean_name = species_name.strip()
        if not clean_name:
            return None

        taxon = self.search_taxon(clean_name)
        if not taxon:
            return {
                "scientific_name": clean_name,
                "status": "NOT_FOUND",
                "audio_count": 0,
                "photos_colombia": 0,
                "photos_total": 0,
                "coordinates_count": 0
            }

        # 1. Taxonomía
        tax_info = self.parse_taxonomy(taxon)
        species_slug = sanitize_filename(tax_info["scientific_name"])
        species_dir = os.path.join(self.output_dir, species_slug)
        os.makedirs(species_dir, exist_ok=True)

        # Guardar taxon_info individual
        tax_path = os.path.join(species_dir, "taxon_info.json")
        with open(tax_path, "w", encoding="utf-8") as f:
            json.dump(tax_info, f, indent=2, ensure_ascii=False)

        print(f"  [Taxonomía]")
        print(f"   • Familia: {tax_info['family_scientific_name']} ({tax_info['family_common_name'] or 'Sin nombre común'})")
        print(f"   • Género:  {tax_info['genus_scientific_name']} ({tax_info['genus_common_name'] or 'Sin nombre común'})")
        print(f"   • Especie: {tax_info['scientific_name']} ({tax_info['species_common_name'] or 'Sin nombre común'})")

        taxon_id = tax_info["taxon_id"]

        # 2. Audios
        if self.skip_audio:
            audio_count, sound_records = 0, []
        else:
            audio_count, sound_records = self.fetch_sounds(taxon_id, species_dir)

        # 3. Fotos y Coordenadas
        col_photos, tot_photos, photo_records, coordinates = self.fetch_photos_and_coordinates(taxon_id, species_dir)

        # 4. Mapa interactivo de la especie
        if coordinates:
            self.generate_species_map(tax_info["scientific_name"], coordinates, species_dir)

        metadata_errors = []
        if audio_count != len(sound_records):
            metadata_errors.append(
                f"Conteo de audios inconsistente: registro={audio_count}, metadatos={len(sound_records)}"
            )
        if tot_photos != len(photo_records):
            metadata_errors.append(
                f"Conteo de fotos inconsistente: registro={tot_photos}, metadatos={len(photo_records)}"
            )

        return {
            "scientific_name": tax_info["scientific_name"],
            "common_name": tax_info["species_common_name"],
            "family": tax_info["family_scientific_name"],
            "genus": tax_info["genus_scientific_name"],
            "status": "OK",
            "data_path": species_dir,
            "taxonomy": tax_info,
            "audio_count": audio_count,
            "photos_colombia": col_photos,
            "photos_fallback": len(photo_records) - col_photos,
            "photos_total": tot_photos,
            "coordinates_count": len(coordinates),
            "coordinates": coordinates,
            "persistent_errors": [],
            "metadata_errors": metadata_errors
        }

    def run(self, species_list: List[str]):
        """Ejecuta el pipeline completo para la lista de especies provista."""
        print("=" * 80)
        print("INICIANDO EXTRACCIÓN DE iNaturalist PARA ANUROS")
        print(f"Carpeta de destino: '{self.output_dir}'")
        print(f"Especies a procesar: {len(species_list)}")
        print(f"Umbral mínimo requerido de Fotos: {self.min_photos} | Audios: {self.min_sounds}")
        print(f"Filtro de calidad iNaturalist: {self.quality_grade or 'sin filtro'}")
        if self.dry_run:
            print("MODO SIMULACIÓN (DRY-RUN): Solo se recopilarán metadatos, sin descargar archivos pesados.")
        print("=" * 80)

        all_taxonomies = []
        all_species_data = []
        audit_records = []

        for idx, sp in enumerate(species_list, 1):
            print(f"\n[{idx}/{len(species_list)}] Procesando: {sp}")
            result = self.process_species(sp)
            if result:
                audit_records.append(result)
                if result.get("status") == "OK":
                    all_taxonomies.append(result["taxonomy"])
                    all_species_data.append(result)

        # Generar consolidaciones finales
        if all_taxonomies:
            self.build_taxonomic_tree_json(all_taxonomies)

        if all_species_data:
            self.generate_master_map(all_species_data)

        if audit_records:
            self.generate_audit_report(audit_records)

        print("\n[✓] Extracción y análisis completados con éxito.")


def load_species_file(filepath: str) -> List[str]:
    """Carga especies desde un archivo de texto, ignorando comentarios y vacíos."""
    species = []
    if not os.path.exists(filepath):
        print(f"[-] Archivo '{filepath}' no encontrado.")
        return species
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            clean = line.strip()
            if clean and not clean.startswith("#"):
                species.append(clean)
    return species


def main():
    parser = argparse.ArgumentParser(
        description="Scraper y Extractor de iNaturalist para Anuros (Ranas)."
    )
    parser.add_argument(
        "-i", "--input", default="especies_input.txt",
        help="Ruta al archivo con lista de especies (default: especies_input.txt)"
    )
    parser.add_argument(
        "-s", "--species", type=str,
        help="Lista de especies separadas por coma directamente desde terminal"
    )
    parser.add_argument(
        "-o", "--output", default=DEFAULT_OUTPUT_DIR,
        help=f"Carpeta de salida (default: '{DEFAULT_OUTPUT_DIR}')"
    )
    parser.add_argument(
        "--min-photos", type=int, default=70,
        help="Cantidad mínima requerida de fotos (default: 70)"
    )
    parser.add_argument(
        "--min-sounds", type=int, default=70,
        help="Cantidad mínima requerida de audios (default: 70)"
    )
    parser.add_argument(
        "--max-photos", type=int, default=None,
        help="Límite máximo opcional de fotos a descargar por especie"
    )
    parser.add_argument(
        "--max-sounds", type=int, default=None,
        help="Límite máximo opcional de audios a descargar por especie"
    )
    parser.add_argument(
        "--delay", type=float, default=1.0,
        help="Retardo en segundos entre peticiones API (default: 1.0)"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Ejecuta la auditoría, taxonomía y mapeo sin descargar archivos binarios (fotos/audios)"
    )
    parser.add_argument(
        "--skip-audio", action="store_true",
        help="Omite completamente la descarga de audios (más rápido cuando solo se necesitan fotos)"
    )
    parser.add_argument(
        "--quality-grade", choices=["research", "needs_id", "casual", "none"],
        default="research",
        help="Filtra observaciones por calidad (default: research; none = sin filtro)"
    )

    args = parser.parse_args()

    species_to_process = []
    if args.species:
        species_to_process = [s.strip() for s in args.species.split(",") if s.strip()]
    elif args.input:
        species_to_process = load_species_file(args.input)

    if not species_to_process:
        print("[!] No se especificaron especies. Agrega especies en 'especies_input.txt' o usa --species.")
        sys.exit(1)

    scraper = INaturalistScraper(
        output_dir=args.output,
        min_photos=args.min_photos,
        min_sounds=args.min_sounds,
        max_photos=args.max_photos,
        max_sounds=args.max_sounds,
        request_delay=args.delay,
        dry_run=args.dry_run,
        skip_audio=args.skip_audio,
        quality_grade=None if args.quality_grade == "none" else args.quality_grade
    )

    scraper.run(species_to_process)


if __name__ == "__main__":
    main()
