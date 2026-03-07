"""Yelp Events scraper for San Francisco.

Source: https://www.yelp.com/events/sf
"""

import json
import requests
from bs4 import BeautifulSoup
from .base import BaseScraper, Event, clean_text, guess_category, parse_datetime, extract_image_from_jsonld, extract_image_from_card

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
}

PAGES = [
    "https://www.yelp.com/events/sf",
    "https://www.yelp.com/events/sf?page=2",
    "https://www.yelp.com/events/sf?page=3",
]


class YelpEventsScraper(BaseScraper):
    name = "yelp_events"

    def scrape(self) -> list[Event]:
        events = []
        seen = set()

        for url in PAGES:
            try:
                resp = requests.get(url, headers=HEADERS, timeout=20)
                resp.raise_for_status()
            except Exception:
                continue

            soup = BeautifulSoup(resp.text, "html.parser")

            # JSON-LD
            for script in soup.find_all("script", type="application/ld+json"):
                try:
                    data = json.loads(script.string)
                    items = data if isinstance(data, list) else [data]
                    for item in items:
                        if item.get("@type") != "Event":
                            continue
                        ev_url = item.get("url", "")
                        if ev_url in seen:
                            continue
                        seen.add(ev_url)
                        loc = item.get("location", {})
                        venue = loc.get("name", "") if isinstance(loc, dict) else ""
                        location = f"{venue}, San Francisco, CA" if venue else "San Francisco, CA"
                        events.append(Event(
                            title=clean_text(item.get("name", "")),
                            description=clean_text(item.get("description", ""))[:500],
                            start_time=parse_datetime(item.get("startDate", "")),
                            end_time=parse_datetime(item.get("endDate", "")),
                            source_url=ev_url,
                            tags=json.dumps(["Yelp Events"]),
                            category=guess_category(item.get("name", "") + " " + item.get("description", "")),
                            location=location,
                            image_url=extract_image_from_jsonld(item),
                            source_name=self.name,
                        ))
                except (json.JSONDecodeError, KeyError):
                    continue

            # HTML event listings
            for card in soup.select(".event-card, .event_listing, li.event"):
                link_el = card.select_one("a[href*='/events/']")
                if not link_el:
                    link_el = card.select_one("a[href]")
                if not link_el:
                    continue
                href = link_el.get("href", "")
                if href and not href.startswith("http"):
                    href = "https://www.yelp.com" + href
                if not href or href in seen:
                    continue
                seen.add(href)

                title_el = card.select_one("h2, h3, .event-title, a span")
                title = clean_text(title_el.get_text()) if title_el else ""
                if not title:
                    continue

                desc_el = card.select_one(".event-description, p")
                desc = clean_text(desc_el.get_text())[:500] if desc_el else ""

                date_el = card.select_one(".event-date, time, .date")
                date_str = ""
                if date_el:
                    date_str = date_el.get("datetime", "") or clean_text(date_el.get_text())

                events.append(Event(
                    title=title,
                    description=desc,
                    start_time=parse_datetime(date_str),
                    source_url=href,
                    tags=json.dumps(["Yelp Events"]),
                    category=guess_category(title + " " + desc),
                    location="San Francisco, CA",
                    image_url=extract_image_from_card(card),
                    source_name=self.name,
                ))

        return events
