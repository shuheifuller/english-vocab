---
tags: [architecture, technical]
created: 2026-05-17
---

# アーキテクチャ — データフローと構成

→ [[_Overview]] に戻る

---

## データフロー

```
【ソース】                  【処理】                   【出力】
────────────────────────────────────────────────────────────
Google Sheets          →  parse_raw_data.py       →  vocab_data.json
raw/queue.json         →  sync.py                 →  vocab_data.json
                              ↓                          ↓
                       辞書API検索                  generate.py
                       (Free Dict / UD /                  ↓
                        Wikipedia / DDG)           vocab.html (PWA)
                              ↓                          ↓
                       MyMemory翻訳            GitHub Pages (公開)
```

### 携帯からの追加フロー（GitHub Actions）
```
携帯ブラウザ
  → vocab.html の「追加」タブ
  → GitHub API dispatch (PAT認証)
  → .github/workflows/add-word.yml
  → ubuntu-latest runner
      → raw/queue.json 書き込み
      → sync.py 実行
      → generate.py 実行
      → git commit & push
  → GitHub Pages 自動更新（~2分）
```

---

## ファイル間の依存関係

### データ依存
- [[raw/sheets_import]] → `parse_raw_data.py` → [[vocab_data]]
- [[raw/queue]] → [[sync]] → [[vocab_data]]
- [[vocab_data]] → [[generate]] → `vocab.html`

### スクリプト依存
- [[sync]] は [[generate]] を subprocess で呼び出す
- [[update_vocab]] は [[vocab_data]] を直接更新する
- [[build_wiki]] は [[vocab_data]] から `wiki/` を生成する

### 設定依存
- `config.json` → [[generate]]（google_client_id, authorized_email）
- `config.json` → [[sync]]（notion_token, notion_db_id）

---

## 辞書検索の優先順位

| 優先度 | ソース | 適している単語 |
|--------|--------|----------------|
| 1 | Free Dictionary API | 標準的な英単語 |
| 2 | Urban Dictionary | スラング・造語・略語 |
| 3 | Wikipedia | 固有名詞・専門用語 |
| 4 | DuckDuckGo | 上記で見つからない場合 |

> フレーズ・イディオム（複数単語）はUrban Dictionaryを優先

---

## PWA構成

```
vocab.html         ← メインアプリ（self-contained）
manifest.json      ← PWAマニフェスト（ホーム画面追加用）
sw.js              ← Service Worker（vocab.htmlをネットワーク優先でキャッシュ）
```

---

## Notion連携（オプション）

`config.json` に `notion_token` を設定すると [[sync]] が Notion DB にも書き込む。  
DB ID: `a7f9fe05-ee04-42f0-bbc7-6990db0963f6`  
→ [[bulk_import_notion]] で一括インポート可能
