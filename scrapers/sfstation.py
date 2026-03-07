"""SF Station events scraper.

Source: https://www.sfstation.com/events/
"""

import json
import requests
from bs4 import BeautifulSoup
from .base import BaseScraper, Event, clean_text, guess_category, parse_datetime

BASE_URL = "https://www.sfstation.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
}

CATEGORY_PAGES = [
    "/events/",
    "/events/music/",
    "/events/art/",
    "/events/nightlife/",
    "/events/food-and-drink/",
    "/events/community/",
    "/events/comedy/",
    "/events/sports/",
    "/events/family/",
]


class SFStationScraper(BaseScraper):
    name = "sfstation"

    def scrape(self) -> list[Event]:
        events = []
        seen = set()

        for path in CATEGORY_PAGES:
            url = BASE_URL + path
            try:
                resp = requests.get(url, headers=HEADERS, timeout=20)
                resp.raise_for_status()
            except Exception:
                continue

            soup = BeautifulSoup(resp.text, "html.parser")

            for item in soup.select(".event-item, .event-listing, .event-card, article"):
                link_el = item.select_one("a[href*='/event/'], a[href*='/events/'], h2 a, h3 a")
                if not link_el:
                    continue
                href = link_el.get("href", "")
                if href and not href.startswith("http"):
                    href = BASE_URL + href
                if not href or href in seen:
                    continue
                seen.add(href)

                title = clean_text(link_el.get_text())
                if not title:
                    continue

                desc_el = item.select_one(".event-description, .description, p")
                desc = clean_text(desc_el.get_text())[:500] if desc_el else ""

                date_el = item.select_one(".event-date, .date, time, .when")
                date_str = ""
                if date_el:
                    date_str = date_el.get("datetime", "") or clean_text(date_el.get_text())

                venue_el = item.select_one(".venue, .location, .where")
                venue = clean_text(venue_el.get_text()) if venue_el else ""

                location = f"{venue}, San Francisco, CA" if venue else "San Francisco, CA"

                cat_hint = path.split("/events/")[-1].rstrip("/") if "/events/" in path else ""
                combined_text = f"{title} {desc} {cat_hint}"

                events.append(Event(
                    title=title,
                    description=desc,
                    start_time=parse_datetime(date_str),
                    source_url=href,
                    tags=json.dumps([cat_hint.replace("-", " ").title()] if cat_hint else ["Events"]),
                    category=guess_category(combined_text),
                    location=location,
                    source_name=self.name,
                ))

        return events
