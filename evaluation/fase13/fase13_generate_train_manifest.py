import json
from pathlib import Path
from collections import defaultdict

def canonical_species_name(name):
    """Normalize species name: underscore to space, strip."""
    if isinstance(name, str):
        return name.replace('_', ' ').strip()
    return str(name)

def generate_train_manifest():
    print("=== GENERANDO TRAIN_MANIFEST.JSON ===")

    training_manifest_path = Path(r"D:\Anura\training\manifiesto.json")
    ref_manifest_path = Path(r"D:\Anura\data calibration\REFERENCE_manifest.json")
    cal_manifest_path = Path(r"D:\Anura\data calibration\CALIBRATION_manifest.json")
    data_cleaned = Path(r"D:\Anura\data cleaned")

    output_dir = Path(r"D:\Anura\evaluation\fase13\manifests")
    output_dir.mkdir(parents=True, exist_ok=True)
    train_manifest_out = output_dir / "TRAIN_manifest.json"

    # Load training manifest
    with open(training_manifest_path, 'r', encoding='utf-8-sig') as f:
        training_data = json.load(f)

    train_records = training_data['particiones']['train']
    print(f"Loaded {len(train_records)} training samples")

    # Load REFERENCE and CALIBRATION to check for contamination
    with open(ref_manifest_path, 'r', encoding='utf-8-sig') as f:
        ref_records = json.load(f)
    ref_paths = {r.get('OriginalPath', r.get('FileName', '')) for r in ref_records}

    with open(cal_manifest_path, 'r', encoding='utf-8-sig') as f:
        cal_records = json.load(f)
    cal_paths = {r.get('OriginalPath', r.get('FileName', '')) for r in cal_records}

    print(f"REFERENCE has {len(ref_paths)} paths")
    print(f"CALIBRATION has {len(cal_paths)} paths")

    contaminated = []
    not_found = []
    train_manifest_clean = []

    for record in train_records:
        ruta = record.get('ruta', '')

        # Check if in REFERENCE or CALIBRATION
        if ruta in ref_paths or ruta in cal_paths:
            contaminated.append(ruta)
            continue

        # Check if image exists in data cleaned
        full_path = data_cleaned / ruta
        if not full_path.exists():
            not_found.append((ruta, str(full_path)))
            continue

        # Convert to manifest format compatible with embedding extraction
        # Normalize species name to use spaces (canonical)
        especie = record.get('especie', '')
        canonical_sp = canonical_species_name(especie)

        manifest_record = {
            'FileName': ruta,
            'OriginalPath': ruta,
            'Species': canonical_sp,
            'especie': canonical_sp,
            'ruta': ruta,
            'SHA256': record.get('sha256', ''),
            'grupo': record.get('grupo', ''),
            'obs_id': record.get('obs_id', '')
        }
        train_manifest_clean.append(manifest_record)

    print(f"Contamination check:")
    print(f"  Clean TRAIN samples (exist in data cleaned, not in REF/CAL): {len(train_manifest_clean)}")
    print(f"  Contaminated (in REFERENCE/CALIBRATION): {len(contaminated)}")
    print(f"  Not found in data cleaned: {len(not_found)}")

    if contaminated:
        print(f"  Contaminated paths (first 5):")
        for p in contaminated[:5]:
            print(f"    - {p}")

    if not_found:
        print(f"  Not found paths (first 5):")
        for p, fp in not_found[:5]:
            print(f"    - {p}")

    # Species breakdown
    species_counts = defaultdict(int)
    for record in train_manifest_clean:
        sp = record['Species']
        species_counts[sp] += 1

    print(f"\nSpecies breakdown ({len(species_counts)} species):")
    for sp in sorted(species_counts.keys()):
        print(f"  {sp}: {species_counts[sp]}")

    # Save manifest
    with open(train_manifest_out, 'w', encoding='utf-8') as f:
        json.dump(train_manifest_clean, f, indent=2, ensure_ascii=False)
    print(f"\nTRAIN manifest saved to: {train_manifest_out}")
    print(f"Total clean TRAIN samples (exist + not contaminated): {len(train_manifest_clean)}")

    return train_manifest_clean

if __name__ == "__main__":
    generate_train_manifest()
