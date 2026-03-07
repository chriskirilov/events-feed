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
  h1 { font-size: 22px; margin-bottom: 4px; }
  .subtitle { color: #888; font-size: 13px; margin-bottom: 16px; }
  .filters {
    display: flex; gap: 8px; overflow-x: auto; padding-bottom: 12px;
    margin-bottom: 16px; -webkit-overflow-scrolling: touch;
  }
  .filters button {
    flex-shrink: 0; padding: 6px 14px; border-radius: 20px;
    border: 1px solid #333; background: #1a1a1a; color: #ccc;
    font-size: 13px; cursor: pointer; white-space: nowrap;
  }
  .filters button.active { background: #fff; color: #000; border-color: #fff; }
  .card {
    background: #151515; border: 1px solid #222; border-radius: 12px;
    padding: 14px; margin-bottom: 12px;
  }
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
  .tags { margin-top: 8px; display: flex; flex-wrap: wrap; gap: 6px; }
  .tag {
    font-size: 11px; padding: 3px 8px; border-radius: 10px;
    background: #1e1e2e; color: #8888cc;
  }
  .load-more {
    display: block; width: 100%; padding: 14px; margin-top: 8px;
    border-radius: 12px; border: 1px solid #333; background: #1a1a1a;
    color: #ccc; font-size: 14px; cursor: pointer; text-align: center;
  }
  .load-more:hover { background: #252525; }
  .spinner { display: none; text-align: center; padding: 20px; color: #666; }
  .search-box {
    width: 100%; padding: 10px 14px; border-radius: 10px;
    border: 1px solid #333; background: #1a1a1a; color: #e0e0e0;
    font-size: 14px; margin-bottom: 12px; outline: none;
  }
  .search-box:focus { border-color: #555; }
  .empty { text-align: center; padding: 40px 0; color: #666; }
</style>
</head>
<body>

<h1>SF Events</h1>
<p class="subtitle"><span id="count">...</span> events</p>

<input class="search-box" type="text" placeholder="Search events..." id="search">

<div class="filters" id="filters">
  <button class="active" data-cat="all">All</button>
  <button data-cat="music">Music</button>
  <button data-cat="food_and_drink">Food & Drink</button>
  <button data-cat="arts_and_culture">Arts</button>
  <button data-cat="tech">Tech</button>
  <button data-cat="sports_and_fitness">Sports</button>
  <button data-cat="nightlife">Nightlife</button>
  <button data-cat="family_and_kids">Family</button>
  <button data-cat="community">Community</button>
  <button data-cat="other">Other</button>
</div>

<div id="feed"></div>
<div class="spinner" id="spinner">Loading...</div>
<button class="load-more" id="load-more" style="display:none">Load more</button>

<script>
const PAGE = 50;
let allEvents = [];
let filtered = [];
let shown = 0;
let activeCat = 'all';
let searchTerm = '';

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

function renderCard(ev) {
  const tags = parseTags(ev.tags);
  const title = ev.title || 'Untitled';
  const desc = ev.description || '';
  const loc = ev.location || '';
  const date = formatDate(ev.start_time);
  const url = ev.source_url || '';

  const titleHtml = url
    ? '<a href="' + url + '" target="_blank" rel="noopener">' + esc(title) + '</a>'
    : esc(title);

  let meta = '';
  if (date) meta += '<span>' + date + '</span>';
  if (loc) meta += '<span>' + esc(loc) + '</span>';

  let tagsHtml = '';
  if (tags.length) {
    tagsHtml = '<div class="tags">' +
      tags.slice(0, 4).map(t => '<span class="tag">' + esc(t) + '</span>').join('') +
      '</div>';
  }

  return '<div class="card">' +
    '<div class="card-title">' + titleHtml + '</div>' +
    (meta ? '<div class="card-meta">' + meta + '</div>' : '') +
    '<div class="card-desc">' + esc(desc) + '</div>' +
    tagsHtml +
    '</div>';
}

function esc(s) {
  const d = document.createElement('div');
  d.textContent = s;
  return d.innerHTML;
}

function applyFilters() {
  filtered = allEvents.filter(ev => {
    if (activeCat !== 'all' && (ev.category || 'other') !== activeCat) return false;
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
  if (e.target.tagName !== 'BUTTON') return;
  document.querySelectorAll('.filters button').forEach(b => b.classList.remove('active'));
  e.target.classList.add('active');
  activeCat = e.target.dataset.cat;
  applyFilters();
});

let searchTimeout;
document.getElementById('search').addEventListener('input', e => {
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => {
    searchTerm = e.target.value;
    applyFilters();
  }, 200);
});

// Load all events (paginated fetch)
async function loadAll() {
  document.getElementById('spinner').style.display = 'block';
  let offset = 0;
  const limit = 500;
  while (true) {
    const r = await fetch('/events?limit=' + limit + '&offset=' + offset);
    const data = await r.json();
    allEvents = allEvents.concat(data.events);
    document.getElementById('count').textContent = data.count;
    if (offset + limit >= data.count) break;
    offset += limit;
  }
  // Sort by start_time descending (upcoming first)
  allEvents.sort((a, b) => {
    const da = new Date(a.start_time || 0);
    const db = new Date(b.start_time || 0);
    return db - da;
  });
  document.getElementById('spinner').style.display = 'none';
  applyFilters();
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

    records = df.iloc[offset:offset + limit].to_dict(orient="records")
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
