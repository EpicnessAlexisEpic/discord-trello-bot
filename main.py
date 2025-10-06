# main.py
import os
import discord
from discord.ext import tasks
import requests

# --- Load secrets from environment ---
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
TRELLO_KEY = os.getenv("TRELLO_KEY")
TRELLO_TOKEN = os.getenv("TRELLO_TOKEN")
BOARD_ID = os.getenv("TRELLO_BOARD_ID")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

if not all([DISCORD_TOKEN, TRELLO_KEY, TRELLO_TOKEN, BOARD_ID, CHANNEL_ID]):
    raise Exception("One or more environment variables are missing!")

API_AUTH = {"key": TRELLO_KEY, "token": TRELLO_TOKEN}

# --- Functions to get Trello data ---
def get_board_lists(board_id):
    url = f"https://api.trello.com/1/boards/{board_id}/lists"
    r = requests.get(url, params=API_AUTH)
    r.raise_for_status()
    return r.json()

def get_cards_for_list(list_id):
    url = f"https://api.trello.com/1/lists/{list_id}/cards"
    params = {"fields": "name,dueComplete,id"}
    params.update(API_AUTH)
    r = requests.get(url, params=params)
    r.raise_for_status()
    return r.json()

def get_checklists_for_card(card_id):
    url = f"https://api.trello.com/1/cards/{card_id}/checklists"
    r = requests.get(url, params=API_AUTH)
    r.raise_for_status()
    return r.json()

def card_is_done(card, checklists):
    if card.get("dueComplete"):
        return True
    if not checklists:
        return False
    for cl in checklists:
        for item in cl.get("checkItems", []):
            if item.get("state") != "complete":
                return False
    return True

def generate_report(board_id, filename="trello_report.txt"):
    lists = get_board_lists(board_id)
    lines = []

    for lst in lists:
        lines.append(f"[{lst['name']}]")
        cards = get_cards_for_list(lst['id'])
        if not cards:
            lines.append(" - (no cards)")
            lines.append("")
            continue

        for card in cards:
            checklists = get_checklists_for_card(card['id'])
            status = "✅" if card_is_done(card, checklists) else "❌"
            lines.append(f" - {card['name']} - {status}")
            for checklist in checklists:
                for item in checklist.get("checkItems", []):
                    item_state = "✅" if item.get("state") == "complete" else "❌"
                    lines.append(f"      - {item.get('name')}  - {item_state}")
        lines.append("")

    text = "\n".join(lines)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)
    return filename

# --- Discord bot ---
intents = discord.Intents.default()
intents.messages = True
bot = discord.Bot(intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    send_report.start()  # start the scheduled task

# --- Task to send report every 24h ---
@tasks.loop(hours=24)
async def send_report():
    channel = bot.get_channel(CHANNEL_ID)
    if channel is None:
        print("Channel not found!")
        return

    filename = generate_report(BOARD_ID)
    try:
        await channel.send(file=discord.File(filename))
        print("Report sent to Discord channel.")
    except Exception as e:
        print("Failed to send report:", e)

# --- Run bot ---
bot.run(DISCORD_TOKEN)