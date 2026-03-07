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
from flask import Flask, jsonify, request

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
