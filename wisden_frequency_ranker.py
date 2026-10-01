import wisden_db
import collections
import re
import nltk
from nltk.corpus import stopwords
nltk.download('stopwords')

cricket_stopwords = [
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
]

# TODO:
# Get a list of stopwords and remove all stop words from the text - do I want to include common cricket terms in this list?
# Then think about how to store the result and how to scale the process for all the articles


# Bigger picture:
# I want to do this by team for all the articles I scrape 
# Because the number of articles for all the teams isn't the same, I will calculate the rate per 1,000 words for each word
# Then I can look at the top 50 most frequently used words for each team and see if it reveals anything

# I ran main.py, the db is populated with 10 articles
# Will use this article for now:
# 'https://www.wisden.com/cricket-news/explained-why-pakistan-have-reappointed-babar-azam-three-years-after-test-captain'

#### MAIN #### for frequency_ranker.py (before running comment out the code in TEST in main.py)
connection = wisden_db.get_db()
cursor = connection.cursor()

article_url = 'https://www.wisden.com/cricket-news/explained-why-pakistan-have-reappointed-babar-azam-three-years-after-test-captain'
body_text = wisden_db.get_text(article_url, cursor)[0]  # a tuple with one item is returned, python tuples have zero based indexing

body_text = body_text.lower()  # convert every character to lowercase
words = re.findall(r"\b[a-zA-Z]+\b", body_text)  # will ignore all punctuation and digits and will return all words in the string as a list

# combined english and cricket stopwords
# Todo run a loop through words to remove all stopwords - you need to make a cricket stopwords list
all_stopwords = set(stopwords.words('english')).union(set(cricket_stopwords))
filtered_words = []
for word in words:
    if word not in all_stopwords:
        filtered_words.append(word)

frequency_counter = collections.Counter(filtered_words)  # Counter is a special data structure. It's pretty much a dict, key is the word and value is frequency. The constructor can take a list of words and figure out their frequencies
most_common = frequency_counter.most_common()  # Will return list of all (word, count) in order from most common to least
for word, count in most_common:
    print(word, ":", count)

# You will basically make a filtered list for each article and then add the frequency up in one counter:
# final_counter = counter1 + counter2 ... countern
# the '+' operator adds/merges counters DON'T this creates a new counter each time
# instead use final_counter.update(<new_filtered_list> ) to avoid that

# then in the end do final_counter.most_common(50) to get 50 most common words


# Reference Links
# collections documentation: https://docs.python.org/3/library/collections.html

