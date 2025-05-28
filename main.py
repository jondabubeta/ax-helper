import os
import time
import requests
from bs4 import BeautifulSoup
import json
from dotenv import load_dotenv
from datetime import datetime
from autographs import trigger_discord_update

# Load environment variables
load_dotenv()

# Configurable variables
URL = os.getenv('EVENT_URL', 'https://store.epic.leapevent.tech/anime-expo/2025')
STATE_FILE = os.getenv('STATE_FILE', 'autograph_list_state.json')
CHECK_INTERVAL_SECONDS = int(os.getenv('CHECK_INTERVAL_SECONDS', 30))

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
        autographs.append({ "name": name, "link": full_url })
        if verbose:
            print(f" - {name}: {full_url}")
    return autographs

def load_previous_state():
    if not os.path.exists(STATE_FILE):
        return {'list': [], 'count': 0}
    with open(STATE_FILE, 'r') as f:
        return json.load(f)

def save_current_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def lists_differ(a, b):
    return json.dumps(a, sort_keys=True) != json.dumps(b, sort_keys=True)

def monitor_loop():
    print("🔄 Starting monitor loop...")
    while True:
        now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{now_str}] Checking for updates...")

        previous_state = load_previous_state()
        current_list = fetch_autograph_list(verbose=True)
        current_count = len(current_list)

        if lists_differ(previous_state.get('list', []), current_list):
            print("⚠️ Autograph list has changed.")
        else:
            print("✅ Autograph list unchanged.")

        # Always sync with Discord, update only if needed (handled in autograph.py)
        trigger_discord_update(current_list)

        save_current_state({ 'list': current_list, 'count': current_count })
        print(f"[{now_str}] Sleeping for {CHECK_INTERVAL_SECONDS} seconds...\n")
        time.sleep(CHECK_INTERVAL_SECONDS)

if __name__ == "__main__":
    monitor_loop()
