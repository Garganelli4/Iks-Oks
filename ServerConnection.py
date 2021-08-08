import sqlite3  # used to talk to the SQL database


class SqlServerConnection():
    def __init__(self, databaseCredential="application.db"):
        # connect with the database 
        self.connection = sqlite3.connect(databaseCredential, check_same_thread=False)
        self.setup_db()


    def setup_db(self):
        # this will create the users and leader board table in the sql database if they dont already exists
        c = self.connection.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username VARCHAR(25) NOT NULL UNIQUE,
            password VARCHAR(25) NOT NULL,
            wins INT UNSIGNED DEFAULT 0,
            loses INT UNSIGNED DEFAULT 0,
            games_played int UNSIGNED DEFAULT 0
        );
        """)
        self.connection.commit()
