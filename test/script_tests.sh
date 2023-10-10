#!/bin/bash

# Test 1 : fonctionnement API
echo "Test 1 : doit renvoyer un message de bienvenue"
curl -X 'GET' \
  'http://localhost:8000/' \
  -H 'accept: application/json'

# Test 2 : création d'un user déjà pris
echo -e '\n\nTest 2 : doit renvoyer un message utilisateur déjà pris'
curl -X POST \
  'http://localhost:8000/1%C3%A8re%20%C3%A9tape%20%3A%20enregistrez-vous' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "Nom": "string",
  "Prenom": "string",
  "Email": "string",
  "Alias": "eelias78",
  "MotdePasse": "string"
}'

# Test 3 : création d'un user
echo -e '\n\nTest 3 : doit renvoyer le user créé et son mot de passe'
ma_date=$(date +'%Y%m%d%H%M')
curl -X POST \
  'http://localhost:8000/1%C3%A8re%20%C3%A9tape%20%3A%20enregistrez-vous' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "Nom": "nom",
  "Prenom": "prenom",
  "Email": "email",
  "Alias": "'"$ma_date"'",
  "MotdePasse": "pwd"
}'

# Test 4 : user inconnu
echo -e '\n\nTest 4 : doit renvoyer un message utilisateur inconnu'
curl -X POST \
  'http://localhost:8000/2%C3%A8me%20%C3%A9tape%20%3A%20authentifiez-vous' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "Alias": "string",
  "MotdePasse": "string"
}'

# Test 5 : mdp inconnu
echo -e '\n\nTest 5 : doit renvoyer un message que le mot de passe est incorrect'
curl -X POST \
  'http://localhost:8000/2%C3%A8me%20%C3%A9tape%20%3A%20authentifiez-vous' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "Alias": "eelias78",
  "MotdePasse": "string"
}'

# Test 6 : authentification ok
echo -e '\n\nTest 6 : doit renvoyer un token'
curl -X POST \
  'http://localhost:8000/2%C3%A8me%20%C3%A9tape%20%3A%20authentifiez-vous' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "Alias": "eelias78",
  "MotdePasse": "pwd"
}'

# Test 7 : autorisation ko
echo -e '\n\nTest 7 : doit renvoyer un message token invalide' 
curl -X GET \
  'http://localhost:8000/3%C3%A8me%20%C3%A9tape%20%3A%20requ%C3%AAte?Region=Bretagne&Localite=Guipavas&DateModele=2023-08-20&Start=0&End=1' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer xxx'

# Test 8 : authentification ok
echo -e '\n\nTest 8 : doit renvoyer un csv de prédictions' 
curl -X GET \
  'http://localhost:8000/3%C3%A8me%20%C3%A9tape%20%3A%20requ%C3%AAte?Region=Bretagne&Localite=Guipavas&DateModele=2023-08-20&Start=0&End=1' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2OTY5NzM2ODYsImlhdCI6MTY5Njk2NzY4Niwic3ViIjoiJDJiJDEyJEFOQ2sueEpFckNYYXpWQ3p6QzdFRE9hSktWM0UzYjVkSTlvUHpoNTI3b2FrYk9ZU0JpenBtIn0.lUU6euJbaZ7wmKeKIRiBMMwhYZK94fx512p3U-lQhqU'
