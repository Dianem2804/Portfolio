import streamlit as st
from datetime import date

db = DatabasePortefeuille()

if "nom_portefeuille" not in st.session_state:
    st.session_state.nom_portefeuille = None

choix = st.sidebar.selectbox("Menu", ["Créer portefeuille", "Ajouter action", "Afficher portefeuille"])

if choix == "Créer portefeuille":
    nom = st.text_input("Nom du portefeuille")
    if st.button("Créer") and nom:
        db.ajouter_portefeuille(nom)
        st.session_state.nom_portefeuille = nom
        st.success(f"Portefeuille '{nom}' créé !")

elif choix == "Ajouter action":
    if st.session_state.nom_portefeuille is None:
        st.warning("Créez d'abord un portefeuille.")
    else:
        ticker = st.text_input("Ticker")
        quantite = st.number_input("Quantité", min_value=1, step=1)
        date_achat = st.date_input("Date d'achat", value=date.today())
        prix_achat = st.number_input("Prix d'achat", min_value=0.0, format="%.2f")

        if st.button("Ajouter"):
            db.ajouter_action(st.session_state.nom_portefeuille, ticker.upper(), quantite, prix_achat, date_achat)
            st.success(f"{quantite} actions {ticker.upper()} ajoutées au portefeuille '{st.session_state.nom_portefeuille}'.")

elif choix == "Afficher portefeuille":
    if st.session_state.nom_portefeuille is None:
        st.warning("Créez d'abord un portefeuille.")
    else:
        st.subheader(f"Portefeuille: {st.session_state.nom_portefeuille}")
        actions = db.get_actions(st.session_state.nom_portefeuille)
        if not actions:
            st.write("Portefeuille vide.")
        else:
            df = pd.DataFrame(actions, columns=["Ticker", "Quantité", "Prix Achat", "Date Achat"])
            st.dataframe(df)
