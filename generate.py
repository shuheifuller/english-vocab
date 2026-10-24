#!/usr/bin/env python3
"""Generate vocab.html (PWA) from vocab_data.json + app_template.html.

Run after any data update. Edit app_template.html for UI changes —
never edit vocab.html directly.
"""

import json, os

SCRIPT_DIR    = os.path.dirname(os.path.abspath(__file__))
VOCAB_JSON    = os.path.join(SCRIPT_DIR, "vocab_data.json")
TEMPLATE_HTML = os.path.join(SCRIPT_DIR, "app_template.html")
OUTPUT_HTML   = os.path.join(SCRIPT_DIR, "vocab.html")


def generate(vocab):
    with open(TEMPLATE_HTML, encoding="utf-8") as f:
        template = f.read()
    # "</" would end the <script> block early if a word ever contained it
    data = json.dumps(vocab, ensure_ascii=False).replace("</", "<\\/")
    assert template.count("__VOCAB__") == 1, "template must contain exactly one __VOCAB__"
    return template.replace("__VOCAB__", data)


def main():
    with open(VOCAB_JSON, encoding="utf-8") as f:
        vocab = json.load(f)
    html = generate(vocab)
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Generated {OUTPUT_HTML} ({len(vocab)} entries)")


if __name__ == "__main__":
    main()
