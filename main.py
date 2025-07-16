import streamlit as st
from datetime import datetime, date
from classe_actifs import Actifs
from classe_index import Index
from classe_portefeuille import Portefeuille
import yfinance as yf
import pandas as pd 

if "portefeuille" not in st.session_state:
    st.session_state.portefeuille = Portefeuille("Mon Portefeuille")

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
                actifs.afficher_graphique()

        case "create_port":
            nom = st.text_input("Nom du portefeuille")
            if st.button("Créer") and nom:
                st.session_state.portefeuille = Portefeuille(nom)
                st.success(f"Portefeuille '{nom}' créé ✔️")

        case "manage_port":
            port = st.session_state.portefeuille
            if port is None:
                st.warning("Créez d'abord un portefeuille dans l'onglet précédent.")
            else:
                actifs_ticker = st.text_input("Ticker de l'action")
                op = st.selectbox("Opération", ["Ajouter", "Retirer"])
                quantite = st.number_input("Quantité", min_value=1, step=1)
                date_achat = None
                
                if op == "Ajouter":
                    date_achat = st.date_input("Date d'achat", value=date.today())
                    
                if st.button("Valider") and actifs_ticker and quantite:
                    actifs = Actifs(actifs_ticker)
                    if op == "Ajouter":
                        port.ajouter_action(actifs, int(quantite), datetime.combine(date_achat, datetime.min.time()))
                        st.success("Actifs ajoutés au portefeuille ✅")
                    else:
                        port.retirer_action(actifs_ticker, int(quantite))
                        st.success("Actifs retirés du portefeuille 🗑️")
                    
                if st.checkbox("Afficher contenu portefeuille"):
                    st.write("Actifs : ", port.actifs)
                    st.write("Quantités : ", port.quantites)
                    st.write("Tickers:", [a.ticker for a in port.actifs])
                   


        case "performance":
            port = st.session_state.portefeuille
            if port is None:
                st.warning("Portefeuille vide.")
            else:
                st.subheader("Performance du portefeuille")
                perf_df = port.afficher_performance()
                st.dataframe(perf_df)
 
       # créer un DataFrame pour affichage propre
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

            perf_df = pd.DataFrame(data)
            st.dataframe(perf_df)


        case "index":
            ticker_index = st.text_input("Ticker de l'Index")
            if ticker_index:
                index = Index(ticker_index)
                st.subheader(f"Informations sur l'Index {ticker_index.upper()}")
                st.write(index.afficher_infos())  # note le pluriel 'afficher_infos'

                fig = index.afficher_graphique()
                if fig:
                    st.pyplot(fig)

        case "compare":
            port = st.session_state.portefeuille
            if port is None:
                st.warning("Créez d'abord un portefeuille.")
            else:
                ticker_index = st.text_input("Ticker de l'Index de référence")
                if ticker_index and st.button("Comparer"):
                    index = Index(ticker_index)
                    compar_df = port.comparer_a_reference(index)
                    st.dataframe(compar_df)

        case "metrics":
            port = st.session_state.portefeuille
            if port is None:
                st.warning("Créez d'abord un portefeuille.")
            else:
                ratio = port.ratio_sharpe()
                st.metric("Ratio de Sharpe", f"{ratio:.4f}")


if __name__ == "__main__":
    main()
