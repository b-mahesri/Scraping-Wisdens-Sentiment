"""
main.py - Orchestrates scraping and storing Wisden cricket articles.

Reference Links:
    Wisden: https://www.wisden.com

    Random Documentation: https://docs.python.org/3/library/random.html
    Time Documentation: https://docs.python.org/3/library/time.html#time.sleep
    Data Classes Documentation: https://docs.python.org/3/library/dataclasses.html

    HTTPS Status Codes: https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status
    Rate Limiting: https://scrape.do/blog/web-scraping-rate-limit/

"""


import random
import time
from dataclasses import dataclass

import wisden_db
import wisden_scraper
import wisden_test  # run 'isort .' to auto-sort imports according to PEP 8


@dataclass
class TeamArchive:
    archive_url: str
    num_pages: int

teams = {
    "Australia": TeamArchive(
        "https://www.wisden.com/team/australia-1/page/", 
        120  # Oct 2021 - Now: 120 pages - Complete archive: 218 pages
    ),
    "England": TeamArchive(
        "https://www.wisden.com/team/england-3/page/",
        229  # Oct 2021 - Now: 229 pages - Complete archive: 407 pages
    ),
    "India": TeamArchive(
        "https://www.wisden.com/team/india-4/page/", 
        229  # Oct 2021 - Now: 229 pages - Complete archive: 347 pages
    ),
    "Pakistan": TeamArchive(
        "https://www.wisden.com/team/pakistan-6/page/", 
        122  # Oct 2021 - Now: 122 pages - Compelete archive: 168 pages
    )
}

MAX_CONSECUTIVE_FAILURES = 3  # After which, we stop scraping


def wait_between_requests():
    """
    Rate Limits - suspends execution for a random duration 
    between the 5 - 10 seconds range.
    """
    sleep_time = random.uniform(5, 10)  # Returns a float, which is a little extra random
    print(f"Being polite :) and avoiding Rate Limiting. Sleeping for {sleep_time:.1f} secondzzzzzzz")
    time.sleep(sleep_time)


def get_article_urls(base_archive_url, num_pages):
    """
    Collects article URLs from a Wisden team's paginated archive
    (https://www.wisden.com/team/{team_name}-{team_number}/page/{n}).

    Stops early after MAX_CONSECUTIVE_FAILURES failed page fetches,
    to avoid hammering a server that may be blocking requests.

    Returns a list of article URLs.
    """
    article_urls = []
    consecutive_failures = 0

    for page in range(num_pages):
        url = base_archive_url + str(page + 1)
        response = wisden_scraper.safe_get(url)

        if response is None:
            consecutive_failures += 1
            print(f"Failed to fetch archive page {page + 1}.")

            if consecutive_failures > MAX_CONSECUTIVE_FAILURES:
                print("Too many consecutive failures - stopping link collection")
                break
            else:
                wait_between_requests()
                continue  # TODO: How to handle a skipped page?

        # else:
        consecutive_failures = 0  # Reset

        print(f"Fetched archive page {page + 1}. Now fetching article urls.")
        urls = wisden_scraper.get_urls(response)
        if urls:
            wisden_test.print_urls(urls)
            article_urls.extend(urls)
        else:
            print(f"No articles scraped from archive page {page + 1}.")  # Unlikely

        wait_between_requests()

    return article_urls


def parse_and_store_articles(article_urls, team, db_connection, db_cursor):
    """
    Parses and stores each article in article_urls into the database.

    Stops early after MAX_CONSECUTIVE_FAILURES failed article fetches
    in a row, to avoid hammering a server that may be blocking requests.
    """
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
                wait_between_requests()
                continue  # TODO: How to handle a missed article?
            
        # else:
        consecutive_failures = 0  # Reset

        wisden_test.print_article(article)
        wisden_db.insert_in_db(db_connection, db_cursor, article)

        wait_between_requests()


def scrape_and_store_archive(team):
    """
    Runs the full pipeline: collects team's article URLs, 
    sets up the database, scrapes and stores each article, 
    then closes the database connection.
    """
    
    urls = get_article_urls(teams[team].archive_url, teams[team].num_pages)

    # Once you've run it for the first team, remove these 2 lines
    wisden_db.reset_db() 
    wisden_db.init_db()

    connection = wisden_db.get_db()
    cursor = connection.cursor()

    parse_and_store_articles(urls, team, connection, cursor)

    # Test
    rows = wisden_db.get_all_rows(team, cursor)
    wisden_test.print_db_output(rows)

    wisden_db.close_db(connection)


if __name__ == "__main__":
    # Bismillah, wisden pls don't block
    scrape_and_store_archive("Pakistan")

    # TODO: Later
    # for team in ["Australia", "England", "India", "Pakistan"]:
    #   scrape_and_store_archive(team)