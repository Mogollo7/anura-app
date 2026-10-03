#!/bin/bash
# FASE 22.1 — Availability Assessment using iNaturalist API

API="https://api.inaturalist.org/v1"
PLACE_ID=6  # Colombia
OUTPUT_DIR="data/unknown_open_set_v2/candidates"
OUTPUT_CSV="$OUTPUT_DIR/species_candidate_availability.csv"

mkdir -p "$OUTPUT_DIR"

# Function to query species
query_species() {
    local genus="$1"
    local species="$2"
    local relation="$3"
    local full_name="${genus}_${species}"

    echo -n "Querying $full_name ($relation)... "

    # Get taxon ID
    taxon_response=$(curl -s "$API/taxa?q=${genus}+${species}&limit=1")
    taxon_id=$(echo "$taxon_response" | grep -o '"id":[0-9]*' | head -1 | cut -d: -f2)

    if [ -z "$taxon_id" ]; then
        echo "[NOT_FOUND]"
        return 1
    fi

    # Get observation count
    obs_response=$(curl -s "$API/observations?taxon_id=$taxon_id&place_id=$PLACE_ID&photos=true&quality_grade=research&per_page=1")
    total_obs=$(echo "$obs_response" | grep -o '"total_results":[0-9]*' | cut -d: -f2)

    if [ "$total_obs" -lt 1 ]; then
        echo "[NO_OBS]"
        return 1
    fi

    # Sample to estimate CC license
    sample=$(curl -s "$API/observations?taxon_id=$taxon_id&place_id=$PLACE_ID&photos=true&quality_grade=research&per_page=50")
    cc_count=$(echo "$sample" | grep -o '"license_code":"cc[^"]*"' | wc -l)
    total_photos=$(echo "$sample" | grep -o '"license_code":"[^"]*"' | wc -l)

    if [ "$total_photos" -gt 0 ]; then
        cc_fraction=$(echo "scale=2; $cc_count / $total_photos" | bc)
    else
        cc_fraction=0
    fi

    estimated_cc=$(echo "scale=0; $total_obs * $cc_fraction" | bc)
    estimated_usable=$(echo "scale=0; $estimated_cc * 0.82" | bc)

    status="PASS"
    if [ "$estimated_usable" -lt 85 ]; then
        status="FAIL"
    fi

    echo "[$status] obs=$total_obs usable=$estimated_usable"

    # Output CSV row
    echo "$full_name,$genus,$relation,$total_obs,$estimated_cc,$estimated_usable,$status"
}

# Write header
echo "species,genus,relation_to_known,available_observations,cc_license_images,estimated_usable_images,candidate_status" > "$OUTPUT_CSV"

# Query candidates
query_species "Boana" "albifrons" "SAME_GENUS" >> "$OUTPUT_CSV"
query_species "Boana" "aurantiaca" "SAME_GENUS" >> "$OUTPUT_CSV"
query_species "Boana" "faber" "SAME_GENUS" >> "$OUTPUT_CSV"
query_species "Boana" "thalassina" "SAME_GENUS" >> "$OUTPUT_CSV"
query_species "Boana" "picturata" "SAME_GENUS" >> "$OUTPUT_CSV"
query_species "Pristimantis" "achatinus" "SAME_GENUS" >> "$OUTPUT_CSV"
query_species "Pristimantis" "brevirostris" "SAME_GENUS" >> "$OUTPUT_CSV"
query_species "Pristimantis" "devillei" "SAME_GENUS" >> "$OUTPUT_CSV"
query_species "Pristimantis" "elegans" "SAME_GENUS" >> "$OUTPUT_CSV"
query_species "Pristimantis" "maculatus" "SAME_GENUS" >> "$OUTPUT_CSV"
query_species "Agalychnis" "callidryas" "SAME_FAMILY" >> "$OUTPUT_CSV"
query_species "Scinax" "fuscovarius" "SAME_FAMILY" >> "$OUTPUT_CSV"

echo "Output: $OUTPUT_CSV"
