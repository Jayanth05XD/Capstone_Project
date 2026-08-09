import requests
from bs4 import BeautifulSoup
import urllib.parse
import pandas as pd

BASE = "https://books.toscrape.com/"

CATEGORIES = {
    "Sequential Art": BASE + "catalogue/category/books/sequential-art_5/index.html",
    "Fiction": BASE + "catalogue/category/books/fiction_10/index.html",
    "NonFiction": BASE + "catalogue/category/books/nonfiction_13/index.html"
}

def parse_book_card(article_tag, category_name):
    title = article_tag.h3.a["title"]
    price = article_tag.find("p", class_="price_color").get_text(strip=True)
    star_rating = article_tag.find("p", class_="star-rating")["class"][1]
    availability = article_tag.find("p", class_="availability").get_text(strip=True)

    return {
        "title": title,
        "price": price,
        "star_rating": star_rating,
        "availability": availability,
        "category": category_name
    }

def scrape_category(start_url, category_name):
    books = []
    url = start_url
    while url:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        resp.encoding = "utf-8"
        soup = BeautifulSoup(resp.text, "html.parser")
        tags = soup.find_all("article", class_="product_pod")
        for tag in tags:
            book = parse_book_card(tag, category_name)
            books.append(book)
        next_li = soup.find("li", class_="next")
        if next_li:
            next_href = next_li.a["href"]
            url = urllib.parse.urljoin(url, next_href)
        else:
            url = None
    return books

all_books = []
for name, url in CATEGORIES.items():
    books = scrape_category(url, name)
    all_books.extend(books)

print(f"Total Books: {len(all_books)}")
categories_found = set(
    book['category']
    for book in all_books
)

print("Categories found:", categories_found)
pd.DataFrame(all_books).to_csv("raw_books.csv", index=False)

print("Saved raw_books.csv")