import numpy as np
from datetime import datetime, timedelta
from classe_actifs import Actifs
import yfinance as yf
import pandas as pd
from database_portefeuille import DatabasePortefeuille

class Portefeuille:
    def __init__(self, nom):
        self.nom = nom
        self.actifs = []            # Liste des objets Actifs
        self.quantites = []         # Quantités associées aux actifs
        self.prix_achats = {}       # Dictionnaire ticker -> prix d'achat moyen pondéré
        self.date_achat_portefeuille = None  # Date du premier achat dans le portefeuille
        self.reference = None       # Référence pour comparaison (objet Index)
        self.db = DatabasePortefeuille()
        self.db.ajouter_portefeuille(nom)
        self.dates_achat = []
        
    def get_prix_achat(self, ticker, date_achat):
        """Récupère le prix de clôture ajusté pour un ticker à une date donnée via yfinance"""
        try:
            start = date_achat.strftime("%Y-%m-%d")
            end = (date_achat + timedelta(days=1)).strftime("%Y-%m-%d")
            df = yf.download(ticker, start=start, end=end, progress=False)
            if df.empty:
                return None
            return df['Adj Close'].iloc[0]
        except Exception as e:
            print(f"Erreur récupération prix pour {ticker} : {e}")
            return None
            
    def save_portefeuille_to_file(port):
        if not port or not isinstance(port, Portefeuille):
            return

        if not port.actifs or not hasattr(port, "quantites") or not hasattr(port, "dates_achat"):
            return

        data = []
        for i in range(len(port.actifs)):
            try:
                action = port.actifs[i]
                quantite = port.quantites[i]
                date_achat = port.dates_achat[i]

                data.append({
                    "Ticker": action.ticker,
                    "Quantité": quantite,
                    "Date Achat": date_achat.strftime("%Y-%m-%d")
            })
            except Exception as e:
                print(f"Erreur lors de la sauvegarde d'une ligne : {e}")
                continue

        if data:
            df = pd.DataFrame(data)
            df.to_csv(DATA_FILE, index=False)

    def ajouter_action(self, action: Actifs, quantite: int, date_achat: datetime):
        """Ajoute un actif avec une quantité et date d'achat"""
        prix_achat = self.get_prix_achat(action.ticker, date_achat)
        if prix_achat is None:
            print(f"Impossible de récupérer le prix d'achat pour {action.ticker} à la date {date_achat.strftime('%Y-%m-%d')}.")
            return
        
        # Ajout en base de données
        self.db.ajouter_action(self.nom, action.ticker, quantite, prix_achat, date_achat)
        
        if action in self.actifs:
            idx = self.actifs.index(action)
            ancienne_qte = self.quantites[idx]
            ancien_prix = self.prix_achats.get(action.ticker, 0)
            # Calcul prix moyen pondéré
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

    def retirer_action(self, ticker: str, quantite: int):
        """Retire une quantité d'un actif du portefeuille"""
        for i, action in enumerate(self.actifs):
            if action.ticker == ticker:
                if self.quantites[i] < quantite:
                    print(f"Quantité à retirer ({quantite}) supérieure à la quantité détenue ({self.quantites[i]}).")
                    return
                self.quantites[i] -= quantite
                print(f"{quantite} actions {ticker} retirées du portefeuille.")
                if self.quantites[i] == 0:
                    # Suppression complète si plus de quantité
                    self.actifs.pop(i)
                    self.quantites.pop(i)
                    self.prix_achats.pop(ticker, None)
                return
        print(f"L'action {ticker} n'est pas présente dans le portefeuille.")

    def afficher_portefeuille(self):
        """Affiche le contenu du portefeuille"""
        print(f"Portefeuille : {self.nom}")
        if not self.actifs:
            print("Portefeuille vide.")
            return
        for action, quantite in zip(self.actifs, self.quantites):
            prix_achat = self.prix_achats.get(action.ticker, 0)
            print(f"Action : {action.ticker} - Quantité : {quantite} - Prix achat moyen : {prix_achat:.2f}")

    def performance_depuis_achat(self):
        """Calcule la performance globale depuis la date du premier achat"""
        if not self.actifs or self.date_achat_portefeuille is None:
            return pd.DataFrame()  # tableau vide

        prix_total_achat = 0
        valeur_actuelle = 0
        for action, quantite in zip(self.actifs, self.quantites):
            prix_achat = self.prix_achats.get(action.ticker, 0)
            prix_total_achat += prix_achat * quantite
            prix_courant = action.get_prix_actuel()
            valeur_actuelle += prix_courant * quantite

        rendement = (valeur_actuelle - prix_total_achat) / prix_total_achat if prix_total_achat > 0 else 0

        df = pd.DataFrame({
            "Date d'achat portefeuille": [self.date_achat_portefeuille.strftime('%Y-%m-%d')],
            "Performance (%)": [round(rendement * 100, 2)]
        })
        return df
        
    def afficher_performance(self):
        """Affiche la performance par actif"""
        if not self.actifs:
            return pd.DataFrame()  # vide si rien

        data = []
        for action, quantite in zip(self.actifs, self.quantites):
            prix_achat = self.prix_achats.get(action.ticker, 0)
            prix_courant = action.get_prix_actuel()
            rendement = (prix_courant - prix_achat) / prix_achat if prix_achat > 0 else 0
            data.append({
                "Ticker": action.ticker,
                "Quantité": quantite,
                "Rendement (%)": round(rendement * 100, 2)
            })
        return pd.DataFrame(data) 

    def comparer_a_reference(self):
        """Compare la performance du portefeuille à un index de référence"""
        if self.reference is None:
            print("Aucun index de référence défini.")
            return

        print(f"Comparaison du portefeuille '{self.nom}' à l'index {self.reference.ticker} :")
        perf_portefeuille = self.performance_depuis_achat()
        print(perf_portefeuille)

        rendement_index = self.reference.get_rendement_depuis(self.date_achat_portefeuille)
        if rendement_index is None:
            print("Impossible de récupérer le rendement de l'index.")
            return
        print(f"Rendement de l'index depuis la date d'achat : {rendement_index*100:.2f} %")

    def ratio_sharpe(self):
        """Calcule un ratio de Sharpe simplifié basé sur les rendements quotidiens"""
        if not self.actifs:
            print("Portefeuille vide.")
            return 0.0

        rendements = []
        for action, quantite in zip(self.actifs, self.quantites):
            series_rendement = action.get_rendements_quotidiens()  # Méthode à implémenter dans Actifs
            if series_rendement is None:
                continue
            rendements.append(series_rendement * quantite)

        if not rendements:
            return 0.0

        # Somme pondérée des rendements
        rendements_portefeuille = np.sum(rendements, axis=0) / sum(self.quantites)

        esp_rend = np.mean(rendements_portefeuille)
        vol = np.std(rendements_portefeuille)

        if vol == 0:
            return 0.0
        sharpe = esp_rend / vol
        return sharpe
