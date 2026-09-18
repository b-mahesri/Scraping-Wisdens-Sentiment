import sqlite3


connection = sqlite3.connect("wisden.db")
cursor = connection.cursor


def init_db():
    return None


def get_db():
    connection = sqlite3.connect("wisden.db")
    cursor = connection.cursor
    connection.commit()
    return cursor


def insert_in_db():
    # cursor.execute(query)
    return None


def close_db():
    return None


# Reference Links:
# SQLite Documentation: https://docs.python.org/3/library/sqlite3.html

# Will need to make a get_db() function, don't want main.py to directly open
# a connection with the db
# Likewise make a close_db() function and an insert_in_db()
# also an init_db() that creates the db that main can call, main doesn't need
# to worry about how exactly to create a db
# a function that expects the shape of extracted_fields and does whatever
# is need so that the fields can be inserted in the DB

# When saving the articles to the db, we don't want to open and close
# the db for each article. Open db once at the start before we parse all the
# articles and pass the connection to insert_in_db() each time, rather opening
# a new connection in every call to insert, and then once all the articles are
# parsed, close_db()

# When to do execute() and when to do commit(), do you only call commit when
# you're about to close the db? It is chill to commit() after every insert or
# if you want to be just a little cheekier and more efficient, commit after
# every N inserts

# Should I pass the extracted_fields dict directly to the insert_in_db() function
# and then insert can worry about figuring out what to do before the
# extracted fields are in the right shape to be inserted into the db?

# Should this file create the db or should main.py create the db? init_db()

# How to delete/ reset the db incase I want to start fresh everytime I 
# execute while im still testing everything
