import yfinance as yf
import math
from typing import List
import pandas as pd
import matplotlib.pyplot as plt

#but du code : créer la classe actif, definir les  paramètres et les méthodes
import yfinance as yf
import math
from typing import List

class Actifs:
    def __init__(self, ticker: str, quantite: int = 0, taux_sans_risque: float = 0.02):
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
            raise RuntimeError(f"Erreur lors de l'initialisation des données pour {self.ticker} : {e}")

    def get_infos(self) -> dict:
        """Retourne un dictionnaire des infos clés à afficher dans Streamlit"""
        return {
            "Ticker": self.ticker,
            "Entreprise": self.nom_entreprise,
            "Secteur": self.secteur,
            "Industrie": self.industrie,
            "Prix aujourd'hui": self.prix_aujourdhui,
            "Prix hier": self.prix_hier,
            "Volume": self.volume,
            "Market Cap": self.market_cap,
            "Valeur la plus haute sur 52 semaines": self.high,
            "Valeur la plus basse sur 52 semaines": self.low,
            "Variation jour": self.variation_jour(),
            "Variation jour (%)": self.variation_jour_pct(),
            "Volatilité historique": self.calculer_vol_historique(),
            "Maximum Drawdown (%)": self.maximum_drawdown() * 100,
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
