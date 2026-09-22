"""Descarga ~40 imagenes genericas 'no-rana' desde Wikimedia Commons (dominio publico/CC)
via la API oficial, en miniatura de 400px para mantener el tamano bajo.
"""
import json
import time
from pathlib import Path
from urllib.parse import urlparse

import requests

SALIDA = Path(__file__).parent / "negativos"
SALIDA.mkdir(exist_ok=True)

TERMINOS = [
    "domestic dog photo", "domestic cat photo", "green leaf plant", "butterfly insect",
    "songbird photo", "granite rock texture", "modern car photo", "brick building facade",
    "sliced bread food", "human face portrait", "red rose flower", "pine forest photo",
    "ocean wave photo", "blue sky clouds", "open book pages", "wooden chair photo",
    "laptop computer photo", "acoustic guitar photo", "wooden table photo", "wristwatch photo",
    "baseball cap hat", "leather shoe photo", "coffee cup photo", "glass bottle photo",
    "bicycle photo", "motorcycle photo", "wild mushroom photo", "monarch butterfly",
    "goldfish aquarium photo", "red-eared slider turtle", "green lizard photo", "garden spider photo",
    "house mouse photo", "wild rabbit photo", "brown horse photo", "dairy cow photo",
    "domestic sheep photo", "african elephant photo", "lion animal photo", "owl bird photo",
]

API = "https://commons.wikimedia.org/w/api.php"
HEADERS = {"User-Agent": "AnuraResearch/1.0 (evaluacion academica umbral no-rana)"}

manifest = []

def get_json(params, tries=4):
    for attempt in range(tries):
        r = requests.get(API, params=params, headers=HEADERS, timeout=20)
        if r.status_code == 200 and r.headers.get("content-type", "").startswith("application/json"):
            return r.json()
        time.sleep(2 * (attempt + 1))
    r.raise_for_status()
    return r.json()


for i, termino in enumerate(TERMINOS):
    try:
        data = get_json({
            "action": "query", "list": "search", "srsearch": termino,
            "srnamespace": 6, "srlimit": 3, "format": "json",
        })
        hits = data.get("query", {}).get("search", [])
        chosen = None
        for h in hits:
            title = h["title"]
            if not title.lower().endswith((".jpg", ".jpeg", ".png")):
                continue
            data2 = get_json({
                "action": "query", "titles": title, "prop": "imageinfo",
                "iiprop": "url|size", "iiurlwidth": 400, "format": "json",
            })
            pages = data2.get("query", {}).get("pages", {})
            for _, page in pages.items():
                info = page.get("imageinfo", [{}])[0]
                thumb = info.get("thumburl")
                if thumb:
                    chosen = (title, thumb)
                    break
            if chosen:
                break
        if not chosen:
            print(f"[{i:02d}] SIN RESULTADO: {termino}")
            continue
        title, thumb = chosen
        ext = Path(urlparse(thumb).path).suffix or ".jpg"
        fname = f"{i:02d}_{termino.replace(' ', '_')}{ext}"
        img = requests.get(thumb, headers=HEADERS, timeout=30)
        (SALIDA / fname).write_bytes(img.content)
        manifest.append({"file": fname, "termino": termino, "titulo_commons": title, "url": thumb, "bytes": len(img.content)})
        print(f"[{i:02d}] OK {fname} ({len(img.content)} bytes)")
        time.sleep(1.0)
    except Exception as e:
        print(f"[{i:02d}] ERROR {termino}: {e}")

(SALIDA / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
total = sum(m["bytes"] for m in manifest)
print(f"\nTotal: {len(manifest)} imagenes, {total/1024:.1f} KB")
