import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
import time
from datetime import datetime, timedelta


# MongoDB connection
client = MongoClient("mongodb://localhost:27017")
db = client.smartmaple
collection = db.kitapsepeti
def scrape_kitapsepeti():
    kitapsepeti_url = "https://www.kitapsepeti.com/arama?q=python&stock=1"
    kitapsepeti_response = requests.get(kitapsepeti_url)
    kitapsepeti_soup = BeautifulSoup(kitapsepeti_response.content, "html.parser")

    kitapsepeti_books = kitapsepeti_soup.find_all("div", class_="productItem")

    for book in kitapsepeti_books:
        title_element = book.find("a", class_="text-description")
        title = title_element.text.strip() if title_element else ""

        publisher_element = book.find("a", class_="text-title")
        publisher = publisher_element.text.strip() if publisher_element else ""

        price_element = book.find("div", class_="currentPrice")
        price = price_element.text.strip() if price_element else ""

        author_element = book.find("a", class_="fl col-12 text-title")
        author = author_element.text.strip() if author_element else ""

        book_data = {
            "title": title,
            "publisher": publisher,
            "price": price,
            "author": author
        }

        # Saving data to MongoDB
        existing_book = collection.find_one({"title": title})
        if existing_book:
            existing_book["author"] = author
            collection.update_one({"_id": existing_book["_id"]}, {"$set": existing_book})
        else:
            collection.insert_one(book_data)

    print("Veriler MongoDB'ye kaydedildi.")



current_time = datetime.now()
target_time = current_time.replace(hour=12, minute=0, second=0, microsecond=0)

if current_time > target_time:
    target_time += timedelta(days=1)

sleep_duration = (target_time - current_time).total_seconds()
time.sleep(sleep_duration)

#  Run the code and then loop it to run at the same time every day
while True:
    scrape_kitapsepeti()
    time.sleep(86400)  # 24 hour cooldown time in seconds