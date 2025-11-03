from connection import get_db
from passlib.hash import pbkdf2_sha256 as pw

def create_user_table():
    connection = get_db()
    sql = connection.cursor()
    sql.execute('''
    create table if not exists users (
        "id" integer primary key autoincrement,
        "email" Text,
        "password" Text
    )
    ''')


def insert_user(email, password):
    connection = get_db()
    sql = connection.cursor()
    hashed = pw.hash(password)
    data = sql.execute(''' insert into users (email, password)
                           values (? , ?)''' , [email, hashed])
    connection.commit()

def find_user(email):
    connection = get_db()
    sql = connection.cursor()
    data = sql.execute('''select * from users where email = ?''', [email])
    user = data.fetchone()
    if user:
        return user

def get_user(email, password):
    user = find_user(email)
    if user:
        hashed = user[2]
        check_hash = pw.verify(password, hashed)
        if check_hash:
            return user

def update_user(user_id, email, password):
    connection = get_db()
    sql = connection.cursor()
    data = sql.execute('''select * from users where email = ? and password = ?''', [email, password])
    user = data.fetchone()
    if user:
        return user
