# trello_report.py
import os
import requests
import datetime
import sys

# --- CONFIG via ENV ---
TRELLO_KEY = os.getenv("TRELLO_KEY")
TRELLO_TOKEN = os.getenv("TRELLO_TOKEN")
BOARD_ID = os.getenv("BOARD_ID")
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")  # create in Discord server Integrations -> Webhooks

if not all([TRELLO_KEY, TRELLO_TOKEN, BOARD_ID, DISCORD_WEBHOOK]):
    print("ERROR: missing one of required env vars: TRELLO_KEY, TRELLO_TOKEN, BOARD_ID, DISCORD_WEBHOOK")
    sys.exit(2)

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
    # A card is "✅" if dueComplete is True OR it has checklist(s) and all checklist items are complete.
    if card.get("dueComplete"):
        return True
    if not checklists:
        return False
    # if there are check items, verify all are complete
    for cl in checklists:
        items = cl.get("checkItems", [])
        if not items:
            continue
        # if any item is not complete -> not done
        for it in items:
            if it.get("state") != "complete":
                return False
    # if we had checklists and no item is incomplete, consider done
    return True

def generate_report(board_id, filename="trello_report.txt"):
    lists = get_board_lists(board_id)
    lines = []
    now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    lines.append(f"Trello Report generated on {now}\n")

    for lst in lists:
        lines.append(f"[{lst['name']}]")
        cards = get_cards_for_list(lst['id'])
        if not cards:
            lines.append(" - (no cards)")
            lines.append("")  # blank line
            continue

        for card in cards:
            checklists = get_checklists_for_card(card['id'])
            status = "✅" if card_is_done(card, checklists) else "❌"
            lines.append(f" - {card['name']} - {status}")
            # Attach checklists (if any)
            for checklist in checklists:
                # each checklist has checkItems
                for item in checklist.get("checkItems", []):
                    item_state = "✅" if item.get("state") == "complete" else "❌"
                    # indent to match your requested format
                    lines.append(f"      - {item.get('name')}  - {item_state}")
        lines.append("")  # blank line between lists

    text = "\n".join(lines)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)
    return filename

def send_file_to_discord_webhook(webhook_url, filename, content="📋 Daily Trello Report"):
    with open(filename, "rb") as f:
        files = {"file": (filename, f)}
        data = {"content": content}
        r = requests.post(webhook_url, data=data, files=files)
    if r.status_code >= 200 and r.status_code < 300:
        print("Uploaded report to Discord (webhook).")
    else:
        print("Failed to upload to Discord:", r.status_code, r.text)
        r.raise_for_status()

def main():
    print("Generating report...")
    fname = generate_report(BOARD_ID)
    print("Report saved to", fname)
    print("Sending to Discord webhook...")
    send_file_to_discord_webhook(DISCORD_WEBHOOK, fname)
    print("Done.")

if __name__ == "__main__":
    main()