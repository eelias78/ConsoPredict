# Utilise une image de base avec Python pré-installé
FROM python:3.11

# Définit le répertoire de travail dans le conteneur
WORKDIR /app

# Copie le fichier requirements.txt dans le conteneur
COPY requirements.txt .

# Installe les dépendances
RUN pip3 install -r requirements.txt

# Copie le contenu de l'application dans le conteneur
COPY . .

# Commande pour lancer l'API FastAPI lorsque le conteneur démarre
CMD ["uvicorn", "api:app"]