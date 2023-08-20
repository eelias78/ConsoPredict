FROM ubuntu:20.04


#Mise à jour et installation des packages
RUN apt-get update && apt-get install -y python3-pip cron
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

#Définition du répertoire de travail et copie du contenu du répertoire local
WORKDIR /app
COPY . .

#Copie du script cron dans le conteneur
COPY crontab /etc/cron.d/crontab
#Copie des répertoires data dans le conteneur
COPY ./data/processed/ /app/data/processed/
COPY ./data/raw/ /app/data/raw/
#Copie des scripts python dans le conteneur
COPY meteo_concept_xtract.py /app/cron_meteo_concept/meteo_concept_xtract.py
COPY meteo_concept_preproc.py /app/cron_meteo_concept/meteo_concept_preproc.py

#Vue
RUN ls -l
#Attribution des droits au script
RUN chmod 0644 /etc/cron.d/crontab
RUN /usr/bin/crontab /etc/cron.d/crontab

#L'executable principal du conteneur
ENTRYPOINT ["cron", "-f"]


