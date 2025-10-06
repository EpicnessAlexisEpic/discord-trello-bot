import os
import requests

# GitHub Actions will provide these via Secrets
TRELLO_KEY = os.getenv("TRELLO_KEY")
TRELLO_TOKEN = os.getenv("TRELLO_TOKEN")
TRELLO_BOARD_ID = os.getenv("TRELLO_BOARD_ID")
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK")

# URLs to fetch board data
BOARD_URL = f"https://api.trello.com/1/boards/{TRELLO_BOARD_ID}/lists?cards=open&card_fields=name&checklists=all&fields=name&key={TRELLO_KEY}&token={TRELLO_TOKEN}"

def get_board_data():
    """Fetch all lists and cards from Trello board"""
    r = requests.get(BOARD_URL)
    r.raise_for_status()
    return r.json()

def generate_report(board_data):
    """Generate Trello-style report with lists, cards, and checklists"""
    lines = []
    total_cards = 0
    completed_cards = 0
    total_checklist_items = 0
    completed_checklist_items = 0

    for lst in board_data:
        list_name = lst["name"]
        lines.append(f"📋 {list_name}")

        for card in lst.get("cards", []):
            card_name = card["name"]

            # Determine card completion: all checklist items complete OR no checklist
            if card.get("checklists"):
                checklist_items = [item for cl in card["checklists"] for item in cl["checkItems"]]
                card_done = all(item["state"] == "complete" for item in checklist_items)
            else:
                card_done = False  # no checklist → mark incomplete
            card_status = "✅" if card_done else "❌"
            lines.append(f"├─ {card_name} - {card_status}")
            total_cards += 1
            if card_done:
                completed_cards += 1

            # Add checklist items
            for checklist in card.get("checklists", []):
                for item in checklist["checkItems"]:
                    item_name = item["name"]
                    item_status = "✅" if item["state"] == "complete" else "❌"
                    lines.append(f"│   ├─ {item_name} - {item_status}")
                    total_checklist_items += 1
                    if item["state"] == "complete":
                        completed_checklist_items += 1

        lines.append("")  # blank line between lists

    report_text = "\n".join(lines)
    summary = (
        f"Trello Board Report: {len(board_data)} lists, {total_cards} cards ({completed_cards} completed ✅), "
        f"{total_checklist_items} checklist items ({completed_checklist_items} completed ✅)"
    )
    return report_text, summary

def send_to_discord_file(report_text, summary):
    """Send summary and full report as a text file"""
    # Send summary message
    requests.post(WEBHOOK_URL, json={"content": summary}).raise_for_status()

    # Save full report as file
    with open("trello_report.txt", "w", encoding="utf-8") as f:
        f.write(report_text)

    # Send file to Discord
    with open("trello_report.txt", "rb") as f:
        r = requests.post(WEBHOOK_URL, files={"file": f})
        r.raise_for_status()

if __name__ == "__main__":
    board_data = get_board_data()
    report_text, summary = generate_report(board_data)
    send_to_discord_file(report_text, summary)