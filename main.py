from classe_actifs import Actifs
from classe_index import Index
from classe_portefeuille import Portefeuille
import streamlit as st
from datetime import date
import pandas as pd
from database_portefeuille import DatabasePortefeuille

db = DatabasePortefeuille()

if "nom_portefeuille" not in st.session_state:
    st.session_state.nom_portefeuille = None

def main():
    st.set_page_config(page_title="Gestion de Portefeuille", page_icon="📉")
    st.title("📉 Gestion de Portefeuille")

    menu = {
        "1) Créer portefeuille": "create_port",
        "2) Ajouter action": "add_action",
        "3) Retirer action": "remove_action",
        "4) Afficher portefeuille": "show_port",
        "5) Consulter une action": "view_action",
        "6) Consulter un Index": "view_index",
        "7) Metrics du portefeuille (ratio de Sharpe)": "metrics",
    }
    choix = st.sidebar.selectbox("Menu", list(menu.keys()))

    match menu[choix]:

        case "create_port":
            nom = st.text_input("Nom du portefeuille")
            if st.button("Créer") and nom:
                if nom in db.get_all_portfolios():
                    st.warning("Ce portefeuille existe déjà.")
                else:
                    db.ajouter_portefeuille(nom)
                    st.session_state.nom_portefeuille = nom
                    st.success(f"Portefeuille '{nom}' créé !")

        case "add_action":
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

        case "remove_action":
            if st.session_state.nom_portefeuille is None:
                st.warning("Créez d'abord un portefeuille.")
            else:
                ticker = st.text_input("Ticker à retirer")
                quantite = st.number_input("Quantité à retirer", min_value=1, step=1)
                if st.button("Retirer"):
                    db.retirer_action(st.session_state.nom_portefeuille, ticker.upper(), quantite)
                    st.success(f"{quantite} actions {ticker.upper()} retirées du portefeuille '{st.session_state.nom_portefeuille}'.")

        case "show_port":
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

        case "view_action":
            ticker = st.text_input("Ticker de l'action à consulter")
            if ticker:
                # Exemple simplifié : récupération via yfinance
                import yfinance as yf
                actif = yf.Ticker(ticker)
                info = actif.info
                st.subheader(f"Informations sur {ticker.upper()}")
                st.write({
                    "Nom": info.get("longName"),
                    "Secteur": info.get("sector"),
                    "Prix actuel": info.get("currentPrice"),
                    "Capitalisation": info.get("marketCap"),
                })
                hist = actif.history(period="1mo")
                if not hist.empty:
                    st.line_chart(hist["Close"])

        case "view_index":
            ticker_index = st.text_input("Ticker de l'Index à consulter")
            if ticker_index:
                import yfinance as yf
                index = yf.Ticker(ticker_index)
                st.subheader(f"Informations sur l'Index {ticker_index.upper()}")
                info = index.info
                st.write({
                    "Nom": info.get("longName"),
                    "Prix actuel": info.get("currentPrice"),
                    "Capitalisation": info.get("marketCap"),
                })
                hist = index.history(period="1mo")
                if not hist.empty:
                    st.line_chart(hist["Close"])

        case "metrics":
            if st.session_state.nom_portefeuille is None:
                st.warning("Créez d'abord un portefeuille.")
            else:
                # Exemple simple du ratio de Sharpe calculé sur les rendements quotidiens simulés
                actions = db.get_actions(st.session_state.nom_portefeuille)
                if not actions:
                    st.warning("Portefeuille vide, impossible de calculer les métriques.")
                else:
                    # Ici tu devras adapter selon ta classe Portefeuille et calculs
                    # Exemple minimal avec données fictives :
                    import numpy as np
                    rendements = np.random.normal(0.001, 0.02, 252)  # simulé
                    sharpe = rendements.mean() / rendements.std() * (252 ** 0.5)
                    st.metric("Ratio de Sharpe estimé", f"{sharpe:.4f}")

if __name__ == "__main__":
    main()
