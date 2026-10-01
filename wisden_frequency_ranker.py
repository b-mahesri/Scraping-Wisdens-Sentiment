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

# TODO:
# Think about how to store the result and how to scale the process for all the articles


# Bigger picture:
# I want to do this by team for all the articles I scrape 
# Because the number of articles for all the teams isn't the same, I will calculate the rate per 1,000 words for each word
# Then I can look at the top 50 most frequently used words for each team and see if it reveals anything

# I ran main.py, the db is populated with 10 articles
# Will use this article for now:
# 'https://www.wisden.com/cricket-news/explained-why-pakistan-have-reappointed-babar-azam-three-years-after-test-captain'

def test_concept():
    connection = wisden_db.get_db()
    cursor = connection.cursor()

    article_url = 'https://www.wisden.com/cricket-news/explained-why-pakistan-have-reappointed-babar-azam-three-years-after-test-captain'
    body_text = wisden_db.get_text(article_url, cursor)[0]  # a tuple with one item is returned, python tuples have zero based indexing

    body_text = body_text.lower()  # convert every character to lowercase
    words = re.findall(r"\b[a-zA-Z]+\b", body_text)  # will ignore all punctuation and digits and will return all words in the string as a list

    filtered_words = []
    for word in words:
        if word not in ALL_STOPWORDS:
            filtered_words.append(word)

    frequency_counter = collections.Counter(filtered_words)  # Counter is a special data structure. It's pretty much a dict, key is the word and value is frequency. The constructor can take a list of words and figure out their frequencies
    most_common = frequency_counter.most_common()  # Will return list of all (word, count) in order from most common to least
    for word, count in most_common:
        print(word, ":", count)


if __name__ == "__main__":
    test_concept()

# You will basically make a filtered list for each article and then add the frequency up in one counter:
# final_counter = counter1 + counter2 ... countern
# the '+' operator adds/merges counters DON'T this creates a new counter each time
# instead use final_counter.update(<new_filtered_list> ) to avoid that

# then in the end do final_counter.most_common(50) to get 50 most common words


# Reference Links
# collections documentation: https://docs.python.org/3/library/collections.html

