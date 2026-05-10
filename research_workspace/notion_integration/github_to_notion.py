import os
import sys
from notion_client import Client

# ---------------------------------------------------------
# 1. Load Environment Variables (Passed by GitHub Actions)
# ---------------------------------------------------------
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

EVENT_NAME = os.getenv("EVENT_NAME", "unknown_event")
ACTION = os.getenv("ACTION_TYPE", "opened")
TITLE = os.getenv("ISSUE_TITLE", "Untitled Task")
URL = os.getenv("ISSUE_URL", "")
AUTHOR = os.getenv("ISSUE_AUTHOR", "Axiom System")

def sync_to_notion():
    if not all([NOTION_TOKEN, DATABASE_ID]):
        print("CRITICAL: Missing Notion API credentials in environment variables.")
        sys.exit(1)

    notion = Client(auth=NOTION_TOKEN)

    # ---------------------------------------------------------
    # 2. Map GitHub Actions to Notion Kanban Statuses
    # ---------------------------------------------------------
    # Assuming your Notion Database has a 'Status' property with these exact options
    status_name = "In Progress"
    if ACTION in ["opened", "reopened"]:
        status_name = "Not Started"
    elif ACTION == "closed":
        status_name = "Done"

    # ---------------------------------------------------------
    # 3. Construct the Notion Page Payload
    # ---------------------------------------------------------
    new_page_props = {
        # The primary column in your Notion DB (usually 'Name' or 'Task')
        "Task": {
            "title": [{"text": {"content": f"[{EVENT_NAME.upper()}] {TITLE}"}}]
        },
        "Status": {
            "status": {"name": status_name}
        },
        "Link": {
            "url": URL
        },
        "Assignee": {
            "rich_text": [{"text": {"content": AUTHOR}}]
        }
    }

    # ---------------------------------------------------------
    # 4. Execute API Call
    # ---------------------------------------------------------
    try:
        response = notion.pages.create(
            parent={"database_id": DATABASE_ID},
            properties=new_page_props
        )
        print(f"✅ Successfully synced '{TITLE}' to Notion. Status set to: {status_name}")
    except Exception as e:
        print(f"❌ Error syncing to Notion: {e}")
        sys.exit(1)

if __name__ == "__main__":
    sync_to_notion()