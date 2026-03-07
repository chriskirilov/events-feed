"""SF Travel / tourism events scraper.

Source: https://www.sftravel.com/events
"""

import json
import requests
from bs4 import BeautifulSoup
from .base import BaseScraper, Event, clean_text, guess_category, parse_datetime

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
}

PAGES = [
    "https://www.sftravel.com/events",
    "https://www.sftravel.com/events/festivals",
    "https://www.sftravel.com/events/concerts",
    "https://www.sftravel.com/events/art-exhibits",
]


class SFTravelScraper(BaseScraper):
    name = "sftravel"

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
                            tags=json.dumps(["SF Events"]),
                            category=guess_category(item.get("name", "") + " " + item.get("description", "")),
                            location="San Francisco, CA",
                            source_name=self.name,
                        ))
                except (json.JSONDecodeError, KeyError):
                    continue

            for card in soup.select(".event-card, .event-item, article, .card, .listing-item"):
                link_el = card.select_one("a[href*='/event'], a[href*='/article'], h2 a, h3 a")
                if not link_el:
                    continue
                href = link_el.get("href", "")
                if href and not href.startswith("http"):
                    href = "https://www.sftravel.com" + href
                if not href or href in seen:
                    continue
                seen.add(href)

                title_el = card.select_one("h2, h3, .card-title, .event-title")
                title = clean_text(title_el.get_text()) if title_el else clean_text(link_el.get_text())
                if not title or len(title) < 5:
                    continue

                desc_el = card.select_one("p, .description, .card-description")
                desc = clean_text(desc_el.get_text())[:500] if desc_el else ""

                date_el = card.select_one(".date, time, .event-date")
                date_str = ""
                if date_el:
                    date_str = date_el.get("datetime", "") or clean_text(date_el.get_text())

                events.append(Event(
                    title=title,
                    description=desc,
                    start_time=parse_datetime(date_str),
                    source_url=href,
                    tags=json.dumps(["SF Events"]),
                    category=guess_category(title + " " + desc),
                    location="San Francisco, CA",
                    source_name=self.name,
                ))

        return events
