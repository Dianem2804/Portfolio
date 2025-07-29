import pandas as pd
from datetime import datetime
from database_portefeuille import DatabasePortefeuille  # Assure-toi que c’est bon
from classe_actifs import Actifs
from classe_index import Index

DATA_FILE = "portefeuille.csv"

class Portefeuille:
    def __init__(self, nom):
        self.nom = nom
        self.actifs = []
        self.quantites = []
        self.dates_achat = []
        self.prix_achats = {}
        self.date_achat_portefeuille = None
        self.reference = None
        self.db = DatabasePortefeuille()
        self.db.ajouter_portefeuille(nom)

    def get_prix_achat(self, ticker: str, date_achat: datetime):
        # Placeholder, à remplacer par vraie récupération
        return 100.0

    def ajouter_action(self, action: Actifs, quantite: int, date_achat: datetime):
        prix_achat = self.get_prix_achat(action.ticker, date_achat)
        if prix_achat is None:
            print(f"Impossible de récupérer le prix d'achat pour {action.ticker} à la date {date_achat.strftime('%Y-%m-%d')}.")
            return

        self.db.ajouter_action(self.nom, action.ticker, quantite, prix_achat, date_achat)

        if action in self.actifs:
            idx = self.actifs.index(action)
            ancienne_qte = self.quantites[idx]
            ancien_prix = self.prix_achats.get(action.ticker, 0)
            nouveau_prix = (ancien_prix * ancienne_qte + prix_achat * quantite) / (ancienne_qte + quantite)
            self.quantites[idx] += quantite
            self.prix_achats[action.ticker] = nouveau_prix
            if date_achat < self.dates_achat[idx]:
                self.dates_achat[idx] = date_achat
        else:
            self.actifs.append(action)
            self.quantites.append(quantite)
            self.dates_achat.append(date_achat)
            self.prix_achats[action.ticker] = prix_achat

        if self.date_achat_portefeuille is None or date_achat < self.date_achat_portefeuille:
            self.date_achat_portefeuille = date_achat

        print(f"Action {action.ticker} ajoutée avec {quantite} unités au prix d'achat {prix_achat:.2f} (date {date_achat.strftime('%Y-%m-%d')})")

    def retirer_action(self, ticker: str, quantite: int):
        """Retirer une quantité d’un actif donné par ticker"""
        # Trouver l’actif correspondant
        index = next((i for i, a in enumerate(self.actifs) if a.ticker == ticker), None)
        if index is None:
            print(f"L'action {ticker} n'est pas dans le portefeuille.")
            return

        if quantite > self.quantites[index]:
            print(f"Impossible de retirer {quantite} unités car seule {self.quantites[index]} est disponible.")
            return

        self.quantites[index] -= quantite
        self.db.retirer_action(self.nom, ticker, quantite)

        if self.quantites[index] == 0:
            del self.actifs[index]
            del self.quantites[index]
            del self.dates_achat[index]
            if ticker in self.prix_achats:
                del self.prix_achats[ticker]

        print(f"{quantite} unités retirées de {ticker}.")

    def save_portefeuille_to_file(self):
        """Sauvegarde le portefeuille dans un fichier CSV"""
        if not self.actifs:
            print("Portefeuille vide, rien à sauvegarder.")
            return

        data = []
        for i in range(len(self.actifs)):
            action = self.actifs[i]
            quantite = self.quantites[i]
            date_achat = self.dates_achat[i]
            data.append({
                "Ticker": action.ticker,
                "Quantité": quantite,
                "Date Achat": date_achat.strftime("%Y-%m-%d")
            })

        df = pd.DataF
