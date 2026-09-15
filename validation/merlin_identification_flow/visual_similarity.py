"""Capa de INTERPRETACION: advertencia de especies visualmente parecidas.

Contrato duro:
  - Es puramente aditiva. No modifica scores, no reordena candidatos,
    no elige ganador y no cambia la decision Open Set.
  - Ninguna pareja esta hardcodeada: todo sale de la configuracion.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Sequence

HERE = Path(__file__).resolve().parent
DEFAULT_CONFIG = HERE / "visual_similarity_groups.json"
DEFAULT_TOP_K = 3


def load_groups(config_path: Path | None = None) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    path = Path(config_path or DEFAULT_CONFIG)
    if not path.exists():
        return [], {"trigger": "TWO_OR_MORE_GROUP_MEMBERS_IN_TOP_K", "top_k": DEFAULT_TOP_K}
    document = json.loads(path.read_text(encoding="utf-8"))
    rule = document.get("presentation_rule", {})
    rule.setdefault("top_k", DEFAULT_TOP_K)
    return document.get("groups", []), rule


def evaluate(
    candidates: Sequence[dict[str, Any]],
    groups: Sequence[dict[str, Any]],
    *,
    top_k: int = DEFAULT_TOP_K,
) -> list[dict[str, Any]]:
    """Devuelve advertencias para grupos con >=2 miembros dentro del Top-K.

    ``candidates`` se lee, nunca se muta.
    """
    window = list(candidates)[:top_k]
    present_ids = {item.get("species_id") for item in window}
    present_names = {item.get("scientific_name") for item in window}
    warnings: list[dict[str, Any]] = []
    for group in groups:
        if not group.get("enabled", True):
            continue
        matched_ids = [sid for sid in group.get("species_ids", []) if sid in present_ids]
        matched_names = [name for name in group.get("scientific_names", []) if name in present_names]
        if len(matched_ids) < 2 and len(matched_names) < 2:
            continue
        warnings.append(
            {
                "group_id": group["group_id"],
                "label": group["label"],
                "description": group["description"],
                "matched_species_ids": matched_ids,
                "matched_scientific_names": matched_names,
                "trigger": f"AT_LEAST_TWO_GROUP_MEMBERS_IN_TOP_{top_k}",
                "advisory_only": True,
                "affects_scores": False,
                "affects_ranking": False,
                "affects_decision": False,
                "provenance": group.get("provenance"),
            }
        )
    return sorted(warnings, key=lambda item: item["group_id"])
