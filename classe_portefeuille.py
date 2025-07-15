import numpy as np
from datetime import datetime, timedelta
from classe_actifs import Actifs
import yfinance as yf

class Portefeuille:
    def __init__(self, nom):
        self.nom = nom
        self.actifs = []            # Liste des objets Action
        self.quantites = []         # Quantités associées aux actions
        self.prix_achats = {}       # Dictionnaire ticker -> prix d'achat moyen
        self.date_achat_portefeuille = None  # Date du premier achat dans le portefeuille
        self.reference = None       # Référence pour comparaison (objet Index)

    def get_prix_achat(self, ticker, date_achat):
        try:
            # Récupère le prix de clôture ajusté à la date donnée
            df = yf.download(ticker, start=date_achat.strftime("%Y-%m-%d"), end=(date_achat + timedelta(days=1)).strftime("%Y-%m-%d"))
            if df.empty:
                return None
            prix = df['Adj Close'].iloc[0]
            return prix
        except Exception as e:
            print(f"Erreur récupération prix pour {ticker} : {e}")
            return None

    def ajouter_action(self, action, quantite: int, date_achat):
        prix_achat = self.get_prix_achat(action.ticker, date_achat)
        if prix_achat is None:
            print(f"Impossible de récupérer le prix d'achat pour {action.ticker} à la date {date_achat.strftime('%Y-%m-%d')}.")
            return

        if action in self.actifs:
            idx = self.actifs.index(action)
            ancienne_qte = self.quantites[idx]
            ancien_prix = self.prix_achats.get(action.ticker, 0)
            # Calcul du prix d'achat moyen pondéré
            nouveau_prix = (ancien_prix * ancienne_qte + prix_achat * quantite) / (ancienne_qte + quantite)
            self.quantites[idx] += quantite
            self.prix_achats[action.ticker] = nouveau_prix
        else:
            self.actifs.append(action)
            self.quantites.append(quantite)
            self.prix_achats[action.ticker] = prix_achat

        if self.date_achat_portefeuille is None or date_achat < self.date_achat_portefeuille:
            self.date_achat_portefeuille = date_achat

        print(f"Action {action.ticker} ajoutée avec {quantite} unités au prix d'achat {prix_achat:.2f} (date {date_achat.strftime('%Y-%m-%d')})")

    def retirer_action(self, ticker, quantite):
        for i, action in enumerate(self.actifs):
            if action.ticker == ticker:
                if self.quantites[i] < quantite:
                    print(f"Quantité à retirer ({quantite}) supérieure à la quantité détenue ({self.quantites[i]}).")
                    return
                self.quantites[i] -= quantite
                print(f"{quantite} actions {ticker} retirées du portefeuille.")
                if self.quantites[i] == 0:
                    # Suppression complète de l'action si plus de quantité
                    self.actifs.pop(i)
                    self.quantites.pop(i)
                    self.prix_achats.pop(ticker, None)
                return
        print(f"L'action {ticker} n'est pas présente dans le portefeuille.")

    def afficher_portefeuille(self):
        print(f"Portefeuille : {self.nom}")
        if not self.actifs:
            print("Portefeuille vide.")
            return
        for action, quantite in zip(self.actifs, self.quantites):
            prix_achat = self.prix_achats.get(action.ticker, 0)
            print(f"Action : {action.ticker} - Quantité : {quantite} - Prix achat moyen : {prix_achat:.2f}")

    def performance_depuis_achat(self):
        if not self.actifs or self.date_achat_portefeuille is None:
            print("Aucune action ou date d'achat disponible pour calculer la performance.")
            return

        prix_total_achat = 0
        valeur_actuelle = 0
        for action, quantite in zip(self.actifs, self.quantites):
            prix_achat = self.prix_achats.get(action.ticker, 0)
            prix_total_achat += prix_achat * quantite
            prix_courant = action.get_prix_actuel()
            valeur_actuelle += prix_courant * quantite

        rendement = (valeur_actuelle - prix_total_achat) / prix_total_achat
        print(f"Performance depuis la date d'achat ({self.date_achat_portefeuille.strftime('%Y-%m-%d')}): {rendement * 100:.2f} %")

    def afficher_performance(self):
        if not self.actifs:
            print("Portefeuille vide.")
            return
        print("Performance du portefeuille :")
        # Calcul simple : somme des performances pondérées par la quantité
        for action, quantite in zip(self.actifs, self.quantites):
            prix_achat = self.prix_achats.get(action.ticker, 0)
            prix_courant = action.get_prix_actuel()
            rendement = (prix_courant - prix_achat) / prix_achat if prix_achat > 0 else 0
            print(f"Action {action.ticker} : Rendement {rendement*100:.2f} % avec {quantite} unités")

    def comparer_a_reference(self):
        if self.reference is None:
            print("Aucun index de référence défini.")
            return

        print(f"Comparaison du portefeuille '{self.nom}' à l'index {self.reference.ticker} :")
        self.performance_depuis_achat()
        rendement_index = self.reference.get_rendement_depuis(self.date_achat_portefeuille)
        if rendement_index is None:
            print("Impossible de récupérer le rendement de l'index.")
            return
        print(f"Rendement de l'index depuis la date d'achat : {rendement_index*100:.2f} %")

    def ratio_sharpe(self):
        # Calcul simplifié du ratio de Sharpe basé sur les rendements quotidiens
   

        if not self.actifs:
            print("Portefeuille vide.")
            return 0.0

        rendements = []
        for action, quantite in zip(self.actifs, self.quantites):
            series_rendement = action.get_rendements_quotidiens()  # À implémenter dans Action
            rendements.append(series_rendement * quantite)

        # Somme pondérée des rendements
        rendements_portefeuille = np.sum(rendements, axis=0) / sum(self.quantites)

        esp_rend = np.mean(rendements_portefeuille)
        vol = np.std(rendements_portefeuille)

        if vol == 0:
            return 0.0
        sharpe = esp_rend / vol
        return sharpe
