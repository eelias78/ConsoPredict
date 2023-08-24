# Utilisation de l'image Python:slim comme base
FROM python:3.11-slim

# Définir le répertoire de travail
WORKDIR /app

# Copie le fichier requirements.txt dans le conteneur
COPY requirements.txt .

# Installer les dépendances (mysql-connector-python)
RUN pip install -r requirements.txt
# Mettre à jour la liste des paquets et installer curl
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copie le contenu de l'application dans le conteneur
COPY . .

# Exécuter le script lorsqu'un conteneur basé sur cette image est démarré
CMD ["python", "test_bdd.py"]
