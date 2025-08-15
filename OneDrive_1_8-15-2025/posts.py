from .connection import get_db


def create_posts_table():
    connection = get_db()
    sql = connection.cursor()
    stmt = """
        CREATE TABLE IF NOT EXISTS posts 
        (
        post_id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        content TEXT
        ) 
    """
    sql.execute(stmt)


def insert_post(title, content):
    connection = get_db()
    sql = connection.cursor()

    stmt = """
        INSERT INTO posts (title, content) VALUES (?, ?)
    """
    args = [title, content]

    sql.execute(stmt, args)
    connection.commit()

    return sql.lastrowid

def select_all_posts():
    connection = get_db()
    sql = connection.cursor()
    result = sql.execute("SELECT * FROM posts ORDER BY post_id DESC")
    return result.fetchall()

def select_post_by_id(post_id):
    connection = get_db()
    sql = connection.cursor()
    stmt = "SELECT * FROM posts WHERE post_id = ?"
    args = [post_id]
    result = sql.execute(stmt, args)
    post = result.fetchone()
    return post