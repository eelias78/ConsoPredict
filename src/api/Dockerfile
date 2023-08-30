# Utilisation de l'image Python:slim comme base
FROM python:3.11-slim

# Définir le répertoire de travail
WORKDIR /app

# Copie le fichier requirements.txt dans le conteneur
COPY requirements.txt .

# Installer les dépendances (mysql-connector-python)
RUN pip install -r requirements.txt

# Copie le contenu de l'application dans le conteneur
COPY . .

# Exécuter le script lorsqu'un conteneur basé sur cette image est démarré
CMD ["python", "api.py"]
