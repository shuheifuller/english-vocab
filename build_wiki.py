#!/usr/bin/env python3
"""
Build initial wiki/ structure from vocab_data.json.
Run once to initialize. Claude maintains wiki/ after that.
"""

import json
import os
from datetime import date

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
VOCAB_JSON = os.path.join(SCRIPT_DIR, "vocab_data.json")
WIKI_DIR = os.path.join(SCRIPT_DIR, "wiki")
THEMES_DIR = os.path.join(WIKI_DIR, "themes")

TODAY = date.today().isoformat()

# ── Categorization rules ──────────────────────────────────────────────────────
# Keywords in word or meaning_ja that suggest a theme
THEME_RULES = {
    "business": [
        "leverage", "overarching", "cadence", "bandwidth", "synergy", "stakeholder",
        "deliverable", "escalate", "align", "runway", "pipeline", "bottleneck",
        "upskill", "bandwidth", "proactive", "actionable", "pivot", "kpi",
        "headcount", "onboard", "offboard", "iterate", "agile", "scrum",
        "roadmap", "milestone", "backlog", "sprint", "velocity", "dwell",
        "housekeeping", "repurpose", "surface", "double down", "elevator pitch",
        "bread and butter", "no brainer", "low hanging fruit", "boil the ocean",
        "redundant", "remuneration", "proposition", "catalyst", "run rate",
        "overhead", "upfront", "cadence", "rapport", "go south", "templatize",
        "factor in", "hold accountable", "gamechanger", "paradigm", "synergy",
        "leverage", "visibility", "bandwidth", "deliverable", "scalable",
        "champion", "circl", "loop", "sync", "align", "deep dive",
        "in a nutshell", "flesh out", "drill down", "take offline",
        "suboptimal", "sub-optimal", "arbitrarily", "consolidate",
        "runrate", "headcount", "metric", "kpi", "okr",
    ],
    "idioms": [
        "in a nutshell", "no brainer", "bread and butter", "low hanging fruit",
        "cut to the chase", "at the end of the day", "bite the bullet",
        "hit the ground running", "think outside the box", "go south",
        "in retrospect", "for god's sake", "by all means", "so be it",
        "point taken", "tell me about it", "you said it", "so much so",
        "not to mention", "just because", "off the top of my head",
        "goes by in a blink", "blink of an eye", "devil's in the details",
        "speak of the devil", "break a leg", "my hats off", "not my cup of tea",
        "have a bun in the oven", "over the moon", "monday blues",
        "double edged sword", "a matter of time", "in good hands",
        "get around to", "going once", "give benefit of the doubt",
        "fall on someone's sword", "for what it's worth", "fwiw",
        "yet another", "two cents", "my 2 cents", "nitty-gritty",
        "flesh out", "piggy back", "add up", "juice is worth",
        "cannot see the forest", "lost in translation", "if the juice",
        "up to speed", "bring up to speed", "run past", "talk through",
    ],
    "aussie-slang": [
        "brolly", "down under", "go walkabout", "she'll be right",
        "un-australian", "suss", "arvo", "reckon", "heaps", "mate",
        "no worries", "strewth", "fair dinkum", "crikey",
        "twag", "nasal", "parkrun", "footpath", "kerb",
    ],
    "medical": [
        "cardiac arrest", "respiratory", "asymptomatic", "hypertension",
        "resuscitate", "tuberculosis", "leukaemia", "pediatric",
        "cruciate ligament", "nasal congestion", "bronchitis",
        "conjunctivitis", "schizophrenia", "autism", "cerebral palsy",
        "acupuncture", "vasectomy", "fertility", "contraception",
        "syphilis", "nearsighted", "farsighted", "inhale", "exhale",
        "complications", "rabies", "asthma", "mortality", "pathology",
        "resuscitate", "anemia", "pelvis", "vaccine", "pandemic",
        "ventilator", "droplet", "viral", "fatality", "acute", "chronic",
    ],
    "legal-political": [
        "jurisdiction", "insurrection", "incitement", "legislation",
        "subpoena", "acquitted", "manslaughter", "disciplinary",
        "voluntary administration", "sovereignty", "coalition",
        "inauguration", "antisemitism", "xenophobia", "misogyny",
        "monarchy", "anarchy", "relinquish", "cause of action",
        "human trafficking", "solidarity", "puberty", "discriminat",
        "disenfranchise", "delegitimize", "punitive", "ultimatum",
        "pyramid scheme", "defy", "exercise one's right", "silent treatment",
    ],
    "social": [
        "rapport", "solidarity", "amicable", "animosity", "resentment",
        "bystander", "social butterfly", "sycophant", "trailblazer",
        "misogyny", "xenophobia", "patriarchy", "equity", "equality",
        "diversity", "inclusion", "belonging", "microaggression",
        "prejudice", "bias", "empathy", "apathy", "complacency",
        "retaliation", "misconduct", "demean", "intimidate",
        "gaffe", "faux pas", "cringe", "obnoxious", "blunt",
        "indifferent", "exasperate", "concur", "dissuade", "persuade",
    ],
}

def categorize(entry):
    """Return a list of theme keys this entry belongs to."""
    w = entry["word"].lower()
    m = (entry.get("meaning_ja") or "").lower()
    matched = []
    for theme, keywords in THEME_RULES.items():
        for kw in keywords:
            if kw in w or kw in m:
                matched.append(theme)
                break
    return matched if matched else ["general"]


def build_index(vocab):
    themes_map = {}
    for entry in vocab:
        for theme in categorize(entry):
            themes_map.setdefault(theme, []).append(entry)

    theme_labels = {
        "business": "ビジネス・職場",
        "idioms": "イディオム・慣用句",
        "aussie-slang": "オーストラリア英語",
        "medical": "医療・健康",
        "legal-political": "法律・政治",
        "social": "社会・人間関係",
        "general": "その他",
    }

    lines = [
        f"# Vocabulary Index",
        f"Last updated: {TODAY} | Total: {len(vocab)} words",
        "",
        "> This file is Claude's primary navigation tool. Search here first, then drill into theme pages.",
        "",
    ]

    for theme in ["business", "idioms", "aussie-slang", "medical", "legal-political", "social", "general"]:
        entries = themes_map.get(theme, [])
        if not entries:
            continue
        label = theme_labels.get(theme, theme)
        lines.append(f"## {label} ({len(entries)} words)")
        for e in sorted(entries, key=lambda x: x["word"].lower()):
            meaning = e.get("meaning_ja") or ""
            if len(meaning) > 50:
                meaning = meaning[:50] + "…"
            lines.append(f"- **{e['word']}** (id:{e['id']}) — {meaning}")
        lines.append("")

    return "\n".join(lines)


def build_theme_page(theme_key, entries, label):
    lines = [
        f"# {label}",
        f"Last updated: {TODAY} | {len(entries)} words",
        "",
        "## Words",
        "",
        "| Word | 意味 | 例文 |",
        "|------|------|------|",
    ]
    for e in sorted(entries, key=lambda x: x["word"].lower()):
        word = e["word"].replace("|", "/")
        meaning = (e.get("meaning_ja") or "").replace("|", "/")[:60]
        example = (e.get("example") or "").replace("|", "/")[:60]
        if len(e.get("meaning_ja") or "") > 60:
            meaning += "…"
        if len(e.get("example") or "") > 60:
            example += "…"
        lines.append(f"| {word} | {meaning} | {example} |")
    lines.append("")
    lines.append("## Insights")
    lines.append("")
    lines.append("_Claude will add cross-references, patterns, and observations here over time._")
    lines.append("")
    return "\n".join(lines)


def build_similar_words():
    """Seed page for easily confused word pairs."""
    content = f"""# Similar & Easily Confused Words
Last updated: {TODAY}

> Cross-references between words that are close in meaning but differ in nuance, formality, or context.
> Claude will expand this page as patterns emerge.

## Formality Ladder
| Casual | Neutral | Formal |
|--------|---------|--------|
| on purpose | intentionally | deliberately |
| smart | astute | perspicacious |
| stubborn | resolute | intransigent |

## Near-Synonyms with Nuance Differences
| Word A | Word B | Difference |
|--------|--------|------------|
| resentment | grudge | grudge is stronger / more long-lasting |
| arbitrary | random | arbitrary implies a decision-maker; random implies chance |
| intrinsic | extrinsic | intrinsic = from within; extrinsic = from outside |
| equity | equality | equity = fair outcome; equality = same treatment |
| tangible | concrete | tangible = can be touched; concrete = definite/specific |

## False Friends / Easy Mistakes
_Claude will add entries here as they come up in conversation._

"""
    return content


def build_log():
    return f"""# Activity Log

> Append-only. Each line: `## [DATE] action | description`
> Parse recent entries: `grep "^## " log.md | tail -10`

## [{TODAY}] init | Imported 411 words from Google Sheets via parse_raw_data.py
## [{TODAY}] init | Built wiki structure: index.md, log.md, themes/ from build_wiki.py
"""


def main():
    with open(VOCAB_JSON, encoding="utf-8") as f:
        vocab = json.load(f)

    os.makedirs(THEMES_DIR, exist_ok=True)

    # Categorize all entries
    themes_map = {}
    for entry in vocab:
        for theme in categorize(entry):
            themes_map.setdefault(theme, []).append(entry)

    theme_labels = {
        "business": "ビジネス・職場表現",
        "idioms": "イディオム・慣用句",
        "aussie-slang": "オーストラリア英語スラング",
        "medical": "医療・健康",
        "legal-political": "法律・政治",
        "social": "社会・人間関係",
        "general": "その他・一般",
    }

    # wiki/index.md
    index_path = os.path.join(WIKI_DIR, "index.md")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(build_index(vocab))
    print(f"✓ {index_path}")

    # wiki/log.md
    log_path = os.path.join(WIKI_DIR, "log.md")
    with open(log_path, "w", encoding="utf-8") as f:
        f.write(build_log())
    print(f"✓ {log_path}")

    # wiki/themes/*.md
    for theme, label in theme_labels.items():
        entries = themes_map.get(theme, [])
        path = os.path.join(THEMES_DIR, f"{theme}.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(build_theme_page(theme, entries, label))
        print(f"✓ {path} ({len(entries)} entries)")

    # wiki/themes/similar-words.md
    sw_path = os.path.join(THEMES_DIR, "similar-words.md")
    with open(sw_path, "w", encoding="utf-8") as f:
        f.write(build_similar_words())
    print(f"✓ {sw_path}")

    # raw/ directory
    raw_dir = os.path.join(SCRIPT_DIR, "raw")
    os.makedirs(raw_dir, exist_ok=True)

    # Move queue.json to raw/ if it exists at root
    root_queue = os.path.join(SCRIPT_DIR, "queue.json")
    raw_queue = os.path.join(raw_dir, "queue.json")
    if os.path.exists(root_queue) and not os.path.exists(raw_queue):
        import shutil
        shutil.copy(root_queue, raw_queue)
        print(f"✓ Copied queue.json → raw/queue.json")

    # Create raw/sheets_import.md placeholder
    sheets_md = os.path.join(raw_dir, "sheets_import.md")
    if not os.path.exists(sheets_md):
        with open(sheets_md, "w", encoding="utf-8") as f:
            f.write(f"""# Google Sheets Import
Source: https://docs.google.com/spreadsheets/d/12e153hyp3ZDLdbdCSY6hwJUUy1fIE4Fd664GTko9jZc
Imported: {TODAY}
Entries: {len(vocab)}

> Raw source data. Do not modify. See vocab_data.json for processed data.
""")
        print(f"✓ {sheets_md}")

    print(f"\nWiki built. Total words categorized:")
    for theme, label in theme_labels.items():
        n = len(themes_map.get(theme, []))
        print(f"  {label}: {n}")


if __name__ == "__main__":
    main()
