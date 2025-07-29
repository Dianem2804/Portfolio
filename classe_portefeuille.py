import pandas as pd
from datetime import datetime
from database_portefeuille import DatabasePortefeuille  # Assure-toi que cette importation est correcte
from classe_actifs import Actifs  # idem pour ta classe Actifs
from class_index import Index

DATA_FILE = "portefeuille.csv"  # Constante globale pour la sauvegarde

class Portefeuille:
    def __init__(self, nom):
        self.nom = nom
        self.actifs = []
        self.quantites = []
        self.dates_achat = []  # Initialisation des dates d'achat
        self.prix_achats = {}
        self.date_achat_portefeuille = None
        self.reference = None
        self.db = DatabasePortefeuille()
        self.db.ajouter_portefeuille(nom)

    def get_prix_achat(self, ticker: str, date_achat: datetime):
        """
        Méthode pour récupérer le prix d'achat à une date donnée.
        Implémenter la logique ou la récupération réelle ici.
        """
        # Placeholder: remplacer par la vraie récupération du prix à date_achat
        # Exemple : requête à une API ou base de données
        return 100.0  # prix fictif pour illustration

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
            # Mise à jour de la date d'achat si plus ancienne
            if date_achat < self.dates_achat[idx]:
                self.dates_achat[idx] = date_achat
        else:
            self.actifs.append(action)
            self.quantites.append(quantite)
            self.dates_achat.append(date_achat)  # Important : garder cohérence des listes
            self.prix_achats[action.ticker] = prix_achat

        if self.date_achat_portefeuille is None or date_achat < self.date_achat_portefeuille:
            self.date_achat_portefeuille = date_achat

        print(f"Action {action.ticker} ajoutée avec {quantite} unités au prix d'achat {prix_achat:.2f} (date {date_achat.strftime('%Y-%m-%d')})")

    def retirer_action(self, action: Actifs, quantite: int):
        """Retire une quantité d’un actif donné du portefeuille"""
        if action in self.actifs:
            idx = self.actifs.index(action)
            if quantite > self.quantites[idx]:
                print(f"Impossible de retirer {quantite} unités car seule {self.quantites[idx]} est disponible.")
                return
            self.quantites[idx] -= quantite
            # Mise à jour base de données nécessaire (à implémenter dans DatabasePortefeuille)
            self.db.retirer_action(self.nom, action.ticker, quantite)
            if self.quantites[idx] == 0:
                del self.actifs[idx]
                del self.quantites[idx]
                del self.dates_achat[idx]
                if action.ticker in self.prix_achats:
                    del self.prix_achats[action.ticker]
            print(f"{quantite} unités retirées de {action.ticker}.")
        else:
            print(f"L'action {action.ticker} n'est pas dans le portefeuille.")

    def save_portefeuille_to_file(self):
        """Sauvegarde le portefeuille dans un fichier CSV"""
        if not self.actifs or not self.quantites or not self.dates_achat:
            print("Portefeuille vide, rien à sauvegarder.")
            return
        
        data = []
        for i in range(len(self.actifs)):
            try:
                action = self.actifs[i]
                quantite = self.quantites[i]
                date_achat = self.dates_achat[i]
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
            print(f"Portefeuille sauvegardé dans {DATA_FILE}")

    def charger_portefeuille_depuis_fichier(self):
        """Charge les données du portefeuille depuis un fichier CSV"""
        try:
            df = pd.read_csv(DATA_FILE)
            self.actifs.clear()
            self.quantites.clear()
            self.dates_achat.clear()
            self.prix_achats.clear()

            for _, row in df.iterrows():
                ticker = row['Ticker']
                quantite = int(row['Quantité'])
                date_achat = datetime.strptime(row['Date Achat'], "%Y-%m-%d")
                action = Actifs(ticker)  # Assure-toi que la classe Actifs peut s'instancier ainsi
                self.ajouter_action(action, quantite, date_achat)
            print(f"Portefeuille chargé depuis {DATA_FILE}")
        except FileNotFoundError:
            print(f"Aucun fichier {DATA_FILE} trouvé.")
        except Exception as e:
            print(f"Erreur lors du chargement du portefeuille : {e}")
