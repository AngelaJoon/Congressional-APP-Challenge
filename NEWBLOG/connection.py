import sqlite3

from flask import g

db_file = "app.db"

def get_db():
    connection = g.get('db', 'null')
    if connection == 'null':
        g.db = sqlite3.connect(db_file, detect_types=sqlite3.PARSE_DECLTYPES)
        g.db.row_factory = sqlite3.Row
        return g.db
    else:
        return connection
