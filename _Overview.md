---
tags: [overview, hub]
created: 2026-05-17
---

# Shuhei's EN Vocab App — Project Overview

英語単語帳PWAの全体構成をまとめたハブノード。

## 🌐 ライブアプリ
**URL**: https://shuheifuller.github.io/english-vocab/vocab.html
**Repo**: https://github.com/shuheifuller/english-vocab

---

## 📁 プロジェクト構成

### コアファイル
- [[vocab.html]] — メインのPWA（フラッシュカード・単語帳・統計）
- [[vocab_data]] — 全単語データ（JSON、412件）
- [[CLAUDE]] — ClaudeへのスキーマとAI操作手順

### スクリプト
- [[sync]] — キュー処理・辞書検索・HTML再生成
- [[generate]] — vocab_dataからvocab.htmlを生成
- [[update_vocab]] — 品詞(POS)・年の自動付与
- [[build_wiki]] — wikiディレクトリの初期構築

### データ
- [[raw/sheets_import]] — Google Sheetsの元データ（不変）
- [[raw/queue]] — 追加待ちキュー

### ナレッジベース
- [[wiki/index]] — 全412単語のカタログ
- [[wiki/log]] — 活動ログ（append-only）
- [[wiki/themes/business]] — ビジネス・職場表現
- [[wiki/themes/idioms]] — イディオム・慣用句
- [[wiki/themes/aussie-slang]] — オーストラリア英語
- [[wiki/themes/medical]] — 医療・健康
- [[wiki/themes/legal-political]] — 法律・政治
- [[wiki/themes/social]] — 社会・人間関係
- [[wiki/themes/similar-words]] — 混同しやすい単語

---

## 🔄 システム構成

→ [[_Architecture]] でデータフローの詳細を確認

---

## 📖 使い方

→ [[_How_to_Use]] でワークフローの詳細を確認

---

## 📊 現在の状態

| 項目 | 内容 |
|------|------|
| 総単語数 | 412件 |
| 期間 | 2020〜2026年 |
| ホスティング | GitHub Pages |
| 認証 | Google SSO (shoeheyu@gmail.com) |
| 辞書ソース | Free Dictionary / Urban Dictionary / Wikipedia / DuckDuckGo |
