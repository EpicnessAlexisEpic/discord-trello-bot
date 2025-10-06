import os
import requests

# Load environment variables
TRELLO_KEY = os.getenv("TRELLO_KEY")
TRELLO_TOKEN = os.getenv("TRELLO_TOKEN")
BOARD_ID = os.getenv("TRELLO_BOARD_ID")
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK")

API_AUTH = {"key": TRELLO_KEY, "token": TRELLO_TOKEN}

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

def generate_report(board_id):
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

    return "\n".join(lines)

def send_to_discord(message):
    data = {"content": f"```{message}```"}
    r = requests.post(WEBHOOK_URL, json=data)
    r.raise_for_status()

if __name__ == "__main__":
    report = generate_report(BOARD_ID)
    send_to_discord(report)
    print("Report sent!")