"""
FASE 22 - UNKNOWN V2
Step 7: Final assembly - coverage table, final/ dataset folder, UNKNOWN_V2_MANIFEST.json, status.
Run AFTER step6 (new-image audit) has produced image_quality_audit.csv + updated leakage/taxonomy CSVs.
"""
import json, csv, re, shutil, sys, hashlib
from pathlib import Path
from collections import defaultdict

ROOT = Path(r"D:\Anura")
BASE = ROOT / "data/unknown_open_set_v2"
OBS_PAT = re.compile(r"col_obs_(\d+)_photo")

KNOWN_GENUS = {
    "Boana", "Craugastor", "Dendrobates", "Dendropsophus", "Engystomops", "Hyloscirtus",
    "Leptodactylus", "Phyllomedusa", "Pithecopus", "Pristimantis", "Rheobates", "Rhinella", "Scinax",
}
KNOWN_FAMILY_BY_GENUS = {
    "Boana": "Hylidae", "Dendropsophus": "Hylidae", "Hyloscirtus": "Hylidae", "Scinax": "Hylidae",
    "Pithecopus": "Hylidae", "Phyllomedusa": "Hylidae", "Smilisca": "Hylidae", "Trachycephalus": "Hylidae",
    "Craugastor": "Craugastoridae", "Pristimantis": "Craugastoridae",
    "Dendrobates": "Dendrobatidae", "Hyloxalus": "Dendrobatidae",
    "Engystomops": "Leptodactylidae", "Leptodactylus": "Leptodactylidae",
    "Rheobates": "Dendrobatidae",  # placeholder if needed
    "Rhinella": "Bufonidae",
    "Sachatamia": "Centrolenidae", "Hyalinobatrachium": "Centrolenidae", "Espadarana": "Centrolenidae",
}


def relation_for(species_us, genus):
    if genus in KNOWN_GENUS:
        return "SAME_GENUS"
    fam = KNOWN_FAMILY_BY_GENUS.get(genus, "")
    known_families = set(KNOWN_FAMILY_BY_GENUS[g] for g in KNOWN_GENUS if g in KNOWN_FAMILY_BY_GENUS)
    if fam and fam in known_families:
        return "SAME_FAMILY"
    return "DIFFERENT_FAMILY"


def main():
    dl_manifest_path = BASE / "manifests/download_manifest.json"
    dl = json.loads(dl_manifest_path.read_text(encoding="utf-8")) if dl_manifest_path.exists() else {"downloaded": [], "candidates": []}
    downloaded_index = {d["path"]: d for d in dl.get("downloaded", [])}

    hist_audit = list(csv.DictReader(open(BASE / "audit/historical_unknown_quality_audit.csv", encoding="utf-8")))
    hist_inv = {r["image_path"]: r for r in csv.DictReader(open(BASE / "metadata/historical_unknown_inventory.csv", encoding="utf-8"))}
    leak_rows = {r["image_path"]: r for r in csv.DictReader(open(BASE / "audit/leakage_audit.csv", encoding="utf-8"))}

    new_audit_path = BASE / "audit/image_quality_audit.csv"
    new_audit = list(csv.DictReader(open(new_audit_path, encoding="utf-8"))) if new_audit_path.exists() else []

    # ---- unify accepted, clean, non-duplicate images from BOTH pools ----
    accepted = []  # dicts: image_path, species, genus, source(historical/new), obs_id
    for r in hist_audit:
        p = r["image_path"]
        if r["decision"] != "ACCEPT":
            continue
        if leak_rows.get(p, {}).get("leakage_status") == "LEAKED":
            continue
        species = hist_inv[p]["species"]
        m = OBS_PAT.search(p)
        obs_id = m.group(1) if m else f"NOOBS_{Path(p).stem}"
        accepted.append({"image_path": p, "species": species, "genus": species.split("_")[0],
                          "source": "historical", "obs_id": obs_id})

    for r in new_audit:
        p = r["image_path"]
        if r["decision"] != "ACCEPT":
            continue
        if r.get("leakage_status") == "LEAKED":
            continue
        d = downloaded_index.get(p)
        if not d:
            continue
        species = d["species"]
        accepted.append({"image_path": p, "species": species, "genus": species.split("_")[0],
                          "source": "new", "obs_id": str(d["observation_id"])})

    # ---- per-species / per-observation rollup ----
    by_species_obs = defaultdict(set)
    by_species_images = defaultdict(list)
    for a in accepted:
        by_species_obs[a["species"]].add(a["obs_id"])
        by_species_images[a["species"]].append(a["image_path"])

    coverage_rows = []
    for sp in sorted(by_species_images.keys()):
        genus = sp.split("_")[0]
        relation = relation_for(sp, genus)
        n_images = len(by_species_images[sp])
        n_obs = len(by_species_obs[sp])
        regions = "Colombia (iNaturalist research-grade)" if any(a["source"] == "new" for a in accepted if a["species"] == sp) else "historical (source region not recorded in F13 lineage)"
        coverage_rows.append({
            "species": sp, "genus": genus, "family": KNOWN_FAMILY_BY_GENUS.get(genus, "UNRESOLVED"),
            "taxon_id": "", "n_images": n_images, "n_individuals": n_obs, "n_observations": n_obs,
            "relation_to_known": relation, "geographic_regions": regions,
            "acceptance_rate": "", "quality_summary": "",
        })

    with open(BASE / "metadata/unknown_taxonomic_coverage.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(coverage_rows[0].keys()) if coverage_rows else
                            ["species", "genus", "family", "taxon_id", "n_images", "n_individuals",
                             "n_observations", "relation_to_known", "geographic_regions",
                             "acceptance_rate", "quality_summary"])
        w.writeheader()
        w.writerows(coverage_rows)

    # ---- build final/ dataset: copy accepted images ----
    final_dir = BASE / "images/final"
    if final_dir.exists():
        shutil.rmtree(final_dir)
    final_dir.mkdir(parents=True, exist_ok=True)
    sha_manifest = {}
    for a in accepted:
        src = Path(a["image_path"])
        dest_dir = final_dir / a["species"]
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / src.name
        shutil.copy2(src, dest)
        h = hashlib.sha256(dest.read_bytes()).hexdigest()
        sha_manifest[str(dest.relative_to(BASE))] = h

    n_species = len(by_species_images)
    n_images_total = len(accepted)
    n_individuals_total = sum(len(v) for v in by_species_obs.values())
    n_genera = len({sp.split("_")[0] for sp in by_species_images})
    families = {KNOWN_FAMILY_BY_GENUS.get(sp.split("_")[0], "UNRESOLVED") for sp in by_species_images}
    n_families = len(families)

    same_genus = sum(1 for r in coverage_rows if r["relation_to_known"] == "SAME_GENUS")
    same_family = sum(1 for r in coverage_rows if r["relation_to_known"] == "SAME_FAMILY")
    diff_family = sum(1 for r in coverage_rows if r["relation_to_known"] == "DIFFERENT_FAMILY")

    n_hist_reviewed = 56
    n_hist_accepted = sum(1 for r in hist_audit if r["decision"] == "ACCEPT" and
                           leak_rows.get(r["image_path"], {}).get("leakage_status") != "LEAKED")
    n_hist_rejected = n_hist_reviewed - n_hist_accepted
    n_new_added = sum(1 for a in accepted if a["source"] == "new")

    quality_rejects = sum(1 for r in hist_audit if r["decision"] == "REJECT_QUALITY") + \
        sum(1 for r in new_audit if r["decision"] == "REJECT_QUALITY")
    n_leaked = sum(1 for r in leak_rows.values() if r["leakage_status"] == "LEAKED")
    n_dup = 0
    dup_path = BASE / "audit/duplicate_audit.csv"
    if dup_path.exists():
        n_dup = len(list(csv.DictReader(open(dup_path, encoding="utf-8"))))

    status = "UNKNOWN_DATA_INSUFFICIENT"
    if n_species >= 10 and n_images_total >= 200 and n_individuals_total >= 50 and n_leaked == 0:
        status = "UNKNOWN_DATA_READY_FOR_PHASE23"
    elif n_species >= 5 or n_images_total >= 100 or n_individuals_total >= 25:
        status = "UNKNOWN_DATA_PARTIALLY_READY"

    manifest = {
        "dataset_version": "unknown_open_set_v2_fase22",
        "creation_date": "2026-09-14",
        "n_species": n_species, "n_genera": n_genera, "n_families": n_families,
        "n_images": n_images_total, "n_individuals": n_individuals_total, "n_observations": n_individuals_total,
        "historical_images_reviewed": n_hist_reviewed,
        "historical_images_accepted": n_hist_accepted,
        "historical_images_rejected": n_hist_rejected,
        "new_images_added": n_new_added,
        "same_genus_species": same_genus, "same_family_species": same_family,
        "different_family_species": diff_family,
        "leakage_count": n_leaked, "duplicate_count": n_dup,
        "quality_rejection_count": quality_rejects,
        "taxonomy_rejection_count": 0,
        "source_distribution": {"historical_F16_F19_F20_F21": n_hist_accepted,
                                 "new_iNaturalist_CC_licensed": n_new_added},
        "geographic_distribution": {"note": "see unknown_taxonomic_coverage.csv geographic_regions column"},
        "sha256_manifest_file": "images/final/ (per-file sha256 in this manifest's sha256_manifest field)",
        "sha256_manifest": sha_manifest,
        "status": status,
        "acquisition_note": dl.get("candidates", []),
    }
    with open(BASE / "UNKNOWN_V2_MANIFEST.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print("=== FASE 22 FINAL NUMBERS ===")
    for k in ["n_species", "n_genera", "n_families", "n_images", "n_individuals",
              "historical_images_accepted", "historical_images_rejected", "new_images_added",
              "same_genus_species", "same_family_species", "different_family_species",
              "leakage_count", "duplicate_count", "quality_rejection_count", "status"]:
        print(f"  {k}: {manifest[k]}")
    print("\nPer-species coverage:")
    for r in coverage_rows:
        print(" ", r["species"], r["genus"], r["family"], r["relation_to_known"],
              "images=", r["n_images"], "individuals=", r["n_individuals"])


if __name__ == "__main__":
    main()
