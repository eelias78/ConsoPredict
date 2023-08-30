# Fichier gérant l'onglet Introduction, composé d'une description de l'application
import streamlit as st

title = "ConsoPredict"
sidebar_name = "Page d'accueil"

def run():
    st.image("img_accueil.jpg")
    st.title(title)
    st.markdown("---")
    st.markdown(
        """
        Cette application vous permet d'estimer la consommation électrique d'une région,
        """)
    st.markdown(
        """
        ainsi que l'étiquette énergétique associée (déduite du "mix" énergétique),
        """)
    st.markdown(
        """
        en fonction des prévisions météorologiques des 14 prochains jours
        """)