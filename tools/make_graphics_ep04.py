# 第4話の図（G01〜G17）をHTMLで作り、Edge（ヘッドレス）で1920x1080のPNGに変換する
# 使い方: python -I tools/make_graphics_ep04.py   （ONLY=G01,G07 のように指定すると、その図だけ作り直す）
# 数値はすべて scripts/ep04_triassic.txt のナレーションと factcheck_ep04.md に一致させること（そこに無い数字は足さない）
# 画面下約200pxは字幕用、右上（右から約350px・上から約150px）は信頼度の表示用に空ける
# 土台は tools/make_graphics_ep03.py（配色・フォント・出典の位置・Edgeでの変換は同じ）
import subprocess, pathlib, html, tempfile, time, os, math

ONLY = [x for x in os.environ.get("ONLY", "").split(",") if x]
ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "images" / "ep04"
SRC = OUT / "graphics_src"
SRC.mkdir(parents=True, exist_ok=True)
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

# チャンネルの配色（第1話〜第3話と同じ深い海の色）
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

LBL = 'paint-order="stroke" stroke="rgba(15,30,43,.85)" stroke-width="7" stroke-linejoin="round"'

# ---------- 生き物の単純な影（どれも向きは左、長さ1000の箱に描いて縮める） ----------
def cymbo(x, yc, L, color="var(--sand)", sy=None):
    """キンボスポンディルス：細長いウナギのような胴・長い口先・背びれなし・小さな尾びれ。頭の骨は前から約1/8.5（2m/17m）"""
    s = L / 1000
    sy = s if sy is None else sy
    return f"""<g transform="translate({x},{yc}) scale({s},{sy})" fill="{color}">
<path d="M0 -2 L60 -8 Q100 -26 130 -32 Q300 -55 480 -48 Q700 -30 900 -10 L955 -30 Q985 -34 1000 -28 L965 0 L1000 18 Q985 24 955 18 L900 10 Q700 30 480 46 Q300 52 130 30 Q100 24 60 8 L0 2 Z"/>
<path d="M190 38 Q215 85 262 96 Q248 62 236 40 Z"/><path d="M520 40 Q540 72 575 80 Q565 55 556 38 Z"/>
<circle cx="96" cy="-12" r="7" fill="#0F1E2B"/></g>"""

def ichthy(x, yc, L, color="var(--sand)", sy=None, dashed=False, jaw=False):
    """大型の魚竜（体の形は近い仲間からの想像）。dashed=True で輪郭だけ点線、jaw=True で下あごだけ塗る"""
    s = L / 1000
    sy = s if sy is None else sy
    body = ("M0 0 Q40 -6 120 -14 Q170 -60 300 -80 Q480 -95 640 -60 Q780 -30 850 -12 L930 -90 Q950 -95 955 -85 L905 0 "
            "L955 85 Q950 95 930 90 L850 12 Q780 30 640 60 Q480 95 300 80 Q170 60 120 14 Q40 6 0 0 Z")
    fins = "M260 70 Q290 120 345 128 Q330 95 320 66 Z M560 58 Q585 98 625 104 Q612 78 602 54 Z"
    if dashed:
        st = f'fill="{color}" fill-opacity=".18" stroke="{color}" stroke-width="{3/ s:.1f}" stroke-dasharray="{14/s:.1f} {10/s:.1f}"'
        g = f'<path d="{body}" {st}/><path d="{fins}" {st}/>'
    else:
        g = f'<path d="{body}" fill="{color}"/><path d="{fins}" fill="{color}"/>'
    if jaw:
        g += '<path d="M2 2 Q40 8 120 18 Q170 34 250 44 L250 60 Q160 52 110 30 Q40 14 2 5 Z" fill="var(--sand)"/>'
    g += '<circle cx="150" cy="-22" r="10" fill="#0F1E2B"/>' if not dashed else f'<circle cx="150" cy="-22" r="10" fill="{color}" fill-opacity=".6"/>'
    return f'<g transform="translate({x},{yc}) scale({s},{sy})">{g}</g>'

def whale(x, yc, L, color="#7E8E9A", sy=None):
    """シロナガスクジラ：横から見た単純な形（尾びれは横向きなので細く見える）"""
    s = L / 1000
    sy = s if sy is None else sy
    return f"""<g transform="translate({x},{yc}) scale({s},{sy})" fill="{color}">
<path d="M0 8 Q8 -38 120 -56 Q400 -84 650 -52 Q800 -30 960 -8 L1000 -12 L1000 12 L960 8 Q800 28 650 50 Q400 76 150 54 Q30 44 0 8 Z"/>
<path d="M760 -38 L790 -62 L805 -34 Z"/><path d="M230 46 Q270 100 322 106 Q302 74 284 48 Z"/>
<circle cx="140" cy="6" r="8" fill="#0F1E2B"/></g>"""

# ---------- G01 年表 ----------
def g01():
    L, R, W, x0 = 262, 192, 1600, 40           # 2億6200万年前 → 1億9200万年前（帯の位置を決めるためだけの目盛り）
    x = lambda ma: x0 + (L - ma) / (L - R) * W
    tri0, jur0 = 251.902, 201.4
    by, bh = 250, 100
    def tick(ma, y1, y2, color):
        return f'<line x1="{x(ma):.0f}" y1="{y1}" x2="{x(ma):.0f}" y2="{y2}" stroke="{color}" stroke-width="4"/>'
    svg = f"""<svg width="1680" height="640" viewBox="0 0 1680 640">
<defs><linearGradient id="pm" x1="0" x2="1"><stop offset="0" stop-color="#8A4A36" stop-opacity="0"/><stop offset="1" stop-color="#8A4A36"/></linearGradient></defs>
<rect x="{x0}" y="{by}" width="{x(tri0)-x0:.0f}" height="{bh}" fill="url(#pm)"/>
<rect x="{x(tri0):.0f}" y="{by-14}" width="{x(jur0)-x(tri0):.0f}" height="{bh+28}" rx="10" fill="#4A6A5A" stroke="var(--sand)" stroke-width="4"/>
<rect x="{x(jur0):.0f}" y="{by}" width="{x0+W-x(jur0):.0f}" height="{bh}" fill="#3E5468"/>
<text x="{(x0+x(tri0))/2+30:.0f}" y="{by+62}" font-size="32" fill="var(--ink)" text-anchor="middle">ペルム紀</text>
<text x="{x(215):.0f}" y="{by+68}" font-size="48" font-weight="700" fill="var(--ink)" text-anchor="middle">三畳紀（今回）</text>
<text x="{(x(jur0)+x0+W)/2:.0f}" y="{by+62}" font-size="32" fill="var(--ink)" text-anchor="middle">ジュラ紀</text>
<rect x="{x(234):.0f}" y="{by-14}" width="{x(232)-x(234):.0f}" height="{bh+28}" fill="var(--sea)" opacity=".75"/>
{tick(tri0, 110, by+bh+14, "var(--sand)")}
<text x="{x(tri0):.0f}" y="62" font-size="32" font-weight="700" fill="var(--sand)" text-anchor="middle">約2億5200万年前</text>
<text x="{x(tri0):.0f}" y="100" font-size="26" fill="var(--sand)" text-anchor="middle">前回の大量絶滅のすぐあと</text>
<line x1="{x(233):.0f}" y1="{by-14}" x2="{x(233):.0f}" y2="150" stroke="var(--sea)" stroke-width="4"/>
<text x="{x(233)-14:.0f}" y="122" font-size="32" font-weight="700" fill="var(--sea)">雨の時代</text>
<text x="{x(233)+150:.0f}" y="122" font-size="28" fill="var(--sea)">2億3400万〜2億3200万年前</text>
{tick(237, by+bh+14, 420, "var(--ink)")}
<text x="{x(237)+14:.0f}" y="452" font-size="30" font-weight="700" fill="var(--ink)" text-anchor="end">約2億3700万年前</text>
<text x="{x(237)+14:.0f}" y="490" font-size="26" fill="var(--sub)" text-anchor="end">三畳紀の後半の始まり（カーニアン期）</text>
{tick(230, by+bh+14, 420, "var(--green)")}
<text x="{x(230)-14:.0f}" y="452" font-size="30" font-weight="700" fill="var(--green)">約2億3000万年前</text>
<text x="{x(230)-14:.0f}" y="490" font-size="26" fill="var(--green)">最も古い恐竜たち</text>
{tick(jur0, 110, by+bh+14, "var(--red)")}
<text x="{x(jur0):.0f}" y="62" font-size="32" font-weight="700" fill="var(--red)" text-anchor="middle" style="fill:#E07A60">約2億100万年前</text>
<text x="{x(jur0):.0f}" y="100" font-size="26" fill="#E07A60" text-anchor="middle">三畳紀の終わりの大量絶滅</text>
</svg>"""
    body = f"""<h1>三畳紀はいつ？　<small>地球の歴史で最大とされる大量絶滅の、すぐあとに始まった時代</small></h1>
<div style="margin-top:-30px">{svg}</div>"""
    page("G01_年表", body, "国際年代層序表 v2026/06（International Chronostratigraphic Chart）／ Dal Corso et al. (2020) Science Advances ／ Martinez et al. (2011) Science")

# ---------- パンゲアの模式図（第3話 G02・G18 と同じ絵） ----------
# 「すべてがひとつにつながった陸」を表すだけの単純な形。実際の輪郭ではない（いまの大陸の形も描かない）
PANGAEA = [(200, 80), (350, 46), (520, 56), (680, 88), (810, 140), (770, 205), (650, 232), (545, 268), (610, 312),
           (730, 345), (810, 390), (770, 465), (630, 545), (455, 578), (300, 545), (215, 460), (175, 360), (150, 250), (160, 150)]

def pangaea_svg(extra="", w=1000, h=640, ox=0, oy=10, under=""):
    P = [(px + ox, py + oy) for px, py in PANGAEA]
    eq = 300 + oy
    return f"""<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<defs><radialGradient id="sea" cx="50%" cy="45%" r="60%"><stop offset="0" stop-color="#1B4660"/><stop offset="1" stop-color="#14354A"/></radialGradient>
<clipPath id="land"><path d="{smooth_px(P)}"/></clipPath></defs>
<rect x="0" y="0" width="{w}" height="{h}" rx="30" fill="url(#sea)" stroke="#2C5A73" stroke-width="3"/>
<line x1="0" y1="{eq}" x2="{w}" y2="{eq}" stroke="var(--sand)" stroke-width="3" stroke-dasharray="14 10" opacity=".85"/>
<path d="{smooth_px(P)}" fill="#2F6E8A" stroke="#2F6E8A" stroke-width="26" stroke-linejoin="round"/>
<path d="{smooth_px(P)}" fill="#8A6A46" stroke="#B0906A" stroke-width="3"/>
<g clip-path="url(#land)">{under}</g>
<text x="{w-24}" y="{eq-14}" font-size="26" fill="var(--sand)" font-weight="700" text-anchor="end">赤道</text>
{extra}</svg>"""

# ---------- G02 パンゲア ----------
def g02():
    lbl = ('<text x="440" y="300" font-size="64" font-weight="700" fill="var(--ink)" text-anchor="middle" '
           'paint-order="stroke" stroke="rgba(15,30,43,.6)" stroke-width="8">パンゲア</text>'
           '<text x="70" y="140" font-size="30" fill="var(--sea)">海</text>')
    body = f"""<h1>ひとつにつながった大陸　<small>三畳紀も、前回と同じく陸地のほとんどがひとつに（模式図）</small></h1>
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

# ---------- G03 回復の年月 ----------
def g03():
    sc = 140          # 100万年あたりのpx
    x0 = 220
    svg = f"""<svg width="1680" height="420" viewBox="0 0 1680 420">
<circle cx="{x0-10}" cy="200" r="34" fill="var(--red)"/>
<path d="M{x0-26} 184 L{x0+6} 216 M{x0+6} 184 L{x0-26} 216" stroke="var(--ink)" stroke-width="7" stroke-linecap="round"/>
<text x="{x0-10}" y="290" font-size="34" font-weight="700" fill="#E07A60" text-anchor="middle">大量絶滅</text>
<text x="{x0-10}" y="330" font-size="26" fill="var(--sub)" text-anchor="middle">ペルム紀の終わり</text>
<rect x="{x0+40}" y="170" width="{8*sc}" height="60" rx="8" fill="var(--sand)"/>
<rect x="{x0+40+8*sc}" y="170" width="{1*sc}" height="60" rx="0" fill="var(--sand)" opacity=".4"/>
<text x="{x0+40+4.5*sc:.0f}" y="140" font-size="40" font-weight="700" fill="var(--ink)" text-anchor="middle">およそ800万〜900万年</text>
<text x="{x0+40+8.5*sc:.0f}" y="270" font-size="24" fill="var(--sub)" text-anchor="middle">見積もりの幅</text>
<circle cx="{x0+40+9*sc+50}" cy="200" r="34" fill="var(--green)"/>
<path d="M{x0+40+9*sc+34} 200 l12 13 l22 -26" stroke="#0F1E2B" stroke-width="7" fill="none" stroke-linecap="round"/>
</svg>"""
    body = f"""<h1>生き物の世界が戻るまで　<small>絶滅のあと、すぐには元に戻らなかった</small></h1>
<div style="margin-top:0">{svg}</div>
<div style="display:flex;justify-content:flex-end;margin-top:-90px">
 <div style="font-size:32px;font-weight:700;line-height:1.5;text-align:right" class="green">食べる・食べられるで<br>たくさんの生き物がつながる世界が<br>しっかり戻る</div></div>"""
    page("G03_回復の年月", body, "Chen & Benton (2012) Nature Geoscience 5:375")

# ---------- G04 魚竜の巨大化 ----------
def g04():
    gy = 470                    # 地面（人が立つ線）
    bx, L = 560, 1050           # キンボスポンディルスの左端と長さ（17m）
    sk = L * 2 / 17             # 頭の骨 2m
    m = L / 17                  # 1mあたりのpx
    svg = f"""<svg width="1680" height="560" viewBox="0 0 1680 560">
{cymbo(40, 300, 220, "#B8A27C")}
<text x="150" y="400" font-size="34" font-weight="700" fill="var(--ink)" text-anchor="middle">最初の魚竜</text>
<text x="150" y="438" font-size="24" fill="var(--sub)" text-anchor="middle">（大きさはおおまか）</text>
<path d="M300 300 H500" stroke="var(--sand)" stroke-width="6"/><path d="M490 284 L516 300 L490 316" fill="var(--sand)"/>
<text x="400" y="262" font-size="30" font-weight="700" fill="var(--sand)" text-anchor="middle">わずか</text>
<text x="400" y="358" font-size="34" font-weight="700" fill="var(--sand)" text-anchor="middle">約300万年</text>
{cymbo(bx, 300, L, "var(--sand)")}
<line x1="{bx}" y1="150" x2="{bx+L}" y2="150" stroke="var(--ink)" stroke-width="4"/>
<path d="M{bx} 136 V164 M{bx+L} 136 V164" stroke="var(--ink)" stroke-width="4"/>
<text x="{bx+L/2:.0f}" y="128" font-size="40" font-weight="700" fill="var(--ink)" text-anchor="middle">全長 17m超（推定）</text>
<line x1="{bx}" y1="226" x2="{bx+sk:.0f}" y2="226" stroke="var(--sea)" stroke-width="4"/>
<path d="M{bx} 214 V238 M{bx+sk:.0f} 214 V238" stroke="var(--sea)" stroke-width="4"/>
<text x="{bx}" y="206" font-size="28" font-weight="700" fill="var(--sea)">頭の骨 2m</text>
<line x1="{bx-20}" y1="{gy}" x2="{bx+L}" y2="{gy}" stroke="var(--sub)" stroke-width="2" stroke-dasharray="8 8" opacity=".6"/>
{human(bx+40, gy, 1.7*m)}
<text x="{bx+60+30}" y="{gy-20}" font-size="26" fill="var(--sub)">人</text>
<text x="{bx+L/2:.0f}" y="{gy+60}" font-size="34" font-weight="700" fill="var(--ink)" text-anchor="middle">キンボスポンディルス</text>
</svg>"""
    body = f"""<h1>最初の巨大な生き物　<small>約2億4600万年前、いまのネバダ州のあたりの海（2021年に名前がつけられた）</small></h1>
<div style="margin-top:-24px">{svg}</div>
<div style="font-size:26px;margin-top:-6px" class="sub">体の形はおおまか。研究チームは、陸と海をあわせて地球で最初の巨大な生き物とみている</div>"""
    page("G04_魚竜の巨大化", body, "Sander et al. (2021) Science 374:eabf5787 ／ ロサンゼルス郡立自然史博物館 発表 \"Earth's First Giant\"")

# ---------- G05 二つの道 ----------
def g05():
    rx, ry = 410, 320          # 根元（カードの右端）
    bx = 520                   # 分かれ目
    up, dn = 150, 470
    C, D = "var(--sand)", "var(--sea)"
    def tip(x, y, color):
        return f'<circle cx="{x}" cy="{y}" r="11" fill="{color}"/>'
    def br(x1, y1, x2, y2, color, w=7):
        return f'<path d="M{x1} {y1} C{x1+60} {y1} {x1+40} {y2} {x1+110} {y2} H{x2}" stroke="{color}" stroke-width="{w}" fill="none"/>'
    svg = f"""<svg width="1680" height="640" viewBox="0 0 1680 640">
<path d="M{rx} {ry} H{bx}" stroke="var(--ink)" stroke-width="8"/>
{br(bx, ry, 860, up, C, 8)}{br(bx, ry, 760, dn, D, 8)}
<circle cx="{bx}" cy="{ry}" r="14" fill="var(--ink)"/>
<text x="650" y="{up-22}" font-size="36" font-weight="700" fill="{C}">ワニにつながる道</text>
<text x="650" y="{up+46}" font-size="24" fill="var(--sub)">より多彩な姿に分かれた</text>
{br(1010, up, 1180, 50, C, 5)}<path d="M860 {up} H1180" stroke="{C}" stroke-width="5"/>{br(1010, up, 1180, 250, C, 5)}
{tip(1180, 50, C)}{tip(1180, up, C)}{tip(1180, 250, C)}
<text x="1206" y="60" font-size="32" fill="var(--ink)">アエトサウルス類</text>
<text x="1206" y="{up+10}" font-size="32" fill="var(--ink)">エフィギア</text>
<text x="1206" y="260" font-size="32" fill="var(--ink)">ワニ</text>
<text x="580" y="{dn+60}" font-size="36" font-weight="700" fill="{D}">恐竜・翼竜・鳥につながる道</text>
{br(760, dn, 1180, 345, D, 5)}<path d="M760 {dn} H1180" stroke="{D}" stroke-width="5"/>
{br(1000, 345, 1180, 400, D, 4)}
{tip(1180, 345, D)}{tip(1180, 400, D)}
<text x="1206" y="355" font-size="32" fill="var(--ink)">ラゲルペトン類 <tspan font-size="24" fill="var(--sub)">（翼のない親戚）</tspan></text>
<text x="1206" y="410" font-size="32" fill="var(--ink)">翼竜</text>
{br(1060, dn, 1180, 560, D, 4)}
<circle cx="1060" cy="{dn}" r="9" fill="{D}"/>
{tip(1180, dn, D)}
<text x="1206" y="{dn+10}" font-size="32" fill="var(--ink)">恐竜 <tspan fill="var(--sub)">→</tspan> 鳥</text>
<circle cx="1180" cy="560" r="11" fill="none" stroke="{D}" stroke-width="4" stroke-dasharray="5 4"/>
<text x="1206" y="570" font-size="32" fill="var(--ink)">ニャササウルス <tspan font-weight="700" fill="var(--sand)">？</tspan></text>
<text x="1206" y="608" font-size="22" fill="var(--sub)">最古の恐竜か、いちばん近い親戚か</text>
</svg>"""
    body = f"""<h1>二つの道　<small>三畳紀の前半のうちに分かれた（枝分かれの模式図。線の長さに意味はない）</small></h1>
<div style="position:relative;margin-top:-40px">{svg}
 <div class="card" style="position:absolute;left:0;top:{ry-70}px;width:{rx}px;padding:18px 20px;font-size:30px;font-weight:700;line-height:1.35;text-align:center">のちに恐竜やワニに<br>つながる仲間</div>
</div>"""
    page("G05_二つの道", body, "Ezcurra et al. (2020) Nature 588:445 ／ Nesbitt et al. (2013) Biology Letters 9 ／ Nesbitt & Norell (2006) Proc. R. Soc. B 273:1045")

# ---------- G06 体の形の多さ ----------
def g06():
    x0 = 420
    svg = f"""<svg width="1680" height="420" viewBox="0 0 1680 420">
<line x1="{x0}" y1="20" x2="{x0}" y2="340" stroke="var(--sub)" stroke-width="3"/>
<text x="{x0-30}" y="118" font-size="36" font-weight="700" fill="var(--sand)" text-anchor="end">ワニにつながる側</text>
<rect x="{x0}" y="60" width="1000" height="90" rx="10" fill="var(--sand)"/>
<text x="{x0-30}" y="268" font-size="36" font-weight="700" fill="var(--sea)" text-anchor="end">恐竜</text>
<rect x="{x0}" y="210" width="560" height="90" rx="10" fill="var(--sea)"/>
<text x="{x0+1030}" y="118" font-size="40" font-weight="700" fill="var(--ink)">多い</text>
<text x="{x0+590}" y="268" font-size="40" font-weight="700" fill="var(--ink)">少ない</text>
<text x="{x0}" y="395" font-size="28" fill="var(--sub)">体の形の種類の多さ →（模式図。数値ではない）</text>
</svg>"""
    body = f"""<h1>体の形の種類の多さ　<small>2008年の研究：三畳紀の恐竜と、ワニにつながる側の骨の形を比べた</small></h1>
<div style="margin-top:0">{svg}</div>
<div style="font-size:34px;margin-top:30px;text-align:center">三畳紀は、<span class="sand">ワニの仲間たちが、さまざまな姿を試していた</span>時代でもあった</div>"""
    page("G06_体の形の多さ", body, "Brusatte, Benton, Ruta & Lloyd (2008) Science 321:1485")

# ---------- G07 恐竜の誕生の年代 ----------
def g07():
    L, R, x0, W = 256, 220, 40, 1600
    x = lambda ma: x0 + (L - ma) / (L - R) * W
    ay = 400   # 時間の軸
    ticks = "".join(f'<line x1="{x(m):.0f}" y1="{ay-10}" x2="{x(m):.0f}" y2="{ay+10}" stroke="var(--sub)" stroke-width="3"/>'
                    f'<text x="{x(m):.0f}" y="{ay+46}" font-size="26" fill="var(--sub)" text-anchor="middle">{t}</text>'
                    for m, t in [(250, "2億5000万年前"), (240, "2億4000万年前"), (230, "2億3000万年前")])
    svg = f"""<svg width="1680" height="660" viewBox="0 0 1680 660">
<line x1="{x0}" y1="{ay}" x2="{x0+W}" y2="{ay}" stroke="var(--sub)" stroke-width="3"/>
<path d="M{x0+W-10} {ay-12} L{x0+W+12} {ay} L{x0+W-10} {ay+12}" fill="var(--sub)"/>
<text x="{x0+W}" y="{ay+46}" font-size="24" fill="var(--sub)" text-anchor="end">時間 →</text>
{ticks}
<rect x="{x(250):.0f}" y="240" width="{x(240)-x(250):.0f}" height="90" rx="10" fill="var(--sea)" opacity=".55"/>
<text x="{(x(250)+x(240))/2:.0f}" y="296" font-size="34" font-weight="700" fill="var(--ink)" text-anchor="middle">恐竜が生まれた時期</text>
<text x="{x(250):.0f}" y="160" font-size="30" font-weight="700" fill="var(--sea)">2026年の研究の見積もり</text>
<text x="{x(250):.0f}" y="204" font-size="30" fill="var(--sea)">2億5000万〜2億4000万年前</text>
<line x1="{x(230):.0f}" y1="230" x2="{x(230):.0f}" y2="{ay}" stroke="var(--green)" stroke-width="4"/>
<circle cx="{x(230):.0f}" cy="230" r="16" fill="var(--green)"/>
<text x="{x(230)+30:.0f}" y="222" font-size="30" font-weight="700" fill="var(--green)">はっきり恐竜と言える</text>
<text x="{x(230)+30:.0f}" y="262" font-size="30" font-weight="700" fill="var(--green)">最も古い化石</text>
<text x="{x(230)+30:.0f}" y="302" font-size="28" fill="var(--green)">約2億3000万年前</text>
<path d="M{x(240):.0f} 360 H{x(230):.0f}" stroke="var(--sand)" stroke-width="4"/>
<path d="M{x(240):.0f} 348 V372 M{x(230):.0f} 348 V372" stroke="var(--sand)" stroke-width="4"/>
<text x="{(x(240)+x(230))/2:.0f}" y="344" font-size="28" font-weight="700" fill="var(--sand)" text-anchor="middle">一千万年ほど早い</text>
<rect x="{x(245):.0f}" y="500" width="{x(225)-x(245):.0f}" height="50" rx="8" fill="var(--sand)" opacity=".35"/>
<text x="{x(245)+20:.0f}" y="536" font-size="28" font-weight="700" fill="var(--ink)">およそ2000万年：種類の少ない、目立たない時期</text>
<text x="{x(245):.0f}" y="600" font-size="26" fill="var(--sub)">2018年の研究：恐竜は約2億4500万年前に生まれ、そのあと長く目立たなかった</text>
</svg>"""
    body = f"""<h1>恐竜はいつ生まれた？　<small>骨の特徴から、枝分かれの年代を計算した研究（見積もり）</small></h1>
<div style="margin-top:-40px">{svg}</div>"""
    page("G07_恐竜の誕生の年代", body, "Brownstein & Griffin (2026) Proc. R. Soc. B 293:20260102 ／ Bernardi et al. (2018) Nature Communications 9:1499 ／ Martinez et al. (2011) Science")

# ---------- G08 最初の恐竜の分布 ----------
def g08():
    band = '<rect x="0" y="388" width="1000" height="100" fill="var(--green)" opacity=".42"/>'
    spots = [("南アメリカ", 290, 430, "end", 12), ("アフリカ南部", 470, 425, "middle", 56), ("インド", 640, 415, "start", 12)]
    dots = ""
    for name, x, y, anc, dy in spots:
        tx = x + (28 if anc == "start" else -28 if anc == "end" else 0)
        dots += (f'<circle cx="{x}" cy="{y}" r="18" fill="var(--sand)" stroke="#0F1E2B" stroke-width="4"/>'
                 f'<text x="{tx}" y="{y+dy}" font-size="32" font-weight="700" fill="var(--ink)" text-anchor="{anc}" {LBL}>{name}</text>')
    body = f"""<h1>最初の恐竜たちが見つかった場所　<small>当時の大陸の、南のほうの限られた気候の帯</small></h1>
<div style="display:flex;gap:60px;align-items:flex-start;margin-top:-10px">
 <div style="flex:none">{pangaea_svg(dots, 960, 630, under=band)}</div>
 <div style="padding-top:110px;font-size:30px;line-height:1.7">
  <div><span style="display:inline-block;width:28px;height:28px;border-radius:50%;background:var(--sand);vertical-align:-4px;margin-right:12px"></span>最初の恐竜の化石</div>
  <div style="font-size:24px;margin-left:40px" class="sub">アルゼンチン・インド・ジンバブエ</div>
  <div style="margin-top:20px"><span style="display:inline-block;width:28px;height:28px;background:var(--green);opacity:.75;vertical-align:-4px;margin-right:12px"></span>限られた気候の帯</div>
  <div style="font-size:28px;margin-top:30px;line-height:1.6">気候のちがいが壁のように<br>広がるのをさまたげた？</div>
  <div class="sub" style="font-size:24px;margin-top:30px;line-height:1.6">位置も帯の幅も、おおまかな模式図<br>（大陸の輪郭は正確ではない）</div>
 </div>
</div>"""
    page("G08_最初の恐竜の分布", body, "Griffin et al. (2022) Nature 609:313 ／ U.S. Geological Survey \"This Dynamic Earth\"")

# ---------- G09 雨の時代 ----------
def g09():
    x = lambda ma: 120 + (236.2 - ma) * 300     # 2億3620万年前 → 2億3080万年前
    a, b = x(234), x(232)
    base = 250
    hump = [(a + 0.10 * (b - a), 150), (a + 0.36 * (b - a), 120), (a + 0.62 * (b - a), 160), (a + 0.88 * (b - a), 130)]
    d = f"M{a-30:.0f} {base}"
    for i, (hx, hy) in enumerate(hump):
        l = hx - 60
        d += f" L{l:.0f} {base} Q{hx:.0f} {hy-(base-hy):.0f} {hx+60:.0f} {base}"
    d += f" L{b+30:.0f} {base}"
    nums = "".join(f'<text x="{hx:.0f}" y="{hy-36:.0f}" font-size="28" font-weight="700" fill="var(--sea)" text-anchor="middle">{c}</text>'
                   for (hx, hy), c in zip(hump, "①②③④"))
    svg = f"""<svg width="1680" height="380" viewBox="0 0 1680 380">
<rect x="{a:.0f}" y="40" width="{b-a:.0f}" height="{base-40}" fill="var(--sea)" opacity=".12"/>
<path d="{d}" fill="var(--sea)" fill-opacity=".45" stroke="var(--sea)" stroke-width="5" stroke-linejoin="round"/>
{nums}
<line x1="60" y1="{base}" x2="1620" y2="{base}" stroke="var(--sub)" stroke-width="3"/>
<path d="M1610 {base-12} L1632 {base} L1610 {base+12}" fill="var(--sub)"/>
<text x="1620" y="{base+44}" font-size="24" fill="var(--sub)" text-anchor="end">時間 →</text>
<text x="{(60+a)/2:.0f}" y="{base-24}" font-size="30" fill="var(--sand)" text-anchor="middle">乾いた時代</text>
<text x="{(b+1560)/2:.0f}" y="{base-24}" font-size="30" fill="var(--sand)" text-anchor="middle">乾いた時代</text>
<path d="M{a:.0f} {base} V{base+30} M{b:.0f} {base} V{base+30}" stroke="var(--ink)" stroke-width="3"/>
<text x="{a:.0f}" y="{base+64}" font-size="28" fill="var(--ink)" text-anchor="middle">約2億3400万年前</text>
<text x="{b:.0f}" y="{base+64}" font-size="28" fill="var(--ink)" text-anchor="middle">約2億3200万年前</text>
<text x="{(a+b)/2:.0f}" y="{base+110}" font-size="24" fill="var(--sub)" text-anchor="middle">雨の多い時期が4回（山の位置と高さは模式）</text>
</svg>"""
    def card(head, note, color):
        return f"""<div class="card" style="flex:1;padding:20px 30px;border-color:{color}">
 <div style="font-size:32px;font-weight:700;color:{color}">{head}</div>
 <div style="font-size:26px;margin-top:8px;line-height:1.45" class="sub">{note}</div></div>"""
    body = f"""<h1>雨が降り続いた時代　<small>三畳紀の後半の初め、世界中で雨が大きく増えた</small></h1>
<div style="margin-top:-40px">{svg}</div>
<div style="display:flex;gap:40px;margin-top:-6px">
 {card("海の生き物のグループの約3分の1が消えた", "という分析（生き物の「属」の数で数えたもの）", "var(--sand)")}
 {card("原因の候補：大規模な火山活動", "いまの北アメリカの西の端に、その跡が残る（推定）", "var(--red)")}
</div>"""
    page("G09_雨の時代", body, "Dal Corso et al. (2020) Science Advances 6:eaba0099 ／ Bernardi et al. (2018) Nature Communications 9:1499")

# ---------- G10 二つの説 ----------
def g10():
    def card(tag, head, lines, color):
        return f"""<div class="card" style="flex:1;padding:30px 36px;border-color:{color}">
 <div style="font-size:28px;font-weight:700;color:{color}">{tag}</div>
 <div style="font-size:40px;font-weight:700;margin-top:14px;line-height:1.35">{head}</div>
 <div style="font-size:28px;margin-top:22px;line-height:1.6" class="sub">{lines}</div></div>"""
    body = f"""<h1>恐竜はどうやって数を増やした？　<small>研究によって、考え方が分かれている</small></h1>
<div style="display:flex;gap:50px;align-items:stretch;height:430px">
 {card("2018年の研究（イタリアの地層など）", "すき間を埋めた", "雨の時代の気候の大きな変化で、<br>それまでの主な植物食の動物が消えた<br>→ そのすき間を、恐竜が埋めていった", "var(--sea)")}
 {card("2011年の研究（アルゼンチンの谷）", "結びつかなかった", "恐竜以外の植物食の動物は、<br>順々に消えていった<br>→ 恐竜の種類が増えたこととは<br>　 結びついていなかった", "var(--sand)")}
</div>
<div style="font-size:36px;font-weight:700;margin-top:34px;text-align:center">答えは、<span class="sand">まだ一つではない</span></div>"""
    page("G10_二つの説", body, "Bernardi et al. (2018) Nature Communications 9:1499 ／ Martinez et al. (2011) Science 331:206")

# ---------- G11 歯の生え替わり ----------
def g11():
    def jaw(rows, sizes, colors, w=560):
        """横から見たあごの模式。rows 段の歯（上が今の歯、下が次に生える歯）"""
        s = f'<svg width="{w}" height="300" viewBox="0 0 {w} 300">'
        s += f'<rect x="20" y="60" width="{w-40}" height="220" rx="40" fill="#B49A70"/>'
        for r in range(rows):
            h, c = sizes[r], colors[r]
            y = 60 + r * 70 if r else 60
            for i in range(7):
                cx = 70 + i * ((w - 140) / 6)
                if r == 0:
                    s += f'<path d="M{cx-22:.0f} {y} L{cx:.0f} {y-h} L{cx+22:.0f} {y} Z" fill="{c}"/>'
                else:
                    s += f'<path d="M{cx-18:.0f} {y+40} L{cx:.0f} {y+40-h} L{cx+18:.0f} {y+40} Z" fill="{c}" opacity=".9"/>'
        return s + "</svg>"
    rep = jaw(3, [56, 46, 40], ["#F2EDE2", "#D8CCB4", "#C4B494"])
    mam1 = jaw(1, [36], ["#F2EDE2"], 360)
    mam2 = jaw(1, [56], ["#F2EDE2"], 360)
    body = f"""<h1>歯の生え替わり　<small>あごの中の歯の模式図（形はおおまか）</small></h1>
<div style="display:flex;gap:50px;align-items:stretch;height:600px">
 <div class="card" style="flex:1;padding:24px 30px;text-align:center">
  <div style="font-size:38px;font-weight:700">爬虫類</div>
  <div style="margin-top:20px">{rep}</div>
  <div style="font-size:34px;font-weight:700;margin-top:20px" class="sand">一生のあいだに、何度も生え替わる</div>
  <div style="font-size:26px;margin-top:10px" class="sub">あごの中で、次の歯が次々に育つ</div></div>
 <div class="card" style="flex:1.2;padding:24px 30px;text-align:center;border-color:var(--sea)">
  <div style="font-size:38px;font-weight:700" class="sea">哺乳類（あなたも）</div>
  <div style="display:flex;align-items:center;justify-content:center;gap:10px;margin-top:20px">
   <div>{mam1}<div style="font-size:30px;font-weight:700">乳歯</div></div>
   <div style="font-size:56px;padding-bottom:40px" class="sea">→</div>
   <div>{mam2}<div style="font-size:30px;font-weight:700">永久歯</div></div></div>
  <div style="font-size:34px;font-weight:700;margin-top:14px" class="sea">生え替わりは一度だけ</div>
  <div style="font-size:26px;margin-top:10px" class="sub">ブラシロドンの下あごも、決まった順番で一度だけ</div></div>
</div>"""
    page("G11_歯の生え替わり", body, "Cabreira et al. (2022) Journal of Anatomy 241:1424")

# ---------- G12 哺乳類の始まり ----------
def g12():
    L, R, x0, W = 236, 198, 60, 1560
    x = lambda ma: x0 + (L - ma) / (L - R) * W
    ay = 330
    svg = f"""<svg width="1680" height="620" viewBox="0 0 1680 620">
<line x1="{x0}" y1="{ay}" x2="{x0+W}" y2="{ay}" stroke="var(--sub)" stroke-width="3"/>
<path d="M{x0+W-10} {ay-12} L{x0+W+12} {ay} L{x0+W-10} {ay+12}" fill="var(--sub)"/>
<text x="{x0+W}" y="{ay+44}" font-size="24" fill="var(--sub)" text-anchor="end">時間 →</text>
<line x1="{x(225):.0f}" y1="190" x2="{x(225):.0f}" y2="{ay}" stroke="var(--sand)" stroke-width="4"/>
<circle cx="{x(225):.0f}" cy="{ay}" r="18" fill="var(--sand)"/>
<text x="{x(225):.0f}" y="70" font-size="38" font-weight="700" fill="var(--sand)" text-anchor="middle">ブラシロドン</text>
<text x="{x(225):.0f}" y="116" font-size="30" fill="var(--ink)" text-anchor="middle">約2億2500万年前</text>
<text x="{x(225):.0f}" y="160" font-size="24" fill="var(--sub)" text-anchor="middle">哺乳類かどうかは意見が分かれる</text>
<line x1="{x(205):.0f}" y1="190" x2="{x(205):.0f}" y2="{ay}" stroke="var(--sea)" stroke-width="4"/>
<circle cx="{x(205):.0f}" cy="{ay}" r="18" fill="var(--sea)"/>
<text x="{x(205):.0f}" y="70" font-size="38" font-weight="700" fill="var(--sea)" text-anchor="middle">モルガヌコドン</text>
<text x="{x(205):.0f}" y="116" font-size="30" fill="var(--ink)" text-anchor="middle">約2億500万年前</text>
<text x="{x(205):.0f}" y="160" font-size="24" fill="var(--sub)" text-anchor="middle">これまで最初の哺乳類とされてきた（歯の化石）</text>
<line x1="{x(230):.0f}" y1="{ay}" x2="{x(230):.0f}" y2="{ay+60}" stroke="var(--green)" stroke-width="4"/>
<circle cx="{x(230):.0f}" cy="{ay}" r="12" fill="var(--green)"/>
<text x="{x(230)-10:.0f}" y="{ay+100}" font-size="28" font-weight="700" fill="var(--green)">最も古い恐竜たち</text>
<text x="{x(230)-10:.0f}" y="{ay+138}" font-size="26" fill="var(--green)">約2億3000万年前</text>
<path d="M{x(225):.0f} {ay+180} H{x(205):.0f}" stroke="var(--sand)" stroke-width="4"/>
<path d="M{x(225):.0f} {ay+168} V{ay+192} M{x(205):.0f} {ay+168} V{ay+192}" stroke="var(--sand)" stroke-width="4"/>
<text x="{(x(225)+x(205))/2:.0f}" y="{ay+164}" font-size="32" font-weight="700" fill="var(--sand)" text-anchor="middle">およそ2000万年さかのぼる？</text>
<text x="{(x(225)+x(205))/2:.0f}" y="{ay+236}" font-size="26" fill="var(--sub)" text-anchor="middle">ブラシロドンを調べた研究チームの主張</text>
</svg>"""
    body = f"""<h1>哺乳類の始まりはいつ？　<small>私たちにつながる仲間は、恐竜とほとんど同じころに現れていた</small></h1>
<div style="margin-top:-30px">{svg}</div>"""
    page("G12_哺乳類の始まり", body, "Cabreira et al. (2022) Journal of Anatomy 241:1424 ／ ロンドン自然史博物館 発表 ／ Martinez et al. (2011) Science")

# ---------- G13 溶岩の広さ ----------
def g13():
    unit = 118                     # 日本の面積（約37.8万km²）の正方形の一辺
    big = unit * math.sqrt(700 / 37.8)
    mid = unit * math.sqrt(500 / 37.8)
    gy = 640
    def sq(x, side, color, op=1, dash=False):
        st = f'stroke="{color}" stroke-width="4"' + (' stroke-dasharray="14 10"' if dash else "")
        return f'<rect x="{x:.0f}" y="{gy-side:.0f}" width="{side:.0f}" height="{side:.0f}" fill="{color}" fill-opacity="{op}" {st}/>'
    x1, x2, x3 = 40, 40 + big + 100, 40 + big + 100 + mid + 100
    svg = f"""<svg width="1680" height="660" viewBox="0 0 1680 660">
{sq(x1, big, "var(--red)", .55)}{sq(x2, mid, "#8A5A4A", .3, True)}{sq(x3, unit, "var(--sea)", .7)}
<text x="{x1+big/2:.0f}" y="{gy-big/2-50:.0f}" font-size="32" font-weight="700" fill="var(--ink)" text-anchor="middle">中央大西洋マグマ分布域</text>
<text x="{x1+big/2:.0f}" y="{gy-big/2+6:.0f}" font-size="44" font-weight="700" fill="var(--ink)" text-anchor="middle">700万km²超</text>
<text x="{x1+big/2:.0f}" y="{gy-big/2+60:.0f}" font-size="34" fill="var(--sand)" text-anchor="middle" font-weight="700">日本の約18.5倍</text>
<text x="{x1+big/2:.0f}" y="{gy-big/2+104:.0f}" font-size="24" fill="var(--ink)" text-anchor="middle">三畳紀の終わり</text>
<text x="{x2+mid/2:.0f}" y="{gy-mid/2-30:.0f}" font-size="28" fill="var(--sub)" text-anchor="middle">前回：シベリアの火山</text>
<text x="{x2+mid/2:.0f}" y="{gy-mid/2+14:.0f}" font-size="32" fill="var(--ink)" text-anchor="middle">最大 約500万km²</text>
<text x="{x2+mid/2:.0f}" y="{gy-mid/2+56:.0f}" font-size="28" fill="var(--sub)" text-anchor="middle">日本の約13倍</text>
<text x="{x3+unit/2:.0f}" y="{gy-unit-58:.0f}" font-size="32" font-weight="700" fill="var(--ink)" text-anchor="middle">日本</text>
<text x="{x3+unit/2:.0f}" y="{gy-unit-20:.0f}" font-size="26" fill="var(--sub)" text-anchor="middle">約37.8万km²</text>
</svg>"""
    body = f"""<h1>火山の跡が広がる範囲　<small>四角の面積で比べた模式図（実際の形とは違う）</small></h1>
<div style="margin-top:-60px">{svg}</div>"""
    page("G13_溶岩の広さ", body, "Marzoli et al. (1999) Science 284:616 ／ 第3話：Reichow et al. (2009) Earth and Planetary Science Letters 277:9 ほか")

# ---------- G14 四回の波 ----------
def g14():
    sc = 19                       # 1万年あたりのpx
    x = lambda t: 300 + t * sc    # t は「最初の噴火」からの万年
    ay = 400
    peaks = [0, 17, 37, 58]       # 波の位置は模式（論文の図の値ではない）
    hs = [190, 150, 170, 130]
    vol = ""
    for t, h in zip(peaks, hs):
        cx = x(t) + 30
        vol += f'<path d="M{cx-45:.0f} {ay} Q{cx:.0f} {ay-2*h:.0f} {cx+45:.0f} {ay} Z" fill="var(--red)" opacity=".85"/>'
    nums = "".join(f'<text x="{x(t)+30:.0f}" y="{ay-h-18:.0f}" font-size="30" font-weight="700" fill="var(--ink)" text-anchor="middle">{c}</text>'
                   for t, h, c in zip(peaks, hs, "1234"))
    svg = f"""<svg width="1680" height="640" viewBox="0 0 1680 640">
<defs><linearGradient id="mg" x1="0" x2="1"><stop offset="0" stop-color="#8A5A4A"/><stop offset=".6" stop-color="#8A5A4A"/><stop offset="1" stop-color="#8A5A4A" stop-opacity="0"/></linearGradient></defs>
<rect x="{x(-10):.0f}" y="{ay+30}" width="{x(6)-x(-10):.0f}" height="34" rx="6" fill="url(#mg)"/>
<text x="{x(-10):.0f}" y="{ay+110}" font-size="28" font-weight="700" fill="#E0A080">地下に入り込んだマグマの活動</text>
<text x="{x(-10):.0f}" y="{ay+150}" font-size="26" fill="var(--sub)">知られている最初の噴火より、約10万年前に始まっていた（2017年の研究）</text>
{vol}{nums}
<line x1="80" y1="{ay}" x2="1600" y2="{ay}" stroke="var(--sub)" stroke-width="3"/>
<path d="M1590 {ay-12} L1612 {ay} L1590 {ay+12}" fill="var(--sub)"/>
<text x="1600" y="{ay-16}" font-size="24" fill="var(--sub)" text-anchor="end">時間 →</text>
<path d="M{x(-10):.0f} {ay+76} H{x(0):.0f}" stroke="#E0A080" stroke-width="3"/>
<path d="M{x(-10):.0f} {ay+66} V{ay+86} M{x(0):.0f} {ay+66} V{ay+86}" stroke="#E0A080" stroke-width="3"/>
<line x1="{x(0)-15:.0f}" y1="70" x2="{x(0)-15:.0f}" y2="{ay}" stroke="var(--sand)" stroke-width="4" stroke-dasharray="10 8"/>
<text x="{x(0)-30:.0f}" y="100" font-size="30" font-weight="700" fill="var(--sand)" text-anchor="end">絶滅</text>
<text x="{x(0)-30:.0f}" y="140" font-size="26" fill="var(--sand)" text-anchor="end">最初の噴火と</text>
<text x="{x(0)-30:.0f}" y="174" font-size="26" fill="var(--sand)" text-anchor="end">同じ時期</text>
<path d="M{x(0):.0f} 60 H{x(60):.0f}" stroke="var(--ink)" stroke-width="4"/>
<path d="M{x(0):.0f} 46 V74 M{x(60):.0f} 46 V74" stroke="var(--ink)" stroke-width="4"/>
<text x="{(x(0)+x(60))/2:.0f}" y="40" font-size="34" font-weight="700" fill="var(--ink)" text-anchor="middle">およそ60万年のあいだに、4回の大きな波</text>
</svg>"""
    body = f"""<h1>噴火は四回の波で　<small>年代を細かく測った研究（波の間隔と高さは模式）</small></h1>
<div style="margin-top:-30px">{svg}</div>"""
    page("G14_四回の波", body, "Blackburn et al. (2013) Science 340:941 ／ Davies et al. (2017) Nature Communications 8:15596")

# ---------- G15 五つの大量絶滅 ----------
def g15():
    names = ["オルドビス紀の終わり", "デボン紀の後期", "ペルム紀の終わり", "三畳紀の終わり", "白亜紀の終わり"]
    xs = [180, 500, 820, 1140, 1460]
    ay = 300
    s = ""
    for i, (n, cx) in enumerate(zip(names, xs)):
        hot = i == 3
        c = "var(--sand)" if hot else "var(--sub)"
        if hot:
            s += f'<circle cx="{cx}" cy="{ay}" r="58" fill="none" stroke="var(--sand)" stroke-width="6"/>'
        s += f'<circle cx="{cx}" cy="{ay}" r="{34 if hot else 26}" fill="{"var(--red)" if hot else "#4A5A68"}"/>'
        s += f'<text x="{cx}" y="{ay+(116 if hot else 90)}" font-size="{38 if hot else 32}" font-weight="700" fill="{"var(--ink)" if hot else "var(--sub)"}" text-anchor="middle">{n}</text>'
    s += f'<text x="{xs[3]}" y="{ay-90}" font-size="38" font-weight="700" fill="var(--sand)" text-anchor="middle">今回</text>'
    s += f'<text x="{xs[2]}" y="{ay-60}" font-size="30" fill="var(--sub)" text-anchor="middle">前回</text>'
    svg = f"""<svg width="1680" height="520" viewBox="0 0 1680 520">
<line x1="60" y1="{ay}" x2="1600" y2="{ay}" stroke="var(--sub)" stroke-width="4"/>
<path d="M1590 {ay-14} L1616 {ay} L1590 {ay+14}" fill="var(--sub)"/>
<text x="60" y="{ay-30}" font-size="26" fill="var(--sub)">古い</text>
<text x="1600" y="{ay-30}" font-size="26" fill="var(--sub)" text-anchor="end">新しい</text>
{s}
<text x="840" y="500" font-size="26" fill="var(--sub)" text-anchor="middle">古い順に並べた模式図（間隔は実際の年代の差とは違う）</text>
</svg>"""
    body = f"""<h1>五つの大きな大量絶滅　<small>三畳紀の終わりの絶滅も、そのひとつに数えられる</small></h1>
<div style="margin-top:-10px">{svg}</div>"""
    page("G15_五つの大量絶滅", body, "Lomax et al. (2024) PLoS ONE 19:e0300289 ／ Davies et al. (2017) Nature Communications 8:15596")

# ---------- G16 魚竜の大きさ比べ ----------
def g16():
    m = 50                 # 1mあたりのpx
    x0 = 380
    sy = 0.85
    rows = [
        (ichthy(x0, 110, 25 * m, "var(--sand)", sy=sy, dashed=True, jaw=True), "最後の巨大な魚竜", "約25m（推定）", "下あごの骨から推定。体の形は想像", "var(--sand)"),
        (cymbo(x0, 300, 17 * m, "#B8A27C", sy=17 * m / 1000 * 1.2), "キンボスポンディルス", "17m超（推定）", "約2億4600万年前", "#B8A27C"),
        (whale(x0, 465, 25 * m, sy=1.0), "シロナガスクジラ", "約25m", "いまの海の動物", "#A0AEB8"),
    ]
    g, lbl = "", ""
    for i, (shape, name, size, note, c) in enumerate(rows):
        y = [110, 300, 465][i]
        g += shape
        lbl += (f'<text x="{x0-30}" y="{y-14}" font-size="32" font-weight="700" fill="{c}" text-anchor="end">{name}</text>'
                f'<text x="{x0-30}" y="{y+28}" font-size="32" font-weight="700" fill="var(--ink)" text-anchor="end">{size}</text>')
    notes = (f'<text x="{x0+10*m+120}" y="{620}" font-size="26" fill="var(--sub)">※ 見つかったのは下あごの骨だけ（濃い部分）</text>'
             f'<text x="{x0+10*m+120}" y="{656}" font-size="26" fill="var(--sub)">　 体の形は近い仲間からの想像（点線）</text>'
             f'<text x="{x0+17*m+30}" y="{300+10}" font-size="24" fill="var(--sub)">約2億4600万年前</text>')
    svg = f"""<svg width="1680" height="670" viewBox="0 0 1680 670">
{g}{lbl}{notes}
<line x1="{x0}" y1="625" x2="{x0+10*m}" y2="625" stroke="var(--ink)" stroke-width="4"/>
<path d="M{x0} 613 V637 M{x0+10*m} 613 V637" stroke="var(--ink)" stroke-width="4"/>
<text x="{x0+10*m+20}" y="635" font-size="26" fill="var(--ink)">10m</text>
</svg>"""
    body = f"""<h1>巨大な魚竜の大きさ比べ　<small>約2億200万年前の魚竜（2024年に名前がつけられた）</small></h1>
<div style="margin-top:-46px">{svg}</div>"""
    page("G16_魚竜の大きさ比べ", body, "Lomax et al. (2024) PLoS ONE 19:e0300289 ／ マンチェスター大学 発表 ／ Sander et al. (2021) Science")

# ---------- G17 なぜ恐竜か ----------
def g17():
    def card(tag, head, lines, color):
        return f"""<div class="card" style="flex:1;padding:30px 36px;border-color:{color}">
 <div style="font-size:28px;font-weight:700;color:{color}">{tag}</div>
 <div style="font-size:42px;font-weight:700;margin-top:14px;line-height:1.35">{head}</div>
 <div style="font-size:28px;margin-top:22px;line-height:1.6" class="sub">{lines}</div></div>"""
    body = f"""<h1>なぜ、恐竜が生き残った？　<small>はっきりした答えは、まだない</small></h1>
<div style="display:flex;gap:30px;align-items:stretch;height:470px">
 {card("2022年の研究", "寒さに強かった説", "恐竜は羽毛のようなもので体を覆っていた？<br>＋ 噴火で空が暗くなり、厳しい寒さ（火山の冬）<br>→ 覆いのない中〜大型の爬虫類が消えた<br><span style='font-size:24px'>※羽毛のようなものは近い親戚からの推し量り</span>", "var(--sea)")}
 <div style="align-self:center;width:170px;text-align:center;font-size:30px;font-weight:700;line-height:1.5" class="sand">答えは<br>まだ<br>出ていない</div>
 {card("2008年の研究", "めぐり合わせ説", "三畳紀の恐竜は、ワニの側の仲間より<br>特に優れていたわけではない<br>→ 栄えたのは、めぐり合わせ（運）による<br>ところが大きかった", "var(--sand)")}
</div>"""
    page("G17_なぜ恐竜か", body, "Olsen et al. (2022) Science Advances 8:eabo6342 ／ Brusatte et al. (2008) Science 321:1485")

for f in (g01, g02, g03, g04, g05, g06, g07, g08, g09, g10, g11, g12, g13, g14, g15, g16, g17):
    f()
