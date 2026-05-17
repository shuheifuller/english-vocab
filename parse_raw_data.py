#!/usr/bin/env python3
"""
Parse Google Sheets vocabulary data into vocab_data.json.
Run once to initialize. After that, use sync.py to add new words.
"""

import json
import re
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT = os.path.join(SCRIPT_DIR, "vocab_data.json")

RAW_DATA = r"""| Date | New Word | Meaning | Sample sentence  | Note |
| :-: | :-: | :-: | :-: | :-: |

| Date | New Word | Meaning | Sample sentence  | Note |
| :-: | :-: | :-: | :-: | :-: |
| 1/6 | So much so that SVO | とてもそうなのでthat以下をしたほど | So much so that they have chosen ANZ for help since site option became available in PSAP  |  |
| 1/22 | Antisemitism | 反ユダヤ主義 |  |  |
| 1/23 | Homophone (C) | 同音異義 - 同じ方法で発音されるが、意味またはつづり方または両方ともにおいて異なるならば、2つの語は同音異義語である（例えば、bare（露出する）、bear（持って行く）） |  |  |
| 2/14 | Divide and conquer  |  |  |  |
| 3/9 | Caveat | 警告、注意 (=warning) |  |  |
| 5/14 | Pyramid scheme  | ネズミこう、マルチ商法 |  |  |

| Date | New Word | Meaning | Sample sentence  | Note |
| :-: | :-: | :-: | :-: | :-: |
| 1/8 | Relinquish ST | STを手放す、捨てる | Musk's temporary relinquishing of the chairman role | Relinquishment (noun) |
| 1/9 | Pro-(ST) | STを支持する人／団体 | Pro-Palestinian (パレスチナ人支持の) |  |
| 1/11 | Not to mention |  言うまでもなく |  |  |
| 1/17 | Actualize ST | STを具体化する |  |  |
| 1/24 | Exponential  | 指数関数的に |  |  |
| 2/1 | Alluding question  |  |  |  |
|  | Allude to ST | STをほのめかす、暗示する |  |  |
| 2/12 | Pugnacious  | 武力または暴力に訴えることのできるまたは用意のある | Tony Abott was overly pugnacious  |  |
| 2/19 | Coalition (=alliance) | 連合、アライアンス |  |  |
| 3/15 | Break grass option | 緊急の場合に普段制限されている権限を与えるオプション |  |  |
| 4/19 | In a nutshell  | 一言で言えば |  |  |
| 4/22 | No brainer | 当たり前、考える必要がない、簡単すぎる |  |  |
| 5/2 | Piggy back ST |  |  |  |
| 5/30 | Apathy | 無関心、無頓着、無気力 |  |  |
| 6/5 | In retrospect  | 振り返ってみると、 |  |  |
| 6/13 | Convoluted  | ややこしい、複雑すぎる |  |  |
| 6/14 | Preconceived notions  | 先入観 |  |  |
| 7/12 | Gaffe | 失言 |  |  |
| 7/23 | et al  | その他各位、~など、~およびその他 | (メールの宛名で) Hi Shuhei et al |  |
| 7/24 | Postmortem  | 事後 | I'll investigate what happened postmortem  |  |
| 7/26 | Misology | 嫌悪 | I will not be lectured sexism and misology by this man (quote from Julia Gillard) |  |
| 8/6 | Overarching  | 包括的な | It'd be an overarching statement  |  |
| 11/2 | Demean SO | SOを辱める |  |  |
| 11/15 | Nitty-gritty  | 核心、本題 |  |  |
| 12/21 | Bread and butter  | 最も重要なもの、必要不可欠なもの | Problem solving skills are leader's bread and butter in many ways |  |
| 12/30 | Caveat (C) | 警告、注意 | There are some important caveats to keep in mind when promoting and wining with LLMs |  |

| Date | New Word | Meaning | Sample sentence  | Note |
| :-: | :-: | :-: | :-: | :-: |
| 1/2 | Conform to ST | STに従う、準ずる、同調する |  |  |
|  | Conformism | 同調主義 |  |  |
| 1/6 | Actions speak louder than words |  |  |  |
| 2/11 | Low hanging fruit  | 簡単に得られるもの、達成できること | If the ask is a low hanging fruit, let's push for it |  |
|  | Drawn out | 引き伸ばされた、長々とした |  |  |
| 2/18 | Just because | なんとなく、そんな気分だったから |  |  |
| 3/17 | Wholesome | 健全、健康的な |  |  |
|  | Porpoise | (パフォーマンスが)不安定な |  |  |
| 4/18 | Arbitrarily  | ランダムに、無作為に |  |  |
| 4/24 | Remuneration  | 報酬 |  |  |
|  | Double down |  |  |  |
|  | Fabricator  | でっちあげ |  |  |
| 5/3 | Made redundant  | リストラされる、失業する、不必要になる | I was made redundant  |  |
| 5/5 | Autonomy  | 自主性、自由、自治権 |  |  |
| 5/13 | Mortality  | 死亡率 |  |  |
| 5/19 | Soap actress | 昼ドラ女優 |  |  |
| 6/6 | Mole | ほくろ |  |  |
| 6/14 | Supposedly  | 噂によれば |  |  |
| 6/17 | Vent | 発散する、不満を吐き出す |  |  |
| 6/28 | Standard deviation  | 標準偏差 |  |  |
|  | Coefficient of Variation (CoV) | 変動係数 |  |  |
|  | Coefficient  | 係数 |  |  |
| 6/29 | Pragmatic | 実践的な |  |  |
| 7/2 | Patriarchy  | 家長制 |  |  |
|  | Bystander effect | 傍観者効果 | ある事件に対して、自分以外に傍観者がいる時に率先して行動を起こさなくなる心理 |  |
|  | Mishmash  | 寄せ集め | It's a mishmash of terms that we use |  |
| 7/14 | Overlay ST | STを横に並べる | You need to overlay risks, findings and recommendations  |  |
| 7/18 | Down Under | オーストラリア |  |  |
|  | If the juice is worth the squeeze |  | We'd need to figure out if the juice is worth the squeeze on our capacity vs improved cx |  |
| 7/24 | Flesh out |  |  |  |
| 7/27 | Cervix |  |  |  |
| 7/30 | Connotation  | ほのめかし、暗示 |  |  |
| 9/3 | Yet another  | さらに別に(さらにを強調) | Another is used when we want to add one thing to one thing else or to a short list. Yet another is used to add one thing to a long list that was mentioned before. |  |
| 9/6 | Decay |  |  |  |
|  | Quotation | 見積もり |  |  |
|  | Pathology |  |  |  |
| 9/14 | Voluntold | 嫌々ボランティア活動に従事させられる |  |  |
|  | Alluded question |  |  |  |
| 9/27 | Nasal Congestion  | 鼻詰まり |  |  |
| 10/11 | Champion ST | 擁護する、守る、庇う | Champion a sense of belonging at AWS |  |
| 11/3 | Be suss on ST/SO | に疑いをかける |  |  |
| 11/6 | Social butterfly | 八方美人 |  |  |
| 11/27 | Brick and mortar companies  | (実店舗で)店舗経営をする会社 |  |  |
| 12/22 | Shameless Plug | アピールするのも恥ずかしいようなこと |  |  |
| 12/30 | Goes by in a blink of an eye | またたく間に過ぎる。瞬きぐらい一瞬で過ぎる | Ten years at AWS. It went by in a blink of an eye |  |

| Date | New Word | Meaning  | Sample sentence | Note |
| :-: | :-: | :-: | :-: | :-: |
| 1/5 | Like to like |  |  |  |
| 1/6 | Speak/Talk of the devil | 噂をすれば、 |  |  |
|  | Vandals  | 野蛮人 | People who do vandalism |  |
| 1/12 | Bronchitis | 気管支炎 |  |  |
|  | Preempt  | 先取りする |  |  |
| 1/17 | Cabin fever  |  |  |  |
| 1/18 | Fertilization treatment | 不妊治療 |  |  |
| 1/26 | Ear-pleasing | 聞こえのいい |  |  |
| 2/1 | Derail | を脱線させる | I don't wanna derail the conversation but |  |
| 2/4 | Flying blind |  |  |  |
| 2/8 | MIA (missing in action) | 行方不明、連絡がつかない、ご無沙汰 | Apologies for going MIA today  |  |
| 2/12 | Fwiw (for what it's worth) | これはあくまで私の個人的な意見ですが |  |  |
|  | Myopic | 目先のことしか考えない、短絡的な、近視眼的な |  |  |
| 2/15 | Guardrails |  | What are the guardrails?  |  |
|  | Jurisdiction  | 管轄 |  |  |
| 2/24 | Sovereignty  | 主権 | Ukraine is fighting for their sovereignty  |  |
|  | Dwarf | を妨げる、小さく見せる | Russia's firepower dwarfs Ukraine |  |
|  | Vow (ST or to do ST) | STを誓う |  |  |
| 3/1 | Two cents  | パッと思いついたこと、簡単な考え |  |  |
|  | Shelling  | 砲撃、集中砲火 |  |  |
| 3/21 | Human trafficking  | 人身売買 |  |  |
|  | Cater for ST | STに応じる、応える、満たす |  |  |
| 4/5 | Templatize | テンプレート化する |  |  |
|  | Go south | が悪化する | It would've gone south quickly  |  |
| 4/12 | Hold SO accountable for ST | SOにSTの責任を負わせる |  |  |
| 5/30 | Solidarity  | 一致団結、結束、連帯 |  |  |
| 6/16 | (The) Wild West | 未開の地、新しく不明な点が多い | Face recognition is the Wild West |  |
| 6/20 | Puberty | 思春期 |  |  |
|  | Speak of the devil | ちょうど噂をすれば |  |  |
| 7/1 | Exhaustive  | 完全な、網羅的な、包括的な |  |  |
| 7/3 | Solicit |  | Solicit the name |  |
| 7/15 | Double down on ST |  | Big data team wants to double down on our recruiting effort |  |
|  | Go along with ST | STに同意 | I'd go along with that |  |
|  | No brainer  | 思考を必要としないもの | It seems obvious and no brainer to me |  |
|  | Going once going twice | ミーティングなどを閉める前にする最終確認のためのカウントダウン |  |  |
| 7/17 | Exasperate SO | SOを憤慨させる、激怒させる |  |  |
| 10/7 | Give SO the benefit of the doubt | (疑わしいところはあるが)SOの言動を信じる |  |  |
|  | So be it | それならそれでいい |  |  |
| 10/8 | Man of culture | (文化人を皮肉った)変態/すけべ |  |  |
| 11/1 | Add up | おかしい、正しくない、つじつまが合わない | Does not add up = does not make sense |  |
| 11/6 | Underdog | 負け犬 |  |  |
| 11/8 | Ultimatum | 最後の通告、最終決断 | Set an ultimatum |  |
| 11/16 | Voluntary Administration | 破産手続き | Deliveroo goes into voluntary administration  |  |
| 12/20 | Leeway | 許容範囲 | Is it a reporting leeway?  |  |

| Date | New Word | Meaning  | Sample sentence | Note |
| :-: | :-: | :-: | :-: | :-: |
| 1/1 | Homy | 家庭的 |  |  |
| 1/2 | Contraception  | 避妊(法) | Artificial contraception - 人口避妊 |  |
| 1/6 | Kerb  | 縁石 |  |  |
| 1/12 | Skew | (事実など)を歪める、を歪曲する |  |  |
| 1/13 | Streak  | 流れ、連続 | Have a major self-destructive streak in you |  |
|  | Torpedo ST | STを破壊する、撃沈する | You kind of torpedo every romantic relationship you're in  |  |
|  | Mistress  | 愛人、不倫相手 |  |  |
|  | Autism  | 自閉症 |  |  |
|  | Inhale | 空気を吸い込む、吸引する |  |  |
|  | Exhale | 空気を吐き出す | Breath out  |  |
| 1/14 | Sever ST | STを断ち切る | Severing all contacts with the Trump organization  |  |
|  | Incitement  | 扇動、鼓舞、誘因 |  |  |
|  | Insurrection  | 反逆、反乱、謀反 |  |  |
|  | Give SO Silent Treatment  | SOにだんまりを決め込む |  |  |
| 1/15 | Procreate | 子供を産む |  |  |
|  | My hats off to SO | SOに脱帽する、を称賛する | Take one's hat off |  |
|  | In accordance with ST | STに合わせて | Change in accordance with the situation  |  |
| 1/19 | Variant  | 変異種 | Researchers are concerned by the fact that the new coronavirus variant is spreading so quickly |  |
| 1/21 | Inauguration  | 就任 |  |  |
| 1/22 | Cause of action  | 方針、やり方、行動様式 |  |  |
| 2/7 | Happen in a vacuum  | 他と無関係に起こる |  |  |
|  | Take sides with SO | SOの一方を支持する |  |  |
|  | Amicable  | 円満な、友好的な | Amicable divorce: 円満離婚 |  |
|  | Abduct SO | 拉致する |  |  |
|  | Go walkabout  | 放浪生活に出る、行方不明 |  |  |
| 2/8 | Make X default to Y | XをYより優先させる | How do I make Excel default to numbers on Mac? |  |
|  | Rebate  | 払い戻し、還付 |  |  |
| 2/10 | Look around the corner  | 先を見越す |  |  |
| 2/11 | Open the kimono with SO | SOに秘密の情報を明かす |  |  |
|  | Cringe  |  |  |  |
| 2/14 | Acquitted  | 潔白な、無罪な |  |  |
| 2/17 | Workation  | WorkとVacationを組み合わせた |  |  |
| 2/20 | Resuscitate | 蘇生する | Do-not-resuscitate form |  |
|  | Not my cup of tea | 興味がない | It's not my cup of tea |  |
| 2/24 | Pull ST off  | STをやり切る、達成する |  |  |
| 3/3 | Tuberculosis | 結核 |  |  |
|  | In light of |  |  |  |
|  | Out of league  | 格が違う、スバ抜けて優秀、高嶺の花 | My friend Megan is out of league  |  |
| 3/11 | Monarchy  | 君主制 |  |  |
| 3/20 | Bring SO up to speed | SOに必要な情報を伝えて状況を理解させる |  |  |
| 3/26 | Misogyny | 女性嫌悪 |  |  |
|  | Xenophobia  | 外国人嫌悪 |  |  |
| 4/2 | Microcosm  | 縮図 | Amazon is a microcosm of the world in some ways |  |
|  | Assimilate | を取り込む、取り入れる | The organization expects employees to assimilate to a certain degree |  |
|  | Resentment  | 恨み、憎しみ |  |  |
|  | Trailblazer  | 草分け的存在、パイオニア |  |  |
| 4/6 | Leukaemia | 白血病 |  |  |
|  | Pediatric  | 小児の | Pediatric Cancer |  |
| 4/9 | Streisand effect | ストライサンド効果 - ある情報を隠蔽しようとする努力が、かえってその情報を広い範囲に拡散させてしまう現象 |  |  |
| 4/13 | Break a leg | 頑張る、うまくやる |  |  |
| 4/22 | Off the top of my head | パッと思いつく限り |  |  |
| 5/15 | You said it | 全くその通りだ | Haha you said it! |  |
| 5/31 | Bystander  | 傍観者 |  |  |
|  | Retaliation  | リベンジ | Retaliation is never accepted |  |
|  | Disciplinary action  | 懲戒処分 | The employee will be subject to disciplinary action |  |
| 6/1 | Impeccable  | 完璧な、非の打ち所がない |  |  |
| 6/2 | Tell me about it | 本当にそうだよね |  |  |
|  | You can say that again | 本当にそうだよね |  |  |
|  | Indifferent  | そっけない、冷たい、無関心な |  |  |
|  | Civil  |  | Keep it civil - 礼儀正しくしなよ |  |
| 6/6 | In one's favor | xxに有利な | Play in his favor |  |
|  | Arbitrary  | 任意の、恣意的な、無作為な |  |  |
|  | Tedious  | 長ったらしい、つまらない、退屈な |  |  |
| 6/13 | Hyperbolize | 言いすぎる、誇張する | I cannot explain my experiences without hyperbolizing  |  |
| 6/15 | Rest assured that  | (That以下のことを)確実であると思う | Rest assured that you will have my ears to listen |  |
| 6/19 | In light of ST | ST(新しい情報)を踏まえると | In the realms of ST |  |
|  | Genesis  | 発生、起源、創生 |  |  |
|  | Tepid | 生ぬるい |  |  |
| 6/25 | She'll be right (Aussie slang) | Whatever is wrong will right itself with time |  |  |
| 6/26 | Schizophrenia | 統合失調症 |  |  |
| 7/4 | Pro bono  | 公共慈善活動 | ラテン語が起源 - Pro (For) Bono (Good) Public |  |
|  | Trump | 切り札を出す | You have to trump somebody to resolve issues as quickly as possible |  |
|  | Set ST apart | STを差別化する | What sets AWS apart? |  |
| 7/7 | Velocity  | 速度 | High velocity - 高速 |  |
|  | Be after | 狙う、追跡する | If you're after some of the best coffee |  |
| 7/11 | For god's sake | ひどい、あきれた、どうか頼むから |  |  |
| 7/13 | Alleviate  | を和らげる、緩和する |  |  |
|  | Epitome  | 典型 | He was the epitome of evil |  |
|  | Watercooler | おしゃべり、立ち話、井戸端会議 |  |  |
| 7/14 | Overhead (UC) | 追加の作業、諸経費 |  |  |
|  | Repurpose  | 目的を変えて再利用する | Ask here is to repurpose your next 1:1 |  |
| 7/15 | Dwell | 住む、居住する | engineers with dwell time over 18 months in role |  |
|  | Housekeeping | 事務連絡、連絡事項、基本的な注意事項 |  |  |
|  | Gauge | を測定する、評価する、判断する | gauge feedback on ST |  |
|  | Cohort | a group of people with a shared characteristic |  |  |
|  | Elevator pitch | 簡潔な説明 | 語源: エレベータ内で顧客に偶然会ったとき、短い時間に自分の会社を説明する |  |
| 7/17 | Hibernate | 休眠させる |  |  |
| 7/20 | Sugarcoated  | 耳障りが良い、汚い部分を隠した |  |  |
| 7/21 | Throttle  | を抑制する、制限する |  |  |
| 7/25 | Resonate | 共鳴する/させる、反響する/させる |  |  |
| 7/26 | Dictate  | を指示する、命令する、決定する |  |  |
|  | Farmed  | 養殖の/された |  |  |
| 7/27 | Trajectory | 曲線、軌道、軌跡 | I can tell he's in a right trajectory |  |
| 7/29 | Aggravate | を悪化させる、荒立てる |  |  |
| 7/30 | Deprive SO of ST | SOからSTを取り上げる、奪う |  |  |
| 8/3 | Surface ST (verb) | アイデアなどを表面に出す | Surface an idea |  |
|  | Apprehensive  | 心配している、不安な | Managers are a bit apprehensive about what format we need to follow  |  |
| 8/19 | Double down | さらに力を入れる、強化する | Day 1 culture requires you to double down |  |
| 8/25 | Glass Cliff | ガラスの崖 - 女性が危機的状況でリーダーに昇進しやすい現象 |  |  |
| 8/26 | Alumni | 卒業生 |  |  |
|  | Deflect  | をそらす、はじく |  |  |
| 8/27 | The devil's in the details | 細かいところに落とし穴がある |  |  |
|  | Heterogeneous  | 異種の、異質な |  |  |
| 8/29 | Carnage  | 大量殺人、大虐殺 |  |  |
|  | Fill SO in (with ST) | SOを(STで)補足して話に追いつかせる |  |  |
| 9/19 | Skew | を歪める、歪曲する | It can skew the data |  |
| 9/21 | Intrinsic  | 内因的な、内からの | Intrinsic motivation  |  |
|  | Extrinsic  | 外因的な、外からの | Extrinsic motivation  |  |
| 9/26 | Joke aside | 冗談はさておき |  |  |
| 9/30 | Status quo  | 現状(維持) |  |  |
| 10/5 | Counterproductive  | 逆効果の |  |  |
| 11/2 | Counterintuitive  | 直感に反する |  |  |
| 11/9 | Catalog ST (verb) | STをリストとしてまとめる、カテゴリー分けする |  |  |
| 11/16 | Axis  | 軸 | X axis and Y axis |  |
| 11/19 | Punitive  | 懲罰的な、過酷な |  |  |
| 11/24 | Factor in ST | STを考慮に入れる |  |  |
| 11/26 | Rapport | 相互理解、相互信頼 | Build rapport and trust  |  |
| 12/20 | I know for a fact that SV | (That以下)を事実として知っている |  |  |
| 12/25 | Cut to the chase | 本題に入る |  |  |
|  | Fall on someone's sword | 誰かの代わりに責任を負う |  |  |
|  | Grudge  | 根深い恨み | Grudgeの方がresentmentより強いニュアンス |  |

| Date | New Word | Meaning  | Sample sentence | Note | How many times did you review? |
| :-: | :-: | :-: | :-: | :-: | :-: |
| 1/5 | Agnostic | 神の存在を否定しない無宗教者(=不可知論者) |  | atheist - 神の存在を否定する人  | 2 |
| 1/6 | Incentivize | (何かしらのincentiveでもって) 促す、動機付けする | I was incentivized by the reward  |  | 1 |
| 1/6 | Call on SO for ST | STをSOに求める、要請する | You have to call on them for their input |  | 1 |
| 1/7 | Auto-pilot mode | 自動運転 | You have to delegate in order to be in the auto-pilot mode |  |  |
| 1/8 | Unconditional support | 無条件のサポート |  |  |  |
| 1/10 | Consensual | 同意による | Cultures that fall as egalitarian believe in consensual decision making. |  |  |
| 1/11 | Dynamic | 流動的な、活動的な | The world is dynamic and things are changing. |  |  |
| 1/11 | Lexicon | 語彙、ボキャブラリー | In today's global business lexicon, the word consensus has a positive ring. |  |  |
| 1/11 | Epitomize | を代表する | The Japanese ringi system epitomizes a culture where decisions take a long time. |  |  |
| 1/11 | Interplay (C) | 相互作用 | There is a stronger interplay between affective and cognitive trust. |  |  |
| 1/11 | Be taken aback | 驚く、衝撃を受ける |  |  |  |
| 1/11 | Misstep | 過失 | Once an affective relationship is established, the forgiveness for any cultural missteps you make comes a lot easier. |  |  |
| 1/12 | Superficial | 表面的な |  |  |  |
| 1/13 | Arson | 放火 | Arson fire, Arson death |  |  |
| 1/14 | Go viral | 急速に広まる、伝搬する |  |  |  |
| 1/14 | Respiratory  | 呼吸器系 | People living in an area with hazardous air quality are advised to limit their time outdoors. |  |  |
| 1/14 | Huddle | 身を寄せ合う | The survivors huddled together to keep warm |  |  |
| 1/15 | Burden (C) | お荷物、厄介、負荷 | This year we will have one engineer shadowing to ensure less of a burden |  |  |
| 1/15 | Woo | に求愛する | Jeff Bezos tries to woo India |  |  |
| 1/16 | Stem from | から由来する、生じる | Many Japanese use drinking to forge connections, stemming from the Japanese verb nomu. |  |  |
| 1/16 | Do wonders | 驚くべき効果がある | Alcohol is not the only way to build a business relationship. A round of karaoke can do wonders. |  |  |
| 1/17 | Chastise | を正す、直す、矯正する | He chastised Sen. Martha McSally for going after his colleague |  |  |
| 1/18 | Cherish | 愛おしむ、愛でる、大切にする |  |  |  |
| 1/18 | Brolly | 傘 | Don't forget to pack a brolly today |  |  |
| 1/19 | Be across ST | に精通する、を知っている |  |  |  |
| 1/20 | Keep ST handy | を手元に置く |  |  |  |
| 1/21 | Run rate | ランレート（直近の実績値の傾向がそのまま続くと仮定した場合の将来予測値） |  |  |  |
| 1/22 | Fatality rate | 致死率 | The fatality rate of Wuhan coronavirus is standing at 1.6% |  |  |
| 1/23 | Plateau | 台地、高地、高台 |  |  |  |
| 1/23 | Apprised | 知らされている | Keep me apprised |  |  |
| 1/23 | Intake  | 摂取する、取り込む |  |  |  |
| 1/27 | Adultery | 不倫、婚外性行 |  |  |  |
| 1/27 | Persona |  |  |  |  |
| 1/27 | A sound argument | 正論 |  |  |  |
| 1/28 | Reiterate | 繰り返す、再度述べる |  |  |  |
| 1/28 | Hygiene (non-C) | 衛生状態 | Have poor hygiene (衛生状態が悪い) |  |  |
| 1/29 | Lost in translation  | 翻訳で意味が失われる |  |  |  |
| 1/30 | Bustle  | 精力的に忙しくする |  |  |  |
| 1/30 | As far as X is concerned | Xに関する限り | As far as I'm concerned - 私の考えとしては |  |  |
| 1/31 | Sub-optimal  | 最適ではない | This is sub-optimal behavior but would achieve the desired outcome  |  |  |
| 1/31 | My 2 cents | 私のちょっとした意見 | Here is my 2 cents |  |  |
| 2/1 | Cardiac arrest (C) | 心肺停止 | Render first aid treatment when you find someone suffering a cardiac arrest |  |  |
| 2/1 | Render  | を与える、を表す、人や物をある状態にする |  |  |  |
| 2/1 | Implications  | 引き起こされるだろう結果、意味合い | Understanding billing implications is quite important |  |  |
| 2/1 | Leverage | を活用する | Understand how to leverage CS for billing and account inquiries  |  |  |
| 2/1 | Subtle (Adj) | 微妙な、繊細なニュアンス |  |  |  |
| 2/1 | Keep you company | あなたについて行く | I'll keep you company |  |  |
|  | Manslaughter  | 故殺(意図せず結果的に殺してしまうこと)、過失致死 | A 29-year-old man has been charged with 20 offenses including manslaughter |  |  |
|  | Legislature | 立法機関 | The current Diet of Japan was established in 1946. |  |  |
| 2/5 | Summon | を召喚する、を呼び出す | Summon a lawyer |  |  |
|  | Fireside chat  | 落ち着いた雰囲気で楽しむ会話 |  |  |  |
|  | Stigma  | 汚点 |  |  |  |
|  | Hard-earned (adj) | 努力して得た |  |  |  |
| 2/13 | Upskill | スキルをあげる |  |  |  |
| 2/16 | Be deprived of SO/ST | STやSOを奪われる | The actress was deprived of any chance to appear on television |  |  |
| 2/17 | Monday Blues | 月曜日に気乗りしない状態 |  |  |  |
|  | Axe | をやめる、終了する | About 600 Holden employees will lose their jobs after parent company announced it would axe the iconic Australian car brand. |  |  |
|  | Terrible twos | イヤイヤ期 |  |  |  |
| 2/19 | Substantial (adj) | かなりの、相当な | A substantial amount of x |  |  |
| 2/24 | Have a bun in the oven  | 妊娠する |  |  |  |
|  | Over the moon (adj) | 大喜びしている |  |  |  |
| 2/28 | Talk SO through ST | STについてSOに細かく説明する |  |  |  |
| 3/4 | Be on top of ST | STに責任を持って自発的に行動する |  |  |  |
|  | Misconduct  | 不正行為 | Financial misconduct  |  |  |
| 3/13 | Deter SO from | SOが何かするのを阻止する |  |  |  |
| 3/15 | Nosy (Adj) | 詮索する様、首を突っ込みがち |  |  |  |
| 3/17 | Cabin fever | 長期間閉じ込められることによる強い閉塞感や焦燥感 |  |  |  |
|  | Anarchy | 無秩序、無政府状態 |  |  |  |
| 3/19 | Ahead of the curve | 先手を打って、先回りして、先取りして |  |  |  |
| 3/20 | Prejudice | 先入観、偏見 |  |  | 1 |
| 3/21 | Unprecedented  | 前例のない、異例の、前代未聞 |  |  |  |
|  | Be blindsided by ST | STによって不意打ちをくらう |  |  |  |
| 3/24 | Radius | 半径 | Delivery available within 500m radius |  |  |
|  | Evict  | を追い出す | Tenants cannot be evicted because of the economic fallout from Coronavirus Crisis. |  |  |
|  | Resemble SO | SOと似ている | I'm becoming to resemble my mother |  |  |
| 3/29 | Temperamental  | 気まぐれな | The internet is becoming temperamental  |  |  |
| 4/2 | Cadence  | 周期、リズム | We need to decide the cadence of the meeting. |  |  |
|  | In light of  | を考慮すると | (= considering or given) |  |  |
| 4/8 | Lift | 解除する | Authorities lifted a ban on outbound travel from Wuhan |  |  |
| 4/14 | Surreal  | 非現実的な、夢のような |  |  |  |
|  | Jurisdiction  | 管轄、管轄区域 |  |  |  |
| 4/15 | Fatality rate | 致死率 |  |  |  |
|  | Hypertension  | 高血圧症 |  |  |  |
| 4/25 | Effing | Fuckingの婉曲語 | That's effing awful. |  |  |
| 5/3 | Laid-back | くつろいだ、リラックスした |  |  |  |
| 5/5 | Reprimand (N & V) | 叱責する、責める、懲戒する |  |  |  |
| 5/9 | Eradicate  | を殲滅する、根絶やしにする |  |  |  |
| 5/14 | Defy | に逆らう、従わない |  |  |  |
|  | Attribute  | STに帰する、STのせいにする |  |  |  |
|  | Be attributed to ST | STが原因と考えられる | Attributed mainly to, partially to, solely to |  |  |
|  | Intimidate | を怯えさせる | It was intimidating. |  |  |
| 5/17 | Stand out | 目立つ、卓越する、際立つ |  |  |  |
| 5/25 | The edge goes to SO/ST | SO/STに軍配が |  |  |  |
| 5/29 | Rein in ST | STをとめる、抑制する | Rein (n) = 手綱 |  |  |
| 6/1 | Resilience  | 柔軟性、耐性、回復力 |  |  |  |
| 6/4 | In turn  | 順番に | (= One by one, in turn) |  |  |
| 6/8 | Dissuade SO from | 説得によってやめさせる |  |  |  |
| 6/12 | Tangent  | 話がずれた | Go off on a tangent (話がずれる) |  |  |
|  | Tangible  | 目に見える、具体的な | (=Visible) |  |  |
| 6/19 | Double edged sword  | 諸刃の剣 |  |  |  |
| 6/27 | Bonanza  | 大当たり、大儲け、金の卵 | It was a perfect combination for a bonanza of new day traders |  |  |
| 7/4 | FOMO (fear of missing out) | 取り残される恐怖心 = 同調圧力 |  |  |  |
| 7/8 | Get around to ST | STにようやく取り掛かる |  |  |  |
| 7/11 | Dynamic | 変化する、流動的な |  |  |  |
| 7/15 | Verbatim | 一語一句同じように、逐語的に |  |  |  |
| 7/16 | Herd immunity  | 集団免疫 |  |  |  |
| 7/18 | Adverse effect | 悪影響 | With no adverse effects |  |  |
|  | Attest to ST | STを証明する |  |  |  |
|  | Get hands dirty | 実際にやってみる、手を動かす |  |  |  |
|  | Collateral  | 付随した、二次的な | Collateral damage  |  |  |
| 7/19 | Upskill | のスキルをあげる |  |  |  |
|  | Complacency (N) | 自己満足、独りよがり | SmugよりFormal |  |  |
|  | Pillar | 柱、大黒柱、中核 | Kuno has become a major pillar of Mallorca |  |  |
|  | Sycophant | ごますりな人、おべっか使い |  |  |  |
|  | Tedious | つまらない、長ったらしい | DullやBoringに似ているが物やプロセスに対して使う |  |  |
|  | Deliberately  | 意図的に | カジュアル: On purpose > Intentionally > Deliberately: フォーマル |  |  |
| 7/22 | Seasoned (adj) | 経験のある、熟練した |  |  |  |
| 7/24 | Token | しるし、記念 | Sending flowers as a token of appreciation  |  |  |
|  | Resourceful  | 臨機応変な |  |  |  |
| 7/26 | Take on ST | STに取り組む(難題や困難) |  |  |  |
| 7/27 | Profane (adj) | 口汚い、冒涜的な |  |  |  |
| 7/28 | Leeway (UC) | 余裕 | Give her some leeway |  |  |
|  | Walk-through | 一つずつやってみせること、デモンストレーション |  |  |  |
| 7/31 | Stellar  | 輝かしい、際立った、星の |  |  |  |
|  | Social Construct | 社会的構成概念 |  |  |  |
| 8/1 | Quip | 冗談を言う |  |  |  |
| 8/2 | Subset | 小さなまとまり、部分集合 | Download a subset of data |  |  |
| 8/5 | Sugar-coating ST | STの見かけを良くする |  |  |  |
| 8/6 | Eerie  | 不気味な |  |  |  |
| 8/11 | Bear in mind | STを心に留める |  |  |  |
|  | Get one's head around ST | STを理解する |  |  |  |
| 8/13 | Cannot see the forest for the trees  | 木を見て森を見ず |  |  |  |
|  | Decipher ST | STを読み解く、を解読する |  |  |  |
| 8/15 | By far  | ずばぬけて | Speaking is by far the most important thing  |  |  |
| 8/22 | Hibernate | 冬眠する/させる |  |  |  |
| 8/23 | Knowingly (adv) | 知りながら | She knowingly bought stolen goods |  |  |
| 8/26 | Asymptomatic | 自覚症状の無い | Asymptomatic person's viral load is the same as symptomatic person's |  |  |
| 8/27 | Echo ST | STに同意する、を繰り返す | I just wanna echo what Adam said |  |  |
| 8/29 | Decisive | 断固たる、決定的な |  |  |  |
|  | Excel at ST | STに秀でる | STで目覚ましい活躍をする |  |  |
| 8/30 | Vigilance  | 警戒、用心 |  |  |  |
| 9/2 | Blow over | 静まる、おさまる、過ぎ去る |  |  |  |
| 9/6 | Cliche (adj) | 決まり文句な、月並みな | I know it sounds cliche  |  |  |
|  | Dexterity  | 器用さ | mental dexterity |  |  |
| 9/7 | In grief | 傷心中、深い哀しみの中にいる | She's in grief of losing a dog  |  |  |
| 9/10 | Pitfall  | 落とし穴 | What is the common pitfall?  |  |  |
| 9/19 | Vasectomy | 精管切除術(男性避妊手術) |  |  |  |
|  | Walk out on SO | SOの元を去る |  |  |  |
| 9/27 | Over the moon | 大喜び | I'm sure you're over the moon with your family back |  |  |
| 10/5 | Obnoxious  | 感じの悪い、反抗的な | The note is obnoxious |  |  |
|  | Pristine  | 手付かずの、新鮮な、自然のままの | Beaches are pristine |  |  |
| 10/7 | Blunt | 率直な、ストレートな、ざっくばらんな |  |  |  |
| 10/17 | A matter of time | 時間の問題 | it was just a matter of time |  |  |
|  | Paragon | 模範、手本 | He's a paragon of fashion  |  |  |
| 10/24 | Truth be told | 実を言うと |  |  |  |
| 11/3 | Blueprint | ひな形、設計図、パターン |  |  |  |
| 11/12 | Fasting  | 断食 |  |  |  |
|  | Sane | 正気 |  |  |  |
|  | Hear SO out | SOの話を最後まで注意して聞く |  |  |  |
| 11/14 | Scaffolding  | 足場、処刑台 |  |  |  |
|  | Equity (vs Equality) | 公平性 | Equality - 同等、平等 |  |  |
| 11/20 | Concur with SO | SOに同意する | Concur with you  |  |  |
| 11/25 | Run past SO | SOに相談する、尋ねる | I also have an idea to run past you |  |  |
| 11/27 | Proposition  | 提案、議案 |  |  |  |
|  | Baseless | 事実無根の、根拠のない |  |  |  |
| 12/1 | Get in the way of ST | STの邪魔をする、妨げになる | What gets in the way of Diversity and Inclusion? |  |  |
|  | Immersive  | 没入感のある |  |  |  |
| 12/21 | Hoax | でっちあげ |  |  |  |
| 12/31 | Complications | 合併症 | Australian famous star died aged 82 from coronavirus complications  |  |  |"""


def clean(s):
    """Clean markdown escapes and extra whitespace from a cell value."""
    if not s:
        return ""
    # Remove common markdown escapes
    s = re.sub(r'\\(.)', r'\1', s)
    # Remove trailing/leading whitespace
    s = s.strip()
    return s


def parse():
    entries = []
    entry_id = 1
    current_date = ""

    for line in RAW_DATA.split('\n'):
        line = line.strip()
        if not line.startswith('|'):
            continue

        parts = line.split('|')
        cols = [clean(p) for p in parts[1:-1]]  # remove first/last empty

        if len(cols) < 2:
            continue

        # Skip header and separator rows
        if not cols or cols[0] == 'Date' or ':-:' in cols[0] or cols[1] in ('New Word', ''):
            if len(cols) > 1 and cols[1] in ('New Word',):
                continue
            if ':-:' in line:
                continue

        date_val = cols[0] if cols else ""
        word = cols[1] if len(cols) > 1 else ""
        meaning = cols[2] if len(cols) > 2 else ""
        example = cols[3] if len(cols) > 3 else ""
        note = cols[4] if len(cols) > 4 else ""

        if date_val:
            current_date = date_val

        # Skip if no word or if it's a header
        if not word or word in ('New Word', 'Date'):
            continue

        entries.append({
            "id": entry_id,
            "word": word,
            "meaning_ja": meaning,
            "english_def": "",
            "example": example,
            "notes": note,
            "date_added": current_date,
            "mastery": "new"
        })
        entry_id += 1

    return entries


def main():
    entries = parse()
    with open(OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(entries)} entries to {OUTPUT}")


if __name__ == '__main__':
    main()
