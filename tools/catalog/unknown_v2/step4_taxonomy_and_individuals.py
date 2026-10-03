"""
FASE 22 - UNKNOWN V2
Step 4: Taxonomy resolution (via tools/catalog/taxonomic_resolution.py, reusing existing
canonico() alias mechanism - NOT a reimplementation) + individual/observation deduplication.

Individual priority per task spec: individual_id > observation_id > SHA256 > path.
Historical pool has no explicit individual_id; observation_id is recovered from the
"col_obs_<id>_photo" filename convention (same regex Fase20 used). Files without that
pattern (e.g. "bmc_*.jpg") get one individual per distinct file (no evidence of shared
individual), consistent with Fase 20's __noind__ fallback.
"""
import csv, re, sys
from pathlib import Path
from collections import defaultdict

ROOT = Path(r"D:\Anura")
sys.path.insert(0, str(ROOT / "tools/catalog"))
from taxonomic_resolution import SpeciesResolver  # noqa: E402

AUDIT_CSV = ROOT / "data/unknown_open_set_v2/audit/historical_unknown_quality_audit.csv"
LEAK_CSV = ROOT / "data/unknown_open_set_v2/audit/leakage_audit.csv"
INV_CSV = ROOT / "data/unknown_open_set_v2/metadata/historical_unknown_inventory.csv"

OUT_TAX = ROOT / "data/unknown_open_set_v2/metadata/taxonomy_resolution.csv"
OUT_OBS = ROOT / "data/unknown_open_set_v2/metadata/unknown_observations.csv"
OUT_IND = ROOT / "data/unknown_open_set_v2/metadata/unknown_individuals.csv"
OUT_SP = ROOT / "data/unknown_open_set_v2/metadata/unknown_species.csv"

OBS_PAT = re.compile(r"col_obs_(\d+)_photo")

KNOWN_GENUS = {  # from the 41 DEPLOYED species (species_registry.json, visual_lifecycle_status=DEPLOYED)
    "Boana", "Craugastor", "Dendrobates", "Dendropsophus", "Engystomops", "Hyloscirtus",
    "Leptodactylus", "Phyllomedusa", "Pithecopus", "Pristimantis", "Rheobates", "Rhinella", "Scinax",
}
KNOWN_FAMILY = {"Hylidae", "Craugastoridae", "Dendrobatidae", "Leptodactylidae", "Bufonidae"}


def main():
    resolver = SpeciesResolver(
        ROOT / "training/taxonomia.py",
        ROOT / "taxonomy/species/species_registry.json",
    )

    inv_rows = {r["image_path"]: r for r in csv.DictReader(open(INV_CSV, encoding="utf-8"))}
    leak_rows = {r["image_path"]: r for r in csv.DictReader(open(LEAK_CSV, encoding="utf-8"))}
    audit_rows = list(csv.DictReader(open(AUDIT_CSV, encoding="utf-8")))

    species_seen = set(inv_rows[r["image_path"]]["species"] for r in audit_rows)
    tax_rows = []
    tax_by_species = {}
    for sp in sorted(species_seen):
        res = resolver.resolve(sp.replace("__", "_"))
        genus = sp.split("_")[0]
        tax_rows.append({
            "species_raw": sp, "canonical_name": res["canonical_name"],
            "species_id": res["species_id"] or "", "genus": genus,
            "resolution_status": res["resolution_status"],
        })
        tax_by_species[sp] = res

    OUT_TAX.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_TAX, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(tax_rows[0].keys()))
        w.writeheader()
        w.writerows(tax_rows)

    # Build observation/individual grouping restricted to ACCEPT + CLEAN(no leakage) images
    accepted = []
    for r in audit_rows:
        p = r["image_path"]
        if r["decision"] != "ACCEPT":
            continue
        if leak_rows.get(p, {}).get("leakage_status") == "LEAKED":
            continue
        accepted.append(r)

    obs_groups = defaultdict(list)
    for i, r in enumerate(accepted):
        p = r["image_path"]
        inv = inv_rows[p]
        species = inv["species"]
        m = OBS_PAT.search(p)
        obs_id = m.group(1) if m else f"NOOBS_{Path(p).stem}"
        obs_groups[(species, obs_id)].append(p)

    obs_rows = []
    for (species, obs_id), paths in obs_groups.items():
        obs_rows.append({
            "observation_id": obs_id, "species": species, "n_images": len(paths),
            "image_paths": ";".join(Path(p).name for p in paths),
            "individual_count": 1,  # multiple photos of same observation = same individual (rule #12)
            "source": "iNaturalist_col_obs" if not obs_id.startswith("NOOBS_") else "no_observation_id_1_photo_1_unit",
        })
    with open(OUT_OBS, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(obs_rows[0].keys()))
        w.writeheader()
        w.writerows(obs_rows)

    # unknown_individuals.csv : one row per individual (= one row per obs_group, priority obs_id>sha>path)
    ind_rows = []
    for (species, obs_id), paths in obs_groups.items():
        res = tax_by_species[species]
        ind_rows.append({
            "individual_id": f"{species}::{obs_id}",
            "species": species,
            "species_id": res["species_id"] or "",
            "n_images": len(paths),
        })
    with open(OUT_IND, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(ind_rows[0].keys()))
        w.writeheader()
        w.writerows(ind_rows)

    # unknown_species.csv : rollup
    sp_rollup = defaultdict(lambda: {"n_images": 0, "n_individuals": 0, "n_observations": 0})
    for (species, obs_id), paths in obs_groups.items():
        sp_rollup[species]["n_images"] += len(paths)
        sp_rollup[species]["n_individuals"] += 1
        sp_rollup[species]["n_observations"] += 1

    sp_rows = []
    for sp, vals in sp_rollup.items():
        res = tax_by_species[sp]
        genus = sp.split("_")[0]
        if genus in KNOWN_GENUS:
            relation = "SAME_GENUS"
        else:
            relation = "SAME_FAMILY_OR_DIFFERENT_FAMILY_SEE_FAMILY_FIELD"
        sp_rows.append({
            "species": sp, "species_id": res["species_id"] or "",
            "genus": genus, "resolution_status": res["resolution_status"],
            "n_images": vals["n_images"], "n_individuals": vals["n_individuals"],
            "n_observations": vals["n_observations"],
            "taxonomic_relation_to_known_genus_level": relation,
        })
    with open(OUT_SP, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(sp_rows[0].keys()))
        w.writeheader()
        w.writerows(sp_rows)

    print("Taxonomy resolution:")
    for r in tax_rows:
        print(" ", r)
    print(f"\nAccepted (post quality+leakage) images: {len(accepted)}")
    print(f"Observations/individuals: {len(obs_groups)}")
    for sp, vals in sp_rollup.items():
        print(f"  {sp}: images={vals['n_images']} individuals={vals['n_individuals']}")

if __name__ == "__main__":
    main()
