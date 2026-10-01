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


def get_all_rows(team, cursor):
    get_all = """
        SELECT * FROM articles
        WHERE team = ?
    """
    team_tuple = (
        team,
    )
    cursor.execute(get_all, team_tuple)  # Needs to always be a tuple
    return cursor.fetchall()  
    # fetchall() returns all the rows the query returned
    # each row is a tuple, so it returns a list of tuples

def count_rows_in_db(cursor, team):
    query = """
        SELECT COUNT(*) FROM articles
        WHERE team = ?
    """
    team = (
        team,
    )
    cursor.execute(query, team)
    return cursor.fetchone()[0]


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
    num_rows = count_rows_in_db(get_db().cursor(), "Pakistan")
    print(num_rows)

# Reference Links:
# SQLite Documentation: https://docs.python.org/3/library/sqlite3.html