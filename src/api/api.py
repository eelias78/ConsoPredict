""" IMPORT DES LIBRAIRIES """

from fastapi import FastAPI, Query, Depends, Response, HTTPException, status
from pydantic import BaseModel
from enum import Enum
import uvicorn

# Les schemas de classe
from schemas import Profil, AuthDetails

# Pour l'authentification utilisateur : Token
from authentication import AuthHandler

# Pour l'authentification admin : Basic
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from starlette.status import HTTP_401_UNAUTHORIZED

# Pour les calculs
import numpy as np
import pandas as pd

# Pour la gestion des fichiers
import os
import json
from os.path import dirname, abspath

# Pour la création & visualisation de la database utilisateurs 
import models
import sqlite3
from database import engine, SessionLocal
from sqlalchemy.orm import Session

import mysql.connector

# Informations de connexion à la base de données
db_config = {
    "host": os.environ.get("DB_HOST", "db"),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASSWORD", "pwd"),
    "database": os.environ.get("DB_NAME", "dbconsopredict"),
    "port": int(os.environ.get("DB_PORT", 3306))
}


""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

tags_metadata = [{"name": "💡🌡️📈 | Prédictions de la consommation électrique en fonction des prévisions\
                météorologiques à horizon 14 jours"
        }]

app = FastAPI(title ='ConsoPredict | Bretagne',

description = """
API développée par Label éCO2

## Fonction habilitation :
* Créer un **Identifiant** utilisateur
* Générer un mot de passe chiffré **Token**

## Fonction modèle de prédiction :
* Saisir une localité et une période de prédiction
* Générer un fichier csv contenant la prédiction de consommation électrique (MW)

## Fonction admin :
* Enregistrement des utilisateurs dans une db users + affichage
* Enregistrement des token dans la db users

"""
, openapi_tags=tags_metadata)

""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""



"""""""""""""""""""""""""""
    BLOC : LE ENDPOINT
"""""""""""""""""""""""""""

@app.get('/', tags=['Endpoint'])
async def test_fonctionnement_api():
    return{"Bonjour et bienvenue sur l'API ConsoPredict"}

    
"""""""""""""""""""""""""""
  BLOC : LANCEMENT SQL A. 
"""""""""""""""""""""""""""

models.Base.metadata.create_all(bind=engine)

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

""""""""""""""""""""""""""""""""""""""""
        BLOC : CREATION UTILISATEUR 
"""""""""""""""""""""""""""""""""""""""""

auth_handler = AuthHandler()
users = []

# Création de l'utilisateur 
@app.post('/1ère étape : enregistrez-vous', status_code=201, tags=['Authentification'])
async def __ (request: Profil, db: Session = Depends(get_db)):
    """
    Renseignez vos informations personnelles
    """
    user_model = models.Users_db()
    user_model.Nom = request.Nom
    user_model.Prenom = request.Prenom  
    user_model.Email = request.Email
    user_model.Alias = request.Alias
    user_model.MotdePasse = request.MotdePasse
    
    # Vérification de l'existence de l'alias + hachage mot de passe
    if any(x['Alias'] == request.Alias for x in users):
        raise HTTPException(status_code=400, detail='Le nom d\'utilisateur est déjà pris')
    else:

        # Database utilisateur
        db.add(user_model)
        db.commit()

        hashed_password = auth_handler.get_password_hash(request.MotdePasse)
        users.append({
            'Alias': request.Alias,
            'MotdePasse': hashed_password    
        })
    
        return {"Alias ": request.Alias, "MotdePasse": request.MotdePasse}


""""""""""""""""""""""""""""""""""""""""
    BLOC : AUTHENTIFICATION PAR TOKEN 
"""""""""""""""""""""""""""""""""""""""""

# Login pour récupérer le token
@app.post('/2ème étape : authentifiez-vous', tags=['Authentification'])
async def __ (auth_details:AuthDetails, db: Session = Depends(get_db)):
    """
    - Renseignez vos identfiants créés à la 1ère étape (alias et mot de passe)
    - Copiez la clé/token entre guillemets
    - Collez le token dans le volet "Prédictions Conso (MW)"
    """

    user = None
    for x in users:
        if x['Alias'] == auth_details.Alias:
            user = x
            break

    if (user is None) or (not auth_handler.verify_password(auth_details.MotdePasse, user['MotdePasse'])):
        raise HTTPException(status_code=401, detail='Identifiant et/ou password incorrect')
    token = auth_handler.encode_token(user['MotdePasse'])  

    # Database pour le token
    token_model = models.Token_db()
    token_model.Token = token

    db.add(token_model)
    db.commit()

    return {'token': token }


""""""""""""""""""""""""""""""""""""""""
  BLOC : PARAMETRAGE DES INPUTS/OUTPUTS 
"""""""""""""""""""""""""""""""""""""""""

# Chargement de la BDD météo
def select_data(Localite, DateModele, Start, End):
    global df_all
    connection = mysql.connector.connect(**db_config)
    try:
        query = f"SELECT localite, date_prediction AS 'date prediction', jour_predit AS 'jour predit', id_jour AS 'id jour', conso AS 'conso(MW)', date_model AS 'date model' FROM PREDICTIONS"
        df_all = pd.read_sql(query, con=connection)
        print("Contenu du dataframe chargé ", df_all.head())  # Affiche le DataFrame
    except Exception as e:
        print(f"Une erreur s'est produite : {str(e)}")
    finally:
        connection.close()
    #df_all = pd.read_json(dirname(dirname(dirname(abspath(__file__))))+"/data/pred_model/model_bretagne_db.json")
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
                Query(None, description="Jour à partir duquel la prédiction est demandée, inclus (0: aujourd'hui, 1: demain, etc.)",
                ge=0, le=13),
                End: int=
                Query(None, description="Jour jusqu'auquel la prédiction est demandée, inclus (0: aujourd'hui, 1: demain, etc.)",
                ge=0, le=13)
                ):

            self.Region = Region
            self.Localite = Localite
            self.DateModele = DateModele
            self.Start = Start
            self.End = End


@app.get('/3ème étape : requête', tags=['Prédictions Conso (MW)'])
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
    elif Start is None and End is None :
        Start = 0
        End = 13
        headers = {'Content-Disposition': f'attachment; filename=ConsoPredict.csv'}
        return Response(select_data(Localite,DateModele,Start,End).to_csv(index=False, sep=';'),
        media_type="text/csv", headers=headers)
    elif Start is None :
        Start = 0
        headers = {'Content-Disposition': f'attachment; filename=ConsoPredict.csv'}
        return Response(select_data(Localite,DateModele,Start,End).to_csv(index=False, sep=';'),
        media_type="text/csv", headers=headers)
    elif End is None :
        End = 13
        headers = {'Content-Disposition': f'attachment; filename=ConsoPredict.csv'}
        return Response(select_data(Localite,DateModele,Start,End).to_csv(index=False, sep=';'),
        media_type="text/csv", headers=headers)
    else:
       headers = {'Content-Disposition': f'attachment; filename=ConsoPredict.csv'}
       return Response(select_data(Localite,DateModele,Start,End).to_csv(index=False, sep=';'),
        media_type="text/csv", headers=headers)


"""""""""""""""""""""""""""""""""""""""""
   BLOC : STOCKAGE DES PROFILS & TOKENS  
"""""""""""""""""""""""""""""""""""""""""

# Sécurisation du volet admin
security = HTTPBasic()

def get_admin(credentials: HTTPBasicCredentials  = Depends(security)):
  if credentials.username != 'admin' or credentials.password != '4dm1N':
     raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Incorrect id or password",
            headers={"WWW-Authenticate": "Basic"})
  return credentials.username

# Espace admin pour visualiser les connexions utilisateurs
@app.get("/admin", tags=['Admin'])
def __(db: Session = Depends(get_db), username:str = Depends(get_admin)):
    return db.query(models.Users_db).all()



if __name__ == "__main__":
    uvicorn.run(app, host = "0.0.0.0", port=8000)