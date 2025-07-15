#but du code : créer la classe actif, definir les  paramètres et les méthodes
import yfinance as yf
import math
from typing import List
import matplotlib.pyplot as plt
import streamlit as st
from datetime import datetime, timedelta

class Actifs: 
    def __init__(self, ticker: str, quantite: int=0, taux_sans_risque: float = 0.02):
        self.ticker = ticker.upper()
        self.quantite = quantite
        self.taux_sans_risque = taux_sans_risque
        self.nom_entreprise = ""
        self.prix_aujourdhui = 0
        self.prix_hier = 0
        self.historique_prix = []
        self.secteur = ""
        self.industrie = ""
        self.high = 0
        self.low = 0
        self.volume = 0
        self.market_cap = 0
        self.historique_rendements: List[float] = []

        self.initialiser_donnees()
    def afficher_infos(self):
        return {
            "Ticker": self.ticker,
            "Entreprise": self.nom_entreprise,
            "Secteur": self.secteur,
            "Prix aujourd'hui": self.prix_aujourdhui,
            "Volume": self.volume,
            "Market Cap": self.market_cap,
            "Industrie": self.industrie,
            "Valeur la + haute sur 52 semaines": self.high,
            "Valeur la + basse sur 52 semaines": self.low,
        }
    def initialiser_donnees(self):
        try:
            info = yf.Ticker(self.ticker)
            data = info.history(period="5d")  

            self.nom_entreprise = info.info.get("longName", "Inconnu")
            self.secteur = info.info.get("sector", "Inconnu")
            self.volume = info.info.get("volume", 0)
            self.market_cap = info.info.get("marketCap", 0)
            self.industrie = info.info.get("industry", "Inconnu")
            self.high = info.info.get("fiftyTwoWeekHigh", 0)
            self.low = info.info.get("fiftyTwoWeekLow", 0)

            self.historique_prix = data["Close"].tolist()

            if len(self.historique_prix) >= 2:
                self.prix_hier = self.historique_prix[-2]
                self.prix_aujourdhui = self.historique_prix[-1]
            elif len(self.historique_prix) == 1:
                self.prix_aujourdhui = self.historique_prix[-1]

            self.calculer_rendements()
        
        except Exception as e:
            print(f"Erreur lors de l'initialisation des données : {e}")

    def get_infos(self):
        return {
            "Ticker": self.ticker,
            "Entreprise": self.nom_entreprise,
            "Secteur": self.secteur,
            "Prix aujourd'hui": self.prix_aujourdhui,
            "Volume": self.volume,
            "Market Cap": self.market_cap,
            "Industrie": self.industrie,
            "Valeur la + haute sur 52 semaines": self.high,
            "Valeur la + basse sur 52 semaines": self.low,
            "Variation jour": self.variation_jour(),
            "Variation jour (%)": f"{self.variation_jour_pct():.2f}%",
            "Volatilité historique": f"{self.calculer_vol_historique():.4f}",
            "Maximum Drawdown (%)": f"{self.maximum_drawdown()*100:.2f}%",
        }

    def variation_jour(self):
        return self.prix_aujourdhui - self.prix_hier

    def variation_jour_pct(self):
        if self.prix_hier != 0:
            return (self.variation_jour() / self.prix_hier) * 100
        return 0

    def calculer_rendements(self):
        self.historique_rendements = []
        for i in range(1, len(self.historique_prix)):
            prix_ancien = self.historique_prix[i - 1]
            prix_nouveau = self.historique_prix[i]
            if prix_ancien != 0:
                rendement = (prix_nouveau - prix_ancien) / prix_ancien
                self.historique_rendements.append(rendement)
            else:
                self.historique_rendements.append(0)

    def calculer_vol_historique(self):
        if len(self.historique_rendements) < 2:
            return 0
        moyenne = sum(self.historique_rendements) / len(self.historique_rendements)
        variance = sum((r - moyenne) ** 2 for r in self.historique_rendements) / (len(self.historique_rendements) - 1)
        return math.sqrt(variance)

    def maximum_drawdown(self):
        if self.high != 0:
            return (self.high - self.low) / self.high
        else: 
            return 0

    def afficher_graphique(self, start_date='2024-01-01', end_date=None):
        if end_date is None:
            end_date = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')

        data = yf.download(self.ticker, start=start_date, end=end_date)
        if data.empty:
            st.warning("Pas de données disponibles pour afficher le graphique.")
            return

        st.line_chart(data['Close'])
        st.write("Derniers jours de clôture:")
        st.dataframe(data[['Close']].tail(5))
        st.write("Statistiques descriptives:")
        st.write(data['Close'].describe().round(2))
