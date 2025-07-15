from classe_actifs import Actifs
from classe_index import Index
from classe_portefeuile import Portefeuille
from datetime import datetime  
import yfinance as yf

def menu():
    print("\nMenu :")
    print("1) Consulter une action")
    print("2) Créer un portefeuille")
    print("3) Ajouter/retirer des actions au portefeuille")
    print("4) Consulter performance / rendements du portefeuille")
    print("5) Consulter un Index")
    print("6) Comparer rendements du portefeuille à un Index")
    print("7) Metrics du portefeuille (ex: ratio de Sharpe)")
    print("0) Quitter")

def main():
    portefeuille = None

    while True:
        menu()
        choix = input("Votre choix : ")

        match choix:
            case "1":
                ticker = input("Ticker de l'action : ")
                actifs = Actifs(ticker)
                actifs.afficher_infos()

            case "2":
                nom = input("Nom du portefeuille : ")
                portefeuille = Portefeuille(nom)
                print(f"Portefeuille '{nom}' créé.")

            case "3":
                if portefeuille is None:
                    print("Créez d'abord un portefeuille (option 2).")
                continue
                actifs_ticker = input("Ticker de l'action à ajouter/retirer : ")
                actifs = Actifs(actifs_ticker)
                op = input("Ajouter (a) ou retirer (r) ? ")

                if op not in ['a', 'r']:
                    print("Option invalide. Tapez 'a' pour ajouter ou 'r' pour retirer.")
                    continue

                try:
                    quantite = int(input("Quantité : "))
                    if quantite <= 0:
                        print("La quantité doit être un entier strictement positif.")
                        continue
                except ValueError:
                    print("Quantité invalide (entrez un entier).")
                    continue

                if op == 'a':
                    date_str = input("Date d'achat (YYYY-MM-DD) : ")
                    try:
                        date_achat = datetime.strptime(date_str, "%Y-%m-%d")
                    except ValueError:
                        print("Format de date invalide. Utilisez YYYY-MM-DD.")
                        continue

                    portefeuille.ajouter_actifs(actifs, quantite, date_achat)

                elif op == 'r':
                    portefeuille.retirer_actifs(actifs_ticker, quantite)

            case "4":
                if portefeuille is None:
                    print("Créez d'abord un portefeuille (option 2).")
                    continue
                portefeuille.afficher_performance()

            case "5":
                ticker_index = input("Ticker de l'Index : ")
                index = Index(ticker_index)
                index.afficher_info()

            case "6":
                if portefeuille is None:
                    print("Créez d'abord un portefeuille (option 2).")
                    continue
                ticker_index = input("Ticker de l'Index : ")
                index = Index(ticker_index)
                portefeuille.comparer_a_reference(index)

            case "7":
                if portefeuille is None:
                    print("Créez d'abord un portefeuille (option 2).")
                    continue
                ratio = portefeuille.ratio_sharpe()
                print(f"Ratio de Sharpe du portefeuille : {ratio:.4f}")

            case "0":
                print("Au revoir.")
                break

            case _:
                print("Choix invalide. Veuillez entrer un nombre entre 0 et 7.")

# Appel de la fonction principale
if __name__ == "__main__":
    main()
