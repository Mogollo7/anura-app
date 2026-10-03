"""
generate_figures.py — FASE 19.12: visualizaciones diagnosticas.
PCA usado UNICAMENTE para la proyeccion 2D visual (embedding_projection.png).
Ninguna otra metrica de esta fase depende de PCA/UMAP -- todas usan el espacio 512D original.
UMAP no disponible en el entorno (verificado); se usa PCA para la proyeccion, documentado aqui.
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from sklearn.decomposition import PCA

ROOT = Path(r"D:\Anura")
OUT = ROOT / "validation" / "fase19_embedding_separability"
FIG = OUT / "figures"


def main():
    data = np.load(OUT / "_intermediate_for_plots.npz", allow_pickle=True)
    C = data["centroids"]
    species_list = data["species_list"]
    dist_matrix_eucl = data["dist_matrix_eucl"]
    known_own_dists = data["known_own_dists"]
    unknown_dists = data["unknown_dists"]
    same_genus_dists = data["same_genus_dists"]
    same_family_dists = data["same_family_dists"]
    diff_family_dists = data["diff_family_dists"]

    with open(OUT / "intra_species_stats.json", encoding="utf-8") as f:
        intra_stats = json.load(f)

    # ── 1. intra_vs_inter.png ──
    intra_means = [v["euclidean"]["mean"] for v in intra_stats.values()]
    plt.figure(figsize=(8, 5))
    plt.hist(intra_means, bins=20, alpha=0.6, label="Intra-especie (mean dist)", color="tab:blue")
    plt.hist(same_genus_dists, bins=20, alpha=0.6, label="Inter-especie mismo genero (centroid dist)", color="tab:orange")
    plt.xlabel("Distancia Euclidiana"); plt.ylabel("Frecuencia")
    plt.title("Distribucion: dispersion intra-especie vs distancia inter-especie (mismo genero)")
    plt.legend(); plt.tight_layout()
    plt.savefig(FIG / "intra_vs_inter.png", dpi=120); plt.close()

    # ── 2. known_vs_unknown.png ──
    plt.figure(figsize=(8, 5))
    plt.hist(known_own_dists, bins=40, alpha=0.6, density=True, label="KNOWN -> nearest centroid", color="tab:green")
    plt.hist(unknown_dists, bins=20, alpha=0.6, density=True, label="UNKNOWN -> nearest centroid", color="tab:red")
    plt.xlabel("Distancia al centroide mas cercano"); plt.ylabel("Densidad")
    plt.title("DIAGNOSTIC ONLY: KNOWN->KNOWN vs UNKNOWN->KNOWN")
    plt.legend(); plt.tight_layout()
    plt.savefig(FIG / "known_vs_unknown.png", dpi=120); plt.close()

    # ── 3. species_distance_matrix.png ──
    plt.figure(figsize=(12, 10))
    plt.imshow(dist_matrix_eucl, cmap="viridis")
    plt.colorbar(label="Distancia euclidiana entre centroides")
    plt.title(f"Matriz de distancias entre {len(species_list)} centroides KNOWN")
    plt.tight_layout()
    plt.savefig(FIG / "species_distance_matrix.png", dpi=120); plt.close()

    # ── 4. genus_separation.png ──
    plt.figure(figsize=(8, 5))
    plt.boxplot([same_genus_dists, same_family_dists, diff_family_dists],
                tick_labels=["Mismo genero", "Misma familia\n(distinto genero)", "Distinta familia"])
    plt.ylabel("Distancia entre centroides (euclidiana)")
    plt.title("Separacion por nivel taxonomico")
    plt.tight_layout()
    plt.savefig(FIG / "genus_separation.png", dpi=120); plt.close()

    # ── 5. family_separation.png (mismo dato, enfoque familia vs resto) ──
    plt.figure(figsize=(6, 5))
    plt.bar(["Mismo genero", "Misma familia", "Distinta familia"],
            [np.mean(same_genus_dists), np.mean(same_family_dists), np.mean(diff_family_dists)],
            yerr=[np.std(same_genus_dists), np.std(same_family_dists), np.std(diff_family_dists)],
            capsize=5, color=["tab:red", "tab:orange", "tab:blue"])
    plt.ylabel("Distancia media entre centroides")
    plt.title("Separacion promedio por relacion taxonomica")
    plt.tight_layout()
    plt.savefig(FIG / "family_separation.png", dpi=120); plt.close()

    # ── 6. embedding_projection.png (PCA, SOLO visualizacion) ──
    pca = PCA(n_components=2, random_state=42)
    C_2d = pca.fit_transform(C)
    plt.figure(figsize=(10, 8))
    plt.scatter(C_2d[:, 0], C_2d[:, 1], s=40, alpha=0.7)
    for i, sp in enumerate(species_list):
        plt.annotate(str(sp), (C_2d[i, 0], C_2d[i, 1]), fontsize=6, alpha=0.7)
    plt.xlabel(f"PC1 ({pca.explained_variance_ratio_[0]*100:.1f}% var)")
    plt.ylabel(f"PC2 ({pca.explained_variance_ratio_[1]*100:.1f}% var)")
    plt.title("Proyeccion PCA de centroides KNOWN (SOLO visualizacion, no metrica)")
    plt.tight_layout()
    plt.savefig(FIG / "embedding_projection.png", dpi=120); plt.close()

    pca_meta = {
        "method": "PCA", "n_components": 2, "random_state": 42,
        "explained_variance_ratio": pca.explained_variance_ratio_.tolist(),
        "note": "UMAP no disponible en el entorno; PCA usado unicamente para esta figura, "
                "ninguna metrica principal de Fase 19 depende de esta proyeccion."
    }
    with open(OUT / "pca_projection_metadata.json", "w", encoding="utf-8") as f:
        json.dump(pca_meta, f, indent=2)

    print("[OK] 6 figuras generadas en", FIG)


if __name__ == "__main__":
    main()
