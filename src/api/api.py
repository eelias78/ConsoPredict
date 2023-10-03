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

# Pour la base de données
import mysql.connector
import time

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

"""
, openapi_tags=tags_metadata)

""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""



"""""""""""""""""""""""""""
    BLOC : LE ENDPOINT
"""""""""""""""""""""""""""

@app.get('/', tags=['Endpoint'])
async def test_fonctionnement_api():
    return{"Bonjour et bienvenue sur l'API ConsoPredict"}
    
""""""""""""""""""""""""""""""""""""""""
        BLOC : CREATION UTILISATEUR 
"""""""""""""""""""""""""""""""""""""""""

auth_handler = AuthHandler()
users = []

# Création de l'utilisateur 
@app.post('/1ère étape : enregistrez-vous', status_code=201, tags=['Authentification'])
async def __ (request: Profil):
    """
    Renseignez vos informations personnelles
    """
    Nom = request.Nom
    Prenom = request.Prenom  
    Email = request.Email
    Alias = request.Alias
    MotdePasse = request.MotdePasse
    
    # Récupération de la liste des alias existants
    connection = mysql.connector.connect(**db_config)
    try:
        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute("SELECT alias FROM USERS")
            liste_alias = [ligne[0] for ligne in cursor.fetchall()]
            cursor.close()
        else:
            raise HTTPException(status_code=404, detail='Erreur de connection à la base de données')
    except Exception as e:
        raise HTTPException(status_code=404, detail= str(e))
    finally:
        connection.close()
    
    # Vérification de l'existence de l'alias
    if any(x == request.Alias for x in liste_alias):
        raise HTTPException(status_code=400, detail='Le nom d\'utilisateur est déjà pris')
    else:
        # Hachage mot de passe et insertion en base de données du user
        connection = mysql.connector.connect(**db_config)
        try:
            if connection.is_connected():
                cursor = connection.cursor()
                hashed_password = auth_handler.get_password_hash(request.MotdePasse)
                query = "INSERT INTO USERS (nom, prenom, email, alias, motdepasse, hashed_mdp) \
                        VALUES('"+Nom+"','"+Prenom+"','"+Email+"','"+Alias+"','"+MotdePasse+"','"+hashed_password+"')"
                print(query)
                cursor.execute(query)
                connection.commit()
                cursor.close()
            else:
                connection.rollback()
                raise HTTPException(status_code=404, detail='Erreur de connection à la base de données')
        except Exception as e:
            raise HTTPException(status_code=404, detail= str(e))
        finally:
            connection.close()
                   
        return {"Alias ": request.Alias, "MotdePasse": request.MotdePasse}


""""""""""""""""""""""""""""""""""""""""
    BLOC : AUTHENTIFICATION PAR TOKEN 
"""""""""""""""""""""""""""""""""""""""""

# Login pour récupérer le token
@app.post('/2ème étape : authentifiez-vous', tags=['Authentification'])
async def __ (auth_details:AuthDetails):
    """
    - Renseignez vos identfiants créés à la 1ère étape (alias et mot de passe)
    - Copiez la clé/token entre guillemets
    - Collez le token dans le volet "Prédictions Conso (MW)"
    """
    # Récupération du mot de passe hashé de cet alias dans la base de données
    connection = mysql.connector.connect(**db_config)
    mdp_bdd = ""
    alias = auth_details.Alias
    try:
        if connection.is_connected():
            cursor = connection.cursor()
            query = "SELECT hashed_mdp FROM USERS WHERE alias = '"+alias+"'"
            cursor.execute(query)
            resultat = cursor.fetchone()
            cursor.close()
            # Si le tuple resultat n'est pas vide, alors le mdp a été trouvé dans la base de données
            if len(resultat) != 0:
                mdp_bdd = resultat[0]
        else:
            raise HTTPException(status_code=404, detail='Erreur de connection à la base de données')
    except Exception as e:
        raise HTTPException(status_code=404, detail= str(e))
    finally:
        connection.close()
    print('Mot de passe :', mdp_bdd)
    # Si le mdp n'a pas été trouvé dans la base de données (donc que l'alias n'existe pas en base), alors échec de connection 
    if mdp_bdd=="":
        raise HTTPException(status_code=401, detail='Alias inconnu')
    # Si le mdp a été trouvé mais que le mot de passe entré n'est pas correct, alors échec de connection
    if (not auth_handler.verify_password(auth_details.MotdePasse, mdp_bdd)):
        raise HTTPException(status_code=401, detail='Mot de passe incorrect')
    token = auth_handler.encode_token(mdp_bdd)
    # Enregistrement en BDD du couple alias / token  
    connection = mysql.connector.connect(**db_config)
    try:
        if connection.is_connected():
            cursor = connection.cursor()
            query = "INSERT INTO ALIAS_TOKEN (alias, token) VALUES('"+alias+"','"+token+"')"
            print(query)
            cursor.execute(query)
            connection.commit()
            cursor.close()
        else:
            connection.rollback()
            raise HTTPException(status_code=404, detail='Erreur de connection à la base de données')
    except Exception as e:
        raise HTTPException(status_code=404, detail= str(e))
    finally:
        connection.close()
    return {'token': token }


""""""""""""""""""""""""""""""""""""""""
  BLOC : PARAMETRAGE DES INPUTS/OUTPUTS 
"""""""""""""""""""""""""""""""""""""""""

# Chargement de l'ensemble des prédictions
def select_all_data():
    connection = mysql.connector.connect(**db_config)
    try:
        if connection.is_connected():
            query = f"SELECT localite, date_prediction AS 'date prediction', jour_predit AS 'jour predit', id_jour AS 'id jour', conso AS 'conso(MW)', date_model AS 'date model' FROM PREDICTIONS"
            df_all = pd.read_sql(query, con=connection)
        else:
            raise HTTPException(status_code=404, detail='Erreur de connection à la base de données')
    except Exception as e:
        raise HTTPException(status_code=404, detail= str(e))
    finally:
        connection.close()
    return(df_all)

# Chargement des prédictions filtrées sur les critères passés en paramètre
def select_data(Localite, DateModele, Start, End): 
    connection = mysql.connector.connect(**db_config)
    try:
        if connection.is_connected():
            query = f"SELECT localite, date_prediction AS 'date prediction', jour_predit AS 'jour predit', id_jour AS 'id jour', \
                conso AS 'conso(MW)', date_model AS 'date model' FROM PREDICTIONS \
                WHERE localite = '{Localite}' AND date_model = '{DateModele}' AND id_jour >= {Start} AND id_jour <= {End}"
            df_criteres = pd.read_sql(query, con=connection)
        else:
            raise HTTPException(status_code=404, detail='Erreur de connection à la base de données')
    except Exception as e:
        raise HTTPException(status_code=404, detail= str(e))
    finally:
        connection.close()
    return(df_criteres)
 

############## On attend 10 secondes pour être sûr que la BDD soit prête !
time.sleep(10)
##############    
# Appel pour récupérer le df global
df_all = select_all_data()

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
        return{"Vous n'avez pas choisi la version du modèle"}
    elif Start is None and End is None :
        Start = 0
        End = 13        
    elif Start is None :
        Start = 0
    elif End is None :
        End = 13
    # Log de la requête
    # On recherche d'abord l'alias correspondant au token
    connection = mysql.connector.connect(**db_config)
    try:
        if connection.is_connected():
            cursor = connection.cursor()
            query = "SELECT alias FROM USERS WHERE hashed_mdp= '"+Identifiant+"'"
            print('recherche alias :',query)
            cursor.execute(query)
            resultat = cursor.fetchone()
            cursor.close()
            # Si le tuple resultat n'est pas vide, alors le mdp a été trouvé dans la base de données
            if len(resultat) != 0:
                alias = resultat[0]
        else:
            raise HTTPException(status_code=404, detail='Erreur de connection à la base de données')
    except Exception as e:
        raise HTTPException(status_code=404, detail= str(e))
    finally:
        connection.close()
    # Puis on enregistre le log
    connection = mysql.connector.connect(**db_config)
    try:
        if connection.is_connected():
            cursor = connection.cursor()
            query = "INSERT INTO LOGS (date_log, alias, localite, date_model, start_day, end_day) \
                        VALUES(NOW(),'"+alias+"','"+Localite+"','"+DateModele+"','"+str(Start)+"','"+str(End)+"')"
            cursor.execute(query)
            connection.commit()
            cursor.close()
        else:
            connection.rollback()
            raise HTTPException(status_code=404, detail='Erreur de connection à la base de données')
    except Exception as e:
        raise HTTPException(status_code=404, detail= str(e))
    finally:
        connection.close()
    
    # Envoi de la réponse
    headers = {'Content-Disposition': f'attachment; filename=ConsoPredict.csv'}
    return Response(select_data(Localite,DateModele,Start,End).to_csv(index=False, sep=';'), media_type="text/csv", headers=headers)

if __name__ == "__main__":
    uvicorn.run(app, host = "0.0.0.0", port=8000)