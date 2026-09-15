"""Representative real-runtime E2E suite; inference receives no species labels."""
import json
from pathlib import Path

from merlin_runtime_pipeline import MerlinRuntimePipeline

ROOT = Path(__file__).resolve().parents[2]
KNOWN_IMAGE = ROOT / "data cleaned/Boana_boans/col_obs_330607060_photo_599545088.jpg"
UNKNOWN_IMAGE = ROOT / "data/unknown_open_set_v2/images/final/Boana_geographica/col_obs_107550537_photo_180907238.jpg"


def main() -> None:
    pipeline = MerlinRuntimePipeline()
    cases = [
        # ZONE_005 has higher frozen Boana boans prior than ZONE_001; this is
        # evaluated after inference and never supplied to the pipeline as truth.
        ("A_known_geo_compatible", KNOWN_IMAGE, 5.50, -75.00),
        ("B_known_geo_incompatible", KNOWN_IMAGE, 5.50, -76.00),
        ("C_unknown_image", UNKNOWN_IMAGE, None, None),
        ("D_multiple_real_candidates", KNOWN_IMAGE, None, None),
        ("E_no_location", KNOWN_IMAGE, None, None),
        ("F_top1_not_automatic", UNKNOWN_IMAGE, 6.25, -75.50),
    ]
    results = []
    for case_id, image, lat, lon in cases:
        assert image.exists(), image
        result = pipeline.identify_image(
            image, "runtime-suite:" + case_id, is_anuran=True,
            anuran_evidence={"source": "test_harness_manual_anuran_gate", "ground_truth_used": False},
            latitude=lat, longitude=lon, top_k=3,
        )
        assert len(result["candidates"]) == 3
        assert result["open_set_evidence"]["status"] == "RELEASE_THRESHOLD"
        assert "ground_truth_species" not in json.dumps(result)
        if case_id in {"C_unknown_image", "E_no_location"}:
            assert result["geographic_context_available"] is False
        if case_id in {"A_known_geo_compatible", "B_known_geo_incompatible", "F_top1_not_automatic"}:
            assert result["geographic_context_available"] is True
        # Rejection can only lead to NO_CONCLUYENTE, never automatic NO_REGISTRADA.
        if result["open_set_evidence"]["score"] > result["open_set_evidence"]["threshold"]:
            assert result["decision"] == "NO_CONCLUYENTE"
        results.append({
            "case": case_id, "decision": result["decision"], "top1": result["candidates"][0]["scientific_name"],
            "geo_available": result["geographic_context_available"],
            "open_set_score": result["open_set_evidence"]["score"],
            "open_set_threshold": result["open_set_evidence"]["threshold"],
            "boana_boans_geographic_score": next((candidate["geographic_score"] for candidate in result["candidates"] if candidate["scientific_name"] == "Boana boans"), None),
        })
    compatible = next(row for row in results if row["case"] == "A_known_geo_compatible")
    incompatible = next(row for row in results if row["case"] == "B_known_geo_incompatible")
    assert compatible["boana_boans_geographic_score"] > incompatible["boana_boans_geographic_score"]
    report = {"status": "PASS", "test_count": len(results), "results": results}
    out = Path(__file__).parent / "runtime_e2e_suite_result.json"
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
