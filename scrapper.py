import requests
from bs4 import BeautifulSoup
import urllib.parse

BASE = "https://books.toscrape.com/"

CATEGORIES = {
    "Sequential Art": BASE + "catalogue/category/books/sequential-art_5/index.html",
    "Fiction": BASE + "catalogue/category/books/fiction_10/index.html",
    "NonFiction": BASE + "catalogue/category/books/nonfiction_13/index.html"
}

def Parse_book_card(article_tag, category_name):
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
        resp = requests.get(url)
        soup = BeautifulSoup(resp.text, "html.parser")
        tags = soup.find_all("article", class_="product_pod")
        for tag in tags:
            book = Parse_book_card(tag, category_name)
            books.append(book)
        next_li = soup.find("li", class_="next")
        if next_li:
            next_href = next_li.a["href"]
            url = urllib.parse.urljoin(url, next_href)
        else:
            url = None
    return books

books = scrape_category(BASE + "catalogue/category/books/sequential-art_5/index.html", "Sequential Art")
print(len(books))
print(books[0])