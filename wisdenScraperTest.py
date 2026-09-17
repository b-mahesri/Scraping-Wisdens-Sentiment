import requests
from bs4 import BeautifulSoup
import time
import random


# Reference Links:
# Wisden: https://www.wisden.com
# HTTPS Status Codes: https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status
# Requests Documentation: https://requests.readthedocs.io/en/latest/


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

MAX_CONSECUTIVE_FAILURES = 3  # When to stop scraping

def rate_limit():
    """
    Suspends execution for a random number of seconds within a given range.
    """
    sleep_time = random.uniform(5, 8)  # Will return a float, little extra random
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
    Wraps requests.get with error handling for request timeouts,
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
    # Print fields out to check
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
    fetches occur in a row, inr order to avoid hammering a
    server that may be blocking requests.

    Returns a set of article URLs.
    """
    links = set()  # automatic deduplication, but order will be unpredictable
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
            continue # go to next iteration in loop

        # Else
        consecutive_failures = 0  # reset

        html = response.text
        soup = BeautifulSoup(html, "html.parser")

        articles = soup.find_all("article")
        for article in articles:
            a_tag = article.find("a")
            if (a_tag and a_tag.get('href')):  # Handle missing a tags and links
                links.add(a_tag.get('href')) # There is only ever one link within an <article>, this is safe to do

        print(f"Listing Page {page + 1}: {len(articles)} articles found")
        rate_limit()
            
    print(f"Total {len(links)} article links collected")
    return links


def scrape_wisden(team_archive, num_pages):
    """
    Scrapes a Wisden team archive to collect article texts.
    """
    article_urls = get_article_urls(team_archive, num_pages)
    for url in article_urls:
        extracted_fields = parse_article(url)
        print(extracted_fields)
        rate_limit()
        

# MAIN
pakistan_archive = "https://www.wisden.com/team/pakistan-6/page/"
pages = 1
scrape_wisden(pakistan_archive, pages)


# Next questions to think about
# Is this the most efficient way to get all the links?

# How far back do I want to go?
# I think go back 10 years. 2016 Test team to now is a pretty compelling narrative and top of mind. I think you can track a decline and a fall in regard, atleast in the journalism.
# So let's go till Sept 2016 - wisden goes back till 2017. 
# The main years where I think the language gets bad is 2023 onwards - and then if you want to do everyone, then maybe do it till 2020 or 2021 T20 WC onwards

# How do I want to store what I parse from the articles?
# Will probably just want to store the cleaned text as is, so that later when I do more
# processing i access it through that storage + if i decide to do soemthing diff
# with the text then I don't have to undo or rescrape anything
# How do I want to process what I parse from the articles? I think this will inform how I want to store it
# Which countries articles will make for an interesting comparison? Big 3 definitely - India, Australia, England and then I think 3 other teams that have been down in the rankings.
# Sri Lanka and West Indies have also struggled of late and Bangladesh is coming up but it's been down. I think even Afghanistan might be interesting. Lowkey I want to look at 
# All the test playing nations

# I think one thing to note is, some countries will have more coverage than others because some countries are richer and play more cricket. That will be something to keep in mind.
# You need to figure out how many pages you have to parse for each country to get to the start of 2020 or maybe when regular schedules resumed post covid?


# What is the best way to process in order to capture patterns or sentiment in the language? Do I just want to look at the most frequently used words or are there other ways?
# Need to look into Sentiment analysis
# Another thing to keep in mind is I want to also try data visualising and maybe
# some analysis are more conducive for data vis than others - maybe I can try
# a couple different analysis?



# When you're doing the write up, you could talk about checking robots.txt
# to make sure your scraping is cool


