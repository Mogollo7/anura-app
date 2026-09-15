"""PARTE 1.3 -- Entradas anomalas / adversariales.

Genera imagenes sinteticas con PIL (documentado abajo, metodo declarado) y las
pasa por MerlinRuntimePipeline.identify_image (el entry point real
image -> embedding -> ranking -> Open Set -> IdentificationResult).

Contrato actual (ver IDENTIFICATION_RESULT_SCHEMA.json / MOBILE_IDENTIFICATION_CONTRACT.md):
solo declara decision in {ESPECIE_CONOCIDA, NO_CONCLUYENTE}. NO existe un estado
formal ERROR_DE_ENTRADA. merlin_runtime_pipeline.identify_image NO envuelve
bioclip.embed_image en try/except -> cualquier excepcion de PIL/onnxruntime se
propaga como excepcion Python cruda, no como un resultado de contrato controlado.
Este test mide exactamente eso, sin inventar un estado nuevo en el JSON de
resultados.
"""
from __future__ import annotations

import json
import sys
import traceback
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parents[2]
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

from merlin_runtime_pipeline import MerlinRuntimePipeline  # noqa: E402

WORKDIR = HERE / "stress_test_v1/adversarial_images"
OUT = HERE / "stress_test_v1/adversarial_inputs_results.json"


def make_images() -> dict[str, Path]:
    WORKDIR.mkdir(parents=True, exist_ok=True)
    paths: dict[str, Path] = {}

    def save(name: str, img: Image.Image, fmt: str = "JPEG"):
        p = WORKDIR / name
        img.save(p, format=fmt)
        paths[name] = p

    rng = np.random.default_rng(42)

    # 1. Very small (below typical encoder input res)
    save("tiny_4x4.jpg", Image.fromarray((rng.integers(0, 255, (4, 4, 3))).astype(np.uint8)))
    # 2. Very large
    save("huge_6000x4000.jpg", Image.fromarray((rng.integers(0, 255, (4000, 6000, 3), dtype=np.uint8))))
    # 3. Extreme aspect ratio
    save("extreme_aspect_5000x40.jpg", Image.fromarray((rng.integers(0, 255, (40, 5000, 3), dtype=np.uint8))))
    save("extreme_aspect_40x5000.jpg", Image.fromarray((rng.integers(0, 255, (5000, 40, 3), dtype=np.uint8))))
    # 4. Very dark (underexposed)
    save("very_dark.jpg", Image.fromarray(np.full((400, 400, 3), 3, dtype=np.uint8)))
    # 5. Overexposed (near-white)
    save("overexposed.jpg", Image.fromarray(np.full((400, 400, 3), 252, dtype=np.uint8)))
    # 6. Blurry: draw a noisy pattern then gaussian-blur heavily
    from PIL import ImageFilter
    base = Image.fromarray((rng.integers(0, 255, (400, 400, 3))).astype(np.uint8))
    save("blurry.jpg", base.filter(ImageFilter.GaussianBlur(radius=25)))
    # 7. Subject occupies tiny corner of frame (simulated: small colored patch in a big blank frame)
    canvas = np.full((800, 800, 3), 40, dtype=np.uint8)
    canvas[20:70, 20:70] = rng.integers(80, 200, (50, 50, 3))
    save("partial_subject_tiny_corner.jpg", Image.fromarray(canvas))
    # 8. No subject at all (uniform textureless background)
    save("no_subject_flat_green.jpg", Image.fromarray(np.tile(np.array([40, 120, 40], dtype=np.uint8), (400, 400, 1))))
    # 9. Corrupted file: valid header, truncated/garbage body
    p = WORKDIR / "corrupted_truncated.jpg"
    good = WORKDIR / "very_dark.jpg"
    data = good.read_bytes()
    p.write_bytes(data[: len(data) // 3])  # truncate to 1/3
    paths["corrupted_truncated.jpg"] = p
    # 10. Corrupted: random bytes with .jpg extension (not an image at all)
    p2 = WORKDIR / "corrupted_random_bytes.jpg"
    p2.write_bytes(rng.integers(0, 255, 2048, dtype=np.uint8).tobytes())
    paths["corrupted_random_bytes.jpg"] = p2
    # 11. Unsupported format: .bmp saved with wrong extension .jpg (actually valid BMP bytes, invalid jpg)
    bmp_path = WORKDIR / "actually_bmp_renamed.jpg"
    Image.fromarray((rng.integers(0, 255, (100, 100, 3))).astype(np.uint8)).save(
        WORKDIR / "_tmp.bmp", format="BMP"
    )
    (WORKDIR / "_tmp.bmp").rename(bmp_path)
    paths["actually_bmp_renamed.jpg"] = bmp_path
    # 12. Genuinely unsupported format: TIFF
    save("unsupported_format.tiff", Image.fromarray((rng.integers(0, 255, (200, 200, 3))).astype(np.uint8)), fmt="TIFF")
    # 13. Empty file (0 bytes)
    p3 = WORKDIR / "empty_file.jpg"
    p3.write_bytes(b"")
    paths["empty_file.jpg"] = p3
    # 14. Grayscale / single channel
    save("grayscale_L.jpg", Image.fromarray(rng.integers(0, 255, (300, 300), dtype=np.uint8)).convert("L"))
    # 15. RGBA with alpha
    save("rgba_with_alpha.png", Image.fromarray(rng.integers(0, 255, (300, 300, 4), dtype=np.uint8), mode="RGBA"), fmt="PNG")

    return paths


def main() -> None:
    images = make_images()
    pipeline = MerlinRuntimePipeline()

    results = []
    for name, path in sorted(images.items()):
        entry = {"case": name, "path": str(path)}
        try:
            result = pipeline.identify_image(
                path, f"adversarial-{name}", is_anuran=True,
                anuran_evidence={"source": "adversarial_stress_test", "ground_truth_used": False},
                latitude=None, longitude=None, top_k=3,
            )
            entry["outcome"] = "CONTROLLED_RESULT"
            entry["decision"] = result["decision"]
            entry["candidates_top1"] = result["candidates"][0]["scientific_name"] if result["candidates"] else None
            entry["limitations"] = result["limitations"]
        except Exception as exc:  # noqa: BLE001 -- deliberately catching everything to characterize crash behavior
            entry["outcome"] = "UNCAUGHT_EXCEPTION"
            entry["exception_type"] = type(exc).__name__
            entry["exception_message"] = str(exc)[:300]
            entry["traceback_last_frame"] = traceback.format_exc().splitlines()[-2:]
        results.append(entry)
        print(name, "->", entry["outcome"], entry.get("decision") or entry.get("exception_type"))

    crashes = [r for r in results if r["outcome"] == "UNCAUGHT_EXCEPTION"]
    controlled = [r for r in results if r["outcome"] == "CONTROLLED_RESULT"]

    report = {
        "method": (
            "Imagenes sinteticas generadas con PIL/numpy (semilla=42): tamano extremo (4x4, "
            "6000x4000), aspect ratio extremo (5000x40 y 40x5000), subexpuesta, sobreexpuesta, "
            "borrosa (GaussianBlur r=25), sujeto minusculo en esquina, sin sujeto (fondo plano), "
            "archivo truncado (1/3 de bytes validos), archivo de bytes aleatorios con extension "
            ".jpg, BMP valido renombrado a .jpg, TIFF real (formato no probado por el pipeline), "
            "archivo vacio (0 bytes), escala de grises, RGBA con canal alfa."
        ),
        "contract_gap": {
            "ERROR_DE_ENTRADA_exists_in_schema": False,
            "evidence": (
                "IDENTIFICATION_RESULT_SCHEMA.json solo permite decision in "
                "{ESPECIE_CONOCIDA, NO_CONCLUYENTE} (ver merlin_flow.py linea ~79-81, que "
                "levanta ValueError si open_set_decision no es uno de esos dos). "
                "merlin_runtime_pipeline.identify_image NO envuelve bioclip.embed_image en "
                "try/except: una imagen corrupta o formato no soportado no produce "
                "NO_CONCLUYENTE, produce una excepcion Python cruda que el llamador debe manejar."
            ),
            "proposed_placement_not_implemented": (
                "Anadir ERROR_DE_ENTRADA como TERCER valor de decision (junto a "
                "ESPECIE_CONOCIDA/NO_CONCLUYENTE) es compatible hacia atras si el schema lo declara "
                "como valor adicional del enum y el campo sigue siendo string -- un cliente v0.2.0 "
                "que solo espera los dos valores existentes se rompe si no maneja el default; por "
                "eso NO se implementa aqui sin decision explicita del responsable del contrato "
                "(mismo principio que el threshold: cambios de contrato no se hacen unilateralmente "
                "en una fase de stress test). La ubicacion natural es en "
                "merlin_runtime_pipeline.identify_image, envolviendo bioclip.embed_image en un "
                "try/except que capture errores de decodificacion/lectura de imagen (PIL "
                "UnidentifiedImageError, OSError) y retorne un IdentificationResult con "
                "decision=ERROR_DE_ENTRADA y candidates=[] en vez de propagar la excepcion."
            ),
        },
        "summary": {
            "total_cases": len(results),
            "controlled_result": len(controlled),
            "uncaught_exception": len(crashes),
        },
        "crash_cases": crashes,
        "all_results": results,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report["summary"], indent=2))


if __name__ == "__main__":
    main()
