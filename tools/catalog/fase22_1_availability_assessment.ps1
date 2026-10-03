# FASE 22.1 — Availability Assessment Phase (PowerShell)
# Pre-evaluates candidate species using iNaturalist API

$InaturalistAPI = "https://api.inaturalist.org/v1"
$ColombiaPlaceID = 6
$OutputDir = "D:\Anura\data\unknown_open_set_v2\candidates"
$OutputCSV = "$OutputDir\species_candidate_availability.csv"

if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
}

$Candidates = @(
    @{name = "Boana_albifrons"; relation = "SAME_GENUS"},
    @{name = "Boana_aurantiaca"; relation = "SAME_GENUS"},
    @{name = "Boana_faber"; relation = "SAME_GENUS"},
    @{name = "Boana_thalassina"; relation = "SAME_GENUS"},
    @{name = "Pristimantis_achatinus"; relation = "SAME_GENUS"},
    @{name = "Pristimantis_brevirostris"; relation = "SAME_GENUS"},
    @{name = "Pristimantis_caryophyllaceus"; relation = "SAME_GENUS"},
    @{name = "Pristimantis_devillei"; relation = "SAME_GENUS"},
    @{name = "Pristimantis_elegans"; relation = "SAME_GENUS"},
    @{name = "Pristimantis_maculatus"; relation = "SAME_GENUS"},
    @{name = "Agalychnis_callidryas"; relation = "SAME_FAMILY"},
    @{name = "Scinax_fuscovarius"; relation = "SAME_FAMILY"},
    @{name = "Trachycephalus_venulosus"; relation = "SAME_FAMILY"}
)

Write-Host "FASE 22.1 — AVAILABILITY ASSESSMENT"
Write-Host "========================================================================"

$CandidatesData = @()

foreach ($i = 0; $i -lt $Candidates.Count; $i++) {
    $cand = $Candidates[$i]
    $speciesName = $cand.name
    $relation = $cand.relation
    $parts = $speciesName -split "_"
    $genus = $parts[0]
    $sp = $parts[1]

    Write-Host ("[" + ($i+1).ToString("00") + "/" + $Candidates.Count.ToString("00") + "] $speciesName") -NoNewline

    try {
        # Build URL with ampersand properly
        $taxonUrl = $InaturalistAPI + "/taxa?q=" + $genus + "+" + $sp + "&limit=1"
        $taxonResp = Invoke-WebRequest -Uri $taxonUrl -UseBasicParsing -TimeoutSec 10 | ConvertFrom-Json

        if ($taxonResp.results.Count -eq 0) {
            Write-Host " [NOT_FOUND]"
            $CandidatesData += [PSCustomObject]@{
                species = $speciesName
                genus = $genus
                relation_to_known = $relation
                available_observations = 0
                estimated_usable_images = 0
                candidate_status = "FAIL"
                rejection_reason = "not_found"
            }
            Start-Sleep -Milliseconds 300
            continue
        }

        $taxonId = $taxonResp.results[0].id

        # Query observations
        $obsUrl = $InaturalistAPI + "/observations?taxon_id=" + $taxonId + "&place_id=" + $ColombiaPlaceID + "&photos=true&quality_grade=research&per_page=1"
        $obsResp = Invoke-WebRequest -Uri $obsUrl -UseBasicParsing -TimeoutSec 10 | ConvertFrom-Json

        $totalCount = $obsResp.total_results

        if ($totalCount -eq 0) {
            Write-Host " [NO_OBS]"
            $CandidatesData += [PSCustomObject]@{
                species = $speciesName
                genus = $genus
                relation_to_known = $relation
                available_observations = 0
                estimated_usable_images = 0
                candidate_status = "FAIL"
                rejection_reason = "no_obs"
            }
            Start-Sleep -Milliseconds 300
            continue
        }

        # Sample to estimate CC license
        $sampleUrl = $InaturalistAPI + "/observations?taxon_id=" + $taxonId + "&place_id=" + $ColombiaPlaceID + "&photos=true&quality_grade=research&per_page=50"
        $sampleResp = Invoke-WebRequest -Uri $sampleUrl -UseBasicParsing -TimeoutSec 10 | ConvertFrom-Json

        $ccPhotos = 0
        $totalPhotos = 0
        foreach ($obs in $sampleResp.results) {
            foreach ($photo in $obs.photos) {
                $totalPhotos++
                if ($photo.license_code -like "cc*") {
                    $ccPhotos++
                }
            }
        }

        $ccFraction = if ($totalPhotos -gt 0) { $ccPhotos / $totalPhotos } else { 0 }
        $estimatedCCPhotos = [int]($totalCount * $ccFraction)
        $estimatedUsable = [int]($estimatedCCPhotos * 0.82)

        $status = "PASS"
        $reject = ""
        if ($estimatedUsable -lt 85) {
            $status = "FAIL"
            $reject = "low_availability"
        }

        Write-Host " [$status] obs=$totalCount usable=$estimatedUsable"

        $CandidatesData += [PSCustomObject]@{
            species = $speciesName
            genus = $genus
            relation_to_known = $relation
            available_observations = $totalCount
            estimated_usable_images = $estimatedUsable
            candidate_status = $status
            rejection_reason = $reject
        }

        Start-Sleep -Milliseconds 300

    } catch {
        Write-Host " [ERROR]"
        $CandidatesData += [PSCustomObject]@{
            species = $speciesName
            genus = $genus
            relation_to_known = $relation
            available_observations = 0
            estimated_usable_images = 0
            candidate_status = "ERROR"
            rejection_reason = "api_error"
        }
        Start-Sleep -Milliseconds 300
    }
}

# Write CSV
$CandidatesData | Export-Csv -Path $OutputCSV -NoTypeInformation -Encoding UTF8 -Force

$passed = @($CandidatesData | Where-Object { $_.candidate_status -eq "PASS" }).Count

Write-Host ""
Write-Host "========================================================================"
Write-Host "Total evaluated: $($CandidatesData.Count) | PASS: $passed | FAIL: $($CandidatesData.Count - $passed)"
Write-Host "Output: $OutputCSV"
