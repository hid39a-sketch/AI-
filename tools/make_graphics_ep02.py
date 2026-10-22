# 第2話の図（G01〜G12）と、地図ふうの S07 をHTMLで作り、Edge（ヘッドレス）で1920x1080のPNGに変換する
# 使い方: python -I tools/make_graphics_ep02.py   （ONLY=G01,S07 のように指定すると、その図だけ作り直す）
# 数値はすべて scripts/ep02_carboniferous.txt のナレーションと factcheck_ep02.md に一致させること
# 画面下140pxは字幕用、右上は信頼度の表示用に空ける
import subprocess, pathlib, html, tempfile, time, os, math, random

ONLY = [x for x in os.environ.get("ONLY", "").split(",") if x]
ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "images" / "ep02"
SRC = OUT / "graphics_src"
SRC.mkdir(parents=True, exist_ok=True)
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

# チャンネルの配色（第1話と同じ深い海の色）
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

def steps_row(items, arrow="→"):
    """横に並ぶ手順のカード（絵 + 見出し + 説明）"""
    cells = ""
    for i, (svg, head, note) in enumerate(items):
        cells += f"""<div class="card" style="flex:1;text-align:center;padding:30px 18px;height:100%">
 <div style="height:230px;display:flex;align-items:center;justify-content:center">{svg}</div>
 <div style="font-size:32px;font-weight:700;margin-top:18px;line-height:1.35">{head}</div>
 <div style="font-size:26px;margin-top:12px;line-height:1.45" class="sub">{note}</div></div>"""
        if i < len(items) - 1:
            cells += f'<div style="font-size:56px;padding:0 14px" class="sand">{arrow}</div>'
    return cells

# ---------- G01 年表：石炭紀の位置 ----------
def g01():
    L, R, W = 437, 215, 1680          # 4億3700万年前 → 2億1500万年前
    x = lambda ma: (L - ma) / (L - R) * W
    dev0, car0, per0, tri0, dino = 419.62, 358.86, 298.9, 251.9, 230
    def band(a, b, bg, name, big=False):
        return f"""<div style="position:absolute;left:{x(a)}px;top:260px;width:{x(b)-x(a)}px;height:{110 if big else 70}px;margin-top:{-20 if big else 0}px;
 background:{bg};display:flex;align-items:center;justify-content:center;font-size:{44 if big else 32}px;font-weight:{700 if big else 400};
 {'box-shadow:0 0 0 4px var(--sand);border-radius:10px;z-index:2;' if big else ''}">{name}</div>"""
    def tick(ma, txt, color="var(--sub)"):
        return f"""<div style="position:absolute;left:{x(ma)-2}px;top:250px;width:4px;height:150px;background:{color}"></div>
<div style="position:absolute;left:{x(ma)-140}px;top:410px;width:280px;text-align:center;font-size:26px;line-height:1.35;color:{color}">{txt}</div>"""
    def ep(ma_a, ma_b, txt, color):
        c = (x(ma_a) + x(ma_b)) / 2
        return f"""<div style="position:absolute;left:{c-150}px;top:130px;width:300px;text-align:center;font-size:30px;font-weight:700;color:{color}">{txt}</div>
<div style="position:absolute;left:{c-2}px;top:180px;width:4px;height:58px;background:{color}"></div>"""
    body = f"""<h1>石炭紀はいつ？　<small>デボン紀のすぐあと、約6000万年続いた時代</small></h1>
<div style="position:relative;height:620px">
 {band(dev0, car0, "#24506A", "デボン紀")}
 {band(car0, per0, "#3E6B4A", "石炭紀", True)}
 {band(per0, tri0, "#4A4E5A", "ペルム紀")}
 <div style="position:absolute;left:{x(tri0)}px;top:260px;width:{x(R)-x(tri0)}px;height:70px;background:linear-gradient(90deg,#2F3A44,rgba(47,58,68,0))"></div>
 <div style="position:absolute;left:{x(dino)-110}px;top:185px;font-size:26px;line-height:1.35;white-space:nowrap" class="sub">恐竜が現れる →<br>約2億3000万年前〜</div>
 {ep(dev0, car0, "第1話", "var(--sub)")}
 {ep(car0, per0, "第2話", "var(--sand)")}
 {tick(dev0, "約4億2000万年前")}
 {tick(car0, "<b>約3億5900万年前</b>", "var(--sand)")}
 {tick(per0, "<b>約2億9900万年前</b>", "var(--sand)")}
 {tick(tri0, "約2億5200万年前<br><span style='font-size:22px'>史上最大の大量絶滅</span>")}
 <div style="position:absolute;left:0;top:560px;font-size:26px" class="sub">名前の由来：イギリスで、石炭をたくさん含む地層があったことから</div>
</div>"""
    page("G01_年表", body, "国際年代層序表 v2026/06（International Chronostratigraphic Chart）／ UC Museum of Paleontology")

# ---------- G02 酸素の割合 ----------
def g02():
    scale = 30  # 1%あたりのpx
    x0 = 420
    def bar(label, lo, hi, color, note, dashed=False):
        solid = f'<div style="position:absolute;left:0;top:0;height:64px;width:{lo*scale}px;background:{color};border-radius:8px 0 0 8px;{"opacity:.45" if dashed else ""}"></div>'
        rng = "" if hi == lo else f'<div style="position:absolute;left:{lo*scale}px;top:0;height:64px;width:{(hi-lo)*scale}px;background:{color};opacity:.35;border-radius:0 8px 8px 0;{"outline:3px dashed "+color+";outline-offset:-3px" if dashed else ""}"></div>'
        return f"""<div style="display:flex;align-items:center;margin:40px 0">
 <div style="width:{x0}px;flex-shrink:0;font-size:32px;line-height:1.3">{label}</div>
 <div style="position:relative;flex-shrink:0;height:64px;width:{hi*scale}px">{solid}{rng}</div>
 <div style="margin-left:26px;font-size:36px;font-weight:700;white-space:nowrap">{note}</div></div>"""
    ticks = "".join(f'<div style="position:absolute;left:{x0+m*scale}px;top:0;font-size:22px;transform:translateX(-50%)" class="sub">{m}%</div>' for m in range(0, 36, 5))
    grid = "".join(f'<div style="position:absolute;left:{x0+m*scale}px;top:40px;width:1px;height:380px;background:var(--line)"></div>' for m in range(0, 36, 5))
    body = f"""<h1>空気の中の酸素の割合　<small>石炭紀の値は、計算や山火事の跡から見積もった推定</small></h1>
<div style="position:relative">
 <div style="position:relative;height:30px">{ticks}</div>{grid}
 <div style="position:absolute;left:{x0+21*scale-2}px;top:40px;width:4px;height:380px;background:var(--sea);opacity:.6"></div>
 {bar("いま", 21, 21, "var(--sea)", "約21%")}
 {bar("石炭紀の終わりごろ<br><span class='sub' style='font-size:26px'>新しい計算の推定</span>", 25, 30, "var(--sand)", "25〜30%")}
 {bar("古い計算", 35, 35, "#8A7F6A", "最大35%", True)}
</div>
<div style="font-size:28px;margin-top:20px;line-height:1.6"><span class="sand">■</span> 薄い部分は推定の幅<br>
<span class="sub">推定には幅があり、計算の方法でも答えが変わる。わかっているのは「いまより多かったらしい」まで</span></div>"""
    page("G02_酸素の割合", body, "Krause et al. (2018) Nature Communications ／ Scott & Glasspool (2006) PNAS")

# ---------- G03 酸素の計算の仕組み ----------
def g03():
    sun = """<svg width="260" height="220" viewBox="0 0 260 220"><circle cx="60" cy="55" r="32" fill="var(--sand)"/>
<g stroke="var(--sand)" stroke-width="5">""" + "".join(
        f'<line x1="{60+44*math.cos(a)}" y1="{55+44*math.sin(a)}" x2="{60+58*math.cos(a)}" y2="{55+58*math.sin(a)}"/>' for a in [i*math.pi/4 for i in range(8)]) + """</g>
<path d="M150 200 V110" stroke="#5E8A62" stroke-width="10"/><ellipse cx="185" cy="105" rx="50" ry="24" fill="var(--green)" transform="rotate(-25 185 105)"/>
<ellipse cx="118" cy="125" rx="40" ry="20" fill="var(--green)" transform="rotate(25 118 125)"/>
<text x="210" y="45" font-size="34" fill="var(--sea)" font-weight="700">O₂</text></svg>"""
    bury = """<svg width="260" height="220" viewBox="0 0 260 220"><rect x="0" y="60" width="260" height="40" fill="#5A4A36"/>
<rect x="0" y="100" width="260" height="40" fill="#4A3C2C"/><rect x="0" y="140" width="260" height="40" fill="#3A2F24"/>
<rect x="30" y="148" width="180" height="16" rx="8" fill="#1C1712"/><rect x="70" y="112" width="150" height="14" rx="7" fill="#251D16"/>
<path d="M130 10 V48" stroke="var(--ink)" stroke-width="5"/><path d="M118 36 L130 52 L142 36" fill="none" stroke="var(--ink)" stroke-width="5"/></svg>"""
    air = """<svg width="260" height="220" viewBox="0 0 260 220">""" + "".join(
        f'<circle cx="{x}" cy="{y}" r="{r}" fill="none" stroke="var(--sea)" stroke-width="4"/><text x="{x}" y="{y+r*0.38}" font-size="{r}" fill="var(--sea)" text-anchor="middle" font-weight="700">O₂</text>'
        for x, y, r in [(70, 70, 40), (180, 60, 34), (125, 150, 44), (215, 160, 30)]) + "</svg>"
    body = f"""<h1>酸素の量を計算する仕組み　<small>植物が埋もれた量から、空気に残った酸素を見積もる</small></h1>
<div style="display:flex;align-items:stretch;height:500px">{steps_row([
        (sun, "植物が光を浴びて<br>酸素を出す", ""),
        (bury, "腐らずに<br>地面の下に埋もれる", "腐ると、出した酸素が<br>使われてしまう"),
        (air, "出した酸素が<br>空気の中に残る", ""),
    ])}</div>
<div style="font-size:32px;margin-top:34px;text-align:center">岩に残る記録から <span class="sand">埋もれた植物の量</span> を見積もり → <span class="sea">酸素の量</span> を計算</div>"""
    page("G03_酸素の計算の仕組み", body, "Krause et al. (2018) Nature Communications")

# ---------- G04 高さ比べ ----------
def g04():
    pm = 13                 # 1メートルあたりのpx
    gy = 600                # 地面
    ticks = "".join(f'<line x1="120" y1="{gy-m*pm}" x2="1600" y2="{gy-m*pm}" stroke="var(--line)" stroke-width="2" stroke-dasharray="6 8"/>'
                    f'<text x="100" y="{gy-m*pm+9}" font-size="24" fill="var(--sub)" text-anchor="end">{m}m</text>' for m in range(0, 41, 10))
    # リンボク：まっすぐな幹、てっぺんで二股に分かれる枝
    tx, top = 470, gy - 39 * pm
    def branch(x, y, ang, ln, depth):
        if depth == 0:
            return f'<ellipse cx="{x}" cy="{y}" rx="14" ry="9" fill="var(--green)"/>'
        x2, y2 = x + ln * math.sin(ang), y - ln * math.cos(ang)
        s = f'<line x1="{x}" y1="{y}" x2="{x2}" y2="{y2}" stroke="#7E6A4C" stroke-width="{2+depth*2}" stroke-linecap="round"/>'
        return s + branch(x2, y2, ang - 0.42, ln * 0.72, depth - 1) + branch(x2, y2, ang + 0.42, ln * 0.72, depth - 1)
    crown_base = top + 112
    tree = (f'<path d="M{tx-22} {gy} L{tx-14} {crown_base} H{tx+14} L{tx+22} {gy} Z" fill="#7E6A4C"/>'
            + "".join(f'<path d="M{tx-12} {y} l12 -8 l12 8 l-12 8 z" fill="none" stroke="#5E4E38" stroke-width="2"/>' for y in range(crown_base + 20, gy - 10, 26))
            + branch(tx, crown_base, -0.5, 52, 4) + branch(tx, crown_base, 0.5, 52, 4))
    # 10階建てのビル（約30m）
    bx, bw, bh = 1010, 170, 30 * pm
    wins = "".join(f'<rect x="{bx+18+c*52}" y="{gy-bh+12+r*bh/10}" width="30" height="{bh/10-18}" fill="#2C4459"/>' for r in range(10) for c in range(3))
    bld = f'<rect x="{bx}" y="{gy-bh}" width="{bw}" height="{bh}" fill="#5C6F7D"/>{wins}'
    hx = 1420
    svg = f"""<svg width="1680" height="660" viewBox="0 0 1680 660">{ticks}
<line x1="120" y1="{gy}" x2="1600" y2="{gy}" stroke="var(--sub)" stroke-width="3"/>
{tree}{bld}{human(hx, gy, 1.7*pm, "var(--ink)")}
<text x="{tx+200}" y="{top+40+30}" font-size="34" font-weight="700" fill="var(--sand)">リンボク</text>
<text x="{tx+200}" y="{top+40+72}" font-size="30" fill="var(--sand)">高さ40m近く</text>
<text x="{tx+200}" y="{top+40+110}" font-size="24" fill="var(--sub)">大きいものの推定</text>
<text x="{bx+bw/2}" y="{gy-bh-46}" font-size="30" text-anchor="middle" fill="var(--ink)">10階建てのビル</text>
<text x="{bx+bw/2}" y="{gy-bh-12}" font-size="26" text-anchor="middle" fill="var(--sub)">約30m</text>
<text x="{hx+8}" y="{gy-110}" font-size="30" text-anchor="middle" fill="var(--ink)">人</text>
<text x="{hx+8}" y="{gy-76}" font-size="26" text-anchor="middle" fill="var(--sub)">1.7m</text>
<line x1="{hx+8}" y1="{gy-62}" x2="{hx+8}" y2="{gy-30}" stroke="var(--sub)" stroke-width="3"/>
</svg>"""
    body = f"""<h1>うろこの木・リンボクの高さ　<small>同じ縮尺で比べると</small></h1>
<div style="margin-top:-30px">{svg}</div>"""
    page("G04_高さ比べ", body, "Kerp, H. \"A History of Palaeozoic Forests\"（ミュンスター大学 古植物学研究所）")

# ---------- G05 アースロプレウラの大きさ ----------
def g05():
    pm = 330
    L, Wd = 2.63 * pm, 0.55 * pm
    x0, cy = 40, 210
    n = 30
    seg = ""
    legs = ""
    for i in range(n):
        t = (i + 0.5) / n
        w = Wd * min(1, 0.62 + 1.6 * t, 0.5 + 2.0 * (1 - t))
        sx = x0 + 40 + i * (L - 40) / n
        sw = (L - 40) / n - 3
        seg += f'<rect x="{sx}" y="{cy-w/2}" width="{sw}" height="{w}" rx="6" fill="#9C845E"/>'
        seg += f'<rect x="{sx+2}" y="{cy-w/2+6}" width="{sw-4}" height="{w*0.18}" rx="4" fill="#B49A70"/>'
        for side in (-1, 1):
            for k in (0.3, 0.75):
                lx = sx + sw * k
                legs += f'<line x1="{lx}" y1="{cy+side*w/2}" x2="{lx-4}" y2="{cy+side*(w/2+20)}" stroke="#7E6A4C" stroke-width="4" stroke-linecap="round"/>'
    head = (f'<ellipse cx="{x0+28}" cy="{cy}" rx="30" ry="40" fill="#8A7350"/>'
            f'<path d="M{x0+8} {cy-20} Q{x0-20} {cy-60} {x0-30} {cy-90}" stroke="#8A7350" stroke-width="4" fill="none"/>'
            f'<path d="M{x0+8} {cy+20} Q{x0-20} {cy+60} {x0-30} {cy+90}" stroke="#8A7350" stroke-width="4" fill="none"/>')
    hx, gy, hh = 1240, 610, 1.7 * pm
    dim = f"""<line x1="{x0}" y1="{cy+Wd/2+60}" x2="{x0+L}" y2="{cy+Wd/2+60}" stroke="var(--sand)" stroke-width="4"/>
<line x1="{x0}" y1="{cy+Wd/2+44}" x2="{x0}" y2="{cy+Wd/2+76}" stroke="var(--sand)" stroke-width="4"/>
<line x1="{x0+L}" y1="{cy+Wd/2+44}" x2="{x0+L}" y2="{cy+Wd/2+76}" stroke="var(--sand)" stroke-width="4"/>
<text x="{x0+L/2}" y="{cy+Wd/2+118}" font-size="40" font-weight="700" fill="var(--sand)" text-anchor="middle">長さ 約2.6m</text>
<line x1="{x0+L+40}" y1="{cy-Wd/2}" x2="{x0+L+40}" y2="{cy+Wd/2}" stroke="var(--sand)" stroke-width="4"/>
<line x1="{x0+L+26}" y1="{cy-Wd/2}" x2="{x0+L+54}" y2="{cy-Wd/2}" stroke="var(--sand)" stroke-width="4"/>
<line x1="{x0+L+26}" y1="{cy+Wd/2}" x2="{x0+L+54}" y2="{cy+Wd/2}" stroke="var(--sand)" stroke-width="4"/>
<text x="{x0+L+70}" y="{cy+12}" font-size="32" fill="var(--sand)">幅 約55cm</text>
<line x1="{hx-40}" y1="{gy-hh}" x2="{hx-40}" y2="{gy}" stroke="var(--sub)" stroke-width="4"/>
<line x1="{hx-54}" y1="{gy-hh}" x2="{hx-26}" y2="{gy-hh}" stroke="var(--sub)" stroke-width="4"/>
<line x1="{hx-54}" y1="{gy}" x2="{hx-26}" y2="{gy}" stroke="var(--sub)" stroke-width="4"/>
<text x="{hx+250}" y="{gy-hh/2-10}" font-size="32" fill="var(--ink)">身長</text>
<text x="{hx+250}" y="{gy-hh/2+32}" font-size="32" fill="var(--ink)">170cm</text>
<text x="{hx+250}" y="{gy-hh/2+70}" font-size="32" fill="var(--ink)">の人</text>"""
    svg = f"""<svg width="1680" height="640" viewBox="0 0 1680 640">{legs}{seg}{head}{human(hx, gy, hh)}{dim}
<text x="{x0}" y="{cy+Wd/2+190}" font-size="30" fill="var(--ink)">重さ 約50kg（推定）</text>
<text x="{x0}" y="{cy+Wd/2+236}" font-size="26" fill="var(--sub)">体の一部の化石（76cm×36cm）の幅から計算した、最大の推定値</text>
</svg>"""
    body = f"""<h1>アースロプレウラの大きさ　<small>上から見た姿と人を、同じ縮尺で（姿はおおまかな復元）</small></h1>
<div style="margin-top:-20px">{svg}</div>"""
    page("G05_アースロプレウラの大きさ", body, "Davies et al. (2022) Journal of the Geological Society 179")

# ---------- G06 翼の大きさ比べ ----------
def dragonfly(cx, cy, span, body_color="#7E6A4C", wing="rgba(232,228,218,.22)"):
    h = span / 2
    bl = span * 0.42
    w = ""
    for dy, ang, k in ((-bl*0.18, -8, 1.0), (bl*0.0, 8, 0.92)):
        for side in (-1, 1):
            ex = cx + side * h * k / 2
            w += (f'<ellipse cx="{ex}" cy="{cy+dy}" rx="{h*k/2}" ry="{span*0.045}" fill="{wing}" stroke="var(--ink)" stroke-width="2" '
                  f'transform="rotate({side*ang} {ex} {cy+dy})"/>')
    b = (f'<ellipse cx="{cx}" cy="{cy-bl*0.18}" rx="{span*0.025}" ry="{bl*0.14}" fill="{body_color}"/>'
         f'<rect x="{cx-span*0.011}" y="{cy-bl*0.05}" width="{span*0.022}" height="{bl*0.75}" rx="{span*0.011}" fill="{body_color}"/>'
         f'<circle cx="{cx}" cy="{cy-bl*0.34}" r="{span*0.03}" fill="{body_color}"/>')
    return w + b

def pigeon(cx, cy, span, color="#93A3B0"):
    h = span / 2
    bl = span * 0.5
    wing = lambda s: (f'<path d="M{cx} {cy-bl*0.08} C{cx+s*h*0.4} {cy-bl*0.25} {cx+s*h*0.85} {cy-bl*0.1} {cx+s*h} {cy+bl*0.02} '
                      f'C{cx+s*h*0.7} {cy+bl*0.12} {cx+s*h*0.35} {cy+bl*0.16} {cx} {cy+bl*0.14} Z" fill="{color}"/>')
    return (wing(-1) + wing(1)
            + f'<ellipse cx="{cx}" cy="{cy}" rx="{span*0.07}" ry="{bl*0.32}" fill="{color}"/>'
            + f'<circle cx="{cx}" cy="{cy-bl*0.34}" r="{span*0.045}" fill="{color}"/>'
            + f'<path d="M{cx-span*0.06} {cy+bl*0.25} L{cx+span*0.06} {cy+bl*0.25} L{cx+span*0.08} {cy+bl*0.5} L{cx-span*0.08} {cy+bl*0.5} Z" fill="{color}"/>')

def g06():
    pc = 9  # 1cmあたりのpx
    def dimbar(cx, y, lo, hi, color):
        s = ""
        if hi != lo:
            s += f'<line x1="{cx-hi*pc/2}" y1="{y}" x2="{cx+hi*pc/2}" y2="{y}" stroke="{color}" stroke-width="6" opacity=".4"/>'
        s += f'<line x1="{cx-lo*pc/2}" y1="{y}" x2="{cx+lo*pc/2}" y2="{y}" stroke="{color}" stroke-width="6"/>'
        for xx in {cx - hi*pc/2, cx + hi*pc/2, cx - lo*pc/2, cx + lo*pc/2}:
            s += f'<line x1="{xx}" y1="{y-12}" x2="{xx}" y2="{y+12}" stroke="{color}" stroke-width="4"/>'
        return s
    c1, c2, c3, cy, dy = 330, 1040, 1520, 230, 430
    svg = f"""<svg width="1680" height="640" viewBox="0 0 1680 640">
{dragonfly(c1, cy, 70*pc)}{pigeon(c2, cy, 67*pc)}{dragonfly(c3, cy, 19*pc, "#5E7A8A", "rgba(147,163,176,.3)")}
{dimbar(c1, dy, 70, 70, "var(--sand)")}{dimbar(c2, dy, 50, 67, "var(--sub)")}{dimbar(c3, dy, 19, 19, "var(--sub)")}
<text x="{c1}" y="{dy+60}" font-size="36" font-weight="700" fill="var(--sand)" text-anchor="middle">メガネウラ</text>
<text x="{c1}" y="{dy+108}" font-size="34" fill="var(--sand)" text-anchor="middle">約70cm</text>
<text x="{c2}" y="{dy+60}" font-size="36" font-weight="700" fill="var(--ink)" text-anchor="middle">ハト</text>
<text x="{c2}" y="{dy+108}" font-size="34" fill="var(--ink)" text-anchor="middle">50〜67cm</text>
<text x="{c3}" y="{dy+60}" font-size="30" font-weight="700" fill="var(--ink)" text-anchor="middle">いま最大の</text>
<text x="{c3}" y="{dy+98}" font-size="30" font-weight="700" fill="var(--ink)" text-anchor="middle">トンボの仲間</text>
<text x="{c3}" y="{dy+142}" font-size="34" fill="var(--ink)" text-anchor="middle">約19cm</text>
</svg>"""
    body = f"""<h1>翼を広げた長さ　<small>同じ縮尺で比べると（姿はおおまかな形）</small></h1>
<div style="margin-top:-30px">{svg}</div>
<div style="font-size:24px;margin-top:-30px" class="sub">いま最大はイトトンボの仲間（中南米）。トンボでは約16cm</div>"""
    page("G06_翼の大きさ比べ", body, "Nel et al. (2018) Scientific Reports ／ Cornell Lab \"All About Birds\" ／ BBC Wildlife")

# ---------- G07 空気の管の割合 ----------
def g07():
    def section(cx, cy, r, frac, seed):
        rnd = random.Random(seed)
        tubes, area = [], 0
        target = frac * r * r
        tries = 0
        while area < target and tries < 20000:
            tries += 1
            tr = rnd.uniform(7, 13)
            a, d = rnd.uniform(0, 2 * math.pi), math.sqrt(rnd.random()) * (r - tr - 8)
            x, y = cx + d * math.cos(a), cy + d * math.sin(a)
            if all((x - X) ** 2 + (y - Y) ** 2 > (tr + R + 3) ** 2 for X, Y, R in tubes):
                tubes.append((x, y, tr))
                area += tr * tr
        dots = "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{t:.1f}" fill="var(--ink)"/>' for x, y, t in tubes)
        return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#7E6A4C" stroke="#B49A70" stroke-width="4"/>{dots}'
    svg = f"""<svg width="1680" height="560" viewBox="0 0 1680 560">
{section(300, 260, 110, 0.05, 2)}{section(860, 260, 240, 0.22, 7)}
<text x="300" y="440" font-size="34" font-weight="700" fill="var(--ink)" text-anchor="middle">小さい虫</text>
<text x="300" y="484" font-size="28" fill="var(--sub)" text-anchor="middle">管の割合が小さい</text>
<path d="M450 260 H570" stroke="var(--sand)" stroke-width="6"/><path d="M554 244 L578 260 L554 276" fill="none" stroke="var(--sand)" stroke-width="6"/>
<text x="860" y="550" font-size="34" font-weight="700" fill="var(--ink)" text-anchor="middle">大きい虫　<tspan font-weight="400" font-size="28" fill="var(--sub)">管の割合が大きい</tspan></text>
<circle cx="1210" cy="80" r="12" fill="var(--ink)"/><text x="1234" y="91" font-size="28" fill="var(--ink)">空気の管</text>
<rect x="1198" y="120" width="24" height="24" rx="6" fill="#7E6A4C"/><text x="1234" y="142" font-size="28" fill="var(--ink)">体</text>
</svg>"""
    body = f"""<h1>体の中の空気の管　<small>体の輪切りのイメージ（数値ではない模式図）</small></h1>
<div style="display:flex;gap:40px;align-items:flex-start;margin-top:-20px">
 <div style="flex:none">{svg}</div>
</div>
<div style="position:absolute;left:1190px;top:340px;width:490px;font-size:30px;line-height:1.55">
 <div class="sand" style="font-weight:700">説</div>酸素が多ければ、管が少なくても<br>体の奥まで届く<br>→ 大きな体を持てた？
 <div class="sub" style="font-size:24px;margin-top:12px">化石が少なく、確かめも否定もできていない</div></div>"""
    page("G07_管の割合", body, "Harrison, Kaiser & VandenBrooks (2010) Proceedings of the Royal Society B")

# ---------- G08 虫の大きさと鳥 ----------
def g08():
    def mini(pts_o, pts_i, bird=False):
        W, H = 620, 230
        path = lambda pts: "M" + " L".join(f"{x*W:.0f} {H-y*H:.0f}" for x, y in pts)
        b = ""
        if bird:
            b = '<path d="M40 40 q25 -22 50 0 q25 -22 50 0 q-25 -8 -50 6 q-25 -14 -50 -6 z" fill="var(--ink)"/>'
        return f"""<svg width="{W}" height="{H+10}" viewBox="0 -5 {W} {H+10}">
<path d="{path(pts_o)}" fill="none" stroke="var(--sea)" stroke-width="6" stroke-dasharray="14 10"/>
<path d="{path(pts_i)}" fill="none" stroke="var(--sand)" stroke-width="7"/>{b}</svg>"""
    xs = [i / 8 for i in range(9)]
    o1 = list(zip(xs, [0.45, 0.7, 0.85, 0.6, 0.35, 0.5, 0.65, 0.5, 0.55]))
    i1 = [(x, y - 0.12) for x, y in o1]
    o2 = list(zip(xs, [0.35, 0.42, 0.5, 0.58, 0.66, 0.72, 0.78, 0.8, 0.82]))
    i2 = list(zip(xs, [0.3, 0.28, 0.3, 0.27, 0.29, 0.28, 0.3, 0.28, 0.29]))
    def panel(num, when, head, svg, note):
        return f"""<div class="card" style="flex:1;padding:30px 36px">
 <div style="font-size:26px" class="sub">{num}　{when}</div>
 <div style="font-size:34px;font-weight:700;margin:10px 0 18px;line-height:1.4">{head}</div>{svg}
 <div style="font-size:26px;margin-top:14px;line-height:1.5" class="sub">{note}</div></div>"""
    body = f"""<h1>最大の虫の大きさと、酸素・鳥　<small>化石の虫の羽、1万点以上を調べた研究</small></h1>
<div style="display:flex;gap:50px;align-items:stretch">
 {panel("①", "約3億年前〜約1億4500万年前", "最大の虫の大きさが<br>酸素の量と一緒に上下", mini(o1, i1), "")}
 {panel("②", "約1億4500万年前ごろから（白亜紀の前半）", "鳥が上手に飛ぶように<br>→ 酸素が増えても大きくならない", mini(o2, i2, True), "空を飛ぶ敵が、虫の大きさをおさえた？")}
</div>
<div style="font-size:26px;margin-top:22px"><span class="sea">- - 酸素の量</span>　<span class="sand">━ 最大の虫の大きさ</span>　<span class="sub">（線は説明のためのイメージで、実際のデータではない。化石の記録が足りないという反論もある）</span></div>"""
    page("G08_虫の大きさと鳥", body, "Clapham & Karr (2012) PNAS 109:10927")

# ---------- G09 石炭ができるまで ----------
def g09():
    def scene(kind):
        s = '<svg width="300" height="220" viewBox="0 0 300 220">'
        if kind == 1:   # 水びたしの森
            s += '<rect x="0" y="150" width="300" height="70" fill="#24506A"/>'
            for x in (60, 150, 240):
                s += f'<rect x="{x-7}" y="40" width="14" height="140" fill="#7E6A4C"/><ellipse cx="{x}" cy="40" rx="34" ry="20" fill="var(--green)"/>'
            s += '<path d="M0 150 q20 -6 40 0 t40 0 t40 0 t40 0 t40 0 t40 0 t40 0 t40 0" fill="none" stroke="var(--sea)" stroke-width="3"/>'
        elif kind == 2: # 倒れた木が積もる
            s += '<rect x="0" y="60" width="300" height="160" fill="#24506A"/>'
            s += '<rect x="0" y="150" width="300" height="70" fill="#3A2F24"/>'
            for y, x, w in ((158, 20, 200), (178, 80, 190), (198, 10, 230), (132, 60, 170)):
                s += f'<rect x="{x}" y="{y}" width="{w}" height="14" rx="7" fill="#7E6A4C"/>'
        elif kind == 3: # 土や砂に埋もれる
            for i, c in enumerate(("#C9B28A", "#A89270", "#C2AA80", "#8F7B5C")):
                s += f'<rect x="0" y="{20+i*30}" width="300" height="30" fill="{c}"/>'
            s += '<rect x="0" y="140" width="300" height="60" fill="#3A2F24"/>'
            for y, x, w in ((148, 20, 200), (172, 80, 190)):
                s += f'<rect x="{x}" y="{y}" width="{w}" height="12" rx="6" fill="#5E4E38"/>'
        else:           # 熱と重さで石炭に
            for i, c in enumerate(("#A89270", "#8F7B5C", "#7A6A4C", "#665840")):
                s += f'<rect x="0" y="{40+i*25}" width="300" height="25" fill="{c}"/>'
            s += '<rect x="0" y="140" width="300" height="34" fill="#141414"/><rect x="0" y="174" width="300" height="46" fill="#4A3C2C"/>'
            for x in (70, 150, 230):
                s += f'<path d="M{x} 0 V28" stroke="var(--ink)" stroke-width="5"/><path d="M{x-12} 16 L{x} 32 L{x+12} 16" fill="none" stroke="var(--ink)" stroke-width="5"/>'
            s += '<text x="150" y="212" font-size="26" fill="var(--red)" text-anchor="middle" font-weight="700">熱</text>'
        return s + "</svg>"
    body = f"""<h1>森が石炭になるまで　<small>長い時間をかけて</small></h1>
<div style="display:flex;align-items:stretch;height:560px">{steps_row([
        (scene(1), "水びたしの森", "地面はいつも<br>水につかっている"),
        (scene(2), "倒れた木が<br>腐らずに積もる", "その上にまた森が育ち<br>厚く重なる（泥炭）"),
        (scene(3), "土や砂に<br>埋もれる", "積み重なった層が<br>地面の下へ"),
        (scene(4), "熱と重さで<br>押し固められる", "こうしてできたのが<br><span class='ink' style='color:var(--ink)'>石炭</span>"),
    ])}</div>"""
    page("G09_石炭ができるまで", body, "UC Museum of Paleontology \"The Carboniferous Period\" ／ Kerp, H.（ミュンスター大学）")

# ---------- 2つの研究を並べる図（G10・G11） ----------
def two_cols(left, right, bottom):
    def col(year, head, items, color):
        lis = "".join(f'<div style="display:flex;gap:14px;margin-top:22px"><div style="color:{color}">●</div><div>{t}</div></div>' for t in items)
        return f"""<div class="card" style="flex:1;padding:34px 40px">
 <div style="font-size:30px;font-weight:700;color:{color}">{year}</div>
 <div style="font-size:36px;font-weight:700;margin-top:8px;line-height:1.4">{head}</div>
 <div style="font-size:30px;line-height:1.5">{lis}</div></div>"""
    return f"""<div style="display:flex;gap:50px;align-items:stretch;height:500px">{col(*left)}{col(*right)}</div>
<div style="font-size:32px;margin-top:30px;text-align:center" class="sand">{bottom}</div>"""

def g10():
    body = f"""<h1>なぜ石炭がたくさんできたのか　<small>二つの考え方</small></h1>
{two_cols(
        ("2012年の説", "木を分解するキノコが、まだいなかった？",
         ["木のかたくて分解されにくい成分を分解できるキノコが現れたのは、石炭紀の終わりごろだったかもしれない",
          "それまでは倒れた木が分解されず、たまり続けた"], "var(--sea)"),
        ("2016年の反論", "気候と土地のせいでは？",
         ["石炭のもとのリンボクの仲間は、幹のほとんどが樹皮で、かたい成分がもともと少なかった",
          "森の主役の植物が入れ替わっても、石炭のたまり方はほとんど同じ",
          "赤道の湿った気候と、大陸がぶつかってできた、沈んでいく低い土地が石炭を生んだ"], "var(--sand)"),
        "どちらが正しいのか、議論はいまも続いている")}"""
    page("G10_石炭の二つの説", body, "Floudas et al. (2012) Science 336:1715 ／ Nelsen et al. (2016) PNAS 113:2442")

def g11():
    body = f"""<h1>森の崩壊と動物たち　<small>約3億500万年前、湿地の森がばらばらに</small></h1>
{two_cols(
        ("2010年の研究", "森の崩壊が動物を変えた",
         ["水辺に卵を産む、カエルの遠い親戚たちは大きな打撃を受けた",
          "乾いた陸でも卵を産める爬虫類の仲間が広がった"], "var(--sea)"),
        ("2018年の研究", "化石のかたよりを補正すると",
         ["四本足の動物の種類は、石炭紀の終わり近くまで、むしろ増え続けていた",
          "大きく減ったのは、そのあと、次の時代（ペルム紀）との境目"], "var(--sand)"),
        "森の崩壊が動物たちの歴史をどこまで変えたのか、研究は続いている")}"""
    page("G11_森の崩壊の二つの研究", body, "Sahney, Benton & Falcon-Lang (2010) Geology ／ Dunne et al. (2018) Proceedings of the Royal Society B")

# ---------- G12 二つの道 ----------
def g12():
    rx, ry = 120, 330          # 根元
    bx = 560                   # 分かれ目
    up, dn = 150, 510
    svg = f"""<svg width="1680" height="660" viewBox="0 0 1680 660">
<path d="M{rx+250} {ry} H{bx}" stroke="var(--ink)" stroke-width="8"/>
<path d="M{bx} {ry} C{bx+80} {ry} {bx+60} {up} {bx+160} {up} H1180" stroke="var(--sea)" stroke-width="8" fill="none"/>
<path d="M{bx} {ry} C{bx+80} {ry} {bx+60} {dn} {bx+160} {dn} H1180" stroke="var(--sand)" stroke-width="8" fill="none"/>
<path d="M1170 {up-16} L1200 {up} L1170 {up+16}" fill="var(--sea)"/><path d="M1170 {dn-16} L1200 {dn} L1170 {dn+16}" fill="var(--sand)"/>
<circle cx="{bx}" cy="{ry}" r="14" fill="var(--ink)"/>
<text x="0" y="{ry+110}" font-size="26" fill="var(--sub)">石炭紀のうちに分かれた</text>
<text x="0" y="{ry+146}" font-size="26" fill="var(--sub)">（遅くとも約3億1500万年前）</text>
<circle cx="{bx+230}" cy="{up}" r="12" fill="var(--sea)"/>
<text x="{bx+230}" y="{up-30}" font-size="30" fill="var(--sea)" text-anchor="middle" font-weight="700">ヒロノムス</text>
<text x="{bx+230}" y="{up+50}" font-size="24" fill="var(--sub)" text-anchor="middle">最も古い爬虫類の一つ</text>
<circle cx="{bx+230}" cy="{dn}" r="12" fill="var(--sand)"/>
<text x="{bx+230}" y="{dn-30}" font-size="30" fill="var(--sand)" text-anchor="middle" font-weight="700">アサフェステラ</text>
<text x="{bx+230}" y="{dn+50}" font-size="24" fill="var(--sub)" text-anchor="middle">こちら側の最も古い化石とされる</text>
<text x="1230" y="{up-6}" font-size="38" font-weight="700" fill="var(--sea)">爬虫類の側</text>
<text x="1230" y="{up+42}" font-size="30" fill="var(--ink)">トカゲ・ワニ・恐竜・鳥</text>
<text x="1230" y="{dn-6}" font-size="38" font-weight="700" fill="var(--sand)">哺乳類の側</text>
<text x="1230" y="{dn+42}" font-size="30" fill="var(--ink)">私たち</text>
</svg>"""
    body = f"""<h1>二つの道　<small>殻のある卵を産む動物たちの枝分かれ</small></h1>
<div style="position:relative;margin-top:-50px">{svg}
 <div class="card" style="position:absolute;left:0;top:{ry-70}px;width:{250+rx}px;padding:18px 20px;font-size:30px;font-weight:700;line-height:1.35;text-align:center">殻のある卵を<br>産む動物</div>
</div>
<div style="font-size:24px;margin-top:-40px;line-height:1.5" class="sub">ヒロノムスもアサフェステラも、カナダ・ノバスコシアの崖（約3億1500万年前の地層）で見つかった<br>それぞれの側の初期の仲間で、私たちや恐竜の直接の祖先とは限らない</div>"""
    page("G12_二つの道", body, "Mann et al. (2020) Papers in Palaeontology ／ Falcon-Lang et al. (2006) Journal of the Geological Society")

# ---------- S07 約3億年前の大陸（おおまかな配置の模式図） ----------
# 組み立てでは pan_left（1.12倍に拡大して横に流す）なので、左右約210px・上下約60pxは隠れることがある。文字はその内側に置く
def s07():
    CX, CY, RX, RY = 960, 545, 590, 290
    def proj(lon, lat):
        """Mollweide 図法（古地理図でよく使われる楕円の地図）"""
        phi = math.radians(lat)
        t = phi
        for _ in range(30):
            if abs(math.cos(t)) < 1e-9:
                break
            t -= (2 * t + math.sin(2 * t) - math.pi * math.sin(phi)) / (2 + 2 * math.cos(2 * t))
        return CX + lon / 180 * RX * math.cos(t), CY - RY * math.sin(t)
    def line(pts):
        P = [proj(*p) for p in pts]
        return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in P)
    def rough(pts, seed, depth=2):
        """海岸線らしく見えるよう、辺を細かく分けて少しずらす（形は毎回同じ）"""
        rnd = random.Random(seed)
        for _ in range(depth):
            out = []
            for i, (a, b) in enumerate(zip(pts, pts[1:] + pts[:1])):
                dx, dy = b[0] - a[0], b[1] - a[1]
                k = rnd.uniform(-0.18, 0.18)
                out += [a, ((a[0] + b[0]) / 2 - dy * k, (a[1] + b[1]) / 2 + dx * k)]
            pts = out
        return pts
    def smooth(pts):
        """経度・緯度の点を投影して、なめらかな閉じた曲線にする（Catmull-Rom）"""
        P = [proj(*p) for p in pts]
        n = len(P)
        d = f"M{P[0][0]:.1f} {P[0][1]:.1f}"
        for i in range(n):
            p0, p1, p2, p3 = P[i - 1], P[i], P[(i + 1) % n], P[(i + 2) % n]
            c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
            c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
            d += f" C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p2[0]:.1f} {p2[1]:.1f}"
        return d + " Z"
    # 約3億年前（石炭紀後期）の陸地の形（PALEOMAP・Blakey の復元図を参考に単純化。経度・緯度は当時のもの）
    # 北アメリカ＋ヨーロッパ（赤道をまたぐ）。西は大きな海、東は東に開いた海に面する
    laurussia = [(-70, -11), (-80, -6), (-88, 2), (-94, 12), (-97, 22), (-96, 32), (-100, 40), (-94, 48), (-86, 55),
                 (-78, 60), (-64, 66), (-50, 70), (-36, 73), (-20, 72), (-8, 68), (4, 70), (16, 68), (28, 64),
                 (38, 60), (46, 54), (48, 46), (46, 38), (48, 30), (44, 22), (36, 15), (28, 10), (20, 7),
                 (10, 3), (0, -1), (-12, -4), (-26, -7), (-40, -9), (-54, -11)]
    # 南の巨大な大陸（いまの南アメリカ・アフリカ・南極・インド・オーストラリアなど）。北の縁が北アメリカ＋ヨーロッパとぶつかっている
    gondwana = [(-58, -10), (-44, -9), (-30, -7), (-16, -4), (-4, -2), (8, -1), (18, -3), (28, -6), (36, -5),
                (44, -8), (52, -14), (58, -20), (66, -24), (76, -26), (86, -30), (96, -34), (106, -36),
                (116, -40), (126, -46), (132, -54), (134, -62), (126, -70), (110, -78), (60, -86), (0, -88),
                (-60, -84), (-86, -72), (-94, -60), (-96, -48), (-92, -36), (-86, -26), (-80, -18), (-70, -13)]
    siberia = [(58, 54), (64, 48), (76, 46), (90, 50), (102, 54), (112, 60), (114, 68), (104, 76), (86, 80),
               (68, 78), (58, 70), (54, 62)]
    kazakh = [(54, 30), (62, 26), (72, 28), (80, 34), (80, 42), (70, 46), (60, 44), (55, 38)]
    tarim = [(84, 24), (94, 22), (98, 28), (92, 33), (84, 30)]
    nchina = [(100, 12), (110, 8), (122, 10), (128, 18), (122, 26), (110, 28), (102, 22)]
    schina = [(104, -6), (114, -9), (124, -5), (126, 2), (118, 6), (108, 4)]
    indochina = [(90, -12), (98, -15), (104, -12), (100, -6), (92, -7)]
    # 南の大陸の氷床（石炭紀後半に広がったり縮んだりした。ここではその広がりのおおよそ）
    ice = [(-94, -62), (-74, -58), (-50, -60), (-30, -56), (-8, -52), (14, -48), (34, -46), (56, -50), (78, -50),
           (98, -54), (118, -56), (138, -64), (130, -90), (-120, -90)]
    # 湿った森（石炭のもとになった森）：赤道付近の北アメリカ＋ヨーロッパと、中国のもとの陸地
    forest = [(-110, -9), (60, -9), (60, 13), (-110, 13)]
    forest_cn = [(98, -20), (140, -20), (140, 30), (98, 30)]
    laurussia, gondwana, siberia, kazakh, tarim, nchina, schina, indochina = [
        rough(p, i + 3) for i, p in enumerate((laurussia, gondwana, siberia, kazakh, tarim, nchina, schina, indochina))]
    ice = rough(ice, 21, 1)
    lands = (laurussia, gondwana, siberia, kazakh, tarim, nchina, schina, indochina)
    land_d = " ".join(smooth(p) for p in lands)
    cn_d = " ".join(smooth(p) for p in (nchina, schina))
    # ぶつかってできた山脈（北アメリカ＋ヨーロッパと南の大陸のあいだ／ヨーロッパの東の縁）
    mountains = [[(-66, -10), (-50, -8), (-34, -6), (-20, -3), (-8, 0), (4, 2), (16, 4), (26, 7)],
                 [(47, 26), (50, 36), (52, 46), (55, 56)]]
    grid = ""
    for lat in (-60, -30, 30, 60):
        a, b = proj(-180, lat), proj(180, lat)
        grid += f'<line x1="{a[0]:.0f}" y1="{a[1]:.0f}" x2="{b[0]:.0f}" y2="{b[1]:.0f}" stroke="#2C5A73" stroke-width="2"/>'
    e1, e2 = proj(-180, 0), proj(180, 0)
    grid += f'<line x1="{e1[0]:.0f}" y1="{CY}" x2="{e2[0]:.0f}" y2="{CY}" stroke="var(--sand)" stroke-width="3" stroke-dasharray="14 10" opacity=".85"/>'
    def arrow(lon1, lat1, lon2, lat2):
        a, b = proj(lon1, lat1), proj(lon2, lat2)
        ang = math.atan2(b[1] - a[1], b[0] - a[0])
        h1 = (b[0] - 18 * math.cos(ang - 0.5), b[1] - 18 * math.sin(ang - 0.5))
        h2 = (b[0] - 18 * math.cos(ang + 0.5), b[1] - 18 * math.sin(ang + 0.5))
        return (f'<line x1="{a[0]:.0f}" y1="{a[1]:.0f}" x2="{b[0]:.0f}" y2="{b[1]:.0f}" stroke="var(--ink)" stroke-width="5" stroke-linecap="round"/>'
                f'<path d="M{h1[0]:.0f} {h1[1]:.0f} L{b[0]:.0f} {b[1]:.0f} L{h2[0]:.0f} {h2[1]:.0f}" fill="none" stroke="var(--ink)" stroke-width="5" stroke-linecap="round"/>')
    def label(lon, lat, txt, size=28, color="var(--ink)", weight=700, anchor="middle"):
        x, y = proj(lon, lat)
        return (f'<text x="{x:.0f}" y="{y:.0f}" font-size="{size}" font-weight="{weight}" fill="{color}" text-anchor="{anchor}" '
                f'paint-order="stroke" stroke="rgba(15,30,43,.75)" stroke-width="6" stroke-linejoin="round">{txt}</text>')
    eq = proj(-180, 0)
    svg = f"""<svg width="1920" height="1080" viewBox="0 0 1920 1080" style="position:absolute;left:0;top:0">
<defs>
 <clipPath id="ocean"><ellipse cx="{CX}" cy="{CY}" rx="{RX}" ry="{RY}"/></clipPath>
 <clipPath id="land"><path d="{land_d}"/></clipPath>
 <clipPath id="cn"><path d="{cn_d}"/></clipPath>
 <radialGradient id="sea" cx="50%" cy="45%" r="60%"><stop offset="0" stop-color="#1B4660"/><stop offset="1" stop-color="#14354A"/></radialGradient>
</defs>
<ellipse cx="{CX}" cy="{CY}" rx="{RX}" ry="{RY}" fill="url(#sea)" stroke="#2C5A73" stroke-width="3"/>
<g clip-path="url(#ocean)">{grid}
 <path d="{land_d}" fill="#2F6E8A" stroke="#2F6E8A" stroke-width="26" stroke-linejoin="round"/>
 <path d="{land_d}" fill="#7A6A4C" stroke="#9C8A66" stroke-width="2"/>
 <g clip-path="url(#land)">
  <path d="{smooth(forest)}" fill="#4F8A5B" opacity=".95"/>
  <path d="{smooth(ice)}" fill="#E8EEF2"/>
 </g>
 <g clip-path="url(#cn)"><path d="{smooth(forest_cn)}" fill="#4F8A5B" opacity=".95"/></g>
 {"".join(f'<path d="{line(m)}" fill="none" stroke="#4E4030" stroke-width="16" stroke-linecap="round" stroke-linejoin="round"/>'
          f'<path d="{line(m)}" fill="none" stroke="#A89570" stroke-width="3" stroke-dasharray="2 9" stroke-linecap="round"/>' for m in mountains)}
</g>
{arrow(140, 62, 124, 62)}
{label(144, 60, '寄り集まる', 22, 'var(--ink)', 400, 'start')}
<text x="{eq[0]+24:.0f}" y="{CY-12}" font-size="26" fill="var(--sand)" font-weight="700">赤道</text>
{label(-52, 42, "いまの北アメリカと")}{label(-52, 31, "ヨーロッパ（つながっている）")}
{label(-30, -30, "南の巨大な大陸", 30)}
{label(-30, -38, "いまの南アメリカ・アフリカ・南極・", 22, "var(--ink)", 400)}
{label(-30, -45, "インド・オーストラリアなど", 22, "var(--ink)", 400)}
<text x="{proj(20, -72)[0]:.0f}" y="{proj(20, -72)[1]:.0f}" font-size="30" font-weight="700" fill="#2C4459" text-anchor="middle">氷床</text>
{label(80, 64, "いまのシベリア", 22, "var(--ink)", 400)}
{label(132, 16, "いまの中国のもと", 20, "var(--ink)", 400, "start")}
{label(-20, -16, "ぶつかってできた山脈", 22, "var(--sand)", 400)}
{label(-145, 20, "大きな海", 28, "var(--sea)", 400)}
{label(80, 2, "東に開いた海", 22, "var(--sea)", 400)}
</svg>"""
    legend = """<div style="position:absolute;left:1530px;top:640px;font-size:24px;line-height:1.7">
 <div><span style="display:inline-block;width:26px;height:18px;background:#4F8A5B;margin-right:10px"></span>湿った森</div>
 <div><span style="display:inline-block;width:26px;height:18px;background:#E8EEF2;margin-right:10px"></span>氷</div>
 <div><span style="display:inline-block;width:26px;height:18px;background:#7A6A4C;margin-right:10px"></span>陸地</div>
 <div><span style="display:inline-block;width:26px;height:8px;background:#4E4030;margin:0 10px 5px 0;vertical-align:middle"></span>山脈</div>
 <div><span style="display:inline-block;width:26px;height:18px;background:#2F6E8A;margin-right:10px"></span>浅い海</div></div>"""
    body = f"""{svg}
<div style="position:absolute;left:240px;top:110px">
 <div style="font-size:52px;font-weight:700;letter-spacing:.03em">約3億年前の大陸</div>
 <div style="font-size:26px;margin-top:8px" class="sub">石炭紀の終わりごろ。研究による復元をもとにした、おおまかな配置の模式図（輪郭は正確ではない）</div>
</div>{legend}"""
    page("S07_寄り集まる大陸", body, "Scotese, PALEOMAP Project ／ Blakey, Deep Time Maps の古地理図を参考に作図",
         wrap_style="inset:0", src_style="left:240px;bottom:205px")

for f in (g01, g02, g03, g04, g05, g06, g07, g08, g09, g10, g11, g12, s07):
    f()
