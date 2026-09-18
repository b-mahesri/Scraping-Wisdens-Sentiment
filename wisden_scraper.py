import requests
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}


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


def get_archive_page(url):
    response = safe_get(url)
    if response is None:
        return None
    else:
        return response


def get_urls_in_archive_page(response):
    links = []  # To store the 10 article links on an archive page
    html = response.text
    soup = BeautifulSoup(html, "html.parser")

    articles = soup.find_all("article")
    if articles is None:
        return None

    for article in articles:
        a_tag = article.find("a")
        if (a_tag and a_tag.get('href')):  # Handle missing <a> tags and links.
            links.append(a_tag.get('href')) # There is only ever one link within an <article>, therefore this is safe to do.

    print(f"Total {len(links)} article links collected from this archive page")
    return links


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


########## TEST #############


# Reference Links:
# Wisden: https://www.wisden.com
# Requests Documentation: https://requests.readthedocs.io/en/latest/
# Beautiful Soup Documentation: https://beautiful-soup-4.readthedocs.io/en/latest/
# HTTPS Status Codes: https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status