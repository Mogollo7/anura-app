import json
import numpy as np
from pathlib import Path

def canonical_species_name(name):
    if isinstance(name, str):
        return name.replace('_', ' ').strip()
    return str(name)

# Load embeddings
ref_data = np.load(Path(r"D:\Anura\evaluation\fase13\embeddings\reference_embeddings.npz"))
train_data = np.load(Path(r"D:\Anura\evaluation\fase13\embeddings\train_embeddings.npz"))

y_ref_raw = ref_data['species']
y_train_raw = train_data['species']

y_ref = np.array([canonical_species_name(sp) for sp in y_ref_raw])
y_train = np.array([canonical_species_name(sp) for sp in y_train_raw])

ref_species = set(y_ref)
train_species = set(y_train)

print(f"REFERENCE species ({len(ref_species)}):")
for sp in sorted(ref_species):
    print(f"  - {sp}")

print(f"\nTRAIN species ({len(train_species)}):")
for sp in sorted(train_species):
    print(f"  - {sp}")

print(f"\nSpecies in TRAIN but not in REFERENCE ({len(train_species - ref_species)}):")
for sp in sorted(train_species - ref_species):
    print(f"  - {sp}")

print(f"\nSpecies in REFERENCE but not in TRAIN ({len(ref_species - train_species)}):")
for sp in sorted(ref_species - train_species):
    print(f"  - {sp}")

print(f"\nOverlap (both REFERENCE and TRAIN): {len(ref_species & train_species)}")

total_centroids = len(ref_species) + len(train_species - ref_species)
print(f"\nTotal centroids would be: {total_centroids}")
print(f"Expected: 41")

# Check if there are species present in both
overlap = ref_species & train_species
print(f"\nSpecies in both REFERENCE and TRAIN (should use REFERENCE centroids):")
for sp in sorted(overlap):
    print(f"  - {sp}")
