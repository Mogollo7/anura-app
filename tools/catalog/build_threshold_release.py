"""
build_threshold_release.py — Formaliza el threshold congelado como artefacto VERSIONADO,
ligado explicitamente a un catalog_release y un covariance_release especificos.

IMPORTANTE: este script NO recalibra threshold_frozen. Lee frozen_rejection_config.json
(Fase 13, artefacto historico protegido, NO se modifica) y lo envuelve con procedencia
explicita hacia covariance_release y catalog_release, mas un SHA256 del contenido para
detectar alteracion futura.

Uso:
    python build_threshold_release.py \
        --frozen-config evaluation/fase13/selection/frozen_rejection_config.json \
        --catalog-release visual_catalog_1.0.0 \
        --covariance-release covariance_1.0.0 \
        --encoder-sha256 219e860e6fa9a80fb30a59fc8f61911421bbd53a4537dca831803d3ab446b2ad \
        --out-dir threshold/v1.0.0/
"""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--frozen-config", required=True)
    ap.add_argument("--catalog-release", required=True)
    ap.add_argument("--covariance-release", required=True)
    ap.add_argument("--encoder-sha256", required=True)
    ap.add_argument("--encoder-id", default="bioclip_anura_v1")
    ap.add_argument("--threshold-release-name", default=None,
                     help="Por defecto: threshold_<version de catalog_release>")
    ap.add_argument("--out-dir", required=True)
    args = ap.parse_args()

    with open(args.frozen_config, encoding="utf-8") as f:
        frozen = json.load(f)

    version_suffix = args.catalog_release.replace("visual_catalog_", "")
    release_name = args.threshold_release_name or f"threshold_{version_suffix}"

    manifest = {
        "threshold_release": release_name,
        "catalog_release": args.catalog_release,
        "covariance_release": args.covariance_release,
        "encoder_contract": {
            "encoder_id": args.encoder_id,
            "encoder_sha256": args.encoder_sha256,
        },
        "threshold": frozen["selected_threshold_tau_95KAR"],
        "metric": "Mahalanobis min-distance to nearest centroid",
        "calibration_method": frozen["selected_method"],
        "calibration_dataset": f"CALIBRATION ({frozen.get('calibration_known_count', '?')} imagenes)",
        "calibration_split": "CALIBRATION",
        "target_operating_point": f"KAR {int(frozen.get('target_KAR_principal', 0.95)*100)}%",
        "alternative_thresholds": frozen.get("threshold_table", {}),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_artifacts": [str(args.frozen_config)],
        "sha256": None,  # se calcula abajo sobre el resto del contenido
        "historical_note": (
            f"threshold={frozen['selected_threshold_tau_95KAR']} es EL MISMO valor congelado "
            f"originalmente en Fase 13 (timestamp original: {frozen.get('timestamp_utc')}). "
            "Este artefacto NO recalibra — solo formaliza procedencia y versión."
        )
    }

    # SHA256 del contenido CIENTIFICO unicamente (excluye sha256 y created_at, que es
    # metadata naturalmente variable entre ejecuciones y NO debe afectar el hash de
    # identidad del threshold_release — dos ejecuciones con los mismos datos de entrada
    # deben producir el MISMO sha256, sin importar cuando se ejecutaron).
    NON_DETERMINISTIC_FIELDS = {"sha256", "created_at"}
    content_for_hash = {k: v for k, v in manifest.items() if k not in NON_DETERMINISTIC_FIELDS}
    content_bytes = json.dumps(content_for_hash, sort_keys=True, ensure_ascii=False).encode("utf-8")
    manifest["sha256"] = hashlib.sha256(content_bytes).hexdigest()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "manifest.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"[OK] threshold_release: {release_name}")
    print(f"[OK] threshold={manifest['threshold']} (preservado, NO recalibrado)")
    print(f"[OK] catalog_release={args.catalog_release}, covariance_release={args.covariance_release}")
    print(f"[OK] sha256={manifest['sha256']}")
    print(f"[OK] Guardado en {out_path}")


if __name__ == "__main__":
    main()
