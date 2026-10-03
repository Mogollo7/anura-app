"""
run_fase19_diagnosis.py — FASE 19: diagnostico de separabilidad taxonomica del embedding
BioCLIP congelado. EXCLUSIVAMENTE DIAGNOSTICO. No modifica BioCLIP, no recalibra nada,
no selecciona metodo Open Set. Reutiliza embeddings ya calculados (mismo encoder/preprocessing
verificado en Fases 13/16/17/18), no reextrae nada.
"""
import csv
import hashlib
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from scipy.spatial.distance import pdist, squareform, cosine, euclidean
from sklearn.metrics import roc_auc_score

ROOT = Path(r"D:\Anura")
sys.path.insert(0, str(ROOT / "tools" / "catalog"))
from taxonomic_resolution import SpeciesResolver

OUT = ROOT / "validation" / "fase19_embedding_separability"


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    print("=== FASE 19: DIAGNOSTICO DE SEPARABILIDAD BioCLIP ===\n")
    resolver = SpeciesResolver(ROOT / "training/taxonomia.py", ROOT / "taxonomy/species/species_registry.json")

    # ══════════════════════════════════════════════════════════════
    # SECCION 1: congelar input del experimento
    # ══════════════════════════════════════════════════════════════
    encoder_path = ROOT / "bioclip/checkpoints/encoder_anura_fp16.onnx"
    encoder_sha = sha256_file(encoder_path)
    expected_sha = "219e860e6fa9a80fb30a59fc8f61911421bbd53a4537dca831803d3ab446b2ad"
    assert encoder_sha == expected_sha, "ERROR: encoder distinto al usado en Fases anteriores"

    import platform
    import sklearn as sk
    import scipy as sp
    phase19_manifest_meta = {
        "encoder_path": str(encoder_path), "encoder_sha256": encoder_sha,
        "embedding_dimension": 512, "normalization": "L2",
        "preprocessing": "open_clip.create_model_and_transforms(hf-hub:imageomics/bioclip)",
        "python_version": platform.python_version(),
        "sklearn_version": sk.__version__, "scipy_version": sp.__version__, "numpy_version": np.__version__,
        "catalog_release": "visual_catalog_1.0.0",
        "analysis_datetime_utc": datetime.now(timezone.utc).isoformat(),
        "embeddings_reused_from": [
            "evaluation/fase13/embeddings/reference_embeddings.npz",
            "evaluation/fase13/embeddings/train_embeddings.npz",
            "validation/fase16_clean_open_set/clean_known_embeddings.npz",
            "evaluation/open_set_v1/knn/knn_embeddings.npz (F4 UNKNOWN)"
        ],
        "no_new_extraction": True
    }
    print(f"[OK] Encoder verificado: {encoder_sha[:16]}...")

    # ══════════════════════════════════════════════════════════════
    # SECCION 2: cargar y auditar todas las fuentes
    # ══════════════════════════════════════════════════════════════
    ref = np.load(ROOT / "evaluation/fase13/embeddings/reference_embeddings.npz")
    train = np.load(ROOT / "evaluation/fase13/embeddings/train_embeddings.npz")
    clean = np.load(ROOT / "validation/fase16_clean_open_set/clean_known_embeddings.npz")
    with open(ROOT / "validation/fase16_clean_open_set/clean_known_manifest.json", encoding="utf-8") as f:
        clean_manifest = json.load(f)
    f4_all = np.load(ROOT / "evaluation/open_set_v1/knn/knn_embeddings.npz")["embeddings"].astype(np.float32)
    with open(ROOT / "evaluation/open_set_v1/knn/knn_open_set_results.json", encoding="utf-8") as f:
        f3f4_records = json.load(f)["records"]
    unknown_records = [r for r in f3f4_records if r["known_unknown"] == "UNKNOWN"]
    unknown_idx = [i for i, r in enumerate(f3f4_records) if r["known_unknown"] == "UNKNOWN"]
    X_unknown = f4_all[unknown_idx]

    # Species metadata (genus/family) via resolver + taxonomia direct
    import importlib.util
    spec = importlib.util.spec_from_file_location("taxonomia", ROOT / "training/taxonomia.py")
    taxonomia = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(taxonomia)

    def sp_meta(canonical_name_underscored):
        try:
            genus = taxonomia.genero_de(canonical_name_underscored)
            family = taxonomia.familia_de(canonical_name_underscored)
        except KeyError:
            genus, family = "UNKNOWN_GENUS", "UNKNOWN_FAMILY"
        return genus, family

    # ── KNOWN: usar el pool COMPLETO de Fase16 (7475) a nivel de imagen, pero
    # unidad principal de analisis = individuo (agrupar por individual_id) ──
    known_by_species = defaultdict(list)  # species_name -> list of (embedding, individual_id, image_id)
    clean_embeddings_arr = clean["embeddings"]  # cargar UNA vez, evitar re-descomprimir en loop
    clean_image_ids_arr = clean["image_ids"]
    emb_by_id = {iid: clean_embeddings_arr[i] for i, iid in enumerate(clean_image_ids_arr)}
    for img in clean_manifest["images"]:
        name = img["scientific_name"].replace(" ", "_")
        known_by_species[name].append({
            "embedding": emb_by_id[img["image_id"]],
            "individual_id": img["individual_id"] or f"__noind__{img['image_id']}",
            "image_id": img["image_id"], "species_id": img["species_id"]
        })

    n_images_known = sum(len(v) for v in known_by_species.values())
    n_individuals_known = len({r["individual_id"] for v in known_by_species.values() for r in v})
    n_species_known = len(known_by_species)
    genera_known = {sp_meta(sp)[0] for sp in known_by_species}
    familias_known = {sp_meta(sp)[1] for sp in known_by_species}

    print(f"KNOWN: {n_images_known} imagenes, {n_individuals_known} individuos, "
          f"{n_species_known} especies, {len(genera_known)} generos, {len(familias_known)} familias")

    # ── UNKNOWN ──
    unknown_by_species = defaultdict(list)
    import re
    obs_pat = re.compile(r"col_obs_(\d+)_photo")
    for i, r in enumerate(unknown_records):
        m = obs_pat.search(r["path"])
        ind = m.group(1) if m else f"__noind__{i}"
        unknown_by_species[r["true_species"]].append({
            "embedding": X_unknown[i], "individual_id": ind, "image_id": r["image_id"]
        })
    n_images_unk = sum(len(v) for v in unknown_by_species.values())
    n_individuals_unk = len({r["individual_id"] for v in unknown_by_species.values() for r in v})
    print(f"UNKNOWN: {n_images_unk} imagenes, {n_individuals_unk} individuos, "
          f"{len(unknown_by_species)} especies")

    # ── Duplicate check (SHA256) dentro de KNOWN pool ──
    hashes_seen = {img["sha256"] for img in clean_manifest["images"]}
    dup_count = n_images_known - len(hashes_seen)
    print(f"Duplicados SHA256 dentro de KNOWN pool: {dup_count}")

    embedding_audit = {
        **phase19_manifest_meta,
        "known": {"n_images": n_images_known, "n_individuals": n_individuals_known,
                   "n_species": n_species_known, "n_genera": len(genera_known), "n_families": len(familias_known),
                   "duplicate_sha256_count": dup_count},
        "unknown": {"n_images": n_images_unk, "n_individuals": n_individuals_unk,
                     "n_species": len(unknown_by_species)},
        "limitation": "UNKNOWN limitado a 2 especies reales (Hyloxalus_picachos, Sachatamia_electrops), "
                      "11-15 individuos totales. No hay mas datos UNKNOWN reales en el repositorio."
    }
    with open(OUT / "embedding_audit.json", "w", encoding="utf-8") as f:
        json.dump(embedding_audit, f, indent=2, ensure_ascii=False, default=str)

    # ══════════════════════════════════════════════════════════════
    # Centroides (diagnostico, NO oficiales)
    # ══════════════════════════════════════════════════════════════
    species_centroids = {}
    species_genus = {}
    species_family = {}
    for name, records in known_by_species.items():
        embs = np.array([r["embedding"] for r in records])
        species_centroids[name] = embs.mean(axis=0)
        g, fam = sp_meta(name)
        species_genus[name] = g
        species_family[name] = fam

    species_list = sorted(species_centroids.keys())
    C = np.array([species_centroids[s] for s in species_list])

    # ══════════════════════════════════════════════════════════════
    # SECCION 4: analisis intraespecie
    # ══════════════════════════════════════════════════════════════
    print("\n=== SECCION 4: intra-especie ===")
    intra_species_stats = {}
    for name, records in known_by_species.items():
        embs = np.array([r["embedding"] for r in records])
        if len(embs) < 2:
            continue
        # Muestreo si hay demasiadas imagenes (evitar pdist O(n^2) gigante)
        if len(embs) > 300:
            rng = np.random.RandomState(42)
            idx = rng.choice(len(embs), 300, replace=False)
            embs_sample = embs[idx]
        else:
            embs_sample = embs
        d_eucl = pdist(embs_sample, metric="euclidean")
        d_cos = pdist(embs_sample, metric="cosine")
        intra_species_stats[name] = {
            "n_images": len(embs), "n_sampled_for_pairwise": len(embs_sample),
            "euclidean": {"mean": float(d_eucl.mean()), "median": float(np.median(d_eucl)),
                          "std": float(d_eucl.std()), "p05": float(np.percentile(d_eucl, 5)),
                          "p25": float(np.percentile(d_eucl, 25)), "p50": float(np.percentile(d_eucl, 50)),
                          "p75": float(np.percentile(d_eucl, 75)), "p95": float(np.percentile(d_eucl, 95)),
                          "max": float(d_eucl.max())},
            "cosine": {"mean": float(d_cos.mean()), "median": float(np.median(d_cos)),
                       "std": float(d_cos.std()), "p95": float(np.percentile(d_cos, 95))},
        }
    print(f"  Especies analizadas: {len(intra_species_stats)}")

    # ══════════════════════════════════════════════════════════════
    # SECCION 5: analisis interespecie + nearest_species_pairs.csv
    # ══════════════════════════════════════════════════════════════
    print("\n=== SECCION 5: inter-especie ===")
    dist_matrix_eucl = squareform(pdist(C, metric="euclidean"))
    dist_matrix_cos = squareform(pdist(C, metric="cosine"))

    pairs = []
    for i in range(len(species_list)):
        for j in range(i + 1, len(species_list)):
            sa, sb = species_list[i], species_list[j]
            ga, gb = species_genus[sa], species_genus[sb]
            fa, fb = species_family[sa], species_family[sb]
            if ga == gb:
                rel = "same_genus"
            elif fa == fb:
                rel = "same_family_diff_genus"
            else:
                rel = "diff_family"
            pairs.append({
                "species_a": sa, "species_b": sb, "genus_a": ga, "genus_b": gb,
                "family_a": fa, "family_b": fb,
                "centroid_distance_euclidean": float(dist_matrix_eucl[i, j]),
                "centroid_distance_cosine": float(dist_matrix_cos[i, j]),
                "taxonomic_relation": rel
            })
    pairs.sort(key=lambda x: x["centroid_distance_euclidean"])

    with open(OUT / "nearest_species_pairs.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(pairs[0].keys()))
        w.writeheader()
        w.writerows(pairs)

    by_relation = defaultdict(list)
    for p in pairs:
        by_relation[p["taxonomic_relation"]].append(p["centroid_distance_euclidean"])
    for rel, dists in by_relation.items():
        print(f"  {rel}: n={len(dists)}, mean_dist={np.mean(dists):.4f}, min={np.min(dists):.4f}")

    print("  Top 10 pares mas cercanos:")
    for p in pairs[:10]:
        print(f"    {p['species_a']} <-> {p['species_b']} ({p['taxonomic_relation']}): "
              f"eucl={p['centroid_distance_euclidean']:.4f}")

    # ══════════════════════════════════════════════════════════════
    # SECCION 6: margen de separacion por imagen KNOWN -> species_separation_report.csv
    # ══════════════════════════════════════════════════════════════
    print("\n=== SECCION 6: margen de separacion ===")
    species_idx = {s: i for i, s in enumerate(species_list)}
    margin_rows = []
    margin_by_species = defaultdict(list)

    for name, records in known_by_species.items():
        embs = np.array([r["embedding"] for r in records])
        if len(embs) > 200:
            rng = np.random.RandomState(123)
            idx_sample = rng.choice(len(embs), 200, replace=False)
            embs = embs[idx_sample]
        own_idx = species_idx[name]
        d_own = np.linalg.norm(embs - C[own_idx], axis=1)
        d_all = np.linalg.norm(embs[:, None, :] - C[None, :, :], axis=2)  # n x n_species
        d_all_masked = d_all.copy()
        d_all_masked[:, own_idx] = np.inf
        nearest_rival_idx = np.argmin(d_all_masked, axis=1)
        d_rival = d_all_masked[np.arange(len(embs)), nearest_rival_idx]
        margin = d_rival - d_own  # positivo = correcto mas cerca que rival (bueno)

        for k in range(len(embs)):
            margin_by_species[name].append(float(margin[k]))

    for name, margins in margin_by_species.items():
        m = np.array(margins)
        margin_rows.append({
            "species": name, "n_samples": len(m),
            "margin_mean": float(m.mean()), "margin_median": float(np.median(m)),
            "margin_p05": float(np.percentile(m, 5)), "margin_p25": float(np.percentile(m, 25)),
            "margin_p50": float(np.percentile(m, 50)), "margin_p75": float(np.percentile(m, 75)),
            "margin_p95": float(np.percentile(m, 95)),
            "fraction_negative_margin": float(np.mean(m < 0))
        })
    margin_rows.sort(key=lambda x: x["margin_mean"])

    with open(OUT / "species_separation_report.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(margin_rows[0].keys()))
        w.writeheader()
        w.writerows(margin_rows)

    print("  5 especies con peor margen (mean):")
    for r in margin_rows[:5]:
        print(f"    {r['species']}: margin_mean={r['margin_mean']:.4f}, "
              f"frac_negative={r['fraction_negative_margin']:.4f}")

    # ══════════════════════════════════════════════════════════════
    # SECCION 7: UNKNOWN analysis -> unknown_analysis.csv
    # ══════════════════════════════════════════════════════════════
    print("\n=== SECCION 7: UNKNOWN analysis ===")
    unknown_rows = []
    unknown_margin_records = []
    for uname, records in unknown_by_species.items():
        embs = np.array([r["embedding"] for r in records])
        n_ind = len({r["individual_id"] for r in records})
        d_all = np.linalg.norm(embs[:, None, :] - C[None, :, :], axis=2)
        nearest_idx = np.argmin(d_all, axis=1)
        d_nearest = d_all[np.arange(len(embs)), nearest_idx]

        second_masked = d_all.copy()
        for k in range(len(embs)):
            second_masked[k, nearest_idx[k]] = np.inf
        second_idx = np.argmin(second_masked, axis=1)

        for k in range(len(embs)):
            nn_sp = species_list[nearest_idx[k]]
            nn_genus, nn_family = species_genus[nn_sp], species_family[nn_sp]
            u_genus, u_family = sp_meta(uname)
            tax_rel = "same_genus" if u_genus == nn_genus else ("same_family" if u_family == nn_family else "diff_family")
            unknown_margin_records.append(d_nearest[k])
            unknown_rows.append({
                "unknown_species": uname, "image_id": records[k]["image_id"],
                "individual_id": records[k]["individual_id"],
                "nearest_known_species": nn_sp, "nearest_known_genus": nn_genus,
                "nearest_known_family": nn_family,
                "unknown_genus": u_genus, "unknown_family": u_family,
                "taxonomic_relation_to_nearest": tax_rel,
                "distance_to_nearest": float(d_nearest[k]),
                "distance_to_second_nearest": float(second_masked[k, second_idx[k]]),
            })
        print(f"  {uname}: n={len(embs)}, {n_ind} individuos")

    with open(OUT / "unknown_analysis.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(unknown_rows[0].keys()))
        w.writeheader()
        w.writerows(unknown_rows)

    tax_rel_counts = defaultdict(int)
    for r in unknown_rows:
        tax_rel_counts[r["taxonomic_relation_to_nearest"]] += 1
    print(f"  Relacion taxonomica UNKNOWN->nearest KNOWN: {dict(tax_rel_counts)}")

    # ══════════════════════════════════════════════════════════════
    # SECCION 8: KNOWN->KNOWN vs UNKNOWN->KNOWN (DIAGNOSTIC ONLY)
    # ══════════════════════════════════════════════════════════════
    print("\n=== SECCION 8: comparacion de distribuciones (DIAGNOSTIC ONLY) ===")
    known_own_dists = []
    for name, records in known_by_species.items():
        embs = np.array([r["embedding"] for r in records])
        if len(embs) > 200:
            rng = np.random.RandomState(7)
            embs = embs[rng.choice(len(embs), 200, replace=False)]
        own_idx = species_idx[name]
        d_all = np.linalg.norm(embs[:, None, :] - C[None, :, :], axis=2)
        known_own_dists.extend(np.min(d_all, axis=1).tolist())
    known_own_dists = np.array(known_own_dists)
    unknown_dists = np.array(unknown_margin_records)

    y_true = np.concatenate([np.zeros(len(known_own_dists)), np.ones(len(unknown_dists))])
    y_score = np.concatenate([known_own_dists, unknown_dists])
    auroc_diag = float(roc_auc_score(y_true, y_score))

    diagnostic_metrics = {
        "label": "DIAGNOSTIC_ONLY - not a new Open Set validation",
        "known_to_known": {
            "n": len(known_own_dists), "mean": float(known_own_dists.mean()), "median": float(np.median(known_own_dists)),
            "p05": float(np.percentile(known_own_dists, 5)), "p25": float(np.percentile(known_own_dists, 25)),
            "p50": float(np.percentile(known_own_dists, 50)), "p75": float(np.percentile(known_own_dists, 75)),
            "p95": float(np.percentile(known_own_dists, 95)),
        },
        "unknown_to_known": {
            "n": len(unknown_dists), "mean": float(unknown_dists.mean()), "median": float(np.median(unknown_dists)),
            "p05": float(np.percentile(unknown_dists, 5)), "p25": float(np.percentile(unknown_dists, 25)),
            "p50": float(np.percentile(unknown_dists, 50)), "p75": float(np.percentile(unknown_dists, 75)),
            "p95": float(np.percentile(unknown_dists, 95)),
        },
        "auroc_diagnostic_only": auroc_diag,
        "overlap_fraction_unknown_below_known_p95": float(np.mean(unknown_dists <= np.percentile(known_own_dists, 95))),
    }
    print(f"  KNOWN->KNOWN mean={known_own_dists.mean():.2f}, UNKNOWN->KNOWN mean={unknown_dists.mean():.2f}")
    print(f"  AUROC (diagnostic only): {auroc_diag:.4f}")

    # ══════════════════════════════════════════════════════════════
    # SECCION 9: taxonomy_separability_report.csv (genero/familia)
    # ══════════════════════════════════════════════════════════════
    print("\n=== SECCION 9: separabilidad taxonomica ===")
    taxonomy_rows = []
    same_genus_dists = [p["centroid_distance_euclidean"] for p in pairs if p["taxonomic_relation"] == "same_genus"]
    same_family_dists = [p["centroid_distance_euclidean"] for p in pairs if p["taxonomic_relation"] == "same_family_diff_genus"]
    diff_family_dists = [p["centroid_distance_euclidean"] for p in pairs if p["taxonomic_relation"] == "diff_family"]

    for label, dists in [("same_genus", same_genus_dists), ("same_family_diff_genus", same_family_dists),
                          ("diff_family", diff_family_dists)]:
        if dists:
            taxonomy_rows.append({
                "relation": label, "n_pairs": len(dists),
                "mean_centroid_distance": float(np.mean(dists)), "median": float(np.median(dists)),
                "std": float(np.std(dists)), "min": float(np.min(dists)), "max": float(np.max(dists)),
            })
    with open(OUT / "taxonomy_separability_report.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(taxonomy_rows[0].keys()))
        w.writeheader()
        w.writerows(taxonomy_rows)

    for r in taxonomy_rows:
        print(f"  {r['relation']}: n={r['n_pairs']}, mean_dist={r['mean_centroid_distance']:.4f}")

    hierarchy_consistent = (np.mean(same_genus_dists) < np.mean(same_family_dists) < np.mean(diff_family_dists))
    print(f"  Jerarquia visual consistente con taxonomia (genero<familia<diff_familia): {hierarchy_consistent}")

    # ══════════════════════════════════════════════════════════════
    # SECCION 10: centroid_diagnostics.csv
    # ══════════════════════════════════════════════════════════════
    centroid_rows = []
    for i, name in enumerate(species_list):
        d_to_others = dist_matrix_eucl[i].copy()
        d_to_others[i] = np.inf
        nn_idx = np.argmin(d_to_others)
        nn_sp = species_list[nn_idx]
        intra = intra_species_stats.get(name, {}).get("euclidean", {}).get("mean")
        centroid_rows.append({
            "species": name, "genus": species_genus[name], "family": species_family[name],
            "n_samples": len(known_by_species[name]),
            "intra_species_dist_mean": intra,
            "nearest_species": nn_sp, "nearest_species_genus": species_genus[nn_sp],
            "nearest_species_family": species_family[nn_sp],
            "distance_to_nearest_species": float(d_to_others[nn_idx]),
        })
    with open(OUT / "centroid_diagnostics.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(centroid_rows[0].keys()))
        w.writeheader()
        w.writerows(centroid_rows)

    # ══════════════════════════════════════════════════════════════
    # SECCION 13: diagnostico de hipotesis
    # ══════════════════════════════════════════════════════════════
    print("\n=== SECCION 13: diagnostico de hipotesis ===")

    # Evidencia clave:
    # - separacion intra vs inter (dentro de KNOWN): si same_genus dist es comparable a intra-class std,
    #   hay especies dificiles POR DISEÑO BIOLOGICO (esperado, no es "falla" del encoder per se)
    # - fraction_negative_margin alto => muchas imagenes mas cerca de un rival que de su propia especie
    frac_negative_margins = [r["fraction_negative_margin"] for r in margin_rows]
    mean_frac_negative = float(np.mean(frac_negative_margins))

    n_unknown_species = len(unknown_by_species)
    n_unknown_individuals = len({r["individual_id"] for v in unknown_by_species.values() for r in v})

    evidence = {
        "encoder_separability": {
            "hierarchy_consistent_with_taxonomy": bool(hierarchy_consistent),
            "same_genus_mean_dist": float(np.mean(same_genus_dists)),
            "diff_family_mean_dist": float(np.mean(diff_family_dists)),
            "ratio_diff_family_vs_same_genus": float(np.mean(diff_family_dists) / max(np.mean(same_genus_dists), 1e-9)),
            "mean_fraction_negative_margin_across_species": mean_frac_negative,
            "interpretation": "Si hierarchy_consistent=True Y el ratio es alto, el encoder SI organiza el "
                               "espacio segun taxonomia -- la dificultad esta en especies filogeneticamente "
                               "cercanas, no en el encoder en general."
        },
        "unknown_coverage": {
            "n_unknown_species": n_unknown_species, "n_unknown_individuals": n_unknown_individuals,
            "sufficient_for_strong_conclusion": n_unknown_species >= 5 and n_unknown_individuals >= 30,
            "interpretation": "2 especies / <20 individuos es insuficiente para concluir sobre "
                               "'capacidad general de rechazo Open Set' -- solo permite diagnostico de estos "
                               "2 casos especificos."
        },
        "postprocessing_evidence": {
            "diagnostic_auroc_raw_distance": auroc_diag,
            "note": "auroc_diag usa distancia cruda al centroide mas cercano (equivalente a Euclidean sin "
                    "threshold), comparable a AUROC de Fase 17/18. Si este numero tambien es mediocre, el "
                    "problema no es el mecanismo de rechazo posterior (threshold/metodo) sino la separacion "
                    "de base del embedding para estas especies."
        }
    }

    # Decision de hipotesis basada en evidencia, no en intuicion
    unknown_insufficient = not evidence["unknown_coverage"]["sufficient_for_strong_conclusion"]
    encoder_weak_for_hard_pairs = not hierarchy_consistent or evidence["encoder_separability"]["ratio_diff_family_vs_same_genus"] < 3

    if unknown_insufficient and encoder_weak_for_hard_pairs:
        hypothesis = "D_MIXED"
    elif unknown_insufficient:
        hypothesis = "C_UNKNOWN_COVERAGE_INSUFFICIENT"
    elif encoder_weak_for_hard_pairs:
        hypothesis = "A_ENCODER_SEPARABILITY_INSUFFICIENT"
    else:
        hypothesis = "B_POSTPROCESSING_REJECTION_PROBLEM"

    evidence["diagnosed_hypothesis"] = hypothesis
    with open(OUT / "diagnostic_metrics.json", "w", encoding="utf-8") as f:
        json.dump({**diagnostic_metrics, "hypothesis_evidence": evidence}, f, indent=2, ensure_ascii=False, default=str)

    print(f"\n  HIPOTESIS DIAGNOSTICADA: {hypothesis}")

    # ══════════════════════════════════════════════════════════════
    # Guardar intra_species_stats, phase19_manifest
    # ══════════════════════════════════════════════════════════════
    with open(OUT / "intra_species_stats.json", "w", encoding="utf-8") as f:
        json.dump(intra_species_stats, f, indent=2, ensure_ascii=False)

    phase19_manifest = {
        **phase19_manifest_meta,
        "n_known_images": n_images_known, "n_known_individuals": n_individuals_known,
        "n_known_species": n_species_known, "n_known_genera": len(genera_known), "n_known_families": len(familias_known),
        "n_unknown_images": n_images_unk, "n_unknown_individuals": n_individuals_unk,
        "n_unknown_species": len(unknown_by_species),
    }
    with open(OUT / "phase19_manifest.json", "w", encoding="utf-8") as f:
        json.dump(phase19_manifest, f, indent=2, ensure_ascii=False, default=str)

    # Guardar objetos intermedios para el script de figuras (evitar recalcular)
    np.savez_compressed(OUT / "_intermediate_for_plots.npz",
                         centroids=C, species_list=np.array(species_list),
                         dist_matrix_eucl=dist_matrix_eucl,
                         known_own_dists=known_own_dists, unknown_dists=unknown_dists,
                         same_genus_dists=np.array(same_genus_dists),
                         same_family_dists=np.array(same_family_dists),
                         diff_family_dists=np.array(diff_family_dists))

    print("\n[OK] Fase 19 analisis numerico completo.")


if __name__ == "__main__":
    main()
