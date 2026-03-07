"""Do415 scraper - curated SF events.

Source: https://do415.com
"""

import json
import requests
from bs4 import BeautifulSoup
from .base import BaseScraper, Event, clean_text, guess_category, parse_datetime

BASE_URL = "https://do415.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
}

PAGES = [
    "/events/today",
    "/events/tomorrow",
    "/events/this-weekend",
    "/events/this-week",
]


class Do415Scraper(BaseScraper):
    name = "do415"

    def scrape(self) -> list[Event]:
        events = []
        seen = set()

        for path in PAGES:
            url = BASE_URL + path
            try:
                resp = requests.get(url, headers=HEADERS, timeout=20)
                resp.raise_for_status()
            except Exception:
                continue

            soup = BeautifulSoup(resp.text, "html.parser")

            # Look for JSON-LD
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
                        events.append(Event(
                            title=clean_text(item.get("name", "")),
                            description=clean_text(item.get("description", ""))[:500],
                            start_time=parse_datetime(item.get("startDate", "")),
                            end_time=parse_datetime(item.get("endDate", "")),
                            source_url=ev_url,
                            tags=json.dumps(["Events"]),
                            category=guess_category(item.get("name", "") + " " + item.get("description", "")),
                            location=self._loc_from_ld(item),
                            source_name=self.name,
                        ))
                except (json.JSONDecodeError, KeyError):
                    continue

            # Parse event cards
            for card in soup.select(".event-card, .event-item, .event-listing, article.event"):
                link_el = card.select_one("a[href*='/event'], h2 a, h3 a, a.event-link")
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

                desc_el = card.select_one(".event-description, .description, p")
                desc = clean_text(desc_el.get_text())[:500] if desc_el else ""

                date_el = card.select_one(".event-date, .date, time")
                date_str = ""
                if date_el:
                    date_str = date_el.get("datetime", "") or clean_text(date_el.get_text())

                venue_el = card.select_one(".venue, .location")
                venue = clean_text(venue_el.get_text()) if venue_el else ""
                location = f"{venue}, San Francisco, CA" if venue else "San Francisco, CA"

                events.append(Event(
                    title=title,
                    description=desc,
                    start_time=parse_datetime(date_str),
                    source_url=href,
                    tags=json.dumps(["Events"]),
                    category=guess_category(title + " " + desc),
                    location=location,
                    source_name=self.name,
                ))

        return events

    def _loc_from_ld(self, item: dict) -> str:
        loc = item.get("location", {})
        if isinstance(loc, dict):
            name = loc.get("name", "")
            addr = loc.get("address", {})
            if isinstance(addr, dict):
                city = addr.get("addressLocality", "San Francisco")
                return f"{name}, {city}, CA" if name else f"{city}, CA"
            return f"{name}, San Francisco, CA" if name else "San Francisco, CA"
        return "San Francisco, CA"
