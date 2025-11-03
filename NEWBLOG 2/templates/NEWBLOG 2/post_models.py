from connection import get_db
from posts import blog_posts
import sqlite3

def create_post_table():
    connection = get_db()
    sql = connection.cursor()
    sql.execute(
        """
        CREATE TABLE IF NOT EXISTS BlogPosts (
            PostId INTEGER PRIMARY KEY AUTOINCREMENT,
            Title TEXT,
            Author TEXT,
            Content TEXT,
            Permalink TEXT,
            Tags TEXT,
            published_on DATE,
            Image TEXT,
            Rating TEXT,
            Address TEXT,
            Latitude REAL,
            Longitude REAL
        );
        """
    )
    connection.commit()


def column_exists(table_name, column_name):
    connection = get_db()
    sql = connection.cursor()
    sql.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in sql.fetchall()]
    return column_name in columns

def add_image_column():
    if not column_exists("BlogPosts", "Image"):
        connection = get_db()
        sql = connection.cursor()
        sql.execute("ALTER TABLE BlogPosts ADD COLUMN Image TEXT;")
        connection.commit()

def add_rating_column():
    if not column_exists("BlogPosts", "Rating"):
        connection = get_db()
        sql = connection.cursor()
        sql.execute("ALTER TABLE BlogPosts ADD COLUMN Rating TEXT;")
        connection.commit()

# post_models.py
def add_location_columns():
    connection = get_db()
    sql = connection.cursor()
    # Address
    sql.execute("PRAGMA table_info(BlogPosts)")
    cols = [row[1] for row in sql.fetchall()]
    if "Address" not in cols:
        sql.execute("ALTER TABLE BlogPosts ADD COLUMN Address TEXT")
    if "Latitude" not in cols:
        sql.execute("ALTER TABLE BlogPosts ADD COLUMN Latitude REAL")
    if "Longitude" not in cols:
        sql.execute("ALTER TABLE BlogPosts ADD COLUMN Longitude REAL")
    connection.commit()


def insert_post(post):
    connection = get_db()
    sql = connection.cursor()
    sql.execute(
        """
        INSERT INTO BlogPosts
          (Title, Author, Content, Permalink, Tags, published_on, Image, Rating, Address, Latitude, Longitude)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
               post.get("title"),
            post.get("author"),
            post.get("content"),
            post.get("permalink"),
            post.get("tags"),
            post.get("published_on"),
            post.get("image"),
            post.get("rating"),
            post.get("address"),
            post.get("latitude"),
            post.get("longitude"),
        ),
    )
    connection.commit()



def update_post(post):
    connection = get_db()
    sql = connection.cursor()
    sql.execute(
        """
        UPDATE BlogPosts
        SET Title=?, Author=?, Content=?, Permalink=?, Tags=?, published_on=?,
            Image=?, Rating=?, Address=?, Latitude=?, Longitude=?
        WHERE PostId=?
        """,
        (
            post["title"], post["author"], post["content"], post["permalink"],
            post["tags"], post["published_on"], post.get("image"),
            post.get("rating"), 
            post.get("address"),
            post.get("latitude"), 
            post.get("longitude"),
            post["post_id"]
        ),
    )
    connection.commit()


    posts = get_posts()
    if len(posts) == 0:
        for post in blog_posts:
            insert_post(post)


def get_posts():
    connection = get_db()
    sql = connection.cursor()
    data = sql.execute("""SELECT * FROM BlogPosts ORDER BY PostId DESC""")
    return data.fetchall()


def count_posts():
    connection = get_db()
    sql = connection.cursor()
    count_query = sql.execute("""SELECT COUNT(PostId) FROM BlogPosts""")
    count = count_query.fetchone()
    return count[0]


def paginated_posts(current_page, per_page):
    connection = get_db()
    sql = connection.cursor()
    offset = (current_page - 1) * per_page
    data = sql.execute(
        """SELECT * FROM BlogPosts ORDER BY PostId DESC LIMIT ? OFFSET ?""",
        (per_page, offset),
    )
    return data.fetchall()


def find_post(permalink):
    connection = get_db()
    sql = connection.cursor()
    data = sql.execute(
        """SELECT * FROM BlogPosts WHERE Permalink = ?""", (permalink,)
    )
    return data.fetchone()


def random_post():
    connection = get_db()
    sql = connection.cursor()
    data = sql.execute("""SELECT * FROM BlogPosts ORDER BY RANDOM() LIMIT 1""")
    return data.fetchone()


def delete_post(post_id):
    connection = get_db()
    sql = connection.cursor()
    sql.execute("DELETE FROM BlogPosts WHERE PostId = ?", (post_id,))
    connection.commit()
    
def drop_post_table():
    connection = get_db()
    sql = connection.cursor()
    sql.execute("DROP TABLE IF EXISTS BlogPosts;")
    connection.commit()
    
