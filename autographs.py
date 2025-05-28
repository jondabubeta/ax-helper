import os
import json
import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
CHANNEL_NAME = os.getenv("DISCORD_CHANNEL_NAME")

# Load autograph list
with open("autograph_list_state.json", "r") as f:
    autograph_data = json.load(f)
autograph_list = autograph_data.get("list", [])

# Build message content
content = "📋 **Autograph List**\n\n" + "\n".join([f"- {a['name']}: {a['link']}" for a in autograph_list])

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"🤖 Logged in as {client.user}")
    for guild in client.guilds:
        channel = discord.utils.get(guild.text_channels, name=CHANNEL_NAME)
        if channel:
            # Check for pinned messages
            pins = await channel.pins()
            if pins:
                print("📝 Editing existing pinned message...")
                await pins[0].edit(content=content)
            else:
                print("📌 Sending and pinning new message...")
                msg = await channel.send(content)
                await msg.pin()
            break
    await client.close()

client.run(TOKEN)
