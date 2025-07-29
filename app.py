import streamlit as st
import pandas as pd
import os

# Nom du fichier de données local
DATA_FILE = "portfolio.csv"

# Fonction pour charger les données (avec cache)
@st.cache_data
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        df = pd.DataFrame(columns=["Nom", "Prix"])  # colonnes initiales
        df.to_csv(DATA_FILE, index=False)
        return df

# Fonction pour enregistrer une nouvelle ligne (pas de cache ici)
def save_data(new_row):
    df = pd.read_csv(DATA_FILE)
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)

# Titre de l'app
st.title("📊 Mon Portefeuille d'Actions")

# Charger les données existantes
df = load_data()

# Afficher les données
st.subheader("📈 Portefeuille actuel")
st.dataframe(df, use_container_width=True)

# Formulaire pour ajouter une nouvelle action
st.subheader("➕ Ajouter une nouvelle action")

with st.form("form_ajout"):
    col1, col2 = st.columns(2)
    with col1:
        nom = st.text_input("Nom de l'action")
    with col2:
        prix = st.number_input("Prix de l'action (€)", min_value=0.0, format="%.2f")

    submitted = st.form_submit_button("Ajouter")

    if submitted:
        if nom.strip() == "":
            st.warning("Le nom de l'action ne peut pas être vide.")
        else:
            new_row = pd.DataFrame([[nom.strip(), prix]], columns=["Nom", "Prix"])
            save_data(new_row)
            st.success(f"L'action '{nom}' a été ajoutée.")
            st.cache_data.clear()  # vider le cache pour recharger les nouvelles données
            st.experimental_rerun()
