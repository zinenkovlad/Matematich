import sqlite3
from datetime import datetime
from utils import Player


class SQLighter:
    def __init__(self, database):
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

    def clean_query(self, query):
        return [x[0] for x in self.cursor.execute(query).fetchall()]

    def get_registered_chats(self):
        return self.clean_query("SELECT name FROM sqlite_master WHERE type='table'")

    def get_registered_users(self, chat):
        return self.clean_query("SELECT user_id FROM {}".format(chat))

    def register_user(self, chat, user_id, username):
        self.cursor.execute(
            """INSERT INTO {} (user_id, username, n_pes, n_matematich) VALUES(?, ?, ?, ?)""".format(chat),
            (user_id, username, 0, 0)
        )
        self.connection.commit()

    def create_new_chat_tables(self, chat, user_id, username):
        self.cursor.execute(
            """
                CREATE TABLE {} (
                    `id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                    `user_id`	INTEGER NOT NULL UNIQUE,
                    `username`	TEXT NOT NULL,
                    `n_pes`	INTEGER NOT NULL,
                    `n_matematich`	INTEGER NOT NULL
                )
            """.format(chat)
        )
        self.register_user(chat, user_id, username)
        self.cursor.execute("""CREATE TABLE {} (`day`	INTEGER NOT NULL)""".format(chat + '_played'))
        self.cursor.execute(""" INSERT INTO {} (`day`) VALUES(-1)""".format(chat + '_played'))
        self.connection.commit()

    def is_played(self, chat):
        """ Did users played today in this chat? """
        day_played = self.clean_query("SELECT day FROM {}_played".format(chat))[0]
        current_day = datetime.today().day
        return current_day == day_played

    def count_users(self, chat):
        """ Count number of users in chat"""
        users = self.cursor.execute("SELECT * FROM {}".format(chat)).fetchall()
        return len(users)

    def get_winner(self, chat, id_winner):
        """ Gets one user """
        winner = self.cursor.execute("SELECT * FROM {0} WHERE id = {1}".format(chat, id_winner)).fetchall()[0]
        return Player(*winner)

    def get_losers(self, chat, id_winner):
        """ Gets all users except one"""
        losers = self.cursor.execute("SELECT * FROM {0} WHERE NOT id = {1}".format(chat, id_winner)).fetchall()
        return [Player(*loser) for loser in losers]

    def update_is_played(self, chat):
        """ Updates is played table """
        self.cursor.execute("UPDATE {0} SET {1} = {2}".format(chat + "_played", "`day`", datetime.today().day))
        self.connection.commit()

    def update_stats(self, chat, winner, losers):
        """ Increments corresponding columns for winner and losers """
        winner_id = winner.id
        losers_id = [loser.id for loser in losers]
        self.cursor.execute("UPDATE {0} SET n_matematich = n_matematich + 1 WHERE id = {1}".format(chat, winner_id))
        self.connection.commit()
        for loser_id in losers_id:
            self.cursor.execute("UPDATE {0} SET n_pes = n_pes + 1 WHERE id = {1}".format(chat, loser_id))
            self.connection.commit()

    def update_tables(self, chat, winner, losers):
        self.update_is_played(chat)
        self.update_stats(chat, winner, losers)

    def get_stats(self, chat):
        stats = self.cursor.execute("SELECT  username, n_matematich FROM {} ORDER BY n_matematich DESC ".format(chat))
        return "\n".join([stat[0] + " - " + str(stat[1]) for stat in stats])

    def nullify_is_played(self, chat):
        """ Nullifies date when played """
        self.cursor.execute("UPDATE {0} SET {1} = {2}".format(chat + "_played", "`day`", 0))
        self.connection.commit()

    def close(self):
        """ Closes connection with DB"""
        self.connection.close()
