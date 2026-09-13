# Fase 9 Rejection Audit

```json
{
  "status": "PASS",
  "generated_at": "2026-09-13T07:29:13.920162+00:00",
  "scope": "Fase 9 rejection; read-only source audit",
  "official_sets": {
    "F3_KNOWN": 766,
    "F4_UNKNOWN": 56,
    "total": 822
  },
  "embedding": {
    "path": "D:\\Anura\\evaluation\\open_set_v1\\knn\\knn_embeddings.npz",
    "shape": [
      822,
      512
    ],
    "dtype": "float64",
    "l2_min": 0.999999907981435,
    "l2_max": 1.000000121564911,
    "sha256": "b5b166f924339011234b70fa0a15daa6421e833b01cae9d1a896b726c977f923",
    "provenance": "Fase 6 retrospective encoder output; 512-D L2"
  },
  "source_records_sha256": "908c9bf2bf60d232067da54d66996b60eca391c72a8364e260f35537eefd419a",
  "leakage": "F3/F4 direct path, obs_id and SHA-256 leakage reported zero in prior audit; no new images used",
  "calibration": "ABSENT_INDEPENDENT_CALIBRATION; TRAIN/index are scale references only; no threshold fitted",
  "forbidden_signals": [
    "GPS/prior",
    "sound",
    "segmentation",
    "masks",
    "synthetic metadata",
    "new images",
    "original embeddings modification"
  ],
  "mahalanobis": {
    "status": "NUMERICALLY_STABLE_IN_SAMPLE",
    "covariance_condition_number": 5541.4106193611005,
    "validation_warning": "Covariance was fitted on F3 KNOWN and evaluated on those same KNOWN embeddings; performance is optimistic and not independent."
  },
  "available_logits_energy": false,
  "inputs": {
    "package": "D:\\Anura\\bioclip\\paquetes_regionales\\antioquia_v1.sqlite",
    "f5": "D:\\Anura\\evaluation\\open_set_v1\\metrics\\open_set_discrimination_metrics.json",
    "f6": "D:\\Anura\\evaluation\\open_set_v1\\knn\\knn_discrimination_metrics.json",
    "f8b": "D:\\Anura\\evaluation\\open_set_v1\\ensemble\\ensemble_metrics.json",
    "calibration_audit": "D:\\Anura\\evaluation\\open_set_v1\\ensemble\\calibration_audit.md"
  }
}
```

Thresholds are EVALUATION ONLY; no independent calibration source exists.
