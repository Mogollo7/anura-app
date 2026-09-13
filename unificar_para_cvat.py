from __future__ import annotations

import argparse
import hashlib
import re
from pathlib import Path

import rawpy
from PIL import Image, ImageOps

RAW_EXTS = {".cr2", ".cr3", ".nef", ".arw", ".dng"}
IMG_EXTS = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".webp"}
SUPPORTED_EXTS = RAW_EXTS | IMG_EXTS


def safe_name(value: str) -> str:
    """Make a relative path suitable for a flat CVAT image directory."""
    value = re.sub(r"[^A-Za-z0-9._-]+", "_", value)
    return value.strip("._") or "imagen"


def open_image(path: Path) -> Image.Image:
    if path.suffix.lower() in RAW_EXTS:
        with rawpy.imread(str(path)) as raw:
            rgb = raw.postprocess(use_camera_wb=True)
        return Image.fromarray(rgb).convert("RGB")

    with Image.open(path) as source:
        image = ImageOps.exif_transpose(source)
        if image.mode in ("RGBA", "LA") or "transparency" in image.info:
            rgba = image.convert("RGBA")
            background = Image.new("RGB", rgba.size, (255, 255, 255))
            background.paste(rgba, mask=rgba.getchannel("A"))
            return background
        return image.convert("RGB")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Unifica fotos y archivos RAW en JPG listos para CVAT."
    )
    parser.add_argument(
        "input_dir", type=Path, nargs="?", default=Path("."),
        help="Carpeta raíz que contiene las especies (por defecto: .)",
    )
    parser.add_argument(
        "output_dir", type=Path, nargs="?", default=Path("dataset_cvat_jpg"),
        help="Carpeta de salida (por defecto: dataset_cvat_jpg)",
    )
    parser.add_argument("--max-dim", type=int, default=2048)
    parser.add_argument("--quality", type=int, default=95)
    args = parser.parse_args()

    if not 1 <= args.quality <= 100:
        parser.error("--quality debe estar entre 1 y 100")
    if args.max_dim < 1:
        parser.error("--max-dim debe ser mayor que cero")

    input_dir = args.input_dir.resolve()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    image_paths = (
        path for path in input_dir.rglob("*")
        if path.is_file()
        and path.suffix.lower() in SUPPORTED_EXTS
        and output_dir not in path.parents
    )

    processed = 0
    failed = 0
    for path_in in sorted(image_paths):
        relative = path_in.relative_to(input_dir).with_suffix(".jpg")
        relative_text = str(relative).replace("\\", "__").replace("/", "__")
        unique_id = hashlib.sha1(str(path_in.relative_to(input_dir)).encode("utf-8")).hexdigest()[:8]
        output_name = f"{safe_name(relative_text)}__{unique_id}.jpg"
        path_out = output_dir / output_name

        try:
            image = open_image(path_in)
            image.thumbnail((args.max_dim, args.max_dim), Image.Resampling.LANCZOS)
            image.save(
                path_out,
                format="JPEG",
                quality=args.quality,
                optimize=True,
                progressive=True,
                subsampling=0,
            )
            processed += 1
            print(f"[{processed}] {path_in} -> {path_out.name}")
        except Exception as error:
            failed += 1
            print(f"ERROR {path_in}: {error}")

    print(f"\nFinalizado: {processed} imágenes convertidas en '{output_dir}'.")
    if failed:
        print(f"Archivos con error: {failed}")


if __name__ == "__main__":
    main()
