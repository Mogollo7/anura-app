@echo off
chcp 65001 > nul
echo ==============================================================================
echo INICIANDO EXTRACCION DE iNaturalist - ANURA
echo ==============================================================================
echo Especies a procesar leidas desde: especies_input.txt
echo Carpeta destino: data dirty
echo.

".venv\Scripts\python.exe" scraper_inaturalist.py --input especies_input.txt --quality-grade research

pause
