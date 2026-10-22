# 第1話の図（G01〜G06）をHTMLで作り、Edge（ヘッドレス）で1920x1080のPNGに変換する
# 使い方: python -I tools/make_graphics_ep01.py   （ONLY=G01,G03 のように指定すると、その図だけ作り直す）
# 数値はすべて scripts/ep01_devon.txt のナレーションと参考文献に一致させること
# 画面下140pxは字幕用、右上は信頼度の表示用に空ける。出典は字幕に隠れないよう左上に置く
import subprocess, pathlib, html, tempfile, time, os

ONLY = [x for x in os.environ.get("ONLY", "").split(",") if x]
ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "images" / "ep01"
SRC = OUT / "graphics_src"
SRC.mkdir(parents=True, exist_ok=True)
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

# チャンネルの配色（深い海の色。研究室の窓のベージュ系と区別する）
CSS = """
:root{--bg:#0F1E2B;--bg2:#162B3C;--ink:#E8E4DA;--sub:#93A3B0;--sea:#4F9DB5;--sand:#D9B779;--red:#C8644B;--green:#7FAE8A;--line:#2C4459}
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:1920px;height:1080px;background:radial-gradient(ellipse at 50% 0%,var(--bg2),var(--bg) 70%);color:var(--ink);
 font-family:"Noto Sans JP","Yu Gothic","Meiryo",sans-serif;overflow:hidden}
.wrap{position:absolute;inset:70px 120px 160px}
h1{font-size:56px;font-weight:700;letter-spacing:.03em;margin-bottom:40px}
h1 small{display:block;font-size:28px;font-weight:400;color:var(--sub);margin-top:12px}
.src{position:absolute;left:120px;top:26px;font-size:20px;color:var(--sub);max-width:1500px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.sea{color:var(--sea)}.sand{color:var(--sand)}.red{color:var(--red)}.green{color:var(--green)}.sub{color:var(--sub)}
"""

def page(name, body, source=""):
    if ONLY and not any(name.startswith(x) for x in ONLY):
        return
    doc = f"""<!doctype html><html lang="ja"><head><meta charset="utf-8"><style>{CSS}</style></head>
<body><div class="wrap">{body}</div>{f'<div class="src">出典：{html.escape(source)}</div>' if source else ''}</body></html>"""
    p = SRC / f"{name}.html"
    p.write_text(doc, encoding="utf-8")
    png = OUT / f"{name}.png"
    if png.exists():
        png.unlink()
    for _ in range(3):
        profile = tempfile.mkdtemp(prefix="kodai_edge_")
        subprocess.run([EDGE, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--user-data-dir={profile}",
                        "--force-device-scale-factor=1", "--window-size=1920,1080", "--virtual-time-budget=3000",
                        f"--screenshot={png}", p.as_uri()],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)
        for _ in range(30):
            if png.exists() and png.stat().st_size > 0:
                break
            time.sleep(0.5)
        if png.exists():
            print("ok", png.name)
            return
    print("FAILED", png.name)

# ---------- G01 年表：デボン紀の位置と第1話の出来事 ----------
def g01():
    # 横軸：デボン紀の後半だけを拡大（3億9200万年前 → 3億5500万年前）
    L, R, W = 392, 355, 1680
    x = lambda ma: (L - ma) / (L - R) * W
    events = [  # (百万年前, 文, 上段か)
        (385, "アーケオプテリスの森<br><span class='sub'>ニューヨーク州</span>", True),
        (380, "ゴーゴーの礁<br><span class='sub'>オーストラリア</span>", False),
        (375, "ティクターリク<br><span class='sub'>カナダ</span>", True),
        (372, "<span class='red'>1度目の大量絶滅</span>", False),
        (360, "ダンクルオステウス<br><span class='sub'>アメリカ・オハイオ州</span>", True),
    ]
    marks = ""
    for ma, txt, up in events:
        top = 150 if up else 420
        line_top, line_h = (300, 80) if up else (380, 30)
        marks += f"""<div style="position:absolute;left:{x(ma)-2}px;top:{line_top}px;width:4px;height:{line_h}px;background:var(--sand)"></div>
<div style="position:absolute;left:{x(ma)-170}px;top:{top}px;width:340px;text-align:center;font-size:30px;line-height:1.35">{txt}<br><span class="sand" style="font-size:26px">{ma//100}億{ma%100}00万年前</span></div>"""
    end = x(358.9)
    body = f"""<h1>デボン紀の後半　<small>デボン紀は約4億2000万年前〜3億5900万年前の「魚の時代」。この図はその後半（3億9000万年前〜）だけを拡大</small></h1>
<div style="position:relative;height:640px">
 <div style="position:absolute;left:0;top:355px;width:{end}px;height:50px;border-radius:25px 0 0 25px;background:linear-gradient(90deg,#24506A,#3E7F99)"></div>
 <div style="position:absolute;left:{end}px;top:355px;width:{W-end}px;height:50px;background:#2A3A46"></div>
 <div style="position:absolute;left:{end-3}px;top:330px;width:6px;height:100px;background:var(--red)"></div>
 <div style="position:absolute;left:{end-200}px;top:560px;width:400px;text-align:center;font-size:30px" class="red">2度目の大量絶滅<br><span style="font-size:26px">3億5900万年前</span></div>
 <div style="position:absolute;left:{end+20}px;top:365px;font-size:24px;white-space:nowrap" class="sub">石炭紀へ</div>
 {marks}
</div>"""
    page("G01_年表", body, "国際年代層序表（International Chronostratigraphic Chart）ほか")

# ---------- G02 かむ力 ----------
def g02():
    body = """<h1>ダンクルオステウスのかむ力　<small>顎の骨の形から計算した値（2006年の研究）</small></h1>
<div style="display:flex;gap:60px;align-items:center;height:620px">
 <div style="flex:1;text-align:center">
  <div style="font-size:34px" class="sub">顎の先</div>
  <div style="font-size:150px;font-weight:700;line-height:1.1" class="sand">4,400<span style="font-size:60px">N以上</span></div>
  <div style="font-size:30px;margin-top:20px">知られている魚で最も強い<br><span class='sub'>上回るのは、とても大きなワニや恐竜くらい</span></div>
 </div>
 <div style="width:2px;height:420px;background:var(--line)"></div>
 <div style="flex:1;font-size:34px;line-height:1.7">
  <div class="red" style="font-weight:700">ただし</div>
  体の長さを <b>約6メートル</b> と考えた計算<br>
  2023年の研究で、体は <b>3.4〜4メートル</b> ほどに<br>見直された<br>
  <span class="sub">→ 実際の値は、もう少し小さかった可能性がある</span>
 </div>
</div>"""
    page("G02_かむ力", body, "Anderson & Westneat (2006) Biology Letters ／ Engelman (2023) Diversity")

# ---------- G03 大きさの見直し ----------
def g03():
    scale = 110  # 1メートルあたりのpx
    def bar(label, lo, hi, color, note):
        return f"""<div style="display:flex;align-items:center;margin:34px 0">
 <div style="width:300px;flex-shrink:0;font-size:32px">{label}</div>
 <div style="position:relative;flex-shrink:0;height:56px;width:{hi*scale}px">
  <div style="position:absolute;left:0;top:0;height:56px;width:{lo*scale}px;background:{color};border-radius:8px 0 0 8px"></div>
  <div style="position:absolute;left:{lo*scale}px;top:0;height:56px;width:{(hi-lo)*scale}px;background:{color};opacity:.35;border-radius:0 8px 8px 0"></div>
 </div>
 <div style="margin-left:24px;font-size:32px;white-space:nowrap">{note}</div></div>"""
    ticks = "".join(f'<div style="position:absolute;left:{300+m*scale}px;top:0;font-size:22px;transform:translateX(-50%)" class="sub">{m}m</div>' for m in range(0, 11, 2))
    body = f"""<h1>ダンクルオステウスの体の長さ　<small>昔の言われ方と、2023年の見直し</small></h1>
<div style="position:relative;height:30px">{ticks}</div>
{bar("昔の言われ方", 6, 10, "#5C6F7D", "6〜10メートル")}
{bar("2023年の見直し", 3.4, 4, "var(--sand)", "3.4〜4メートル")}
{bar("人（参考）", 1.7, 1.7, "var(--sub)", "1.7メートル")}
<div style="font-size:28px;margin-top:30px" class="sub">頭の大きさと、いまの魚・昔の魚の体の比率から推定。研究者のあいだで議論は続いている</div>"""
    page("G03_大きさの見直し", body, "Engelman (2023) Diversity 15(3):318")

# ---------- G04 魚から陸の動物へ ----------
def g04():
    steps = [("ひれの付け根が太い魚", "ひれの中に骨"), ("ティクターリク", "首と、肩・ひじ・手首にあたる骨"),
             ("四本足の動物", "指のある足"), ("のちの陸の動物", "やがて人類へ")]
    cells = ""
    for i, (a, b) in enumerate(steps):
        cells += f"""<div style="flex:1;text-align:center;padding:40px 20px;border:2px solid var(--line);border-radius:24px;background:rgba(255,255,255,.03)">
 <div style="font-size:32px;font-weight:700;white-space:nowrap">{a}</div><div style="font-size:28px;margin-top:16px" class="sub">{b}</div></div>"""
        if i < len(steps) - 1:
            cells += '<div style="font-size:60px;padding:0 18px" class="sand">→</div>'
    body = f"""<h1>水辺に向かった魚たち　<small>一本道ではなく、似た仲間が何度も現れた</small></h1>
<div style="display:flex;align-items:center;height:520px">{cells}</div>
<div style="font-size:28px" class="sub">並びは体のつくりの変化を示したもので、直接の親子関係ではない</div>"""
    page("G04_魚から陸の動物へ", body, "Daeschler, Shubin & Jenkins (2006) Nature ほか")

# ---------- G05 海から酸素が消える仕組み（説の一つ） ----------
def g05():
    steps = ["森が広がり、根が岩を砕く", "土の栄養が川から海へ", "海の小さな藻が爆発的に増える", "藻が死んで沈み、腐る", "海の底の酸素が使い果たされる"]
    rows = ""
    for i, s in enumerate(steps):
        rows += f"""<div style="display:flex;align-items:center;margin:14px 0"><div style="width:64px;height:64px;border-radius:32px;background:{'var(--red)' if i==len(steps)-1 else 'var(--sea)'};display:flex;align-items:center;justify-content:center;font-size:32px;font-weight:700;color:#0F1E2B">{i+1}</div>
<div style="font-size:38px;margin-left:30px">{s}</div></div>"""
        if i < len(steps) - 1:
            rows += '<div style="margin-left:22px;font-size:30px" class="sub">↓</div>'
    body = f"""<h1>海から酸素が消えた理由　<small>有力な説の一つ（ほかに火山の噴火、気候の急な変化などの説もある）</small></h1>
<div style="margin-left:80px">{rows}</div>"""
    page("G05_海から酸素が消える仕組み", body, "Britannica \"Devonian extinctions\" ほか")

# ---------- G06 腕の骨の比較 ----------
def g06():
    def col(title, sub, parts):
        boxes = ""
        for name, w, n, color in parts:
            unit = "".join(f'<div style="width:{w}px;height:46px;border-radius:23px;background:{color};margin:0 6px"></div>' for _ in range(n))
            boxes += f'<div style="display:flex;align-items:center;margin:26px 0"><div style="width:200px;font-size:30px;text-align:right;margin-right:30px">{name}</div><div style="display:flex">{unit}</div></div>'
        return f'<div style="flex:1"><div style="font-size:40px;font-weight:700;text-align:center">{title}</div><div style="font-size:26px;text-align:center;margin-bottom:20px" class="sub">{sub}</div>{boxes}</div>'
    body = f"""<h1>同じ並び方の骨　<small>付け根から：1本 → 2本 → たくさん</small></h1>
<div style="display:flex;gap:80px;align-items:flex-start;height:560px">
 {col("ティクターリクの胸びれ", "3億7500万年前", [("肩〜ひじ", 260, 1, "var(--sand)"), ("ひじ〜手首", 120, 2, "var(--sea)"), ("手首", 50, 4, "var(--green)")])}
 {col("あなたの腕", "いま", [("二の腕", 260, 1, "var(--sand)"), ("ひじ〜手首", 120, 2, "var(--sea)"), ("手首と指", 50, 5, "var(--green)")])}
</div>"""
    page("G06_腕の骨の比較", body, "Daeschler, Shubin & Jenkins (2006) Nature ／ Shubin, Daeschler & Jenkins (2006) Nature")

for f in (g01, g02, g03, g04, g05, g06):
    f()
