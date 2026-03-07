#!/usr/bin/env python3
"""
Lightweight API server for triggering scrapers remotely.

Endpoints:
    GET  /              - Health check / status
    POST /scrape        - Run all scrapers (or specific ones via ?sources=funcheap,luma)
    GET  /events        - Return current event_data.csv as JSON
    GET  /events/count  - Quick count of events in CSV

Deploy on Railway, Render, Fly.io, or any container host.
Hit /scrape from your phone browser or a cron job.
"""

import io
import logging
import os
import threading
import time
from datetime import datetime

import pandas as pd
from flask import Flask, jsonify, redirect, request
from markupsafe import Markup, escape

from ingest_sf_events import (
    ALL_SCRAPERS,
    CSV_PATH,
    SOURCE_NAMES,
    deduplicate_events,
    events_to_dataframe,
    filter_sf_events,
    merge_with_existing,
    scrape_all,
    setup_logging,
)

app = Flask(__name__)
setup_logging()

# Simple in-memory state so you can check progress from your phone
_status = {
    "running": False,
    "last_run": None,
    "last_result": None,
}
_lock = threading.Lock()

API_KEY = os.getenv("API_KEY", "")  # optional auth


def check_auth():
    """If API_KEY is set, require it via ?key= or Authorization header."""
    if not API_KEY:
        return True
    key = request.args.get("key") or request.headers.get("Authorization", "").removeprefix("Bearer ")
    return key == API_KEY


@app.before_request
def auth_guard():
    if not check_auth():
        return jsonify({"error": "unauthorized"}), 401


@app.route("/")
def index():
    return redirect("/feed")


@app.route("/status")
def status():
    event_count = 0
    try:
        df = pd.read_csv(CSV_PATH)
        event_count = len(df)
    except Exception:
        pass

    return jsonify({
        "status": "ok",
        "events_in_csv": event_count,
        "scraper_running": _status["running"],
        "last_run": _status["last_run"],
        "available_sources": sorted(SOURCE_NAMES),
    })


FEED_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SF Events</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: #0a0a0a; color: #e0e0e0;
    padding: 16px; padding-bottom: 80px;
  }
  .header {
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 14px; padding: 2px 0;
  }
  .profile-icon {
    width: 36px; height: 36px; border-radius: 50%;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
    display: flex; align-items: center; justify-content: center;
    font-size: 16px; color: #fff; font-weight: 700;
    flex-shrink: 0;
  }
  .header-title {
    font-family: 'Georgia', 'Times New Roman', serif;
    font-size: 20px; font-weight: 600; letter-spacing: 0.3px;
    color: #f0f0f0;
  }
  .chat-icon {
    width: 36px; height: 36px; border-radius: 50%;
    border: 1px solid #333; background: #1a1a1a;
    display: flex; align-items: center; justify-content: center;
    font-size: 18px; color: #ccc; cursor: pointer; flex-shrink: 0;
  }

  .toolbar {
    display: flex; align-items: center; gap: 0;
    margin-bottom: 16px; overflow-x: auto;
    -webkit-overflow-scrolling: touch;
    scrollbar-width: none;
  }
  .toolbar::-webkit-scrollbar { display: none; }

  .search-wrap {
    display: flex; align-items: center; flex-shrink: 0;
    position: relative;
  }
  .search-btn {
    width: 38px; height: 38px; border-radius: 50%;
    border: 1px solid #333; background: #1a1a1a; color: #ccc;
    font-size: 18px; cursor: pointer; display: flex;
    align-items: center; justify-content: center; flex-shrink: 0;
  }
  .search-btn.active { background: #fff; color: #000; border-color: #fff; }
  .search-input {
    width: 0; opacity: 0; padding: 0; border: none;
    background: #1a1a1a; color: #e0e0e0; font-size: 14px;
    border-radius: 19px; height: 38px; outline: none;
    transition: width 0.25s ease, opacity 0.25s ease, padding 0.25s ease;
  }
  .search-input.open {
    width: 160px; opacity: 1; padding: 0 14px;
    border: 1px solid #333; margin-left: 6px;
  }
  .search-input.open:focus { border-color: #555; }

  .divider {
    width: 1px; height: 24px; background: #333;
    margin: 0 10px; flex-shrink: 0;
  }

  .filters {
    display: flex; align-items: center; gap: 6px; flex-shrink: 0;
  }
  .filters button {
    flex-shrink: 0; height: 38px; border-radius: 19px;
    border: 1px solid #333; background: #1a1a1a; color: #ccc;
    font-size: 18px; cursor: pointer; display: flex;
    align-items: center; justify-content: center;
    padding: 0 10px; line-height: 1;
    transition: all 0.2s ease; min-width: 38px;
  }
  .filters button:not(.active) { width: 38px; padding: 0; border-radius: 50%; }
  .filters button.active { background: #fff; color: #000; border-color: #fff; }
  .filters button .lbl {
    display: none; font-size: 13px; font-weight: 600;
    margin-left: 5px; white-space: nowrap;
  }
  .filters button.active .lbl { display: inline; }

  .card {
    background: #151515; border: 1px solid #222; border-radius: 12px;
    margin-bottom: 12px; overflow: hidden;
  }
  .card-img {
    width: 100%; height: 160px; object-fit: cover; display: block;
  }
  .card-body { padding: 14px; }
  .card-title {
    font-size: 16px; font-weight: 600; margin-bottom: 6px;
    line-height: 1.3;
  }
  .card-title a { color: #e0e0e0; text-decoration: none; }
  .card-title a:hover { text-decoration: underline; }
  .card-meta { font-size: 12px; color: #888; margin-bottom: 8px; }
  .card-meta span { margin-right: 12px; }
  .card-desc {
    font-size: 13px; color: #aaa; line-height: 1.5;
    display: -webkit-box; -webkit-line-clamp: 3;
    -webkit-box-orient: vertical; overflow: hidden;
  }
  .cat-icons { margin-top: 8px; display: flex; gap: 4px; font-size: 16px; }
  .load-more {
    display: block; width: 100%; padding: 14px; margin-top: 8px;
    border-radius: 12px; border: 1px solid #333; background: #1a1a1a;
    color: #ccc; font-size: 14px; cursor: pointer; text-align: center;
  }
  .load-more:hover { background: #252525; }
  .spinner { display: none; text-align: center; padding: 20px; color: #666; }
  .empty { text-align: center; padding: 40px 0; color: #666; }
</style>
</head>
<body>

<div class="header">
  <div class="profile-icon">
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
  </div>
  <span class="header-title">San Francisco</span>
  <div class="chat-icon">
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
  </div>
</div>

<div class="toolbar">
  <div class="search-wrap">
    <button class="search-btn" id="search-btn">&#x1F50D;</button>
    <input class="search-input" type="text" placeholder="Search..." id="search">
  </div>
  <div class="divider"></div>
  <div class="filters" id="filters">
    <button data-cat="music" title="Music">&#x1F3B5;<span class="lbl">Music</span></button>
    <button data-cat="arts" title="Arts & Culture">&#x1F3A8;<span class="lbl">Arts</span></button>
    <button data-cat="food" title="Food & Drink">&#x1F37D;&#xFE0F;<span class="lbl">Food</span></button>
    <button data-cat="sports" title="Sports & Fitness">&#x1F3C3;<span class="lbl">Sports</span></button>
    <button data-cat="nightlife" title="Nightlife & Comedy">&#x1F378;<span class="lbl">Nightlife</span></button>
    <button data-cat="community" title="Community">&#x1F91D;<span class="lbl">Community</span></button>
    <button data-cat="learning" title="Learning">&#x1F4DA;<span class="lbl">Learning</span></button>
    <button data-cat="outdoors" title="Outdoors & Festivals">&#x1F333;<span class="lbl">Outdoors</span></button>
    <button data-cat="family" title="Family & Kids">&#x1F46A;<span class="lbl">Family</span></button>
  </div>
</div>

<div id="feed"></div>
<div class="spinner" id="spinner">Loading...</div>
<button class="load-more" id="load-more" style="display:none">Load more</button>

<script>
const PAGE = 50;
let allEvents = [];
let filtered = [];
let shown = 0;
let activeCat = null;
let searchTerm = '';

// Search expand/collapse
const searchBtn = document.getElementById('search-btn');
const searchInput = document.getElementById('search');
let searchOpen = false;

searchBtn.addEventListener('click', () => {
  searchOpen = !searchOpen;
  searchInput.classList.toggle('open', searchOpen);
  searchBtn.classList.toggle('active', searchOpen);
  if (searchOpen) {
    searchInput.focus();
  } else {
    searchInput.value = '';
    searchTerm = '';
    applyFilters();
  }
});

// Close search if user taps away on empty search
searchInput.addEventListener('blur', () => {
  if (!searchInput.value) {
    searchOpen = false;
    searchInput.classList.remove('open');
    searchBtn.classList.remove('active');
  }
});

// Forward ?key= param so API auth works from the feed page
const urlKey = new URLSearchParams(window.location.search).get('key');
function apiUrl(path) {
  return urlKey ? path + (path.includes('?') ? '&' : '?') + 'key=' + encodeURIComponent(urlKey) : path;
}

function formatDate(d) {
  if (!d) return '';
  try {
    const dt = new Date(d);
    if (isNaN(dt)) return '';
    return dt.toLocaleDateString('en-US', {
      weekday: 'short', month: 'short', day: 'numeric',
      hour: 'numeric', minute: '2-digit'
    });
  } catch { return ''; }
}

function parseTags(t) {
  if (!t) return [];
  try {
    const arr = JSON.parse(t.replace(/'/g, '"'));
    return Array.isArray(arr) ? arr : [];
  } catch { return []; }
}

const CAT_EMOJIS = {
  music: '\u{1F3B5}', arts: '\u{1F3A8}', food: '\u{1F37D}\uFE0F',
  sports: '\u{1F3C3}', nightlife: '\u{1F378}', community: '\u{1F91D}',
  learning: '\u{1F4DA}', outdoors: '\u{1F333}', family: '\u{1F46A}'
};

const CAT_IMAGES = {
  music:     'https://images.unsplash.com/photo-1506157786151-b8491531f063?w=600&q=75',
  arts:      'https://images.unsplash.com/photo-1536924940846-227afb31e2a5?w=600&q=75',
  food:      'https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=600&q=75',
  sports:    'https://images.unsplash.com/photo-1461896836934-bd45ba8482fe?w=600&q=75',
  nightlife: 'https://images.unsplash.com/photo-1533174072545-7a4b6ad7a6c3?w=600&q=75',
  community: 'https://images.unsplash.com/photo-1528605248644-14dd04022da1?w=600&q=75',
  learning:  'https://images.unsplash.com/photo-1475721027785-f74eccf877e2?w=600&q=75',
  outdoors:  'https://images.unsplash.com/photo-1464366400600-7168b8af9bc3?w=600&q=75',
  family:    'https://images.unsplash.com/photo-1501281668745-f7f57925c3b4?w=600&q=75',
  _default:  'https://images.unsplash.com/photo-1492684223066-81342ee5ff30?w=600&q=75',
};

function getMatchingGroups(ev) {
  const groups = [];
  for (const g of Object.keys(CAT_GROUPS)) {
    if (matchesCat(ev, g)) groups.push(g);
  }
  return groups;
}

function renderCard(ev) {
  const title = ev.title || 'Untitled';
  const desc = ev.description || '';
  const loc = ev.location || '';
  const date = formatDate(ev.start_time);
  const url = ev.source_url || '';

  const groups = getMatchingGroups(ev);
  const imgSrc = ev.image_url || (groups.length ? CAT_IMAGES[groups[0]] : CAT_IMAGES._default);

  const titleHtml = url
    ? '<a href="' + url + '" target="_blank" rel="noopener">' + esc(title) + '</a>'
    : esc(title);

  let meta = '';
  if (date) meta += '<span>' + date + '</span>';
  if (loc) meta += '<span>' + esc(loc) + '</span>';

  let iconsHtml = '';
  if (groups.length) {
    iconsHtml = '<div class="cat-icons">' +
      groups.map(g => '<span title="' + g + '">' + CAT_EMOJIS[g] + '</span>').join('') +
      '</div>';
  }

  return '<div class="card">' +
    '<img class="card-img" src="' + imgSrc + '" alt="" loading="lazy">' +
    '<div class="card-body">' +
    '<div class="card-title">' + titleHtml + '</div>' +
    (meta ? '<div class="card-meta">' + meta + '</div>' : '') +
    '<div class="card-desc">' + esc(desc) + '</div>' +
    iconsHtml +
    '</div></div>';
}

function esc(s) {
  const d = document.createElement('div');
  d.textContent = s;
  return d.innerHTML;
}

// Category groups mapping filter buttons to actual CSV category values
const CAT_GROUPS = {
  music:      ['concert', 'live_music', 'music'],
  arts:       ['arts_and_culture', 'theater', 'museum', 'architecture', 'art', 'culture', 'heritage', 'film', 'dance'],
  food:       ['food_and_dining', 'bar_and_mixology', 'beer_and_brewery', 'farmers_market', 'food', 'drink'],
  sports:     ['sports', 'run_club', 'health_and_wellness', 'fitness', 'basketball'],
  nightlife:  ['nightlife', 'comedy', 'trivia_night', 'stand-up'],
  community:  ['community_and_social', 'volunteer_and_charity', 'civic_and_public_service', 'volunteer', 'networking', 'jobs_and_networking'],
  learning:   ['education', 'panel', 'library', 'books'],
  outdoors:   ['festival', 'park', 'outdoor_movie', 'parade', 'block_party', 'nature', 'outdoors'],
  family:     ['family_and_kids', 'pets', 'family', 'kids'],
};

function getEventCats(ev) {
  const raw = (ev.category || '').toLowerCase();
  // Try to parse as JSON array (handles ["Music", "Education"] style)
  if (raw.startsWith('[')) {
    try {
      const arr = JSON.parse(raw.replace(/'/g, '"'));
      if (Array.isArray(arr)) return arr.map(s => s.toLowerCase().trim());
    } catch {}
  }
  return [raw.replace(/_/g, ' '), raw];
}

function matchesCat(ev, group) {
  const cats = getEventCats(ev);
  const keywords = CAT_GROUPS[group] || [];
  return cats.some(c => keywords.some(k => c.includes(k)));
}

function applyFilters() {
  filtered = allEvents.filter(ev => {
    if (activeCat && !matchesCat(ev, activeCat)) return false;
    if (searchTerm) {
      const s = searchTerm.toLowerCase();
      const hay = ((ev.title || '') + ' ' + (ev.description || '') + ' ' + (ev.location || '') + ' ' + (ev.tags || '')).toLowerCase();
      if (!hay.includes(s)) return false;
    }
    return true;
  });
  shown = 0;
  document.getElementById('feed').innerHTML = '';
  showMore();
}

function showMore() {
  const feed = document.getElementById('feed');
  const batch = filtered.slice(shown, shown + PAGE);
  batch.forEach(ev => { feed.insertAdjacentHTML('beforeend', renderCard(ev)); });
  shown += batch.length;
  document.getElementById('load-more').style.display =
    shown < filtered.length ? 'block' : 'none';
  if (filtered.length === 0) {
    feed.innerHTML = '<div class="empty">No events found</div>';
  }
}

document.getElementById('load-more').addEventListener('click', showMore);

document.getElementById('filters').addEventListener('click', e => {
  const btn = e.target.closest('button');
  if (!btn) return;
  if (btn.classList.contains('active')) {
    btn.classList.remove('active');
    activeCat = null;
  } else {
    document.querySelectorAll('.filters button').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    activeCat = btn.dataset.cat;
  }
  applyFilters();
});

let searchTimeout;
searchInput.addEventListener('input', e => {
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => {
    searchTerm = e.target.value;
    applyFilters();
  }, 200);
});

// Load all events (paginated fetch)
async function loadAll() {
  document.getElementById('spinner').style.display = 'block';
  try {
    let offset = 0;
    const limit = 500;
    while (true) {
      const r = await fetch(apiUrl('/events?limit=' + limit + '&offset=' + offset));
      if (!r.ok) throw new Error('HTTP ' + r.status);
      const data = await r.json();
      allEvents = allEvents.concat(data.events);
      // count available in data.count if needed
      if (offset + limit >= data.count) break;
      offset += limit;
    }
    // Sort by start_time descending (upcoming first)
    allEvents.sort((a, b) => {
      const da = new Date(a.start_time || 0);
      const db = new Date(b.start_time || 0);
      return db - da;
    });
    applyFilters();
  } catch (err) {
    document.getElementById('feed').innerHTML =
      '<div class="empty">Failed to load events: ' + esc(err.message) + '</div>';
  }
  document.getElementById('spinner').style.display = 'none';
}
loadAll();
</script>
</body>
</html>"""


@app.route("/feed")
def feed():
    return FEED_HTML


@app.route("/scrape", methods=["GET", "POST"])
def scrape():
    with _lock:
        if _status["running"]:
            return jsonify({"error": "scrape already in progress", "started": _status["last_run"]}), 409

    # Parse options
    sources = request.args.get("sources", "")
    workers = int(request.args.get("workers", "5"))
    dry_run = request.args.get("dry_run", "false").lower() == "true"

    # Select scrapers
    if sources:
        selected = {s.strip() for s in sources.split(",")}
        invalid = selected - SOURCE_NAMES
        if invalid:
            return jsonify({"error": f"unknown sources: {sorted(invalid)}", "available": sorted(SOURCE_NAMES)}), 400
        scrapers = [s for s in ALL_SCRAPERS if s.name in selected]
    else:
        scrapers = list(ALL_SCRAPERS)

    # Run in background thread so the HTTP response returns immediately
    def run():
        with _lock:
            _status["running"] = True
            _status["last_run"] = datetime.now().isoformat()

        try:
            start = time.time()
            raw = scrape_all(scrapers, max_workers=workers)
            sf = filter_sf_events(raw)
            unique = deduplicate_events(sf)
            elapsed = time.time() - start

            result = {
                "raw_events": len(raw),
                "sf_filtered": len(sf),
                "deduplicated": len(unique),
                "elapsed_seconds": round(elapsed, 1),
                "sources_run": [s.name for s in scrapers],
            }

            if not dry_run and unique:
                new_df = events_to_dataframe(unique)
                merged = merge_with_existing(new_df, CSV_PATH)
                merged.to_csv(CSV_PATH, index=False)
                result["total_in_csv"] = len(merged)
                result["new_added"] = len(merged) - (len(merged) - len(new_df))

            with _lock:
                _status["last_result"] = result
                _status["running"] = False

            logging.info(f"Scrape done: {result}")

        except Exception as e:
            logging.exception("Scrape failed")
            with _lock:
                _status["last_result"] = {"error": str(e)}
                _status["running"] = False

    thread = threading.Thread(target=run, daemon=True)
    thread.start()

    return jsonify({
        "message": "scrape started",
        "sources": [s.name for s in scrapers],
        "workers": workers,
        "dry_run": dry_run,
        "check_status": "GET /",
    }), 202


@app.route("/scrape/status")
def scrape_status():
    return jsonify(_status)


@app.route("/events")
def events():
    try:
        df = pd.read_csv(CSV_PATH)
    except FileNotFoundError:
        return jsonify({"events": [], "count": 0})

    limit = int(request.args.get("limit", "100"))
    offset = int(request.args.get("offset", "0"))

    chunk = df.iloc[offset:offset + limit].fillna("")
    records = chunk.to_dict(orient="records")
    return jsonify({"events": records, "count": len(df), "limit": limit, "offset": offset})


@app.route("/events/count")
def events_count():
    try:
        df = pd.read_csv(CSV_PATH)
        return jsonify({"count": len(df)})
    except FileNotFoundError:
        return jsonify({"count": 0})


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    app.run(host="0.0.0.0", port=port, debug=False)
