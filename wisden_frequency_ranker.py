import collections
import re

import nltk
from nltk.corpus import stopwords

import wisden_db

ENGLISH_STOPWORDS = set(stopwords.words('english'))

CRICKET_STOPWORDS = set([
    'ball',
    'bat',
    'pitch',
    'bowler',
    'batsman',
    'umpire',
    'innings',
    'over',
    'run',
    'runs',
    'wicket',
    'pitch',
    'player',
    'spinner',
    'right',
    'left',
    'arm',
    'hand',
    'handed',
    'hander',
    'leg',
    'cover',
    'drive',
    'field',
    'game'
])

ALL_STOPWORDS = ENGLISH_STOPWORDS.union(CRICKET_STOPWORDS)

# Reference Links
# collections documentation: https://docs.python.org/3/library/collections.html

# Breaking it down step by step:

# What I want at the end: 
# 4 lists, one for each team, of the 50 most frequently used words
# accross all articles, where frequency is normalised to rate per 1,000 words

# 1) For each team, initialise a Counter
# 2) pull all article body_texts
#   probably not a good idea to pull all articles at once, better to do something
#   like 10 at a time so that the program doesn't use too much memory
#   Say you pull 10 at a time
# 3) For each body_text, clean it, make a list of words, filter the list
# 4) then update counter with that filtered list
# 5) When you've done this for every article for that team, run counter.most_common(50) and store it 
#   (list? or do I just want to save the counters? Do i want to write to a txt or csv?)

# I ran main.py, the db is populated with all Pakistan articles
# Will use this article for now:
# 'https://www.wisden.com/cricket-news/explained-why-pakistan-have-reappointed-babar-azam-three-years-after-test-captain'


def clean_text(body_text):
    filtered_words = []

    body_text = body_text.lower()  # conver every character in the string to lower case
    words = re.findall(r"\b[a-zA-Z]+\b", body_text)  # Ignore all punctuation and digits, convert string to a list of words
    for word in words:
        if word not in ALL_STOPWORDS:
            filtered_words.append(word)

    return filtered_words

def test_concept():
    frequency_counter = collections.Counter() # Empty

    connection = wisden_db.get_db()
    cursor = connection.cursor()

    # TODO: Loop for getting 10 articles at a time
    #       I wrote the function, I can write the loop tomorrow

    # Placeholder
    article_urls = ['https://www.wisden.com/cricket-news/explained-why-pakistan-have-reappointed-babar-azam-three-years-after-test-captain']
    for url in article_urls:

        # Placeholder
        body_text = wisden_db.get_text(url, cursor)[0]  # a tuple with one item is returned, python tuples have zero based indexing

        filtered_words = clean_text(body_text)

        frequency_counter.update(filtered_words)  # Counter is a special data structure. It's pretty much a dict, key is the word and value is frequency. The constructor can take a list of words and figure out their frequencies
        
        most_common = frequency_counter.most_common(50)  # Will return list of all (word, count) in order from most common to least
        for word, count in most_common:
            print(word, ":", count)


if __name__ == "__main__":
    test_concept()
