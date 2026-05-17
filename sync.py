#!/usr/bin/env python3
"""
Sync script: processes queue.json, looks up definitions, updates vocab_data.json,
optionally syncs to Notion, and regenerates vocab.html.

Usage:
  python3 sync.py               # Process queue + regenerate HTML
  python3 sync.py --add "word"  # Add word to queue immediately and process
"""

import json
import os
import sys
import urllib.request
import urllib.parse
import subprocess
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
VOCAB_JSON = os.path.join(SCRIPT_DIR, "vocab_data.json")
RAW_DIR    = os.path.join(SCRIPT_DIR, "raw")
QUEUE_JSON = os.path.join(SCRIPT_DIR, "raw", "queue.json")
CONFIG_JSON = os.path.join(SCRIPT_DIR, "config.json")
GENERATE_PY = os.path.join(SCRIPT_DIR, "generate.py")


def load_json(path, default):
    if os.path.exists(path):
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    return default


def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


POS_MAP = {
    "noun": "noun", "verb": "verb", "adjective": "adjective",
    "adverb": "adverb", "abbreviation": "abbreviation",
    "pronoun": "noun", "conjunction": "expression",
    "preposition": "expression", "interjection": "expression",
}
PARTICLES = {'up','out','down','in','on','off','away','over','through','back',
             'around','along','into','for','to','from','past','at','with','by','about'}

def detect_pos_from_word(word):
    """Heuristic POS detection (fallback when API doesn't return one)."""
    import re
    w = word.lower().strip()
    tokens = w.split()
    if re.match(r'^[A-Z]{2,}', word): return 'abbreviation'
    has_placeholder = bool(re.search(r'\b(ST|SO)\b', word))
    if has_placeholder:
        meaningful = [t for t in tokens if t not in ('st','so','or','and','a','an','the')]
        if any(t in PARTICLES for t in meaningful) and len(meaningful) > 1:
            return 'phrasal_verb'
        return 'verb'
    if len(tokens) > 1: return 'expression'
    if re.search(r'ly$', w) and len(w) > 4: return 'adverb'
    if re.search(r'(ize|ise|ify|ate)$', w): return 'verb'
    if re.search(r'(ous|ful|ish|ical|ic|ive|able|ible|ent|ant|al)$', w): return 'adjective'
    return 'noun'

def lookup_dictionary(word):
    """Fetch English definition, example, and POS from Free Dictionary API."""
    base_word = word.split()[0].strip("()[]").lower()
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{urllib.parse.quote(base_word)}"
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            data = json.loads(r.read())
        if isinstance(data, list) and data:
            entry = data[0]
            meanings = entry.get('meanings', [])
            en_def, example, api_pos = "", "", ""
            for m in meanings:
                defs = m.get('definitions', [])
                if defs:
                    en_def = defs[0].get('definition', '')
                    example = defs[0].get('example', '')
                    api_pos = m.get('partOfSpeech', '')
                    if en_def:
                        break
            # Map API POS to our scheme, then check if phrasal verb
            pos = POS_MAP.get(api_pos, '') or detect_pos_from_word(word)
            if pos == 'verb' and len(word.split()) > 1:
                pos = 'phrasal_verb'
            return en_def, example, pos
    except Exception as e:
        print(f"  Dictionary API error for '{word}': {e}")
    return "", "", detect_pos_from_word(word)


def lookup_translation(text):
    """Get Japanese translation using MyMemory API."""
    if not text:
        return ""
    params = urllib.parse.urlencode({'q': text, 'langpair': 'en|ja'})
    url = f"https://api.mymemory.translated.net/get?{params}"
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            data = json.loads(r.read())
        return data.get('responseData', {}).get('translatedText', '')
    except Exception as e:
        print(f"  Translation API error: {e}")
    return ""


def next_id(vocab):
    return max((v['id'] for v in vocab), default=0) + 1


def is_duplicate(word, vocab):
    word_lower = word.lower().strip()
    return any(v['word'].lower().strip() == word_lower for v in vocab)


def process_queue():
    vocab = load_json(VOCAB_JSON, [])
    queue = load_json(QUEUE_JSON, {"entries": []})
    entries = queue.get("entries", [])

    if not entries:
        print("Queue is empty.")
        return vocab, False

    new_entries = []
    changed = False

    for item in entries:
        word = item.get("word", "").strip()
        if not word:
            continue

        if is_duplicate(word, vocab):
            print(f"  Skipping duplicate: '{word}'")
            continue

        print(f"  Processing: '{word}'")
        en_def, en_example, pos = lookup_dictionary(word)

        # Auto-translate English definition to Japanese
        meaning_ja = ""
        if en_def:
            meaning_ja = lookup_translation(en_def)

        # Use dictionary example
        example = en_example

        from datetime import date as _date
        now = datetime.now()
        year = _date.today().year

        entry = {
            "id": next_id(vocab),
            "word": word,
            "meaning_ja": meaning_ja,
            "english_def": en_def,
            "example": example,
            "notes": item.get("notes", ""),
            "date_added": item.get("date_added", f"{now.month}/{now.day}"),
            "year": year,
            "pos": pos,
            "mastery": "new"
        }
        vocab.append(entry)
        new_entries.append(entry)
        changed = True
        print(f"    ✓ Added: {word} — {meaning_ja[:40] if meaning_ja else '(no meaning)'}")

    # Clear processed queue
    save_json(QUEUE_JSON, {"entries": []})

    if changed:
        save_json(VOCAB_JSON, vocab)
        print(f"\nSaved {len(new_entries)} new entries. Total: {len(vocab)}")

    return vocab, changed


def sync_to_notion(entry, config):
    """Sync a single entry to Notion (requires token and db_id in config.json)."""
    token = config.get("notion_token", "")
    db_id = config.get("notion_db_id", "")
    if not token or not db_id:
        return False
    try:
        payload = json.dumps({
            "parent": {"database_id": db_id},
            "properties": {
                "Word": {"title": [{"text": {"content": entry["word"]}}]},
                "Meaning (JA)": {"rich_text": [{"text": {"content": entry["meaning_ja"]}}]},
                "Definition (EN)": {"rich_text": [{"text": {"content": entry["english_def"]}}]},
                "Example": {"rich_text": [{"text": {"content": entry["example"]}}]},
                "Notes": {"rich_text": [{"text": {"content": entry["notes"]}}]},
                "Mastery": {"select": {"name": entry["mastery"]}},
                "Date Added": {"date": {"start": datetime.now().strftime("%Y-%m-%d")}}
            }
        }).encode()
        req = urllib.request.Request(
            "https://api.notion.com/v1/pages",
            data=payload,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "Notion-Version": "2022-06-28"
            },
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status == 200
    except Exception as e:
        print(f"  Notion sync error: {e}")
    return False


def add_to_queue(word, notes="", meaning_ja=""):
    """Add a word to the offline queue."""
    queue = load_json(QUEUE_JSON, {"entries": []})
    queue["entries"].append({
        "word": word,
        "meaning_ja": meaning_ja,
        "notes": notes,
        "date_added": datetime.now().strftime("%m/%d")
    })
    save_json(QUEUE_JSON, queue)
    print(f"Added '{word}' to queue.")


def regenerate_html():
    """Regenerate vocab.html."""
    result = subprocess.run([sys.executable, GENERATE_PY], capture_output=True, text=True)
    if result.returncode == 0:
        print(result.stdout.strip())
    else:
        print(f"HTML generation failed: {result.stderr}")


def main():
    args = sys.argv[1:]

    if '--add' in args:
        idx = args.index('--add')
        word = args[idx + 1] if idx + 1 < len(args) else ""
        notes = args[idx + 2] if idx + 2 < len(args) else ""
        if word:
            add_to_queue(word, notes)

    print("Processing queue...")
    vocab, changed = process_queue()

    # Optional Notion sync for newly added entries
    if changed:
        config = load_json(CONFIG_JSON, {})
        if config.get("notion_token") and config.get("notion_db_id"):
            print("Syncing to Notion...")
            for entry in vocab[-10:]:  # Sync recent entries
                sync_to_notion(entry, config)

    print("Regenerating HTML...")
    regenerate_html()
    print("Done.")


if __name__ == '__main__':
    main()
