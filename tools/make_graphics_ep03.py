# 第3話の図（G01〜G19）をHTMLで作り、Edge（ヘッドレス）で1920x1080のPNGに変換する
# 使い方: python -I tools/make_graphics_ep03.py   （ONLY=G01,G07 のように指定すると、その図だけ作り直す）
# 数値はすべて scripts/ep03_permian.txt のナレーションと factcheck_ep03.md に一致させること（そこに無い数字は足さない）
# 画面下約200pxは字幕用、右上（右から約350px・上から約150px）は信頼度の表示用に空ける
import subprocess, pathlib, html, tempfile, time, os, math, random

ONLY = [x for x in os.environ.get("ONLY", "").split(",") if x]
ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "images" / "ep03"
SRC = OUT / "graphics_src"
SRC.mkdir(parents=True, exist_ok=True)
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

# チャンネルの配色（第1話・第2話と同じ深い海の色）
CSS = """
:root{--bg:#0F1E2B;--bg2:#162B3C;--ink:#E8E4DA;--sub:#93A3B0;--sea:#4F9DB5;--sand:#D9B779;--red:#C8644B;--green:#7FAE8A;--line:#2C4459}
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:1920px;height:1080px;background:radial-gradient(ellipse at 50% 0%,var(--bg2),var(--bg) 70%);color:var(--ink);
 font-family:"Noto Sans JP","Yu Gothic","Meiryo",sans-serif;overflow:hidden}
.wrap{position:absolute;inset:70px 120px 200px}
h1{font-size:56px;font-weight:700;letter-spacing:.03em;margin-bottom:40px;max-width:1420px}
h1 small{display:block;font-size:28px;font-weight:400;color:var(--sub);margin-top:12px}
.src{position:absolute;left:120px;top:26px;font-size:20px;color:var(--sub);max-width:1400px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.sea{color:var(--sea)}.sand{color:var(--sand)}.red{color:var(--red)}.green{color:var(--green)}.sub{color:var(--sub)}
.card{border:2px solid var(--line);border-radius:24px;background:rgba(255,255,255,.03)}
svg text{font-family:"Noto Sans JP","Yu Gothic","Meiryo",sans-serif}
"""

def bottom_is_white(png):
    """Edge がときどき画面の高さを短く取り、下端が白く写る。最下行の明るさで見分ける"""
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(png), "-vf", "crop=iw:1:0:ih-1", "-f", "rawvideo", "-pix_fmt", "gray", "-"],
                       capture_output=True)
    row = r.stdout
    return bool(row) and sum(row) / len(row) > 200

def page(name, body, source="", wrap_style="", src_style=""):
    if ONLY and not any(name.startswith(x) for x in ONLY):
        return
    src = f'<div class="src" style="{src_style}">出典：{html.escape(source)}</div>' if source else ""
    doc = f"""<!doctype html><html lang="ja"><head><meta charset="utf-8"><style>{CSS}</style></head>
<body><div class="wrap" style="{wrap_style}">{body}</div>{src}</body></html>"""
    p = SRC / f"{name}.html"
    p.write_text(doc, encoding="utf-8")
    png = OUT / f"{name}.png"
    if png.exists():
        png.unlink()
    for _ in range(5):
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
            if bottom_is_white(png):
                print("retry（下端が白い）", png.name)
                png.unlink()
                continue
            print("ok", png.name)
            return
    print("FAILED", png.name)

# 人の影（高さ100・幅40の箱に描く。transformで縮尺を合わせる）
HUMAN = ('<circle cx="20" cy="8" r="7.5"/>'
         '<path d="M11 17 H29 Q33 17 33 22 L35 52 H30 L28 28 V97 H22 V60 H18 V97 H12 V28 L10 52 H5 L7 22 Q7 17 11 17 Z"/>')

def human(x, y_feet, h_px, color="var(--sub)"):
    s = h_px / 100
    return f'<g transform="translate({x},{y_feet - h_px}) scale({s})" fill="{color}">{HUMAN}</g>'

def steps_row(items, arrow="→", pic_h=230):
    """横に並ぶ手順のカード（絵 + 見出し + 説明）"""
    cells = ""
    for i, (svg, head, note) in enumerate(items):
        cells += f"""<div class="card" style="flex:1;text-align:center;padding:30px 18px;height:100%">
 <div style="height:{pic_h}px;display:flex;align-items:center;justify-content:center">{svg}</div>
 <div style="font-size:32px;font-weight:700;margin-top:18px;line-height:1.35">{head}</div>
 <div style="font-size:26px;margin-top:12px;line-height:1.45" class="sub">{note}</div></div>"""
        if i < len(items) - 1 and arrow:
            cells += f'<div style="font-size:56px;padding:0 14px;align-self:center" class="sand">{arrow}</div>'
    return cells

def smooth_px(P):
    """画面上の点をなめらかな閉じた曲線にする（Catmull-Rom）"""
    n = len(P)
    d = f"M{P[0][0]:.1f} {P[0][1]:.1f}"
    for i in range(n):
        p0, p1, p2, p3 = P[i - 1], P[i], P[(i + 1) % n], P[(i + 2) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f" C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p2[0]:.1f} {p2[1]:.1f}"
    return d + " Z"

# ---------- 生き物の単純な影 ----------
def dimetro(x, ground, w, color="var(--sand)"):
    """ディメトロドン：横に張り出した脚・長い尾・背骨から伸びた骨が支える帆（向きは左）。幅 w"""
    s = w / 420
    top = lambda t: -78 - 190 * math.sin(math.pi * t) ** 1.3
    spines = "".join(f'<line x1="{95+i*21}" y1="-75" x2="{95+i*21}" y2="{top(i/10):.0f}" stroke="{color}" stroke-width="7" stroke-linecap="round"/>' for i in range(11))
    sail = "M95 -75 " + " ".join(f"L{95+i*21} {top(i/10):.0f}" for i in range(11)) + " L305 -75 Z"
    return f"""<g transform="translate({x},{ground}) scale({s})" fill="{color}">
<path d="{sail}" fill-opacity=".45"/>{spines}
<ellipse cx="205" cy="-58" rx="140" ry="27"/>
<path d="M330 -70 Q390 -60 420 -30 Q370 -42 330 -45 Z"/>
<path d="M80 -78 Q30 -84 0 -64 Q18 -46 85 -44 Z"/>
<path d="M105 -40 L78 -8 L60 -2 L100 -4 L125 -38 Z"/><path d="M285 -40 L318 -8 L336 -2 L298 -4 L262 -38 Z"/></g>"""

def dicyn(x, ground, w, color="var(--sand)"):
    """ディキノドン類：ずんぐりした胴・くちばし・上あごの牙（向きは左）。幅 w"""
    s = w / 300
    return f"""<g transform="translate({x},{ground}) scale({s})" fill="{color}">
<ellipse cx="170" cy="-80" rx="115" ry="62"/>
<path d="M70 -110 Q20 -125 5 -88 Q0 -62 30 -55 Q60 -50 85 -60 Z"/>
<path d="M5 -88 L-12 -76 L6 -68 Z"/>
<path d="M36 -60 L32 -26 L44 -58 Z" fill="var(--ink)"/>
<path d="M90 -40 L80 0 H105 L115 -35 Z"/><path d="M220 -40 L230 0 H255 L250 -38 Z"/>
<path d="M282 -88 L300 -80 L284 -70 Z"/></g>"""

def gorgon(x, ground, w, color="var(--red)"):
    """ゴルゴノプス類：長めの脚・大きな頭・長い牙（向きは左）。幅 w"""
    s = w / 340
    return f"""<g transform="translate({x},{ground}) scale({s})" fill="{color}">
<ellipse cx="180" cy="-120" rx="110" ry="42"/>
<path d="M85 -150 Q30 -165 0 -130 Q5 -105 40 -100 Q70 -96 95 -105 Z"/>
<path d="M28 -104 L24 -66 L40 -102 Z" fill="var(--ink)"/>
<path d="M285 -130 Q320 -120 340 -95 Q310 -108 280 -108 Z"/>
<path d="M105 -95 L95 0 H118 L130 -92 Z"/><path d="M235 -95 L250 0 H272 L262 -95 Z"/></g>"""

# ---------- G01 年表：ペルム紀の位置 ----------
def g01():
    L, R, W = 365, 225, 1680          # 3億6500万年前 → 2億2500万年前（帯の位置を決めるためだけの目盛り）
    x = lambda ma: (L - ma) / (L - R) * W
    car0, per0, tri0 = 358.86, 298.9, 251.902
    def band(a, b, bg, name, big=False):
        return f"""<div style="position:absolute;left:{x(a)}px;top:260px;width:{x(b)-x(a)}px;height:{110 if big else 70}px;margin-top:{-20 if big else 0}px;
 background:{bg};display:flex;align-items:center;justify-content:center;font-size:{48 if big else 34}px;font-weight:{700 if big else 400};
 {'box-shadow:0 0 0 4px var(--sand);border-radius:10px;z-index:2;' if big else ''}">{name}</div>"""
    def tick(ma, txt, color="var(--sub)"):
        return f"""<div style="position:absolute;left:{x(ma)-2}px;top:250px;width:4px;height:150px;background:{color}"></div>
<div style="position:absolute;left:{x(ma)-170}px;top:410px;width:340px;text-align:center;font-size:30px;line-height:1.4;color:{color}">{txt}</div>"""
    def ep(ma_a, ma_b, txt, color):
        c = (x(ma_a) + x(ma_b)) / 2
        return f"""<div style="position:absolute;left:{c-150}px;top:130px;width:300px;text-align:center;font-size:32px;font-weight:700;color:{color}">{txt}</div>
<div style="position:absolute;left:{c-2}px;top:182px;width:4px;height:56px;background:{color}"></div>"""
    body = f"""<h1>ペルム紀はいつ？　<small>石炭紀のすぐあとに続いた時代</small></h1>
<div style="position:relative;height:600px">
 <div style="position:absolute;left:0;top:260px;width:{x(car0)}px;height:70px;background:linear-gradient(90deg,rgba(36,80,106,0),#24506A)"></div>
 {band(car0, per0, "#3E6B4A", "石炭紀")}
 {band(per0, tri0, "#8A4A36", "ペルム紀", True)}
 {band(tri0, R, "#4A4E5A", "三畳紀")}
 {ep(car0, per0, "第2話", "var(--sub)")}
 {ep(per0, tri0, "第3話", "var(--sand)")}
 {tick(per0, "<b>約2億9900万年前</b>", "var(--sand)")}
 {tick(tri0, "<b>約2億5200万年前</b><br><span style='font-size:26px'>地球の歴史で最大の<br>大量絶滅で終わる</span>", "var(--sand)")}
</div>"""
    page("G01_年表", body, "国際年代層序表 v2026/06（International Chronostratigraphic Chart）／ Burgess et al. (2014) PNAS")

# ---------- パンゲアの模式図（G02・G18で共通） ----------
# 「すべてがひとつにつながった陸」を表すだけの単純な形。実際の輪郭ではない（いまの大陸の形も描かない）
PANGAEA = [(200, 80), (350, 46), (520, 56), (680, 88), (810, 140), (770, 205), (650, 232), (545, 268), (610, 312),
           (730, 345), (810, 390), (770, 465), (630, 545), (455, 578), (300, 545), (215, 460), (175, 360), (150, 250), (160, 150)]

def pangaea_svg(extra="", w=1000, h=640, ox=0, oy=10):
    P = [(px + ox, py + oy) for px, py in PANGAEA]
    eq = 300 + oy
    return f"""<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<defs><radialGradient id="sea" cx="50%" cy="45%" r="60%"><stop offset="0" stop-color="#1B4660"/><stop offset="1" stop-color="#14354A"/></radialGradient></defs>
<rect x="0" y="0" width="{w}" height="{h}" rx="30" fill="url(#sea)" stroke="#2C5A73" stroke-width="3"/>
<line x1="0" y1="{eq}" x2="{w}" y2="{eq}" stroke="var(--sand)" stroke-width="3" stroke-dasharray="14 10" opacity=".85"/>
<path d="{smooth_px(P)}" fill="#2F6E8A" stroke="#2F6E8A" stroke-width="26" stroke-linejoin="round"/>
<path d="{smooth_px(P)}" fill="#8A6A46" stroke="#B0906A" stroke-width="3"/>
<text x="{w-24}" y="{eq-14}" font-size="26" fill="var(--sand)" font-weight="700" text-anchor="end">赤道</text>
{extra}</svg>"""

# ---------- G02 パンゲア ----------
def g02():
    lbl = ('<text x="440" y="300" font-size="64" font-weight="700" fill="var(--ink)" text-anchor="middle" '
           'paint-order="stroke" stroke="rgba(15,30,43,.6)" stroke-width="8">パンゲア</text>'
           '<text x="70" y="140" font-size="30" fill="var(--sea)">海</text>')
    body = f"""<h1>ひとつにつながった大陸　<small>ペルム紀のころ、陸地のほとんどがひとつに（模式図）</small></h1>
<div style="display:flex;gap:60px;align-items:flex-start;margin-top:-10px">
 <div style="flex:none">{pangaea_svg(lbl, 960, 630)}</div>
 <div style="padding-top:120px">
  <div style="font-size:34px" class="sub">名前の意味</div>
  <div style="font-size:64px;font-weight:700;margin-top:10px" class="sand">「すべての陸」</div>
  <div style="font-size:30px;margin-top:50px" class="sea">まわりは、ひとつの大きな海</div>
  <div style="font-size:28px;margin-top:40px;line-height:1.6" class="sub">形は研究による復元をもとにした<br>おおまかな模式図<br>（輪郭は正確ではない）</div>
 </div>
</div>"""
    page("G02_パンゲア", body, "U.S. Geological Survey \"This Dynamic Earth: Historical perspective\"")

# ---------- G03 頭の骨の穴 ----------
def g03():
    hole = "fill='#0F1E2B' stroke='var(--sand)' stroke-width='6'"
    dim = f"""<svg width="720" height="400" viewBox="0 0 720 400">
<path d="M40 230 Q90 175 180 150 L420 105 Q560 95 640 150 L650 275 Q600 310 520 305 L300 300 Q140 290 50 262 Z" fill="#B49A70"/>
<path d="M60 255 Q300 265 640 262" stroke="#7E6A4C" stroke-width="5" fill="none"/>
{''.join(f'<path d="M{70+i*40} {250+i*0.6} l10 18 l10 -18 z" fill="var(--ink)"/>' for i in range(2, 13))}
<path d="M95 244 l12 46 l12 -44 z" fill="var(--ink)"/><path d="M135 248 l11 40 l11 -38 z" fill="var(--ink)"/>
<circle cx="400" cy="170" r="42" fill="#0F1E2B"/>
<ellipse cx="540" cy="205" rx="40" ry="52" {hole}/>
<path d="M540 140 V80" stroke="var(--sand)" stroke-width="4"/>
<text x="540" y="66" font-size="30" font-weight="700" fill="var(--sand)" text-anchor="middle">目の後ろの穴</text>
<text x="400" y="179" font-size="26" fill="var(--sub)" text-anchor="middle">目</text>
</svg>"""
    hum = f"""<svg width="640" height="400" viewBox="0 0 640 400">
<ellipse cx="300" cy="175" rx="170" ry="145" fill="#D8CCB4"/>
<path d="M150 170 Q120 230 140 300 Q160 360 230 365 L300 360 Q330 330 330 290 L330 250 Z" fill="#D8CCB4"/>
<circle cx="190" cy="200" r="38" fill="#0F1E2B"/>
<path d="M200 270 H360" stroke="#B8AC94" stroke-width="16" stroke-linecap="round"/>
<path d="M232 238 Q290 222 345 240 Q350 255 345 262 H235 Q228 250 232 238 Z" {hole}/>
<path d="M350 250 H470" stroke="var(--sand)" stroke-width="4"/>
<text x="480" y="242" font-size="30" font-weight="700" fill="var(--sand)">形を変えて</text>
<text x="480" y="282" font-size="30" font-weight="700" fill="var(--sand)">残る穴</text>
<path d="M190 300 h120" stroke="#B8AC94" stroke-width="4"/>
{''.join(f'<rect x="{196+i*18}" y="304" width="12" height="18" rx="3" fill="#F2EDE2"/>' for i in range(6))}
<text x="190" y="208" font-size="24" fill="var(--sub)" text-anchor="middle">目</text>
</svg>"""
    body = f"""<h1>目の後ろの、頭の骨の穴　<small>左右に一つずつ。横から見た頭の骨（形はおおまか）</small></h1>
<div style="display:flex;gap:40px;align-items:flex-end">
 <div style="text-align:center">{dim}<div style="font-size:40px;font-weight:700;margin-top:10px">ディメトロドン</div></div>
 <div style="font-size:80px;padding-bottom:180px" class="sand">→</div>
 <div style="text-align:center">{hum}<div style="font-size:40px;font-weight:700;margin-top:10px">あなた（人）</div></div>
</div>
<div style="font-size:30px;margin-top:26px;text-align:center" class="sub">この穴は、私たち哺乳類につながる仲間のしるし</div>"""
    page("G03_頭の骨の穴", body, "Angielczyk (2009) Evolution: Education and Outreach 2:257")

# ---------- G04 二つの道 ----------
def g04():
    rx, ry = 120, 300          # 根元
    bx = 560                   # 分かれ目
    up, dn = 130, 470
    tw = 900                   # 哺乳類の側の、帆を持つ枝が分かれる位置
    svg = f"""<svg width="1680" height="620" viewBox="0 0 1680 620">
<path d="M{rx+250} {ry} H{bx}" stroke="var(--ink)" stroke-width="8"/>
<path d="M{bx} {ry} C{bx+80} {ry} {bx+60} {up} {bx+160} {up} H1180" stroke="var(--sea)" stroke-width="8" fill="none"/>
<path d="M{bx} {ry} C{bx+80} {ry} {bx+60} {dn} {bx+160} {dn} H1180" stroke="var(--sand)" stroke-width="8" fill="none"/>
<path d="M1170 {up-16} L1200 {up} L1170 {up+16}" fill="var(--sea)"/><path d="M1170 {dn-16} L1200 {dn} L1170 {dn+16}" fill="var(--sand)"/>
<path d="M{tw} {dn} C{tw+40} {dn} {tw+30} {dn-110} {tw+90} {dn-110} H{tw+130}" stroke="var(--sand)" stroke-width="6" fill="none"/>
<circle cx="{tw+136}" cy="{dn-110}" r="10" fill="var(--sand)"/>
{dimetro(tw+160, dn-70, 190)}
<text x="{tw+255}" y="{dn-200}" font-size="30" font-weight="700" fill="var(--sand)" text-anchor="middle">ディメトロドン</text>
<text x="{tw-10}" y="{dn+52}" font-size="26" fill="var(--sub)" text-anchor="middle">帆は、この枝だけに生まれた</text>
<circle cx="{bx}" cy="{ry}" r="14" fill="var(--ink)"/>
<text x="1230" y="{up-6}" font-size="38" font-weight="700" fill="var(--sea)">爬虫類の側</text>
<text x="1230" y="{up+42}" font-size="30" fill="var(--ink)">トカゲ・ワニ・恐竜・鳥</text>
<text x="1230" y="{dn-6}" font-size="38" font-weight="700" fill="var(--sand)">哺乳類の側</text>
<text x="1230" y="{dn+42}" font-size="30" fill="var(--ink)">私たち</text>
</svg>"""
    body = f"""<h1>二つの道　<small>前回の話の続き：殻のある卵を産む動物たちの枝分かれ</small></h1>
<div style="position:relative;margin-top:-30px">{svg}
 <div class="card" style="position:absolute;left:0;top:{ry-70}px;width:{250+rx}px;padding:18px 20px;font-size:30px;font-weight:700;line-height:1.35;text-align:center">殻のある卵を<br>産む動物</div>
</div>
<div style="font-size:28px;margin-top:-10px;line-height:1.5" class="sub">ディメトロドンは私たちにつながる側の仲間。ただし、あなたの直接の祖先に帆があったわけではない</div>"""
    page("G04_二つの道", body, "Angielczyk (2009) Evolution: Education and Outreach 2:257")

# ---------- G05 ディキノドン類の大きさ ----------
def g05():
    gy = 470
    svg = f"""<svg width="1680" height="540" viewBox="0 0 1680 540">
<line x1="40" y1="{gy}" x2="1640" y2="{gy}" stroke="var(--sub)" stroke-width="3"/>
{dicyn(170, gy, 150)}
{dicyn(800, gy, 620)}
<text x="245" y="{gy+56}" font-size="36" font-weight="700" fill="var(--ink)" text-anchor="middle">小さなもの</text>
<text x="1110" y="{gy+56}" font-size="36" font-weight="700" fill="var(--ink)" text-anchor="middle">大きなもの</text>
<text x="245" y="{gy-120}" font-size="34" fill="var(--sand)" text-anchor="middle">マーモットほど</text>
<text x="1110" y="{gy-330}" font-size="40" fill="var(--sand)" text-anchor="middle" font-weight="700">カバやサイほど</text>
</svg>"""
    body = f"""<h1>ディキノドン類の大きさ　<small>くちばしを持ち、植物を食べる仲間。数がとても多かった</small></h1>
<div style="margin-top:-10px">{svg}</div>
<div style="font-size:26px;margin-top:6px" class="sub">姿と大きさはおおまかなイメージ（同じ仲間の、いちばん小さいものと大きいもの）</div>"""
    page("G05_ディキノドン類の大きさ", body, "Angielczyk (2009) Evolution: Education and Outreach 2:257")

# ---------- G06 捕食者の入れ替わり ----------
def g06():
    def pic(kind):
        s = '<svg width="320" height="220" viewBox="0 0 320 220"><line x1="10" y1="200" x2="310" y2="200" stroke="var(--sub)" stroke-width="3"/>'
        if kind == 1:
            s += gorgon(30, 200, 260, "#A65A44")
        elif kind == 2:
            s += gorgon(20, 200, 280, "var(--red)")
            s += '<path d="M250 40 H300" stroke="var(--ink)" stroke-width="5"/><path d="M262 28 L248 40 L262 52" fill="none" stroke="var(--ink)" stroke-width="5"/>'
            s += '<text x="275" y="80" font-size="22" fill="var(--sub)" text-anchor="middle">北から</text>'
        else:
            s += '<g opacity=".25">' + gorgon(30, 200, 260, "var(--sub)") + '</g>'
            s += '<path d="M110 60 L210 160 M210 60 L110 160" stroke="var(--red)" stroke-width="10" stroke-linecap="round"/>'
        return s + "</svg>"
    body = f"""<h1>頂点の捕食者の入れ替わり　<small>ペルム紀の終わり近く、南アフリカ（2023年の研究）</small></h1>
<div style="display:flex;align-items:stretch;height:500px">{steps_row([
        (pic(1), "それまでの<br>大きな捕食者", "ゴルゴノプス類の<br>大きな種類"),
        (pic(2), "北の地域から<br>移ってきた種類", "ライオンほどの大きさ<br>（イノストランケビア）"),
        (pic(3), "その天下も<br>長く続かなかった", "ゴルゴノプス類は<br>絶滅までにいなくなった"),
    ])}</div>
<div style="font-size:32px;margin-top:30px;text-align:center"><span class="sand">短いあいだに次々と入れ替わる</span> ＝ 生き物の世界が大きく揺らいでいたしるし</div>"""
    page("G06_捕食者の入れ替わり", body, "Kammerer et al. (2023) Current Biology 33:2283 ／ ウィットウォーターズランド大学 発表（2023年5月）")

# ---------- G07 絶滅の割合 ----------
def g07():
    scale = 9.6  # 1%あたりのpx
    x0 = 470
    def bar(label, lo, hi, color, note):
        solid = f'<div style="position:absolute;left:0;top:0;height:76px;width:{lo*scale}px;background:{color};border-radius:8px 0 0 8px"></div>'
        rng = "" if hi == lo else f'<div style="position:absolute;left:{lo*scale}px;top:0;height:76px;width:{(hi-lo)*scale}px;background:{color};opacity:.4;border-radius:0 8px 8px 0"></div>'
        return f"""<div style="display:flex;align-items:center;margin:44px 0">
 <div style="width:{x0}px;flex-shrink:0;font-size:34px;line-height:1.3">{label}</div>
 <div style="position:relative;flex-shrink:0;height:76px;width:{hi*scale}px">{solid}{rng}</div>
 <div style="margin-left:26px;font-size:40px;font-weight:700;white-space:nowrap">{note}</div></div>"""
    ticks = "".join(f'<div style="position:absolute;left:{x0+m*scale}px;top:0;font-size:24px;transform:translateX(-50%)" class="sub">{m}%</div>' for m in range(0, 101, 25))
    grid = "".join(f'<div style="position:absolute;left:{x0+m*scale}px;top:40px;width:1px;height:430px;background:var(--line)"></div>' for m in range(0, 101, 25))
    body = f"""<h1>消えた種の割合　<small>どれも推定。見積もりには幅がある</small></h1>
<div style="position:relative">
 <div style="position:relative;height:30px">{ticks}</div>{grid}
 {bar("海の生き物<br><span class='sub' style='font-size:26px'>これまでよく使われた数字</span>", 90, 96, "#8A7F6A", "90〜96%")}
 {bar("海の生き物<br><span class='sub' style='font-size:26px'>2016年の見積もり直し</span>", 81, 81, "var(--sea)", "約81%")}
 {bar("陸の生き物", 75, 75, "var(--sand)", "約4分の3（約75%）")}
</div>
<div style="font-size:28px;margin-top:10px;line-height:1.6" class="sub">2016年の研究：古い数字には、ペルム紀の半ばに起きた別の絶滅の分まで入っていた</div>"""
    page("G07_絶滅の割合", body, "Stanley (2016) PNAS 113:E6325 ／ Burgess & Bowring (2015) Science Advances 1:e1500470")

# ---------- G08 六万年 ----------
def g08():
    sc = 12  # 1000年あたりのpx
    x0 = 80
    ticks = "".join(f'<line x1="{x0+k*sc}" y1="330" x2="{x0+k*sc}" y2="350" stroke="var(--sub)" stroke-width="3"/>'
                    f'<text x="{x0+k*sc}" y="392" font-size="28" fill="var(--sub)" text-anchor="middle">{k//10 if k else 0}{"万年" if k else ""}</text>'
                    for k in range(0, 121, 20))
    svg = f"""<svg width="1680" height="440" viewBox="0 0 1680 440">
<line x1="{x0}" y1="340" x2="{x0+120*sc}" y2="340" stroke="var(--sub)" stroke-width="3"/>{ticks}
<rect x="{x0+12*sc}" y="190" width="{96*sc}" height="100" rx="10" fill="var(--sand)" opacity=".28"/>
<rect x="{x0}" y="210" width="{60*sc}" height="60" rx="8" fill="var(--sand)"/>
<line x1="{x0+12*sc}" y1="150" x2="{x0+108*sc}" y2="150" stroke="var(--sand)" stroke-width="4"/>
<line x1="{x0+12*sc}" y1="136" x2="{x0+12*sc}" y2="164" stroke="var(--sand)" stroke-width="4"/>
<line x1="{x0+108*sc}" y1="136" x2="{x0+108*sc}" y2="164" stroke="var(--sand)" stroke-width="4"/>
<text x="{x0+60*sc}" y="120" font-size="30" fill="var(--sand)" text-anchor="middle">誤差の幅（±約4万8千年）</text>
<text x="{x0+60*sc+24}" y="252" font-size="40" font-weight="700" fill="var(--ink)">およそ6万年</text>
</svg>"""
    body = f"""<h1>海の絶滅にかかった時間　<small>中国・煤山（メイシャン）の地層の火山灰の年代から</small></h1>
<div style="margin-top:0">{svg}</div>
<div style="display:flex;gap:60px;margin-top:20px;font-size:32px;line-height:1.5">
 <div>およそ <b class="sand">6万年</b>（誤差 <b>±約4万8千年</b>）</div>
 <div class="sub">地球の長い歴史から見れば、ほんの一瞬</div>
</div>"""
    page("G08_六万年", body, "Burgess, Bowring & Shen (2014) PNAS 111:3316")

# ---------- G09 陸と海の順番 ----------
def g09():
    sc = 1.0   # 1000年あたりのpx
    x0 = 330
    dur = f"""<svg width="1680" height="180" viewBox="0 0 1680 180">
<text x="0" y="58" font-size="32" fill="var(--sea)" font-weight="700">海</text>
<rect x="{x0}" y="26" width="{60*sc}" height="44" rx="6" fill="var(--sea)"/>
<text x="{x0+60*sc+20}" y="60" font-size="30" fill="var(--ink)">およそ6万年</text>
<text x="0" y="148" font-size="32" fill="var(--sand)" font-weight="700">陸（南アフリカ）</text>
<rect x="{x0}" y="116" width="{1000*sc}" height="44" rx="6" fill="var(--sand)"/>
<text x="{x0+1000*sc+20}" y="150" font-size="30" fill="var(--ink)">およそ100万年</text>
</svg>"""
    ax = 1500
    order = f"""<svg width="1680" height="225" viewBox="0 0 1680 225">
<line x1="60" y1="120" x2="{ax+60}" y2="120" stroke="var(--sub)" stroke-width="3"/>
<path d="M{ax+50} 108 L{ax+72} 120 L{ax+50} 132" fill="var(--sub)"/>
<text x="{ax+60}" y="170" font-size="24" fill="var(--sub)" text-anchor="end">時間 →</text>
<circle cx="560" cy="120" r="16" fill="var(--green)"/>
<text x="560" y="78" font-size="30" fill="var(--green)" font-weight="700" text-anchor="middle">陸の森が崩れる</text>
<circle cx="1200" cy="120" r="16" fill="var(--sea)"/>
<text x="1200" y="78" font-size="30" fill="var(--sea)" font-weight="700" text-anchor="middle">海の絶滅</text>
<path d="M580 170 H1180" stroke="var(--sand)" stroke-width="4"/>
<path d="M580 158 V182 M1180 158 V182" stroke="var(--sand)" stroke-width="4"/>
<text x="880" y="216" font-size="30" fill="var(--sand)" text-anchor="middle">30数万年 早い</text>
</svg>"""
    body = f"""<h1>陸と海、同時だった？　<small>海は短く、陸はもっと長くかかったとする研究がある</small></h1>
<div class="card" style="padding:14px 30px">
 <div style="font-size:28px" class="sub">かかった時間の比べっこ（長さは同じ縮尺）</div>{dur}</div>
<div class="card" style="padding:14px 30px;margin-top:20px">
 <div style="font-size:28px" class="sub">オーストラリアの地層では</div>{order}</div>"""
    page("G09_陸と海の順番", body, "Burgess et al. (2014) PNAS ／ Viglietti et al. (2021) PNAS 118 ／ Fielding et al. (2019) Nature Communications 10:385")

# ---------- G10 溶岩の広さ ----------
def g10():
    unit = 150                     # 日本の面積（約38万km²）の正方形の一辺
    big = unit * math.sqrt(500 / 37.8)
    mid = unit * math.sqrt(160 / 37.8)
    gy = 600
    def sq(x, side, color, op=1, dash=False):
        st = f'stroke="{color}" stroke-width="4"' + (' stroke-dasharray="14 10"' if dash else "")
        return f'<rect x="{x}" y="{gy-side:.0f}" width="{side:.0f}" height="{side:.0f}" fill="{color}" fill-opacity="{op}" {st}/>'
    x1, x2, x3 = 40, 40 + big + 90, 40 + big + 90 + mid + 90
    svg = f"""<svg width="1680" height="620" viewBox="0 0 1680 620">
{sq(x1, big, "var(--red)", .35)}{sq(x2, mid, "var(--red)", .6)}{sq(x3, unit, "var(--sea)", .7)}
<text x="{x1+big/2:.0f}" y="{gy-big/2-10:.0f}" font-size="40" font-weight="700" fill="var(--ink)" text-anchor="middle">最大 約500万km²</text>
<text x="{x1+big/2:.0f}" y="{gy-big/2+44:.0f}" font-size="34" fill="var(--sand)" text-anchor="middle">日本の約13倍</text>
<text x="{x2+mid/2:.0f}" y="{gy-mid-62:.0f}" font-size="28" fill="var(--ink)" text-anchor="middle">絶滅と同じころの部分だけ</text>
<text x="{x2+mid/2:.0f}" y="{gy-mid-22:.0f}" font-size="28" fill="var(--ink)" text-anchor="middle">少なくとも 約160万km²</text>
<text x="{x2+mid/2:.0f}" y="{gy-mid/2+14:.0f}" font-size="32" fill="var(--sand)" text-anchor="middle" font-weight="700">日本の約4倍</text>
<text x="{x3+unit/2:.0f}" y="{gy-unit-58:.0f}" font-size="32" font-weight="700" fill="var(--ink)" text-anchor="middle">日本</text>
<text x="{x3+unit/2:.0f}" y="{gy-unit-20:.0f}" font-size="26" fill="var(--sub)" text-anchor="middle">約38万km²</text>
</svg>"""
    body = f"""<h1>溶岩などが広がった範囲　<small>四角の面積で比べた模式図（実際の形とは違う）</small></h1>
<div style="margin-top:-24px">{svg}</div>"""
    page("G10_溶岩の広さ", body, "Reichow et al. (2009) Earth and Planetary Science Letters 277:9 ほか")

# ---------- G11 噴き出した時期 ----------
def g11():
    r = 210
    cx, cy = 260, 270
    a = 2 * math.pi * 2 / 3
    ex, ey = cx + r * math.sin(a), cy - r * math.cos(a)
    pie = f"""<svg width="540" height="540" viewBox="0 0 540 540">
<circle cx="{cx}" cy="{cy}" r="{r}" fill="#4A4E5A"/>
<path d="M{cx} {cy} L{cx} {cy-r} A{r} {r} 0 1 1 {ex:.1f} {ey:.1f} Z" fill="var(--red)"/>
<text x="{cx+80}" y="{cy+75}" font-size="56" font-weight="700" fill="var(--ink)" text-anchor="middle">3分の2</text>
<text x="{cx-120}" y="{cy-60}" font-size="26" fill="var(--ink)" text-anchor="middle">残り</text>
<text x="{cx}" y="{cy+r+52}" font-size="30" fill="var(--sub)" text-anchor="middle">シベリアの溶岩など全体の量</text>
</svg>"""
    tl = f"""<svg width="1000" height="420" viewBox="0 0 1000 420">
<line x1="20" y1="250" x2="960" y2="250" stroke="var(--sub)" stroke-width="3"/>
<path d="M950 238 L972 250 L950 262" fill="var(--sub)"/>
<text x="960" y="300" font-size="26" fill="var(--sub)" text-anchor="end">時間 →</text>
<rect x="250" y="200" width="460" height="100" rx="10" fill="var(--red)" opacity=".85"/>
<text x="480" y="262" font-size="40" font-weight="700" fill="var(--ink)" text-anchor="middle">およそ30万年</text>
<rect x="560" y="120" width="150" height="40" rx="6" fill="var(--sand)"/>
<text x="635" y="100" font-size="30" fill="var(--sand)" text-anchor="middle" font-weight="700">絶滅</text>
<path d="M560 168 V196 M710 168 V196" stroke="var(--sand)" stroke-width="3" stroke-dasharray="4 4"/>
<text x="405" y="350" font-size="28" fill="var(--ink)" text-anchor="middle">絶滅の前から</text>
<text x="635" y="350" font-size="28" fill="var(--ink)" text-anchor="middle">絶滅のあいだ</text>
</svg>"""
    body = f"""<h1>溶岩が噴き出した時期　<small>年代を細かく測った研究（図の位置はおおまか）</small></h1>
<div style="display:flex;gap:40px;align-items:center;margin-top:-20px">
 <div style="flex:none">{pie}</div>
 <div style="flex:none">{tl}
  <div style="font-size:32px;line-height:1.5;margin-left:20px">溶岩の <b class="red" style="color:#E07A60">3分の2ほど</b>が、<br>絶滅の前から絶滅のあいだの <b class="sand">約30万年</b>で</div></div>
</div>"""
    page("G11_噴き出した時期", body, "Burgess & Bowring (2015) Science Advances 1:e1500470")

# ---------- G12 炭素の記録 ----------
def g12():
    # 模式図：平らな記録 → 急な落ち込み → ゆれが続く（実際のデータではない）
    pts = [(80, 200), (300, 202), (480, 198), (600, 200)]
    rnd = random.Random(4)
    x = 600
    pts += [(640, 330), (670, 400)]
    x = 670
    while x < 1300:
        x += 40
        pts.append((x, 350 + rnd.uniform(-60, 60)))
    pts += [(1360, 300), (1440, 290), (1560, 295)]
    d = "M" + " L".join(f"{px:.0f} {py:.0f}" for px, py in pts)
    svg = f"""<svg width="1680" height="560" viewBox="0 0 1680 560">
<rect x="680" y="60" width="620" height="420" fill="var(--sand)" opacity=".10"/>
<line x1="80" y1="470" x2="1600" y2="470" stroke="var(--sub)" stroke-width="3"/>
<path d="M1590 458 L1612 470 L1590 482" fill="var(--sub)"/>
<text x="1600" y="515" font-size="26" fill="var(--sub)" text-anchor="end">時間 →（新しい地層へ）</text>
<path d="{d}" fill="none" stroke="var(--sea)" stroke-width="7" stroke-linejoin="round"/>
<line x1="680" y1="60" x2="680" y2="470" stroke="var(--red)" stroke-width="4" stroke-dasharray="10 8"/>
<text x="690" y="44" font-size="30" font-weight="700" fill="var(--red)">絶滅の始まり</text>
<text x="300" y="160" font-size="30" fill="var(--ink)" text-anchor="middle">落ち着いた記録</text>
<text x="560" y="300" font-size="30" font-weight="700" fill="var(--sea)" text-anchor="end">直前に急に乱れる</text>
<text x="990" y="250" font-size="32" font-weight="700" fill="var(--sand)" text-anchor="middle">乱れが およそ50万年 続く</text>
</svg>"""
    body = f"""<h1>岩に残る炭素の記録　<small>中国・煤山の地層。線は説明のための模式図（実際のデータではない）</small></h1>
<div style="margin-top:-20px">{svg}</div>
<div style="font-size:28px;margin-top:-10px" class="sub">空気と海に、大量の炭素が加わったしるしと考えられている（原因の部分は推定）</div>"""
    page("G12_炭素の記録", body, "Burgess, Bowring & Shen (2014) PNAS 111:3316")

# ---------- G13 マグマと絶滅の始まり ----------
def g13():
    def section(kind):
        s = '<svg width="620" height="330" viewBox="0 0 620 330">'
        s += '<rect x="0" y="40" width="620" height="290" fill="#3A2F24"/>'
        s += '<rect x="0" y="140" width="620" height="50" fill="#5A4A36"/><rect x="0" y="230" width="620" height="40" fill="#C9C2B0" opacity=".55"/>'
        s += '<rect x="290" y="60" width="40" height="270" fill="var(--red)"/>'
        if kind == 1:
            s += '<path d="M0 40 H620 V20 Q460 6 310 10 Q160 6 0 20 Z" fill="var(--red)"/><path d="M0 26 H620" stroke="#E07A60" stroke-width="3"/>'
        else:
            s += '<rect x="0" y="40" width="620" height="18" fill="#7E5A44"/>'
            s += '<rect x="60" y="176" width="500" height="22" rx="11" fill="var(--red)"/><rect x="40" y="250" width="540" height="20" rx="10" fill="var(--red)"/>'
            for x in (120, 230, 400, 510):
                s += f'<path d="M{x} 130 C{x-14} 90 {x+14} 60 {x} 0" stroke="var(--sub)" stroke-width="6" fill="none" stroke-dasharray="10 8"/>'
        return s + "</svg>"
    body = f"""<h1>マグマが地下に広がった時期　<small>2017年の研究</small></h1>
<div style="display:flex;gap:40px;align-items:stretch;height:560px">
 <div class="card" style="flex:1;padding:24px 30px;text-align:center">
  <div style="font-size:32px;font-weight:700">それまで</div>
  <div style="margin-top:14px">{section(1)}</div>
  <div style="font-size:30px;margin-top:16px;line-height:1.45">溶岩が<b class="red" style="color:#E07A60">地面の上</b>にあふれ出す</div></div>
 <div style="font-size:56px;align-self:center" class="sand">→</div>
 <div class="card" style="flex:1;padding:24px 30px;text-align:center;border-color:var(--sand)">
  <div style="font-size:32px;font-weight:700" class="sand">絶滅の始まりと、ちょうど重なる</div>
  <div style="margin-top:14px">{section(2)}</div>
  <div style="font-size:30px;margin-top:16px;line-height:1.45">マグマが<b class="red" style="color:#E07A60">地下で横に</b>広がり始める<br><span class="sub" style="font-size:24px">生き物の名残を含む岩や岩塩を熱し、ガスが出た（推定）</span></div></div>
</div>"""
    page("G13_マグマと絶滅の始まり", body, "Burgess, Muirhead & Bowring (2017) Nature Communications 8:164 ／ Svensen et al. (2009) EPSL 277:490")

# ---------- G14 三つの変化 ----------
def g14():
    heat = """<svg width="200" height="220" viewBox="0 0 200 220"><rect x="80" y="10" width="40" height="150" rx="20" fill="none" stroke="var(--ink)" stroke-width="6"/>
<rect x="90" y="60" width="20" height="110" fill="var(--red)"/><circle cx="100" cy="180" r="32" fill="var(--red)" stroke="var(--ink)" stroke-width="6"/>
<path d="M140 40 l14 -14 M140 80 h20 M140 120 l14 14" stroke="var(--red)" stroke-width="5"/></svg>"""
    acid = """<svg width="240" height="220" viewBox="0 0 240 220"><rect x="0" y="60" width="240" height="160" fill="#24506A"/>
<path d="M60 170 Q120 80 180 170 Z" fill="#D8CCB4" opacity=".55"/><path d="M80 170 Q120 110 160 170" fill="none" stroke="#D8CCB4" stroke-width="4" stroke-dasharray="8 7"/>
<text x="120" y="45" font-size="34" font-weight="700" fill="var(--sea)" text-anchor="middle">CO₂</text>
<path d="M120 55 V80" stroke="var(--sea)" stroke-width="4"/></svg>"""
    oxy = """<svg width="240" height="220" viewBox="0 0 240 220"><rect x="0" y="40" width="240" height="180" fill="#24506A"/>""" + "".join(
        f'<circle cx="{x}" cy="{y}" r="{r}" fill="none" stroke="var(--sea)" stroke-width="3" opacity="{o}"/>' for x, y, r, o in
        [(60, 90, 16, 1), (170, 130, 12, .6), (110, 180, 10, .35)]) + """
<text x="60" y="97" font-size="16" fill="var(--sea)" text-anchor="middle" font-weight="700">O₂</text></svg>"""
    body = f"""<h1>火山のあと、地球に起きた三つの変化　<small>研究者たちが挙げているもの</small></h1>
<div style="display:flex;align-items:stretch;height:480px;gap:40px">{steps_row([
        (heat, "① 温暖化", "赤道に近い海の表面は<br>約40℃という推定も"),
        (acid, "② 海の酸性化", "殻や骨格を<br>つくりにくくなる"),
        (oxy, "③ 海の酸素不足", "温かい水は<br>酸素を溶かしにくい"),
    ], arrow="")}</div>"""
    page("G14_三つの変化", body, "Sun et al. (2012) Science 338:366 ／ Clarkson et al. (2015) Science 348:229 ／ Penn et al. (2018) Science 362")

# ---------- G15 熱帯と極 ----------
def g15():
    rows = [("極に近い冷たい海（北）", 0.95, "#4F7FA0"), ("熱帯の海（赤道のあたり）", 0.45, "#C8644B"), ("極に近い冷たい海（南）", 0.95, "#4F7FA0")]
    x0, W = 520, 820
    bars = ""
    for i, (lbl, v, c) in enumerate(rows):
        y = 40 + i * 150
        bars += (f'<text x="{x0-30}" y="{y+52}" font-size="32" fill="var(--ink)" text-anchor="end">{lbl}</text>'
                 f'<rect x="{x0}" y="{y+10}" width="{W*v:.0f}" height="64" rx="8" fill="{c}"/>')
    svg = f"""<svg width="1680" height="500" viewBox="0 0 1680 500">
<line x1="{x0}" y1="20" x2="{x0}" y2="440" stroke="var(--sub)" stroke-width="3"/>
{bars}
<text x="{x0+W*0.95+20:.0f}" y="102" font-size="34" font-weight="700" fill="var(--ink)">激しい</text>
<text x="{x0+W*0.45+20:.0f}" y="252" font-size="34" font-weight="700" fill="var(--ink)">比べると弱い</text>
<text x="{x0+W*0.95+20:.0f}" y="402" font-size="34" font-weight="700" fill="var(--ink)">激しい</text>
<text x="{x0}" y="490" font-size="28" fill="var(--sub)">絶滅の激しさ →（模式図。数値ではない）</text>
</svg>"""
    body = f"""<h1>どこの海で絶滅が激しかった？　<small>2018年の研究：熱帯よりも、極に近い冷たい海</small></h1>
<div style="margin-top:-20px">{svg}</div>
<div style="font-size:28px;margin-top:4px" class="sub">冷たくて酸素の多い水に慣れた生き物には、移り住める場所が残らなかったと考えられている</div>"""
    page("G15_熱帯と極", body, "Penn, Deutsch, Payne & Sperling (2018) Science 362:eaat1327")

# ---------- G16 原因の説 ----------
def g16():
    def box(txt, color, w=None):
        ws = "flex:1;"
        return f'<div class="card" style="{ws}padding:16px 22px;text-align:center;font-size:30px;font-weight:700;border-color:{color};line-height:1.35">{txt}</div>'
    arrow = '<div style="font-size:44px;text-align:center;line-height:1" class="sand">↓</div>'
    left = f"""<div class="card" style="flex:1.45;padding:26px 34px;border-color:var(--sand)">
 <div style="font-size:30px;font-weight:700" class="sand">有力な見方</div>
 <div style="display:flex;flex-direction:column;gap:12px;margin-top:16px">
  {box("シベリアの火山活動（引き金）", "var(--red)")}{arrow}
  <div style="display:flex;gap:16px">{box("温暖化", "var(--line)")}{box("海の酸性化", "var(--line)")}{box("海の酸素不足", "var(--line)")}</div>
  {arrow}{box("いくつもの変化が重なり、生き物を追いつめた", "var(--line)")}
 </div></div>"""
    def other(head, note):
        return f"""<div class="card" style="padding:22px 28px">
 <div style="font-size:30px;font-weight:700">{head}</div>
 <div style="font-size:26px;margin-top:10px;line-height:1.5" class="sub">{note}</div></div>"""
    right = f"""<div style="flex:1;display:flex;flex-direction:column;gap:22px">
 <div style="font-size:30px;font-weight:700" class="sub">ほかの説</div>
 {other("紫外線をさえぎる層が壊れた？", "形のゆがんだ花粉が見つかっている")}
 {other("隕石の衝突？", "オーストラリア沖の海の底に、<br>跡かもしれない地形がある。<br>はっきりした証拠はそろっていない")}
</div>"""
    body = f"""<h1>絶滅の原因は？　<small>これで決まり、というわけではない</small></h1>
<div style="display:flex;gap:40px;align-items:stretch;height:520px">{left}{right}</div>"""
    page("G16_原因の説", body, "Burgess & Bowring (2015) ／ Penn et al. (2018) ／ Benca et al. (2018) ／ Becker et al. (2004) Science ／ NASA Astrobiology")

# ---------- G17 化石の七割 ----------
def g17():
    def grid(n, color):
        cells = ""
        for i in range(100):
            r, c = divmod(i, 10)
            fill = color if i < n else "#2C4459"
            cells += f'<circle cx="{22+c*44}" cy="{22+(9-r)*44}" r="17" fill="{fill}"/>'
        return f'<svg width="440" height="440" viewBox="0 0 440 440">{cells}</svg>'
    def col(when, n, color):
        return f"""<div style="text-align:center">
 <div style="font-size:34px;font-weight:700;margin-bottom:18px">{when}</div>{grid(n, color)}
 <div style="font-size:52px;font-weight:700;margin-top:10px;color:{color}">{"約" if n == 70 else ""}{n}%</div></div>"""
    body = f"""<h1>化石の多くがリストロサウルス　<small>南アフリカの、四本足の動物の化石のうちの割合</small></h1>
<div style="display:flex;gap:120px;align-items:flex-start;margin-top:-6px;padding-left:40px">
 {col("絶滅が始まるころ", 54, "#C9A86A")}
 <div style="font-size:72px;align-self:center;padding-bottom:40px" class="sand">→</div>
 {col("絶滅のあと", 70, "var(--sand)")}
 <div style="align-self:center;font-size:28px;line-height:1.7;padding-bottom:40px">
  <div><span style="display:inline-block;width:24px;height:24px;border-radius:50%;background:var(--sand);vertical-align:-3px;margin-right:10px"></span>リストロサウルス</div>
  <div><span style="display:inline-block;width:24px;height:24px;border-radius:50%;background:#2C4459;vertical-align:-3px;margin-right:10px"></span>ほかの動物</div>
  <div class="sub" style="font-size:24px;margin-top:10px">点1つ＝1%</div></div>
</div>"""
    page("G17_化石の七割", body, "Viglietti et al. (2021) PNAS 118:e2017045118")

# ---------- G18 見つかった場所 ----------
def g18():
    spots = [("ロシア", 470, 130, "middle", -34), ("中国", 735, 182, "middle", -34), ("インド", 640, 420, "start", 12),
             ("ザンビア", 455, 395, "start", 12), ("南アフリカ", 420, 455, "end", 12), ("南極", 470, 545, "middle", 52)]
    dots = ""
    for name, x, y, anc, dy in spots:
        tx = x + (26 if anc == "start" else -26 if anc == "end" else 0)
        dots += (f'<circle cx="{x}" cy="{y}" r="18" fill="var(--sand)" stroke="#0F1E2B" stroke-width="4"/>'
                 f'<text x="{tx}" y="{y+dy}" font-size="32" font-weight="700" fill="var(--ink)" text-anchor="{anc}" '
                 f'paint-order="stroke" stroke="rgba(15,30,43,.8)" stroke-width="7" stroke-linejoin="round">{name}</text>')
    body = f"""<h1>リストロサウルスが見つかった場所　<small>ひとつながりの大陸の上に、広く暮らしていた</small></h1>
<div style="display:flex;gap:60px;align-items:flex-start;margin-top:-10px">
 <div style="flex:none">{pangaea_svg(dots, 960, 630)}</div>
 <div style="padding-top:140px;font-size:30px;line-height:1.7">
  <div><span style="display:inline-block;width:28px;height:28px;border-radius:50%;background:var(--sand);vertical-align:-4px;margin-right:12px"></span>化石が見つかった地域</div>
  <div class="sub" style="font-size:28px;margin-top:40px;line-height:1.6">当時の大陸の上での<br>おおまかな位置を示した模式図<br>（輪郭も位置も正確ではない）</div>
 </div>
</div>"""
    page("G18_見つかった場所", body, "Modesto (2020) Frontiers in Earth Science 8:610463")

# ---------- G19 回復の段 ----------
def g19():
    steps = [("植物を食べる生き物", "#5E8A62"), ("それを食べる生き物", "#A0844E"), ("さらに上の捕食者", "#B05A44")]
    blocks = ""
    for i, (txt, c) in enumerate(steps):
        x, y, w = 40 + i * 230, 470 - (i + 1) * 120, 820 - i * 230
        blocks += (f'<rect x="{x}" y="{y}" width="{w}" height="110" rx="10" fill="{c}"/>'
                   f'<text x="{x+30}" y="{y+68}" font-size="34" font-weight="700" fill="var(--ink)">{txt}</text>')
    svg = f"""<svg width="900" height="520" viewBox="0 0 900 520">
<line x1="20" y1="470" x2="880" y2="470" stroke="var(--sub)" stroke-width="3"/>{blocks}
<path d="M20 450 C 0 300 60 160 160 90" stroke="var(--sand)" stroke-width="6" fill="none"/>
<path d="M140 84 L166 86 L156 110" fill="none" stroke="var(--sand)" stroke-width="6"/>
<text x="40" y="510" font-size="26" fill="var(--sub)">下の段から順に、一段ずつ積み上がる</text>
</svg>"""
    def tl(when, txt, color):
        return f"""<div style="display:flex;gap:20px;align-items:flex-start;margin-top:26px">
 <div style="width:22px;height:22px;border-radius:50%;background:{color};margin-top:12px;flex:none"></div>
 <div><div style="font-size:30px;font-weight:700;color:{color}">{when}</div><div style="font-size:28px;line-height:1.45;margin-top:4px">{txt}</div></div></div>"""
    body = f"""<h1>長い回復　<small>絶滅のあと、世界はすぐには元に戻らなかった</small></h1>
<div style="display:flex;gap:50px;align-items:flex-start;margin-top:-10px">
 <div style="flex:none">{svg}</div>
 <div class="card" style="flex:1;padding:20px 32px 30px">
  <div style="font-size:28px" class="sub">絶滅のあと</div>
  {tl("100万〜300万年ほど", "一部の生き物が種類を増やし始める<br><span class='sub' style='font-size:24px'>そのあいだも絶滅は続いた</span>", "var(--sea)")}
  {tl("およそ800万〜900万年", "たくさんの生き物が複雑につながる<br>世界が、しっかり戻る", "var(--sand)")}
 </div>
</div>"""
    page("G19_回復の段", body, "Chen & Benton (2012) Nature Geoscience 5:375")

for f in (g01, g02, g03, g04, g05, g06, g07, g08, g09, g10, g11, g12, g13, g14, g15, g16, g17, g18, g19):
    f()
