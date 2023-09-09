#!/bin/bash

# Execution du script python qui va extraire les données météo
python3 /app/cron_meteo_concept/1-meteo_concept_xtract.py

# Attente 10 secondes
sleep 10

# Execution du script python qui va preprocesser les données météo
python3 /app/cron_meteo_concept/2-meteo_concept_preproc.py

# Attente 10 secondes
#sleep 10

# Execution du script python qui va prédire la consommation
python3 /app/cron_meteo_concept/3-meteo_concept_model.py

# Attente 10 secondes
sleep 10

# Execution du script python qui va agréger les prédictions
python3 /app/cron_meteo_concept/4-meteo_concept_hist_model.py