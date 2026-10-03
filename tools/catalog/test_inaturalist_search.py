#!/usr/bin/env python3
"""Test iNaturalist search for target species with different name formats."""

import requests
import json

# Try manual search on iNaturalist for one species
taxa_url = 'https://api.inaturalist.org/v1/taxa'
obs_url = 'https://api.inaturalist.org/v1/observations'

test_species = [
    'Hyloxalus picachos',
    'Dendropsophus minutus',
    'Pristimantis w-nigrum',
    'Pristimantis w nigrum',
    'Pristimantis wNigrum',
    'Pristimantis w.nigrum',
    'Sachatamia electrops',
]

print("=" * 80)
print("TESTING iNaturalist SPECIES SEARCH")
print("=" * 80)

for sp_name in test_species:
    response = requests.get(taxa_url, params={'q': sp_name, 'limit': 1}, timeout=10)
    results = response.json()['results']
    if results:
        taxon = results[0]
        taxon_id = taxon['id']
        taxon_name = taxon['name']
        print(f'\n{sp_name:30s} FOUND')
        print(f'  -> ID={taxon_id} name={taxon_name}')

        # Query observations in Colombia
        obs_response = requests.get(
            obs_url,
            params={
                'taxon_id': taxon_id,
                'place_id': 6,
                'photos': True,
                'per_page': 1,
            },
            timeout=10
        )
        total = obs_response.json()['total_results']
        print(f'  -> Observations in Colombia: {total}')
    else:
        print(f'\n{sp_name:30s} NOT FOUND')

print("\n" + "=" * 80)
print("DIRECT SEARCH IN COLOMBIA")
print("=" * 80)

# Try direct observation queries
search_terms = [
    'Hyloxalus picachos',
    'Dendropsophus minutus',
    'Pristimantis w nigrum',
    'Sachatamia electrops',
]

for search_term in search_terms:
    response = requests.get(
        obs_url,
        params={
            'q': search_term,
            'place_id': 6,
            'photos': True,
            'per_page': 1,
        },
        timeout=10
    )
    total = response.json()['total_results']
    print(f'{search_term:30s} -> {total:4d} observations')
