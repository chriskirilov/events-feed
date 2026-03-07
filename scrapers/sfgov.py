"""SF.gov and SF Parks & Rec events scraper.

Sources:
- https://sf.gov/events
- https://sfrecpark.org/events
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
        "url": "https://sf.gov/events",
        "base": "https://sf.gov",
        "tags": ["Community", "Government", "Free"],
    },
    {
        "url": "https://sfrecpark.org/calendar",
        "base": "https://sfrecpark.org",
        "tags": ["Parks", "Recreation", "Free"],
    },
    {
        "url": "https://sfrecpark.org/events",
        "base": "https://sfrecpark.org",
        "tags": ["Parks", "Recreation", "Free"],
    },
]


class SFGovScraper(BaseScraper):
    name = "sfgov"

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
                            category=guess_category(item.get("name", "")),
                            location="San Francisco, CA",
                            image_url=extract_image_from_jsonld(item),
                            source_name=self.name,
                        ))
                except (json.JSONDecodeError, KeyError):
                    continue

            # HTML parsing
            for card in soup.select(".event, .views-row, .event-item, article, .node--type-event"):
                link_el = card.select_one("a[href]")
                if not link_el:
                    continue
                href = link_el.get("href", "")
                if href and not href.startswith("http"):
                    href = source["base"] + href
                if not href or href in seen:
                    continue
                seen.add(href)

                title_el = card.select_one("h2, h3, .field--name-title, .event-title")
                title = clean_text(title_el.get_text()) if title_el else clean_text(link_el.get_text())
                if not title or len(title) < 3:
                    continue

                desc_el = card.select_one(".field--name-body, .description, p, .summary")
                desc = clean_text(desc_el.get_text())[:500] if desc_el else ""

                date_el = card.select_one(".date, time, .datetime, .field--name-field-date-range")
                date_str = ""
                if date_el:
                    date_str = date_el.get("datetime", "") or clean_text(date_el.get_text())

                loc_el = card.select_one(".location, .field--name-field-location, .venue")
                loc = clean_text(loc_el.get_text()) if loc_el else ""
                location = f"{loc}, San Francisco, CA" if loc else "San Francisco, CA"

                events.append(Event(
                    title=title,
                    description=desc,
                    start_time=parse_datetime(date_str),
                    source_url=href,
                    tags=json.dumps(source["tags"]),
                    category=guess_category(title + " " + desc),
                    location=location,
                    image_url=extract_image_from_card(card),
                    source_name=self.name,
                ))

        return events
