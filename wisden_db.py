import os
import sqlite3

# NEXT TODO
# TODO: Clean up the code and add documentation
# TODO: Test everything more thoroughly and with one page of archives, look into the best way to test something like this
# TODO: Add a couple of get() functions, get row given url, get all rows for a certain team
# TODO: Look into sentiment analysis and decide which to start working on, do a very simple one first


file_name = "wisden.db"


def init_db():
    connection = sqlite3.connect(file_name)
    cursor = connection.cursor()

    create_table = """ 
        CREATE TABLE IF NOT EXISTS articles (
            url TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            date TEXT NOT NULL,
            series TEXT,
            author TEXT,
            body_text TEXT NOT NULL,
            team TEXT NOT NULL
        )
    """

    cursor.execute(create_table)
    connection.commit()
    connection.close()
    print("Wisden SQLite db created")


def get_db():
    if not os.path.exists("wisden.db"):
        print("Database doesn't exist yet. Run init_db() first")
        return None
    
    connection = sqlite3.connect("wisden.db")
    return connection  # things like commit() and close() live with the connection, so we don't want to just return the cursor


def insert_in_db(connection, cursor, fields):  # Passing in cursor from main.py so that we don't create a new instance for each insert
    # this is the shape of the dict being passed in
    # "url": url,
    #         "title": title,
    #         "date": date,
    #         "series": series,
    #         "author": author,
    #         "body_text": body_text,
    #         "team": team,

    insert_row = """
        INSERT INTO articles (
            url, 
            title, 
            date, 
            series, 
            author, 
            body_text, 
            team)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    data = (
        fields["url"], 
        fields["title"], 
        fields["date"], 
        fields["series"], 
        fields["author"],
        fields["body_text"],
        fields["team"],
        )

    try:
        cursor.execute(insert_row, data)
        connection.commit()
        return True
    except sqlite3.IntegrityError:
        print(f"Skipping duplicate: {fields["url"]}")
        return False


def close_db(connection):
    if connection is None:
        print("Database connection is None.")
        return
    connection.commit()  # Not the primary commit, just a safety net
    connection.close()
    print("Database connection closed.")


def reset_db():
    if os.path.exists(file_name):
        os.remove(file_name)
        print(f"Deleted {file_name}")
    else:
        print(f"{file_name} doesn't exist, nothing to delete")


############## TEST ###############
reset_db()
# init_db()
# connection = get_db()
# data = {
#         "url": "test_url",
#         "title": "test title",
#         "date": "YYYY-MM-DD",
#         "series": "test series",
#         "author": "test author",
#         "body_text": "test body text",
#         "team": "test team",
#     }
# insert_in_db(connection, connection.cursor(), data)
# result = connection.cursor().execute("SELECT * FROM articles")
# print(result.fetchone())
# close_db(connection)
# Testing is not thorough, but seems to work



# Reference Links:
# SQLite Documentation: https://docs.python.org/3/library/sqlite3.html


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