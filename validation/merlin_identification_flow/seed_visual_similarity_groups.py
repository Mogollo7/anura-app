"""Siembra `visual_similarity_groups.json` con evidencia MEDIDA, no inventada.

Metodo (documentado y reproducible):
  1. Se toman los 41 centroides del pool GEO-6 (VisualRankingAdapter), que es
     exactamente el pool que el ranking usa en produccion.
  2. Se calculan las 820 distancias euclidianas par-a-par.
  3. Criterio de umbral: un par es CANDIDATO si su distancia esta por debajo
     del percentil 1 de esa distribucion empirica (umbral data-driven, no
     una constante elegida a mano).
  4. Los pares candidatos se agrupan por componentes conexas (cierre
     transitivo), de modo que A~B y B~C producen el grupo {A,B,C}.
  5. Cada grupo guarda su procedencia: pares medidos, distancias, metodo,
     umbral y fecha.

No se hardcodea ninguna pareja: si los centroides cambian, el archivo cambia.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from runtime_adapters import VisualRankingAdapter  # noqa: E402

PERCENTILE = 1.0
OUTPUT = HERE / "visual_similarity_groups.json"
LABEL = "ESPECIES VISUALMENTE MUY PARECIDAS"
DESCRIPTION = (
    "Estas especies presentan caracteristicas externas muy similares. "
    "La fotografia por si sola puede no ser suficiente para una identificacion concluyente."
)


def main() -> None:
    adapter = VisualRankingAdapter()
    names = list(adapter.names)
    centroids = adapter.centroids
    n = len(names)
    distances = np.linalg.norm(centroids[:, None, :] - centroids[None, :, :], axis=2)
    upper = np.triu_indices(n, 1)
    values = distances[upper]
    threshold = float(np.percentile(values, PERCENTILE))

    registry = json.loads(
        (HERE.parents[1] / "taxonomy/species/species_registry.json").read_text(encoding="utf-8")
    )
    species_id_by_name = {item["scientific_name"]: item["species_id"] for item in registry["species"]}

    pairs = []
    for i, j in zip(*upper):
        value = float(distances[i, j])
        if value <= threshold:
            pairs.append((value, names[i], names[j]))
    pairs.sort()

    # Componentes conexas sobre los pares candidatos.
    parent = {name: name for name in names}

    def find(x: str) -> str:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for _, a, b in pairs:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    components: dict[str, list[str]] = {}
    for _, a, b in pairs:
        components.setdefault(find(a), [])
        for name in (a, b):
            if name not in components[find(a)]:
                components[find(a)].append(name)

    groups = []
    for index, (_, members) in enumerate(sorted(components.items(), key=lambda kv: sorted(kv[1])), start=1):
        members = sorted(members)
        genus = {name.split()[0] for name in members}
        slug = (next(iter(genus)) if len(genus) == 1 else "mixed").lower()
        group_pairs = [
            {
                "species": [a, b],
                "euclidean_centroid_distance": round(value, 6),
            }
            for value, a, b in pairs
            if a in members and b in members
        ]
        groups.append(
            {
                "group_id": f"VSG_{slug.upper()}_{index:02d}",
                "species_ids": [species_id_by_name[name] for name in members],
                "scientific_names": members,
                "label": LABEL,
                "description": DESCRIPTION,
                "enabled": True,
                "provenance": {
                    "method": "euclidean distance between GEO-6 Fase-13 centroids (41-species pool)",
                    "criterion": f"pairwise distance <= percentile {PERCENTILE} of the 820-pair distribution",
                    "threshold_value": round(threshold, 6),
                    "measured_pairs": group_pairs,
                    "measured_on": time.strftime("%Y-%m-%d"),
                    "centroid_source": "evaluation/fase13/embeddings/{reference,train}_embeddings.npz",
                },
            }
        )

    document = {
        "schema_version": "anura.visual-similarity-groups/1.0.0",
        "presentation_rule": {
            "trigger": "TWO_OR_MORE_GROUP_MEMBERS_IN_TOP_K",
            "top_k": 3,
            "effect": "ADVISORY_ONLY",
            "must_not": [
                "modify visual_score/geographic_score/ranking_score",
                "reorder candidates",
                "select a winner",
                "change the Open Set decision",
            ],
        },
        "distribution_stats": {
            "pool_size": n,
            "pair_count": int(values.size),
            "min": round(float(values.min()), 6),
            "mean": round(float(values.mean()), 6),
            "max": round(float(values.max()), 6),
            "percentile_used": PERCENTILE,
            "threshold_value": round(threshold, 6),
        },
        "notes": [
            "Rhinella marina NO existe en species_registry.json ni en los embeddings de Fase 13; "
            "el catalogo contiene Rhinella alata, Rhinella horribilis y Rhinella margaritifera. "
            "El par Rhinella mas cercano medido es alata|margaritifera.",
            "Rhinella rivularis NO existe en el catalogo; no se inventa.",
        ],
        "groups": groups,
    }
    OUTPUT.write_text(json.dumps(document, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"threshold": threshold, "group_count": len(groups),
                      "groups": [(g["group_id"], g["scientific_names"]) for g in groups]},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
