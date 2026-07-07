#!/usr/bin/env python3
"""Generate vocab.html (PWA) from vocab_data.json. Run after any data update."""

import json, os

SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
VOCAB_JSON  = os.path.join(SCRIPT_DIR, "vocab_data.json")
CONFIG_JSON = os.path.join(SCRIPT_DIR, "config.json")
OUTPUT_HTML = os.path.join(SCRIPT_DIR, "vocab.html")

def get_config():
    try:
        with open(CONFIG_JSON) as f: return json.load(f)
    except: return {}

def generate(vocab, cfg):
    vj      = json.dumps(vocab, ensure_ascii=False)
    total   = len(vocab)
    years   = sorted({v.get("year", 2020) for v in vocab}, reverse=True)
    yrs_js  = json.dumps(years)
    gh_repo = cfg.get("github_repo", "shuheifuller/english-vocab")

    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="theme-color" content="#0f0f1a">
<title>英語単語帳</title>
<link rel="manifest" href="manifest.json">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<link rel="icon" type="image/png" href="icon-192.png">
<meta name="apple-mobile-web-app-title" content="単語帳">
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0;-webkit-tap-highlight-color:transparent}}
:root{{
  --bg:#0f0f1a;--sf:#1a1a2e;--sf2:#16213e;
  --ac:#e94560;--tx:#eaeaea;--tx2:#8892b0;--bd:#2a2a4a;
  --gn:#4ade80;--yw:#fbbf24;--pu:#a78bfa;
  --r:16px;--st:env(safe-area-inset-top);--sb:env(safe-area-inset-bottom);
}}
@media(prefers-color-scheme:light){{
  :root{{--bg:#f0f2f8;--sf:#fff;--sf2:#e8ebf5;--tx:#1a1a2e;--tx2:#5a6080;--bd:#d0d5e8;}}
}}
html,body{{height:100%;overflow:hidden;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',system-ui,sans-serif;background:var(--bg);color:var(--tx)}}
#app{{display:flex;flex-direction:column;height:100%;padding-top:var(--st)}}

/* ── NAV ──────────────────────────────────────── */
#nav{{display:flex;background:var(--sf);border-top:1px solid var(--bd);padding-bottom:var(--sb);flex-shrink:0;order:2}}
.nb{{flex:1;display:flex;flex-direction:column;align-items:center;gap:3px;padding:10px 2px 8px;border:none;background:none;color:var(--tx2);font-size:9px;cursor:pointer;transition:color .2s;position:relative;font-family:inherit}}
.nb.active{{color:var(--ac)}}
.nb svg{{width:22px;height:22px;flex-shrink:0}}
.badge{{position:absolute;top:6px;right:calc(50% - 18px);background:var(--ac);color:#fff;font-size:9px;font-weight:800;padding:1px 5px;border-radius:10px;display:none}}

/* ── VIEWS ────────────────────────────────────── */
#content{{flex:1;overflow:hidden;position:relative;order:1}}
.view{{position:absolute;inset:0;overflow-y:auto;display:none;flex-direction:column}}
.view.active{{display:flex}}
.vh{{padding:14px 16px 10px;display:flex;align-items:flex-start;justify-content:space-between;flex-shrink:0;gap:10px}}
.vtitle{{font-size:18px;font-weight:800}}
.vsub{{font-size:11px;color:var(--tx2);margin-top:2px}}

/* ── FILTER CHIPS ─────────────────────────────── */
.fbar{{display:flex;gap:6px;padding:0 16px 8px;overflow-x:auto;flex-shrink:0;-webkit-overflow-scrolling:touch}}
.fbar::-webkit-scrollbar{{display:none}}
.chip{{padding:6px 14px;border-radius:20px;border:1px solid var(--bd);background:none;color:var(--tx2);font-size:12px;font-weight:600;cursor:pointer;white-space:nowrap;font-family:inherit;transition:all .15s;flex-shrink:0}}
.chip.active{{background:var(--ac);color:#fff;border-color:var(--ac)}}
.chip.pn.active{{background:#3b82f6;border-color:#3b82f6}}
.chip.pv.active{{background:#22c55e;border-color:#22c55e}}
.chip.ppv.active{{background:#10b981;border-color:#10b981}}
.chip.pa.active{{background:#f97316;border-color:#f97316}}
.chip.pad.active{{background:#a855f7;border-color:#a855f7}}
.chip.pe.active{{background:#e94560;border-color:#e94560}}
.chip.pab.active{{background:#6b7280;border-color:#6b7280}}

/* ── ADD ──────────────────────────────────────── */
#va{{padding-bottom:20px}}
.fsec{{padding:0 16px 14px}}
.flbl{{font-size:12px;color:var(--tx2);text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;font-weight:700;display:block}}
.fi{{width:100%;background:var(--sf);border:1px solid var(--bd);border-radius:10px;padding:12px 14px;font-size:15px;color:var(--tx);font-family:inherit;outline:none;transition:border-color .2s}}
.fi:focus{{border-color:var(--ac)}}
.fi::placeholder{{color:var(--tx2)}}
textarea.fi{{min-height:80px;resize:vertical;line-height:1.5}}
.subbtn{{width:100%;background:var(--ac);color:#fff;border:none;border-radius:12px;padding:16px;font-size:16px;font-weight:700;cursor:pointer;font-family:inherit}}
.subbtn:active{{opacity:.8}}
.psec{{background:var(--sf);border-radius:12px;border:1px solid var(--bd);overflow:hidden}}
.pi{{display:flex;align-items:center;justify-content:space-between;padding:12px 14px;border-bottom:1px solid var(--bd);gap:8px}}
.pi:last-child{{border-bottom:none}}
.piw{{font-size:14px;font-weight:700}}
.pdel{{background:none;border:none;color:var(--ac);cursor:pointer;font-size:16px;padding:4px}}
.expbtn{{width:100%;background:var(--sf2);color:var(--tx);border:1px solid var(--bd);border-radius:12px;padding:14px;font-size:14px;font-weight:700;cursor:pointer;font-family:inherit}}
.empty{{text-align:center;padding:28px;color:var(--tx2);font-size:14px}}
.divider{{height:1px;background:var(--bd);margin:0 16px 16px}}

/* ── REVIEW ───────────────────────────────────── */
#vr{{align-items:center;justify-content:center;padding:14px 16px 10px}}
.pw{{width:100%;max-width:400px;margin-bottom:12px;flex-shrink:0}}
.pb2{{height:4px;background:var(--bd);border-radius:2px;overflow:hidden}}
.pf{{height:100%;background:var(--ac);transition:width .3s}}
.pl{{display:flex;justify-content:space-between;font-size:11px;color:var(--tx2);margin-top:5px}}
.cw{{flex:1;width:100%;max-width:400px;perspective:1000px;cursor:pointer;min-height:0}}
.card{{width:100%;height:100%;position:relative;transform-style:preserve-3d;transition:transform .45s cubic-bezier(.4,0,.2,1)}}
.card.flip{{transform:rotateY(180deg)}}
.cf{{position:absolute;inset:0;backface-visibility:hidden;-webkit-backface-visibility:hidden;background:var(--sf);border-radius:var(--r);padding:24px 20px;display:flex;flex-direction:column;border:1px solid var(--bd);box-shadow:0 8px 32px rgba(0,0,0,.2)}}
.cb{{transform:rotateY(180deg)}}
.clbl{{font-size:10px;color:var(--tx2);text-transform:uppercase;letter-spacing:1px;margin-bottom:10px;font-weight:700}}
.cb .clbl{{color:var(--ac)}}
.cword{{font-size:clamp(20px,5vw,30px);font-weight:800;line-height:1.2;flex:1;display:flex;align-items:center}}
.chint{{font-size:12px;color:var(--tx2);text-align:center;margin-top:auto}}
.cmeta{{display:flex;gap:6px;margin-bottom:10px;flex-wrap:wrap}}
.ctag{{font-size:10px;padding:2px 8px;border-radius:10px;font-weight:700;background:var(--sf2);color:var(--tx2)}}
.cmja{{font-size:clamp(15px,3.5vw,19px);font-weight:700;margin-bottom:10px;line-height:1.4}}
.cmen{{font-size:12px;color:var(--tx2);margin-bottom:12px;line-height:1.6;font-style:italic}}
.cex{{background:var(--sf2);border-radius:10px;padding:10px 12px;margin-bottom:auto}}
.cexl{{font-size:9px;color:var(--ac);text-transform:uppercase;letter-spacing:1px;margin-bottom:5px;font-weight:800}}
.cext{{font-size:12px;line-height:1.6}}
.cnote{{font-size:11px;color:var(--tx2);margin-top:6px;line-height:1.5;font-style:italic}}
.ca{{display:flex;gap:8px;width:100%;max-width:400px;flex-shrink:0;margin-top:10px}}
.ab{{flex:1;padding:12px 8px;border-radius:12px;border:none;font-size:13px;font-weight:700;cursor:pointer;transition:all .15s;font-family:inherit}}
.again{{background:rgba(233,69,96,.15);color:var(--ac)}}
.good{{background:rgba(74,222,128,.15);color:var(--gn)}}
.again:active{{background:rgba(233,69,96,.3)}}
.good:active{{background:rgba(74,222,128,.3)}}
.arr{{display:flex;gap:10px;width:100%;max-width:400px;justify-content:center;margin-top:6px;flex-shrink:0}}
.arb{{background:var(--sf2);border:1px solid var(--bd);color:var(--tx2);width:44px;height:44px;border-radius:50%;display:flex;align-items:center;justify-content:center;cursor:pointer;font-size:18px}}
.arb:active{{background:var(--bd)}}
.arb.spk{{font-size:20px}}
.arb.spk.speaking{{background:var(--ac);border-color:var(--ac);color:#fff}}
.sh{{font-size:10px;color:var(--tx2);text-align:center;margin-top:4px;flex-shrink:0}}

/* ── WORDS ────────────────────────────────────── */
#vw .vh{{flex-direction:column;align-items:stretch;gap:8px}}
.srow{{display:flex;gap:8px;align-items:center}}
.sbox{{flex:1;background:var(--sf);border:1px solid var(--bd);border-radius:10px;padding:10px 14px;font-size:15px;color:var(--tx);font-family:inherit;outline:none}}
.sbox::placeholder{{color:var(--tx2)}}
.sbtn{{background:var(--sf);border:1px solid var(--bd);border-radius:10px;padding:10px 12px;font-size:12px;color:var(--tx2);cursor:pointer;font-family:inherit;white-space:nowrap}}
.wl{{flex:1;overflow-y:auto;padding:0 16px 8px}}
.wi{{background:var(--sf);border-radius:12px;padding:12px 14px;margin-bottom:8px;border:1px solid var(--bd)}}
.wit{{display:flex;align-items:flex-start;justify-content:space-between;gap:8px}}
.wiw{{font-size:15px;font-weight:700;flex:1;line-height:1.3}}
.wib{{display:flex;flex-direction:column;align-items:flex-end;gap:3px;flex-shrink:0}}
.mb{{font-size:9px;padding:2px 7px;border-radius:10px;font-weight:700}}
.db{{font-size:9px;color:var(--tx2);font-weight:600}}
.mn{{background:rgba(167,139,250,.15);color:var(--pu)}}
.ml{{background:rgba(251,191,36,.15);color:var(--yw)}}
.mm{{background:rgba(74,222,128,.15);color:var(--gn)}}
.wim{{font-size:12px;color:var(--tx2);margin-top:5px;line-height:1.5}}
.wie{{font-size:11px;color:var(--tx2);margin-top:3px;font-style:italic;line-height:1.4}}
.ptag{{display:inline-block;font-size:9px;padding:2px 7px;border-radius:6px;font-weight:700;margin-top:4px;background:var(--sf2);color:var(--tx2)}}
.win{{font-size:11px;color:var(--tx2);margin-top:6px;line-height:1.5;border-left:2px solid var(--pu);padding-left:8px}}
.winl{{display:inline-block;font-size:9px;font-weight:700;color:var(--pu);margin-right:6px;text-transform:uppercase;letter-spacing:.04em}}
.wirow{{display:flex;align-items:center;justify-content:space-between;margin-top:6px}}
.wedit{{font-size:10px;font-weight:700;color:var(--tx2);background:var(--sf2);border:1px solid var(--bd);border-radius:8px;padding:3px 10px;cursor:pointer}}
.wedit:active{{opacity:.6}}
.wspk{{background:none;border:none;color:var(--tx2);cursor:pointer;font-size:14px;padding:0 4px;line-height:1;flex-shrink:0;opacity:.65}}
.wspk:active{{opacity:1;color:var(--ac)}}
.trunc-note{{text-align:center;padding:12px;color:var(--tx2);font-size:12px}}

/* ── EDIT MODAL ───────────────────────────────── */
.modal{{position:fixed;inset:0;z-index:200;display:none;align-items:flex-end;justify-content:center;background:rgba(0,0,0,.55);padding-bottom:0}}
.modal.show{{display:flex}}
.modal-card{{width:100%;max-width:560px;background:var(--sf);border-top-left-radius:20px;border-top-right-radius:20px;border:1px solid var(--bd);padding:18px 16px calc(20px + var(--sb));max-height:90%;overflow-y:auto}}
.modal-h{{display:flex;align-items:center;justify-content:space-between;margin-bottom:14px}}
.modal-t{{font-size:16px;font-weight:800}}
.modal-w{{font-size:13px;color:var(--ac);font-weight:700}}
.modal-x{{font-size:22px;line-height:1;color:var(--tx2);background:none;border:none;cursor:pointer;padding:4px}}
.efld{{margin-bottom:14px}}
.elbl{{display:block;font-size:11px;font-weight:700;color:var(--tx2);margin-bottom:6px}}
.eti{{width:100%;background:var(--bg);color:var(--tx);border:1px solid var(--bd);border-radius:10px;padding:10px 12px;font-size:14px;font-family:inherit;line-height:1.5;resize:vertical;min-height:46px}}
.eti:focus{{outline:none;border-color:var(--ac)}}
.ebtns{{display:flex;gap:10px;margin-top:6px}}
.ebtn{{flex:1;padding:12px;border-radius:12px;font-size:14px;font-weight:700;border:none;cursor:pointer}}
.ebtn.save{{background:var(--ac);color:#fff}}
.ebtn.cancel{{background:var(--sf2);color:var(--tx2)}}
.ebtn:disabled{{opacity:.5}}
.emsg{{font-size:12px;margin-top:10px;line-height:1.5}}

/* ── STATS ────────────────────────────────────── */
#vst{{padding-bottom:40px}}
.ssec{{padding:0 16px 20px}}
.stitle{{font-size:11px;color:var(--tx2);text-transform:uppercase;letter-spacing:1px;margin-bottom:12px;font-weight:700}}
.guide-card{{background:var(--sf);border-radius:14px;border:1px solid var(--bd);overflow:hidden}}
.guide-item{{display:flex;gap:14px;padding:14px 16px;border-bottom:1px solid var(--bd);align-items:flex-start}}
.guide-item:last-child{{border-bottom:none}}
.guide-icon{{font-size:24px;flex-shrink:0;margin-top:2px}}
.guide-title{{font-size:14px;font-weight:700;margin-bottom:4px}}
.guide-body{{font-size:12px;color:var(--tx2);line-height:1.6}}
.guide-code{{font-family:monospace;background:var(--sf2);border-radius:6px;padding:2px 6px;font-size:11px;color:var(--ac)}}
.chart-scroll{{overflow-x:auto;-webkit-overflow-scrolling:touch}}
.chart-scroll::-webkit-scrollbar{{display:none}}
#trend-svg{{display:block}}
.donut-wrap{{display:flex;align-items:center;gap:20px;padding:4px 0 16px}}
.donut-legend{{display:flex;flex-direction:column;gap:8px;flex:1}}
.dl{{display:flex;align-items:center;gap:8px;font-size:13px}}
.dldot{{width:10px;height:10px;border-radius:50%;flex-shrink:0}}
.dlnum{{font-weight:700;margin-left:auto}}
.yt{{width:100%;border-collapse:collapse;font-size:12px}}
.yt th{{text-align:left;color:var(--tx2);font-weight:600;padding:6px 8px 10px;font-size:11px;border-bottom:1px solid var(--bd)}}
.yt td{{padding:8px;border-bottom:1px solid var(--bd);vertical-align:middle}}
.yt tr:last-child td{{border-bottom:none}}
.yt .yn{{font-weight:700}}
.prog-seg{{height:8px;border-radius:4px;overflow:hidden;background:var(--bd);display:flex;margin-top:4px}}
.seg-m{{background:var(--gn)}}.seg-l{{background:var(--yw)}}.seg-n{{background:var(--pu)}}
.sc{{background:var(--sf);border-radius:12px;overflow:hidden;border:1px solid var(--bd)}}
.sr{{display:flex;align-items:center;padding:13px 16px;border-bottom:1px solid var(--bd);gap:10px;cursor:pointer}}
.sr:last-child{{border-bottom:none}}
.srt{{flex:1}}
.srl{{font-size:14px;font-weight:500}}
.srs{{font-size:11px;color:var(--tx2);margin-top:2px}}
.srv{{font-size:13px;color:var(--ac);font-weight:700;flex-shrink:0}}
.sbtn2{{background:var(--ac);color:#fff;border:none;border-radius:8px;padding:7px 14px;font-size:13px;font-weight:700;cursor:pointer;font-family:inherit}}
.ssel{{background:var(--sf2);color:var(--tx);border:1px solid var(--bd);border-radius:8px;padding:7px 10px;font-size:13px;font-family:inherit;outline:none}}
.user-badge{{background:var(--sf);border:1px solid var(--bd);border-radius:24px;padding:6px 14px 6px 8px;display:flex;align-items:center;gap:8px;font-size:13px;font-weight:600}}
.user-av{{width:28px;height:28px;border-radius:50%;background:var(--ac);display:flex;align-items:center;justify-content:center;color:#fff;font-size:14px;font-weight:800;flex-shrink:0}}
</style>
</head>
<body>

<!-- ═══════════ APP ════════════════════════════════ -->
<div id="app">
<div id="content">

<!-- ADD (first / default view) -->
<div id="va" class="view active">
  <div class="vh"><div><div class="vtitle">単語を追加</div><div class="vsub">意味・発音・品詞は自動で調べます</div></div></div>

  <div style="margin:0 16px 12px;background:rgba(167,139,250,.1);border:1px solid var(--pu);border-radius:10px;padding:10px 14px;font-size:12px;color:var(--pu);line-height:1.6">
    💡 「追加」を押すと確認ページが開きます。<b>緑の保存ボタン</b>を押すだけで、数分後に単語が登録されます。
  </div>

  <div class="fsec">
    <label class="flbl">単語 / 表現 *</label>
    <input class="fi" id="aw" placeholder="例: reconcile, in a nutshell" autocorrect="off" autocapitalize="none">
  </div>
  <div class="fsec">
    <label class="flbl">メモ（任意）</label>
    <textarea class="fi" id="an" placeholder="どこで出会った？気になった点など…"></textarea>
  </div>
  <div class="fsec">
    <button class="subbtn" id="add-submit-btn" onclick="addW()">追加する →</button>
  </div>

  <!-- Add status -->
  <div id="dispatch-status" style="display:none;margin:0 16px 14px;text-align:center">
    <div id="dispatch-msg" style="font-size:13px;color:var(--tx2)"></div>
    <div style="font-size:11px;color:var(--tx2);margin-top:6px">数分後に自動で反映されます</div>
  </div>

  <div class="divider"></div>

  <!-- Pending (saved while offline) -->
  <div class="fsec" id="local-queue-section">
    <div class="stitle">追加待ち（<span id="qcnt">0</span>件）</div>
    <div id="qempty" class="empty">追加待ちの単語はありません</div>
    <div class="psec" id="plist" style="display:none"></div>
    <div id="pending-hint" class="empty" style="display:none;font-size:12px;padding:12px 4px 0;text-align:left;line-height:1.6">
      オフライン中に保存した単語です。オンラインに戻ったら各単語の<b>「追加」</b>を押すと登録されます。
    </div>
  </div>
</div>

<!-- REVIEW -->
<div id="vr" class="view">
  <div class="pw">
    <div class="pb2"><div class="pf" id="pf" style="width:0%"></div></div>
    <div class="pl"><span id="pt">{total}件</span><span id="sess">✓0 ↺0</span><span id="pfl">全て</span></div>
  </div>
  <div class="cw" id="cw">
    <div class="card" id="card">
      <div class="cf">
        <div class="clbl">英語</div>
        <div class="cword" id="cword">-</div>
        <div class="chint">タップでめくる</div>
      </div>
      <div class="cf cb">
        <div class="clbl">意味</div>
        <div class="cmeta" id="cmeta"></div>
        <div class="cmja" id="cmja"></div>
        <div class="cmen" id="cmen"></div>
        <div class="cex" id="cex">
          <div class="cexl">例文</div>
          <div class="cext" id="cext"></div>
          <div class="cnote" id="cnote"></div>
        </div>
      </div>
    </div>
  </div>
  <div class="ca" id="ca" style="display:none">
    <button class="ab again" onclick="mark(false)">もう一度 ↺</button>
    <button class="ab good" onclick="mark(true)">わかった！ ✓</button>
  </div>
  <div class="arr">
    <button class="arb" onclick="nav(-1)">←</button>
    <button class="arb spk" id="spk-btn" onclick="speakCurrent()" title="発音を聞く">🔊</button>
    <button class="arb" onclick="nav(1)">→</button>
  </div>
  <div class="sh">タップ / Space でめくる ・ ←→ で移動 ・ 🔊 or S で発音 ・ 1/2 で判定</div>
</div>

<!-- WORDS -->
<div id="vw" class="view">
  <div class="vh">
    <div><div class="vtitle">単語一覧</div><div class="vsub" id="wcount">{total}件</div></div>
    <div class="srow" style="width:100%">
      <input class="sbox" placeholder="検索…" oninput="setSrch(this.value)">
      <button class="sbtn" onclick="togSort()" id="sortbtn">新→旧</button>
    </div>
  </div>
  <div class="fbar" id="ybar">
    <button class="chip active" onclick="setY('all',this)">全年</button>
    {''.join(f'<button class="chip" onclick="setY({y},this)">{y}</button>' for y in years)}
  </div>
  <div class="fbar" id="pbar">
    <button class="chip active" onclick="setP('all',this)">全品詞</button>
    <button class="chip pn" onclick="setP('noun',this)">名詞</button>
    <button class="chip pv" onclick="setP('verb',this)">動詞</button>
    <button class="chip ppv" onclick="setP('phrasal_verb',this)">句動詞</button>
    <button class="chip pa" onclick="setP('adjective',this)">形容詞</button>
    <button class="chip pad" onclick="setP('adverb',this)">副詞</button>
    <button class="chip pe" onclick="setP('expression',this)">表現</button>
    <button class="chip pab" onclick="setP('abbreviation',this)">略語</button>
  </div>
  <div class="fbar">
    <button class="chip active" onclick="setM('all',this)">全習熟度</button>
    <button class="chip" onclick="setM('new',this)">未学習</button>
    <button class="chip" onclick="setM('learning',this)">学習中</button>
    <button class="chip" onclick="setM('mastered',this)">習得済み</button>
  </div>
  <div class="wl" id="wl"></div>
</div>

<!-- STATS -->
<div id="vst" class="view">
  <div class="vh">
    <div><div class="vtitle">統計・設定</div></div>
  </div>

  <div class="ssec">
    <div class="stitle">📖 使い方</div>
    <div class="guide-card">
      <div class="guide-item">
        <div class="guide-icon">➕</div>
        <div>
          <div class="guide-title">「追加」タブから登録</div>
          <div class="guide-body">単語を入力して「追加」を押し、開いた確認ページで<b>緑の保存ボタン</b>を押すだけ。意味・発音・品詞・日本語訳は自動で調べます。</div>
        </div>
      </div>
      <div class="guide-item">
        <div class="guide-icon">🃏</div>
        <div>
          <div class="guide-title">フラッシュカードで復習</div>
          <div class="guide-body">タップでめくる / スワイプで次へ / 「わかった！」で習熟度が上がります。</div>
        </div>
      </div>
    </div>
  </div>

  <div class="ssec">
    <div class="stitle">📈 単語追加トレンド（年別）</div>
    <div class="chart-scroll"><svg id="trend-svg" height="180"></svg></div>
  </div>

  <div class="ssec">
    <div class="stitle">📊 現在の習熟度</div>
    <div class="donut-wrap">
      <svg id="donut-svg" width="110" height="110" viewBox="-1 -1 2 2" style="flex-shrink:0"></svg>
      <div class="donut-legend" id="donut-legend"></div>
    </div>
  </div>

  <div class="ssec">
    <div class="stitle">📅 年別習熟度</div>
    <table class="yt" id="yt"></table>
  </div>

  <div class="ssec">
    <div class="stitle">⚙️ 復習フィルター</div>
    <div class="sc">
      <div class="sr" onclick="setRF('all')"><div class="srt"><div class="srl">すべての単語</div></div><div class="srv" id="rf-all">✓</div></div>
      <div class="sr" onclick="setRF('new')"><div class="srt"><div class="srl">未学習のみ</div></div><div class="srv" id="rf-new"></div></div>
      <div class="sr" onclick="setRF('learning')"><div class="srt"><div class="srl">学習中のみ</div></div><div class="srv" id="rf-learning"></div></div>
      <div class="sr" onclick="setRF('mastered')"><div class="srt"><div class="srl">習得済みのみ</div></div><div class="srv" id="rf-mastered"></div></div>
    </div>
  </div>

  <div class="ssec">
    <div class="stitle">⚙️ 操作</div>
    <div class="sc">
      <div class="sr"><div class="srt"><div class="srl">カードをシャッフル</div></div><button class="sbtn2" onclick="shuf()">シャッフル</button></div>
      <div class="sr"><div class="srt"><div class="srl">進捗をリセット</div><div class="srs">全単語を未学習に戻す</div></div><button class="sbtn2" style="background:var(--tx2)" onclick="resetP()">リセット</button></div>
    </div>
  </div>
</div>

</div><!-- /content -->

<nav id="nav">
  <button class="nb active" data-v="va" onclick="sw('va',this)" id="add-nb">
    <div class="badge" id="add-badge">0</div>
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="16"/><line x1="8" y1="12" x2="16" y2="12"/></svg>追加
  </button>
  <button class="nb" data-v="vr" onclick="sw('vr',this)">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="3" width="20" height="18" rx="3"/><path d="M8 10h8M8 14h5"/></svg>復習
  </button>
  <button class="nb" data-v="vw" onclick="sw('vw',this)">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/></svg>単語帳
  </button>
  <button class="nb" data-v="vst" onclick="sw('vst',this)">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>統計
  </button>
</nav>

<!-- Edit word modal -->
<div class="modal" id="edit-modal">
  <div class="modal-card">
    <div class="modal-h">
      <div>
        <div class="modal-t">編集</div>
        <div class="modal-w" id="ed-word"></div>
      </div>
      <button class="modal-x" onclick="closeEdit()">×</button>
    </div>
    <div class="efld">
      <label class="elbl">意味（日本語）</label>
      <textarea class="eti" id="ed-meaning" rows="2"></textarea>
    </div>
    <div class="efld">
      <label class="elbl">例文</label>
      <textarea class="eti" id="ed-example" rows="3"></textarea>
    </div>
    <div class="efld">
      <label class="elbl">メモ / Note</label>
      <textarea class="eti" id="ed-notes" rows="2"></textarea>
    </div>
    <div class="ebtns">
      <button class="ebtn cancel" onclick="closeEdit()">キャンセル</button>
      <button class="ebtn save" id="ed-save-btn" onclick="saveEdit()">保存する →</button>
    </div>
    <div class="emsg" id="ed-msg" style="display:none"></div>
  </div>
</div>
</div><!-- /app -->

<script>
const VOCAB = {vj};
const ALL_YEARS  = {yrs_js};
const GH_REPO    = '{gh_repo}';
const POS_L = {{noun:'名詞',verb:'動詞',phrasal_verb:'句動詞',adjective:'形容詞',adverb:'副詞',expression:'表現',abbreviation:'略語'}};

// ── PRONUNCIATION (Web Speech API) ─────────────
let enVoice = null;
function pickVoice() {{
  if (!('speechSynthesis' in window)) return;
  const vs = speechSynthesis.getVoices();
  enVoice = vs.find(v => /en[-_]US/i.test(v.lang) && /Samantha|Google US|Natural/i.test(v.name))
        || vs.find(v => /en[-_]US/i.test(v.lang))
        || vs.find(v => /^en/i.test(v.lang)) || null;
}}
if ('speechSynthesis' in window) {{
  pickVoice();
  speechSynthesis.onvoiceschanged = pickVoice;
}}
function speak(text, btn) {{
  if (!text || !('speechSynthesis' in window)) return;
  try {{
    speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(text);
    u.lang = 'en-US'; u.rate = 0.92;
    if (enVoice) u.voice = enVoice;
    if (btn) {{
      btn.classList.add('speaking');
      u.onend = u.onerror = () => btn.classList.remove('speaking');
    }}
    speechSynthesis.speak(u);
  }} catch(e) {{}}
}}
function speakCurrent() {{ if (deck.length) speak(deck[idx].word, document.getElementById('spk-btn')); }}
function speakId(id) {{ const c = VOCAB.find(v => v.id === id); if (c) speak(c.word); }}

// ── STATE ──────────────────────────────────────
let prog = {{}}, st = {{revFilter: 'all'}};
let deck = [], idx = 0, flipped = false;
let wf = {{year: 'all', pos: 'all', mastery: 'all', search: '', sortNew: true}};
let pq = [];
let sess = {{good: 0, again: 0}};
const MASTERY_RANK = {{new: 0, learning: 1, mastered: 2}};

function loadSt() {{
  try {{ prog = JSON.parse(localStorage.getItem('vp') || '{{}}'); }} catch(e) {{}}
  try {{
    const s = JSON.parse(localStorage.getItem('vs') || '{{}}');
    st = {{...st, ...s}};
  }} catch(e) {{}}
  try {{ pq = JSON.parse(localStorage.getItem('vq') || '[]'); }} catch(e) {{}}
}}
function savP() {{ localStorage.setItem('vp', JSON.stringify(prog)); }}
function savSt(k, v) {{ st[k] = v; localStorage.setItem('vs', JSON.stringify(st)); }}
function savQ() {{ localStorage.setItem('vq', JSON.stringify(pq)); updQUI(); }}
function gm(c) {{ return prog[c.id] || c.mastery || 'new'; }}

// ── REVIEW ─────────────────────────────────────
function buildDeck() {{
  const rf = st.revFilter || 'all';
  deck = rf === 'all' ? [...VOCAB] : VOCAB.filter(c => gm(c) === rf);
  // Smart order: study unmastered words first (stable within each tier)
  deck = deck
    .map((c, i) => [c, i])
    .sort((a, b) => (MASTERY_RANK[gm(a[0])] - MASTERY_RANK[gm(b[0])]) || (a[1] - b[1]))
    .map(p => p[0]);
  idx = 0;
  document.getElementById('pfl').textContent =
    {{all:'全て', new:'未学習', learning:'学習中', mastered:'習得済み'}}[rf] || '全て';
  showC();
}}
function updSess() {{
  const el = document.getElementById('sess');
  if (el) el.textContent = `✓${{sess.good}} ↺${{sess.again}}`;
}}
function showC() {{
  if (flipped) {{ flipped = false; document.getElementById('card').classList.remove('flip'); }}
  document.getElementById('ca').style.display = 'none';
  const t = deck.length;
  if (!t) {{ document.getElementById('cword').textContent = '該当なし'; document.getElementById('pt').textContent = '0件'; return; }}
  const c = deck[idx];
  document.getElementById('cword').textContent = c.word;
  document.getElementById('cmja').textContent = c.meaning_ja || '（意味未登録）';
  document.getElementById('cmen').textContent = c.english_def || '';
  const ex = c.example || '', nt = c.notes || '';
  document.getElementById('cext').textContent = ex;
  document.getElementById('cnote').textContent = nt;
  document.getElementById('cex').style.display = (ex || nt) ? '' : 'none';
  const posL = POS_L[c.pos] || c.pos || '';
  document.getElementById('cmeta').innerHTML =
    (c.year ? `<span class="ctag">${{c.year}}</span>` : '') +
    (posL   ? `<span class="ctag">${{posL}}</span>`   : '');
  document.getElementById('pt').textContent = `${{idx + 1}} / ${{t}}`;
  document.getElementById('pf').style.width = `${{(idx / Math.max(1, t - 1)) * 100}}%`;
}}
function flipC() {{
  flipped = !flipped;
  document.getElementById('card').classList.toggle('flip', flipped);
  document.getElementById('ca').style.display = flipped ? 'flex' : 'none';
}}
function nav(d) {{
  if (!deck.length) return;
  idx = (idx + d + deck.length) % deck.length;
  showC();
}}
function mark(good) {{
  if (!deck.length) return;
  const c = deck[idx], cur = gm(c);
  prog[c.id] = good
    ? (cur === 'new' ? 'learning' : 'mastered')
    : (cur === 'mastered' ? 'learning' : 'new');
  savP();
  if (good) sess.good++; else sess.again++;
  updSess();
  if (navigator.vibrate) navigator.vibrate(good ? 14 : [8, 40, 8]);
  nav(1);
}}
function shuf() {{
  for (let i = deck.length - 1; i > 0; i--) {{
    const j = Math.floor(Math.random() * (i + 1));
    [deck[i], deck[j]] = [deck[j], deck[i]];
  }}
  idx = 0; showC();
}}

// Touch / Swipe
let tx = 0, ty = 0, tt = 0;
document.getElementById('cw').addEventListener('touchstart', e => {{
  tx = e.touches[0].clientX; ty = e.touches[0].clientY; tt = Date.now();
}}, {{passive: true}});
document.getElementById('cw').addEventListener('touchend', e => {{
  const dx = e.changedTouches[0].clientX - tx;
  const dy = e.changedTouches[0].clientY - ty;
  const dt = Date.now() - tt;
  if (Math.abs(dx) > Math.abs(dy) && Math.abs(dx) > 50) nav(dx < 0 ? 1 : -1);
  else if (Math.abs(dx) < 12 && Math.abs(dy) < 12 && dt < 300) flipC();
}}, {{passive: true}});
document.getElementById('card').addEventListener('click', flipC);

// Keyboard shortcuts (desktop) — active only in the Review view
document.addEventListener('keydown', e => {{
  if (!document.getElementById('vr').classList.contains('active')) return;
  const t = e.target.tagName;
  if (t === 'INPUT' || t === 'TEXTAREA' || e.metaKey || e.ctrlKey || e.altKey) return;
  const k = e.key;
  if (k === 'ArrowLeft') {{ nav(-1); }}
  else if (k === 'ArrowRight') {{ nav(1); }}
  else if (k === ' ' || k === 'Enter' || k === 'ArrowUp' || k === 'ArrowDown') {{ e.preventDefault(); flipC(); }}
  else if (k === '1') {{ if (flipped) mark(false); }}
  else if (k === '2') {{ if (flipped) mark(true); }}
  else if (k === 's' || k === 'S') {{ speakCurrent(); }}
  else return;
}});

// ── WORDS ──────────────────────────────────────
function filt() {{
  let l = VOCAB;
  if (wf.year !== 'all')    l = l.filter(c => c.year === parseInt(wf.year));
  if (wf.pos !== 'all')     l = l.filter(c => c.pos === wf.pos);
  if (wf.mastery !== 'all') l = l.filter(c => gm(c) === wf.mastery);
  if (wf.search) {{
    const q = wf.search.toLowerCase();
    l = l.filter(c =>
      c.word.toLowerCase().includes(q) ||
      (c.meaning_ja || '').includes(q) ||
      (c.example || '').toLowerCase().includes(q) ||
      (c.notes || '').toLowerCase().includes(q));
  }}
  return wf.sortNew ? [...l].reverse() : l;
}}
function renW() {{
  const l = filt();
  document.getElementById('wcount').textContent = `${{l.length}}件`;
  const el = document.getElementById('wl');
  if (!l.length) {{ el.innerHTML = '<div class="empty">該当する単語がありません</div>'; return; }}
  const LIMIT = 300;
  const trunc = l.length > LIMIT;
  el.innerHTML = l.slice(0, LIMIT).map(c => {{
    const m = gm(c);
    const ml = {{new:'未学習', learning:'学習中', mastered:'習得済み'}}[m];
    const mo = parseInt((c.date_added || '').split('/')[0]) || '';
    const dl = c.year ? (c.year + (mo ? '/' + mo : '')) : '';
    const pl = POS_L[c.pos] || c.pos || '';
    return `<div class="wi">
      <div class="wit">
        <div class="wiw">${{esc(c.word)}} <button class="wspk" onclick="speakId(${{c.id}})" title="発音を聞く">🔊</button></div>
        <div class="wib">
          <span class="mb m${{m[0]}}">${{ml}}</span>
          ${{dl ? `<span class="db">${{dl}}</span>` : ''}}
        </div>
      </div>
      ${{c.meaning_ja ? `<div class="wim">${{esc(c.meaning_ja)}}</div>` : ''}}
      ${{c.example    ? `<div class="wie">${{esc(c.example)}}</div>`    : ''}}
      ${{c.notes      ? `<div class="win"><span class="winl">Note</span>${{esc(c.notes)}}</div>` : ''}}
      <div class="wirow">
        ${{pl ? `<span class="ptag">${{pl}}</span>` : '<span></span>'}}
        <button class="wedit" onclick="openEdit(${{c.id}})">✎ 編集</button>
      </div>
    </div>`;
  }}).join('') + (trunc ? `<div class="trunc-note">上位 ${{LIMIT}} 件を表示中（全 ${{l.length}} 件）。検索やフィルターで絞り込めます。</div>` : '');
}}
function setSrch(v) {{ wf.search = v; renW(); }}
function setY(v, b) {{ wf.year = v;    chp('ybar', b); renW(); }}
function setP(v, b) {{ wf.pos = v;     chp('pbar', b); renW(); }}
function setM(v, b) {{ wf.mastery = v; chp(b.parentElement, b); renW(); }}
function togSort() {{
  wf.sortNew = !wf.sortNew;
  document.getElementById('sortbtn').textContent = wf.sortNew ? '新→旧' : '旧→新';
  renW();
}}
function chp(p, b) {{
  const el = typeof p === 'string' ? document.getElementById(p) : p;
  if (el) el.querySelectorAll('.chip').forEach(x => x.classList.remove('active'));
  b.classList.add('active');
}}

// ── EDIT WORD ──────────────────────────────────
let editingId = null;
function openEdit(id) {{
  const c = VOCAB.find(v => v.id === id);
  if (!c) return;
  editingId = id;
  document.getElementById('ed-word').textContent = c.word;
  document.getElementById('ed-meaning').value = c.meaning_ja || '';
  document.getElementById('ed-example').value = c.example || '';
  document.getElementById('ed-notes').value   = c.notes || '';
  document.getElementById('ed-msg').style.display = 'none';
  document.getElementById('edit-modal').classList.add('show');
}}
function closeEdit() {{
  document.getElementById('edit-modal').classList.remove('show');
  editingId = null;
}}
// Tap on the dark backdrop closes the modal
document.getElementById('edit-modal').addEventListener('click', e => {{
  if (e.target.id === 'edit-modal') closeEdit();
}});
async function saveEdit() {{
  if (editingId == null) return;
  const meaning_ja = document.getElementById('ed-meaning').value.trim();
  const example    = document.getElementById('ed-example').value.trim();
  const notes      = document.getElementById('ed-notes').value.trim();
  const c = VOCAB.find(v => v.id === editingId);
  const body = `<!--vocab:meaning_ja-->\n${{meaning_ja}}\n<!--vocab:example-->\n${{example}}\n<!--vocab:notes-->\n${{notes}}`;
  const url = `https://github.com/${{GH_REPO}}/issues/new` +
    `?title=${{encodeURIComponent(`[vocab-edit] id=${{editingId}} ${{c ? c.word : ''}}`)}}` +
    `&body=${{encodeURIComponent(body)}}`;
  window.open(url, '_blank');
  // Show the change straight away while it saves in the background
  if (c) {{ c.meaning_ja = meaning_ja; c.example = example; c.notes = notes; }}
  renW();
  if (deck.length && deck[idx] && deck[idx].id === editingId) showC();
  const msg = document.getElementById('ed-msg');
  msg.innerHTML = '✅ 確認ページが開きました。<b>緑の保存ボタン</b>を押すと保存されます。<br>数分後に自動で反映されます。';
  msg.style.color = 'var(--gn)';
  msg.style.display = '';
  setTimeout(() => closeEdit(), 2400);
  setTimeout(() => location.reload(), 150000);
}}

// ── ADD WORD ───────────────────────────────────
async function addW() {{
  const w = document.getElementById('aw').value.trim();
  if (!w) {{ alert('単語を入力してください'); return; }}
  const notes = document.getElementById('an').value.trim();

  if (navigator.onLine === false) {{
    // Offline: keep it safe until you're back online
    const now = new Date();
    pq.push({{word: w, notes, date_added: `${{now.getMonth()+1}}/${{now.getDate()}}`}});
    savQ();
    document.getElementById('aw').value = '';
    document.getElementById('an').value = '';
    alert(`✓ オフラインのため "${{w}}" を追加待ちに保存しました`);
  }} else {{
    openAddIssue(w, notes);
  }}
}}

function openAddIssue(word, notes) {{
  const url = `https://github.com/${{GH_REPO}}/issues/new` +
    `?title=${{encodeURIComponent('[vocab-add] ' + word)}}` +
    `&body=${{encodeURIComponent(notes || '')}}`;
  window.open(url, '_blank');
  document.getElementById('aw').value = '';
  document.getElementById('an').value = '';
  const statusEl = document.getElementById('dispatch-status');
  const msgEl = document.getElementById('dispatch-msg');
  msgEl.innerHTML = `✅ 確認ページが開きました。<b>緑の保存ボタン</b>を押すと<br><b>${{esc(word)}}</b> が登録されます（数分後に反映）`;
  msgEl.style.color = 'var(--gn)';
  statusEl.style.display = '';
  setTimeout(() => {{ msgEl.textContent = '最新の状態を確認中…'; location.reload(); }}, 150000);
}}

function remQ(i) {{ pq.splice(i, 1); savQ(); }}
function submitPending(i) {{
  const q = pq[i];
  if (!q) return;
  pq.splice(i, 1); savQ();
  openAddIssue(q.word, q.notes || '');
}}
function updQUI() {{
  const n = pq.length;
  document.getElementById('qcnt').textContent = n;
  const b = document.getElementById('add-badge');
  b.textContent = n; b.style.display = n ? '' : 'none';
  document.getElementById('qempty').style.display = n ? 'none' : '';
  const pl = document.getElementById('plist');
  pl.style.display = n ? '' : 'none';
  const hint = document.getElementById('pending-hint');
  if (hint) hint.style.display = n ? '' : 'none';
  pl.innerHTML = pq.map((q, i) => `
    <div class="pi">
      <div>
        <div class="piw">${{esc(q.word)}}</div>
        ${{q.notes ? `<div style="font-size:12px;color:var(--tx2)">${{esc(q.notes)}}</div>` : ''}}
      </div>
      <div style="display:flex;align-items:center;gap:8px;flex-shrink:0">
        <button class="sbtn2" style="padding:6px 13px;font-size:12px" onclick="submitPending(${{i}})">追加</button>
        <button class="pdel" onclick="remQ(${{i}})">✕</button>
      </div>
    </div>`).join('');
}}

// ── STATS CHARTS ───────────────────────────────
function renderTrend() {{
  const yg = {{}};
  VOCAB.forEach(v => {{ const y = v.year || 2020; yg[y] = (yg[y] || 0) + 1; }});
  const ys = ALL_YEARS.slice().reverse();
  const max = Math.max(...Object.values(yg), 1);
  const W = 60, PAD = 10, H = 160, BOTTOM = 30;
  const barH = H - BOTTOM - 20 - PAD;
  const svgW = ys.length * W + PAD * 2;
  let out = `<line x1="${{PAD}}" y1="${{H - BOTTOM}}" x2="${{svgW - PAD}}" y2="${{H - BOTTOM}}" stroke="var(--bd)" stroke-width="1"/>`;
  ys.forEach((y, i) => {{
    const cnt = yg[y] || 0;
    const bh  = Math.round((cnt / max) * barH);
    const x   = PAD + i * W + 8, bw = W - 16;
    const by  = H - BOTTOM - bh;
    out += `<rect x="${{x}}" y="${{by}}" width="${{bw}}" height="${{bh}}" rx="6" fill="var(--ac)" opacity="${{0.45 + 0.55 * (cnt / max)}}"/>`;
    out += `<text x="${{x + bw / 2}}" y="${{by - 5}}" text-anchor="middle" font-size="11" font-weight="700" fill="var(--tx)">${{cnt}}</text>`;
    out += `<text x="${{x + bw / 2}}" y="${{H - BOTTOM + 14}}" text-anchor="middle" font-size="11" fill="var(--tx2)">${{y}}</text>`;
  }});
  const svg = document.getElementById('trend-svg');
  svg.setAttribute('width', svgW); svg.innerHTML = out;
}}

function renderDonut() {{
  let n = 0, l = 0, m = 0;
  VOCAB.forEach(c => {{ const x = gm(c); if (x==='new') n++; else if (x==='learning') l++; else m++; }});
  const tot = VOCAB.length;
  const segs = [
    {{v: m, color: 'var(--gn)', label: '習得済み'}},
    {{v: l, color: 'var(--yw)', label: '学習中'}},
    {{v: n, color: 'var(--pu)', label: '未学習'}},
  ];
  let angle = -Math.PI / 2, paths = '';
  segs.forEach(s => {{
    if (!s.v) return;
    const a = (s.v / tot) * Math.PI * 2;
    const x1 = Math.cos(angle).toFixed(3), y1 = Math.sin(angle).toFixed(3);
    const x2 = Math.cos(angle + a).toFixed(3), y2 = Math.sin(angle + a).toFixed(3);
    paths += `<path d="M 0 0 L ${{x1}} ${{y1}} A 1 1 0 ${{a > Math.PI ? 1 : 0}} 1 ${{x2}} ${{y2}} Z" fill="${{s.color}}"/>`;
    angle += a;
  }});
  const pct = Math.round(m / tot * 100);
  paths += `<circle cx="0" cy="0" r="0.55" fill="var(--sf)"/>`;
  paths += `<text x="0" y="-0.08" text-anchor="middle" font-size="0.26" font-weight="800" fill="var(--tx)">${{pct}}%</text>`;
  paths += `<text x="0" y="0.18" text-anchor="middle" font-size="0.14" fill="var(--tx2)">習得</text>`;
  document.getElementById('donut-svg').innerHTML = paths;
  document.getElementById('donut-legend').innerHTML =
    segs.map(s => `<div class="dl"><div class="dldot" style="background:${{s.color}}"></div>${{s.label}}<span class="dlnum">${{s.v}}</span></div>`).join('');
}}

function renderYearTable() {{
  const rows = ALL_YEARS.map(y => {{
    const ws = VOCAB.filter(v => (v.year || 2020) === y);
    const tot = ws.length;
    const m = ws.filter(v => gm(v) === 'mastered').length;
    const l = ws.filter(v => gm(v) === 'learning').length;
    const mp = tot ? Math.round(m / tot * 100) : 0;
    const lp = tot ? Math.round(l / tot * 100) : 0;
    return `<tr>
      <td class="yn">${{y}}</td><td>${{tot}}</td>
      <td>
        <div style="font-size:11px;color:var(--tx2)">${{mp}}% 習得 / ${{lp}}% 学習中</div>
        <div class="prog-seg">
          <div class="seg-m" style="width:${{mp}}%"></div>
          <div class="seg-l" style="width:${{lp}}%"></div>
          <div class="seg-n" style="width:${{100 - mp - lp}}%"></div>
        </div>
      </td>
    </tr>`;
  }}).join('');
  document.getElementById('yt').innerHTML =
    `<thead><tr><th>年</th><th>件数</th><th>習熟度</th></tr></thead><tbody>${{rows}}</tbody>`;
}}

// ── SETTINGS ───────────────────────────────────
function setRF(f) {{
  st.revFilter = f;
  ['all','new','learning','mastered'].forEach(k =>
    document.getElementById('rf-' + k).textContent = f === k ? '✓' : '');
  savSt('revFilter', f); buildDeck();
}}
function resetP() {{
  if (!confirm('全ての進捗をリセットしますか？')) return;
  prog = {{}}; savP(); buildDeck(); renW();
  renderDonut(); renderYearTable();
}}

// ── NAV ────────────────────────────────────────
function sw(id, btn) {{
  document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  document.querySelectorAll('.nb').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  try {{ localStorage.setItem('lastView', id); }} catch(e) {{}}
  if (id === 'vw')  renW();
  if (id === 'vr')  updSess();
  if (id === 'va')  {{ updQUI(); }}
  if (id === 'vst') {{
    renderTrend(); renderDonut(); renderYearTable();
    ['all','new','learning','mastered'].forEach(k =>
      document.getElementById('rf-' + k).textContent = (st.revFilter === k) ? '✓' : '');
  }}
}}
function goView(id) {{
  const btn = document.querySelector(`#nav .nb[data-v="${{id}}"]`);
  if (btn) sw(id, btn);
}}

// ── UTILS ──────────────────────────────────────
function esc(s) {{ return (s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }}

// ── INIT ───────────────────────────────────────
function initApp() {{
  loadSt();
  buildDeck(); renW(); updQUI(); updSess();
  setRF(st.revFilter || 'all');
  // Restore the last tab the user was on (defaults to Add)
  let last = 'va';
  try {{ last = localStorage.getItem('lastView') || 'va'; }} catch(e) {{}}
  if (last !== 'va') goView(last);
  if ('serviceWorker' in navigator) navigator.serviceWorker.register('sw.js').catch(() => {{}});
}}

initApp();
</script>
</body>
</html>"""

def main():
    with open(VOCAB_JSON, encoding='utf-8') as f:
        vocab = json.load(f)
    cfg = get_config()
    html = generate(vocab, cfg)
    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Generated {OUTPUT_HTML} ({len(vocab)} entries)")

if __name__ == '__main__':
    main()
