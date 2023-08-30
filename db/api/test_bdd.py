import os
import mysql.connector
import time
from fastapi import FastAPI
import uvicorn
import logging

logger = logging.getLogger("my_logger")
logging.basicConfig(level=logging.DEBUG)

# Informations de connexion à la base de données
db_config = {
    "host": os.environ.get("DB_HOST", "db"),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASSWORD", "pwd"),
    "database": os.environ.get("DB_NAME", "dbconsopredict"),
    "port": int(os.environ.get("DB_PORT", 3306))
}

def test_database_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            print("Connected to the database")
            
            # Exécuter une requête SELECT
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM users")
            result = cursor.fetchall()
            print("SELECT * FROM users returned:", result)
            cursor.close()
            connection.close()
        else:
            print("Connection failed")
    except Exception as e:
        print("Error:", str(e))

tags_metadata = [{"name": "nom api"
        }]

app = FastAPI(title ='titre API', description = 'description API', openapi_tags=tags_metadata)
@app.get('/', tags=['Endpoint'])
async def test_fonctionnement_api():
    logger.info("Accès à la racine")
    return{"Bonjour et bienvenue sur cette API"}

if __name__ == "__main__":
    # sleep 10
    print("attente démarrage base de données")
    time.sleep(10)
    print("test connexion base de données")
    test_database_connection()
    print("démarrage API")
    uvicorn.run(app, host = "0.0.0.0", port=8000)