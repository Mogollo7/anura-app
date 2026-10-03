"""
FASE 22 - UNKNOWN V2
Step 5: Acquire NEW UNKNOWN species candidates from iNaturalist (official public API).

Compliance:
  - Official API only (api.inaturalist.org/v1), no scraping of the website, no robots.txt bypass needed
    (API is the documented public access point).
  - Single stable User-Agent identifying the project + contact email. No UA rotation.
  - Rate limit: 1 request per ~1.1s (well under iNaturalist's documented 60 req/min / 10000 req/day),
    exponential backoff on 429/5xx, max 3 retries.
  - Only images with a CC license code (cc0, cc-by, cc-by-nc, cc-by-sa, cc-by-nc-sa) are downloaded, and
    license + observer + observation URL are recorded for attribution.
  - Filtered to quality_grade='research' at the OBSERVATION level only as an initial relevance filter
    (per task rule #13: never as final image-quality criterion - full independent quality audit runs
    in step 6 exactly like the historical images).
  - Candidates are selected BEFORE any Open-Set evaluation exists for this data (no BLIND-test-informed
    selection - satisfies task rule #8).

Candidate species were chosen using only taxonomic knowledge available before evaluation:
Priority 1 (SAME_GENUS as a KNOWN deployed species, different species) and Priority 2/3
(SAME_FAMILY / DIFFERENT_FAMILY) — see CANDIDATES below with the stated rationale.
"""
import json, time, hashlib, sys
from pathlib import Path
import requests

ROOT = Path(r"D:\Anura")
OUT_DIR = ROOT / "data/unknown_open_set_v2/images/new"
MANIFEST_OUT = ROOT / "data/unknown_open_set_v2/manifests/download_manifest.json"
CACHE_DIR = ROOT / "data/unknown_open_set_v2/manifests/_inat_cache"

UA = "AnuraColombiaResearch-Fase22/1.0 (non-commercial academic classification research; contact: sebastianmartinez06.js@gmail.com)"
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": UA})

COLOMBIA_PLACE_ID = 7196
ALLOWED_LICENSES = {"cc0", "cc-by", "cc-by-nc", "cc-by-sa", "cc-by-nc-sa"}

# KNOWN deployed genera/families (species_registry.json, visual_lifecycle_status=DEPLOYED, 41 species)
KNOWN_SPECIES_UNDERSCORED = {
    "Boana_boans", "Boana_cinerascens", "Boana_lanciformis", "Boana_platanera", "Boana_pugnax",
    "Boana_punctata", "Boana_rosenbergi", "Boana_xerophylla", "Craugastor_raniformis",
    "Dendrobates_truncatus", "Dendropsophus_bogerti", "Dendropsophus_columbianus",
    "Dendropsophus_ebraccatus", "Dendropsophus_mathiassoni", "Dendropsophus_microcephalus",
    "Dendropsophus_molitor", "Dendropsophus_norandinus", "Dendropsophus_reticulatus",
    "Dendropsophus_triangulum", "Engystomops_pustulosus", "Hyloscirtus_palmeri",
    "Leptodactylus_colombiensis", "Phyllomedusa_tarsius", "Phyllomedusa_venusta",
    "Pithecopus_hypochondrialis", "Pristimantis_achatinus", "Pristimantis_bogotensis",
    "Pristimantis_erythropleura", "Pristimantis_gaigei", "Pristimantis_paisa",
    "Pristimantis_palmeri", "Pristimantis_penelopus", "Pristimantis_permixtus",
    "Pristimantis_taeniatus", "Pristimantis_thectopternus", "Pristimantis_vilarsi",
    "Rheobates_palmatus", "Rhinella_alata", "Rhinella_horribilis", "Rhinella_margaritifera",
    "Scinax_ruber",
}

# (species_name, relation, rationale)
CANDIDATES = [
    ("Boana geographica", "SAME_GENUS", "Same genus as 8 KNOWN Boana spp.; widespread lowland Colombia; visually similar body plan (large treefrog) -> plausible confusion candidate."),
    ("Boana crepitans", "SAME_GENUS", "Same genus as KNOWN Boana; common in Colombia; similar habitat/photo conditions to existing Boana KNOWN images."),
    ("Dendropsophus labialis", "SAME_GENUS", "Same genus as 8 KNOWN Dendropsophus spp.; high-Andean, common in Colombia photo records."),
    ("Dendropsophus minutus", "SAME_GENUS", "Same genus as KNOWN Dendropsophus; small hylid, morphologically close to several KNOWN Dendropsophus."),
    ("Pristimantis w-nigrum", "SAME_GENUS", "Same genus as 10 KNOWN Pristimantis spp. (the largest KNOWN genus) - high value for testing intra-genus separability."),
    ("Pristimantis nervicus", "SAME_GENUS", "Same genus as KNOWN Pristimantis; Colombian endemic-adjacent range."),
    ("Rhinella marina", "SAME_GENUS", "Same genus as 3 KNOWN Rhinella spp.; common, large sample availability."),
    ("Smilisca phaeota", "SAME_FAMILY", "Family Hylidae (same family as 8 Boana + 8 Dendropsophus + Hyloscirtus + Scinax + Pithecopus KNOWN, 19 of 41 spp.), different genus -> family-level confusion test."),
    ("Trachycephalus typhonius", "SAME_FAMILY", "Family Hylidae, different genus, distinctive but same-family confusion candidate."),
    ("Leptodactylus fragilis", "SAME_GENUS", "Same genus as KNOWN Leptodactylus_colombiensis, only 1 KNOWN species in that genus -> tests a thin genus."),
    ("Hyalinobatrachium fleischmanni", "DIFFERENT_FAMILY", "Family Centrolenidae (glass frogs) - same family as the historical UNKNOWN Sachatamia_electrops, extending that family's representation rather than relying on a single historical species."),
    ("Espadarana prosoblepon", "DIFFERENT_FAMILY", "Family Centrolenidae, different genus from Sachatamia -> adds within-family diversity to the glass-frog UNKNOWN stratum."),
]


def get_json(url, params, max_retries=3):
    backoff = 2.0
    for attempt in range(max_retries):
        r = SESSION.get(url, params=params, timeout=20)
        if r.status_code == 200:
            return r.json()
        if r.status_code in (429, 500, 502, 503):
            time.sleep(backoff)
            backoff *= 2
            continue
        r.raise_for_status()
    raise RuntimeError(f"Failed after {max_retries} retries: {url} {params}")


def fetch_observations(species_name, per_page=30, max_pages=2):
    results = []
    for page in range(1, max_pages + 1):
        d = get_json("https://api.inaturalist.org/v1/observations", {
            "taxon_name": species_name, "place_id": COLOMBIA_PLACE_ID,
            "quality_grade": "research", "photos": "true", "per_page": per_page,
            "page": page, "order": "desc", "order_by": "created_at",
        })
        time.sleep(1.1)
        page_results = d.get("results", [])
        results.extend(page_results)
        if len(page_results) < per_page:
            break
    return results


def sha256_of_bytes(b):
    return hashlib.sha256(b).hexdigest()


def download(url, dest: Path):
    r = SESSION.get(url, timeout=30)
    if r.status_code != 200:
        return None
    dest.write_bytes(r.content)
    return sha256_of_bytes(r.content)


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    manifest = {"candidates": [], "downloaded": [], "skipped_no_cc_license": 0,
                "skipped_taxon_name_mismatch": 0, "api": "api.inaturalist.org/v1",
                "user_agent": UA, "license_filter": sorted(ALLOWED_LICENSES)}

    for species_name, relation, rationale in CANDIDATES:
        sp_underscored = species_name.replace(" ", "_").replace("-", "_")
        if sp_underscored in KNOWN_SPECIES_UNDERSCORED:
            print(f"SKIP {species_name}: already KNOWN deployed species")
            continue
        cache_file = CACHE_DIR / f"{sp_underscored}.json"
        if cache_file.exists():
            obs = json.loads(cache_file.read_text(encoding="utf-8"))
            print(f"[cache] {species_name}: {len(obs)} obs")
        else:
            try:
                obs = fetch_observations(species_name)
            except Exception as e:
                print(f"ERROR fetching {species_name}: {e}")
                manifest["candidates"].append({"species": species_name, "relation": relation,
                                                "rationale": rationale, "status": f"FETCH_ERROR:{e}"})
                continue
            cache_file.write_text(json.dumps(obs, ensure_ascii=False), encoding="utf-8")
            print(f"[api] {species_name}: {len(obs)} obs fetched")

        n_downloaded = 0
        species_dir = OUT_DIR / sp_underscored
        for o in obs:
            obs_id = o["id"]
            taxon = o.get("taxon") or {}
            if not taxon or species_name.split()[0] not in (taxon.get("name") or ""):
                manifest["skipped_taxon_name_mismatch"] += 1
                continue
            for photo in o.get("photos", []):
                lic = (photo.get("license_code") or "").lower()
                if lic not in ALLOWED_LICENSES:
                    manifest["skipped_no_cc_license"] += 1
                    continue
                photo_id = photo["id"]
                url = photo["url"].replace("square", "large")
                species_dir.mkdir(parents=True, exist_ok=True)
                fname = f"col_obs_{obs_id}_photo_{photo_id}.jpg"
                dest = species_dir / fname
                if dest.exists():
                    continue
                h = download(url, dest)
                time.sleep(1.1)
                if not h:
                    continue
                geo = o.get("geojson") or {}
                coords = geo.get("coordinates") if geo else None
                manifest["downloaded"].append({
                    "species": sp_underscored, "observation_id": obs_id, "photo_id": photo_id,
                    "path": str(dest), "sha256": h, "license": lic,
                    "observer": (o.get("user") or {}).get("login", ""),
                    "quality_grade": o.get("quality_grade", ""),
                    "date": o.get("observed_on", ""),
                    "latitude": coords[1] if coords else "",
                    "longitude": coords[0] if coords else "",
                    "original_url": url,
                    "obs_url": f"https://www.inaturalist.org/observations/{obs_id}",
                })
                n_downloaded += 1

        manifest["candidates"].append({
            "species": species_name, "relation": relation, "rationale": rationale,
            "n_observations_found": len(obs), "n_images_downloaded": n_downloaded,
            "status": "OK" if n_downloaded > 0 else "NO_CC_LICENSED_PHOTOS_FOUND",
        })
        print(f"  -> downloaded {n_downloaded} CC-licensed images for {species_name}")

    MANIFEST_OUT.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_OUT.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nWrote {MANIFEST_OUT}")
    print(f"Total new images downloaded: {len(manifest['downloaded'])}")


if __name__ == "__main__":
    main()
