import os
import sqlite3
from datetime import datetime

from oblind.constants import CONFIG_DIR


def create_db():
    """
    Fonction créant la base de donnees POKER en SQL (3 tables Joueurs, Parties, Résultats)
    """
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)

    connection = sqlite3.connect(os.path.join(CONFIG_DIR, "POKER.db"))

    cursor = connection.cursor()
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS Joueurs(
            Joueurs_Id	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
            Nom	TEXT,
            Prenom	TEXT,
            DateAjout	INTEGER,
            Avatar	TEXT
            )
            """)
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS Parties (
            Parties_Id	INTEGER PRIMARY KEY AUTOINCREMENT,
            Date	TEXT,
            NbJetonCave	INTEGER,
            PrixCave	INTEGER,
            Recave  INTEGER
            )
            """)
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS Resultats (
            ID	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
            Joueur_Id	INTEGER,
            Partie_Id	INTEGER,
            JetonFinPartie	INTEGER,
            NbRecave INTEGER,
            FOREIGN KEY(Partie_Id) REFERENCES Parties(Parties_Id),
            FOREIGN KEY(Joueur_Id) REFERENCES Joueurs(Joueurs_Id)
            )
            """)
    connection.commit()
    connection.close()


def add_player_db(name, lastname, date, avatar):
    """
    Fonction ajoutant un joueur à la base de données
    """

    if not os.path.isfile(os.path.join(CONFIG_DIR, "POKER.db")):
        create_db()
    connection = sqlite3.connect(os.path.join(CONFIG_DIR, "POKER.db"))
    cursor = connection.cursor()
    cursor.execute("INSERT INTO Joueurs (Nom,Prenom,DateAjout,Avatar) VALUES (?,?,?,?)",
                   (name, lastname, date, avatar))
    connection.commit()
    connection.close()


def modify_player_db(name, lastname, avatar, id_p):
    """
    Fonction modifiant un joueur à la base de données
    """
    connection = sqlite3.connect(os.path.join(CONFIG_DIR, "POKER.db"))
    cursor = connection.cursor()
    cursor.execute("UPDATE Joueurs SET Nom = ?, Prenom = ?, Avatar = ? WHERE Joueurs_Id = ?",
                   (name, lastname, avatar, id_p))
    connection.commit()
    connection.close()


def delete_player_db(id_p):
    """
    Fonction supprimant un joueur de la base de données
    """
    connection = sqlite3.connect(os.path.join(CONFIG_DIR, "POKER.db"))
    cursor = connection.cursor()
    cursor.execute("DELETE FROM Joueurs WHERE Joueurs_Id = ?",
                   (id_p,))
    connection.commit()
    connection.close()


def list_players_db():
    """
    Fonction retournant un dictionnaire des joueurs présents dans la BD
    clé : id du joueur

    valeurs : (clé,valeur)
              ("name", nom) , → str
              ("lastname", prénom) , → str
              ("date_create", date de creation), → str
              ("avatar", chemin du fichier image sur le disque représentant l'avatar), → str
              ("seated", participation à la partie) → bool par défaut False
    """
    players = {}
    if not os.path.isfile(os.path.join(CONFIG_DIR, "POKER.db")):
        create_db()
    connection = sqlite3.connect(os.path.join(CONFIG_DIR, "POKER.db"))
    cursor = connection.cursor()
    p_list = cursor.execute("SELECT Joueurs_Id,Nom,Prenom,DateAjout,Avatar FROM Joueurs").fetchall()
    connection.close()
    for x in p_list:
        players[x[0]] = {"name": x[1], "lastname": x[2], "date_create": x[3], "avatar": x[4], "seated": False}
    return players


def list_players_game(id_game):
    """
    Fonction pour récupérer une liste triée par nb de jetons descendants
    des joueurs participants et jetons restants à une partie
    """
    players = []
    connection = sqlite3.connect(os.path.join(CONFIG_DIR, "POKER.db"))
    cursor = connection.cursor()
    p_list = cursor.execute("""
                    SELECT Joueurs_Id, Prenom, JetonFinPartie, NbRecave
                    FROM Resultats 
                    INNER JOIN Joueurs ON Resultats.Joueur_Id = Joueurs.Joueurs_Id 
                    WHERE Partie_Id = ?""", (id_game,)).fetchall()
    connection.close()
    for x in p_list:
        players.append((x[0], x[1], x[2], x[3]))
    sort_players_game = sorted(players, key=lambda score: score[2], reverse=True)
    return sort_players_game


def save_start_game_db(buy_in, chips, list_player, recave):
    """
    Fonction de mise à jour des tables Parties et Résultats de la BD
    pour ajouter la nouvelle partie et les joueurs participants
    """
    date_game = datetime.now().strftime("%d %m %Y %H:%M")

    connection = sqlite3.connect(os.path.join(CONFIG_DIR, "POKER.db"))
    cursor = connection.cursor()
    cursor.execute("INSERT INTO Parties (Date, NbJetonCave, PrixCave, Recave) VALUES (?,?,?,?)",
                   (date_game, chips, buy_in, recave))
    id_game = cursor.lastrowid

    nb_recave = None
    if recave:
        nb_recave = 0

    for j in list_player:
        cursor.execute("INSERT INTO Resultats (Joueur_Id, Partie_Id, JetonFinPartie,  NbRecave) VALUES (?,?,?,?)",
                       (j, id_game, 0, nb_recave))
    connection.commit()
    connection.close()

    return id_game


def save_add_cave(nb_recave ,player, game):
    """
    Fonction pour mettre à jour la table Resultats après une recave
    :param player:
    :param game:
    """
    connection = sqlite3.connect(os.path.join(CONFIG_DIR, "POKER.db"))
    cursor = connection.cursor()
    cursor.execute("""UPDATE Resultats
                   SET NbRecave = ?
                   WHERE Joueur_Id = ? AND Partie_Id = ?""", (nb_recave, player, game))
    connection.commit()
    connection.close()


def save_result_db(nb_chip, player, game):
    """
    Fonction de mise à jour de la BD de la table résultats
    """

    connection = sqlite3.connect(os.path.join(CONFIG_DIR, "POKER.db"))
    cursor = connection.cursor()
    cursor.execute("""UPDATE Resultats
                   SET JetonFinPartie = ?
                   WHERE Joueur_Id = ? AND Partie_Id = ?""", (nb_chip, player, game))
    connection.commit()
    connection.close()


#
def cave_info(parties_id):
    """
    Fonction pour récupérer le nombre de jetons d'une partie et la valeur de cave correspondante
    """
    connection = sqlite3.connect(os.path.join(CONFIG_DIR, "POKER.db"))
    cursor = connection.cursor()
    _list = cursor.execute("""
                    SELECT Date, NbJetonCave, PrixCave, Parties_Id, Recave
                    FROM Parties
                    WHERE Parties_Id = ?""", (parties_id,)).fetchall()
    connection.commit()
    connection.close()
    return _list[0]


def list_game():
    """
    Fonction pour récupérer une liste des parties de la BD
    """
    connection = sqlite3.connect(os.path.join(CONFIG_DIR, "POKER.db"))
    cursor = connection.cursor()
    _list = cursor.execute("""SELECT Parties_Id, Date FROM Parties""").fetchall()
    connection.commit()
    connection.close()
    return _list
