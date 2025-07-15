import streamlit as st
from datetime import datetime, date
from classe_actifs import Actifs
from classe_index import Index
from classe_portefeuille import Portefeuille
import yfinance as yf



def main():
    st.set_page_config(page_title="Gestion de Portefeuille", page_icon="📉")
    st.title("📉 Gestion de Portefeuille")

    # ---- État de session ----
    if "portefeuille" not in st.session_state:
        st.session_state.portefeuille = None

    # ---- Menu latéral ----
    menu = {
        "1) Consulter une action": "action",
        "2) Créer un portefeuille": "create_port",
        "3) Ajouter/retirer des actions au portefeuille": "manage_port",
        "4) Consulter performance / rendements du portefeuille": "performance",
        "5) Consulter un Index": "index",
        "6) Comparer rendements du portefeuille à un Index": "compare",
        "7) Metrics du portefeuille (ratio de Sharpe)": "metrics",
    }
    choix = st.sidebar.selectbox("Menu", list(menu.keys()))

    match menu[choix]:
        case "action":
            ticker = st.text_input("Ticker de l'action")
            if ticker:
                actifs = Actifs(ticker)
                st.subheader(f"Informations sur {ticker.upper()}")
                st.write(actifs.afficher_infos())

        case "create_port":
            nom = st.text_input("Nom du portefeuille")
            if st.button("Créer") and nom:
                st.session_state.portefeuille = Portefeuille(nom)
                st.success(f"Portefeuille '{nom}' créé ✔️")

        case "manage_port":
            port = st.session_state.portefeuille
            if port is None:
                st.warning("Créez d'abord un portefeuille dans l'onglet précédent.")
                break
            actifs_ticker = st.text_input("Ticker de l'action")
            op = st.selectbox("Opération", ["Ajouter", "Retirer"])
            quantite = st.number_input("Quantité", min_value=1, step=1)
            date_achat = None
            if op == "Ajouter":
                date_achat = st.date_input("Date d'achat", value=date.today())
            if st.button("Valider") and actifs_ticker and quantite:
                actifs = Actifs(actifs_ticker)
                if op == "Ajouter":
                    port.ajouter_actifs(actifs, int(quantite), datetime.combine(date_achat, datetime.min.time()))
                    st.success("Actifs ajoutés au portefeuille ✅")
                else:
                    port.retirer_actifs(actifs_ticker, int(quantite))
                    st.success("Actifs retirés du portefeuille 🗑️")

        case "performance":
            port = st.session_state.portefeuille
            if port is None:
                st.warning("Créez d'abord un portefeuille.")
                break
            st.subheader("Performance du portefeuille")
            perf_df = port.afficher_performance()
            st.dataframe(perf_df)

        case "index":
            ticker_index = st.text_input("Ticker de l'Index")
            if ticker_index:
                index = Index(ticker_index)
                st.subheader(f"Informations sur l'Index {ticker_index.upper()}")
                st.write(index.afficher_info())

        case "compare":
            port = st.session_state.portefeuille
            if port is None:
                st.warning("Créez d'abord un portefeuille.")
                break
            ticker_index = st.text_input("Ticker de l'Index de référence")
            if ticker_index and st.button("Comparer"):
                index = Index(ticker_index)
                compar_df = port.comparer_a_reference(index)
                st.dataframe(compar_df)

        case "metrics":
            port = st.session_state.portefeuille
            if port is None:
                st.warning("Créez d'abord un portefeuille.")
                break
            ratio = port.ratio_sharpe()
            st.metric("Ratio de Sharpe", f"{ratio:.4f}")


if __name__ == "__main__":
    main()
