"""Auditoría lógica: ¿familia/género/especie/ubicación/altura se usan como contexto?

No modifica artefactos congelados. Evalúa el código runtime y los paquetes.
"""
from __future__ import annotations

import ast
import inspect
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

from merlin_flow import MerlinFlow, VisualCandidate  # noqa: E402
from package_manager import FilesystemPackageSource, LocalPackageManager  # noqa: E402
from runtime_adapters import GeographicAdapter  # noqa: E402
import merlin_runtime_pipeline as pipeline_mod  # noqa: E402
import merlin_flow as flow_mod  # noqa: E402
import runtime_adapters as adapters_mod  # noqa: E402


def source_of(obj) -> str:
    return inspect.getsource(obj)


def mentions(text: str, *needles: str) -> dict[str, bool]:
    lower = text.lower()
    return {n: n.lower() in lower for n in needles}


def audit_code_wiring() -> dict:
    pipeline_src = source_of(pipeline_mod.MerlinRuntimePipeline.identify_image)
    flow_rank_src = source_of(flow_mod.MerlinFlow._rank)
    geo_src = source_of(adapters_mod.GeographicAdapter.scores)
    identify_params = list(inspect.signature(pipeline_mod.MerlinRuntimePipeline.identify_image).parameters)

    # AST: does identify_image call package geography/elevation?
    tree = ast.parse(Path(pipeline_mod.__file__).read_text(encoding="utf-8"))
    calls = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                calls.append(node.func.attr)
            elif isinstance(node.func, ast.Name):
                calls.append(node.func.id)

    return {
        "identify_image_parameters": identify_params,
        "has_latitude_longitude_params": "latitude" in identify_params and "longitude" in identify_params,
        "has_elevation_param": "elevation" in identify_params or "altitude" in identify_params,
        "pipeline_calls_active_geography": "active_geography" in calls,
        "pipeline_calls_active_elevation": "active_elevation" in calls,
        "ranking_formula_uses_geo_weight_0_3": "GEO6_W_GEO_RANK" in flow_rank_src,
        "ranking_attaches_genus_family_as_metadata": mentions(flow_rank_src, "genus", "family") == {"genus": True, "family": True},
        "ranking_formula_includes_genus_or_family": any(
            token in flow_rank_src for token in ("genus_score", "family_score", "prior_genus", "prior_family")
        ),
        "geographic_adapter_requires_lat_lon": "LOCATION_UNAVAILABLE" in geo_src,
        "geographic_adapter_uses_species_prior_only": "prior_zone_taxon" in geo_src and "genus" not in geo_src.lower() and "family" not in geo_src.lower(),
        "pipeline_src_mentions": mentions(pipeline_src, "elevation", "altitude", "family", "genus", "geography"),
    }


def audit_packages() -> dict:
    repo = HERE / "package_repository"
    source = FilesystemPackageSource(repo)
    refs = {ref.key: ref for ref in source.list_available()}
    rows = []
    for key, ref in sorted(refs.items()):
        pkg_dir = repo / ref.package_id / ref.package_version
        taxonomy = json.loads((pkg_dir / "taxonomy.json").read_text(encoding="utf-8")) if (pkg_dir / "taxonomy.json").exists() else {}
        species = json.loads((pkg_dir / "species.json").read_text(encoding="utf-8"))["species"]
        geo = pkg_dir / "geography.json"
        elev = pkg_dir / "elevation.json"
        tax_entries = taxonomy.get("by_species") or taxonomy.get("species") or {}
        if isinstance(tax_entries, dict):
            tax_count = len(tax_entries)
            with_family = sum(1 for v in tax_entries.values() if isinstance(v, dict) and v.get("family"))
            with_genus = sum(1 for v in tax_entries.values() if isinstance(v, dict) and v.get("genus"))
        elif isinstance(tax_entries, list):
            tax_count = len(tax_entries)
            with_family = sum(1 for v in tax_entries if v.get("family"))
            with_genus = sum(1 for v in tax_entries if v.get("genus"))
        else:
            tax_count = with_family = with_genus = 0
        rows.append({
            "package": key,
            "species_count": len(species),
            "taxonomy_entries": tax_count,
            "taxonomy_with_family": with_family,
            "taxonomy_with_genus": with_genus,
            "families_listed": len(taxonomy.get("families") or []),
            "genera_listed": len(taxonomy.get("genera") or []),
            "has_geography_json": geo.exists(),
            "has_elevation_json": elev.exists(),
        })
    return {"packages": rows}


def functional_probe() -> dict:
    """Probes deterministas sin ONNX: MerlinFlow + GeographicAdapter."""
    flow = MerlinFlow()
    # Familia/género aparecen en metadata pero no cambian ranking
    base = [
        VisualCandidate("Boana boans", 0.70),
        VisualCandidate("Dendrobates truncatus", 0.80),
        VisualCandidate("Pristimantis paisa", 0.60),
    ]
    no_geo = flow.identify(
        observation_id="probe:no-geo",
        input_metadata={},
        is_anuran=True,
        anuran_evidence={"source": "audit"},
        visual_candidates=base,
        geographic_context_available=False,
        open_set_unknownness_score=0.1,
        open_set_thresholds={"low": 0.2, "high": 0.9},
    )
    with_geo = flow.identify(
        observation_id="probe:geo",
        input_metadata={},
        is_anuran=True,
        anuran_evidence={"source": "audit"},
        visual_candidates=base,
        geographic_scores={"Boana boans": 1.0, "Dendrobates truncatus": 0.0, "Pristimantis paisa": 0.0},
        geographic_context_available=True,
        open_set_unknownness_score=0.1,
        open_set_thresholds={"low": 0.2, "high": 0.9},
    )
    # ranking with strong geo should prefer Boana despite lower visual
    # score = 0.7*visual + 0.3*geo => Boana=0.7*0.7+0.3*1=0.79; Dend=0.7*0.8+0.3*0=0.56
    top1_no_geo = no_geo["candidates"][0]["scientific_name"]
    top1_with_geo = with_geo["candidates"][0]["scientific_name"]

    genus_family_present = all(
        c.get("genus") and c.get("family") for c in no_geo["candidates"]
    )
    # Prove genus/family do not affect score: same visual, different taxa metadata already attached
    ranking_scores_no_geo = [c["ranking_score"] for c in no_geo["candidates"]]
    ranking_equals_visual = ranking_scores_no_geo == [c["visual_score"] for c in no_geo["candidates"]]

    geo = GeographicAdapter()
    empty, meta_empty = geo.scores(["Boana boans"], None, None)
    # Approximate Antioquia cell — Medellín ~6.25, -75.57
    scored, meta_ok = geo.scores(
        ["Boana boans", "Dendrobates truncatus", "Pristimantis paisa"],
        6.25,
        -75.57,
    )
    outside, meta_out = geo.scores(["Boana boans"], -33.0, -70.0)

    # Package manager: context readable but not consumed by pipeline signature
    import shutil
    import tempfile

    repo = HERE / "package_repository"
    tmp = Path(tempfile.mkdtemp(prefix="merlin-context-audit-"))
    try:
        manager = LocalPackageManager(tmp)
        source = FilesystemPackageSource(repo)
        refs = {ref.key: ref for ref in source.list_available()}
        ant_key = "anura_antioquia_visual@v1.1.0"
        if ant_key in refs:
            manager.install(source, refs[ant_key])
            manager.activate("anura_antioquia_visual", "v1.1.0")
            geo_entries = len(manager.active_geography())
            elev_entries = len(manager.active_elevation())
            tax = manager.catalog_state_summary()
            taxonomy_path = tmp / "installed" / "anura_antioquia_visual" / "v1.1.0" / "taxonomy.json"
            if taxonomy_path.exists():
                tax_data = json.loads(taxonomy_path.read_text(encoding="utf-8"))
                tax["families"] = tax_data.get("families")
                tax["genera"] = tax_data.get("genera")
        else:
            geo_entries = elev_entries = 0
            tax = {"error": f"missing {ant_key}"}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    return {
        "top1_without_geo": top1_no_geo,
        "top1_with_species_geo_prior": top1_with_geo,
        "geo_reranks_when_species_prior_strong": top1_no_geo != top1_with_geo and top1_with_geo == "Boana boans",
        "genus_family_present_in_candidates": genus_family_present,
        "without_geo_ranking_equals_visual": ranking_equals_visual,
        "geographic_adapter_no_location": {"scores": empty, "meta": meta_empty},
        "geographic_adapter_medellin": {
            "available": meta_ok.get("available"),
            "zone_id": meta_ok.get("zone_id"),
            "scores": scored,
            "meta": meta_ok,
        },
        "geographic_adapter_outside_coverage": {"scores": outside, "meta": meta_out},
        "package_context_readable": {
            "geography_entries": geo_entries,
            "elevation_entries": elev_entries,
            "catalog_state_keys": sorted(tax.keys()) if isinstance(tax, dict) else [],
            "families_in_state": tax.get("families") if isinstance(tax, dict) else None,
            "genera_in_state": tax.get("genera") if isinstance(tax, dict) else None,
        },
    }


def logical_findings(code: dict, packages: dict, probe: dict) -> list[dict]:
    findings = []

    findings.append({
        "id": "CTX-SPECIES",
        "signal": "especie",
        "used_as_context": True,
        "role": "unidad de ranking visual, prior geográfico (especie×zona) y open-set centroids",
        "severity": "info",
    })
    findings.append({
        "id": "CTX-LOCATION",
        "signal": "ubicacion (lat/lon)",
        "used_as_context": True,
        "role": "GeographicAdapter → zona → prior especie; entra a ranking con w=0.3 SOLO si lat/lon presentes y dentro de cobertura Antioquia",
        "severity": "info",
        "evidence": {
            "has_params": code["has_latitude_longitude_params"],
            "medellin_available": probe["geographic_adapter_medellin"]["available"],
            "rerank_works": probe["geo_reranks_when_species_prior_strong"],
        },
    })
    findings.append({
        "id": "CTX-FAMILY",
        "signal": "familia",
        "used_as_context": False,
        "role": "metadata de salida + taxonomía de paquete; NO entra a ranking_score. Priors jerárquicos GEO4 existen como experimento, no cableados al runtime",
        "severity": "gap",
        "evidence": {
            "in_candidates": probe["genus_family_present_in_candidates"],
            "in_ranking_formula": code["ranking_formula_includes_genus_or_family"],
            "geo_adapter_species_only": code["geographic_adapter_uses_species_prior_only"],
        },
    })
    findings.append({
        "id": "CTX-GENUS",
        "signal": "genero",
        "used_as_context": False,
        "role": "metadata de salida + grupos de similitud visual (interpretación); NO entra a ranking_score",
        "severity": "gap",
        "evidence": {
            "in_candidates": probe["genus_family_present_in_candidates"],
            "in_ranking_formula": code["ranking_formula_includes_genus_or_family"],
        },
    })
    findings.append({
        "id": "CTX-ELEVATION",
        "signal": "altura/elevacion",
        "used_as_context": False,
        "role": "elevation.json en paquetes v1.1+ es legible vía PackageManager, pero identify_image no acepta altitude y no consulta active_elevation()",
        "severity": "logical_error" if (any(p["has_elevation_json"] for p in packages["packages"]) and not code["has_elevation_param"]) else "gap",
        "evidence": {
            "packages_with_elevation": sum(1 for p in packages["packages"] if p["has_elevation_json"]),
            "pipeline_has_elevation_param": code["has_elevation_param"],
            "pipeline_calls_active_elevation": code["pipeline_calls_active_elevation"],
            "elevation_entries_active_package": probe["package_context_readable"]["elevation_entries"],
        },
    })
    findings.append({
        "id": "CTX-PACKAGE-GEO-DISCONNECT",
        "signal": "geography.json de paquete",
        "used_as_context": False,
        "role": "paquetes declaran geography.json pero el score geográfico runtime usa prior_zone_taxon_v2_clean (Antioquia), NO geography.json del paquete",
        "severity": "logical_error",
        "evidence": {
            "packages_with_geography": sum(1 for p in packages["packages"] if p["has_geography_json"]),
            "pipeline_calls_active_geography": code["pipeline_calls_active_geography"],
            "geo_entries_active_package": probe["package_context_readable"]["geography_entries"],
        },
    })
    findings.append({
        "id": "CTX-CAUCA-GEO-COVERAGE",
        "signal": "ubicacion fuera de Antioquia",
        "used_as_context": False,
        "role": "GeographicAdapter solo tiene cell_zone_map de Antioquia; coordenadas fuera → LOCATION_OUTSIDE_GEO_COVERAGE y ranking queda solo visual",
        "severity": "limitation",
        "evidence": probe["geographic_adapter_outside_coverage"]["meta"],
    })

    # Consistency: without geo, ranking must equal visual
    if not probe["without_geo_ranking_equals_visual"]:
        findings.append({
            "id": "BUG-RANKING-WITHOUT-GEO",
            "signal": "ranking",
            "used_as_context": None,
            "role": "sin geo, ranking_score debería igualar visual_score",
            "severity": "bug",
        })

    # Residual open-set defect already observed in lifecycle tests
    findings.append({
        "id": "OPENSET-THRESHOLD-RESIDUAL",
        "signal": "open_set",
        "used_as_context": None,
        "role": "Al desactivar un paquete, ESPECIE_CONOCIDA puede persistir por un centroide ajeno bajo el threshold histórico permisivo (no fuga de catálogo)",
        "severity": "known_defect",
    })

    return findings


def main() -> None:
    code = audit_code_wiring()
    packages = audit_packages()
    probe = functional_probe()
    findings = logical_findings(code, packages, probe)

    # Run deterministic MerlinFlow fixture tests inline
    cases = json.loads((HERE / "MERLIN_FLOW_TEST_CASES.json").read_text(encoding="utf-8"))["cases"]
    flow = MerlinFlow()
    test_results = []
    failures = []
    for case in cases:
        data = case["input"]
        try:
            result = flow.identify(
                observation_id="test:" + case["id"],
                input_metadata={"fixture": case["id"]},
                is_anuran=data["is_anuran"],
                anuran_evidence={"source": "deterministic_fixture"},
                visual_candidates=[VisualCandidate(name, score) for name, score in data["visual_candidates"]],
                geographic_scores=data.get("geographic_scores"),
                geographic_context_available=data["geographic_context_available"],
                open_set_unknownness_score=data["open_set_unknownness_score"],
                segmentation_evidence=[{"feature": "dorsal_region", "state": "NO_EVALUABLE"}],
                model_version="fixture-adapter/v0.1",
            )
            expected = case["expect"]
            if "top1" in expected and result["candidates"][0]["scientific_name"] != expected["top1"]:
                raise AssertionError(f"top1 {result['candidates'][0]['scientific_name']} != {expected['top1']}")
            if "geo_used" in expected and result["geographic_context_used"] is not expected["geo_used"]:
                raise AssertionError("geo_used mismatch")
            if "genus" in expected:
                assert result["candidates"][0]["genus"] == expected["genus"]
                assert result["candidates"][0]["family"] == expected["family"]
            test_results.append({"id": case["id"], "status": "PASS"})
        except Exception as exc:  # noqa: BLE001
            failures.append({"id": case["id"], "error": str(exc)})
            test_results.append({"id": case["id"], "status": "FAIL", "error": str(exc)})

    summary = {
        "signals": {
            "familia": "NO usado en score (solo metadata)",
            "genero": "NO usado en score (solo metadata / similitud visual interpretativa)",
            "especie": "SI — unidad de visual + prior geo + open-set",
            "ubicacion": "SI condicional — lat/lon → zona Antioquia → prior especie w=0.3",
            "altura": "NO — datos en paquetes, no cableados al pipeline",
        },
        "fixture_tests": {"passed": sum(r["status"] == "PASS" for r in test_results), "failed": len(failures), "total": len(test_results)},
        "logical_error_count": sum(1 for f in findings if f["severity"] == "logical_error"),
        "gap_count": sum(1 for f in findings if f["severity"] == "gap"),
    }

    report = {
        "status": "COMPLETED",
        "date": "2026-09-14",
        "summary": summary,
        "code_wiring": code,
        "packages": packages,
        "functional_probe": probe,
        "findings": findings,
        "fixture_test_results": test_results,
    }
    out = HERE / "CONTEXT_USAGE_AUDIT_20260914.json"
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"output": str(out), "summary": summary, "findings": [
        {"id": f["id"], "signal": f["signal"], "used": f["used_as_context"], "severity": f["severity"]}
        for f in findings
    ]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
