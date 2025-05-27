import os
import time
import requests
from bs4 import BeautifulSoup
import json
from dotenv import load_dotenv
from datetime import datetime

# Load configuration from .env file
load_dotenv()

# Configurable variables
URL = os.getenv('EVENT_URL', 'https://store.epic.leapevent.tech/anime-expo/2025')
STATE_FILE = os.getenv('STATE_FILE', 'autograph_list_state.json')
CHECK_INTERVAL_SECONDS = int(os.getenv('CHECK_INTERVAL_SECONDS', 30))  # default: 30 seconds
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')

def fetch_autograph_list(verbose=False):
    session = requests.Session()
    response = session.get(URL)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    cards = soup.select('#productContainer .ProductCard')
    autographs = []

    for card in cards:
        name_tag = card.select_one('.ProductTitle')
        link_tag = card.select_one('a')

        name = name_tag.get_text(strip=True) if name_tag else 'Unknown'
        link = link_tag['href'] if link_tag and link_tag.has_attr('href') else ''
        full_url = f"https://store.epic.leapevent.tech{link}" if link.startswith('/') else link

        autograph_details = {
            "name": name,
            "link": full_url
        }

        if verbose:
            print(f" - {name}: {full_url}")

        autographs.append(autograph_details)

    return autographs

def load_previous_state():
    if not os.path.exists(STATE_FILE):
        return {'list': [], 'count': 0}
    with open(STATE_FILE, 'r') as f:
        return json.load(f)

def save_current_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def send_discord_webhook(message):
    if not DISCORD_WEBHOOK_URL:
        print("No Discord webhook URL configured.")
        return

    payload = {"content": message}
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        response.raise_for_status()
        print(f"[{datetime.now()}] Discord notification sent.")
    except requests.exceptions.RequestException as e:
        print(f"[{datetime.now()}] Failed to send Discord message: {e}")

def monitor_loop():
    baseline_env = os.getenv("BASELINE_COUNT")
    baseline_count = int(baseline_env) if baseline_env and baseline_env.isdigit() else None

    if baseline_count is None:
        print("No baseline defined in .env — fetching initial count...")
        initial_list = fetch_autograph_list(verbose=True)
        baseline_count = len(initial_list)
        print(f"Using initial autograph count as baseline: {baseline_count}")

    while True:
        now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{now_str}] Starting check...")

        current_list = fetch_autograph_list(verbose=True)
        current_count = len(current_list)
        print(f"[{now_str}] Found {current_count} autograph(s). (Baseline: {baseline_count})")

        if current_count != baseline_count:
            message = f"⚠️ Autograph count changed: {current_count} (Expected: {baseline_count})"
            send_discord_webhook(message)
        else:
            print(f"[{now_str}] Autograph count is {baseline_count} — all good.")

        # Save current list and count
        save_current_state({
            'list': current_list,
            'count': current_count
        })
        print(f"[{now_str}] Saved current state to {STATE_FILE}")
        print(f"[{now_str}] Sleeping for {CHECK_INTERVAL_SECONDS} seconds...\n")
        time.sleep(CHECK_INTERVAL_SECONDS)

if __name__ == "__main__":
    monitor_loop()
