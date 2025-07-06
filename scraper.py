import os
import json
import requests
import datetime
from bs4 import BeautifulSoup

# URL and paths
url = "https://www.singaporepools.com.sg/DataFileArchive/Lottery/Output/fourd_result_top_draws_en.html"
json_out = os.path.join("docs", "result.json")
os.makedirs("debug", exist_ok=True)

# Fetch and parse HTML
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")
draw_tables = soup.select("table.orange-header")

# Load existing results
if os.path.exists(json_out):
    with open(json_out, "r", encoding="utf-8") as f:
        existing = json.load(f)
else:
    existing = []

# ✅ EARLY EXIT: Skip if latest known draw_no matches the most recent online
if existing:
    latest_known_draw = existing[0].get("draw_no", "")
    try:
        latest_scraped_draw = draw_tables[0].select_one("th.drawNumber").text.strip().split("Draw No.")[1].strip()
        if latest_scraped_draw == latest_known_draw:
            msg = f"✅ Already have latest draw no. {latest_known_draw}. Exiting."
            print(msg)
            with open("debug/debug_log.txt", "a") as f:
                f.write(f"[{datetime.datetime.now().isoformat()}] {msg}\n")
            exit(0)
    except Exception as e:
        msg = f"⚠️ Failed early-exit check: {e}"
        print(msg)
        with open("debug/debug_log.txt", "a") as f:
            f.write(f"[{datetime.datetime.now().isoformat()}] {msg}\n")

# Track existing draw numbers
existing_draws = {d["draw_no"] for d in existing if "draw_no" in d}
if existing:
    with open("debug/last_known_draw.txt", "w") as f:
        f.write(existing[0].get("draw_no", ""))

# Parse all draw tables
all_results = []
for main_table in draw_tables:
    starter_table = main_table.find_next_sibling("table", class_="table-striped")
    consolation_table = starter_table.find_next_sibling("table", class_="table-striped") if starter_table else None
    if not (starter_table and consolation_table):
        print("⚠️ Skipping table due to missing starter/consolation sections.")
        continue

    try:
        draw_date = main_table.select_one("th.drawDate").text.strip()
        draw_no = main_table.select_one("th.drawNumber").text.strip().split("Draw No.")[1].strip()
        rows = main_table.select("tbody tr")
        first = rows[0].select("td")[0].text.strip()
        second = rows[1].select("td")[0].text.strip()
        third = rows[2].select("td")[0].text.strip()
        starter = [td.text.strip() for td in starter_table.select("tbody tr td")]
        consolation = [td.text.strip() for td in consolation_table.select("tbody tr td")]
    except Exception as e:
        print(f"⚠️ Error parsing draw table: {e}")
        continue

    if not draw_no:
        print("⚠️ Empty draw_no. Skipping.")
        continue

    if draw_no in existing_draws:
        print(f"ℹ️ draw_no {draw_no} already exists. Skipping.")
        continue

    result = {
        "draw_date": draw_date,
        "draw_no": draw_no,
        "first": first,
        "second": second,
        "third": third,
        "starter_prizes": starter,
        "consolation_prizes": consolation
    }

    all_results.append(result)
    with open("debug/scraped_draw.txt", "w") as f:
        f.write(draw_no)

# Save if new results were found
if all_results:
    combined = all_results + existing
    with open(json_out, "w", encoding="utf-8") as f:
        json.dump(combined, f, indent=2)
    msg = f"✅ Added {len(all_results)} new result(s)"
else:
    msg = "ℹ️ No new results found"

# Log outcome
print(msg)
with open("debug/debug_log.txt", "a") as f:
    f.write(f"[{datetime.datetime.now().isoformat()}] {msg}\n")
