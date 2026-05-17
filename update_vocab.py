#!/usr/bin/env python3
"""
Update vocab_data.json:
  - Replace `categories` with `pos` (part of speech) field
  - Year field already set from previous run
Run once to migrate existing data.
"""

import json, os, re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
VOCAB_JSON = os.path.join(SCRIPT_DIR, "vocab_data.json")

YEAR_MAP = [
    (1,   6,   2025),
    (7,   32,  2024),
    (33,  77,  2023),
    (78,  121, 2022),
    (122, 242, 2021),
    (243, 999, 2020),
]

def assign_year(entry_id):
    for lo, hi, yr in YEAR_MAP:
        if lo <= entry_id <= hi:
            return yr
    return 2020

# Particles that signal a phrasal verb
PARTICLES = {
    'up','out','down','in','on','off','away','over','through','back',
    'around','along','into','for','to','from','past','at','with','by',
    'about','aside','forward','apart','together','around'
}

def detect_pos(entry):
    word = entry['word'].strip()
    w = word.lower()
    tokens = w.split()

    # ── 1. Abbreviation ──────────────────────────────────────────────
    # All-caps words: MIA, FOMO, FWB, YOLO, POC
    if re.match(r'^[A-Z]{2,}(\s|$|\()', word):
        return 'abbreviation'
    # Known lowercase abbreviations
    known_abbrevs = {'et al', 'fwiw', 'yolo', 'mia', 'fwb', 'poc', 'a&b',
                     'capex', 'opex', 'cov', 'kpi', 'okr', 'uc', 'arr'}
    if w in known_abbrevs or w.rstrip('.') in known_abbrevs:
        return 'abbreviation'

    # ── 2. Explicit POS tags in word ─────────────────────────────────
    w_tag = w  # work on lowercase copy
    if re.search(r'\(adj\)', w_tag):  return 'adjective'
    if re.search(r'\(adv\)', w_tag):  return 'adverb'
    if re.search(r'\(n\b|\(noun\)', w_tag): return 'noun'
    if re.search(r'\(c\)|\(uc\)|\(non-c\)', w_tag): return 'noun'
    if re.search(r'\(v\b|\(verb\)', w_tag): return 'verb'

    # Strip parenthetical annotations before further analysis
    w_clean = re.sub(r'\([^)]*\)', '', w).strip()
    tokens_clean = w_clean.split()

    # ── 3. Has ST (something) or SO (someone) → verb / phrasal verb ──
    has_placeholder = bool(re.search(r'\b(ST|SO)\b', word))
    if has_placeholder:
        meaningful = [t for t in tokens_clean if t not in ('st','so','or','and','a','an','the','one\'s','your')]
        if any(t in PARTICLES for t in meaningful) and len(meaningful) > 1:
            return 'phrasal_verb'
        return 'verb'

    # ── 4. Multi-word without placeholder → expression ───────────────
    if len(tokens_clean) > 1:
        # But check if it's a verb form like "go viral", "go south"
        if tokens_clean[0] in ('go','get','make','take','give','put','set','come',
                                'run','turn','break','bring','hold','call','cut'):
            if any(t in PARTICLES for t in tokens_clean[1:]):
                return 'phrasal_verb'
        return 'expression'

    # ── 5. Single-word heuristics ─────────────────────────────────────
    w1 = w_clean

    # Adverb
    if re.search(r'ly$', w1) and len(w1) > 4:
        return 'adverb'

    # Verb suffixes
    if re.search(r'(ize|ise|ify|ate)$', w1) and len(w1) > 4:
        return 'verb'

    # Adjective suffixes
    if re.search(r'(ous|ful|ish|ical|ic|ive|able|ible|ent|ant|ary|some|ory|al)$', w1):
        # Exception: nouns ending in -al, -ent etc.
        nouns_ending_al = {'funeral','animal','canal','medal','renewal','signal'}
        if w1 not in nouns_ending_al:
            return 'adjective'

    # Default single word → noun
    return 'noun'


def main():
    with open(VOCAB_JSON, encoding='utf-8') as f:
        vocab = json.load(f)

    pos_counts = {}
    for entry in vocab:
        # Ensure year is set
        entry['year'] = entry.get('year') or assign_year(entry['id'])
        # Replace categories with pos
        entry.pop('categories', None)
        pos = detect_pos(entry)
        entry['pos'] = pos
        pos_counts[pos] = pos_counts.get(pos, 0) + 1

    with open(VOCAB_JSON, 'w', encoding='utf-8') as f:
        json.dump(vocab, f, ensure_ascii=False, indent=2)

    print(f"Updated {len(vocab)} entries — 'categories' → 'pos'")
    print("\nPOS distribution:")
    for pos, count in sorted(pos_counts.items(), key=lambda x: -x[1]):
        print(f"  {pos:20s}: {count}")


if __name__ == '__main__':
    main()
