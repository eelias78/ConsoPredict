# Fichier principal de l'application

# Import librairies python nécessaires
from collections import OrderedDict
import streamlit as st
import os

# Import librairies définies dans l'application
import config
from tabs import intro, second_tab

# Construction de la page principale : sidebar + 2 tabs (onglets)
os.chdir(os.path.dirname( __file__ ))

st.set_page_config(
    page_title=config.TITLE,
    page_icon="https://datascientest.com/wp-content/uploads/2020/03/cropped-favicon-datascientest-1-32x32.png",
)

with open("style.css", "r") as f:
    style = f.read()

st.markdown(f"<style>{style}</style>", unsafe_allow_html=True)

TABS = OrderedDict(
    [
        (intro.sidebar_name, intro),
        (second_tab.sidebar_name, second_tab),
    ]
)


def run():
    st.sidebar.image(
        "https://www.leslivresblancs.fr/sites/default/files/logo-datascientest.png",
        width=200,
    )
    tab_name = st.sidebar.radio("", list(TABS.keys()), 0)
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"## {config.PROMOTION}")

    st.sidebar.markdown("### Team members:")
    for member in config.TEAM_MEMBERS:
        st.sidebar.markdown(member.sidebar_markdown(), unsafe_allow_html=True)

    tab = TABS[tab_name]

    tab.run()

if __name__ == "__main__":
    run()