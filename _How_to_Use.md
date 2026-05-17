---
tags: [guide, workflow]
created: 2026-05-17
---

# 使い方ガイド

→ [[_Overview]] に戻る

---

## 単語を追加する方法

### 方法①：Claudeに話しかける（推奨）

```
「reconcileをvocabに追加して」
```

Claudeが自動で：
1. 辞書検索（Free Dict → Urban Dict → Wikipedia → DuckDuckGo）
2. 品詞（POS）を判定
3. 英語定義を日本語翻訳
4. [[vocab_data]] に追加
5. `vocab.html` を再生成
6. `git push` でGitHub Pages更新

### 方法②：携帯のアプリから追加（GitHub Actions）

1. https://shuheifuller.github.io/english-vocab/vocab.html を開く
2. 「追加」タブに単語を入力
3. 「追加する →」をタップ
4. 約1〜2分後に自動でページが更新される

> 事前に「統計タブ → クラウド設定」でGitHub PATを設定する必要あり

### 方法③：ローカルで手動追加

```bash
# raw/queue.json に追記して sync.py を実行
python3 sync.py --add "serendipity"
```

---

## HTMLを更新する

[[vocab_data]] を変更後：

```bash
python3 generate.py   # vocab.html を再生成
git add vocab.html vocab_data.json
git commit -m "Update vocab"
git push              # GitHub Pages に自動反映
```

---

## 単語を削除する

[[vocab_data]] を直接編集して該当エントリを削除し、`generate.py` を実行。

---

## ローカルで開発・確認する

```bash
./launch.sh   # http://localhost:8080 でHTTPサーバー起動
```

> Google SSOは `file://` では動かない。必ず `./launch.sh` 経由で確認する。

---

## Obsidian でナレッジを管理する

| ファイル | 役割 |
|---------|------|
| [[_Overview]] | 全体のハブ（ここから始める） |
| [[_Architecture]] | 技術的な構成・データフロー |
| [[wiki/index]] | 全412単語のカタログ |
| [[wiki/log]] | 追加・変更の記録 |
| [[wiki/themes/business]] | ビジネス系単語 |
| [[wiki/themes/idioms]] | イディオム |
| [[CLAUDE]] | ClaudeへのAI操作手順 |
