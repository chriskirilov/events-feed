import pandas as pd
import json
import os
import time
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GMI_API_KEY"),
    base_url="https://api.gmi-serving.com/v1"
)

CSV_PATH = "event_data.csv"
BATCH_SIZE = 100

df = pd.read_csv(CSV_PATH)

if "location" not in df.columns:
    df["location"] = ""

remaining = df[df["location"].astype(str).isin(["", "nan"])].index.tolist()
total = len(remaining)
print(f"Events needing locations: {total}")

for batch_start in range(0, total, BATCH_SIZE):
    batch_idx = remaining[batch_start:batch_start + BATCH_SIZE]
    batch = df.loc[batch_idx]
    batch_num = batch_start // BATCH_SIZE + 1
    total_batches = (total + BATCH_SIZE - 1) // BATCH_SIZE
    print(f"\nBatch {batch_num}/{total_batches} ({len(batch_idx)} events)...")

    lines = []
    for i, row in batch.iterrows():
        title = str(row.get("title", ""))[:80]
        desc = str(row.get("description", ""))[:120]
        url = str(row.get("source_url", ""))[:100]
        lines.append(f"{i}|{title}|{desc}|{url}")

    events_block = "\n".join(lines)

    prompt = (
        "Extract the city and US state for each event from its title, description, and URL. "
        "Use format 'City, State' (e.g. 'San Francisco, CA'). "
        "If only a state or county is clear, use that (e.g. 'Montgomery County, MD'). "
        "If no location can be determined, use 'Unknown'. "
        "Return JSON: {\"locations\":{\"<id>\":\"<location>\"}}\n\n"
        f"{events_block}"
    )

    for attempt in range(3):
        try:
            resp = client.chat.completions.create(
                model="openai/gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=4000,
                response_format={"type": "json_object"}
            )
            raw = json.loads(resp.choices[0].message.content)
            locs = raw.get("locations", raw)

            filled = 0
            for str_id, loc in locs.items():
                idx = int(str_id)
                if idx in df.index and loc and loc != "Unknown":
                    df.at[idx, "location"] = loc
                    filled += 1

            print(f"  Filled {filled}/{len(batch_idx)} locations")
            break
        except Exception as e:
            print(f"  Attempt {attempt+1} failed: {e}")
            if attempt < 2:
                time.sleep(2)

    df.to_csv(CSV_PATH, index=False)
    print(f"  Saved progress to {CSV_PATH}")
    time.sleep(0.3)

known = df["location"].astype(str).apply(lambda x: x not in ["", "nan", "Unknown"]).sum()
print(f"\nDone! {known}/{len(df)} events have locations.")
