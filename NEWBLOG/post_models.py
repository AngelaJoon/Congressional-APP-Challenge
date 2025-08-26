from connection import get_db
from posts import blog_posts


def create_post_table():
    connection = get_db()
    sql = connection.cursor()
    sql.execute(
        """
    create table if not exists BlogPosts (
        "PostId" integer primary key autoincrement,
        "Title" Text,
        "Author" Text,
        "Content" Text,
        "Permalink" Text,
        "Tags" Text,
        "published_on" date
    )
    """
    )

    posts = get_posts()
    if len(posts) == 0:
        for post in blog_posts:
            insert_post(post)


def insert_post(post):
    connection = get_db()
    sql = connection.cursor()
    post_items = post.values()
    sql.execute(
        """
        Insert into BlogPosts (Title, Author, Content, Permalink, Tags, published_on)
        values(?, ?, ?, ? ,?, ?)
    """,
        list(post_items),
    )
    connection.commit()


def update_post(post):
    connection = get_db()
    sql = connection.cursor()
    post_items = post.values()
    sql.execute(
        """
        Update BlogPosts
        set Title=?, Author=?, Content=?, Permalink=?, Tags=?, published_on=?
        where PostId=?
    """,
        list(post_items),
    )
    connection.commit()


def get_posts():
    connection = get_db()
    sql = connection.cursor()
    data = sql.execute("""select * from BlogPosts order by PostId desc""")
    saved_posts = data.fetchall()
    return saved_posts


def count_posts():
    connection = get_db()
    sql = connection.cursor()
    count_query = sql.execute("""select count(PostId) from BlogPosts""")
    count = count_query.fetchone()
    return count[0]


def paginated_posts(current_page, per_page):
    connection = get_db()
    sql = connection.cursor()

    prev_page = current_page - 1
    offset = prev_page * per_page

    data = sql.execute(
        """select * from BlogPosts order by PostId desc
                          limit ? offset ?""",
        [per_page, offset],
    )

    saved_posts = data.fetchall()
    return saved_posts


def find_post(permalink):
    connection = get_db()
    sql = connection.cursor()
    data = sql.execute("""select * from BlogPosts where permalink = ?""", [permalink])
    post = data.fetchone()
    return post


def random_post():
    connection = get_db()
    sql = connection.cursor()
    data = sql.execute("""select * from BlogPosts order by random() Limit 1""")
    post = data.fetchone()
    return post


def delete_post(post_id):
    connection = get_db()
    sql = connection.cursor()
    data = sql.execute("delete from BlogPosts where PostId=?", [post_id])
    connection.commit()
