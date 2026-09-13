#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Complementa scraper_inaturalist.py: descarga audios desde Xeno-canto API v3
para las especies de especies_input.txt, evitando duplicados por nombre de archivo,
y deja un log de trazabilidad en data dirty/fuentes_xeno_canto.json.
"""
import os
import re
import sys
import json
import time
import requests

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, ".env")
INPUT_FILE = os.path.join(BASE_DIR, "especies_input.txt")
OUTPUT_DIR = os.path.join(BASE_DIR, "data dirty")
LOG_PATH = os.path.join(OUTPUT_DIR, "fuentes_xeno_canto.json")


def load_api_key():
    with open(ENV_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("XENO_CANTO_API_KEY="):
                return line.strip().split("=", 1)[1]
    raise RuntimeError("No se encontró XENO_CANTO_API_KEY en .env")


def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>| ]', '_', name.strip())


def load_species():
    species = []
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        for line in f:
            clean = line.strip()
            if clean and not clean.startswith("#"):
                species.append(clean)
    return species


def main():
    key = load_api_key()
    session = requests.Session()
    session.headers.update({"User-Agent": "AnuraScraper/1.0 (Amphibian Research Pipeline - Colombia)"})

    species_list = load_species()
    log = {}
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            log = json.load(f)

    for sp in species_list:
        slug = sanitize_filename(sp)
        species_dir = os.path.join(OUTPUT_DIR, slug)
        sonidos_dir = os.path.join(species_dir, "sonidos")
        os.makedirs(sonidos_dir, exist_ok=True)

        print(f"\n[Xeno-canto] {sp}")
        query = f'gen:"{sp.split()[0]}" sp:"{sp.split()[1]}"'
        url = "https://xeno-canto.org/api/3/recordings"
        try:
            resp = session.get(url, params={"query": query, "key": key, "per_page": 100}, timeout=30)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"  [!] Error de API: {e}")
            continue

        num = int(data.get("numRecordings", 0))
        recs = data.get("recordings", [])
        print(f"  {num} grabaciones encontradas (fg+bg incluidos por la query)")

        entry = log.setdefault(sp, {"source": "xeno-canto API v3", "recordings": []})
        existing_ids = {r["id"] for r in entry["recordings"]}

        downloaded = 0
        for rec in recs:
            rec_id = rec.get("id")
            if rec_id in existing_ids:
                continue
            file_url = rec.get("file")
            if not file_url:
                continue
            fname = f"XC{rec_id}_{sanitize_filename(rec.get('rec', 'unknown'))}_{sanitize_filename(rec.get('cnt', ''))}.mp3"
            dest = os.path.join(sonidos_dir, fname)
            if os.path.exists(dest) and os.path.getsize(dest) > 0:
                entry["recordings"].append({"id": rec_id, "url": rec.get("url"), "file": fname, "already_existed": True})
                continue
            try:
                r = session.get(file_url, timeout=30)
                if r.status_code == 200:
                    with open(dest, "wb") as f:
                        f.write(r.content)
                    downloaded += 1
                    entry["recordings"].append({
                        "id": rec_id, "url": rec.get("url"), "file": fname,
                        "recordist": rec.get("rec"), "country": rec.get("cnt"),
                        "type": rec.get("type"), "date": rec.get("date")
                    })
                    print(f"    [+] Descargado XC{rec_id} ({rec.get('cnt')}, {rec.get('rec')})")
            except Exception as e:
                print(f"    [!] Error descargando XC{rec_id}: {e}")
            time.sleep(0.5)

        print(f"  [Total nuevos]: {downloaded}")

        with open(LOG_PATH, "w", encoding="utf-8") as f:
            json.dump(log, f, indent=2, ensure_ascii=False)

        time.sleep(1.0)

    print("\n[OK] Proceso Xeno-canto completado.")


if __name__ == "__main__":
    main()
