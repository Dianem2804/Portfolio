import sqlite3
from datetime import date

class DatabasePortefeuille:
    def __init__(self, db_path="portefeuille.db"):
        self.conn = sqlite3.connect(db_path)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS portefeuilles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT UNIQUE NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                portefeuille_id INTEGER,
                ticker TEXT,
                quantite INTEGER,
                prix_achat REAL,
                date_achat TEXT,
                FOREIGN KEY (portefeuille_id) REFERENCES portefeuilles(id)
            )
        ''')
        self.conn.commit()

    def ajouter_portefeuille(self, nom):
        cursor = self.conn.cursor()
        cursor.execute('INSERT OR IGNORE INTO portefeuilles (nom) VALUES (?)', (nom,))
        self.conn.commit()

    def get_portefeuille_id(self, nom):
        cursor = self.conn.cursor()
        cursor.execute('SELECT id FROM portefeuilles WHERE nom = ?', (nom,))
        res = cursor.fetchone()
        return res[0] if res else None

    def ajouter_action(self, nom_portefeuille, ticker, quantite, prix_achat, date_achat):
        portefeuille_id = self.get_portefeuille_id(nom_portefeuille)
        if portefeuille_id is None:
            raise ValueError("Portefeuille non trouvé")
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO actions (portefeuille_id, ticker, quantite, prix_achat, date_achat)
            VALUES (?, ?, ?, ?, ?)
        ''', (portefeuille_id, ticker, quantite, prix_achat, date_achat.isoformat()))
        self.conn.commit()

    def get_actions(self, nom_portefeuille):
        portefeuille_id = self.get_portefeuille_id(nom_portefeuille)
        if portefeuille_id is None:
            return []
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT ticker, quantite, prix_achat, date_achat FROM actions WHERE portefeuille_id = ?
        ''', (portefeuille_id,))
        return cursor.fetchall()
