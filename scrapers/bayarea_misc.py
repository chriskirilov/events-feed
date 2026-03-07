"""Miscellaneous Bay Area / SF event sources scraper.

Covers smaller but valuable SF event listings:
- The Bold Italic
- SF Weekly
- SFist
- 19th Avenue Events / Sunset & Richmond neighborhood events
- Mission Local
- Hoodline SF
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
        "url": "https://thebolditalic.com/tagged/events",
        "base": "https://thebolditalic.com",
        "name": "The Bold Italic",
        "tags": ["Culture", "Local"],
    },
    {
        "url": "https://www.sfweekly.com/events/",
        "base": "https://www.sfweekly.com",
        "name": "SF Weekly",
        "tags": ["Events", "Entertainment"],
    },
    {
        "url": "https://sfist.com/category/events/",
        "base": "https://sfist.com",
        "name": "SFist",
        "tags": ["Events", "Local"],
    },
    {
        "url": "https://hoodline.com/neighborhood/san-francisco/events",
        "base": "https://hoodline.com",
        "name": "Hoodline",
        "tags": ["Neighborhood", "Local"],
    },
    {
        "url": "https://missionlocal.org/category/events/",
        "base": "https://missionlocal.org",
        "name": "Mission Local",
        "tags": ["Mission District", "Local"],
    },
    {
        "url": "https://www.timeout.com/san-francisco/things-to-do/things-to-do-in-san-francisco-this-week",
        "base": "https://www.timeout.com",
        "name": "Time Out SF",
        "tags": ["Things to Do", "Curated"],
    },
    {
        "url": "https://www.timeout.com/san-francisco/things-to-do/free-things-to-do-in-san-francisco",
        "base": "https://www.timeout.com",
        "name": "Time Out SF Free",
        "tags": ["Free", "Things to Do"],
    },
]


class BayAreaMiscScraper(BaseScraper):
    name = "bayarea_misc"

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
                        if item.get("@type") not in ("Event", "Article"):
                            continue
                        ev_url = item.get("url", "")
                        if ev_url in seen:
                            continue
                        seen.add(ev_url)
                        if item.get("@type") == "Event":
                            events.append(Event(
                                title=clean_text(item.get("name", "")),
                                description=clean_text(item.get("description", ""))[:500],
                                start_time=parse_datetime(item.get("startDate", "")),
                                end_time=parse_datetime(item.get("endDate", "")),
                                source_url=ev_url,
                                tags=json.dumps(source["tags"]),
                                category=guess_category(item.get("name", "")),
                                location="San Francisco, CA",
                                image_url=extract_image_from_jsonld(item),
                                source_name=self.name,
                            ))
                except (json.JSONDecodeError, KeyError):
                    continue

            # HTML articles
            for card in soup.select("article, .post, .event-card, .event-item, .card, .listing"):
                link_el = card.select_one("a[href]")
                if not link_el:
                    continue
                href = link_el.get("href", "")
                if href and not href.startswith("http"):
                    href = source["base"] + href
                if not href or href in seen:
                    continue
                seen.add(href)

                title_el = card.select_one("h2, h3, h4, .title, .entry-title, .card-title")
                title = clean_text(title_el.get_text()) if title_el else ""
                if not title or len(title) < 5:
                    continue

                desc_el = card.select_one("p, .excerpt, .description, .entry-summary")
                desc = clean_text(desc_el.get_text())[:500] if desc_el else ""

                # Filter for event-like content
                combined = (title + " " + desc).lower()
                event_signals = ["event", "festival", "show", "concert", "exhibition",
                                 "opening", "party", "fair", "market", "parade",
                                 "celebration", "performance", "tour", "walk",
                                 "popup", "pop-up", "tasting", "screening"]
                if not any(sig in combined for sig in event_signals):
                    continue

                date_el = card.select_one("time, .date, .published")
                date_str = ""
                if date_el:
                    date_str = date_el.get("datetime", "") or clean_text(date_el.get_text())

                events.append(Event(
                    title=title,
                    description=desc,
                    start_time=parse_datetime(date_str),
                    source_url=href,
                    tags=json.dumps(source["tags"]),
                    category=guess_category(title + " " + desc),
                    location="San Francisco, CA",
                    image_url=extract_image_from_card(card),
                    source_name=self.name,
                ))

        return events
