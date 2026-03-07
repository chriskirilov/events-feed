#!/usr/bin/env python3
"""
SF Events Mass Ingestion Pipeline
==================================

Scrapes events from 30+ San Francisco sources, normalizes them,
deduplicates, and merges into the unified event_data.csv feed.

Sources covered:
  - Eventbrite SF (10 categories)
  - SF Funcheap (free & cheap events, 30-day daily pages + category pages)
  - DoTheBay (Bay Area events, 30-day daily + category + venue pages)
  - Lu.ma (tech/startup/AI meetups, SF calendars, API + HTML scraping)
  - SF Station (music, art, nightlife, food, comedy, sports, family, community)
  - Do415 (curated SF events)
  - SF Chronicle / Datebook (music, art, theater, comedy, food, nightlife, family)
  - SF Arts venues (SFMOMA, de Young, Asian Art Museum, YBCA, SF Jazz,
    SF Symphony, The Fillmore, The Chapel, Great American Music Hall,
    Exploratorium, California Academy of Sciences, SF Public Library)
  - Meetup SF (tech, arts, food, health, music, outdoors, social, sports)
  - SF.gov & SF Parks & Rec
  - Yelp Events SF
  - Goldstar SF (concerts, comedy, theater, sports, nightlife, food)
  - SF Food Scene (Eater SF, 7x7, SF Travel food)
  - SF Travel (festivals, concerts, art exhibits)
  - Bay Area Misc (Bold Italic, SF Weekly, SFist, Hoodline, Mission Local, Time Out SF)

Usage:
    python ingest_sf_events.py [--dry-run] [--sources SOURCE1,SOURCE2] [--verbose]
"""

import argparse
import logging
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

import pandas as pd

from scrapers.base import BaseScraper, Event
from scrapers.eventbrite import EventbriteScraper
from scrapers.funcheap import FuncheapScraper
from scrapers.dothebay import DoTheBayScraper
from scrapers.luma import LumaScraper
from scrapers.sfstation import SFStationScraper
from scrapers.do415 import Do415Scraper
from scrapers.sfchronicle import SFChronicleScraper
from scrapers.sfarts import SFArtsScraper
from scrapers.meetup import MeetupScraper
from scrapers.sfgov import SFGovScraper
from scrapers.yelp_events import YelpEventsScraper
from scrapers.goldstar import GoldstarScraper
from scrapers.sffoodscene import SFFoodSceneScraper
from scrapers.sftravel import SFTravelScraper
from scrapers.bayarea_misc import BayAreaMiscScraper

CSV_PATH = "event_data.csv"

ALL_SCRAPERS: list[BaseScraper] = [
    EventbriteScraper(),
    FuncheapScraper(),
    DoTheBayScraper(),
    LumaScraper(),
    SFStationScraper(),
    Do415Scraper(),
    SFChronicleScraper(),
    SFArtsScraper(),
    MeetupScraper(),
    SFGovScraper(),
    YelpEventsScraper(),
    GoldstarScraper(),
    SFFoodSceneScraper(),
    SFTravelScraper(),
    BayAreaMiscScraper(),
]

SOURCE_NAMES = {s.name for s in ALL_SCRAPERS}


def setup_logging(verbose: bool = False):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )


def scrape_all(scrapers: list[BaseScraper], max_workers: int = 5) -> list[Event]:
    """Run all scrapers concurrently and collect results."""
    all_events: list[Event] = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(s.safe_scrape): s for s in scrapers}
        for future in as_completed(futures):
            scraper = futures[future]
            try:
                events = future.result(timeout=120)
                all_events.extend(events)
            except Exception as e:
                logging.error(f"[{scraper.name}] executor error: {e}")

    return all_events


def deduplicate_events(events: list[Event]) -> list[Event]:
    """Remove duplicate events based on title similarity and URL."""
    seen_urls = set()
    seen_titles = set()
    unique = []

    for ev in events:
        # Skip if same URL
        if ev.source_url and ev.source_url in seen_urls:
            continue

        # Skip if very similar title (normalize for comparison)
        title_key = ev.title.lower().strip()
        title_key = "".join(c for c in title_key if c.isalnum() or c == " ")
        title_key = " ".join(title_key.split())  # normalize whitespace

        if title_key and title_key in seen_titles:
            continue

        if ev.source_url:
            seen_urls.add(ev.source_url)
        if title_key:
            seen_titles.add(title_key)

        unique.append(ev)

    return unique


def filter_sf_events(events: list[Event]) -> list[Event]:
    """Keep only events that are in or near San Francisco."""
    sf_keywords = [
        "san francisco", "sf", "soma", "mission district", "castro",
        "haight", "nob hill", "north beach", "chinatown", "richmond district",
        "sunset district", "marina", "pac heights", "pacific heights",
        "tenderloin", "financial district", "union square", "fisherman",
        "embarcadero", "potrero", "dogpatch", "bayview", "excelsior",
        "glen park", "bernal", "noe valley", "cole valley", "inner sunset",
        "outer sunset", "inner richmond", "outer richmond", "presidio",
        "golden gate", "twin peaks", "treasure island",
    ]

    filtered = []
    for ev in events:
        loc_lower = ev.location.lower()
        title_lower = ev.title.lower()
        # Keep if location mentions SF area
        if any(kw in loc_lower for kw in sf_keywords):
            filtered.append(ev)
        # Keep if title mentions SF
        elif any(kw in title_lower for kw in ["san francisco", "sf "]):
            filtered.append(ev)
        # Keep if location is just the default (scraper was SF-specific)
        elif loc_lower in ("san francisco, ca", "san francisco, california"):
            filtered.append(ev)

    return filtered


def events_to_dataframe(events: list[Event]) -> pd.DataFrame:
    """Convert Event objects to a DataFrame matching event_data.csv schema."""
    records = [ev.to_dict() for ev in events]
    df = pd.DataFrame(records)

    # Ensure column order matches existing CSV
    expected_cols = [
        "creation_date", "title", "description", "start_time", "end_time",
        "region", "source_url", "tags", "category", "location",
    ]
    for col in expected_cols:
        if col not in df.columns:
            df[col] = ""

    return df[expected_cols]


def merge_with_existing(new_df: pd.DataFrame, csv_path: str) -> pd.DataFrame:
    """Merge new events with existing CSV, avoiding duplicates."""
    try:
        existing = pd.read_csv(csv_path)
        logging.info(f"Existing events: {len(existing)}")
    except FileNotFoundError:
        logging.info("No existing CSV found, creating new one")
        return new_df

    # Remove duplicates by source_url
    existing_urls = set(existing["source_url"].dropna().astype(str))
    new_unique = new_df[~new_df["source_url"].astype(str).isin(existing_urls)]

    # Also check by title similarity
    existing_titles = set(
        existing["title"].dropna().str.lower().str.strip()
    )
    new_unique = new_unique[
        ~new_unique["title"].str.lower().str.strip().isin(existing_titles)
    ]

    logging.info(f"New unique events to add: {len(new_unique)}")

    merged = pd.concat([existing, new_unique], ignore_index=True)
    return merged


def print_summary(events: list[Event], scrapers: list[BaseScraper]):
    """Print a summary of scraping results."""
    print("\n" + "=" * 60)
    print("SF EVENTS MASS INGESTION SUMMARY")
    print("=" * 60)

    # Count by source
    source_counts: dict[str, int] = {}
    for ev in events:
        source_counts[ev.source_name] = source_counts.get(ev.source_name, 0) + 1

    print(f"\n{'Source':<25} {'Events':>8}")
    print("-" * 35)
    for scraper in scrapers:
        count = source_counts.get(scraper.name, 0)
        print(f"  {scraper.name:<23} {count:>6}")
    print("-" * 35)
    print(f"  {'TOTAL':<23} {len(events):>6}")

    # Count by category
    cat_counts: dict[str, int] = {}
    for ev in events:
        cat_counts[ev.category] = cat_counts.get(ev.category, 0) + 1

    print(f"\n{'Category':<25} {'Events':>8}")
    print("-" * 35)
    for cat, count in sorted(cat_counts.items(), key=lambda x: -x[1]):
        print(f"  {cat:<23} {count:>6}")

    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="SF Events Mass Ingestion Pipeline")
    parser.add_argument("--dry-run", action="store_true", help="Scrape but don't write to CSV")
    parser.add_argument("--sources", type=str, default="", help="Comma-separated list of sources to run (default: all)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    parser.add_argument("--workers", type=int, default=5, help="Max concurrent scrapers")
    parser.add_argument("--output", type=str, default=CSV_PATH, help="Output CSV path")
    args = parser.parse_args()

    setup_logging(args.verbose)
    logging.info("Starting SF Events Mass Ingestion Pipeline")

    # Select scrapers
    if args.sources:
        selected_names = {s.strip() for s in args.sources.split(",")}
        invalid = selected_names - SOURCE_NAMES
        if invalid:
            print(f"Unknown sources: {invalid}")
            print(f"Available: {sorted(SOURCE_NAMES)}")
            sys.exit(1)
        scrapers = [s for s in ALL_SCRAPERS if s.name in selected_names]
    else:
        scrapers = ALL_SCRAPERS

    print(f"\nRunning {len(scrapers)} scrapers with {args.workers} workers...")
    print(f"Sources: {', '.join(s.name for s in scrapers)}\n")

    # Scrape
    start = time.time()
    raw_events = scrape_all(scrapers, max_workers=args.workers)
    elapsed = time.time() - start
    logging.info(f"Scraping completed in {elapsed:.1f}s - {len(raw_events)} raw events")

    # Filter to SF
    sf_events = filter_sf_events(raw_events)
    logging.info(f"After SF filter: {len(sf_events)} events")

    # Deduplicate
    unique_events = deduplicate_events(sf_events)
    logging.info(f"After dedup: {len(unique_events)} events")

    # Summary
    print_summary(unique_events, scrapers)

    if args.dry_run:
        print("\n[DRY RUN] No changes written.")
        return

    if not unique_events:
        print("\nNo new events found.")
        return

    # Convert and merge
    new_df = events_to_dataframe(unique_events)
    merged_df = merge_with_existing(new_df, args.output)

    # Save
    merged_df.to_csv(args.output, index=False)
    print(f"\nSaved {len(merged_df)} total events to {args.output}")
    print(f"  (added {len(merged_df) - len(pd.read_csv(args.output) if False else pd.DataFrame())} new events)")


if __name__ == "__main__":
    main()
