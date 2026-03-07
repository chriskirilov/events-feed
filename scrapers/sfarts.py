"""SF Arts Commission / various SF museum & arts venue scrapers.

Covers: SFMOMA, de Young, Asian Art Museum, Yerba Buena Center for the Arts,
SF Jazz, SF Symphony, The Fillmore, etc.
"""

import json
import requests
from bs4 import BeautifulSoup
from .base import BaseScraper, Event, clean_text, guess_category, parse_datetime, extract_image_from_jsonld, extract_image_from_card

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
}

VENUE_PAGES = [
    {
        "name": "SFMOMA",
        "url": "https://www.sfmoma.org/events/",
        "location": "SFMOMA, San Francisco, CA",
        "tags": ["Art", "Museum"],
    },
    {
        "name": "Asian Art Museum",
        "url": "https://asianart.org/events/",
        "location": "Asian Art Museum, San Francisco, CA",
        "tags": ["Art", "Museum", "Culture"],
    },
    {
        "name": "de Young Museum",
        "url": "https://www.famsf.org/calendar",
        "location": "de Young Museum, San Francisco, CA",
        "tags": ["Art", "Museum"],
    },
    {
        "name": "YBCA",
        "url": "https://ybca.org/events/",
        "location": "Yerba Buena Center for the Arts, San Francisco, CA",
        "tags": ["Art", "Performance"],
    },
    {
        "name": "SF Jazz",
        "url": "https://www.sfjazz.org/events/",
        "location": "SFJAZZ Center, San Francisco, CA",
        "tags": ["Jazz", "Music", "Live Performance"],
    },
    {
        "name": "SF Symphony",
        "url": "https://www.sfsymphony.org/events",
        "location": "Davies Symphony Hall, San Francisco, CA",
        "tags": ["Classical", "Music", "Symphony"],
    },
    {
        "name": "The Fillmore",
        "url": "https://www.livenation.com/venue/KovZpZAJAteA/the-fillmore-events",
        "location": "The Fillmore, San Francisco, CA",
        "tags": ["Music", "Concert", "Live"],
    },
    {
        "name": "The Chapel",
        "url": "https://www.thechapelsf.com/events",
        "location": "The Chapel, San Francisco, CA",
        "tags": ["Music", "Concert", "Live"],
    },
    {
        "name": "Great American Music Hall",
        "url": "https://www.slimspresents.com/calendar/",
        "location": "Great American Music Hall, San Francisco, CA",
        "tags": ["Music", "Concert"],
    },
    {
        "name": "Exploratorium",
        "url": "https://www.exploratorium.edu/events",
        "location": "Exploratorium, San Francisco, CA",
        "tags": ["Science", "Family", "Museum"],
    },
    {
        "name": "California Academy of Sciences",
        "url": "https://www.calacademy.org/events",
        "location": "California Academy of Sciences, San Francisco, CA",
        "tags": ["Science", "Family", "Nightlife"],
    },
    {
        "name": "SF Public Library",
        "url": "https://sfpl.org/events",
        "location": "SF Public Library, San Francisco, CA",
        "tags": ["Community", "Free", "Education"],
    },
]


class SFArtsScraper(BaseScraper):
    name = "sf_arts_venues"

    def scrape(self) -> list[Event]:
        events = []
        seen = set()

        for venue in VENUE_PAGES:
            try:
                resp = requests.get(venue["url"], headers=HEADERS, timeout=20)
                resp.raise_for_status()
            except Exception:
                continue

            soup = BeautifulSoup(resp.text, "html.parser")

            # JSON-LD extraction
            for script in soup.find_all("script", type="application/ld+json"):
                try:
                    data = json.loads(script.string)
                    items = data if isinstance(data, list) else [data]
                    for item in items:
                        if item.get("@type") not in ("Event", "MusicEvent", "TheaterEvent", "EducationEvent"):
                            continue
                        ev_url = item.get("url", venue["url"])
                        if ev_url in seen:
                            continue
                        seen.add(ev_url)
                        events.append(Event(
                            title=clean_text(item.get("name", "")),
                            description=clean_text(item.get("description", ""))[:500],
                            start_time=parse_datetime(item.get("startDate", "")),
                            end_time=parse_datetime(item.get("endDate", "")),
                            source_url=ev_url,
                            tags=json.dumps(venue["tags"]),
                            category=guess_category(item.get("name", "") + " " + " ".join(venue["tags"])),
                            location=venue["location"],
                            image_url=extract_image_from_jsonld(item),
                            source_name=self.name,
                        ))
                except (json.JSONDecodeError, KeyError):
                    continue

            # Generic HTML card parsing
            selectors = [
                ".event-card", ".event-item", ".event-listing",
                "article.event", ".calendar-event", ".program-item",
                ".events-list-item", ".event-row",
            ]
            for sel in selectors:
                for card in soup.select(sel):
                    link_el = card.select_one("a[href]")
                    if not link_el:
                        continue
                    href = link_el.get("href", "")
                    if href and not href.startswith("http"):
                        base = venue["url"].rstrip("/").rsplit("/", 1)[0]
                        href = base + "/" + href.lstrip("/")
                    if not href or href in seen:
                        continue
                    seen.add(href)

                    title_el = card.select_one("h2, h3, h4, .title, .event-title")
                    title = clean_text(title_el.get_text()) if title_el else clean_text(link_el.get_text())
                    if not title or len(title) < 3:
                        continue

                    desc_el = card.select_one(".description, .summary, p")
                    desc = clean_text(desc_el.get_text())[:500] if desc_el else ""

                    date_el = card.select_one(".date, time, .event-date, .start-date")
                    date_str = ""
                    if date_el:
                        date_str = date_el.get("datetime", "") or clean_text(date_el.get_text())

                    events.append(Event(
                        title=title,
                        description=desc,
                        start_time=parse_datetime(date_str),
                        source_url=href,
                        tags=json.dumps(venue["tags"]),
                        category=guess_category(title + " " + " ".join(venue["tags"])),
                        location=venue["location"],
                        image_url=extract_image_from_card(card),
                        source_name=self.name,
                    ))

        return events
