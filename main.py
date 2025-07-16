import streamlit as st
import pandas as pd
from datetime import date, datetime
from database_portefeuille import DatabasePortefeuille
from classe_actifs import Actifs
from classe_index import Index
from classe_portefeuille import Portefeuille

db = DatabasePortefeuille()

if "nom_portefeuille" not in st.session_state:
    st.session_state.nom_portefeuille = None
if "portefeuille_obj" not in st.session_state:
    st.session_state.portefeuille_obj = None

def load_portfolio_obj(nom):
    # Load portfolio data from DB and build Portefeuille object
    actions = db.get_actions(nom)
    port = Portefeuille(nom)
    # Clear current holdings before reload (assuming Portefeuille has such a method)
    port.clear_all()  
    for (ticker, quantite, prix_achat, date_achat) in actions:
        actifs = Actifs(ticker)
        port.ajouter_action(actifs, quantite, datetime.combine(date_achat, datetime.min.time()), prix_achat)
    return port

def main():
    st.set_page_config(page_title="Gestion de Portefeuille", page_icon="📉")
    st.title("📉 Gestion de Portefeuille")

    portfolios = db.get_all_portfolios()

    menu = {
        "1) Créer portefeuille": "create_portfolio",
        "2) Sélectionner portefeuille": "select_portfolio",
        "3) Ajouter/Retirer action": "manage_actions",
        "4) Performance / Rendements": "performance",
        "5) Consulter un Index": "index",
        "6) Comparer portefeuille à un Index": "compare",
        "7) Metrics du portefeuille (Sharpe ratio)": "metrics",
    }

    choix = st.sidebar.selectbox("Menu", list(menu.keys()))

    match menu[choix]:

        case "create_portfolio":
            nom = st.text_input("Nom du portefeuille")
            if st.button("Créer") and nom:
                if nom in portfolios:
                    st.warning("Ce portefeuille existe déjà.")
                else:
                    db.ajouter_portefeuille(nom)
                    st.session_state.nom_portefeuille = nom
                    st.session_state.portefeuille_obj = Portefeuille(nom)
                    st.success(f"Portefeuille '{nom}' créé !")

        case "select_portfolio":
            if portfolios:
                selected = st.selectbox("Choisissez un portefeuille", portfolios)
                if st.button("Sélectionner"):
                    st.session_state.nom_portefeuille = selected
                    st.session_state.portefeuille_obj = load_portfolio_obj(selected)
                    st.success(f"Portefeuille '{selected}' sélectionné.")
            else:
                st.warning("Aucun portefeuille trouvé. Créez-en un d'abord.")

        case "manage_actions":
            if st.session_state.nom_portefeuille is None:
                st.warning("Créez ou sélectionnez d'abord un portefeuille.")
            else:
                port = st.session_state.portefeuille_obj
                op = st.selectbox("Opération", ["Ajouter", "Retirer"])
                ticker = st.text_input("Ticker")
                quantite = st.number_input("Quantité", min_value=1, step=1)
                date_achat = None
                prix_achat = None

                if op == "Ajouter":
                    date_achat = st.date_input("Date d'achat", value=date.today())
                    prix_achat = st.number_input("Prix d'achat", min_value=0.0, format="%.2f")

                if st.button("Valider"):
                    if not ticker:
                        st.warning("Veuillez saisir un ticker.")
                    elif op == "Ajouter" and (date_achat is None or prix_achat is None):
                        st.warning("Veuillez saisir la date et le prix d'achat.")
                    else:
                        if op == "Ajouter":
                            actifs = Actifs(ticker.upper())
                            port.ajouter_action(actifs, quantite, datetime.combine(date_achat, datetime.min.time()), prix_achat)
                            db.ajouter_action(st.session_state.nom_portefeuille, ticker.upper(), quantite, prix_achat, date_achat)
                            st.success(f"{quantite} actions {ticker.upper()} ajoutées au portefeuille.")
                        else:  # Retirer
                            port.retirer_action(ticker.upper(), quantite)
                            db.retirer_action(st.session_state.nom_portefeuille, ticker.upper(), quantite)
                            st.success(f"{quantite} actions {ticker.upper()} retirées du portefeuille.")

        case "performance":
            if st.session_state.nom_portefeuille is None:
                st.warning("Créez ou sélectionnez d'abord un portefeuille.")
            else:
                port = st.session_state.portefeuille_obj
                st.subheader("Performance du portefeuille")
                perf_df = port.afficher_performance()
                st.dataframe(perf_df)

                # Show detailed rendement par action
                data = []
                for action, quantite in zip(port.actifs, port.quantites):
                    prix_achat = port.prix_achats.get(action.ticker, 0)
                    prix_courant = action.get_prix_actuel()
                    rendement = (prix_courant - prix_achat) / prix_achat if prix_achat else 0
                    data.append({
                        "Ticker": action.ticker,
                        "Quantité": quantite,
                        "Prix Achat": round(prix_achat, 2),
                        "Prix Actuel": round(prix_courant, 2),
                        "Rendement (%)": round(rendement * 100, 2)
                    })
                perf_detail_df = pd.DataFrame(data)
                st.dataframe(perf_detail_df)

        case "index":
            ticker_index = st.text_input("Ticker de l'Index")
            if ticker_index:
                index = Index(ticker_index)
                st.subheader(f"Informations sur l'Index {ticker_index.upper()}")
                st.write(index.afficher_infos())

                fig = index.afficher_graphique()
                if fig:
                    st.pyplot(fig)

        case "compare":
            if st.session_state.nom_portefeuille is None:
                st.warning("Créez ou sélectionnez d'abord un portefeuille.")
            else:
                ticker_index = st.text_input("Ticker de l'Index de référence")
                if ticker_index and st.button("Comparer"):
                    index = Index(ticker_index)
                    compar_df = st.session_state.portefeuille_obj.comparer_a_reference(index)
                    st.dataframe(compar_df)

        case "metrics":
            if st.session_state.nom_portefeuille is None:
                st.warning("Créez ou sélectionnez d'abord un portefeuille.")
            else:
                ratio = st.session_state.portefeuille_obj.ratio_sharpe()
                st.metric("Ratio de Sharpe", f"{ratio:.4f}")

if __name__ == "__main__":
    main()
