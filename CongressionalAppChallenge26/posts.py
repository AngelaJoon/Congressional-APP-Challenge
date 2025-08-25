from .connection import get_db


def create_posts_table():
   connection = get_db()
   sql = connection.cursor()
   # Create table if missing
   sql.execute("""
       CREATE TABLE IF NOT EXISTS posts (
           post_id INTEGER PRIMARY KEY AUTOINCREMENT,
           title TEXT,
           content TEXT
       )
   """)
   # --- add image_path if it doesn't exist (migration) ---
   cols = [row[1] for row in sql.execute("PRAGMA table_info(posts)").fetchall()]
   if "image_path" not in cols:
       sql.execute("ALTER TABLE posts ADD COLUMN image_path TEXT")
   connection.commit()


def insert_post(title, content, image_path=None):
   connection = get_db()
   sql = connection.cursor()
   sql.execute(
       "INSERT INTO posts (title, content, image_path) VALUES (?, ?, ?)",
       (title, content, image_path),
   )
   connection.commit()


def select_all_posts():
   connection = get_db()
   sql = connection.cursor()
   return sql.execute("SELECT * FROM posts ORDER BY post_id DESC").fetchall()


def select_post_by_id(post_id):
   connection = get_db()
   sql = connection.cursor()
   return sql.execute("SELECT * FROM posts WHERE post_id = ?", (post_id,)).fetchone()
