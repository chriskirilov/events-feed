"""Lu.ma scraper - tech, startup, and community events in SF.

Source: https://lu.ma (also https://luma.com)
Lu.ma is heavily used for SF tech/startup events, AI meetups,
founder dinners, and community gatherings. It has both a public
event discovery page and individual calendar pages.

Lu.ma uses a React SPA with API endpoints for event data.
We hit both the public API and HTML pages.
"""

import json
import logging
import re
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup

from .base import BaseScraper, Event, clean_text, guess_category, parse_datetime

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/html, */*",
    "Accept-Language": "en-US,en;q=0.9",
}

# Lu.ma API endpoint for discovering events by city
# The public API serves JSON when called with the right headers
LUMA_API_BASE = "https://api.lu.ma/public/v2"
LUMA_DISCOVER_URL = "https://api.lu.ma/discover/get-events"

# Known SF community calendars on lu.ma with high event volume
CALENDAR_SLUGS = [
    "sfvibe",           # SFVibe - 60k+ subscribers, weekly SF guide
    "sf",               # General SF events
    "san-francisco",    # San Francisco hub
    "demo-night",       # SF Demo Night at SHACK15
    "sv-demo-night",    # Silicon Valley Demo Night
    "startupsocial",    # Startup Social SF
    "sf-founders",      # SF Founders & Investors
    "SFpolitics",       # SF Politics events
    "sffashionpr",      # SF Fashion
    "date-week",        # Date Week SF
    "techstarsweekendsf",  # Techstars Startup Weekend
    "sf-demo",          # SF Demo events
    "monthly-robotics-ai-meetup",  # Monthly Robotics & AI
    "founderslivesf",   # Founders Live SF
]

# Direct event page URLs we know about
KNOWN_EVENT_PAGES = [
    "https://lu.ma/bejuyv7i",   # AGI Builders Meetup
    "https://lu.ma/premier",     # AI Showdown
    "https://lu.ma/ucgvu3v0",   # Open Source AI Meetup
    "https://lu.ma/devs4",      # Local AI developer meetup
    "https://lu.ma/sfd",        # SF Demo Night (GenAI)
    "https://lu.ma/bsype6t6",   # Pre AI Conference Hack Day
]


def _fetch(url: str, session: requests.Session, as_json: bool = False):
    """Fetch URL, return soup or JSON."""
    try:
        resp = session.get(url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
        if as_json:
            return resp.json()
        return BeautifulSoup(resp.text, "html.parser")
    except Exception as e:
        logger.debug(f"[luma] Failed to fetch {url}: {e}")
        return None


def _extract_events_from_html(soup: BeautifulSoup, page_url: str, seen: set) -> list[Event]:
    """Extract events from a lu.ma HTML page."""
    events = []

    # Lu.ma embeds event data in __NEXT_DATA__ script tag (Next.js)
    next_data = soup.select_one("script#__NEXT_DATA__")
    if next_data and next_data.string:
        try:
            data = json.loads(next_data.string)
            props = data.get("props", {}).get("pageProps", {})
            events.extend(_parse_next_data(props, page_url, seen))
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            logger.debug(f"[luma] Failed to parse __NEXT_DATA__: {e}")

    # Also try JSON-LD
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            ld_data = json.loads(script.string)
            items = ld_data if isinstance(ld_data, list) else [ld_data]
            for item in items:
                if item.get("@type") != "Event":
                    continue
                ev_url = item.get("url", page_url)
                if ev_url in seen:
                    continue
                seen.add(ev_url)

                loc = "San Francisco, CA"
                loc_data = item.get("location", {})
                if isinstance(loc_data, dict):
                    venue = loc_data.get("name", "")
                    addr = loc_data.get("address", {})
                    if isinstance(addr, dict):
                        city = addr.get("addressLocality", "")
                        state = addr.get("addressRegion", "")
                        if venue:
                            loc = f"{venue}, {city}, {state}"
                        elif city:
                            loc = f"{city}, {state}"

                events.append(Event(
                    title=clean_text(item.get("name", "")),
                    description=clean_text(item.get("description", ""))[:500],
                    start_time=parse_datetime(item.get("startDate", "")),
                    end_time=parse_datetime(item.get("endDate", "")),
                    source_url=ev_url,
                    tags=json.dumps(["Tech", "Startup", "Community"]),
                    category=guess_category(
                        item.get("name", "") + " " + item.get("description", "")
                    ),
                    location=loc,
                    source_name="luma",
                ))
        except (json.JSONDecodeError, KeyError, TypeError):
            continue

    # Fallback: parse visible HTML content
    # Lu.ma event cards typically have title, date, location
    for card in soup.select(
        "[class*='event-card'], [class*='EventCard'], "
        "[data-testid*='event'], a[href*='/event/']"
    ):
        link_el = card if card.name == "a" else card.select_one("a[href]")
        if not link_el:
            continue
        href = link_el.get("href", "")
        if href.startswith("/"):
            href = "https://lu.ma" + href
        if href in seen:
            continue
        if not href:
            continue
        seen.add(href)

        title = ""
        for sel in ["h2", "h3", "h4", "[class*='title']", "[class*='name']"]:
            el = card.select_one(sel)
            if el:
                title = clean_text(el.get_text())
                break
        if not title:
            title = clean_text(link_el.get_text())[:120]
        if not title or len(title) < 3:
            continue

        date_el = card.select_one("time, [class*='date'], [class*='time']")
        date_str = ""
        if date_el:
            date_str = date_el.get("datetime", "") or clean_text(date_el.get_text())

        loc_el = card.select_one("[class*='location'], [class*='venue']")
        loc = clean_text(loc_el.get_text()) if loc_el else "San Francisco, CA"

        events.append(Event(
            title=title,
            description="",
            start_time=parse_datetime(date_str),
            source_url=href,
            tags=json.dumps(["Tech", "Startup", "Community"]),
            category=guess_category(title),
            location=loc,
            source_name="luma",
        ))

    return events


def _parse_next_data(props: dict, page_url: str, seen: set) -> list[Event]:
    """Parse events from Next.js __NEXT_DATA__ props."""
    events = []

    # Calendar page data
    calendar_events = props.get("initialData", {}).get("events", [])
    if not calendar_events:
        calendar_events = props.get("events", [])
    if not calendar_events:
        # Try nested structures
        for key in ["calendarEvents", "upcomingEvents", "featuredEvents"]:
            calendar_events = props.get(key, [])
            if calendar_events:
                break

    for ev_data in calendar_events:
        # Handle both direct event objects and wrapped ones
        event = ev_data.get("event", ev_data) if isinstance(ev_data, dict) else {}
        if not isinstance(event, dict):
            continue

        title = event.get("name", "") or event.get("title", "")
        if not title:
            continue

        ev_url = ""
        slug = event.get("url", "") or event.get("slug", "")
        api_id = event.get("api_id", "")
        if slug:
            ev_url = f"https://lu.ma/{slug}"
        elif api_id:
            ev_url = f"https://lu.ma/{api_id}"

        if ev_url in seen:
            continue
        if ev_url:
            seen.add(ev_url)

        desc = event.get("description", "") or event.get("description_short", "")

        start = event.get("start_at", "") or event.get("startDate", "")
        end = event.get("end_at", "") or event.get("endDate", "")

        # Location
        loc = "San Francisco, CA"
        geo = event.get("geo_address_info", {})
        if isinstance(geo, dict):
            city = geo.get("city", "")
            region = geo.get("region", "")
            place = geo.get("place_name", "")
            if place and city:
                loc = f"{place}, {city}, {region}"
            elif city:
                loc = f"{city}, {region}"

        location_str = event.get("location_name", "")
        if location_str and loc == "San Francisco, CA":
            loc = location_str

        # Tags
        tags = []
        for tag_field in ["tags", "categories", "topics"]:
            tag_val = event.get(tag_field, [])
            if isinstance(tag_val, list):
                tags.extend(str(t) for t in tag_val)
            elif isinstance(tag_val, str):
                tags.extend(t.strip() for t in tag_val.split(","))
        if not tags:
            tags = ["Tech", "Community"]

        events.append(Event(
            title=clean_text(title),
            description=clean_text(desc)[:500],
            start_time=parse_datetime(start),
            end_time=parse_datetime(end),
            source_url=ev_url or page_url,
            tags=json.dumps(tags[:5]),
            category=guess_category(title + " " + desc),
            location=loc,
            source_name="luma",
        ))

    # Single event page
    event = props.get("event", {})
    if isinstance(event, dict) and event.get("name"):
        title = event.get("name", "")
        slug = event.get("url", "")
        ev_url = f"https://lu.ma/{slug}" if slug else page_url

        if ev_url not in seen:
            seen.add(ev_url)
            desc = event.get("description", "")
            start = event.get("start_at", "")
            end = event.get("end_at", "")

            loc = "San Francisco, CA"
            geo = event.get("geo_address_info", {})
            if isinstance(geo, dict):
                city = geo.get("city", "")
                region = geo.get("region", "")
                if city:
                    loc = f"{city}, {region}"

            events.append(Event(
                title=clean_text(title),
                description=clean_text(desc)[:500],
                start_time=parse_datetime(start),
                end_time=parse_datetime(end),
                source_url=ev_url,
                tags=json.dumps(["Tech", "Community"]),
                category=guess_category(title + " " + desc),
                location=loc,
                source_name="luma",
            ))

    return events


def _try_luma_api(session: requests.Session, seen: set) -> list[Event]:
    """Try to fetch events from lu.ma's public API endpoints."""
    events = []

    # Try the discover endpoint with SF geo filter
    api_urls = [
        f"{LUMA_DISCOVER_URL}?geo_latitude=37.7749&geo_longitude=-122.4194&geo_radius=50",
        "https://api.lu.ma/discover/get-events-for-city?city=san-francisco",
        "https://api.lu.ma/public/v1/calendar/get-items?calendar_api_id=cal-sf",
    ]

    for url in api_urls:
        try:
            resp = session.get(url, headers={
                **HEADERS,
                "x-luma-source": "discover",
            }, timeout=15)
            if resp.status_code != 200:
                continue

            data = resp.json()
            event_list = data.get("events", data.get("entries", data.get("data", [])))
            if not isinstance(event_list, list):
                continue

            for item in event_list:
                ev = item.get("event", item)
                if not isinstance(ev, dict):
                    continue
                title = ev.get("name", "")
                if not title:
                    continue

                slug = ev.get("url", "") or ev.get("slug", "")
                ev_url = f"https://lu.ma/{slug}" if slug else ""
                if ev_url in seen:
                    continue
                if ev_url:
                    seen.add(ev_url)

                events.append(Event(
                    title=clean_text(title),
                    description=clean_text(ev.get("description", ""))[:500],
                    start_time=parse_datetime(ev.get("start_at", "")),
                    end_time=parse_datetime(ev.get("end_at", "")),
                    source_url=ev_url,
                    tags=json.dumps(["Tech", "Community"]),
                    category=guess_category(title + " " + ev.get("description", "")),
                    location="San Francisco, CA",
                    source_name="luma",
                ))
        except Exception as e:
            logger.debug(f"[luma] API request failed: {e}")
            continue

    return events


class LumaScraper(BaseScraper):
    name = "luma"

    def scrape(self) -> list[Event]:
        events = []
        seen = set()
        session = requests.Session()

        # 1. Try the lu.ma API for SF events
        logger.info("[luma] Trying API endpoints...")
        api_events = _try_luma_api(session, seen)
        events.extend(api_events)
        logger.info(f"[luma] API returned {len(api_events)} events")

        # 2. Crawl the SF discovery pages
        discovery_urls = [
            "https://lu.ma/sf",
            "https://luma.com/sf",
            "https://luma.com/san-francisco",
            "https://lu.ma/discover?city=san-francisco",
        ]
        for url in discovery_urls:
            soup = _fetch(url, session)
            if soup:
                page_events = _extract_events_from_html(soup, url, seen)
                events.extend(page_events)
                logger.debug(f"[luma] {url} -> {len(page_events)} events")

        # 3. Crawl known calendar pages
        logger.info(f"[luma] Crawling {len(CALENDAR_SLUGS)} calendar pages...")
        for slug in CALENDAR_SLUGS:
            url = f"https://lu.ma/{slug}"
            soup = _fetch(url, session)
            if soup:
                page_events = _extract_events_from_html(soup, url, seen)
                events.extend(page_events)
                logger.debug(f"[luma] {url} -> {len(page_events)} events")

        # 4. Crawl known event pages
        logger.info(f"[luma] Crawling {len(KNOWN_EVENT_PAGES)} event pages...")
        for url in KNOWN_EVENT_PAGES:
            soup = _fetch(url, session)
            if soup:
                page_events = _extract_events_from_html(soup, url, seen)
                events.extend(page_events)

        # 5. Enrich events with short descriptions
        for ev in events:
            if ev.source_url and len(ev.description) < 50 and "lu.ma" in ev.source_url:
                detail = _fetch(ev.source_url, session)
                if detail:
                    # Try og:description meta
                    og_desc = detail.select_one('meta[property="og:description"]')
                    if og_desc:
                        ev.description = clean_text(og_desc.get("content", ""))[:500]

        logger.info(f"[luma] Total: {len(events)} unique events")
        return events
