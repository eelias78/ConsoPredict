""" IMPORT DES LIBRAIRIES """

from fastapi import FastAPI, Query, Depends, Response, HTTPException, status
from pydantic import BaseModel
from enum import Enum
import uvicorn

# Les schemas de classe
from schemas import AuthDetails, Profil

# Pour l'authentification utilisateur : Token
from authentication import AuthHandler

# Pour l'authentification admin : Basic
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from starlette.status import HTTP_401_UNAUTHORIZED

# Pour les calculs
import numpy as np
import pandas as pd

import os
import json
from os.path import dirname, abspath

# Pour la création & visualisation de la database utilisateurs 
import models
import sqlite3
from database import engine, SessionLocal
from sqlalchemy.orm import Session






""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

tags_metadata = [{"name": "💡🌡️📈 | Prévisions de la consommation électrique en fonction des prévisions\
                météorologiques à horizon 14 jours"
        }]

app = FastAPI(title ='ConsoPredict | Bretagne',

description = """
API développée par Label éCO2

## Fonction habilitation :
* Créer un **Identifiant** utilisateur
* Générer un mot de passe chiffré **Token**

## Fonction modèle de prévision :
* Saisir une localité et une période de prédiction
* Générer un fichier csv contenant la consommation électrique en MW

"""
, openapi_tags=tags_metadata)

""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""



"""""""""""""""""""""""""""
    BLOC : LE ENDPOINT
"""""""""""""""""""""""""""

@app.get('/', tags=['Endpoint'])
async def test_fonctionnement_api():
    return{"Bonjour et bienvenue sur cette API"}

    
"""""""""""""""""""""""""""
       BLOC : DATABASE
"""""""""""""""""""""""""""

models.Base.metadata.create_all(bind=engine)

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

""""""""""""""""""""""""""""""""""""""""
        BLOC : CREATION USER 
"""""""""""""""""""""""""""""""""""""""""

@app.post('/1ère étape : renseignez votre profil', tags=['Informations'])
def __(request: Profil, db: Session = Depends(get_db)):
    user_model = models.Users_db()
    user_model.Nom = request.Nom
    user_model.Prenom = request.Prenom  
    user_model.Email = request.Email
    user_model.Alias = request.Alias
    
    db.add(user_model)
    db.commit()

    return request


""""""""""""""""""""""""""""""""""""""""
    BLOC : AUTHENTIFICATION PAR TOKEN 
"""""""""""""""""""""""""""""""""""""""""

auth_handler = AuthHandler()
users = []

# Création de l'utilisateur : nom de user + mot de passe
@app.post('/2ème étape : enregistrez-vous', status_code=201, tags=['Authentification'])
async def __ (auth_details: AuthDetails):
    """
    Renseignez votre alias (identifiant) et créez un mot de passe:
    - **identifiant**: chaîne de caractère "xxxx"
    - **mot de passe**: chaîne de caractère "xxxx"
    - Le nom d'utilisateur et le mot de passe peuvent être identiques
    """

    if any(x['Identifiant'] == auth_details.Identifiant for x in users):
        raise HTTPException(status_code=400, detail='Le nom d\'utilisateur est déjà pris')
    hashed_password = auth_handler.get_password_hash(auth_details.MotDePasse)
    users.append({
        'Identifiant': auth_details.Identifiant,
        'MotDePasse': hashed_password    
    })
    return{'Identifiant': auth_details.Identifiant}

    
# Login pour récupérer le token
@app.post('/3ème étape : authentifiez-vous', tags=['Authentification'])
async def __ (auth_details: AuthDetails):
    """
    - Copiez la clé/token entre guillemets
    - Renseignez le token dans le volet "Prévisions Conso(MW)"
    """
    user = None
    for x in users:
        if x['Identifiant'] == auth_details.Identifiant:
            user = x
            break
    
    if (user is None) or (not auth_handler.verify_password(auth_details.MotDePasse, user['MotDePasse'])):
        raise HTTPException(status_code=401, detail='Identifiant et/ou password incorrect')
    token = auth_handler.encode_token(user['Identifiant'])
    return { 'token': token }


""""""""""""""""""""""""""""""""""""""""
    BLOC : SAISIE DE LA LOCALISATION 
"""""""""""""""""""""""""""""""""""""""""

# Chargement de la BDD
def select_data(Localite, DateModele, Start, End):
    global df_all
    df_all = pd.read_json(dirname(dirname(abspath(__file__)))+"/data/model/model_bretagne_db.json")
    df = df_all.loc[(df_all['localite'] == Localite) & (df_all['date model'] == DateModele) & (df_all['id jour'] >= Start) & ( df_all['id jour'] <= End),:]
    return(df)
    

# Appel pour récupérer le df global    
select_data(None,None,None,None)

# Liste des régions possibles
liste_station = ['Bretagne']

# Liste des localités disponibles
liste_localite = list(np.unique(df_all['localite']))

# Liste des modèles
liste_modele = list(np.unique(df_all['date model']))

# Paramètres pour le menu déroulant
class parametres:
    def __init__(self, Region: str = 
                Query(None, enum=liste_station), Localite: str= Query(None, enum=liste_localite),
                DateModele: str= Query(None, enum=liste_modele),
                Start: int=
                Query(None, description="Jour à partir duquel la prévision est demandée, inclus (0: aujourd'hui, 1: demain, etc.)",
                ge=0, le=13),
                End: int=
                Query(None, description="Jour jusqu'auquel la prévision est demandée, inclus (0: aujourd'hui, 1: demain, etc.)",
                ge=0, le=13)
                ):

            self.Region = Region
            self.Localite = Localite
            self.DateModele = DateModele
            self.Start = Start
            self.End = End


@app.get('/4ème étape : requête', tags=['Previsions Conso(MW)'])
async def __(params:parametres=Depends(),Identifiant: str = Depends(auth_handler.auth_wrapper)):
    Region = params.Region
    Localite = params.Localite
    DateModele = params.DateModele
    Start = params.Start
    End = params.End

    if Region is None:
        return{"Vous n'avez pas saisi la région"}
    if Localite is None:
        return{"Vous n'avez pas saisi la localite"}
    if DateModele is None :
        return{"Vous n'avez pas choisir la version du modèle"}
    elif Start is None :
        headers = {'Content-Disposition': f'attachment; filename=ConsoPredict.csv'}
        return Response(select_data(Localite,DateModele,1,End).to_csv(index=False, sep=';'),
        media_type="text/csv", headers=headers)
    else:
       headers = {'Content-Disposition': f'attachment; filename=ConsoPredict.csv'}
       return Response(select_data(Localite,DateModele,Start,End).to_csv(index=False, sep=';'),
        media_type="text/csv", headers=headers)


"""""""""""""""""""""""""""""""""""""""""
    BLOC : HISTORIQUE DES PROFILS CREES 
"""""""""""""""""""""""""""""""""""""""""

# Sécurisation du volet admin
security = HTTPBasic()

def get_admin(credentials: HTTPBasicCredentials  = Depends(security)):
  if credentials.username != 'admin' or credentials.password != '4dm1N':
     raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Incorrect id or password",
            headers={"WWW-Authenticate": "Basic"})
  return credentials.username


# Espace admin pour visualiser les connexions
@app.get("/admin", tags=['Admin'])
def __(db: Session = Depends(get_db), username:str = Depends(get_admin)):
    return db.query(models.Users_db).all()

if __name__ == "__main__":
    uvicorn.run(app, host = "127.0.0.1", port=8000)