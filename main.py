import streamlit as st
from datetime import date
import pandas as pd
from classe_portefeuille import Portefeuille
from classe_index import Index
from database_portefeuille import DatabasePortefeuille

db = DatabasePortefeuille()

if "nom_portefeuille" not in st.session_state:
    st.session_state.nom_portefeuille = None

def main():
    st.set_page_config(page_title="Gestion de Portefeuille", page_icon="📉")
    st.title("📉 Gestion de Portefeuille")

    menu = {
        "1) Créer portefeuille": "create_portfolio",
        "2) Ajouter action": "add_action",
        "3) Afficher portefeuille": "show_portfolio",
        "4) Afficher performance": "show_performance",
        "5) Consulter un Index": "view_index",
        "6) Comparer portefeuille à un Index": "compare_index",
        "7) Metrics du portefeuille (ratio de Sharpe)": "metrics",
    }

    choix = st.sidebar.selectbox("Menu", list(menu.keys()))

    match menu[choix]:
        case "create_portfolio":
            nom = st.text_input("Nom du portefeuille")
            if st.button("Créer") and nom:
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

        case "show_portfolio":
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

        case "show_performance":
            if st.session_state.nom_portefeuille is None:
                st.warning("Créez d'abord un portefeuille.")
            else:
                port = Portefeuille(st.session_state.nom_portefeuille, db)
                perf_df = port.afficher_performance()
                st.subheader(f"Performance du portefeuille '{port.nom}'")
                st.dataframe(perf_df)

        case "view_index":
            ticker_index = st.text_input("Ticker de l'Index")
            if ticker_index:
                index = Index(ticker_index)
                st.subheader(f"Informations sur l'Index {ticker_index.upper()}")
                st.write(index.afficher_infos())

                fig = index.afficher_graphique()
                if fig:
                    st.pyplot(fig)

        case "compare_index":
            if st.session_state.nom_portefeuille is None:
                st.warning("Créez d'abord un portefeuille.")
            else:
                ticker_index = st.text_input("Ticker de l'Index de référence")
                if ticker_index and st.button("Comparer"):
                    index = Index(ticker_index)
                    port = Portefeuille(st.session_state.nom_portefeuille, db)
                    compar_df = port.comparer_a_reference(index)
                    st.dataframe(compar_df)

        case "metrics":
            if st.session_state.nom_portefeuille is None:
                st.warning("Créez d'abord un portefeuille.")
            else:
                port = Portefeuille(st.session_state.nom_portefeuille, db)
                ratio = port.ratio_sharpe()
                st.metric("Ratio de Sharpe", f"{ratio:.4f}")

if __name__ == "__main__":
    main()
