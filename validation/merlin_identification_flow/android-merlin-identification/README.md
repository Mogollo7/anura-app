# Merlin Identification Android

Android/Kotlin adapter for the frozen BioCLIP FP16 encoder and the stable Merlin identification contract.

This module deliberately does not claim to implement visual ranking, GEO or Mahalanobis acceptance until their frozen runtime releases are exported into the application assets.

## Frozen encoder

Place `encoder_anura_fp16.onnx` in `src/main/assets/models/`. Its SHA-256 must be:

`219e860e6fa9a80fb30a59fc8f61911421bbd53a4537dca831803d3ab446b2ad`

The adapter verifies it before creating an ONNX Runtime session. The model input is Float32 NCHW `[1, 3, 224, 224]`; output is expected to be a 512-dimensional L2-normalized embedding.

## Preprocessing parity

`BioClipPreprocessor` implements the documented OpenCLIP/BioCLIP validation transform: RGB, resize shortest side to 224 using bicubic interpolation, center crop 224×224, scale to `[0,1]`, normalize with CLIP mean `[0.48145466, 0.4578275, 0.40821073]` and std `[0.26862954, 0.26130258, 0.27577711]`, then CHW Float32.

Before a production release, run an image parity fixture against the validated desktop transform. This scaffold intentionally fails closed if the output is not finite or L2 normalized.

## Usage

```kotlin
val encoder = BioClipOnnxEncoder(context)
val embedding = encoder.embed(contentResolver, request.imageUri)
// Pass embedding to an implementation of IdentificationEngine that owns the frozen ranking releases.
```

`IdentificationRequest` and `IdentificationResult` preserve the semantic contract described in the parent flow. Scores are never probabilities, and `NO_CONCLUYENTE` remains distinct from `NO_REGISTRADA`.
