import yfinance as yf
import math
from typing import List
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd

class Index:
    def __init__(self, ticker: str):
        self.ticker = ticker
        self.nom = ""
        self.historique_prix: List[float] = []
        self.historique_rendements: List[float] = []
        self.historique_dates = []
        self.initialiser_donnees()

    def initialiser_donnees(self):
        try:
            info = yf.Ticker(self.ticker)
            data = info.history(period="1y")  # Dernière année par défaut

            self.nom = info.info.get("longName", "Inconnu")
            self.historique_prix = data["Close"].tolist()
            self.historique_dates = data.index.to_list()
            self.calculer_rendements()
        except Exception as e:
            # On évite print, on peut stocker une erreur ou la gérer différemment
            self.nom = "Erreur chargement données"
            self.historique_prix = []
            self.historique_dates = []
            self.historique_rendements = []

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

    def variation_jour(self):
        if len(self.historique_prix) < 2:
            return 0
        return self.historique_prix[-1] - self.historique_prix[-2]

    def variation_jour_pct(self):
        if len(self.historique_prix) < 2 or self.historique_prix[-2] == 0:
            return 0
        return (self.historique_prix[-1] - self.historique_prix[-2]) / self.historique_prix[-2] * 100

    def calculer_vol_historique(self):
        return self.volatilite()

    def volatilite(self):
        if len(self.historique_rendements) < 2:
            return 0
        moyenne = sum(self.historique_rendements) / len(self.historique_rendements)
        variance = sum((r - moyenne) ** 2 for r in self.historique_rendements) / (len(self.historique_rendements) - 1)
        return math.sqrt(variance)

    def calculer_sharpe(self, taux_sans_risque=0.01):
        if not self.historique_rendements:
            return 0
        rendement_moyen = sum(self.historique_rendements) / len(self.historique_rendements)
        volatilite = self.volatilite()
        if volatilite == 0:
            return 0
        rendement_annuel = rendement_moyen * 252
        return (rendement_annuel - taux_sans_risque) / (volatilite * math.sqrt(252))

    def maximum_drawdown(self):
        if not self.historique_prix:
            return 0
        pic = self.historique_prix[0]
        max_dd = 0
        for prix in self.historique_prix:
            if prix > pic:
                pic = prix
            drawdown = (prix - pic) / pic
            if drawdown < max_dd:
                max_dd = drawdown
        return abs(max_dd)

    def get_rendement_depuis(self,date_debut):
        if isinstance(date_debut, str):
            try:
                date_debut = datetime.strptime(date_debut, "%Y-%m-%d")
            except ValueError:
                return None

        if not self.historique_dates or not self.historique_prix:
            return None

        index_debut = None
        for i, d in enumerate(self.historique_dates):
            if d is None:
                continue
            if d >= date_debut:
                index_debut = i
                break

        if index_debut is None:
            return None

        prix_debut = self.historique_prix[index_debut]
        prix_fin = self.historique_prix[-1]

        if prix_debut == 0:
            return None

        rendement = (prix_fin / prix_debut) - 1
        return rendement

    def performance_cumulee(self):
        if not self.historique_prix:
            return 0
        return (self.historique_prix[-1] / self.historique_prix[0]) - 1

    def afficher_infos(self):
        # Retourner un dict à afficher dans Streamlit
        return {
            "Index/ETF": f"{self.nom} ({self.ticker})",
            "Période (jours)": len(self.historique_prix),
            "Performance cumulée (%)": round(self.performance_cumulee() * 100, 2),
            "Volatilité (%)": round(self.volatilite() * 100, 2),
            "Variation jour": round(self.variation_jour(), 2),
            "Variation jour (%)": round(self.variation_jour_pct(), 2),
            "Ratio de Sharpe": round(self.calculer_sharpe(), 4),
            "Maximum Drawdown (%)": round(self.maximum_drawdown() * 100, 2),
        }

    def afficher_graphique(self):
        if not self.historique_dates or not self.historique_prix:
            return None
        plt.figure(figsize=(10, 5))
        plt.plot(self.historique_dates, self.historique_prix, label="Prix de clôture")
        plt.title(f"Historique des prix pour {self.ticker.upper()}")
        plt.xlabel("Date")
        plt.ylabel("Prix")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        return plt

    def get_performance(self):
        """Retourne un DataFrame avec les indicateurs clés de performance"""
        infos = self.afficher_infos()
        df = pd.DataFrame([infos])
        return df
