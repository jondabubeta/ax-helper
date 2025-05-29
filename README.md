# 🎟️ Anime Expo Autograph Watcher

This tool monitors the Anime Expo autograph sales page and automatically syncs the latest list to a pinned message in a Discord channel.

It helps fans avoid manual refreshing and ensures your Discord stays up to date with current autograph listings.

---

## 🚀 Features

- ✅ Monitors the Anime Expo autograph page (`epic.leapevent.tech`)
- ✅ Sends the full autograph list to a Discord channel
- ✅ Automatically splits long messages (Discord 2000-char limit)
- ✅ Pins the first message for visibility
- ✅ Unpins outdated messages
- ✅ Tracks and saves the last list sent to avoid redundant updates
- ✅ Runs continuously on a loop

---

## 🛠️ Requirements

- Python 3.8+
- A Discord bot with the following permissions:
  - `Send Messages`
  - `Read Message History`
  - `Manage Messages`

Install dependencies:

```bash
pip install -r requirements.txt
```

## 📬 Discord Bot Integration

This project uses a full **Discord bot**, not just a webhook.

### 🔧 How It Works

- The bot connects to your server using the `DISCORD_BOT_TOKEN`.
- It looks for the channel named `DISCORD_CHANNEL_NAME`.
- The autograph list is formatted into multiple messages (each ≤ 2000 characters).
- All previous pinned messages in that channel are unpinned.
- The new messages are sent, and the **first message is pinned**.