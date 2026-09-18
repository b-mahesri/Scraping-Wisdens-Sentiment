import requests
from bs4 import BeautifulSoup
import time
import random


# Reference Links:
# Wisden: https://www.wisden.com
# Requests Documentation: https://requests.readthedocs.io/en/latest/
# Beautiful Soup Documentation: https://beautiful-soup-4.readthedocs.io/en/latest/
# Time Documentation: https://docs.python.org/3/library/time.html#time.sleep
# Random Documentation: https://docs.python.org/3/library/random.html
# HTTPS Status Codes: https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status
# Rate Limiting: https://scrape.do/blog/web-scraping-rate-limit/


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

MAX_CONSECUTIVE_FAILURES = 3  # After which, we stop scraping.


def rate_limit():
    """
    Suspends execution for a random number of seconds within a given range.
    """
    sleep_time = random.uniform(5, 8)  # This will return a float, which is a little extra random
    print(f"Being polite :) and avoiding Rate Limiting. Sleeping for {sleep_time:.1f} secondzzzzzzz")
    time.sleep(sleep_time)


def get_clean_text(tag):
    """
    Returns clean text within HTML tag, returns None if empty tag.
    """
    if tag is None:
        return None
    return " ".join(tag.get_text().split())


def safe_get(url):
    """
    Wraps requests.get() with error handling for request timeouts,
    rate-limit responses (429), and bot-block responses (403/503).

    Returns the Response object on success, else returns None.
    """
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)  # 10 seconds is a reasoanable amount of time to wait for a response
    except requests.exceptions.RequestException as e:
        print(f"Request failed entirely for {url}: {e}")
        return None
    
    # Note: Wisden is not "hostile", there is no Akamai to deny access.
    #       The following checks should be enough.
    status_code = response.status_code

    if status_code == 429:
        print(f"429 Too Many Requests on {url}. We have been Rate Limited, checking for Retry-After header...")
        retry_after = response.headers.get("Retry-After")
        if retry_after:
            print (f"Server asked us to wait {retry_after} seconds.")
        return None

    if status_code == 403:
        print(f"403 Forbidden on {url}. The server knows us and is refusing to serve, we have possibly been blocked :(")
        return None

    if status_code == 503:
        print(f"503 Service Unavailable on {url}. Server possibly down for maintenance or overloaded, checking for Retry-After header... ")
        retry_after = response.headers.get("Retry-After")
        if retry_after:
            print(f"Server asked us to wait {retry_after} seconds.")
        return None

    if status_code != 200:
        print(f"({status_code}) Unexpected status on {url}. Refer to documentation.")
        return None
  
    return response


def parse_article(url):
    """
    Fetches and parses a single article.
    Returns a dict of extracted fields, or None if the fetch failed.
    Tested on: 
    - Recent article from 2026: "https://www.wisden.com/series/england-vs-pakistan-m-2026/cricket-features/why-are-pakistan-this-bad-at-test-cricket"
    - Oldest listed article from 2017: "https://www.wisden.com/cricket-news/2017-review-legend-leaves-one-last-gift"
    """
    response = safe_get(url)
    if response is None:
        return None

    html = response.text
    soup = BeautifulSoup(html, "html.parser")

    article = soup.find("article")
    if article is None:
        print("No <article> tag found in {url}")
        return None

    title = get_clean_text(article.find("h1"))
    date = get_clean_text(article.find("span", class_="meta-date meta"))
    series = get_clean_text(article.find("a", class_="meta meta-category"))
    author = get_clean_text(article.find("h4"))

    article_body = article.find("div", class_="article-body")
    paragraphs = article_body.find_all("p")
    body_text = "\n".join(
        get_clean_text(p) for p in paragraphs if get_clean_text(p)
    )
    
    return {
        "url": url,
        "title": title,
        "date": date,
        "series": series,
        "author": author,
        "body_text": body_text,
    }


def get_article_urls(base_url, num_pages):
    """
    Scrapes a Wisden team archive listing pages to collect
    article URLs.

    Iterates through a fixed number of paginated archive pages 
    (https://www.wisden.com/team/{team_name}-{team_number}/page/{n}).
    Uses safe_get() for each page and rate_limit() between each request.
    
    Stops scraping early if MAX_CONSECUTIVE_FAILURES failed page
    fetches occur in a row, in order to avoid hammering a
    server that may be blocking requests.

    Returns a set of article URLs.
    """
    links = set()  # Provides automatic deduplication, but order will be unpredictable.
    consecutive_failures = 0

    for page in range(num_pages):
        url = base_url + str(page + 1)
        response = safe_get(url)

        if response is None:
            consecutive_failures += 1
            print(f"Failed on listing page {page + 1}")
            if consecutive_failures > MAX_CONSECUTIVE_FAILURES:
                print("Too many consecutive failures - stopping link collection")
                break  # End scraping loop
            # else
            rate_limit()
            continue # Go to next loop iteration and try next url.

        # Else
        consecutive_failures = 0  # Reset.

        html = response.text
        soup = BeautifulSoup(html, "html.parser")

        articles = soup.find_all("article")
        for article in articles:
            a_tag = article.find("a")
            if (a_tag and a_tag.get('href')):  # Handle missing <a> tags and links.
                links.add(a_tag.get('href')) # There is only ever one link within an <article>, therefore this is safe to do.

        print(f"Listing Page {page + 1}: {len(articles)} articles found")
        rate_limit()
            
    print(f"Total {len(links)} article links collected")
    return links


def scrape_wisden(team_archive, num_pages):
    """
    Scrapes a Wisden team archive and collects article texts.
    """
    article_urls = get_article_urls(team_archive, num_pages)
    for url in article_urls:
        extracted_fields = parse_article(url)
        print(extracted_fields)
        rate_limit()

        
########## TEST #############
pakistan_archive = "https://www.wisden.com/team/pakistan-6/page/"
pages = 1
scrape_wisden(pakistan_archive, pages)


# Thinking about separation of concerns:
# I want the scraper code and the DB code to be separate and not know about eachother
# I want to write a third "orchestrator script" that calls functions from both
# Here's something important to think about:
# Right now, I'm checking for errors in the get requests in the scraper
# I stop scraping for links if there are too many errors
# Arguably, that's a separation of concerns issue and something the orchestrator
# should worry about, not the scraper, but I need to think about what that looks like
# Furthermore, I realised I'm only handling for failures when fetching the listing pages,
# I should also be handling for failures in the parse function when I'm fetching individual articles
# I also need to think about the order in which things get moved to DB storage.
# Right now it's get all links, then get 10 articles at a time, and then arguably store
# 10 at a time in the DB. But would listing link->articles->store in DB, repeat be better?
# What should I do first? Set up DB, edit scraper or figure out orchestrator?
# I think figure out what the orchestrator needs to be doing, that will then
# dictate what the scraper and db scripts should look like