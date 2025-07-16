import pandas as pd
from datetime import date
import os

class DatabasePortefeuille:
    def __init__(self, filename="portfolios.csv"):
        self.filename = filename
        if os.path.exists(self.filename):
            self.df = pd.read_csv(self.filename, parse_dates=["date_achat"])
        else:
            self.df = pd.DataFrame(columns=["nom_portefeuille", "ticker", "quantite", "prix_achat", "date_achat"])

    def sauvegarder(self):
        self.df.to_csv(self.filename, index=False)

    def ajouter_portefeuille(self, nom):
        # Pas besoin de ligne spéciale, on crée portefeuille à la création d'action
        if nom not in self.df["nom_portefeuille"].unique():
            # Juste une méthode pour avoir un nom reconnu, sans action
            pass

    def get_all_portfolios(self):
        return list(self.df["nom_portefeuille"].unique())

    def ajouter_action(self, nom_portefeuille, ticker, quantite, prix_achat, date_achat):
        # Ajouter ligne nouvelle action
        new_row = {
            "nom_portefeuille": nom_portefeuille,
            "ticker": ticker,
            "quantite": quantite,
            "prix_achat": prix_achat,
            "date_achat": pd.to_datetime(date_achat)
        }
        self.df = pd.concat([self.df, pd.DataFrame([new_row])], ignore_index=True)
        self.sauvegarder()

    def get_actions(self, nom_portefeuille):
        subset = self.df[self.df["nom_portefeuille"] == nom_portefeuille]
        # Retourne liste de tuples (ticker, quantite, prix_achat, date_achat)
        return list(subset[["ticker", "quantite", "prix_achat", "date_achat"]].itertuples(index=False, name=None))

    def retirer_action(self, nom_portefeuille, ticker, quantite):
        # Retirer quantité dans l'ordre ancienneté date_achat
        subset = self.df[(self.df["nom_portefeuille"] == nom_portefeuille) & (self.df["ticker"] == ticker)]
        subset = subset.sort_values(by="date_achat")
        
        qty_to_remove = quantite
        indices_to_drop = []
        for idx, row in subset.iterrows():
            if qty_to_remove <= 0:
                break
            if row["quantite"] <= qty_to_remove:
                qty_to_remove -= row["quantite"]
                indices_to_drop.append(idx)
            else:
                # Modifier la quantité restante
                self.df.at[idx, "quantite"] = row["quantite"] - qty_to_remove
                qty_to_remove = 0

        # Supprimer les lignes où quantité totalement retirée
        self.df = self.df.drop(indices_to_drop)
        self.sauvegarder()
