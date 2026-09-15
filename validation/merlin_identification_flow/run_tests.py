"""Deterministic validation for the isolated Merlin flow."""
import json
from pathlib import Path

from merlin_flow import MerlinFlow, VisualCandidate

HERE = Path(__file__).parent


def main() -> None:
    cases = json.loads((HERE / "MERLIN_FLOW_TEST_CASES.json").read_text(encoding="utf-8"))["cases"]
    flow = MerlinFlow()
    results = []
    for case in cases:
        data = case["input"]
        result = flow.identify(
            observation_id="test:" + case["id"], input_metadata={"fixture": case["id"]},
            is_anuran=data["is_anuran"], anuran_evidence={"source": "deterministic_fixture"},
            visual_candidates=[VisualCandidate(name, score) for name, score in data["visual_candidates"]],
            geographic_scores=data.get("geographic_scores"),
            geographic_context_available=data["geographic_context_available"],
            open_set_unknownness_score=data["open_set_unknownness_score"],
            segmentation_evidence=[{"feature": "dorsal_region", "state": "NO_EVALUABLE"}],
            model_version="fixture-adapter/v0.1",
        )
        required = {"observation_id", "input_metadata", "is_anuran", "anuran_evidence", "candidates", "decision", "open_set_evidence", "explanation", "limitations", "model_version", "catalog_version", "geographic_context_used", "geographic_context_available", "experimental_flags"}
        assert required.issubset(result), case["id"]
        expected = case["expect"]
        assert result["decision"] == expected.get("decision", result["decision"]), case["id"]
        if "top1" in expected:
            assert result["candidates"][0]["scientific_name"] == expected["top1"], case["id"]
        if "candidate_count" in expected:
            assert len(result["candidates"]) == expected["candidate_count"], case["id"]
        if "geo_used" in expected:
            assert result["geographic_context_used"] is expected["geo_used"], case["id"]
        if "first_geographic_score" in expected:
            assert result["candidates"][0]["geographic_score"] is expected["first_geographic_score"], case["id"]
        if "must_have_limitation" in expected:
            assert expected["must_have_limitation"] in result["limitations"], case["id"]
        if "genus" in expected:
            assert result["candidates"][0]["genus"] == expected["genus"], case["id"]
            assert result["candidates"][0]["family"] == expected["family"], case["id"]
        if "experimental_flag" in expected:
            assert expected["experimental_flag"] in result["experimental_flags"], case["id"]
        # Result contract has no probability field; numeric outputs remain named scores.
        assert not any("probability" in key.lower() for candidate in result["candidates"] for key in candidate), case["id"]
        results.append({"id": case["id"], "status": "PASS", "decision": result["decision"], "top1": result["candidates"][0]["scientific_name"]})
    report = {"status": "PASS", "test_count": len(results), "results": results}
    (HERE / "test_execution_result.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
