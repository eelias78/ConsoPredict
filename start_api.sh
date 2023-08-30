#!/bin/bash

# Verif si Docker en cours d'exécution
if ! command -v docker &> /dev/null; then
    echo "Docker n'est pas installé ou n'est pas dans le chemin d'exécution."
    exit 1
fi

# Creation image_api
cd src/api
docker image build . --no-cache=true -t img_api:latest

# Lancer docker-compose
docker-compose up
