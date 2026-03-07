"""SF food & drink events scraper.

Sources: Eater SF, SF Beer Week, SF Food Wars, 7x7 SF dining events, etc.
"""

import json
import requests
from bs4 import BeautifulSoup
from .base import BaseScraper, Event, clean_text, guess_category, parse_datetime, extract_image_from_jsonld, extract_image_from_card

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
}

SOURCES = [
    {
        "url": "https://sf.eater.com/events-guide",
        "base": "https://sf.eater.com",
        "name": "Eater SF",
        "tags": ["Food", "Dining"],
    },
    {
        "url": "https://sf.eater.com/pop-ups-and-events",
        "base": "https://sf.eater.com",
        "name": "Eater SF Pop-ups",
        "tags": ["Food", "Pop-up"],
    },
    {
        "url": "https://www.7x7.com/food-drink",
        "base": "https://www.7x7.com",
        "name": "7x7",
        "tags": ["Food", "Drink"],
    },
    {
        "url": "https://www.sftravel.com/article/san-francisco-food-festivals-and-events",
        "base": "https://www.sftravel.com",
        "name": "SF Travel Food",
        "tags": ["Food", "Festival"],
    },
]


class SFFoodSceneScraper(BaseScraper):
    name = "sf_food"

    def scrape(self) -> list[Event]:
        events = []
        seen = set()

        for source in SOURCES:
            try:
                resp = requests.get(source["url"], headers=HEADERS, timeout=20)
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
                        events.append(Event(
                            title=clean_text(item.get("name", "")),
                            description=clean_text(item.get("description", ""))[:500],
                            start_time=parse_datetime(item.get("startDate", "")),
                            end_time=parse_datetime(item.get("endDate", "")),
                            source_url=ev_url,
                            tags=json.dumps(source["tags"]),
                            category="food",
                            location="San Francisco, CA",
                            image_url=extract_image_from_jsonld(item),
                            source_name=self.name,
                        ))
                except (json.JSONDecodeError, KeyError):
                    continue

            # HTML articles/cards that look event-like
            for card in soup.select("article, .c-entry-box, .event-card, .event-item, .listing-item"):
                link_el = card.select_one("a[href]")
                if not link_el:
                    continue
                href = link_el.get("href", "")
                if href and not href.startswith("http"):
                    href = source["base"] + href
                if not href or href in seen:
                    continue
                seen.add(href)

                title_el = card.select_one("h2, h3, .c-entry-box--compact__title, .event-title")
                title = clean_text(title_el.get_text()) if title_el else ""
                if not title or len(title) < 5:
                    continue

                desc_el = card.select_one("p, .description, .c-entry-box--compact__dek")
                desc = clean_text(desc_el.get_text())[:500] if desc_el else ""

                # Only include if it sounds event-like
                combined = (title + " " + desc).lower()
                event_keywords = ["event", "festival", "tasting", "pop-up", "popup", "dinner",
                                  "brunch", "happy hour", "opening", "launch", "celebration",
                                  "class", "workshop", "tour", "week"]
                if not any(kw in combined for kw in event_keywords):
                    continue

                events.append(Event(
                    title=title,
                    description=desc,
                    start_time=None,
                    source_url=href,
                    tags=json.dumps(source["tags"]),
                    category="food",
                    location="San Francisco, CA",
                    image_url=extract_image_from_card(card),
                    source_name=self.name,
                ))

        return events
