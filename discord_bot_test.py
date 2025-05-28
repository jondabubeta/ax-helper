# test_bot.py
import os
import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

client = discord.Client(intents=discord.Intents.default())

@client.event
async def on_ready():
    print(f"✅ Connected as {client.user}")
    await client.close()

client.run(TOKEN)
