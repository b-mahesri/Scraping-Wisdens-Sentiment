"""
# Reference Links
# Collections documentation: https://docs.python.org/3/library/collections.html
# Python - List Comprehension: https://www.w3schools.com/python/python_lists_comprehension.asp
"""
import collections
import re

import nltk
from nltk.corpus import stopwords

import wisden_db

ENGLISH_STOPWORDS = set(stopwords.words('english'))

# This is going to have to be much more extensive, all the results are super boring, but note i just have 10 articles per team rn
CRICKET_STOPWORDS = set([
    'africa',
    'also',
    'arm',
    'australia',
    'bangladesh',
    'bat',
    'batsman',
    'batsmen',
    'batter',
    'batting',
    'bowled',
    'bowler',
    'bowlers',
    'bowling',
    'boundary',
    'catch',
    'caught',
    'century',
    'cover',
    'cricket',
    'crease',
    'deliveries',
    'delivery',
    'dismissal',
    'dismissed',
    'drive',
    'eight',
    'england',
    'field',
    'fielder',
    'fielding',
    'five',
    'four',
    'game',
    'hand',
    'hander',
    'handed',
    'india',
    'indies',
    'innings',
    'leg',
    'left',
    'match',
    'new',
    'nine',
    'odi',
    'one',
    'out',
    'over',
    'overs',
    'pakistan',
    'pitch',
    'play',
    'played',
    'player',
    'players',
    'playing',
    'right',
    'run',
    'runs',
    'score',
    'scored',
    'scoring',
    'season',
    'series',
    'seven',
    'six',
    'south',
    'spinner',
    't20',
    'team',
    'test',
    'three',
    'ten',
    'two',
    'umpire',
    'west',
    'wicket',
    'wickets',
    'wicketkeeper',
    'zealand',
    'zimbabwe',
])

ALL_STOPWORDS = ENGLISH_STOPWORDS.union(CRICKET_STOPWORDS)

PAGINATION_LIMIT = 25

def clean_text(body_text):
    """
    Lowercases, strips punctuation/digits, and removes stopwords
    from body_text. Returns a list of filtered words.
    """
    body_text = body_text.lower()  # Lowercases each char
    words = re.findall(r"\b[a-zA-Z]+\b", body_text)  # Strips all punctuation/digits, returns a list of words
    filtered = [word for word in words if word not in ALL_STOPWORDS]  # Python List Comprehension syntax
    return filtered


def print_most_common(frequencies, n):
    for word, count in frequencies.most_common(n):
        print(word, ":", count)

    
def calculate_frequencies(team):
    frequencies = collections.Counter()

    connection = wisden_db.get_db()
    cursor = connection.cursor()

    # Loop to process all articles of team
    offset = 0 
    while True:
        rows = wisden_db.get_rows_paginated(cursor, PAGINATION_LIMIT, offset, team)  # List of tuples, each tuple will have all the columns in it
        
        if not rows:  # query return nothing, no more articles left to fetch
            break

        for row in rows:
            body_text = row["body_text"]
            filtered = clean_text(body_text)
            frequencies.update(filtered)

        offset += PAGINATION_LIMIT

    # Calculate top 50
    print(f"{team}'s 50 most frequent words:")
    print_most_common(frequencies, 50)
    print()
        

if __name__ == "__main__":
    calculate_frequencies("Australia")
    calculate_frequencies("England")
    calculate_frequencies("India")
    calculate_frequencies("Pakistan")

