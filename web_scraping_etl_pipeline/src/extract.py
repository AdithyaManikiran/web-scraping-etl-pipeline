"""Extraction layer for the Books to Scrape practice site."""
from __future__ import annotations
import logging
import time
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://books.toscrape.com/"
HEADERS = {"User-Agent": "AdithyaLearningETL/1.0 (educational practice project)"}

def extract_books(pages: int = 2, delay_seconds: float = 0.5) -> list[dict]:
    """Extract book cards from the first `pages` catalogue pages."""
    if pages < 1:
        raise ValueError("pages must be at least 1")
    session = requests.Session()
    session.headers.update(HEADERS)
    records: list[dict] = []
    page_url = BASE_URL
    for page_num in range(1, pages + 1):
        logging.info("Fetching page %s: %s", page_num, page_url)
        response = session.get(page_url, timeout=20)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        cards = soup.select("article.product_pod")
        if not cards:
            logging.warning("No product cards found on page %s", page_num)
            break
        for card in cards:
            title_node = card.select_one("h3 a")
            price_node = card.select_one(".price_color")
            availability_node = card.select_one(".availability")
            rating_node = card.select_one("p.star-rating")
            if not title_node:
                continue
            rating_classes = rating_node.get("class", []) if rating_node else []
            rating = next((x for x in rating_classes if x in {"One","Two","Three","Four","Five"}), None)
            records.append({
                "title": title_node.get("title") or title_node.get_text(" ", strip=True),
                "price_text": price_node.get_text(" ", strip=True) if price_node else None,
                "availability": availability_node.get_text(" ", strip=True) if availability_node else None,
                "rating_text": rating,
                "product_url": urljoin(page_url, title_node.get("href", "")),
                "source_page": page_num,
            })
        next_link = soup.select_one("li.next a")
        if page_num < pages and next_link:
            page_url = urljoin(page_url, next_link.get("href", ""))
        elif page_num < pages:
            logging.info("No next-page link found; stopping pagination.")
            break
        if page_num < pages and delay_seconds:
            time.sleep(delay_seconds)
    logging.info("Extracted %s records", len(records))
    return records
