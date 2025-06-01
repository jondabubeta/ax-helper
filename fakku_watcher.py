import os
import re
import requests
import difflib
import asyncio
from dotenv import load_dotenv
from datetime import datetime
import discord

# Load environment variables
load_dotenv()

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
FAKKU_CHANNEL_NAME = os.getenv("FAKKU_CHANNEL_NAME", "fakku-watcher")
FAKKU_URL = "https://www.fakku.net/fakku-anime-expo-2025"
FAKKU_STATE_FILE = "fakku_page_state.html"
FAKKU_INTERVAL = int(os.getenv("FAKKU_CHECK_INTERVAL_SECONDS", 60))
DISCORD_MSG_LIMIT = 2000
MAX_DIFF_LINES = 1000

intents = discord.Intents.default()
intents.message_content = True

def fetch_page():
    response = requests.get(FAKKU_URL)
    response.raise_for_status()
    html = response.text

    # Normalize whitespace
    normalized = html.replace('\r\n', '\n').strip()
    normalized = '\n'.join(line.strip() for line in normalized.splitlines())

    # ❌ Remove <style> blocks entirely
    normalized = re.sub(r'<style[^>]*>.*?</style>', '', normalized, flags=re.DOTALL | re.IGNORECASE)

    # Optionally: also remove <script> and <meta> if noisy
    normalized = re.sub(r'<(script|meta)[^>]*>.*?</\1>', '', normalized, flags=re.DOTALL | re.IGNORECASE)

    return normalized

def load_previous_html():
    if not os.path.exists(FAKKU_STATE_FILE):
        return ""
    with open(FAKKU_STATE_FILE, "r", encoding="utf-8") as f:
        return f.read()

def save_current_html(html):
    with open(FAKKU_STATE_FILE, "w", encoding="utf-8") as f:
        f.write(html)

def split_diff_by_characters(diff_lines):
    messages = []
    current_block = "```diff\n"

    for line in diff_lines:
        # If line itself is too long, chunk it
        while len(line) > DISCORD_MSG_LIMIT - len("```diff\n\n```") - 3:
            part = line[:DISCORD_MSG_LIMIT - len("```diff\n\n```") - 3]
            messages.append(f"```diff\n{part}\n```")
            line = line[len(part):]

        # Add line to current block
        if len(current_block) + len(line) + 1 > DISCORD_MSG_LIMIT - len("```"):
            current_block += "\n```"
            messages.append(current_block)
            current_block = "```diff\n" + line
        else:
            current_block += "\n" + line

    if current_block.strip():
        current_block += "\n```"
        messages.append(current_block)

    return messages

def generate_diff_chunks(old, new):
    old_lines = old.splitlines()
    new_lines = new.splitlines()
    diff = list(difflib.unified_diff(old_lines, new_lines, lineterm=""))
    if not diff:
        return None
    return split_diff_by_characters(diff[:MAX_DIFF_LINES])

async def send_discord_alert(banner, diff_chunks):
    client = discord.Client(intents=intents)

    async def send_messages():
        print(f"🤖 Logged in as {client.user}")
        try:
            for guild in client.guilds:
                print(f"🔍 In guild: {guild.name}")
                for channel in guild.text_channels:
                    print(f" - #{channel.name}")
                channel = discord.utils.get(guild.text_channels, name=FAKKU_CHANNEL_NAME)
                if not channel:
                    print(f"❌ Channel '{FAKKU_CHANNEL_NAME}' not found in {guild.name}")
                    continue

                await channel.send(banner)
                for chunk in diff_chunks:
                    await channel.send(chunk)
                print("✅ Sent change alert.")
        except Exception as e:
            print(f"❌ Error sending Discord alert: {e}")

    @client.event
    async def on_ready():
        await send_messages()
        await client.close()

    await client.start(DISCORD_BOT_TOKEN)

def run_fakku_monitor():
    print(f"[{datetime.now()}] Checking FAKKU page...")
    new_html = fetch_page()

    if not os.path.exists(FAKKU_STATE_FILE):
        print("📌 No baseline found — saving current page as baseline.")
        save_current_html(new_html)
        return

    old_html = load_previous_html()

    if old_html.strip() == new_html.strip():
        print("✅ No changes detected.")
        return

    diff_chunks = generate_diff_chunks(old_html, new_html)
    banner = "⚠️ FAKKU AX 2025 page has changed!"

    save_current_html(new_html)
    print("💾 Updated local HTML snapshot.")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(send_discord_alert(banner, diff_chunks or ["(No visible difference)"]))
    finally:
        loop.run_until_complete(asyncio.sleep(1))  # Allow graceful close
        loop.close()

def run_monitor_loop():
    print("🔄 Starting FAKKU monitoring loop...")
    while True:
        run_fakku_monitor()
        print(f"⏲️ Sleeping for {FAKKU_INTERVAL} seconds...\n")
        time.sleep(FAKKU_INTERVAL)

if __name__ == "__main__":
    import time
    run_monitor_loop()

