"""
validate_embedding_contract.py — Verifica que un .npz de embeddings sea compatible con el
contrato de encoder declarado (ver EMBEDDING_CONTRACT.md).

Este script es de SOLO LECTURA sobre el .npz objetivo. No modifica nada.

Uso:
    python validate_embedding_contract.py --npz path/al/embeddings.npz --dim 512 \
        --encoder-sha256 219e860e6fa9a80fb30a59fc8f61911421bbd53a4537dca831803d3ab446b2ad \
        --encoder-path path/al/encoder.onnx

Si --encoder-path se provee, calcula el SHA256 real del archivo y lo compara contra
--encoder-sha256, en vez de confiar ciegamente en el valor declarado.
"""
import argparse
import hashlib
import sys
import numpy as np
from pathlib import Path


def sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--npz", required=True, help="Ruta al .npz de embeddings a verificar")
    ap.add_argument("--dim", type=int, default=512, help="Dimension esperada del embedding")
    ap.add_argument("--encoder-sha256", required=True, help="SHA256 esperado del encoder")
    ap.add_argument("--encoder-path", default=None,
                     help="Si se provee, se recalcula el SHA256 real del encoder para comparar")
    args = ap.parse_args()

    npz_path = Path(args.npz)
    if not npz_path.exists():
        print(f"[ERROR] No existe: {npz_path}")
        sys.exit(1)

    data = np.load(npz_path, allow_pickle=True)
    if "embeddings" not in data:
        print(f"[ERROR] El .npz no contiene la clave 'embeddings'")
        sys.exit(1)

    embeddings = data["embeddings"]
    actual_dim = embeddings.shape[1] if embeddings.ndim == 2 else None

    results = {"npz": str(npz_path), "checks": []}

    dim_ok = actual_dim == args.dim
    results["checks"].append({
        "check": "embedding_dimension",
        "expected": args.dim,
        "actual": actual_dim,
        "status": "PASS" if dim_ok else "FAIL"
    })

    if args.encoder_path:
        encoder_path = Path(args.encoder_path)
        if not encoder_path.exists():
            results["checks"].append({
                "check": "encoder_sha256",
                "status": "ERROR",
                "note": f"encoder no encontrado: {encoder_path}"
            })
        else:
            actual_sha = sha256_of_file(encoder_path)
            sha_ok = actual_sha == args.encoder_sha256
            results["checks"].append({
                "check": "encoder_sha256",
                "expected": args.encoder_sha256,
                "actual": actual_sha,
                "status": "PASS" if sha_ok else "FAIL"
            })
    else:
        results["checks"].append({
            "check": "encoder_sha256",
            "status": "SKIPPED",
            "note": "no se proveyo --encoder-path, no se pudo verificar contra archivo real"
        })

    overall = "PASS" if all(c["status"] in ("PASS", "SKIPPED") for c in results["checks"]) else "FAIL"
    results["overall"] = overall

    print(f"\n=== VALIDACION DE CONTRATO DE EMBEDDING ===")
    for c in results["checks"]:
        print(f"  [{c['status']}] {c['check']}: {c.get('actual', c.get('note', ''))}")
    print(f"\nResultado: {overall}")

    sys.exit(0 if overall == "PASS" else 1)


if __name__ == "__main__":
    main()
