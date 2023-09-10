#!/bin/bash

# Verif si Docker en cours d'exécution
if ! command -v docker &> /dev/null; then
    echo "Docker n'est pas installé ou n'est pas dans le chemin d'exécution."
    exit 1
fi

# Lancement docker-compose
docker-compose up
