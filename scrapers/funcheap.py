"""SF Funcheap scraper - free and cheap events in SF.

Source: https://sf.funcheap.com
Crawls daily listing pages for the current month + next 30 days,
plus category pages, to capture the full breadth of events.
"""

import json
import logging
import re
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup

from .base import BaseScraper, Event, clean_text, guess_category, parse_datetime

logger = logging.getLogger(__name__)

BASE = "https://sf.funcheap.com"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

# Category archive pages on funcheap
CATEGORY_PAGES = [
    f"{BASE}/category/event/event-types/fairs-festivals/",
    f"{BASE}/category/event/event-types/free-museum-days/",
    f"{BASE}/category/outdoors/",
    f"{BASE}/category/event/event-types/nightlife/",
    f"{BASE}/category/event/event-types/art/",
    f"{BASE}/category/event/event-types/music-2/",
    f"{BASE}/category/event/event-types/food-drink/",
    f"{BASE}/category/event/event-types/sports-active/",
    f"{BASE}/category/event/event-types/community/",
    f"{BASE}/category/event/event-types/comedy/",
    f"{BASE}/category/event/event-types/kids-family/",
    f"{BASE}/category/event/event-types/classes-workshops/",
]

# How many days ahead to crawl daily pages
DAYS_AHEAD = 30


def _build_daily_urls() -> list[str]:
    """Generate URLs for daily listing pages from today through DAYS_AHEAD."""
    urls = []
    today = datetime.now().date()
    for offset in range(DAYS_AHEAD + 1):
        d = today + timedelta(days=offset)
        urls.append(f"{BASE}/{d.strftime('%Y/%m/%d')}/")
    return urls


def _extract_events_from_page(soup: BeautifulSoup, page_url: str, seen: set) -> list[Event]:
    """Parse event listings from a funcheap page."""
    events = []

    # Funcheap uses <article> elements or .tdb_module_loop for each event
    selectors = [
        "article",
        ".tdb_module_loop",
        ".td-block-span12",
        ".td-module-container",
        ".entry",
    ]
    articles = []
    for sel in selectors:
        articles = soup.select(sel)
        if articles:
            break

    if not articles:
        # Fallback: look for any post links
        articles = soup.select(".type-post, .post")

    for article in articles:
        # Find title link
        title_el = article.select_one(
            "h2 a, h3 a, .entry-title a, .td-module-title a, "
            ".tdb-title-text a"
        )
        if not title_el:
            continue

        title = clean_text(title_el.get_text())
        link = title_el.get("href", "")

        if not title or not link:
            continue
        if link in seen:
            continue
        seen.add(link)

        # Description
        desc = ""
        desc_el = article.select_one(
            ".entry-content, .entry-summary, .td-excerpt, "
            ".tdb-block-inner p, .td-post-text-content"
        )
        if desc_el:
            desc = clean_text(desc_el.get_text())[:500]

        # Date/time
        date_str = ""
        date_el = article.select_one("time, .event-date, .date, .td-post-date")
        if date_el:
            date_str = date_el.get("datetime", "") or clean_text(date_el.get_text())

        # Try extracting date from URL pattern /YYYY/MM/DD/
        if not date_str:
            m = re.search(r"/(\d{4}/\d{2}/\d{2})/", link)
            if m:
                date_str = m.group(1).replace("/", "-")

        # Location
        loc = "San Francisco, CA"
        loc_el = article.select_one(".event-location, .location, .venue")
        if loc_el:
            loc_text = clean_text(loc_el.get_text())
            if loc_text:
                loc = loc_text

        # Price info
        price_el = article.select_one(".event-cost, .price, .cost")
        price = clean_text(price_el.get_text()) if price_el else ""

        # Tags from categories
        tag_els = article.select(
            ".cat-links a, .tag-links a, .post-categories a, "
            ".td-post-category a"
        )
        tags = [clean_text(t.get_text()) for t in tag_els if t.get_text().strip()][:5]
        if not tags:
            tags = ["Free & Cheap"]
        if price and "free" in price.lower():
            if "Free" not in tags:
                tags.append("Free")

        # Build description with price if available
        if price and price not in desc:
            desc = f"[{price}] {desc}" if desc else price

        events.append(Event(
            title=title,
            description=desc,
            start_time=parse_datetime(date_str),
            source_url=link,
            tags=json.dumps(tags),
            category=guess_category(title + " " + desc),
            location=loc,
            source_name="funcheap",
        ))

    return events


def _fetch_page(url: str, session: requests.Session) -> BeautifulSoup | None:
    """Fetch a page and return parsed soup, or None on failure."""
    try:
        resp = session.get(url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, "html.parser")
    except Exception as e:
        logger.debug(f"[funcheap] Failed to fetch {url}: {e}")
        return None


class FuncheapScraper(BaseScraper):
    name = "funcheap"

    def scrape(self) -> list[Event]:
        events = []
        seen = set()
        session = requests.Session()

        # 1. Crawl daily listing pages for today + next 30 days
        daily_urls = _build_daily_urls()
        logger.info(f"[funcheap] Crawling {len(daily_urls)} daily pages...")
        for url in daily_urls:
            soup = _fetch_page(url, session)
            if soup:
                page_events = _extract_events_from_page(soup, url, seen)
                events.extend(page_events)
                logger.debug(f"[funcheap] {url} -> {len(page_events)} events")

        # 2. Crawl category archive pages (page 1 only)
        logger.info(f"[funcheap] Crawling {len(CATEGORY_PAGES)} category pages...")
        for url in CATEGORY_PAGES:
            soup = _fetch_page(url, session)
            if soup:
                page_events = _extract_events_from_page(soup, url, seen)
                events.extend(page_events)
                logger.debug(f"[funcheap] {url} -> {len(page_events)} events")

        # 3. Crawl the weekend and this-week aggregation pages
        for slug in ["today", "tomorrow", "this-weekend", "this-week", "next-week"]:
            url = f"{BASE}/{slug}/"
            soup = _fetch_page(url, session)
            if soup:
                page_events = _extract_events_from_page(soup, url, seen)
                events.extend(page_events)

        # 4. Follow individual event links for richer descriptions
        # (only for events with short descriptions)
        for ev in events:
            if ev.source_url and len(ev.description) < 50:
                detail_soup = _fetch_page(ev.source_url, session)
                if detail_soup:
                    content = detail_soup.select_one(
                        ".entry-content, .td-post-content, article .tdb-block-inner"
                    )
                    if content:
                        ev.description = clean_text(content.get_text())[:500]

                    # Try to get more precise date from event detail page
                    date_el = detail_soup.select_one(
                        ".event-date, time[datetime], .dtstart"
                    )
                    if date_el and not ev.start_time:
                        dt = date_el.get("datetime", "") or clean_text(date_el.get_text())
                        ev.start_time = parse_datetime(dt)

        logger.info(f"[funcheap] Total: {len(events)} unique events")
        return events
