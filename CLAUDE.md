# English Vocabulary Wiki — Schema

## About This Project

Shuhei's personal English vocabulary knowledge base. He works in a professional setting in Australia (previously at AWS), encounters English daily, and records words/expressions he doesn't know. The goal is to build a compounding, interconnected knowledge base — not just a flat word list.

**Key principle**: This wiki grows richer with every session. Cross-references, themes, and synthesis are built up over time by Claude. Shuhei sources the words; Claude does the maintenance.

---

## Directory Structure

```
English Vocabulary List/
├── CLAUDE.md               ← You are here (schema)
├── raw/
│   ├── sheets_import.md    # Original Google Sheets data (immutable)
│   └── queue.json          # Words pending processing
├── wiki/
│   ├── index.md            # Master catalog of all words (search starting point)
│   ├── log.md              # Append-only activity log
│   └── themes/             # Thematic groupings with analysis
│       ├── business.md
│       ├── idioms.md
│       ├── aussie-slang.md
│       ├── medical.md
│       ├── legal-political.md
│       ├── social.md
│       └── similar-words.md
├── vocab_data.json         # Flat JSON for PWA (auto-generated from wiki)
├── generate.py             # Generates vocab.html from vocab_data.json
├── sync.py                 # Processes queue, calls dictionary APIs, updates wiki
├── vocab.html              # PWA flashcard app (generated — do not edit directly)
├── manifest.json
└── sw.js
```

---

## Your Workflows

### 1. Add a New Word (Ingest)

When Shuhei says something like _"add 'reconcile' to my vocab"_ or _"reconcileってNotionに追加して"_:

1. **Check for duplicates** — search `wiki/index.md` for the word before adding
2. **Look up definition** — call Free Dictionary API for single words; use your own knowledge for phrases/idioms
3. **Update `vocab_data.json`** — append new entry with `id`, `word`, `meaning_ja`, `english_def`, `example`, `notes`, `date_added`, `mastery: "new"`
4. **Update `wiki/index.md`** — add the word to the catalog under the appropriate category
5. **Update relevant theme page** — add/mention the word in `wiki/themes/*.md` with context
6. **Cross-reference** — note any related words already in the wiki (synonyms, antonyms, same context)
7. **Append to `wiki/log.md`** — one line: `## [YYYY-MM-DD] ingest | Word — brief note`
8. **Regenerate HTML** — run `python3 generate.py`

### 2. Query the Wiki

When Shuhei asks questions about his vocabulary:

1. Read `wiki/index.md` first for orientation
2. Drill into relevant theme pages or search `vocab_data.json`
3. Synthesize answers with citations to specific entries
4. **File valuable answers back** — if the answer is a useful comparison or insight, add it to the appropriate theme page or create a new `wiki/themes/` page

### 3. Sync Queue (Process Pending Words)

When Shuhei adds words to `raw/queue.json` while offline:
- Run: `python3 sync.py`
- This calls Free Dictionary API + MyMemory translation API, updates `vocab_data.json`, and regenerates `vocab.html`
- After sync, manually update `wiki/index.md` and relevant theme pages

### 4. Lint (Health Check)

Periodically run a health check on the wiki. Look for:
- Words in `vocab_data.json` with empty `meaning_ja` or `english_def`
- Words mentioned in themes but not in `vocab_data.json` (or vice versa)
- Themes that haven't been updated recently (check `wiki/log.md`)
- Related words that could be cross-referenced but aren't
- Gaps: important concepts mentioned in examples but not their own entry

---

## vocab_data.json Schema

Each entry:
```json
{
  "id": 1,
  "word": "reconcile",
  "meaning_ja": "和解する、調整する、折り合いをつける",
  "english_def": "to restore friendly relations between; to make consistent or compatible",
  "example": "It's hard to reconcile these two opposing views.",
  "notes": "Often used in business: 'reconcile the data', 'reconcile differences'",
  "date_added": "5/17",
  "mastery": "new"
}
```

`mastery` values: `new` | `learning` | `mastered`

---

## wiki/index.md Format

The index is the LLM's primary navigation tool. Format:

```markdown
# Vocabulary Index
Last updated: YYYY-MM-DD | Total: NNN words

## Business & Professional
- **reconcile** — 和解する、調整する → [themes/business.md]
- **overarching** — 包括的な → [themes/business.md]

## Idioms & Expressions
- **no brainer** — 当たり前、考える必要がない → [themes/idioms.md]
...
```

---

## wiki/log.md Format

Append-only. Most recent entries at the bottom.

```markdown
## [2026-05-17] init | Imported 411 words from Google Sheets
## [2026-05-17] ingest | reconcile — business context, added to themes/business.md
## [2026-05-20] lint | Found 38 words with empty english_def, queued for API lookup
```

---

## Theme Page Format

```markdown
# [Theme Name]
Last updated: YYYY-MM-DD | N words

## Overview
Brief description of this theme and why these words matter to Shuhei.

## Words
| Word | Meaning (JA) | Context / Notes |
|------|-------------|-----------------|
| overarching | 包括的な | "an overarching statement" — used in professional settings |

## Related Themes
- → [business.md] for formal professional expressions
- → [similar-words.md] for easily confused pairs

## Insights
Patterns, common mistakes, or interesting observations Claude has noticed.
```

---

## Context About Shuhei

- Lives in Australia; many words come from work/news/daily life there
- Previously worked at AWS (many business/tech expressions)
- Learning English as a second language (native Japanese speaker)
- Words span casual, professional, medical, political, and Aussie-specific contexts
- The Google Sheets spanned multiple years — earlier entries tend to have less context

---

## Important Rules

1. **Never modify `raw/` files** — they are the immutable source of truth
2. **Never edit `vocab.html` directly** — always edit data/scripts then regenerate
3. **Always append to `wiki/log.md`** — never rewrite history
4. **Check for duplicates before adding** — the same word appears multiple times in the source data (e.g., "caveat" appears twice, "in light of" appears twice)
5. **Preserve existing `mastery` values** when updating entries — don't reset progress
6. **When in doubt about a phrase's meaning, use your own knowledge** — the Free Dictionary API only handles single words well
