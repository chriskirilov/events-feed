"""Meetup.com SF events scraper.

Uses Meetup's public event search pages for San Francisco.
"""

import json
import requests
from bs4 import BeautifulSoup
from .base import BaseScraper, Event, clean_text, guess_category, parse_datetime

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
}

CATEGORY_SLUGS = [
    "tech",
    "arts-culture",
    "career-business",
    "food-drink",
    "health-wellbeing",
    "music",
    "outdoors-adventure",
    "social-activities",
    "sports-fitness",
    "language-ethnic-identity",
]


class MeetupScraper(BaseScraper):
    name = "meetup"

    def scrape(self) -> list[Event]:
        events = []
        seen = set()

        # Main search page
        urls = [
            "https://www.meetup.com/find/?location=San%20Francisco%2C%20CA&source=EVENTS",
        ]
        for slug in CATEGORY_SLUGS:
            urls.append(
                f"https://www.meetup.com/find/?location=San%20Francisco%2C%20CA&source=EVENTS&categoryId={slug}"
            )

        for url in urls:
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
                        venue_name = loc.get("name", "") if isinstance(loc, dict) else ""
                        location = f"{venue_name}, San Francisco, CA" if venue_name else "San Francisco, CA"
                        events.append(Event(
                            title=clean_text(item.get("name", "")),
                            description=clean_text(item.get("description", ""))[:500],
                            start_time=parse_datetime(item.get("startDate", "")),
                            end_time=parse_datetime(item.get("endDate", "")),
                            source_url=ev_url,
                            tags=json.dumps(["Meetup"]),
                            category=guess_category(item.get("name", "") + " " + item.get("description", "")),
                            location=location,
                            source_name=self.name,
                        ))
                except (json.JSONDecodeError, KeyError):
                    continue

            # HTML parsing
            for card in soup.select("[data-testid='categoryResults-eventCard'], .event-card, .searchResult"):
                link_el = card.select_one("a[href*='/events/']")
                if not link_el:
                    continue
                href = link_el.get("href", "")
                if href and not href.startswith("http"):
                    href = "https://www.meetup.com" + href
                if not href or href in seen:
                    continue
                seen.add(href)

                title_el = card.select_one("h2, h3, .event-title, [data-testid='event-name']")
                title = clean_text(title_el.get_text()) if title_el else ""
                if not title:
                    continue

                desc_el = card.select_one(".description, p")
                desc = clean_text(desc_el.get_text())[:500] if desc_el else ""

                date_el = card.select_one("time, .event-date")
                date_str = ""
                if date_el:
                    date_str = date_el.get("datetime", "") or clean_text(date_el.get_text())

                group_el = card.select_one(".group-name, [data-testid='group-name']")
                group_name = clean_text(group_el.get_text()) if group_el else ""

                events.append(Event(
                    title=title,
                    description=desc if desc else f"Hosted by {group_name}" if group_name else "",
                    start_time=parse_datetime(date_str),
                    source_url=href,
                    tags=json.dumps(["Meetup", group_name] if group_name else ["Meetup"]),
                    category=guess_category(title + " " + desc),
                    location="San Francisco, CA",
                    source_name=self.name,
                ))

        return events
