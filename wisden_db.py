import os
import sqlite3

# NEXT TODO
# TODO: Clean up the code and add documentation
# TODO: Test everything more thoroughly and with one page of archives, look into the best way to test something like this
# TODO: Add a couple of get() functions, get row given url


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
    # "title": title,
    # "date": date,
    # "series": series,
    # "author": author,
    # "body_text": body_text,
    # "team": team,

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


def count_rows_in_db(cursor, team=None):
    if team:
        query = """SELECT COUNT(*) FROM articles WHERE team = ?"""
        cursor.execute(query, (team,))
    else:
        query = """SELECT COUNT(*) FROM articles"""
        cursor.execute(query)

    return cursor.fetchone()[0]


# PAGINATION FUNCTION
# LIMIT is how many rows you want the query to return
# OFFSET determines from which row onwards you want the query to apply to
# We can fix the LIMIT at 10 and then run a loop where OFFSET is incremented by 10 in each iteration
# That way we can get 10 articles at a time rather than all of them at once
def get_rows_paginated(cursor, limit, offset, team=None):
    if team:
        query = """
            SELECT * FROM articles WHERE team = ? LIMIT ? OFFSET ?
        """
        cursor.execute(query, (team, limit, offset))
    else:
        query = """
            SELECT * FROM articles LIMIT ? OFFSET ?
        """
        cursor.execute(query, (limit, offset))

    return cursor.fetchall()
    # fetchall() returns all the rows the query returned
    # each row is a tuple, so it returns a list of tuples


# Temp test function for frequency ranker
def get_text(article_url, cursor):
    query = """
        SELECT body_text FROM ARTICLES
        WHERE url = ?
    """
    url = (
        article_url,
    )
    cursor.execute(query, url)
    return cursor.fetchone()  # returns a tuple containing the text

    # fetchone() returns one row from all the rows the query returns 
    # starting with the first row, then when you call cursor.fetchone() 
    # again it'll return the second row and advance the cursor 
    # to the third row and so on


if __name__ == "__main__":
    cursor = get_db().cursor()
    print(f"{count_rows_in_db(cursor, "Australia")} Australia articles uploaded to db.")
    print(f"{count_rows_in_db(cursor, "England")} England articles uploaded to db.")
    print(f"{count_rows_in_db(cursor, "India")} India articles uploaded to db.")
    print(f"{count_rows_in_db(cursor, "Pakistan")} Pakistan articles uploaded to db.")
    print(f"{count_rows_in_db(cursor)} total articles uploaded to db.")

# Reference Links:
# SQLite Documentation: https://docs.python.org/3/library/sqlite3.html