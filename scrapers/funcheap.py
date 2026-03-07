"""SF Funcheap scraper - free and cheap events in SF.

Source: https://sf.funcheap.com
"""

import json
import re
import requests
from bs4 import BeautifulSoup
from .base import BaseScraper, Event, clean_text, guess_category, parse_datetime

BASE_URL = "https://sf.funcheap.com/today/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
}
# Crawl multiple date listing pages
PAGES = [
    "https://sf.funcheap.com/today/",
    "https://sf.funcheap.com/tomorrow/",
    "https://sf.funcheap.com/this-weekend/",
    "https://sf.funcheap.com/this-week/",
]


class FuncheapScraper(BaseScraper):
    name = "funcheap"

    def scrape(self) -> list[Event]:
        events = []
        seen = set()

        for page_url in PAGES:
            try:
                resp = requests.get(page_url, headers=HEADERS, timeout=20)
                resp.raise_for_status()
            except Exception:
                continue

            soup = BeautifulSoup(resp.text, "html.parser")

            for article in soup.select("article, .entry-content .post, .type-post"):
                title_el = article.select_one("h2 a, h3 a, .entry-title a")
                if not title_el:
                    continue
                title = clean_text(title_el.get_text())
                link = title_el.get("href", "")
                if not title or link in seen:
                    continue
                seen.add(link)

                desc_el = article.select_one(".entry-content, .entry-summary, p")
                desc = clean_text(desc_el.get_text())[:500] if desc_el else ""

                # Try to find date/time info
                date_el = article.select_one(".event-date, .date, time")
                date_str = ""
                if date_el:
                    date_str = date_el.get("datetime", "") or clean_text(date_el.get_text())

                # Location
                loc_el = article.select_one(".event-location, .location")
                location = clean_text(loc_el.get_text()) if loc_el else "San Francisco, CA"
                if location and "San Francisco" not in location and "SF" not in location:
                    location = f"{location}, San Francisco, CA"

                # Tags from categories
                tag_els = article.select(".cat-links a, .tag-links a, .post-categories a")
                tags = [clean_text(t.get_text()) for t in tag_els][:5]
                if not tags:
                    tags = ["Free & Cheap"]

                events.append(Event(
                    title=title,
                    description=desc,
                    start_time=parse_datetime(date_str),
                    source_url=link,
                    tags=json.dumps(tags),
                    category=guess_category(title + " " + desc),
                    location=location,
                    source_name=self.name,
                ))

        return events
