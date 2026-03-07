"""Base scraper class and shared utilities."""

import re
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class Event:
    """Normalized event record matching event_data.csv schema."""
    title: str
    description: str = ""
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    source_url: str = ""
    tags: str = "[]"
    category: str = "other"
    location: str = "San Francisco, CA"
    region: str = "us"
    creation_date: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    image_url: str = ""
    source_name: str = ""

    def to_dict(self):
        d = asdict(self)
        d.pop("source_name", None)
        return d


CATEGORY_MAP = {
    # keywords -> category
    "art": "arts_and_culture",
    "museum": "arts_and_culture",
    "gallery": "arts_and_culture",
    "theater": "arts_and_culture",
    "theatre": "arts_and_culture",
    "film": "arts_and_culture",
    "dance": "arts_and_culture",
    "comedy": "arts_and_culture",
    "literary": "arts_and_culture",
    "book": "arts_and_culture",
    "poetry": "arts_and_culture",
    "music": "music",
    "concert": "music",
    "jazz": "music",
    "dj": "music",
    "live band": "music",
    "symphony": "music",
    "opera": "music",
    "food": "food",
    "drink": "food",
    "wine": "food",
    "beer": "food",
    "cocktail": "food",
    "dining": "food",
    "tasting": "food",
    "brunch": "food",
    "restaurant": "food",
    "chef": "food",
    "kids": "family_and_kids",
    "family": "family_and_kids",
    "children": "family_and_kids",
    "toddler": "family_and_kids",
    "storytime": "family_and_kids",
    "sports": "sports",
    "run": "sports",
    "marathon": "sports",
    "fitness": "sports",
    "yoga": "sports",
    "hike": "sports",
    "hiking": "sports",
    "bike": "sports",
    "cycling": "sports",
    "game": "sports",
    "nightlife": "nightlife",
    "club": "nightlife",
    "bar": "nightlife",
    "party": "nightlife",
    "happy hour": "nightlife",
    "networking": "social",
    "meetup": "social",
    "mixer": "social",
    "community": "social",
    "volunteer": "social",
    "workshop": "social",
    "class": "social",
    "tech": "social",
    "startup": "social",
}


def guess_category(text: str) -> str:
    """Guess event category from text content."""
    lower = text.lower()
    scores: dict[str, int] = {}
    for keyword, cat in CATEGORY_MAP.items():
        if keyword in lower:
            scores[cat] = scores.get(cat, 0) + 1
    if not scores:
        return "other"
    return max(scores, key=scores.get)


def clean_text(text: str) -> str:
    """Strip HTML tags and normalize whitespace."""
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def parse_datetime(dt_str: str) -> Optional[str]:
    """Try to parse a datetime string into consistent format."""
    if not dt_str or dt_str.lower() in ("none", "nan", ""):
        return None
    formats = [
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
        "%m/%d/%Y %I:%M %p",
        "%m/%d/%Y",
        "%B %d, %Y %I:%M %p",
        "%B %d, %Y",
        "%b %d, %Y %I:%M %p",
        "%b %d, %Y",
        "%A, %B %d, %Y",
        "%a, %b %d, %Y %I:%M %p",
    ]
    dt_str = dt_str.strip()
    for fmt in formats:
        try:
            dt = datetime.strptime(dt_str, fmt)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue
    return dt_str


def extract_image_from_jsonld(item: dict) -> str:
    """Extract image URL from a JSON-LD item."""
    img = item.get("image", "")
    if isinstance(img, list):
        img = img[0] if img else ""
    if isinstance(img, dict):
        img = img.get("url", img.get("contentUrl", ""))
    return str(img).strip() if img else ""


def extract_image_from_card(card) -> str:
    """Extract image URL from a BeautifulSoup card element."""
    # Try img tag
    img = card.select_one("img[src]")
    if img:
        src = img.get("src", "")
        if src and not src.startswith("data:"):
            return src
    # Try background-image in style
    for el in [card] + card.select("[style*='background']"):
        style = el.get("style", "")
        if "url(" in style:
            import re as _re
            m = _re.search(r"url\(['\"]?([^'\")\s]+)", style)
            if m:
                return m.group(1)
    return ""


class BaseScraper:
    """Base class for all event scrapers."""
    name: str = "base"

    def scrape(self) -> list[Event]:
        """Return list of Event objects. Override in subclass."""
        raise NotImplementedError

    def safe_scrape(self) -> list[Event]:
        """Scrape with error handling."""
        try:
            events = self.scrape()
            logger.info(f"[{self.name}] scraped {len(events)} events")
            return events
        except Exception as e:
            logger.error(f"[{self.name}] failed: {e}")
            return []
