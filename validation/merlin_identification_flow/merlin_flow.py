"""Capa determinista de integración Merlin; no ejecuta ni modifica experimentos congelados."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import visual_similarity

ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = ROOT / "taxonomy" / "species" / "species_registry.json"
GEO6_W_GEO_RANK = 0.3
DIAGNOSTIC_LOW = 0.519000742678619
DIAGNOSTIC_HIGH = 0.8233217349267955


@dataclass(frozen=True)
class VisualCandidate:
    scientific_name: str
    visual_score: float


class MerlinFlow:
    """Orquesta evidencia ya calculada por adaptadores de runtime validados.

    ``visual_score``, ``geographic_score`` y ``ranking_score`` son scores, no
    probabilidades. Familia y género se adjuntan exclusivamente como metadata.
    """

    def __init__(
        self,
        registry_path: Path = REGISTRY_PATH,
        visual_similarity_config: Path | None = None,
    ) -> None:
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        self.catalog = {item["scientific_name"]: item for item in registry["species"]}
        self.catalog_version = registry_path.name + ":" + str(registry.get("species_count", len(self.catalog)))
        self.visual_similarity_groups, self.visual_similarity_rule = visual_similarity.load_groups(
            visual_similarity_config
        )

    def identify(
        self,
        *,
        observation_id: str,
        input_metadata: dict[str, Any],
        is_anuran: bool | None,
        anuran_evidence: dict[str, Any],
        visual_candidates: Iterable[VisualCandidate],
        geographic_scores: dict[str, float] | None = None,
        geographic_context_available: bool = False,
        open_set_unknownness_score: float | None = None,
        open_set_thresholds: dict[str, float] | None = None,
        open_set_decision: str | None = None,
        open_set_evidence_override: dict[str, Any] | None = None,
        segmentation_evidence: list[dict[str, str]] | None = None,
        visual_similarity_groups: list[dict[str, Any]] | None = None,
        visual_similarity_top_k: int | None = None,
        catalog_state: dict[str, Any] | None = None,
        active_species_ids: Iterable[str] | None = None,
        top_k: int = 3,
        model_version: str = "BioCLIP-adapter-not-connected",
    ) -> dict[str, Any]:
        """``active_species_ids``: catalogo activo que produjo la evidencia.

        Si se declara, ningun candidato ni especie aceptada por Open Set puede
        quedar fuera de el (precondicion independiente del threshold). Si es
        ``None`` (fixtures / modo sin gestor) el comportamiento no cambia.
        """
        if top_k < 1:
            raise ValueError("top_k must be >= 1")
        membership = None if active_species_ids is None else frozenset(active_species_ids)
        limitations: list[str] = []
        flags = ["EXPERIMENTAL_GEO6_W_GEO_RANK_0_3", "SCORES_ARE_NOT_PROBABILITIES"]
        geo = geographic_scores or {}
        candidates = self._rank(visual_candidates, geo, geographic_context_available, top_k, membership)
        geo_used = any(c["geographic_context_available"] for c in candidates)
        if not geographic_context_available:
            limitations.append("GEOGRAPHIC_CONTEXT_UNAVAILABLE")
        elif not geo_used:
            limitations.append("GEOGRAPHIC_CONTEXT_AVAILABLE_BUT_NO_CANDIDATE_SCORE")
        if geographic_context_available:
            flags.append("GEOGRAPHIC_CONTEXT_WHEN_AVAILABLE_ONLY")

        if open_set_decision is not None:
            if open_set_decision not in {"ESPECIE_CONOCIDA", "NO_CONCLUYENTE"}:
                raise ValueError("Only ESPECIE_CONOCIDA or NO_CONCLUYENTE can be supplied by Open Set")
            decision = open_set_decision if is_anuran is True else "NO_CONCLUYENTE"
            open_evidence = open_set_evidence_override or {"status": "UNSPECIFIED"}
            decision_limitations = ([] if decision == "ESPECIE_CONOCIDA" else ["NO_REGISTRADA_NOT_ASSERTED"])
            if membership is not None and decision == "ESPECIE_CONOCIDA":
                accepted = open_evidence.get("nearest_species_id")
                if accepted in membership:
                    open_evidence = {**open_evidence, "catalog_membership_gate": {"passed": True}}
                else:
                    # Pertenencia al catalogo activo: precondicion independiente del threshold.
                    decision = "NO_CONCLUYENTE"
                    open_evidence = {
                        **open_evidence,
                        "score": None,
                        "nearest_species_id": None,
                        "catalog_membership_gate": {
                            "passed": False,
                            "rejected_species_id": accepted,
                            "rejected_score": open_evidence.get("score"),
                            "reason": "OPEN_SET_ACCEPTED_SPECIES_NOT_IN_ACTIVE_CATALOG",
                        },
                    }
                    decision_limitations = ["OPEN_SET_ACCEPTED_SPECIES_NOT_IN_ACTIVE_CATALOG", "NO_REGISTRADA_NOT_ASSERTED"]
        else:
            decision, open_evidence, decision_limitations = self._open_set_decision(
                is_anuran, open_set_unknownness_score, open_set_thresholds
            )
        limitations.extend(decision_limitations)
        explanation = self._explain(candidates, decision, geo_used, geographic_context_available, open_evidence)
        # Capa de INTERPRETACION: se calcula sobre `candidates` ya construido y
        # NO lo modifica (ni scores, ni orden, ni `decision`).
        groups = visual_similarity_groups if visual_similarity_groups is not None else self.visual_similarity_groups
        rule_top_k = visual_similarity_top_k or self.visual_similarity_rule.get("top_k", 3)
        warnings = visual_similarity.evaluate(candidates, groups, top_k=rule_top_k)
        if warnings:
            limitations.append("VISUALLY_SIMILAR_SPECIES_IN_TOP_CANDIDATES")
        return {
            "observation_id": observation_id,
            "input_metadata": input_metadata,
            "is_anuran": is_anuran,
            "anuran_evidence": anuran_evidence,
            "candidates": candidates,
            "decision": decision,
            "open_set_evidence": open_evidence,
            "explanation": explanation,
            "limitations": sorted(set(limitations)),
            "segmentation_evidence": self._validate_segmentation(segmentation_evidence or []),
            "visual_similarity_warnings": warnings,
            "model_version": model_version,
            "catalog_version": self.catalog_version,
            "catalog_state": catalog_state or {"source": "STATIC_SPECIES_REGISTRY", "package_manager_connected": False},
            "geographic_context_used": geo_used,
            "geographic_context_available": geographic_context_available,
            "experimental_flags": flags,
        }

    def _rank(self, visual_candidates: Iterable[VisualCandidate], geo: dict[str, float], geo_available: bool, top_k: int, membership: frozenset[str] | None = None) -> list[dict[str, Any]]:
        rows = []
        for candidate in visual_candidates:
            taxon = self.catalog.get(candidate.scientific_name)
            if taxon is None:
                raise ValueError(f"Candidate outside species registry: {candidate.scientific_name}")
            if membership is not None and taxon["species_id"] not in membership:
                # El registro taxonomico es metadata, no catalogo activo.
                continue
            geographic_score = geo.get(candidate.scientific_name) if geo_available else None
            has_geo = geographic_score is not None
            # Missing geographic evidence does not become a negative signal.
            ranking_score = ((1 - GEO6_W_GEO_RANK) * candidate.visual_score + GEO6_W_GEO_RANK * geographic_score) if has_geo else candidate.visual_score
            rows.append({
                "species_id": taxon["species_id"], "scientific_name": candidate.scientific_name,
                "common_name": taxon.get("common_name"), "genus": taxon.get("genus"), "family": taxon.get("family"),
                "visual_score": candidate.visual_score, "geographic_score": geographic_score,
                "ranking_score": ranking_score, "geographic_context_available": has_geo,
            })
        rows.sort(key=lambda item: item["ranking_score"], reverse=True)
        for rank, item in enumerate(rows[:top_k], start=1):
            item["rank"] = rank
        return rows[:top_k]

    def _open_set_decision(self, is_anuran: bool | None, score: float | None, thresholds: dict[str, float] | None) -> tuple[str, dict[str, Any], list[str]]:
        if is_anuran is not True:
            return "NO_CONCLUYENTE", {"status": "NOT_EVALUATED", "reason": "INITIAL_ANURAN_VALIDATION_NOT_PASSED"}, ["INITIAL_ANURAN_VALIDATION_NOT_PASSED"]
        if score is None:
            return "NO_CONCLUYENTE", {"status": "UNAVAILABLE", "reason": "OPEN_SET_EVIDENCE_UNAVAILABLE"}, ["OPEN_SET_EVIDENCE_UNAVAILABLE"]
        supplied = thresholds or {"low": DIAGNOSTIC_LOW, "high": DIAGNOSTIC_HIGH}
        low, high = supplied["low"], supplied["high"]
        if low >= high:
            raise ValueError("Open Set thresholds require low < high")
        evidence = {"status": "DIAGNOSTIC", "unknownness_score": score, "low_threshold": low, "high_threshold": high, "thresholds_production_ready": False}
        if score < low:
            return "ESPECIE_CONOCIDA", evidence, ["OPEN_SET_THRESHOLDS_DIAGNOSTIC"]
        # The current scientific evidence does not support an automatic NO_REGISTRADA claim.
        evidence["reason"] = "INSUFFICIENT_EVIDENCE_TO_DISTINGUISH_UNREGISTERED_FROM_AMBIGUOUS"
        return "NO_CONCLUYENTE", evidence, ["OPEN_SET_THRESHOLDS_DIAGNOSTIC", "NO_REGISTRADA_NOT_ASSERTED"]

    @staticmethod
    def _validate_segmentation(evidence: list[dict[str, str]]) -> list[dict[str, str]]:
        valid = {"PRESENTE", "AUSENTE", "NO_EVALUABLE"}
        for item in evidence:
            if item.get("state") not in valid or not item.get("feature"):
                raise ValueError("Segmentation evidence requires feature and PRESENTE/AUSENTE/NO_EVALUABLE")
        return evidence

    @staticmethod
    def _explain(candidates: list[dict[str, Any]], decision: str, geo_used: bool, geo_available: bool, open_evidence: dict[str, Any]) -> dict[str, Any]:
        return {
            "candidate_summary": "Candidatos ordenados por compatibilidad; los scores no son probabilidades.",
            "most_visual_compatible": max(candidates, key=lambda c: c["visual_score"])["scientific_name"] if candidates else None,
            "geographic_context": "USED_FOR_RANKING" if geo_used else ("AVAILABLE_BUT_NOT_APPLIED" if geo_available else "UNAVAILABLE"),
            "information_used": ["visual_similarity"] + (["species_geographic_context"] if geo_used else []) + (["open_set_evidence"] if open_evidence.get("status") not in {"UNAVAILABLE", "NOT_EVALUATED"} else []),
            "information_unavailable": ([] if geo_available else ["geographic_context"]) + ([] if open_evidence.get("status") not in {"UNAVAILABLE", "NOT_EVALUATED"} else ["open_set_evidence"]),
            "decision": decision,
            "why_top1_not_automatically_accepted": "Ranking ordena candidatos; la aceptación depende de una etapa Open Set separada.",
        }
