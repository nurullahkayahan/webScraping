import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
import time
from datetime import datetime, timedelta

# MongoDB connection
client = MongoClient("mongodb://localhost:27017")
db = client.smartmaple
collection = db.kitapyurdu

def scrape_kitapyurdu():
    kitapyurdu_url = "https://www.kitapyurdu.com/index.php?route=product/search&filter_name=python&filter_in_stock=1&fuzzy=0&limit=50"
    kitapyurdu_response = requests.get(kitapyurdu_url)
    kitapyurdu_soup = BeautifulSoup(kitapyurdu_response.content, "html.parser")

    kitapyurdu_books = kitapyurdu_soup.find_all("div", class_="name ellipsis")
    kitapyurdu_books_publisher = kitapyurdu_soup.find_all("div", class_="publisher")
    kitapyurdu_books_price = kitapyurdu_soup.find_all("div", class_="price-new")
    kitapyurdu_books_author = kitapyurdu_soup.find_all("div", class_="author")

    for i in range(2, len(kitapyurdu_books)):
        title = kitapyurdu_books[i].find("a").text.strip()
        publisher = kitapyurdu_books_publisher[i].find("a").text.strip()
        price = kitapyurdu_books_price[i].find("span", class_="value").text.strip()

        author_tags = kitapyurdu_books_author[i].find_all("a")
        authors = [author.text.strip() for author in author_tags]

        book_data = {
            "title": title,
            "publisher": publisher,
            "price": price,
            "authors": authors
        }

        # Saving data to MongoDB
        existing_book = collection.find_one({"title": title})
        if existing_book:
            existing_book["authors"].extend(authors)
            collection.update_one({"_id": existing_book["_id"]}, {"$set": existing_book})
        else:
            collection.insert_one(book_data)

    print("Data has been saved to MongoDB.")



current_time = datetime.now()
target_time = current_time.replace(hour=12, minute=0, second=0, microsecond=0)

if current_time > target_time:
    target_time += timedelta(days=1)
sleep_duration = (target_time - current_time).total_seconds()
time.sleep(sleep_duration)

# Run the code and then loop it to run at the same time every day
while True:
    scrape_kitapyurdu()
    time.sleep(86400)  # 24 hour cooldown time in seconds
