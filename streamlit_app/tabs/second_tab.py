# Fichier gérant l'onglet Application, qui est le coeur de l'appli (saisie des paramètres et appel de l'API ConsoPredict
import streamlit as st
import requests

# définition de l'adresse de l'API
api_address = '127.0.0.1'
# port de l'API
api_port = 8000

title = "Application"
sidebar_name = "Application"

def run():
    st.title(title)
    st.image("img_appli.jpg")
    # Choix du jour de début entre aujourd'hui (par défaut) et J+14
    jour_deb = st.slider('Jour de début entre 0 (aujourd''hui) et 14 (J+14)',0,14,value=0)
    # Choix du jour de fin entre aujourd'hui et J+14 (par défaut)
    jour_fin = st.slider('Jour de fin entre 0 (aujourd''hui) et 14 (J+14)',0,14,value=14)
    # Choix de la région
    region = st.radio('Région',['50041','14137', '76116', '29075','22168', '35238', '61001', '56152', '44020'])
    if st.button('Calcul'):
        if jour_fin<jour_deb:
            st.error('Le jour de fin doit être supérieur au jour de début')
        else:
            # Appel API
            # Pour l'instant, on va juste appeler le endpoint de base qui renvoie un message de bienvenue
            r = requests.get(url='http://{address}:{port}/'.format(address=api_address, port=api_port),
                             params= {'username': 'daniel',
                                      'password': 'datascientest'})
            st.info(r.text)            