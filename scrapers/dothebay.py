"""DoTheBay scraper - comprehensive Bay Area event listings.

Source: https://dothebay.com
Crawls daily event pages, category pages, and venue pages for
the full breadth of Bay Area events.
"""

import json
import logging
import re
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup

from .base import BaseScraper, Event, clean_text, guess_category, parse_datetime

logger = logging.getLogger(__name__)

BASE = "https://dothebay.com"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

# DoTheBay category slugs
CATEGORIES = [
    "music",
    "arts",
    "food-drink",
    "nightlife",
    "sports",
    "comedy",
    "community",
    "family",
    "film",
    "health-wellness",
]

DAYS_AHEAD = 30


def _build_daily_urls() -> list[tuple[str, str]]:
    """Generate (url, date_str) tuples for daily pages."""
    urls = []
    today = datetime.now().date()
    for offset in range(DAYS_AHEAD + 1):
        d = today + timedelta(days=offset)
        url = f"{BASE}/events/{d.strftime('%Y/%m/%-d')}"
        urls.append((url, d.strftime("%Y-%m-%d")))
    return urls


def _build_category_urls() -> list[str]:
    """Generate URLs for category pages for the next 30 days."""
    urls = []
    today = datetime.now().date()
    # Crawl category pages for today, +7, +14, +21, +28 days
    for offset in [0, 7, 14, 21, 28]:
        d = today + timedelta(days=offset)
        for cat in CATEGORIES:
            urls.append(f"{BASE}/events/{cat}/{d.strftime('%Y/%m/%-d')}")
    return urls


def _fetch_page(url: str, session: requests.Session) -> BeautifulSoup | None:
    """Fetch and parse a page."""
    try:
        resp = session.get(url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, "html.parser")
    except Exception as e:
        logger.debug(f"[dothebay] Failed to fetch {url}: {e}")
        return None


def _extract_events_from_page(
    soup: BeautifulSoup, page_url: str, fallback_date: str, seen: set
) -> list[Event]:
    """Extract events from a DoTheBay listing page."""
    events = []

    # DoTheBay uses structured event cards
    # Try JSON-LD first
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

                # Extract location
                loc = "San Francisco, CA"
                location_data = item.get("location", {})
                if isinstance(location_data, dict):
                    venue_name = location_data.get("name", "")
                    addr = location_data.get("address", {})
                    if isinstance(addr, dict):
                        city = addr.get("addressLocality", "")
                        state = addr.get("addressRegion", "")
                        if venue_name and city:
                            loc = f"{venue_name}, {city}, {state}"
                        elif city:
                            loc = f"{city}, {state}"

                events.append(Event(
                    title=clean_text(item.get("name", "")),
                    description=clean_text(item.get("description", ""))[:500],
                    start_time=parse_datetime(item.get("startDate", "")),
                    end_time=parse_datetime(item.get("endDate", "")),
                    source_url=ev_url,
                    tags=json.dumps(_extract_tags_from_jsonld(item)),
                    category=guess_category(
                        item.get("name", "") + " " + item.get("description", "")
                    ),
                    location=loc,
                    source_name="dothebay",
                ))
        except (json.JSONDecodeError, KeyError, TypeError):
            continue

    # Fallback: parse event cards from HTML
    card_selectors = [
        ".event-card",
        ".ds-listing",
        ".ds-events-group .ds-event",
        "a[href*='/events/']",
        ".event-list-item",
        ".card",
    ]
    for sel in card_selectors:
        cards = soup.select(sel)
        if cards:
            break
    else:
        cards = []

    for card in cards:
        # Get link
        link_el = card if card.name == "a" else card.select_one("a[href]")
        if not link_el:
            continue
        href = link_el.get("href", "")
        if not href:
            continue
        # Make absolute
        if href.startswith("/"):
            href = BASE + href
        if href in seen:
            continue
        if "/events/" not in href:
            continue
        seen.add(href)

        # Title
        title_el = card.select_one(
            "h2, h3, h4, .event-title, .ds-listing-event-title, "
            ".title, [class*='title']"
        )
        title = clean_text(title_el.get_text()) if title_el else ""
        if not title:
            title = clean_text(link_el.get_text())[:120]
        if not title or len(title) < 3:
            continue

        # Date
        date_el = card.select_one(
            "time, .event-date, .ds-listing-event-date, .date, "
            "[class*='date']"
        )
        date_str = ""
        if date_el:
            date_str = date_el.get("datetime", "") or clean_text(date_el.get_text())
        if not date_str:
            date_str = fallback_date

        # Venue / location
        venue_el = card.select_one(
            ".event-venue, .ds-venue-name, .venue, .location, "
            "[class*='venue']"
        )
        loc = clean_text(venue_el.get_text()) if venue_el else "San Francisco, CA"

        # Price
        price_el = card.select_one(
            ".event-cost, .price, .ds-listing-event-price, [class*='price']"
        )
        price = clean_text(price_el.get_text()) if price_el else ""

        # Description snippet
        desc_el = card.select_one(".description, .snippet, p")
        desc = clean_text(desc_el.get_text())[:300] if desc_el else ""
        if price and price not in desc:
            desc = f"[{price}] {desc}" if desc else price

        # Category from URL
        cat_match = re.search(r"/events/(\w[\w-]*)/\d{4}", page_url)
        url_cat = cat_match.group(1) if cat_match else ""

        tags = [url_cat.replace("-", " ").title()] if url_cat else []
        if price and "free" in price.lower():
            tags.append("Free")
        if not tags:
            tags = ["Bay Area Events"]

        events.append(Event(
            title=title,
            description=desc,
            start_time=parse_datetime(date_str),
            source_url=href,
            tags=json.dumps(tags),
            category=guess_category(title + " " + desc + " " + url_cat),
            location=loc,
            source_name="dothebay",
        ))

    return events


def _extract_tags_from_jsonld(item: dict) -> list[str]:
    """Extract tags from JSON-LD event data."""
    tags = []
    for key in ("keywords", "genre", "eventType"):
        val = item.get(key)
        if isinstance(val, str):
            tags.extend(t.strip() for t in val.split(","))
        elif isinstance(val, list):
            tags.extend(str(v) for v in val)
    return tags[:5] if tags else ["Bay Area Events"]


class DoTheBayScraper(BaseScraper):
    name = "dothebay"

    def scrape(self) -> list[Event]:
        events = []
        seen = set()
        session = requests.Session()

        # 1. Crawl daily listing pages
        daily_urls = _build_daily_urls()
        logger.info(f"[dothebay] Crawling {len(daily_urls)} daily pages...")
        for url, date_str in daily_urls:
            soup = _fetch_page(url, session)
            if soup:
                page_events = _extract_events_from_page(soup, url, date_str, seen)
                events.extend(page_events)
                logger.debug(f"[dothebay] {url} -> {len(page_events)} events")

        # 2. Crawl category pages (sampled dates)
        cat_urls = _build_category_urls()
        logger.info(f"[dothebay] Crawling {len(cat_urls)} category pages...")
        for url in cat_urls:
            date_match = re.search(r"/(\d{4})/(\d{2})/(\d+)$", url)
            fallback = ""
            if date_match:
                y, m, d = date_match.groups()
                fallback = f"{y}-{m}-{d.zfill(2)}"
            soup = _fetch_page(url, session)
            if soup:
                page_events = _extract_events_from_page(soup, url, fallback, seen)
                events.extend(page_events)

        # 3. Crawl venue pages for major SF venues
        venue_slugs = [
            "the-fillmore", "the-chapel", "the-independent",
            "great-american-music-hall", "the-warfield", "august-hall",
            "bottom-of-the-hill", "punch-line-san-francisco",
            "cobbs-comedy-club", "public-works", "1015-folsom",
            "the-regency-ballroom", "cafe-du-nord", "brick-mortar-music-hall",
            "yoshis-oakland", "the-uc-theatre", "the-freight",
            "the-guild-theatre", "fox-theater-oakland",
        ]
        logger.info(f"[dothebay] Crawling {len(venue_slugs)} venue pages...")
        for slug in venue_slugs:
            url = f"{BASE}/venues/{slug}"
            soup = _fetch_page(url, session)
            if soup:
                page_events = _extract_events_from_page(soup, url, "", seen)
                events.extend(page_events)

        # 4. Enrich short descriptions from detail pages
        for ev in events:
            if ev.source_url and len(ev.description) < 50:
                detail = _fetch_page(ev.source_url, session)
                if detail:
                    content = detail.select_one(
                        ".event-detail-description, .ds-event-description, "
                        ".event-description, article .content, .description"
                    )
                    if content:
                        ev.description = clean_text(content.get_text())[:500]

        logger.info(f"[dothebay] Total: {len(events)} unique events")
        return events
