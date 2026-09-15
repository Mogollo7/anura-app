# Android adapter status

Implemented:

- Kotlin `IdentificationRequest`, `IdentificationResult` and decision/candidate types.
- Boundary validation including the rule that a rejected Open Set cannot silently become `NO_REGISTRADA`.
- Android ONNX Runtime adapter for `encoder_anura_fp16.onnx`, with immutable SHA-256 verification.
- RGB, resize-shortest-side, center-crop, CLIP normalization and NCHW Float32 conversion.
- A suspend adapter that connects the encoder to a future frozen-ranking `IdentificationEngine`.

Not yet production-validated:

- The Android image scaler must pass a pixel/tensor parity fixture against the exact desktop `open_clip` transform. Until then preprocessing is an implementation candidate, not a validated equivalent.
- Fase-13 centroid arrays, GEO-6 zone/prior release, taxonomy metadata and Mahalanobis precision/threshold are not packaged as mobile assets. Therefore this module does not emit a final offline `IdentificationResult` by itself.
- No Android SDK/Gradle wrapper was present in the source checkout, so compilation and device inference were not executed here.
