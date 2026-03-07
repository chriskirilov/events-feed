"""Eventbrite SF events scraper.

Uses Eventbrite's public search page to find SF events.
"""

import json
import re
import requests
from bs4 import BeautifulSoup
from .base import BaseScraper, Event, clean_text, guess_category, parse_datetime, extract_image_from_jsonld, extract_image_from_card

SEARCH_URL = "https://www.eventbrite.com/d/ca--san-francisco/events/"
CATEGORIES = [
    "music--performances",
    "food--drink",
    "arts",
    "nightlife",
    "health",
    "sports--fitness",
    "family--education",
    "community",
    "tech",
    "film--media",
]
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}


class EventbriteScraper(BaseScraper):
    name = "eventbrite"

    def scrape(self) -> list[Event]:
        events = []
        seen_urls = set()

        for cat_slug in CATEGORIES:
            url = f"https://www.eventbrite.com/d/ca--san-francisco/{cat_slug}/"
            try:
                resp = requests.get(url, headers=HEADERS, timeout=20)
                resp.raise_for_status()
            except Exception:
                continue

            soup = BeautifulSoup(resp.text, "html.parser")

            # Try to find JSON-LD structured data first
            for script in soup.find_all("script", type="application/ld+json"):
                try:
                    data = json.loads(script.string)
                    items = data if isinstance(data, list) else [data]
                    for item in items:
                        if item.get("@type") != "Event":
                            continue
                        ev_url = item.get("url", "")
                        if ev_url in seen_urls:
                            continue
                        seen_urls.add(ev_url)

                        events.append(Event(
                            title=clean_text(item.get("name", "")),
                            description=clean_text(item.get("description", ""))[:500],
                            start_time=parse_datetime(item.get("startDate", "")),
                            end_time=parse_datetime(item.get("endDate", "")),
                            source_url=ev_url,
                            tags=json.dumps(self._extract_tags(item)),
                            category=guess_category(item.get("name", "") + " " + item.get("description", "")),
                            location=self._extract_location(item),
                            image_url=extract_image_from_jsonld(item),
                            source_name=self.name,
                        ))
                except (json.JSONDecodeError, KeyError):
                    continue

            # Fallback: parse event cards from HTML
            for card in soup.select("a[data-testid='event-card-link'], .search-event-card-wrapper a, .eds-event-card-content__primary-content a"):
                href = card.get("href", "")
                if not href or href in seen_urls:
                    continue
                if "eventbrite.com/e/" not in href:
                    continue
                seen_urls.add(href)
                title_el = card.select_one("[data-testid='event-card-title'], .eds-event-card__formatted-name--is-clamped, .event-card__clamp-line--one")
                title = clean_text(title_el.get_text()) if title_el else ""
                if not title:
                    title = clean_text(card.get_text())[:120]

                date_el = card.select_one("[data-testid='event-card-date'], .eds-event-card-content__sub-title")
                date_str = clean_text(date_el.get_text()) if date_el else ""

                loc_el = card.select_one("[data-testid='event-card-location']")
                loc_str = clean_text(loc_el.get_text()) if loc_el else "San Francisco, CA"

                events.append(Event(
                    title=title,
                    description="",
                    start_time=parse_datetime(date_str),
                    source_url=href.split("?")[0],
                    tags=json.dumps([cat_slug.replace("--", " & ").replace("-", " ").title()]),
                    category=guess_category(title + " " + cat_slug),
                    location=loc_str if loc_str else "San Francisco, CA",
                    image_url=extract_image_from_card(card),
                    source_name=self.name,
                ))

        return events

    def _extract_tags(self, item: dict) -> list[str]:
        tags = []
        if "keywords" in item:
            kw = item["keywords"]
            if isinstance(kw, str):
                tags = [t.strip() for t in kw.split(",")][:5]
            elif isinstance(kw, list):
                tags = kw[:5]
        return tags if tags else ["Events"]

    def _extract_location(self, item: dict) -> str:
        loc = item.get("location", {})
        if isinstance(loc, dict):
            addr = loc.get("address", {})
            if isinstance(addr, dict):
                city = addr.get("addressLocality", "San Francisco")
                state = addr.get("addressRegion", "CA")
                venue = loc.get("name", "")
                if venue:
                    return f"{venue}, {city}, {state}"
                return f"{city}, {state}"
        return "San Francisco, CA"
