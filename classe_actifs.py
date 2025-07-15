import yfinance as yf
import math
from typing import List
import pandas as pd
import matplotlib.pyplot as plt

#but du code : créer la classe actif, definir les  paramètres et les méthodes 
 
class Actifs : 
    def __init__(self, ticker: str, quantite: int=0, taux_sans_risque: float = 0.02):
        self.ticker = ticker
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
        self.historique_rendements: List[float] = []
       

        self.initialiser_donnees()
        self.afficher_infos()

# extraire les infos de yahoo finance 

    def initialiser_donnees(self):
        try:
            info = yf.Ticker(self.ticker)
            data = info.history(period="5d")  

            self.nom_entreprise = info.info.get("longName", "Inconnu")
            self.secteur = info.info.get("sector", "Inconnu")
            self.volume = info.info.get("volume", 0)
            self.market_cap = info.info.get("marketCap")
            self.industrie = info.info.get("industry")
            self.high = info.info.get("fiftyTwoWeekHigh")
            self.low = info.info.get("fiftyTwoWeekLow")

            self.historique_prix = data["Close"].tolist()

            if len(self.historique_prix) >= 2:
                self.prix_hier = self.historique_prix[-2]
                self.prix_aujourdhui = self.historique_prix[-1]
            elif len(self.historique_prix) == 1:
                self.prix_aujourdhui = self.historique_prix[-1]

            self.calculer_rendements()
        
        except Exception as e:
            print(f"Erreur lors de l'initialisation des données : {e}")

    def afficher_infos(self):
        print(f"Ticker : {self.ticker}")
        print(f"Entreprise : {self.nom_entreprise}")
        print(f"Secteur : {self.secteur}")
        print(f"Prix aujourd'hui : {self.prix_aujourdhui}")
        print(f"Volume : {self.volume}")
        print(f"Market Cap : {self.market_cap}")
        print(f"Industrie : {self.industrie}")
        print(f"Valeur la + haute sur 52 semaines : {self.high}")
        print(f"Valeur la + basse sur 52 semaines : {self.low}")

        
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


# calculer le maximum drawdown ( plus grande perte enregistrée sur une période donnée)
    def maximum_drawdown(self):
        if self.high != 0:
            return (self.high - self.low) / self.high
        else: 
            return 0

from datetime import datetime, timedelta



if __name__ == "__main__":
    while True:
        ticker = input("Entrer un ticker (ou 'exit' pour quitter) : ").upper()

        if ticker == "EXIT":
            print("Programme terminé.")
            break

        try:
            info = yf.Ticker(ticker).info
            if not info or info.get("regularMarketPrice") is None:
                print("Ticker non existant.\n")
            else:
                action = Actifs(ticker)
                print(f"Variation jour : {action.variation_jour():.2f}")
                print(f"Variation jour (%) : {action.variation_jour_pct():.2f}%")
                print(f"Volatilité historique : {action.calculer_vol_historique():.4f}")
                print(f"Maximum Drawdown : {action.maximum_drawdown():.2%}")

                start_date = '2024-01-01'
                end_date = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')

                data = yf.download(ticker, start=start_date, end=end_date)
                if not data.empty:
                    # Graphique des prix de clôture
                    data['Close'].plot(title=f"Clôture {ticker} ({start_date} → {end_date})")
                    plt.xlabel("Date")
                    plt.ylabel("Prix de clôture ($)")
                    plt.grid()
                    plt.tight_layout()
                    plt.show()

                    # Affichage des 5 derniers prix de clôture
                    print("\nDerniers jours de clôture :")
                    print(data[['Close']].tail(5))

                    # Statistiques descriptives
                    print("\nStatistiques descriptives :")
                    print(data['Close'].describe().round(2))

                    # Tableau personnalisé avec les stats Action
                    stats = pd.DataFrame({
                        'Variation jour': [action.variation_jour()],
                        'Variation jour (%)': [action.variation_jour_pct()],
                        'Volatilité historique': [action.calculer_vol_historique()],
                        'Maximum Drawdown (%)': [action.maximum_drawdown() * 100] })
                    print("\nRésumé des statistiques calculées :")
                    print(stats.round(2))

    

                else:
                    print("Pas de données disponibles sur cette période.\n")
        except Exception as e:
            print(f"Erreur lors de la création de l'action : {e}\n")
