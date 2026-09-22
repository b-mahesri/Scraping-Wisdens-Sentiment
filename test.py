# Functions to help testing
from pprint import pprint


def print_urls(urls):
    print("\n" * 1)
    for i, url in enumerate(urls):
        print(f"{i + 1}) {url}")
    print("\n" * 1)


def print_article(article):
    preview = article.copy()
    preview["body_text"] = preview["body_text"][:100] + "..."
    print("\n" * 1)
    pprint(preview)
    print("\n" * 1)


def print_db_output(rows):
    for row in rows:
        pprint(row)
        print("\n" * 1)