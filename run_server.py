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

  .card-link {
    text-decoration: none; color: inherit; display: block;
  }
  .card {
    background: #151515; border: 1px solid #222; border-radius: 14px;
    margin-bottom: 14px; overflow: hidden;
    display: flex; flex-direction: column; position: relative;
  }
  .card:active { opacity: 0.92; }
  .card-img-wrap {
    position: relative; width: 100%; height: 160px; overflow: hidden;
    background: #1a1a1a;
  }
  .card-img {
    width: 100%; height: 100%; object-fit: cover; display: block;
    transition: opacity 0.3s;
  }
  .card-img.hidden { display: none; }
  .card-img-overlay {
    position: absolute; bottom: 0; left: 0; right: 0; height: 80px;
    background: linear-gradient(transparent, rgba(0,0,0,0.7));
    pointer-events: none;
  }
  .card-date-badge {
    position: absolute; top: 10px; left: 10px;
    background: rgba(0,0,0,0.65); backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    border-radius: 8px; padding: 4px 8px;
    font-size: 11px; font-weight: 600; color: #fff;
    line-height: 1.3; text-align: center;
  }
  .card-date-badge .date-month { font-size: 9px; text-transform: uppercase; letter-spacing: 0.5px; color: #ff6b6b; }
  .card-cat-badge {
    position: absolute; top: 10px; right: 10px;
    background: rgba(0,0,0,0.55); backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    border-radius: 6px; padding: 3px 7px;
    font-size: 13px;
  }
  .card-body {
    padding: 12px 14px; flex: 1; min-width: 0;
  }
  .card-title {
    font-size: 15px; font-weight: 600; margin-bottom: 4px;
    line-height: 1.3;
    display: -webkit-box; -webkit-line-clamp: 2;
    -webkit-box-orient: vertical; overflow: hidden;
  }
  .card-meta { font-size: 11px; color: #888; margin-bottom: 4px; }
  .card-meta span { margin-right: 10px; }
  .card-desc {
    font-size: 12px; color: #aaa; line-height: 1.4;
    display: -webkit-box; -webkit-line-clamp: 2;
    -webkit-box-orient: vertical; overflow: hidden;
  }
  .cat-icons { margin-top: 6px; display: flex; gap: 4px; font-size: 14px; }
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
  music: '🎵', arts: '🎨', food: '🍽️',
  sports: '🏃', nightlife: '🍸', community: '🤝',
  learning: '📚', outdoors: '🌳', family: '👪'
};

const CAT_IMAGES = {
  music: [
    'https://images.unsplash.com/photo-1506157786151-b8491531f063?w=800&q=80',
    'https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=800&q=80',
    'https://images.unsplash.com/photo-1470225620780-dba8ba36b745?w=800&q=80',
    'https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=800&q=80',
  ],
  arts: [
    'https://images.unsplash.com/photo-1536924940846-227afb31e2a5?w=800&q=80',
    'https://images.unsplash.com/photo-1561214115-f2f134cc4912?w=800&q=80',
    'https://images.unsplash.com/photo-1547891654-e66ed7ebb968?w=800&q=80',
    'https://images.unsplash.com/photo-1460661419201-fd4cecdf8a8b?w=800&q=80',
  ],
  food: [
    'https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=800&q=80',
    'https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=800&q=80',
    'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=800&q=80',
    'https://images.unsplash.com/photo-1476224203421-9ac39bcb3327?w=800&q=80',
  ],
  sports: [
    'https://images.unsplash.com/photo-1461896836934-bd45ba8482fe?w=800&q=80',
    'https://images.unsplash.com/photo-1530549387789-4c1017266635?w=800&q=80',
    'https://images.unsplash.com/photo-1517649763962-0c623066013b?w=800&q=80',
    'https://images.unsplash.com/photo-1552674605-db6ffd4facb5?w=800&q=80',
  ],
  nightlife: [
    'https://images.unsplash.com/photo-1533174072545-7a4b6ad7a6c3?w=800&q=80',
    'https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=800&q=80',
    'https://images.unsplash.com/photo-1571266028243-e4733b0f0bb0?w=800&q=80',
    'https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?w=800&q=80',
  ],
  community: [
    'https://images.unsplash.com/photo-1528605248644-14dd04022da1?w=800&q=80',
    'https://images.unsplash.com/photo-1529156069898-49953e39b3ac?w=800&q=80',
    'https://images.unsplash.com/photo-1511632765486-a01980e01a18?w=800&q=80',
    'https://images.unsplash.com/photo-1582213782179-e0d53f98f2ca?w=800&q=80',
  ],
  learning: [
    'https://images.unsplash.com/photo-1475721027785-f74eccf877e2?w=800&q=80',
    'https://images.unsplash.com/photo-1524178232363-1fb2b075b655?w=800&q=80',
    'https://images.unsplash.com/photo-1503676260728-1c00da094a0b?w=800&q=80',
    'https://images.unsplash.com/photo-1513258496099-48168024aec0?w=800&q=80',
  ],
  outdoors: [
    'https://images.unsplash.com/photo-1464366400600-7168b8af9bc3?w=800&q=80',
    'https://images.unsplash.com/photo-1551632811-561732d1e306?w=800&q=80',
    'https://images.unsplash.com/photo-1501555088652-021faa106b9b?w=800&q=80',
    'https://images.unsplash.com/photo-1533240332313-0db49b459ad6?w=800&q=80',
  ],
  family: [
    'https://images.unsplash.com/photo-1501281668745-f7f57925c3b4?w=800&q=80',
    'https://images.unsplash.com/photo-1536640712-4d4c36ff0e4e?w=800&q=80',
    'https://images.unsplash.com/photo-1472586662442-3eec04b9dbda?w=800&q=80',
    'https://images.unsplash.com/photo-1609220136736-443140cffec6?w=800&q=80',
  ],
  _default: [
    'https://images.unsplash.com/photo-1492684223066-81342ee5ff30?w=800&q=80',
    'https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=800&q=80',
    'https://images.unsplash.com/photo-1501386761578-eac5c94b800a?w=800&q=80',
    'https://images.unsplash.com/photo-1429962714451-bb934ecdc4ec?w=800&q=80',
  ],
};
function pickCatImage(cat, title) {
  const imgs = CAT_IMAGES[cat] || CAT_IMAGES._default;
  let hash = 0;
  for (let i = 0; i < title.length; i++) hash = ((hash << 5) - hash + title.charCodeAt(i)) | 0;
  return imgs[Math.abs(hash) % imgs.length];
}

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
  const fallbackCat = groups.length ? groups[0] : '_default';
  const fallbackImg = pickCatImage(fallbackCat, title);
  const hasRealImage = !!ev.image_url;
  const imgSrc = ev.image_url || fallbackImg;

  const titleHtml = esc(title);

  let locHtml = loc ? '<span>' + esc(loc) + '</span>' : '';

  // Date badge overlay
  let dateBadge = '';
  if (ev.start_time) {
    try {
      const dt = new Date(ev.start_time);
      if (!isNaN(dt)) {
        const mon = dt.toLocaleDateString('en-US', { month: 'short' }).toUpperCase();
        const day = dt.getDate();
        dateBadge = '<div class="card-date-badge"><div class="date-month">' + mon + '</div>' + day + '</div>';
      }
    } catch {}
  }

  // Category emoji badge
  let catBadge = '';
  if (groups.length) {
    catBadge = '<div class="card-cat-badge">' +
      groups.map(g => '<span title="' + g + '">' + CAT_EMOJIS[g] + '</span>').join('') +
      '</div>';
  }

  const inner = '<div class="card">' +
    '<div class="card-img-wrap">' +
    '<img class="card-img" src="' + imgSrc + '" alt="" loading="lazy" data-fallback="' + fallbackImg + '" data-source="' + esc(url) + '"' + (hasRealImage ? '' : ' data-needs-enrich="1"') + ' onerror="handleImgError(this)">' +
    '<div class="card-img-overlay"></div>' +
    dateBadge + catBadge +
    '</div>' +
    '<div class="card-body">' +
    '<div class="card-title">' + titleHtml + '</div>' +
    (date || locHtml ? '<div class="card-meta">' + (date ? '<span>' + date + '</span>' : '') + locHtml + '</div>' : '') +
    '<div class="card-desc">' + esc(desc) + '</div>' +
    '</div></div>';

  if (url) {
    return '<a class="card-link" href="' + url + '" target="_blank" rel="noopener">' + inner + '</a>';
  }
  return inner;
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
  observeNewImages();
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

// Handle broken images: try server-side enrichment, then fall back to category placeholder
function handleImgError(img) {
  const fallback = img.dataset.fallback || '';
  const sourceUrl = img.dataset.source || '';
  // If image already tried enrichment or is already on fallback, hide it
  if (img.dataset.tried) {
    if (fallback && img.src !== fallback) {
      img.src = fallback;
    } else {
      img.style.display = 'none';
    }
    return;
  }
  img.dataset.tried = '1';
  // Try server-side enrichment via source URL
  if (sourceUrl) {
    fetch(apiUrl('/enrich-image?url=' + encodeURIComponent(sourceUrl)))
      .then(r => r.ok ? r.json() : null)
      .then(data => {
        if (data && data.image_url) {
          img.src = data.image_url;
        } else if (fallback) {
          img.src = fallback;
        } else {
          img.style.display = 'none';
        }
      })
      .catch(() => {
        if (fallback) img.src = fallback;
        else img.style.display = 'none';
      });
  } else if (fallback) {
    img.src = fallback;
  } else {
    img.style.display = 'none';
  }
}

// Lazy-enrich images: when a card scrolls into view and has no real image,
// fetch the actual event image from the source page
const enrichObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (!entry.isIntersecting) return;
    const img = entry.target;
    enrichObserver.unobserve(img);
    const sourceUrl = img.dataset.source;
    if (!sourceUrl) return;
    fetch(apiUrl('/enrich-image?url=' + encodeURIComponent(sourceUrl)))
      .then(r => r.ok ? r.json() : null)
      .then(data => {
        if (data && data.image_url) {
          img.dataset.tried = '1';
          img.src = data.image_url;
        }
      })
      .catch(() => {});
  });
}, { rootMargin: '200px' });

// After cards are added to the DOM, observe images that need enrichment
function observeNewImages() {
  document.querySelectorAll('img[data-needs-enrich="1"]').forEach(img => {
    img.removeAttribute('data-needs-enrich');
    enrichObserver.observe(img);
  });
}

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

    if "image_url" not in df.columns:
        df["image_url"] = ""
    chunk = df.iloc[offset:offset + limit].fillna("")
    records = chunk.to_dict(orient="records")
    return jsonify({"events": records, "count": len(df), "limit": limit, "offset": offset})


_image_cache = {}  # in-memory cache: source_url -> image_url (or "")


@app.route("/enrich-image")
def enrich_image():
    """Fetch og:image from an event's source page to fill missing images."""
    url = request.args.get("url", "").strip()
    if not url:
        return jsonify({"error": "missing url param"}), 400

    # Check in-memory cache first
    if url in _image_cache:
        return jsonify({"image_url": _image_cache[url]})

    try:
        import requests as req
        from bs4 import BeautifulSoup

        resp = req.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # Try og:image first, then twitter:image
        for prop in ("og:image", "twitter:image"):
            tag = soup.select_one(f'meta[property="{prop}"]') or soup.select_one(f'meta[name="{prop}"]')
            if tag and tag.get("content", "").startswith("http"):
                image_url = tag["content"]
                _image_cache[url] = image_url
                # Update the CSV so we don't re-fetch next time
                _update_csv_image(url, image_url)
                return jsonify({"image_url": image_url})

        _image_cache[url] = ""
        return jsonify({"image_url": ""})

    except Exception as e:
        logging.debug(f"Image enrichment failed for {url}: {e}")
        _image_cache[url] = ""
        return jsonify({"image_url": ""})


def _update_csv_image(source_url: str, image_url: str):
    """Persist an enriched image_url back into the CSV."""
    try:
        df = pd.read_csv(CSV_PATH)
        if "image_url" not in df.columns:
            df["image_url"] = ""
        mask = df["source_url"].astype(str) == source_url
        if mask.any():
            df.loc[mask, "image_url"] = image_url
            df.to_csv(CSV_PATH, index=False)
    except Exception as e:
        logging.debug(f"CSV image update failed: {e}")


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
