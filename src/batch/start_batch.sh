#!/bin/bash
pwd
# Execution du script python qui va extraire les données météo
python3 /app/cron_meteo_concept/1-meteo_concept_xtract.py

# Attente 30 secondes
sleep 30

# Execution du script python qui va preprocesser les données météo
python3 /app/cron_meteo_concept/2-meteo_concept_preproc.py
