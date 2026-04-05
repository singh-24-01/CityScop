import streamlit as st
import pandas as pd

st.set_page_config(layout="wide", page_title="Données sources", page_icon="📂")

st.title("📂 Données sources")

st.write(
    "Vous trouverez ici l'ensemble des données brutes utilisées dans l'application. "
    "Ces tableaux sont exportés directement depuis nos fichiers de référence, "
    "sans transformation ni agrégation."
)

st.divider()

def afficher_data_dep():
    st.header("🗺️ Données par département")
    st.write("Indicateurs économiques, sociaux, éducatifs et climatiques agrégés à l'échelle départementale.")
    data_dep = pd.read_excel('data/data_departement.xlsx')
    st.dataframe(data_dep, use_container_width=True)

def afficher_data_meteo():
    st.header("🌤️ Données météorologiques")
    st.write("Températures moyennes, précipitations, humidité et vitesse du vent par département.")
    data_meteo = pd.read_excel('data/meteo.xlsx')
    st.dataframe(data_meteo, use_container_width=True)

def afficher_data_ville():
    st.header("🏙️ Données par ville")
    st.write("Mêmes indicateurs que les départements, mais à l'échelle communale pour les villes de plus de 20 000 habitants.")
    data_ville = pd.read_excel('data/data_ville.xlsx')
    st.dataframe(data_ville, use_container_width=True)

tab1, tab2, tab3 = st.tabs(["Départements", "Météo", "Villes"])

with tab1:
    afficher_data_dep()

with tab2:
    afficher_data_meteo()

with tab3:
    afficher_data_ville()
