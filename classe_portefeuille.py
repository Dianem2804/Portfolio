import pandas as pd
from datetime import datetime
from database_portefeuille import DatabasePortefeuille
from classe_actifs import Actifs
from classe_index import Index  # Ton indice de référence

DATA_FILE = "portefeuille.csv"

class Portefeuille:
    def __init__(self, nom):
        self.nom = nom
        self.actifs = []
        self.quantites = []
        self.dates_achat = []
        self.prix_achats = {}
        self.date_achat_portefeuille = None
        self.reference = None  # Un objet Index pour la référence
        self.db = DatabasePortefeuille()
        self.db.ajouter_portefeuille(nom)

    def get_prix_achat(self, ticker: str, date_achat: datetime):
        # TODO: remplacer par vrai prix d'achat selon date
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

        df = pd.DataFrame(data)
        df.to_csv(DATA_FILE, index=False)
        print(f"Portefeuille sauvegardé dans {DATA_FILE}")

    def charger_portefeuille_depuis_fichier(self):
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
                action = Actifs(ticker)
                self.ajouter_action(action, quantite, date_achat)

            print(f"Portefeuille chargé depuis {DATA_FILE}")
        except FileNotFoundError:
            print(f"Aucun fichier {DATA_FILE} trouvé.")
        except Exception as e:
            print(f"Erreur lors du chargement du portefeuille : {e}")

    def afficher_performance(self):
        data = []
        for i, actif in enumerate(self.actifs):
            quantite = self.quantites[i]
            prix_achat = self.prix_achats.get(actif.ticker, 0)
            # Ici il faudrait récupérer la valeur actuelle de l’actif
            valeur_actuelle = actif.get_prix_actuel()  # Exemple, à implémenter dans classe Actifs
            performance = (valeur_actuelle - prix_achat) / prix_achat if prix_achat > 0 else 0
            data.append({
                "Ticker": actif.ticker,
                "Quantité": quantite,
                "Prix Achat": prix_achat,
                "Valeur Actuelle": valeur_actuelle,
                "Performance": performance
            })
        return pd.DataFrame(data)

    def comparer_a_reference(self, reference: Index):
        self.reference = reference
        perf_portefeuille = self.afficher_performance()
        # Supposons que reference a une méthode get_performance() qui renvoie un DataFrame similaire
        perf_reference = reference.get_performance()

        # Ici on fait un join sur ticker ou sur la date selon ta structure
        # Exemple simple, jointure par 'Ticker'
        comparaison = pd.merge(perf_portefeuille, perf_reference, on="Ticker", suffixes=('_Portefeuille', '_Reference'))
        return comparaison

    def ratio_sharpe(self, taux_sans_risque=0.01):
        """
        Calcul simple du ratio de Sharpe annualisé.
        Hypothèse: on a une méthode get_rendements() qui renvoie une série pandas des rendements journaliers.
        """

        # On calcule la valeur totale du portefeuille au fil du temps, puis les rendements quotidiens
        try:
            rendements = self.get_rendements()  # A implémenter: retourne pd.Series des rendements journaliers
            excess_returns = rendements - taux_sans_risque / 252  # Approx 252 jours de bourse/an
            sharpe_ratio = excess_returns.mean() / excess_returns.std() * (252 ** 0.5)
            return sharpe_ratio
        except Exception as e:
            print(f"Erreur dans le calcul du ratio de Sharpe: {e}")
            return None

    # Exemple d'implémentation d'une méthode get_rendements() simplifiée
    def get_rendements(self):
        """
        Calcule les rendements journaliers du portefeuille en fonction des prix actuels des actifs.
        Ici on suppose que chaque actif a une méthode get_historique_prix() qui renvoie une série de prix quotidiens.
        """

        # Pour chaque actif, récupérer l'historique des prix et multiplier par la quantité
        df_valeurs = None
        for i, actif in enumerate(self.actifs):
            quantite = self.quantites[i]
            try:
                prix_hist = actif.get_historique_prix()  # pd.Series indexée par date
                valeur_actif = prix_hist * quantite
                if df_valeurs is None:
                    df_valeurs = valeur_actif.to_frame(name=actif.ticker)
                else:
                    df_valeurs = df_valeurs.join(valeur_actif.to_frame(name=actif.ticker), how='outer')
            except Exception as e:
                print(f"Erreur récupération historique prix pour {actif.ticker}: {e}")

        if df_valeurs is None:
            raise ValueError("Pas d'actifs ou données historiques disponibles")

        df_valeurs = df_valeurs.fillna(method='ffill').fillna(method='bfill')
        df_valeurs['Total'] = df_valeurs.sum(axis=1)

        rendements = df_valeurs['Total'].pct_change().dropna()
        return rendements
