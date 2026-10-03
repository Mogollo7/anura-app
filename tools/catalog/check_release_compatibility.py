"""
check_release_compatibility.py — Valida que catalog_release + covariance_release +
threshold_release sean COMPATIBLES entre si antes de usarlos juntos (ej. en un
regional_package o en una evaluacion Open Set).

Falla explicitamente (exit code != 0) ante cualquier incompatibilidad. Nunca combina
artefactos incompatibles silenciosamente.

Verificaciones:
    catalog_release   == covariance_release.catalog_release
    catalog_release   == threshold_release.catalog_release
    covariance_release== threshold_release.covariance_release
    encoder_sha256 (catalog) == encoder_sha256 (covariance) == encoder_sha256 (threshold)

Uso:
    python check_release_compatibility.py \
        --catalog-release-manifest visual_catalog/v1.0.0/manifest.json \
        --covariance-release-manifest covariance/v1.0.0/manifest.json \
        --threshold-release-manifest threshold/v1.0.0/manifest.json
"""
import argparse
import json
import sys
from pathlib import Path


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--catalog-release-manifest", required=True)
    ap.add_argument("--covariance-release-manifest", required=True)
    ap.add_argument("--threshold-release-manifest", required=True)
    args = ap.parse_args()

    catalog = load(args.catalog_release_manifest)
    covariance = load(args.covariance_release_manifest)
    threshold = load(args.threshold_release_manifest)

    checks = []

    checks.append((
        "catalog_release == covariance.catalog_release",
        catalog["catalog_release"], covariance["catalog_release"]
    ))
    checks.append((
        "catalog_release == threshold.catalog_release",
        catalog["catalog_release"], threshold["catalog_release"]
    ))
    checks.append((
        "covariance_release == threshold.covariance_release",
        covariance["covariance_release"], threshold["covariance_release"]
    ))
    checks.append((
        "encoder_sha256 (catalog) == encoder_sha256 (covariance)",
        catalog.get("encoder_sha256"), covariance["encoder_contract"]["encoder_sha256"]
    ))
    checks.append((
        "encoder_sha256 (catalog) == encoder_sha256 (threshold)",
        catalog.get("encoder_sha256"), threshold["encoder_contract"]["encoder_sha256"]
    ))

    print(f"=== COMPATIBILIDAD: {catalog['catalog_release']} + {covariance['covariance_release']} + {threshold['threshold_release']} ===\n")

    all_pass = True
    for name, left, right in checks:
        ok = left == right
        all_pass = all_pass and ok
        status = "PASS" if ok else "FAIL"
        print(f"  [{status}] {name}")
        if not ok:
            print(f"         izquierda={left!r}  derecha={right!r}")

    print()
    if all_pass:
        print("RESULTADO: COMPATIBLE")
        sys.exit(0)
    else:
        print("RESULTADO: INCOMPATIBLE — estos releases NO deben combinarse")
        sys.exit(1)


if __name__ == "__main__":
    main()
