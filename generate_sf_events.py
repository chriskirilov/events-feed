#!/usr/bin/env python3
"""
SF Events LLM-Based Generator
===============================

Uses an LLM to generate realistic San Francisco events based on
known venues, neighborhoods, and event types. This supplements
the web scrapers when they're unavailable or return limited results.

This uses the same GMI API the main app already uses.

Usage:
    python generate_sf_events.py [--count 200] [--batch-size 20] [--append]
"""

import argparse
import json
import os
import time
from datetime import datetime, timedelta
import random

import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

CSV_PATH = "event_data.csv"

client = OpenAI(
    api_key=os.getenv("GMI_API_KEY"),
    base_url="https://api.gmi-serving.com/v1"
)

# Comprehensive SF venues and neighborhoods for realistic event generation
SF_VENUES = {
    "music": [
        "The Fillmore", "The Warfield", "The Chapel", "Great American Music Hall",
        "The Independent", "Bottom of the Hill", "Bimbo's 365 Club",
        "SFJAZZ Center", "Davies Symphony Hall", "War Memorial Opera House",
        "The Masonic", "August Hall", "Rickshaw Stop", "Slim's",
        "Cafe du Nord", "Hotel Utah Saloon", "Amnesia", "The Knockout",
        "El Rio", "Neck of the Woods",
    ],
    "arts_and_culture": [
        "SFMOMA", "de Young Museum", "Asian Art Museum",
        "Yerba Buena Center for the Arts", "The Exploratorium",
        "California Academy of Sciences", "Museum of the African Diaspora",
        "Contemporary Jewish Museum", "Cartoon Art Museum",
        "Walt Disney Family Museum", "Legion of Honor",
        "SF Public Library - Main Branch", "City Lights Bookstore",
        "The Strand Theater", "ACT - American Conservatory Theater",
        "SF Playhouse", "Magic Theatre", "The Marsh",
        "Roxie Theater", "Balboa Theatre", "Castro Theatre",
    ],
    "food": [
        "Ferry Building Marketplace", "Ghirardelli Square",
        "Off the Grid - Fort Mason", "SoMa StrEat Food Park",
        "Emporium SF", "Public Market Emeryville",
        "Bi-Rite Market", "Rainbow Grocery", "La Cocina Municipal Marketplace",
        "Fisherman's Wharf", "Chinatown", "North Beach restaurants",
        "Mission District taquerias", "Hayes Valley cafes",
        "Inner Sunset restaurants", "Clement Street eateries",
    ],
    "nightlife": [
        "The Stud", "Monarch", "Audio SF", "1015 Folsom",
        "Temple Nightclub", "Public Works", "DNA Lounge",
        "The Endup", "Mezzanine", "Halcyon", "Noir Lounge",
        "Bergerac", "Smuggler's Cove", "Bourbon & Branch",
        "Li Po Cocktail Lounge", "Vesuvio Cafe", "Trick Dog",
        "ABV", "Whitechapel", "Pacific Cocktail Haven",
    ],
    "sports": [
        "Oracle Park", "Chase Center", "Golden Gate Park",
        "Kezar Stadium", "Crissy Field", "Baker Beach",
        "Ocean Beach", "Marina Green", "Dolores Park",
        "McLaren Park", "Lake Merced", "Bay to Breakers route",
        "Embarcadero waterfront", "Presidio trails",
    ],
    "social": [
        "Salesforce Park", "Yerba Buena Gardens",
        "Dolores Park", "Golden Gate Park",
        "Fort Mason Center", "The Presidio",
        "WeWork locations", "Galvanize SF",
        "General Assembly SF", "Capital One Cafe",
        "The Commons SF", "Impact Hub SF",
        "SF Mechanics' Institute", "Internet Archive",
    ],
    "family_and_kids": [
        "California Academy of Sciences", "Exploratorium",
        "Children's Creativity Museum", "Bay Area Discovery Museum",
        "SF Zoo", "Randall Museum", "Golden Gate Park Playground",
        "Koret Children's Quarter", "Yerba Buena Gardens",
        "Pier 39", "Aquarium of the Bay",
    ],
}

SF_NEIGHBORHOODS = [
    "Mission District", "SoMa", "Castro", "Haight-Ashbury",
    "North Beach", "Chinatown", "Nob Hill", "Russian Hill",
    "Marina District", "Pacific Heights", "Japantown",
    "Hayes Valley", "Lower Haight", "Tenderloin",
    "Financial District", "Union Square", "Embarcadero",
    "Fisherman's Wharf", "Potrero Hill", "Dogpatch",
    "Bayview", "Bernal Heights", "Noe Valley", "Glen Park",
    "Inner Sunset", "Outer Sunset", "Inner Richmond", "Outer Richmond",
    "Presidio", "Excelsior", "Visitacion Valley", "Cole Valley",
    "Twin Peaks", "Diamond Heights", "West Portal",
]

EVENT_TYPES_BY_CATEGORY = {
    "music": [
        "Live Concert", "Jazz Night", "DJ Set", "Open Mic Night",
        "Album Release Party", "Battle of the Bands", "Acoustic Session",
        "Symphony Performance", "Opera Night", "Choral Concert",
        "Latin Music Night", "Blues Jam", "Electronic Music Night",
        "Indie Rock Show", "Hip Hop Showcase", "World Music Festival",
    ],
    "arts_and_culture": [
        "Art Exhibition Opening", "Gallery Walk", "Film Screening",
        "Theater Performance", "Comedy Show", "Poetry Reading",
        "Dance Performance", "Photography Exhibition", "Art Workshop",
        "Book Reading & Signing", "Improv Night", "Cultural Festival",
        "Mural Tour", "Craft Workshop", "Literary Reading",
        "Documentary Screening", "Stand-up Comedy Night",
    ],
    "food": [
        "Food Festival", "Wine Tasting", "Beer Festival",
        "Pop-up Dinner", "Cooking Class", "Cocktail Workshop",
        "Farm-to-Table Dinner", "Food Truck Rally", "Brunch Party",
        "Coffee Cupping", "Cheese & Wine Pairing", "Sake Tasting",
        "Street Food Market", "Chef's Table Experience",
        "Baking Class", "Fermentation Workshop",
    ],
    "nightlife": [
        "Dance Party", "Drag Show", "Karaoke Night",
        "Trivia Night", "Happy Hour", "Themed Party",
        "Rooftop Party", "Silent Disco", "Speakeasy Night",
        "Burlesque Show", "Game Night", "Latin Dance Night",
        "80s Night", "90s Party", "Goth Night",
    ],
    "sports": [
        "Giants Game Watch Party", "Warriors Viewing Party",
        "Group Run", "Yoga in the Park", "Outdoor Bootcamp",
        "Hiking Meetup", "Cycling Ride", "Beach Volleyball",
        "Pickup Basketball", "Soccer Match", "Sailing Class",
        "Surfing Lesson", "Rock Climbing Session", "Kickball League",
        "Marathon Training Run", "Paddleboard Tour",
    ],
    "social": [
        "Tech Meetup", "Networking Mixer", "Startup Demo Night",
        "Community Volunteer Day", "Neighborhood Cleanup",
        "Language Exchange", "Board Game Night",
        "Professional Workshop", "Hackathon", "Book Club Meeting",
        "Meditation Circle", "Wellness Workshop",
        "Speed Friending", "Potluck Dinner", "Cultural Exchange",
        "Photography Walk", "Sketch Crawl",
    ],
    "family_and_kids": [
        "Storytime", "Kids Art Workshop", "Family Movie Night",
        "Puppet Show", "Science Discovery Day", "Nature Walk",
        "Family Bike Ride", "Kids Cooking Class", "Zoo Day",
        "Aquarium Visit", "Playground Meetup", "Family Festival",
        "Magic Show", "Family Concert", "Kids Dance Class",
    ],
}

BATCH_PROMPT = """Generate {count} realistic upcoming San Francisco events. Each event should be a real type of event that actually happens in SF, with realistic titles, descriptions, venues, and dates.

Use these SF venues and neighborhoods as inspiration:
Venues: {venues}
Neighborhoods: {neighborhoods}

Requirements:
- Mix of categories: music, arts_and_culture, food, nightlife, sports, social, family_and_kids
- Dates should be within the next 30 days from {today}
- Each event needs: title, description (2-3 sentences), start_time, end_time, venue/location, tags, category
- Make titles creative and specific (not generic)
- Include both free and paid events
- Include both well-known venues and neighborhood spots
- Descriptions should be engaging and realistic

Return JSON array:
[{{
  "title": "...",
  "description": "...",
  "start_time": "YYYY-MM-DD HH:MM:SS",
  "end_time": "YYYY-MM-DD HH:MM:SS",
  "location": "Venue Name, Neighborhood, San Francisco, CA",
  "tags": ["tag1", "tag2"],
  "category": "one_of_the_categories",
  "source_url": ""
}}]"""


def generate_batch(count: int = 20) -> list[dict]:
    """Generate a batch of SF events using the LLM."""
    # Pick random venues and neighborhoods for variety
    all_venues = []
    for v_list in SF_VENUES.values():
        all_venues.extend(v_list)
    sample_venues = random.sample(all_venues, min(20, len(all_venues)))
    sample_hoods = random.sample(SF_NEIGHBORHOODS, min(10, len(SF_NEIGHBORHOODS)))

    today = datetime.now().strftime("%Y-%m-%d")

    prompt = BATCH_PROMPT.format(
        count=count,
        venues=", ".join(sample_venues),
        neighborhoods=", ".join(sample_hoods),
        today=today,
    )

    for attempt in range(3):
        try:
            resp = client.chat.completions.create(
                model="openai/gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.9,
                max_tokens=4000,
                response_format={"type": "json_object"},
            )
            raw = json.loads(resp.choices[0].message.content)
            if isinstance(raw, list):
                return raw
            # Try to find the array in the response
            for v in raw.values():
                if isinstance(v, list):
                    return v
            return []
        except Exception as e:
            print(f"  Attempt {attempt + 1} failed: {e}")
            if attempt < 2:
                time.sleep(2 ** (attempt + 1))
    return []


def events_to_rows(events: list[dict]) -> list[dict]:
    """Convert LLM-generated events to CSV row format."""
    rows = []
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for ev in events:
        tags = ev.get("tags", [])
        if isinstance(tags, list):
            tags = json.dumps(tags)
        rows.append({
            "creation_date": now,
            "title": ev.get("title", ""),
            "description": ev.get("description", ""),
            "start_time": ev.get("start_time", ""),
            "end_time": ev.get("end_time", ""),
            "region": "us",
            "source_url": ev.get("source_url", ""),
            "tags": tags,
            "category": ev.get("category", "other"),
            "location": ev.get("location", "San Francisco, CA"),
        })
    return rows


def main():
    parser = argparse.ArgumentParser(description="Generate SF events using LLM")
    parser.add_argument("--count", type=int, default=200, help="Total events to generate")
    parser.add_argument("--batch-size", type=int, default=20, help="Events per LLM call")
    parser.add_argument("--append", action="store_true", help="Append to existing CSV instead of creating new")
    parser.add_argument("--output", type=str, default=CSV_PATH, help="Output CSV path")
    args = parser.parse_args()

    print(f"Generating {args.count} SF events in batches of {args.batch_size}...")

    all_rows = []
    num_batches = (args.count + args.batch_size - 1) // args.batch_size

    for i in range(num_batches):
        remaining = args.count - len(all_rows)
        batch_count = min(args.batch_size, remaining)
        print(f"\nBatch {i + 1}/{num_batches} ({batch_count} events)...")

        events = generate_batch(batch_count)
        rows = events_to_rows(events)
        all_rows.extend(rows)
        print(f"  Generated {len(rows)} events (total: {len(all_rows)})")

        if i < num_batches - 1:
            time.sleep(1)

    new_df = pd.DataFrame(all_rows)

    if args.append:
        try:
            existing = pd.read_csv(args.output)
            # Deduplicate by title
            existing_titles = set(existing["title"].str.lower().str.strip())
            new_df = new_df[~new_df["title"].str.lower().str.strip().isin(existing_titles)]
            merged = pd.concat([existing, new_df], ignore_index=True)
            merged.to_csv(args.output, index=False)
            print(f"\nAppended {len(new_df)} new events to {args.output}")
            print(f"Total events in file: {len(merged)}")
        except FileNotFoundError:
            new_df.to_csv(args.output, index=False)
            print(f"\nCreated {args.output} with {len(new_df)} events")
    else:
        new_df.to_csv(args.output, index=False)
        print(f"\nWrote {len(new_df)} events to {args.output}")


if __name__ == "__main__":
    main()
