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

# Execution du script python qui va historiser les prédictions
python3 /app/cron_meteo_concept/4-meteo_concept_hist_model.py

# Attente 10 secondes
sleep 10

# Execution du script python qui va calculer la performance du modèle sur les 14 jours précédents
python3 /app/cron_meteo_concept/5-performance_model_J+14.py

# Attente 10 secondes
sleep 10

# Execution du script python qui va historiser les observations sur les 14 jours précédents
python3 /app/cron_meteo_concept/6-monitoring_hist_data_tps_reel.py

# Attente 10 secondes
sleep 10

# Execution du script python qui va calculer le data drift
python3 /app/cron_meteo_concept/7-monitoring_analyse_drift.py

# Attente 10 secondes
sleep 10

# Execution du script python qui va évaluer si on doit réentrainer le modèle
python3 /app/cron_meteo_concept/8-monitoring_retraining_model.py.py