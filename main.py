import random
import test
import time

import wisden_db
import wisden_scraper

archive_urls = {
    "Australia": "https://www.wisden.com/team/australia-1/page/",  # 218 pages total
    "England": "https://www.wisden.com/team/england-3/page/",  # 407 pages total
    "India": "https://www.wisden.com/team/india-4/page/",  # 347 pages total
    "Pakistan": "https://www.wisden.com/team/pakistan-6/page/"  # 168 pages total
}

# The number of archive pages that need to be parsed in order to collect all articles between Oct 2021 - Now (last 5 years)
num_archive_pages = {
    "Australia": 120,  # 1200 articles
    "England": 229,  # 2290 articles
    "India": 229,  # 2290 articles
    "Pakistan": 122  # 1220 articles
}

MAX_CONSECUTIVE_FAILURES = 3  # After which, we stop scraping.


def rate_limit():
    """
    Suspends execution for a random number of seconds within a given range.
    """
    sleep_time = random.uniform(5, 10)  # This will return a float, which is a little extra random
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
            print(f"Failed to fetch archive page {page + 1}.")

            if consecutive_failures > MAX_CONSECUTIVE_FAILURES:
                print("Too many consecutive failures - stopping link collection")
                break  # End scraping loop
            else:
                rate_limit()  # Wait before fetching next archive page
                continue  # Need to figure out what to do if a page gets missed

        # Else
        consecutive_failures = 0  # Reset

        print(f"Fetched archive page {page + 1}. Now fetching article urls.")

        urls = wisden_scraper.get_urls(response)
        if urls:
            test.print_urls(urls)
            article_urls = article_urls + urls
        else:
            print(f"No articles scraped from archive page {page + 1}.")  # Unlikely

        rate_limit()  # Wait before fetching next archive page

    return article_urls


def parse_and_store_articles(article_urls, team, db_connection, db_cursor):
    consecutive_failures = 0
    
    for url in article_urls:
        article = wisden_scraper.parse_article(url, team)

        if article is None:
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

        # test.print_article(article)
        wisden_db.insert_in_db(db_connection, db_cursor, article)
        rate_limit()


def scrape_and_store():
    
    pakistan_urls = get_article_urls(archive_urls["Pakistan"], num_archive_pages["Pakistan"])

    wisden_db.reset_db()
    wisden_db.init_db()
    connection = wisden_db.get_db()
    cursor = connection.cursor()

    parse_and_store_articles(pakistan_urls, "Pakistan", connection, cursor)

    rows = wisden_db.get_all_rows("Pakistan", cursor)
    test.print_db_output(rows)

    wisden_db.close_db(connection) # Looks like it works


########## Main #############
scrape_and_store()


# Reference Links:
# Wisden: https://www.wisden.com
# Time Documentation: https://docs.python.org/3/library/time.html#time.sleep
# Random Documentation: https://docs.python.org/3/library/random.html
# HTTPS Status Codes: https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status
# Rate Limiting: https://scrape.do/blog/web-scraping-rate-limit/