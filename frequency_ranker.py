import wisden_db
import collections

# TODO:
# Focus on the text of one article
# Remove all '\n' chars - if you print the text after converting it into a string you don't see the endline char in the output
# Set all words to lower case
# Get a list of stopwords and remove all stop words from the text - do I want to include common cricket terms in this list?
# Count frequency for each remaining word
# Print it out to test
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
print(body_text)  # is working




# Reference Links
# collections documentation: https://docs.python.org/3/library/collections.html