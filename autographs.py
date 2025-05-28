
import os
import discord
import asyncio
import json
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
CHANNEL_NAME = os.getenv("DISCORD_CHANNEL_NAME")
STATE_FILE = "last_sent_state.json"

intents = discord.Intents.default()
intents.message_content = True
MAX_MSG_LEN = 2000

def split_autograph_messages(autographs):
    chunks = []
    current = "📋 **Autograph List**\n\n"

    for a in autographs:
        line = f"- {a['name']}: {a['link']}\n"
        if len(current) + len(line) > MAX_MSG_LEN:
            chunks.append(current.strip())
            current = line
        else:
            current += line

    if current.strip():
        chunks.append(current.strip())

    return chunks

def load_last_sent_state():
    if not os.path.exists(STATE_FILE):
        return []
    with open(STATE_FILE, "r") as f:
        return json.load(f).get("list", [])

def save_last_sent_state(autograph_list):
    with open(STATE_FILE, "w") as f:
        json.dump({ "list": autograph_list }, f, indent=2)

def lists_differ(a, b):
    return json.dumps(a, sort_keys=True) != json.dumps(b, sort_keys=True)

async def update_discord_message(autograph_list):
    last_sent = load_last_sent_state()

    if not lists_differ(last_sent, autograph_list):
        print("✅ Autograph list already synced with Discord. No update needed.")
        return

    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print(f"🤖 Logged in as {client.user}")
        try:
            for guild in client.guilds:
                channel = discord.utils.get(guild.text_channels, name=CHANNEL_NAME)
                if not channel:
                    print(f"❌ Channel '{CHANNEL_NAME}' not found in {guild.name}")
                    continue

                print(f"✅ Found channel: {channel.name}")

                new_chunks = split_autograph_messages(autograph_list)
                existing_pins = await channel.pins()

                for msg in existing_pins:
                    await msg.unpin()

                sent_messages = []
                for chunk in new_chunks:
                    msg = await channel.send(chunk)
                    sent_messages.append(msg)

                if sent_messages:
                    await sent_messages[0].pin()
                    print(f"📌 Pinned first of {len(sent_messages)} messages.")

                save_last_sent_state(autograph_list)
                print("💾 Saved current list as last sent state.")

        except Exception as e:
            print(f"❌ Error inside on_ready: {e}")
        finally:
            await client.close()

    await client.start(TOKEN)

def trigger_discord_update(autograph_list):
    asyncio.run(update_discord_message(autograph_list))
