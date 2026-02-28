import streamlit as st
import pandas as pd
from openai import OpenAI
import os
import json
import random
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GMI_API_KEY"),
    base_url="https://api.gmi-serving.com/v1"
)

st.set_page_config(page_title="Events Near You", layout="wide")

CATEGORY_EMOJI = {
    "arts_and_culture": "🎨",
    "family_and_kids": "👨‍👩‍👧",
    "music": "🎵",
    "sports": "⚽",
    "food": "🍕",
    "nightlife": "🌙",
    "social": "🌐",
    "other": "📌",
}

COVER_IMAGES = [
    "https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=800&q=80",
    "https://images.unsplash.com/photo-1511795409834-ef04bbd61622?w=800&q=80",
    "https://images.unsplash.com/photo-1492684223066-81342ee5ff30?w=800&q=80",
    "https://images.unsplash.com/photo-1501281668745-f7f57925c3b4?w=800&q=80",
    "https://images.unsplash.com/photo-1528605248644-14dd04022da1?w=800&q=80",
    "https://images.unsplash.com/photo-1506157786151-b8491531f063?w=800&q=80",
    "https://images.unsplash.com/photo-1533174072545-7a4b6ad7a6c3?w=800&q=80",
    "https://images.unsplash.com/photo-1475721027785-f74eccf877e2?w=800&q=80",
    "https://images.unsplash.com/photo-1464366400600-7168b8af9bc3?w=800&q=80",
    "https://images.unsplash.com/photo-1429962714451-bb934ecdc4ec?w=800&q=80",
]

st.markdown("""
<style>
    .block-container {padding: 1.5rem 2rem 6rem !important;}
    h1 {font-size: 1.5rem !important; font-weight: 700 !important; margin-bottom: 0.25rem !important;}
    .cards-scroll {
        display: flex; gap: 16px; overflow-x: auto; padding: 8px 0 16px;
        scroll-snap-type: x mandatory; -webkit-overflow-scrolling: touch;
    }
    .cards-scroll::-webkit-scrollbar {height: 4px;}
    .cards-scroll::-webkit-scrollbar-thumb {background: #ddd; border-radius: 4px;}
    .event-card {
        min-width: 260px; max-width: 260px; border-radius: 16px; overflow: hidden;
        background: white; box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        border: 1px solid #f0f0f0; scroll-snap-align: start; flex-shrink: 0;
    }
    .event-card img {
        width: 100%; height: 140px; object-fit: cover; display: block;
    }
    .card-body {padding: 12px 14px 14px;}
    .tag-row {display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 8px;}
    .tag-pill {
        background: #f4f4f5; padding: 3px 10px; border-radius: 16px;
        font-size: 11px; font-weight: 500; color: #555; white-space: nowrap;
    }
    .event-title {
        font-size: 15px; font-weight: 700; color: #1a1a1a;
        margin: 0 0 6px; line-height: 1.3;
        overflow: hidden; text-overflow: ellipsis;
        display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;
    }
    .event-meta {font-size: 12px; color: #888; margin: 0;}
    .join-row {display: flex; justify-content: space-between; align-items: center; margin-top: 8px;}
    .join-btn {
        background: #5b4cff; color: white; border: none; padding: 7px 20px;
        border-radius: 20px; font-size: 13px; font-weight: 600; cursor: pointer;
        transition: background 0.15s;
    }
    .join-btn:hover {background: #4a3de6;}
    .attendees {display: flex; align-items: center;}
    .attendees .avatar {
        width: 24px; height: 24px; border-radius: 50%; border: 2px solid white;
        margin-left: -6px; object-fit: cover;
    }
    .attendees .avatar:first-child {margin-left: 0;}
    .attendees .count {
        background: #e8e6ff; color: #5b4cff; font-size: 11px; font-weight: 600;
        padding: 2px 6px; border-radius: 10px; margin-left: 4px;
    }
    .bottom-nav {
        position: fixed; bottom: 0; left: 0; right: 0; background: white;
        border-top: 1px solid #eee; padding: 8px 0; display: flex;
        justify-content: space-around; z-index: 100;
    }
    .nav-item {text-align: center; font-size: 10px; color: #999;}
    .nav-item.active {color: #5b4cff; font-weight: 700;}
    div[data-testid="stSpinner"] {margin: 40px auto;}
</style>
""", unsafe_allow_html=True)

st.title("Events Near You")

@st.cache_data(ttl=600)
def load_data():
    df = pd.read_csv("event_data.csv")
    df["start_time"] = pd.to_datetime(df["start_time"], errors="coerce")
    df["end_time"] = pd.to_datetime(df["end_time"], errors="coerce")
    if "location" not in df.columns:
        df["location"] = ""
    return df

df = load_data()

location = st.text_input("📍 Neighborhood", value="San Francisco", label_visibility="collapsed",
                         placeholder="📍 Your neighborhood (e.g. Mission District)")

if st.button("Discover Events ✨", type="primary", use_container_width=True):
    with st.spinner("Finding the best events near you..."):
        loc_lower = location.lower()
        loc_matches = df[df["location"].str.lower().str.contains(loc_lower, na=False)]

        if len(loc_matches) == 0:
            loc_matches = df[
                df["title"].str.lower().str.contains(loc_lower, na=False)
                | df["description"].str.lower().str.contains(loc_lower, na=False)
            ]

        if len(loc_matches) >= 5:
            sample = loc_matches.sample(min(15, len(loc_matches))).copy()
        else:
            extra = df[~df.index.isin(loc_matches.index)].sample(min(15 - len(loc_matches), len(df) - len(loc_matches)))
            sample = pd.concat([loc_matches, extra]).copy()

        compact = "\n".join([
            f"{i}|{row.title}|{str(row.get('location',''))}|{str(row.tags)[:40]}"
            for i, row in sample.iterrows()
        ])

        prompt = f"User in {location}. Pick 5 most relevant/fun events for this area. Prefer events in or near {location}. Return JSON: {{\"picks\":[{{\"id\":int,\"why\":\"<8 words>\"}}]}}\n\n{compact}"

        response = client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=300,
            response_format={"type": "json_object"}
        )

        raw = json.loads(response.choices[0].message.content)
        if isinstance(raw, list):
            result = raw
        else:
            result = next((v for v in raw.values() if isinstance(v, list)), [])

        top_ids = [int(item["id"]) for item in result]
        top_events = sample[sample.index.isin(top_ids)].copy()
        why_map = {int(item["id"]): item.get("why", "") for item in result}

        if top_events.empty:
            top_events = sample.head(5).copy()

        imgs = random.sample(COVER_IMAGES, min(len(top_events), len(COVER_IMAGES)))

        cards_html = ""
        for idx, (row_idx, row) in enumerate(top_events.head(5).iterrows()):
            img = imgs[idx % len(imgs)]
            date_str = row["start_time"].strftime("%a, %b %d, %H:%M") if pd.notna(row["start_time"]) else ""
            loc_str = str(row.get("location", "")) if pd.notna(row.get("location", "")) else ""
            tags_raw = str(row.get("tags", "")).replace("[", "").replace("]", "").replace('"', "")
            tag_list = [t.strip() for t in tags_raw.split(",") if t.strip()]
            cat = str(row.get("category", "other"))
            emoji = CATEGORY_EMOJI.get(cat, "📌")
            attendee_count = random.randint(3, 80)

            tag_html = "".join(
                f'<span class="tag-pill">{emoji if i == 0 else ""} {t}</span>'
                for i, t in enumerate(tag_list[:2])
            )

            avatar_html = "".join(
                f'<img class="avatar" src="https://i.pravatar.cc/60?img={random.randint(1,70)}">'
                for _ in range(min(3, attendee_count))
            )

            cards_html += f"""
<div class="event-card">
    <img src="{img}" alt="event">
    <div class="card-body">
        <div class="tag-row">{tag_html}</div>
        <div class="event-title">{row["title"]}</div>
        <p class="event-meta">{date_str}{f"  /  {loc_str}" if loc_str else ""}</p>
        <div class="join-row">
            <div class="attendees">{avatar_html}<span class="count">+{attendee_count}</span></div>
            <button class="join-btn">Join</button>
        </div>
    </div>
</div>"""

        st.markdown(f'<div class="cards-scroll">{cards_html}</div>', unsafe_allow_html=True)

st.markdown("""
<div class="bottom-nav">
    <div class="nav-item">🏠<br>Home</div>
    <div class="nav-item active">🎟️<br>Events</div>
    <div class="nav-item">💬<br>Chat</div>
    <div class="nav-item">👤<br>Profile</div>
</div>
""", unsafe_allow_html=True)
