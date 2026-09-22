import time
import random
import wisden_scraper
import wisden_db


# What does this script need to do?
# It needs to run the scraper and store the scraped data into the sqlite db

# What should running the scraper look like, with separation of concerns?
# Under separation of concerns, this script should worry about issues that may arise in scraping
# The scraper functions should either return data, or return None along w some info if unable to return data
# The functions here will keep track of what that means and how to handle it, so I'm moving the issue handling
# out from the scraper to this orchestrator
# Furthermore, I realised I'm only handling for failures when fetching the listing pages,
# I should also be handling for failures in the parse function when I'm fetching individual articles
# I also need to think about the order in which things get moved to DB storage.
# Right now it's get all links, then get 10 articles at a time, and then arguably store
# 10 at a time in the DB. But would listing link->articles->store in DB, repeat be better?

MAX_CONSECUTIVE_FAILURES = 3  # After which, we stop scraping.


def rate_limit():
    """
    Suspends execution for a random number of seconds within a given range.
    """
    sleep_time = random.uniform(5, 8)  # This will return a float, which is a little extra random
    print(f"Being polite :) and avoiding Rate Limiting. Sleeping for {sleep_time:.1f} secondzzzzzzz")
    time.sleep(sleep_time)


def get_article_urls(base_archive_url, num_pages):
    """
    Calls wisden_scraper.py on a Wisden team archive to collect
    article URLs.

    Iterates through a fixed number of paginated archive pages
    (https://www.wisden.com/team/{team_name}-{team_number}/page/{n}).

    Stops scraping early if MAX_CONSECUTIVE_FAILURES failed page
    fetches occur in a row, in order to avoid hammering a
    server that may be blocking requests.

    Returns a list of article URLs.
    """
    article_urls = []  # I will think about if this needs to be set given sqlite db takes care of deduplication
    consecutive_failures = 0

    for page in range(num_pages):
        url = base_archive_url + str(page + 1)

        response = wisden_scraper.safe_get(url)

        if response is None:
            consecutive_failures += 1
            print(f"Failed on listing page {page + 1}")
            if consecutive_failures > MAX_CONSECUTIVE_FAILURES:
                print("Too many consecutive failures - stopping link collection")
                break  # End scraping loop
            else:
                rate_limit()  # Wait before fetching next archive page
                continue  # Need to figure out what to do if a page gets missed

        # Else
        consecutive_failures = 0  # Reset
        print("Got the archive page, now getting the article urls")
        article_urls = wisden_scraper.get_urls(response)
        if article_urls:
            for url in article_urls:
                print(l)  # Sanity check
            article_urls = article_urls + urls
            print(f"Listing Page {page + 1}: articles added")
        else:
            # This is very unlikely to happen but have it incase
            print(f"Listing Page {page + 1}: no articles found")

        rate_limit()  # Wait before fetching next archive page

    return article_urls


def parse_and_store_articles(article_urls, team):
    consecutive_failures = 0
    # TODO: connection = wisden_db.get_db() do we want to open a new connection for each team? Probably because I'll do 4 diff scrapes to avoid issues
    # TODO: cursor = connection.cursor()
    for url in article_urls:
        extracted_fields = wisden_scraper.parse_article(url, team)
        if extracted_fields is None:
            consecutive_failures += 1
            print(f"Failed on article {url}")
            if consecutive_failures > MAX_CONSECUTIVE_FAILURES:
                print("Too many consecutive failures - stopping article parsing")
                break
            else:
                rate_limit()
                continue  # Need to figure out what to do if a page gets missed
            
        # Else
        consecutive_failures = 0  # Reset
        print(extracted_fields)
        # TODO: insert_db(connection, cursor, extracted_fields)
        rate_limit()

    # TODO: wisden_db.close_db(connection)


########## TEST #############
team = "Pakistan"
archive = "https://www.wisden.com/team/pakistan-6/page/"  # 168 pages
pages = 1
urls = get_article_urls(archive, pages)
# TODO: init_db()
parse_and_store_articles(urls, team)  # Kewl it works, idk if passing in team here is the best, but you don't want to have it to figure it out for each article, I already
# know so might as well just pass it in here so it's going in in one place and the DB doesn't have to worry about it

india_archive = "https://www.wisden.com/team/india-4/page/"  # 347 pages
england_archive = "https://www.wisden.com/team/england-3/page/"  # 407 pages
australia_archive = "https://www.wisden.com/team/australia-1/page/"  # 218 pages


# Reference Links:
# Wisden: https://www.wisden.com
# Time Documentation: https://docs.python.org/3/library/time.html#time.sleep
# Random Documentation: https://docs.python.org/3/library/random.html
# HTTPS Status Codes: https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status
# Rate Limiting: https://scrape.do/blog/web-scraping-rate-limit/