import sqlite3

from flask import g, render_template

db_file = "approot/app.db"


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(db_file)
        g.db.row_factory = sqlite3.Row
    return g.db


def display_tables():
    conn = get_db()
    sql = conn.cursor()
    stmt = """
        SELECT name FROM sqlite_schema
        WHERE 
            type ='table' AND 
            name NOT LIKE 'sqlite_%';
    """
    tables = sql.execute(stmt)
    results = {}

    for row in tables.fetchall():
        name = row[0]
        cols = sql.execute(f'select name from pragma_table_info("{name}")').fetchall()
        rows = sql.execute(f"SELECT * FROM  {name}").fetchall()
        results[name] = {"rows":[dict(r) for r in rows], "cols": [c[0] for c in cols]}
    return render_template("tables.html", tables=results)
