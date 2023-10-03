from fastapi.testclient import TestClient
import json

from .api import app
import schemas
import authentication

client = TestClient(app)

def test_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Bonjour et bienvenue sur l'API ConsoPredict"}

def test_connection():
    API_URL = "/2ème étape : authentifiez-vous"
    data = {
        "Alias": "eelias78",
        "MotdePasse": "pwd"
    }
    # Envoi de la requête POST
    response = client.post(API_URL, json=data)
    # Vérification du code de statut de la réponse
    assert response.status_code == 200
    # Vérification que la réponse contient le mot token
    response_data = response.json()
    assert "token" in response_data
