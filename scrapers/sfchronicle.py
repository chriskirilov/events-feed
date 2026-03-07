"""SF Chronicle / Datebook events scraper.

Source: https://datebook.sfchronicle.com/events
"""

import json
import requests
from bs4 import BeautifulSoup
from .base import BaseScraper, Event, clean_text, guess_category, parse_datetime

BASE_URL = "https://datebook.sfchronicle.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
}

PAGES = [
    "/events",
    "/events/music",
    "/events/art-exhibits",
    "/events/theater",
    "/events/comedy",
    "/events/food-drink",
    "/events/festivals",
    "/events/nightlife",
    "/events/family",
]


class SFChronicleScraper(BaseScraper):
    name = "sfchronicle"

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
                            tags=json.dumps([path.split("/")[-1].replace("-", " ").title() or "Events"]),
                            category=guess_category(item.get("name", "") + " " + item.get("description", "")),
                            location=location,
                            source_name=self.name,
                        ))
                except (json.JSONDecodeError, KeyError):
                    continue

            # HTML cards
            for card in soup.select(".event-card, .event-item, article, .listing-item"):
                link_el = card.select_one("a[href*='/event'], a[href*='/events/'], h2 a, h3 a")
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

                desc_el = card.select_one(".description, .summary, p")
                desc = clean_text(desc_el.get_text())[:500] if desc_el else ""

                date_el = card.select_one(".date, time, .event-date")
                date_str = ""
                if date_el:
                    date_str = date_el.get("datetime", "") or clean_text(date_el.get_text())

                venue_el = card.select_one(".venue, .location")
                venue = clean_text(venue_el.get_text()) if venue_el else ""
                location = f"{venue}, San Francisco, CA" if venue else "San Francisco, CA"

                cat_hint = path.split("/")[-1] if path != "/events" else ""
                events.append(Event(
                    title=title,
                    description=desc,
                    start_time=parse_datetime(date_str),
                    source_url=href,
                    tags=json.dumps([cat_hint.replace("-", " ").title()] if cat_hint else ["Events"]),
                    category=guess_category(title + " " + desc + " " + cat_hint),
                    location=location,
                    source_name=self.name,
                ))

        return events
