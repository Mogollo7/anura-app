"""Real runtime smoke/E2E test using a local image; labels never enter inference."""
import json
from pathlib import Path

from merlin_runtime_pipeline import MerlinRuntimePipeline

ROOT = Path(__file__).resolve().parents[2]
IMAGE = ROOT / "data cleaned/Boana_boans/col_obs_330607060_photo_599545088.jpg"


def main() -> None:
    if not IMAGE.exists():
        raise FileNotFoundError(IMAGE)
    pipeline = MerlinRuntimePipeline()
    # The boolean is a test-harness initial-validation input, not a species label.
    result = pipeline.identify_image(
        IMAGE, "runtime-e2e-local-image", is_anuran=True,
        anuran_evidence={"source": "test_harness_manual_anuran_gate", "ground_truth_used": False},
        latitude=6.25, longitude=-75.5, top_k=3,
    )
    assert result["candidates"] and len(result["candidates"]) == 3
    assert result["input_metadata"]["runtime"]["bioclip"]["embedding_dim"] == 512
    assert result["geographic_context_available"] is True
    assert result["open_set_evidence"]["status"] == "RELEASE_THRESHOLD"
    assert result["decision"] in {"ESPECIE_CONOCIDA", "NO_CONCLUYENTE"}
    assert "ground_truth_species" not in json.dumps(result)
    out = Path(__file__).parent / "runtime_e2e_result.json"
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"status": "PASS", "decision": result["decision"], "top1": result["candidates"][0]["scientific_name"], "output": str(out)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
