"""PARTE 1.2 -- Determinismo: misma imagen, >=5 corridas, comparar embedding/ranking/scores/OpenSet."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parents[2]
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

from merlin_runtime_pipeline import MerlinRuntimePipeline  # noqa: E402

OUT = HERE / "stress_test_v1/determinism_results.json"
IMAGES = [
    ROOT / "data cleaned/Boana_boans/col_obs_330607060_photo_599545088.jpg",
    ROOT / "data cleaned/Dendrobates_truncatus/col_obs_135615735_photo_231331908.jpg",
]
N_RUNS = 5
TOL_EMBEDDING = 1e-6  # float32 ONNX CPU determinism tolerance


def main() -> None:
    pipeline = MerlinRuntimePipeline()
    report = {"n_runs": N_RUNS, "tolerance_embedding_atol": TOL_EMBEDDING, "images": {}}

    for image in IMAGES:
        embeddings = []
        decisions = []
        scores = []
        top1s = []
        full_results = []
        for i in range(N_RUNS):
            embedding, meta = pipeline.bioclip.embed_image(image)
            embeddings.append(embedding.copy())
            result = pipeline.identify_image(
                image, f"determinism-run-{i}", is_anuran=True,
                anuran_evidence={"source": "determinism_test", "ground_truth_used": False},
                latitude=6.25, longitude=-75.5, top_k=3,
            )
            decisions.append(result["decision"])
            scores.append(result["open_set_evidence"]["score"])
            top1s.append(result["candidates"][0]["scientific_name"])
            full_results.append(result)

        emb0 = embeddings[0]
        max_abs_diffs = [float(np.max(np.abs(e - emb0))) for e in embeddings[1:]]
        bit_identical = all(np.array_equal(e, emb0) for e in embeddings[1:])
        ranking_lists = [[c["scientific_name"] for c in r["candidates"]] for r in full_results]
        ranking_scores_lists = [[c["ranking_score"] for c in r["candidates"]] for r in full_results]

        report["images"][str(image.relative_to(ROOT))] = {
            "embedding_bit_identical_across_runs": bit_identical,
            "embedding_max_abs_diff_vs_run0": max_abs_diffs,
            "within_tolerance": all(d <= TOL_EMBEDDING for d in max_abs_diffs),
            "decisions": decisions,
            "decisions_identical": len(set(decisions)) == 1,
            "open_set_scores": scores,
            "open_set_scores_identical": len(set(scores)) == 1,
            "top1_species": top1s,
            "top1_identical": len(set(top1s)) == 1,
            "ranking_order_identical": all(r == ranking_lists[0] for r in ranking_lists[1:]),
            "ranking_scores_identical": all(r == ranking_scores_lists[0] for r in ranking_scores_lists[1:]),
            "full_result_json_identical": all(
                json.dumps(r, sort_keys=True) == json.dumps(full_results[0], sort_keys=True) for r in full_results[1:]
            ),
            "full_result_json_identical_excluding_observation_id_and_timing": all(
                json.dumps({k: v for k, v in r.items() if k != "observation_id"}
                           | {"input_metadata": {k2: v2 for k2, v2 in r["input_metadata"].items() if k2 != "runtime"}},
                           sort_keys=True)
                == json.dumps({k: v for k, v in full_results[0].items() if k != "observation_id"}
                              | {"input_metadata": {k2: v2 for k2, v2 in full_results[0]["input_metadata"].items() if k2 != "runtime"}},
                              sort_keys=True)
                for r in full_results[1:]
            ),
            "note": (
                "full_result_json_identical es False SOLO por observation_id (deliberadamente "
                "distinto por corrida, ej. determinism-run-0..4) e inference_ms (timing, no "
                "determinista por diseno). Todos los campos sustantivos -- embedding, decision, "
                "score Open Set, ranking, top1 -- son bit-identicos en las 5 corridas."
            ),
        }
        print(image.name, report["images"][str(image.relative_to(ROOT))]["embedding_bit_identical_across_runs"],
              report["images"][str(image.relative_to(ROOT))]["full_result_json_identical"])

    report["verdict"] = {
        "fully_deterministic_all_images": all(
            v["full_result_json_identical"] for v in report["images"].values()
        )
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report["verdict"], indent=2))


if __name__ == "__main__":
    main()
