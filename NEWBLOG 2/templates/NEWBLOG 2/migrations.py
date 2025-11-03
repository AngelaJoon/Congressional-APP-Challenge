from datetime import date
from connection import get_db

def add_publish_date():
    connection = get_db()
    sql = connection.cursor()
    sql.execute('''alter table BlogPosts
                     add published_on date''')

def insert_dates():
    connection = get_db()
    sql = connection.cursor()
    
    sql.execute('''
    update BlogPosts
    set published_on=?
    where published_on is null
    ''', [date.today()])
    
    connection.commit()
