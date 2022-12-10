import os
import sqlite3
from datetime import datetime

from oblind.constants import CONFIG_DIR


# creation de la base de donnees POKER (table Joueurs,Parties,Resultats)
def create_db():
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
            PrixCave	INTEGER
            )
            """)
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS Resultats (
            ID	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
            Joueur_Id	INTEGER,
            Partie_Id	INTEGER,
            JetonFinPartie	INTEGER,
            FOREIGN KEY(Partie_Id) REFERENCES Parties(Parties_Id),
            FOREIGN KEY(Joueur_Id) REFERENCES Joueurs(Joueurs_Id)
            )
            """)
    connection.commit()
    connection.close()


def add_player_db(name, lastname, date, avatar):
    if not os.path.isfile(os.path.join(CONFIG_DIR, "POKER.db")):
        create_db()
    connection = sqlite3.connect(os.path.join(CONFIG_DIR, "POKER.db"))
    cursor = connection.cursor()
    cursor.execute("INSERT INTO Joueurs (Nom,Prenom,DateAjout,Avatar) VALUES (?,?,?,?)",
                   (name, lastname, date, avatar))
    connection.commit()
    connection.close()


def modify_player_db(name, lastname, avatar, id_p):
    connection = sqlite3.connect(os.path.join(CONFIG_DIR, "POKER.db"))
    cursor = connection.cursor()
    cursor.execute("UPDATE Joueurs SET Nom = ?, Prenom = ?, Avatar = ? WHERE Joueurs_Id = ?",
                   (name, lastname, avatar, id_p))
    connection.commit()
    connection.close()


def delete_player_db(id_p):
    connection = sqlite3.connect(os.path.join(CONFIG_DIR, "POKER.db"))
    cursor = connection.cursor()
    cursor.execute("DELETE FROM Joueurs WHERE Joueurs_Id = ?",
                   (id_p,))
    connection.commit()
    connection.close()


# fonction pour recuperer un dictionnaire des joueurs presents dans la BD POKER
# cle id du joueur
# valeurs : (cle,valeur)
#           ("name", nom) , -> str
#           ("lastname", prenom) , -> str
#           ("date_create", date de creation),
#           ("avatar", chemin du fichier image sur le disque representant l'avatar), -> str
#           ("seated", participation à la partie) -> bool par defaut False

def list_players_db():
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


# fonction pour récuperer une liste triée par nb de jetons des joueurs participants et jetons restants à une partie "id_game"

def list_players_game(id_game):
    players = []
    connection = sqlite3.connect(os.path.join(CONFIG_DIR, "POKER.db"))
    cursor = connection.cursor()
    p_list = cursor.execute("""
                    SELECT Joueurs_Id, Prenom, JetonFinPartie
                    FROM Resultats 
                    INNER JOIN Joueurs ON Resultats.Joueur_Id = Joueurs.Joueurs_Id 
                    WHERE Partie_Id = ?"""
                            , (id_game,)).fetchall()
    connection.close()
    for x in p_list:
        players.append((x[0], x[1], x[2]))
    sort_players_game = sorted(players, key=lambda score: score[2], reverse=True)
    return sort_players_game


# Fonction de mise à jour de la BD des tables Parties et Resultats
# pour ajouter la nouvelle partie et les joueurs participants
def save_start_game_db(buy_in, chips, list_player):
    date_game = datetime.now().strftime("%d %m %Y %H:%M")

    connection = sqlite3.connect(os.path.join(CONFIG_DIR, "POKER.db"))
    cursor = connection.cursor()
    cursor.execute("INSERT INTO Parties (Date, NbJetonCave, PrixCave) VALUES (?,?,?)",
                   (date_game, chips, buy_in))
    id_game = cursor.lastrowid

    for j in list_player:
        cursor.execute("INSERT INTO Resultats (Joueur_Id, Partie_Id, JetonFinPartie) VALUES (?,?,?)",
                       (j, id_game, 0))
    connection.commit()
    connection.close()

    return id_game


# Fonction de mise à jour de la BD de la tables resultats
# Arguments : Joueur_Id, Partie_Id, Nb_Jeton
def save_result_db(nb_chip, player, game):
    connection = sqlite3.connect(os.path.join(CONFIG_DIR, "POKER.db"))
    cursor = connection.cursor()
    cursor.execute("""UPDATE Resultats
                   SET JetonFinPartie = ?
                   WHERE Joueur_Id = ? AND Partie_Id = ?"""
                   , (nb_chip, player, game))
    connection.commit()
    connection.close()


# Fonction pour recuperer le nombre de jetons d'une partie et la valeur de cave correspondante
def cave_info(Parties_Id):
    connection = sqlite3.connect(os.path.join(CONFIG_DIR, "POKER.db"))
    cursor = connection.cursor()
    _list = cursor.execute("""
                    SELECT Date, NbJetonCave, PrixCave, Parties_Id
                    FROM Parties
                    WHERE Parties_Id = ?"""
                           , (Parties_Id,)).fetchall()
    connection.commit()
    connection.close()
    return _list[0]


# Fonction pour recuperer une liste des parties de la DB
def list_game():
    connection = sqlite3.connect(os.path.join(CONFIG_DIR, "POKER.db"))
    cursor = connection.cursor()
    _list = cursor.execute("""SELECT Parties_Id, Date FROM Parties""").fetchall()
    connection.commit()
    connection.close()
    return _list
