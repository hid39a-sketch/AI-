# 第5話「ジュラ紀：巨人たちと最初の鳥」ファクトチェック（2026-10-23）

対象：`scripts/ep05_jurassic.txt`。行番号は、下の「1. 直した点」と「5. 読みの確認」を台本に反映した**あとの**台本ファイルの行番号です（修正はすでに台本に入れてあります）。

判定の意味
- **OK** … 一次文献（論文・博物館・大学・公的機関）で裏付けが取れた
- **修正** … 書く途中で数字や言い方を直した（直す前の文と、直した理由・出典つき。台本には反映済み）
- **外す** … 裏付けが取れなかった、または長さの都合で、台本に入れなかった

調査の限界（正直に書いておくこと）
- 出版社のサイト（Science・Nature・Elsevier など）は接続を拒否することが多いため、多くの論文は **Europe PMC・Crossref・OpenAlex の要旨**で確認しました。本文まで読めたのは Sander et al. 2011（PMC）・Barba-Montoya et al. 2018（PMC）・Taylor 2009（著者公開PDF）・Taylor, Wedel & Naish 2009・Griebeler et al. 2013・Motani et al. 2014（PMC）・Trujillo & Kowallis 2015（PDF）・Mallison 2011（PDF）です。
- 要旨・博物館や大学の発表・公的機関のページだけで確認したもの：ディプロドクスの全長（ロンドン自然史博物館＝NHM）、ステゴサウルス「ソフィー」の大きさ（NHMの発表）、アロサウルス・ジムマドセニの大きさ・歯の数（ユタ自然史博物館の発表）、始祖鳥の産地・年代（NHM）とシカゴ標本の大きさ（フィールド博物館の発表）、アンキオルニスの年代（NHM）、メアリー・アニングの経歴（NHM）、モリソン層の州・名前の由来（USGS Geolex）・干ばつ（国立公園局 NPS）、ジュラ紀の名前の由来と植物（UCMP）、パンゲアの分裂（USGS）。
- 参考文献のDOIは、すべて Crossref で書誌（著者・雑誌・巻・ページ）と一致することを確かめました（2026-10-23。Carpenter et al. 2005 は書籍の章でDOIがないので、内容は Mallison 2011 の本文で確かめた）。
- USGS Geolex のページは自動取得で403が返ることがあったので、モリソン層の「12州」「名前の由来」は調査時に読めた内容（下の表に引用）にもとづきます。

---

## 1. 直した点（書く途中で直したもの。重要な順。すべて台本に反映済み）

| # | 行 | 直す前（構想・初稿） | 問題 | 直した後 |
|---|---|---|---|---|
| 1 | 31・315 | 「ジュラ紀は2億100万年前から1億4500万年前まで」 | 国際年代層序表 v2026/06 では、白亜紀の始まり（＝ジュラ紀の終わり）は **143.1±0.6 Ma**。v2023 の「~145.0」から変わっている | 「一億四千三百万年前まで」。改訂の話は長さの都合で台本から外した（3節） |
| 2 | 106〜107 | 「プレシオサウルスの胴はなめらかで、尾にうろこ」 | Marx et al. 2025 は逆。"The tail integument was apparently scale-less"、ひれに "small, sub-triangular structures reminiscent of modern reptilian scales"。胴については書いていない | 「尾のまわりの皮ふは、うろこのない、なめらかなもの。ひれには、小さな三角形の、うろこのようなもの」 |
| 3 | 200〜204 | 「2023年の研究：アロサウルスは死骸をあさる動物だった」（PLoS ONE、doi:10.1371/journal.pone.0290459） | そのDOIは同じ著者の別の論文（脂肪の蓄えの研究）。腐肉食のシミュレーションは **Pahl & Ruedas 2021, Ecological Modelling**。しかも2023年に反論（Kane et al. 2023）が出ている | 「2021年の研究は〜十分な食べ物になったはずだと考えました」「2023年には、その計算の前提に疑問を示す研究」 |
| 4 | 73〜78 | 「三畳紀末の絶滅のあと、首の長い巨大な恐竜がすぐに主役になった」 | Pol et al. 2020：竜脚類が大型植物食動物の主役になったのは "towards the end of the Early Jurassic (190-174 Ma)"。南ゴンドワナの火山活動（180〜184 Ma）・気候の乱れ・植物の多様性の低下のあと | 「主役になったのは、ジュラ紀の前半の、終わりごろ」とし、2020年の研究を紹介 |
| 5 | 153 | 「モリソン層では、5種類の首の長い恐竜が同じ場所で一緒に暮らしていた」 | 同じ時・同じ場所で暮らしたことを直接示す一次資料を確認できなかった | 「モリソン層からは〜何種類も見つかっています」 |
| 6 | 14・139 | 「ディプロドクスの全長26メートル」 | NHM は 26m（図鑑）・24〜26m（Q&A）、レプリカの実測は 21.3m（ウェールズ国立博物館）。資料で差がある | 「二十五メートル前後」 |
| 7 | 131 | 「モリソン層の時代は、雨季と乾季のある気候」 | NPS のページは「少なくとも3回のひどい干ばつ」と書くが、同じページに「今より温暖で湿潤」ともあり、「季節的に乾燥」とは言えない | 「ひどい干ばつにも、少なくとも三回みまわれた土地」 |
| 8 | 214〜216 | 「ステゴサウルスの板は体温を調節するためのもの」 | Main et al. 2005：主に種の見分け・見せるため、体温調節は "rarely" | 「かつては〜と考えられていました」「2005年の研究は〜体温の調節に使われたことは、あってもまれだった」 |
| 9 | 50 | 「ジュラ紀には北極にも南極にも氷はなかった」 | Gómez et al. 2016 はプリンスバッキアン期後期に顕著な寒冷期があったとし、氷の有無は議論がある | 「北極や南極に氷があったかどうかは、研究者のあいだで議論が続いています」 |
| 10 | 55〜62 | 「ジュラ紀には、花はなかった」 | 確かな最古の化石は白亜紀前期だが、分子時計はジュラ紀以前を示し（Barba-Montoya et al. 2018）、ジュラ紀の花とする報告（Fu et al. 2018）も議論中。UCMPも "at least as we know them today" と留保 | 「この森にも、まだ、花は見当たりません」＋化石と遺伝子の計算の食い違い、中国の報告の議論 |
| 11 | 113 | 「弟のジョセフ」 | NHM：ジョセフは "her older brother" | 「兄のジョセフ」 |
| 12 | 275 | 「始祖鳥は、最初の鳥」 | NHM は「最初の鳥」とすることに異論がある、と書いている | 「始祖鳥を最初の鳥と呼ぶことにも、異論があります」 |
| 13 | 303〜306 | 「クルサトドンの寿命は7年」 | Panciroli et al. 2024 の「約7歳」は大人1個体の死亡時の年齢 | 「大人は、死んだとき、およそ七歳」「ずっと長く生きることができたらしい」 |
| 14 | 191 | 「アロサウルスは、ジュラ紀で最も大きな肉食恐竜」 | 比べた資料を確認していない | 「ジュラ紀の後半の北アメリカを代表する、大型の肉食恐竜」 |
| 15 | 94 | 「上から見ても下から見ても目立たない色」と言い切る | Lindgren et al. 2018 は "suggests countershading" と控えめ | 「〜目立ちにくい色だったと考えられています」 |
| 16 | 参考文献[33] | Dearc の論文の第一著者を Jakubczak としていた | Crossref で確認すると **Jagielska, N.** | 参考文献を直した |

---

## 2. 行ごとの判定

### タイトル案・冒頭

| 行 | 台本の主張 | 判定 | 根拠・正しい内容 |
|---|---|---|---|
| 3 | 案A：全長25m前後、食べ物を噛まずに丸のみ。陸を歩いた最大の動物 | OK | ディプロドクス 24〜26m（NHM）。"food was ingested without mastication"（Sander et al. 2011 doi:10.1111/j.1469-185X.2010.00137.x）。竜脚形類は "the largest land animals recorded in the history of life"（Apaldetti et al. 2018 doi:10.1038/s41559-018-0599-y）。「最大の動物」は首の長い恐竜の仲間を指す |
| 4 | 案B：鳥は恐竜の子孫。始祖鳥と羽毛の恐竜、1億5000万年前 | OK | 始祖鳥 約1億5000万年前（フィールド博物館の発表、NHM）。"all birds— including the ones alive today— are dinosaurs"（フィールド博物館） |
| 5 | 案C：恐竜の足元で、哺乳類は泳ぎ、滑空し、土を掘っていた | OK | カストロカウダ（Ji et al. 2006）、滑空する仲間（Meng et al. 2017）、地中性のドコフォッソル（Luo et al. 2015）。いずれも「哺乳類とその近い仲間（哺乳形類）」なので、台本本文では「哺乳類に近い仲間」と書いた |
| 14 | 全長25m前後。陸を歩いた動物の中で最も大きな仲間の一つ | 修正済み（#6） | 上記。ディプロドクスは竜脚類の一つ |
| 15 | 食べた植物をほとんど噛まずに飲み込んでいたと考えられる | OK（推定） | "The small head was possible because food was ingested without mastication."（Sander et al. 2011 要旨）。画面「推定」 |
| 17 | 霧の立ちこめる川辺に立つ | OK（演出） | 場面は想像。画面「演出」 |
| 18 | 前回の終わりに、大量絶滅をくぐり抜けた恐竜を見送った | OK | 第4話の台本 266〜303行目（Olsen et al. 2022 doi:10.1126/sciadv.abo6342） |
| 20 | それから五千万年ほど、およそ1億5000万年前、ジュラ紀の後半 | OK | 三畳紀末の絶滅 201.6 Ma（Olsen et al. 2022）→ 150 Ma で約5160万年。後期ジュラ紀は 161.5〜143.1 Ma（国際年代層序表 v2026/06）。モリソン層の年代（約1億5700万〜1億5000万年前、Trujillo & Kowallis 2015）とも重なる |
| 22〜24 | 地面が揺れ、林の向こうから長い首。首の長い巨大な植物食の恐竜 | OK（演出） | 揺れは演出。竜脚類が植物食で首が長いことは一般的事実（Sander et al. 2011） |
| 26〜27 | 恐竜が陸の主役になった時代。巨大化の理由と鳥の起源をたどる | OK | "insulated dinosaurs ... not only survived but also underwent a rapid adaptive radiation and ecological expansion in the Jurassic"（Olsen et al. 2022） |

### 1. 裂けていく大陸

| 行 | 台本の主張 | 判定 | 根拠・正しい内容 |
|---|---|---|---|
| 31 | 2億100万年前〜1億4300万年前 | 修正済み（#1） | 国際年代層序表 v2026/06（https://stratigraphy.org/ICSchart/ChronostratChart2026-06.pdf 、PDFの文字から読み取り）：ヘッタンギアン基底 201.4±0.2 Ma、ベリアシアン基底（白亜紀の始まり）143.1±0.6 Ma。中期の始まり（アーレニアン基底）174.7±0.8、後期の始まり（オックスフォーディアン基底）161.5±1.0、ティトニアン基底 149.2±0.7 |
| 34 | 名前はフランスとスイスの国境のジュラ山脈から。この時代の岩が最初に詳しく調べられた場所 | OK | "Named for the Jura Mountains on the border between France and Switzerland, where rocks of this age were first studied"（UCMP "The Jurassic Period" https://ucmp.berkeley.edu/mesozoic/jurassic/jurassic.php ）。フンボルト（1795年または1799年で資料が分かれる）・ブロンニャール（1829年が多数）の話は入れなかった |
| 36 | 前回まで陸地はほとんどがパンゲア | OK | 第4話と同じ（USGS "This Dynamic Earth"） |
| 37 | パンゲアが2億年前ごろから裂け始め、北のローラシアと南のゴンドワナに分かれた | OK（推定） | "around 200 million years ago, the supercontinent Pangaea began to split apart"、"Pangaea first broke into two large continental landmasses, Laurasia in the northern hemisphere, and Gondwanaland in the southern hemisphere"（USGS https://pubs.usgs.gov/gip/dynamic/historical.html ）。同ページには「225〜200 Ma」という幅のある書き方もあるので「ごろから」。大陸の配置は復元なので画面「推定」 |
| 40 | 北アメリカとアフリカのあいだの裂け目に新しい海の底が広がり始めた。大西洋の始まり | OK（推定） | 中央大西洋の開き始め（Labails et al. 2010 doi:10.1016/j.epsl.2010.06.024）。米国南東部では約2億年前、カナダ沿海部では約1億8500万年前に地溝の段階から海洋底拡大の段階へ（Withjack et al. 1998 doi:10.1306/1d9bc60b-172d-11d7-8645000102c1865d）。「海洋地殻」は「新しい海の底」と言い換えた |
| 43 | 始まりを1億9000万年前ごろとする研究もあれば、もっとあととする見方も | OK（推定） | "the opening of the Central Atlantic Ocean started already during the Late Sinemurian (190 Ma)"、"most of the existing models are based on one or multiple ridge jumps at the Middle Jurassic"（Labails et al. 2010 要旨）。画面「説が分かれている」 |
| 47 | ジュラ紀は全体にいまより暖かかった。極に近い場所の気温がいまより10〜20℃高かった時期がある、という研究 | OK（推定） | 約1億8000万年前（ジュラ紀前期）について "These polar temperatures were ∼ 10–20 °C higher than present along with reduced latitudinal gradients."（Letulle et al. 2022 doi:10.5194/cp-18-435-2022）。海の生き物の殻から推定した値で、「時期がある」「研究もある」とした |
| 50 | 短い寒い時期もあり、極に氷があったかどうかは議論 | 修正済み（#9） | "One of the main controversial themes in palaeoclimatology involves elucidating whether climate during the Jurassic was warmer than the present day"、"The Late Pliensbachian represents an outstanding cooling interval."（Gómez et al. 2016 doi:10.5194/cp-12-1199-2016） |
| 52 | 森はセコイア・イトスギ・マツ・イチイに近い針葉樹、イチョウ、ソテツの仲間、シダ | OK | "Conifers were also present, including close relatives of living redwoods, cypresses, pines, and yews."、シダ・イチョウ・ベネチテス類（cycadeoids）・ソテツ（UCMP 上記）。ベネチテス類はナレーションでは「ソテツの仲間」にまとめた |
| 55 | この森にもまだ花は見当たらない | 修正済み（#10） | "there were no palms or any other flowering plants — at least as we know them today — in the Jurassic"（UCMP 上記）。留保つきなので「見当たりません」 |
| 56 | 花を咲かせる植物の確かな最古の化石は、白亜紀の初めごろの花粉 | OK | "none provide unequivocal evidence of pre-Cretaceous angiosperms"（Herendeen et al. 2017 doi:10.1038/nplants.2017.15）。"a Northern Gondwanan appearance of monosulcate angiosperms in the Valanginian"（Coiro et al. 2019 doi:10.1111/nph.15708）。ヴァランギニアン期は約1億3700万〜1億3300万年前（v2026/06） |
| 59 | 遺伝子からさかのぼる計算では、始まりはジュラ紀かそれより前、という結果が多い | OK（推定） | "We reject a post-Jurassic origin of angiosperms"、"Crown‐angiosperms originated within the late Permian–latest Jurassic interval (256–149 Ma)"（Barba-Montoya et al. 2018 doi:10.1111/nph.15011、PMC本文）。「分子時計」はナレーションでは使わない。画面「説が分かれている」 |
| 62 | 中国でジュラ紀の花とする化石が報告されたが、本当に花かは議論 | OK（推定） | ナンジンガンサス、前期ジュラ紀（Fu et al. 2018 doi:10.7554/eLife.38827、"bona fide angiosperm from the Jurassic" と主張）。同号の解説が "will continue the debate"（Taylor & Li 2018 doi:10.7554/eLife.43421）。Coiro et al. 2019 も、白亜紀より前とされる被子植物は "either represent other plant groups or lack features that might confidently assign them to the angiosperms" とする |

### 2. 主役になった恐竜

| 行 | 台本の主張 | 判定 | 根拠・正しい内容 |
|---|---|---|---|
| 66 | 恐竜は三畳紀末の大量絶滅を生き延びた | OK | 第4話と同じ（Olsen et al. 2022） |
| 68 | 北アメリカ東部で足跡や骨を調べた研究：絶滅から10万年もたたないうちに恐竜が中心の顔ぶれ | OK（解釈は推定） | "Analysis of tetrapod footprints and skeletal material from more than 70 localities in eastern North America"、"Eastern North American dinosaurian diversity reached a stable maximum less than 100,000 years after the boundary, marking the establishment of dinosaur-dominated communities"（Olsen et al. 2002 doi:10.1126/science.1065522 要旨）。同論文は原因を隕石の衝突と推測したが、現在は火山活動が有力（第4話）なので、原因の話は入れなかった |
| 71 | 生き残った恐竜はジュラ紀に急速に種類を増やし広がった | OK | "underwent a rapid adaptive radiation and ecological expansion in the Jurassic"（Olsen et al. 2022） |
| 73 | 首の長い巨大な恐竜が大きな植物食動物の主役になったのは、ジュラ紀の前半の終わりごろ | 修正済み（#4） | "Sauropods ... became the dominant group of large herbivores in terrestrial ecosystems after multiple related lineages became extinct towards the end of the Early Jurassic (190-174 Ma)."（Pol et al. 2020 doi:10.1098/rspb.2020.2310 要旨） |
| 76 | 2020年の研究：アルゼンチンの地層、約1億8400万〜1億8000万年前の南の大陸の大規模な火山活動 | OK | "The terrestrial sedimentary successions of the Cañadón Asfalto Basin in central Patagonia (Argentina)"、"a massive magmatic event impacting southern Gondwana (180-184 Ma)"（同上） |
| 78 | そのあと気候が乱れ植物の種類が減り、首の長い恐竜の親戚の仲間が消え、首の長い恐竜が主役に | OK（推定） | "eusauropod dominance was established after a massive magmatic event ... and coincided with severe perturbations to the climate and a drastic decrease in the floral diversity characterized by the rise of conifers with small scaly leaves"（同上）。消えた "related lineages" は竜脚類以外の竜脚形類なので「首の長い恐竜の親戚にあたる仲間」と言い換えた |

### 3. 海の竜

| 行 | 台本の主張 | 判定 | 根拠・正しい内容 |
|---|---|---|---|
| 84 | 約2億年前、ジュラ紀の初め、いまのイギリス南の海岸は海の中 | OK | アニングの1812年の魚竜（現在のテムノドントサウルス・プラティオドン）は約2億年前、ジュラ紀前期（NHM "Mary Anning's fossils" https://www.nhm.ac.uk/discover/mary-anning-fossils.html ）。ライムレジス（ドーセット） |
| 87〜88 | 薄暗い海、流れるような形の影 | OK（演出） | 場面は想像 |
| 89 | 魚竜＝前回の三畳紀の海で出会った海の爬虫類の仲間 | OK | 第4話の台本 61〜72行目。ジュラ紀の魚竜も同じグループ |
| 91 | 2018年の研究：ドイツで見つかったジュラ紀前半の魚竜の化石の皮ふのあとを調べた | OK | ジュラ紀前期のステノプテリギウス（ドイツ・ホルツマーデン）の軟組織（Lindgren et al. 2018 doi:10.1038/s41586-018-0775-x） |
| 93 | 皮ふの下に厚い脂肪の層、体温を保てた可能性（研究チームの考え） | OK（推定） | "These are underlain by insulating blubber that would have augmented streamlining, buoyancy and homeothermy."（同上 要旨） |
| 94 | 色の粒の並び方から、背中が暗く腹が明るい、目立ちにくい色 | 修正済み（#15） | "Distributional variation of melanophores across the body suggests countershading"（同上）。題名の "crypsis"（目立たない色） |
| 97 | 魚竜は卵ではなく子を産んだ。お腹の中に子が入ったままの化石 | OK | Motani et al. 2014 doi:10.1371/journal.pone.0088640（本文の図に、ステノプテリギウスの標本 SMNS 6293「胎児1体が出産の位置、体内に3体」）。Miedema et al. 2023 doi:10.1186/s12862-023-02110-4 も胎児の向きを多数の標本で検討。「出産の瞬間の化石」は、死後に押し出された可能性が指摘されているので言わなかった |
| 100〜101 | 岩陰に小さな頭、とても長い首、平たい胴から4枚の大きなひれ | OK（演出） | 場面は想像。体のつくりはプレシオサウルスの骨格（NHM） |
| 102 | プレシオサウルス＝首の長い海の爬虫類、首長竜とも呼ばれる。恐竜ではない | OK | 首長竜（長頸竜）は海生爬虫類で、恐竜とは別のグループ（一般的事実）。名前は一度出してすぐ説明 |
| 104 | 首の長さは胴と尾を合わせたほど | OK | "neck ... roughly the same length as its body and tail combined"（NHM "Mary Anning's fossils"。アニングの1823年のプレシオサウルスについて） |
| 106 | 2025年、ドイツで見つかった約1億8300万年前のプレシオサウルスの仲間の化石から皮ふのあと | OK | ドイツ・ポシドニア頁岩のほぼ完全なプレシオサウルス類（Marx et al. 2025 doi:10.1016/j.cub.2025.01.001）。属は Plesiosaurus ではないので「プレシオサウルスの仲間」 |
| 107 | 尾のまわりの皮ふはうろこがなくなめらか。ひれには小さな三角形のうろこのようなもの | 修正済み（#2） | "The tail integument was apparently scale-less and retains identifiable melanosomes, keratinocytes with cell nuclei"、"The flipper integument otherwise integrates small, sub-triangular structures reminiscent of modern reptilian scales."（同上 要旨） |
| 110〜111 | これらの化石を200年あまり前にイギリスの海岸で掘り出した人、メアリー・アニング | OK | 1799〜1847年、ライムレジス（NHM "Mary Anning: the unsung hero" https://www.nhm.ac.uk/discover/mary-anning-unsung-hero.html ） |
| 113 | 1811年に兄のジョセフが奇妙な頭の骨。翌年、十代の初めのメアリーが長さ5mほどの魚竜の骨格を掘り出す | 修正済み（#11） | "In the autumn of 1811, when Mary was 12, Joseph found a strange-looking fossilised skull"、"About a year later, in November 1812, Mary searched for and painstakingly dug the outline of its five-metre-long skeleton"、"her older brother, Joseph"（NHM 上記） |
| 116 | 1823年にプレシオサウルスの全身の骨格を初めて見つけた | OK | "In December 1823, Mary was the first to discover the complete skeleton of a Plesiosaurus."（NHM 上記）。発見は1823年12月10日（ロンドン地質学会の展示ページ） |

### 4. モリソン層の巨人たち

| 行 | 台本の主張 | 判定 | 根拠・正しい内容 |
|---|---|---|---|
| 121 | 約1億5700万〜1億5000万年前、北アメリカの西部 | OK | 再計算した年代は 156.84±0.59 Ma（層の基底）〜149.74±0.64 Ma（Trujillo & Kowallis 2015 doi:10.31711/giw.v2.pp1-8 の表）。"~157-149 Ma"（Whitlock et al. 2018 Geology of the Intermountain West 5:9–22） |
| 124〜125 | 平らな土地、曲がりくねった川、針葉樹とシダの茂み | OK（演出） | 「広く平らな氾濫原」（NPS https://www.nps.gov/dino/learn/nature/morrison-formation.htm ）。植物の配置は想像。画面「演出」 |
| 126 | 川やあふれた水が運んだ泥や砂が、アメリカ西部の12の州にまたがる地層として残る | OK | "Morrison Formation (AZ*,CO*,KS,MT*,NE,NM*,ND*,OK*,SD*,TX,UT*,WY*)"（USGS Geolex https://ngmdb.usgs.gov/Geolex/Units/Morrison_9394.html ）。面積は資料が食い違う（3節）ので言わない |
| 129 | モリソン層。コロラド州のモリソンの町の近くで調べられたことから命名 | OK | "Named from exposures near town of Morrison, Jefferson Co., CO (Eldridge, 1896)."（同上） |
| 131 | 広い平原を川が流れ、ひどい干ばつに少なくとも3回みまわれた | 修正済み（#7） | Brushy Basin 部層は "a large flat floodplain"、化石から "at least three severe droughts"（NPS 上記） |
| 134 | 恐竜の化石が豊富に見つかることで世界的に知られる地層 | OK | "it is the Morrison Formation that contains the majority of the dinosaur fossils found here"（NPS、ダイナソー国定公園）。アロサウルス・ステゴサウルス・ディプロドクスなどの産地（Chure & Loewen 2020、Maidment et al. 2015、Tschopp et al. 2015） |
| 136 | 川岸で巨大な恐竜が首を低く伸ばし、地面近くの植物を食べる | OK（演出） | 場面は想像。地面に近い高さで食べたとする研究（157行目） |
| 138〜139 | ディプロドクス、全長25m前後、大型路線バス2台を並べたより長い | 修正済み（#6） | "Length: 26.0 m"（NHM図鑑 https://www.nhm.ac.uk/discover/dino-directory/diplodocus.html ）、"was 24 to 26 metres long and probably weighed up to around 15 tonnes"（NHM Q&A https://www.nhm.ac.uk/discover/quick-questions/how-big-was-diplodocus-carnegii.html ）。大型路線バス約11m×2＝22m（第4話と同じ比べ方） |
| 143 | ブラキオサウルス、前脚が長く、体の重さの多くを前にかけていた | OK | アメリカの種は胴が長く深く、体重のより多くを前脚にかけていた（Taylor 2009 doi:10.1671/039.029.0309 要旨）。前脚が長いことは同論文の上腕骨 204cm などの記述と一般的な復元による |
| 146 | 体重は約29トンと見積もり | OK（推定） | 本文のモデル推定で 28,688 kg（Taylor 2009）。推定なので画面「推定」 |
| 149〜150 | よく知られた背の高いブラキオサウルスの姿の多くはアフリカの別の恐竜がもと。2009年に別の仲間と結論、ギラファティタン | OK | "These animals must therefore be considered generically separate, and the genus name Giraffatitan Paul 1988 must be used for 'Brachiosaurus' brancai"（Taylor 2009 要旨）。よく知られた復元はベルリンのアフリカの標本にもとづく（同） |
| 153 | アパトサウルス、カマラサウルス、2015年に再び独立した仲間と認められたブロントサウルスなど、首の長い恐竜が何種類も | 修正済み（#5） | "Of particular note is that the famous genus Brontosaurus is considered valid by our quantitative approach."（Tschopp, Mateus & Benson 2015 doi:10.7717/peerj.857）。カマラサウルスとディプロドクスの比較（Button et al. 2014）、アパトサウルス（Whitlock 2011）もモリソン層 |
| 157 | 口先の形や歯の細かい傷から、ディプロドクスやアパトサウルスは地面に近い高さの植物を選ばずに食べた | OK（推定） | "The square snouts, large proportion of pits, and fine subparallel scratches in Apatosaurus, Diplodocus, Nigersaurus, and Rebbachisaurus suggest ground-height nonselective browsing"（Whitlock 2011 doi:10.1371/journal.pone.0018304） |
| 160 | 頭の骨が頑丈なカマラサウルスはディプロドクスより強い力でかめ、硬い植物も食べられた | OK（推定） | "Camarasaurus capable of exerting and accommodating greater bite forces than Diplodocus, permitting consumption of harder food items."（Button, Rayfield & Barrett 2014 doi:10.1098/rspb.2014.2114）。題名は "resource-poor environments" での多様性 |

### 5. 巨人の秘密

| 行 | 台本の主張 | 判定 | 根拠・正しい内容 |
|---|---|---|---|
| 165 | 2011年、ドイツを中心とする研究グループの研究：いくつもの特徴が組み合わさった結果 | OK（推定） | Sander et al. 2011（16人の著者。ドイツの研究グループ「竜脚類の巨大化の生物学」が中心、Biological Reviews 86:117–155）。要旨が複数の特徴の組み合わせを「カスケード」として説明 |
| 168 | 長い首：体を動かさずに広い範囲を食べられ、ほかの動物の届かない葉にも届いた | OK（推定） | 本文 "over a large volume without moving the massive body"、要旨で他の植物食動物の届かない餌にも届いた（同上） |
| 170 | 噛まないので頭を小さく軽くでき、首を長くしても支えられた | OK | "The small head was possible because food was ingested without mastication."。小さな頭と骨の空洞化が長い首を可能にした（同上 要旨） |
| 172 | 鳥と同じように肺につながる空気の袋、骨の中にまで空気の入る空間 | OK（空間は確認、働きは推定） | 鳥型の呼吸系（気嚢）と骨の含気化（pneumaticity）（同上）。「気嚢」はナレーションでは「空気の袋」と言い換えた |
| 173 | 体が軽くなり、呼吸の効率もよくなった | OK（推定） | 呼吸のコストを下げ、比重を下げた（同上 要旨）。体の熱を逃がす働きの可能性は長さの都合で外した |
| 176 | 陸の哺乳類は体が大きいほど産む子が少ない。首の長い恐竜は小さな子を毎年たくさん産み、数が減っても早く取り戻せた | OK（推定） | "Sauropods produced numerous but small offspring each season while land mammals show a negative correlation of reproductive output to body size."（同上 要旨）。個体数の回復が早い点も要旨 |
| 178 | 骨の断面の成長の跡から、とても速く育っていた | OK | 骨の組織学から速い成長（同上、Curry 1999 JVP 19:654–665 doi:10.1080/02724634.1999.10011179） |
| 179 | 大人の大きさまで40年もかからない。最も速い時期は年500kg〜2トン増えた可能性 | OK（推定） | "full size was reached in less than four decades"、成長の最も速い時期は年 500〜2000 kg（Sander et al. 2011 本文）。年齢は骨に残らない成長輪があるので最小値の推定（Griebeler, Klein & Sander 2013 PLoS ONE 8:e67012 doi:10.1371/journal.pone.0067012） |
| 183 | 首を高く持ち上げていたと考える研究と、水平に伸ばして低いところを食べたと考える研究。議論は続く | OK（推定） | "Unless sauropods behaved differently from all extant amniote groups, they must have habitually held their necks extended and their heads flexed."（Taylor, Wedel & Naish 2009 doi:10.4202/app.2009.0007、いまの動物との比較）。"these sauropods were adapted to ground feeding or low browsing"（Stevens & Parrish 1999 doi:10.1126/science.284.5415.798）。NHM図鑑も今もディプロドクスは首を水平に保てたと書いており、決着していない |

### 6. アロサウルスとステゴサウルス

| 行 | 台本の主張 | 判定 | 根拠・正しい内容 |
|---|---|---|---|
| 188〜190 | 平原に狙う者。林の陰から大きな頭の肉食恐竜が二本の脚で | OK（演出） | 場面は想像 |
| 191 | アロサウルス＝ジュラ紀後半の北アメリカを代表する大型の肉食恐竜 | 修正済み（#14） | モリソン層の大型獣脚類（Chure & Loewen 2020 doi:10.7717/peerj.7803）。クリーブランド・ロイド発掘地だけで46頭以上（BLM https://www.blm.gov/node/8171 ）。「最大」とは言わない |
| 193 | 2020年に新しい種類。全長8〜9m、体重1.8トンほど、鋭い歯が80本ほど | OK（大きさは推定） | アロサウルス・ジムマドセニ（Chure & Loewen 2020）。"approximately 26 to 29 feet (8-9 meters) long"、"around 4000 lbs. (1.8 metric tonnes)"、"80 sharp teeth"（ユタ自然史博物館の発表 https://nhmu.utah.edu/press/new-species-allosaurus-discovered-utah ）。種名はナレーションでは出さない |
| 197 | 2001年の研究：頭の骨の強さをコンピューターで調べ、特殊な食べ方の可能性。斧を振り下ろすようなかみつき方と紹介された。反論もある | OK（推定） | "suggests a very specific feeding behaviour"（Rayfield et al. 2001 doi:10.1038/35059070 要旨）。斧のたとえは報道（Scientific American 2001-02-22 "in a manner akin to a person wielding a hatchet" https://www.scientificamerican.com/article/dissecting-a-dinosaurs-bi/ ）なので「紹介されました」とし、研究者の言葉としては書かない。反論：Frazzetta & Kardong 2002 doi:10.1038/416387a |
| 200〜201 | 死骸をあさって暮らしたのではという研究。2021年、当時の世界をコンピューターで再現し、巨大な首の長い恐竜の死骸が十分な食べ物になったはず | 修正済み（#3） | "Given the enormous supply of sauropod carrion, they were under no resource-based selective pressure to overpower prey and may have evolved as terrestrial vulture analogues."（Pahl & Ruedas 2021 doi:10.1016/j.ecolmodel.2021.109706、エージェントベースのシミュレーション） |
| 204 | 2023年、その計算の前提に疑問を示す研究。答えは一つではない | OK（推定） | Kane, Healy & Ruxton 2023 "Was Allosaurus really predominantly a scavenger?" Ecological Modelling 476:110247 doi:10.1016/j.ecolmodel.2022.110247。どちらもシミュレーションで、化石の直接証拠ではない。画面「説が分かれている」 |
| 206〜208 | ステゴサウルス：背中に骨でできた大きな板、尾の先に鋭いとげ | OK | 板は皮骨（Main et al. 2005）。とげ（Mallison 2011 本文、Maidment et al. 2015） |
| 211 | NHMの最も完全に近い骨格は全長5.6m、高さ2.9m、若い大人 | OK | "560 centimetres long and 290 centimetres tall"、"young adult"、ほぼ完全（NHMの発表 https://www.nhm.ac.uk/press-office/press-releases/world_s-most-complete-stegosaurus-goes-on-show.html ）。骨格の記載：Maidment, Brassey & Barrett 2015 doi:10.1371/journal.pone.0138352 |
| 214 | かつては板で体の熱を逃がしたり温めたりすると考えられていた | OK | 体温調節説は Main et al. 2005 が検討した従来説（"facultative thermoregulation"） |
| 216 | 2005年の研究：板の骨の内部を調べ、主な役割は種類の見分けや見せること、体温調節はあってもまれ | 修正済み（#8） | "the variation of dermal armor form in stegosaurs was primarily linked to species individuation and recognition, perhaps secondarily to inter- and intraspecific display, and rarely to facultative thermoregulation."（Main et al. 2005 doi:10.1666/0094-8373(2005)031[0291:TEAFOT]2.0.CO;2）。骨の組織学の研究。ただし近縁種の皮ふ痕の研究（Christiansen & Tschopp 2010 doi:10.1007/s00015-010-0026-0）は「どの説も否定できない」とするので画面「説が分かれている」 |
| 219 | 尾のとげは武器。アロサウルスの尾の骨に、ステゴサウルスのとげが刺さったとみられる穴 | OK（骨は確認、解釈は推定） | アロサウルスの尾椎の棘突起をとげの先が貫いた（Carpenter et al. 2005, The Carnivorous Dinosaurs pp.325–350。内容は Mallison 2011 Palaeontologia Electronica 14(2):10A の本文で確認 https://palaeo-electronica.org/2011_2/255/255.pdf ）。モリソン層のとげ51本のうち約10%の先が折れていた（同） |

### 7. 羽毛の恐竜と最初の鳥

| 行 | 台本の主張 | 判定 | 根拠・正しい内容 |
|---|---|---|---|
| 225 | ジュラ紀の空にはすでに翼竜 | OK | 翼竜は三畳紀後期から（第4話）。ジュラ紀中期の大型翼竜（Jagielska et al. 2022） |
| 228 | 2022年、スカイ島の約1億7000万年前の翼竜の骨格。翼を広げて2.5m超。骨格のよく残ったジュラ紀の翼竜で最大 | OK（翼の幅は推定） | "Its wingspan is estimated at >2.5 m ... making it the largest known Jurassic pterosaur represented by a well-preserved skeleton."（Jagielska et al. 2022 doi:10.1016/j.cub.2022.01.073）。約1億7000万年前・スカイ島・2017年発見（エディンバラ大学の発表 2022-02-22）。名前（ディアルク）はナレーションでは出さない |
| 231〜235 | 恐竜の中から新しい空の住人。約1億6000万年前、いまの中国。枝の上の羽毛の小動物 | OK（場面は演出） | アンキオルニス "lived around 160 million years ago"（NHM図鑑 https://www.nhm.ac.uk/discover/dino-directory/anchiornis.html ）。中国（Hu et al. 2009 doi:10.1038/nature08322）。枝の上の場面は想像 |
| 236〜237 | アンキオルニス＝羽毛に覆われた小さな恐竜。前脚にも後ろ脚にも長い羽根 | OK | "A pre-Archaeopteryx troodontid theropod from China with long feathers on the metatarsus"（Hu et al. 2009 の題名）、"the long limb feathers"（Li et al. 2010） |
| 240〜241 | 2010年の研究：羽毛に残った色の粒から色を復元。体は灰色と黒っぽい色、頭頂は赤茶色、顔に赤茶色の斑点、手足の長い羽根は白く先に黒い模様 | OK（分析は確認、全身の色は推定） | "the body was gray and dark and the face had rufous speckles. The crown was rufous, and the long limb feathers were white with distal black spangles."（Li et al. 2010 doi:10.1126/science.1186290 要旨） |
| 244 | アンキオルニスは始祖鳥より古い | OK | 題名 "A pre-Archaeopteryx ..."（Hu et al. 2009）。年代は資料により1億5100万〜1億6100万年前と幅があるが、どの値でも始祖鳥（約1億5000万年前）より古い |
| 246〜247 | 羽毛は鳥に近い恐竜だけではなかったかも。クリンダドロメウス：シベリア、約1億6800万〜1億6600万年前、二本足の小さな植物食の恐竜 | OK | 鳥盤類（Godefroit et al. 2014 doi:10.1126/science.1253351）。年代はバトニアン期の約1億6800万〜1億6600万年前（Cincotta et al. 2019 doi:10.7717/peerj.6239） |
| 250 | 頭や胸に糸のような羽毛、尾に重なり合ったうろこ | OK | 頭と胸に糸状の構造、尾に重なり合う大きなうろこ（Godefroit et al. 2014。題名 "with both feathers and scales"） |
| 253 | 鳥とは遠い仲間。研究チームは羽毛のようなものが恐竜全体に広く見られた可能性を考える | OK（推定） | "featherlike structures coexisted with scales and were potentially widespread among the entire dinosaur clade"（Godefroit et al. 2014 要旨）。"potentially" なので「可能性」。画面「説が分かれている」 |
| 256 | 約1億5000万年前、いまのドイツの南部 | OK | "Late Jurassic, 149–145 million years ago"（NHM図鑑 https://www.nhm.ac.uk/discover/dino-directory/archaeopteryx.html ）、"lived about 150 million years ago"（フィールド博物館の発表）。ゾルンホーフェンはバイエルン州。NHMの「145」は古い表のジュラ紀の終わりの値で、v2026/06 では 143.1 Ma。台本では「およそ1億5000万年前」だけを使う |
| 259 | 始祖鳥、アーケオプテリクスとも | OK | 名前は一度出してすぐ説明 |
| 260 | ゾルンホーフェンの町の近くの石灰岩の石切り場から化石 | OK | "All are from the limestone quarries near Solnhofen in Germany."（NHM図鑑） |
| 262 | 1861年、まず羽根1枚の化石が報告され、同じ年に骨格の化石も報告 | OK | "The discovery of the first Archaeopteryx fossil in Germany in 1861"、"The first Archaeopteryx fossil ever found was a single feather"、"Later, full skeletons were discovered"（NHM図鑑）。ロンドン標本の発見は1861年に公表、NHMの購入は1862年。羽根1枚が本当に始祖鳥のものかは議論がある（NHM図鑑）が、ナレーションでは触れない |
| 264 | 鳥のような羽根と翼、口に歯、骨の入った長い尾、手にかぎ爪のある指。鳥と恐竜の特徴をあわせ持つ | OK | "Unlike modern birds, however, Archaeopteryx had sharp teeth and a long, bony tail"（NHM図鑑）。羽毛・叉骨と、歯・長い骨の尾・かぎ爪のある手（NHM "What were the first birds like?" https://www.nhm.ac.uk/discover/what-were-the-first-birds-like.html ） |
| 267 | 2025年、シカゴの博物館が、ハトほどのつぶれていない始祖鳥の化石を詳しく調べた結果を発表 | OK | 14番目の標本、ほぼ完全でつぶれていない（O'Connor et al. 2025 doi:10.1038/s41586-025-08912-4）。"the smallest one known, only about the size of a pigeon"（フィールド博物館の発表 2025-05-14 https://www.fieldmuseum.org/about/press/uv-light-and-ct-scans-helped-scientists-unlock-hidden-details ） |
| 269 | 両方の翼の体に近い部分に特別な羽根。鳥に近い恐竜には見られず、飛ぶために生まれたと研究チームは考える | OK（羽根は確認、働きは推定） | "Specialized inner secondary feathers called tertials are observed on both wings. Humeral tertials are absent in non-avian dinosaurs closely related to birds, suggesting that these feathers evolved for flight"（O'Connor et al. 2025 要旨）。「三列風切」はナレーションでは使わない |
| 272 | どれほど上手に飛べたかは議論中。研究チームは地上を歩く時間も長かったとみる | OK（推定） | "spent a lot of its time walking on the ground"（フィールド博物館の発表）。足の裏のふくらみが地上歩行に適した形（O'Connor et al. 2025）。飛ぶ力の議論は NHM も指摘 |
| 275 | 始祖鳥を最初の鳥と呼ぶことにも異論。鳥が肉食恐竜の仲間から生まれたことは広く認められている | 修正済み（#12） | 「最初の鳥」とすることに多くの研究者が異論（NHM "What were the first birds like?"）。"evolving within a group of dinosaurs called theropods"（同）。「獣脚類」は「肉食恐竜の仲間」と言い換えた |
| 277 | 鳥は恐竜の子孫であり、恐竜の一員 | OK | "all birds— including the ones alive today— are dinosaurs."（フィールド博物館の発表） |

### 8. 足元の小さな哺乳類

| 行 | 台本の主張 | 判定 | 根拠・正しい内容 |
|---|---|---|---|
| 282〜284 | 夜の川辺、水面に小さな頭 | OK（演出） | 場面は想像 |
| 285 | カストロカウダ：中国、ジュラ紀の中ごろ、哺乳類に近い仲間 | OK | "A Swimming Mammaliaform from the Middle Jurassic"（Ji et al. 2006 doi:10.1126/science.1123026 の題名）。中国（内モンゴル）。mammaliaform を「哺乳類に近い仲間」と言い換えた |
| 288 | 毛の跡が残り、平たく幅広い、一部うろこの尾。ビーバーの尾に似る。泳ぎが得意だったと考えられる | OK（泳ぎは推定） | "has a broad, flattened, partly scaly tail analogous to that of modern beavers"、毛の確認された哺乳類の系統として最も原始的（同上 要旨） |
| 291 | ジュラ紀後半の中国から、手足のあいだの皮ふの膜で滑空した仲間、モグラのように土を掘った仲間 | OK（暮らし方は推定） | "skin membranes and skeletal features that are adapted for gliding"（Meng et al. 2017 doi:10.1038/nature23476、ジュラ紀後期、中国）。"A new Late Jurassic docodontan shows specializations for a subterranean lifestyle. It is similar to extant subterranean golden moles"（Luo et al. 2015 doi:10.1126/science.1260880、中国）。種名は出さない |
| 294 | 2015年の研究：歯やあごの形の変化を調べ、ジュラ紀の前半〜中ごろに変化がとても速かった | OK（推定） | "Rates of morphological evolution were significantly elevated prior to the Late Jurassic, with a pronounced peak occurring during the Early to Middle Jurassic."（Close et al. 2015 doi:10.1016/j.cub.2015.06.047）。分析は歯とあごなどの形質にもとづく |
| 297 | 恐竜時代の哺乳類は小さく目立たないと思われがちだが、泳ぎ、滑空し、土を掘り、さまざまな暮らしを試した | OK | 285〜294行目の3研究のまとめ。Ji et al. 2006 の題名 "ecomorphological diversification of early mammals" |
| 299〜300 | 2024年、スカイ島から新しい発見。クルサトドン、ジュラ紀の中ごろの哺乳類に近い仲間 | OK | "the Middle Jurassic docodontan Krusatodon"（Panciroli et al. 2024 doi:10.1038/s41586-024-07733-1 要旨）。スカイ島（同チームの先行研究 Panciroli et al. 2021 Palaeontology 65:e12577 doi:10.1111/pala.12577） |
| 303 | 大人と子どもの化石の歯の成長の跡を調べ、大人は死亡時約7歳、子どもは生後7か月〜2年ほど | 修正済み（#13） | "We used synchrotron X-ray micro-computed tomography imaging of cementum growth increments in the teeth"、"The adult was about 7 years and the juvenile 7 to 24 months of age at death"（同上 要旨）。歯のセメント質の成長線を「木の年輪のような成長の跡」と言い換えた |
| 306 | 同じくらいの大きさのいまの小さな哺乳類と比べ、ゆっくり育ち、ずっと長く生きられたらしい | OK（推定） | "this development was prolonged ... as part of a significantly longer maximum lifespan than extant mammals of comparable adult body mass (156 g or less)"（同上）。体重の数字は言わない |
| 309 | ネズミのように速く育ち短い一生を送る暮らし方は、もっとあとの時代に生まれたのかも | OK（推定） | "the fundamental shift to faster growth over a shorter lifespan may not have taken place in mammaliaforms until during or after the Middle Jurassic"（同上）。"may" なので「かもしれません」 |
| 311 | 私たちにつながる仲間は小さいながら多様な姿へ広がっていた | OK（推定） | 上記のまとめ。「私たちにつながる仲間」は哺乳形類全体を指し、それぞれの種が直接の祖先とは言っていない |

### 結び

| 行 | 台本の主張 | 判定 | 根拠・正しい内容 |
|---|---|---|---|
| 315 | 1億4300万年前、ジュラ紀が終わる | 修正済み（#1） | 143.1±0.6 Ma（国際年代層序表 v2026/06） |
| 317 | 裂けていく大陸の上で、恐竜は陸を歩いた中で最も大きな動物に | OK | 竜脚形類は陸の歴史で最大の動物（Apaldetti et al. 2018）、50トンを超える体重（Sander et al. 2011 要旨。ジュラ紀に限った値ではないので数字は言わない） |
| 319 | 羽毛の小さな恐竜が現れ、空へと向かい始めていた | OK | アンキオルニス・始祖鳥（Li et al. 2010、O'Connor et al. 2025）。「向かい始めていた」にとどめた |
| 321 | 足元で小さな哺乳類の仲間がさまざまな暮らし | OK | 8章のまとめ |
| 323〜324 | 次の白亜紀、森に花が咲き広がる。その終わりに空から巨大な岩が落ちる | OK | 被子植物の急な多様化は白亜紀中ごろから（UCMP "Angiosperms: Fossil Record" https://ucmp.berkeley.edu/anthophyta/anthophytafr.html ）。白亜紀末のチクシュルーブ衝突（Schulte et al. 2010 doi:10.1126/science.1177265）。第6話（白亜紀）の内容に合わせて調整してよい |
| 327〜328 | 巨人の足音はもう聞こえない。羽毛の恐竜の子孫が窓の外でさえずる | OK | 鳥は恐竜（フィールド博物館の発表）。表現は演出 |

---

## 3. 調べたが台本に入れなかった数字・話（外す）

### 裏付けが取れなかった、または資料が食い違ったもの
| 内容 | 理由 |
|---|---|
| ブラキオサウルスの高さ（「13m」など）・全長 | フィールド博物館などの公式な数字を確認できなかった。NHM図鑑のギラファティタン「高さ約25m」は一般的な推定と大きく食い違う。体重（約29t、Taylor 2009）だけにした |
| スーパーサウルスの全長「約39〜42m」 | 学会発表の報道のみで査読論文を確認できなかった |
| ステゴサウルスの脳の大きさ（「クルミほど」など） | 確かな数値を確認していない |
| モリソン層の面積「150万km²」 | 「150万平方マイル」とする論文もあり、単位の取り違えとみられる。公的機関の数字を確認できなかった |
| プレシオサウルスの全長「3〜3.5m」 | 博物館や一次資料に数字がなかった（ウィキペディアのみ）。「首が胴と尾を合わせたほど」だけにした |
| 魚竜の胎児つき化石の数（「100体以上」など） | 二次資料のみ |
| 「魚竜の出産の瞬間の化石」 | 死後に腐敗ガスで胎児が押し出された可能性が指摘されている（一次資料は確認できず）。「お腹の中に子どもが入ったままの化石」にとどめた |
| ジュラ紀の哺乳類の「ほとんどが100g未満」「ネズミほど」 | 一次資料で確認できたのは Panciroli et al. 2024 の「156g以下」の比較だけ |
| 滑空する仲間の種名（マイオパタギウム）と「約1億6000万年前」 | 要旨では確認できず、大学の発表などの二次資料のみ。種名と年代は言わず「ジュラ紀の後半の中国」とした |
| 海に進出したワニの仲間（タラットスクス類）のひれ・尾びれ・うろこのない皮ふ | Schwab et al. 2020 PNAS（doi:10.1073/pnas.2002146117）で陸から外洋への移行は確認したが、体のつくりの記述の論文の書誌を照合できなかった。長さの都合もあり章を立てなかった |
| クリーブランド・ロイド発掘地の肉食恐竜の割合（75%超／67%） | BLMのページとパンフレットで数字が違う。長さの都合で発掘地の話ごと外した |
| フンボルトがジュラ紀の地層に名前をつけた年 | 1795年と1799年で資料が分かれ、一次文献を確認できなかった |
| 中央大西洋の開き始めを「約1億7500万〜1億7000万年前」とする具体的な研究 | 論文と数値を特定できなかった。「もっとあとだとする見方もあります」にとどめた |
| 始祖鳥の羽の色（黒） | 今回は一次資料を確認していない。画像の設定では「落ち着いた黒褐色」とし、画面「推定」 |

### 確認はできたが、長さの都合で外したもの（約20分に収めるため）
| 内容 | 出典 |
|---|---|
| ジュラ紀の終わりの年代が、v2023 の約1億4500万年前から 143.1 Ma に改められたこと | 国際年代層序表 v2026/06 |
| 中央大西洋の広がり方は、はじめの約2000万年は年0.8cmほどで、約1億7000万年前に年1.7cmほどに速まった | Labails et al. 2010 |
| ジュラ紀の花は、あったとしても限られた場所の目立たないものだったかもしれない | Coiro et al. 2019 |
| メアリー・アニングの化石がいまもロンドン自然史博物館にあること | NHM、ロンドン地質学会 |
| ロンドン自然史博物館のディプロドクスの複製「ディッピー」（2017年から巡回、2024年にブロンズ像） | NHM |
| 首の長い恐竜が食べる高さや硬さで食べ物を分け合っていた可能性（まとめの一文） | Whitlock 2011、Button et al. 2014 |
| 空気の袋が体の熱を逃がすのにも役立った可能性 | Sander et al. 2011 |
| アロサウルス・ジムマドセニは最も古いアロサウルスで、A. fragilis より少なくとも500万年古い（1億5700万〜1億5200万年前） | ユタ自然史博物館の発表 |
| クリーブランド・ロイド発掘地：1万2000点以上の化石、アロサウルス46頭以上 | BLM |
| ステゴサウルスの近い仲間（ヘスペロサウルス）の板に角質の覆いのあと | Christiansen & Tschopp 2010 |
| スカイ島の翼竜は骨の組織からまだ成長中の若い個体 | Jagielska et al. 2022 |

---

## 4. 画像・図への注意（事実確認から）

### Geminiで描かせるときの注意
- S01・S03・S27・S31（ディプロドクス）：**四本足**、肩より腰が高く、首は水平に近く前へ。頭はとても小さく、口先は四角い。羽毛は描かない。全長25m前後の見た目だが、人や物と並べる大きさ比べはしない（大きさは図 G07）
- S29（ブラキオサウルス）：**前脚が長く肩が高い**、首は斜め上へ。ディプロドクスと同じ体つきにしない。高さの数字は示さない
- S30（背の高い骨格）：アフリカのギラファティタンの骨格が「よく知られた姿」のもと。説明板・ラベル・文字は入れない
- S33（カマラサウルス）：首は短め、頭は箱のように高い。四本足
- S13（ジュラ紀前期の首の長い恐竜）：特定の種にしない。背景は**細かいうろこ状の葉の針葉樹**（Pol et al. 2020 "the rise of conifers with small scaly leaves"）
- S37（卵と子ども）：ジュラ紀の竜脚類の巣はほとんど分かっていないので、画面「演出」。卵の大きさや並び方を事実として示さない
- S40〜S43（アロサウルス）：二本足、前脚の指は3本、頭は細長く目の前の上に低い突起。羽毛なし。ティラノサウルスにしない。**血や傷は描かない**
- S44（ステゴサウルス）：**四本足**、板は2列で互い違い、尾の先にとげ。全長5.6mほど。羽毛なし
- S45（ステゴサウルスの骨格）：NHMの「ソフィー」をまねた展示風景にはしない（特定の博物館の展示に見せない）。ラベルなし
- S47（とげの傷のある骨）：穴のあいた尾椎。とげそのものは刺さったまま描かない（実物は穴だけ）
- S16・S18（魚竜）：ジュラ紀の魚竜は**イルカのような流線形、背びれ、縦の三日月形の尾びれ**（第4話のキンボスポンディルスとは別の姿）。噴気孔は付けない
- S17・S19・S23（魚竜の化石）：S19は「お腹の中に子どもが入った」化石。出産の瞬間として演出しない（画面「確認」はお腹の中の子どもについて）
- S20・S21（プレシオサウルス）：ひれ足4枚、首は胴と尾を合わせたほどの長さ。首を白鳥のようにS字に持ち上げない。**尾はなめらか、ひれに小さな三角形のうろこ状の粒**（Marx et al. 2025）
- S48・S49（翼竜）：膜の翼、長い尾。S49はジュラ紀中期の大型（翼を広げて2.5mほど）。大きなとさかを付けない
- S50・S51（アンキオルニス）：色は Li et al. 2010 のとおり（灰色と黒の体、赤茶色の頭頂と顔の斑点、白に黒い先の長い羽根）。後ろ脚にも長い羽根。口に歯
- S53（クリンダドロメウス）：二本足の小型の植物食。**糸のような羽毛とうろこの両方**。鳥の翼にしない
- S54・S57・S58（始祖鳥）：ハトほど。口に歯（くちばしにしない）、骨の入った長い尾、翼の先にかぎ爪の指。S57は翼の付け根まで羽根が並ぶ（三列風切、O'Connor et al. 2025）。羽の色は推定
- S55（始祖鳥の化石）：ゾルンホーフェンの淡い石灰岩に羽根のあと
- S61（カストロカウダ）：小さく、毛に覆われ、平たく幅広い一部うろこの尾。ビーバーそのものの大きさ・顔にしない
- S62（滑空する仲間）：膜は手足のあいだ。コウモリの翼にしない
- S66（クルサトドン）：手のひらに乗るほどの小動物。ネズミそのものにしない
- S06・S22・S64（現代の景色）、S12（足跡）：人間・建物・看板・文字を入れない
- 景色：針葉樹・シダ・トクサ・イチョウまで。**花・イネ科の草地・ヤシ**はジュラ紀にない。ソテツの仲間はジュラ紀にもあったが、Geminiはヤシと区別できない形で描くので景色には入れない。S68（白亜紀への予告）だけ、ごく小さく地味な花を入れる
- 地球を宇宙から見た画像や、大陸の形が分かる画像は作らない（大陸の分裂は図 G02・G03 で見せる）
- メアリー・アニングの顔や姿は作らない（実在の人物の肖像を作り出さない）

### 図（Pythonで作る。G01〜G16）
- G01（年表）：三畳紀の終わり 2億140万年前 → ジュラ紀（前期・中期・後期）→ 1億4310万年前 白亜紀へ。目盛りに「中期の始まり 約1億7470万年前」「後期の始まり 約1億6150万年前」と、この回の出来事（三畳紀末の大量絶滅 約2億160万年前、首の長い恐竜が主役に 約1億8000万年前ごろ、モリソン層 約1億5700万〜1億5000万年前、始祖鳥 約1億5000万年前）を置く（国際年代層序表 v2026/06、Olsen et al. 2022、Pol et al. 2020、Trujillo & Kowallis 2015）
- G02（大陸の分裂）：第3話・第4話のパンゲアの模式図を流用し、北の「ローラシア」と南の「ゴンドワナ」に分かれる2枚の並び（約2億年前ごろから）。大陸の形は簡略化し、「推定」と表示（USGS）
- G03（大西洋の始まり）：**地図ではなく断面の模式図**。「大陸が裂ける → 裂け目に新しい海の底ができる → 広がる」の3段階。注記「始まりは約1億9000万年前とする研究も、もっと後とする見方も」（Labails et al. 2010）
- G04（花の起源の議論）：年表の横棒に「遺伝子からの計算：2億5600万〜1億4900万年前のどこか（帯）」「確かな最古の化石：白亜紀の初め（約1億3700万〜1億3300万年前の花粉）」「中国のジュラ紀の報告：議論中（？付き）」（Barba-Montoya et al. 2018、Coiro et al. 2019、Fu et al. 2018）
- G05（首の長い恐竜が主役になるまで）：年表に「三畳紀末の大量絶滅 約2億160万年前」「南の大陸の大規模な火山活動 1億8400万〜1億8000万年前」「気候の乱れ・植物の種類の減少」「首の長い恐竜が大型植物食動物の主役に（ジュラ紀前期の終わり）」（Pol et al. 2020）
- G06（モリソン層）：アメリカの地図は描かず、12州の名前（アリゾナ、コロラド、カンザス、モンタナ、ネブラスカ、ニューメキシコ、ノースダコタ、オクラホマ、サウスダコタ、テキサス、ユタ、ワイオミング）を並べた一覧と、年代の帯「約1億5700万〜1億5000万年前」。名前の由来「コロラド州モリソン」（USGS Geolex、Trujillo & Kowallis 2015）
- G07（ディプロドクスの大きさ）：単純な輪郭で「ディプロドクス 全長25m前後（博物館の表記24〜26m）」と「大型路線バス 約11m×2台」の横の長さ比べ
- G08（長い首と小さな頭）：Sander et al. 2011 の図は写さない。「長い首：体を動かさずに広く食べる」「噛まずに飲み込む → 頭が小さく軽い → 首を長くできる」の流れの模式図（1つ目と2つ目の理由）
- G09（成長の速さ）：「大人の大きさまで：40年未満」「最も速い時期：年500kg〜2t」の2つの数字のパネル（Sander et al. 2011。推定）
- G10（首の角度）：同じ首の長い恐竜の輪郭2つ。左「高く持ち上げていた説（2009年）」、右「水平に近かった説（1999年）」。中央に「議論は続いている」（Taylor et al. 2009、Stevens & Parrish 1999）
- G11（板の役割）：左「以前の考え：体温の調節」（薄く表示）、右「2005年の研究：種類の見分け・見せるため（体温調節はあってもまれ）」（Main et al. 2005）
- G12（年代の並び）：横軸に「スカイ島の大型翼竜 約1億7000万年前」「クリンダドロメウス 約1億6800万〜1億6600万年前」「アンキオルニス 約1億6000万年前」「始祖鳥 約1億5000万年前」（Jagielska et al. 2022、Cincotta et al. 2019、NHM）。アンキオルニスの年代には幅があると注記
- G13（鳥と恐竜の特徴）：始祖鳥の輪郭に「鳥の特徴：羽根・翼」「恐竜の特徴：歯・骨の入った長い尾・かぎ爪のある指」のラベル（NHM）
- G14（鳥は恐竜）：単純な系統図。「肉食恐竜の仲間（獣脚類）」の枝の中から「アンキオルニス」「始祖鳥」「いまの鳥」が分かれる。始祖鳥の位置に「最初の鳥かどうかは議論」と注記。鳥盤類（クリンダドロメウス）を別の枝として遠くに置く（NHM、Godefroit et al. 2014）
- G15（哺乳類の多様な暮らし）：3つのアイコン「泳ぐ（カストロカウダ、ジュラ紀中期）」「滑空する（ジュラ紀後期）」「土を掘る（ジュラ紀後期）」と、「形の変化が速かった時期：ジュラ紀前期〜中期」の帯（Ji et al. 2006、Meng et al. 2017、Luo et al. 2015、Close et al. 2015）
- G16（歯の成長の跡）：歯の断面の模式図（成長線）に「大人：死亡時 約7歳」「子ども：生後7か月〜2年」（Panciroli et al. 2024）

## 5. 読みの確認（AivisSpeech、話者ID 1310138976）

台本の全行（143行）を `POST /audio_query?text=…&speaker=1310138976` に通し、返ってきた accent_phrases の moras をつなげて読みを確認した（`{表記|よみ}` はよみの側を送る。narrate.py と同じ処理）。直したもの（台本に反映済み）：

| 行 | 誤った読み | 直した後 |
|---|---|---|
| 78（2か所）・176 | 首の長い恐竜（シュノナガイ） | {首\|くび} |
| 136 | 首を低く（シュオヒクク） | {首\|くび} |
| 168 | 首だけを（シュダケオ） | {首\|くび} |
| 97 | お腹の中に（オハラノウチニ） | {お腹の中\|おなかのなか} |

書く段階で `{表記|よみ}` を入れておいたもの：{魚竜\|ぎょりゅう}（89・91・97・113）、{頭の骨\|あたまのほね}（113・160・197）、{首長竜\|くびながりゅう}（102）、{一・八\|いってんはち}（193）、{五・六\|ごてんろく}・{二・九\|にてんきゅう}（211）、{二・五\|にてんご}（228）、年号（{一八一一年\|せんはっぴゃくじゅういちねん}、{二〇二〇年\|にせんにじゅうねん} など）。

正しく読まれることを確認したもの：生き物の名前（ディプロドクス、ブラキオサウルス、ギラファティタン、アパトサウルス、カマラサウルス、ブロントサウルス、アロサウルス、ステゴサウルス、プレシオサウルス、アンキオルニス、クリンダドロメウス、始祖鳥（シソチョウ）、アーケオプテリクス、カストロカウダ、クルサトドン）、人名（メアリー・アニング、ジョセフ）、地名（ジュラ山脈、パンゲア、ローラシア、ゴンドワナ、モリソン層、コロラド州、ゾルンホーフェン、スカイ島（スカイトウ）、シベリア、アルゼンチン）、白亜紀（ハクアキ）、三畳紀、爬虫類・哺乳類・翼竜・針葉樹・セコイア・イトスギ・イチイ・斑点（ハンテン）・滑空（カックウ）・干ばつ（カンバツ）・兄（アニ）、お腹（94行目、オナカ）、年代の数字（二億百万・一億四千三百万・一億九千万・一億八千四百万・一億五千七百万・一億六千八百万など）、二十五メートル・二十九トン・八十本（ハチジッポン）・五百キログラム（ゴヒャッキログラム）・十二の州・十度から二十度・四枚・七歳・生後七か月。
