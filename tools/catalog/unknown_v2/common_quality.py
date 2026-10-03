"""Shared quality-audit primitives for FASE 22 (used by historical and new-image audits)."""
from pathlib import Path
import numpy as np
from PIL import Image, ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = False

MIN_W, MIN_H = 200, 200
MIN_FILE_SIZE = 2 * 1024
BLUR_REJECT_THRESHOLD = 15.0
BRIGHT_LOW, BRIGHT_HIGH = 15, 240
CONTRAST_MIN = 8.0


def laplacian_variance(gray: np.ndarray) -> float:
    k = np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]], dtype=np.float32)
    gy, gx = gray.shape
    out = np.zeros((gy - 2, gx - 2), dtype=np.float32)
    for i in range(3):
        for j in range(3):
            if k[i, j] == 0:
                continue
            out += k[i, j] * gray[i:i + gy - 2, j:j + gx - 2]
    return float(out.var())


def edge_density(gray: np.ndarray) -> float:
    gx = np.abs(np.diff(gray, axis=1))
    gy = np.abs(np.diff(gray, axis=0))
    thresh = 20
    return float(((gx > thresh).mean() + (gy > thresh).mean()) / 2)


def audit_one(path: Path):
    row = {
        "image_path": str(path), "decision": "", "rejection_reason": "",
        "width": "", "height": "", "blur_score": "", "brightness_score": "",
        "contrast_score": "", "subject_visibility": "", "duplicate_group": "",
        "leakage_status": "PENDING", "taxonomic_status": "PENDING", "notes": "",
    }
    try:
        size = path.stat().st_size
        if size < MIN_FILE_SIZE:
            row.update(decision="REJECT_CORRUPTED", rejection_reason=f"file_size_{size}b_below_floor")
            return row
        with Image.open(path) as im:
            im.verify()
        with Image.open(path) as im:
            im = im.convert("RGB")
            w, h = im.size
            row["width"], row["height"] = w, h
            if w < MIN_W or h < MIN_H:
                row.update(decision="REJECT_RESOLUTION",
                           rejection_reason=f"{w}x{h}_below_min_{MIN_W}x{MIN_H}")
                return row
            arr = np.asarray(im.convert("L"), dtype=np.float32)
            if max(arr.shape) > 900:
                step = max(arr.shape) // 900 + 1
                arr = arr[::step, ::step]
            blur = laplacian_variance(arr)
            bright = float(arr.mean())
            contrast = float(arr.std())
            edens = edge_density(arr)
            row["blur_score"] = round(blur, 2)
            row["brightness_score"] = round(bright, 2)
            row["contrast_score"] = round(contrast, 2)

            reasons = []
            if blur < BLUR_REJECT_THRESHOLD:
                reasons.append(f"blur_var_{blur:.1f}_below_{BLUR_REJECT_THRESHOLD}")
            if bright < BRIGHT_LOW or bright > BRIGHT_HIGH:
                reasons.append(f"brightness_{bright:.1f}_out_of_range")
            if contrast < CONTRAST_MIN:
                reasons.append(f"contrast_{contrast:.1f}_below_{CONTRAST_MIN}")

            if reasons:
                row.update(decision="REJECT_QUALITY", rejection_reason=";".join(reasons))
                return row

            if edens < 0.02:
                row["subject_visibility"] = "LOW_CONFIDENCE_FLAT_IMAGE"
                row["notes"] = "low edge density - possible poor subject definition; not auto-rejected"
            else:
                row["subject_visibility"] = "OK"
            row["decision"] = "ACCEPT"
            return row
    except Exception as e:
        row.update(decision="REJECT_CORRUPTED", rejection_reason=f"decode_error:{e}")
        return row
