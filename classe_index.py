import yfinance as yf
import math
from typing import List

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
            print(f"Erreur lors de l'initialisation des données : {e}")

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
            try : 
                date_debut = datetime.strptime(date_debut, "%Y-%m-%d")
            except ValueError : 
                print ("Format de date invale : {date_debut}. Utilisez 'YYYY-MM-DD'.")
                return None 
            
        if not self.historique_dates or not self.historique_prix : 
            print ("Pas de donées historiques disponibles.")
            return None
        
        index_debut = None
        for i, d in enumerate(self.historique_dates) :
            if d is None : 
                continue
            if d>= date_debut : 
                index_debut = i 
                break
        
        if index_debut is None :
            print (f"Aucune donnée dispo après la date {date_debut.date()}")
            return None 
        
        prix_debut = self.historique_prix[index_debut]
        prix_fin = self.historique_prix[-1]
        
        if prix_debut == 0:
            print ("Prix initial nul, rendement non défini.")
            return None 
        
        rendement = (prix_fin / prix_debut) - 1
        return rendement

    def performance_cumulee(self):
        if not self.historique_prix:
            return 0
        return (self.historique_prix[-1] / self.historique_prix[0]) - 1

    def afficher_infos(self):
        print(f"Index/ETF : {self.nom} ({self.ticker})")
        print(f"Période : {len(self.historique_prix)} jours")
        print(f"Performance cumulée sur la période : {self.performance_cumulee() * 100:.2f}%")
        print(f"Volatilité : {self.volatilite() * 100:.2f}%")
        
if __name__ == "__main__":
    while True:
        ticker = input("Entrer un ticker d'indice (ou 'exit' pour quitter) : ").upper()

        if ticker == "EXIT":
            print("Programme terminé.")
            break
        try:
            info = yf.Ticker(ticker).info
            if not info or info.get("regularMarketPrice") is None:
                print("Ticker non existant.\n")
            else:
                indice = Index(ticker)
                print(f"Variation jour : {indice.variation_jour():.2f}")
                print(f"Variation jour (%) : {indice.variation_jour_pct():.2f}%")
                print(f"Volatilité historique : {indice.calculer_vol_historique():.4f}")
                print(f"Ratio de Sharpe : {indice.calculer_sharpe():.4f}")
                print(f"Maximum Drawdown : {indice.maximum_drawdown():.2%}\n")
        except Exception as e:
            print(f"Erreur lors de la création de l'indice : {e}\n")
