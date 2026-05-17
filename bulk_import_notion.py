#!/usr/bin/env python3
"""
Bulk import all vocab_data.json entries to Notion.
Requires notion_token in config.json.

Usage:
  python3 bulk_import_notion.py
  python3 bulk_import_notion.py --dry-run   # preview only
"""

import json, os, sys, time
import urllib.request, urllib.error

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
VOCAB_JSON  = os.path.join(SCRIPT_DIR, "vocab_data.json")
CONFIG_JSON = os.path.join(SCRIPT_DIR, "config.json")

NOTION_API  = "https://api.notion.com/v1/pages"
NOTION_VER  = "2022-06-28"

def load_config():
    with open(CONFIG_JSON) as f:
        return json.load(f)

def parse_month(date_added):
    try: return int(date_added.split("/")[0])
    except: return 0

def make_page(entry, db_id):
    cats = entry.get("categories", ["general"])
    month = parse_month(entry.get("date_added", ""))
    return {
        "parent": {"database_id": db_id},
        "properties": {
            "Word":           {"title": [{"text": {"content": entry["word"][:200]}}]},
            "Meaning (JA)":  {"rich_text": [{"text": {"content": (entry.get("meaning_ja") or "")[:2000]}}]},
            "Definition (EN)":{"rich_text": [{"text": {"content": (entry.get("english_def") or "")[:2000]}}]},
            "Example":        {"rich_text": [{"text": {"content": (entry.get("example") or "")[:2000]}}]},
            "Notes":          {"rich_text": [{"text": {"content": (entry.get("notes") or "")[:2000]}}]},
            "Category":       {"multi_select": [{"name": c} for c in cats]},
            "Mastery":        {"select": {"name": entry.get("mastery", "new")}},
            "Year":           {"number": entry.get("year", 2020)},
            "Month":          {"number": month},
            "Date Added":     {"rich_text": [{"text": {"content": entry.get("date_added", "")}}]},
        }
    }

def create_page(page_data, token):
    payload = json.dumps(page_data, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        NOTION_API, data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Notion-Version": NOTION_VER,
        },
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read()), None
    except urllib.error.HTTPError as e:
        return None, f"HTTP {e.code}: {e.read().decode()[:200]}"
    except Exception as e:
        return None, str(e)

def main():
    dry_run = "--dry-run" in sys.argv

    config = load_config()
    token = config.get("notion_token", "")
    db_id = config.get("notion_db_id", "")

    if not token and not dry_run:
        print("Error: notion_token not set in config.json")
        print("  1. Go to https://www.notion.so/my-integrations")
        print("  2. Create integration, copy token")
        print("  3. Share the 英語単語帳 database with the integration")
        print("  4. Add token to config.json: {\"notion_token\": \"ntn_...\"}")
        sys.exit(1)

    if not db_id:
        print("Error: notion_db_id not set in config.json")
        sys.exit(1)

    with open(VOCAB_JSON, encoding="utf-8") as f:
        vocab = json.load(f)

    print(f"{'[DRY RUN] ' if dry_run else ''}Importing {len(vocab)} entries to Notion db: {db_id}")

    ok, fail = 0, 0
    for i, entry in enumerate(vocab):
        page = make_page(entry, db_id)
        if dry_run:
            print(f"  [{i+1:3d}] Would create: {entry['word']}")
            ok += 1
            continue

        result, err = create_page(page, token)
        if result:
            ok += 1
            if (i+1) % 20 == 0:
                print(f"  Progress: {ok}/{len(vocab)} ({fail} errors)")
        else:
            fail += 1
            print(f"  [FAIL] {entry['word']}: {err}")

        # Rate limit: Notion allows ~3 req/sec
        time.sleep(0.35)

    print(f"\nDone: {ok} imported, {fail} failed")

if __name__ == "__main__":
    main()
