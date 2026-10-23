# 第6話の図（G01〜G14）をHTMLで作り、Edge（ヘッドレス）で1920x1080のPNGに変換する
# 使い方: python -I tools/make_graphics_ep06.py   （ONLY=G01,G07 のように指定すると、その図だけ作り直す）
# 数値はすべて scripts/ep06_cretaceous.txt のナレーションと factcheck_ep06.md に一致させること（そこに無い数字は足さない）
# 画面下約200pxは字幕用、右上（右から約350px・上から約150px）は信頼度の表示用に空ける
# 土台は tools/make_graphics_ep03.py（配色・フォント・出典の位置・変換の仕組みは同じ）
import subprocess, pathlib, html, tempfile, time, os, math

ONLY = [x for x in os.environ.get("ONLY", "").split(",") if x]
ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "images" / "ep06"
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

def badge(txt, color="var(--sand)"):
    return (f'<span style="display:inline-block;font-size:24px;font-weight:700;color:{color};border:2px solid {color};'
            f'border-radius:999px;padding:2px 16px;vertical-align:middle">{txt}</span>')

# ---------- 生き物の単純な影（どれも向きは左） ----------
def spino(x, ground, w, color="var(--sand)"):
    """スピノサウルス：細長い口先・背中の帆・上下に高い尾。箱の幅600を w に縮める（0〜600が頭の先〜尾の先）"""
    s = w / 600
    return f"""<g transform="translate({x},{ground}) scale({s})" fill="{color}">
<path d="M185 -172 Q215 -318 300 -330 Q385 -318 420 -168 Z" fill-opacity=".45"/>
<ellipse cx="300" cy="-150" rx="150" ry="44"/>
<path d="M180 -172 Q130 -206 92 -200 L8 -186 Q-2 -178 10 -171 L96 -163 Q132 -150 168 -128 Z"/>
<path d="M430 -178 Q520 -205 600 -150 Q520 -106 430 -122 Z"/>
<path d="M232 -118 L222 0 H250 L262 -112 Z"/><path d="M340 -118 L352 0 H380 L372 -114 Z"/>
<path d="M190 -140 L170 -96 L184 -92 L204 -134 Z"/></g>"""

def mosa(x, y_mid, w, color="var(--sea)"):
    """モササウルスの仲間：細長い体・4枚のひれ・下向きに曲がった尾びれ。箱の幅600を w に縮める"""
    s = w / 600
    return f"""<g transform="translate({x},{y_mid}) scale({s})" fill="{color}">
<path d="M0 0 Q20 -14 70 -20 L120 -27 Q260 -40 400 -20 Q470 -10 520 -3 L582 -22 L560 6 L600 54 L515 14 Q470 16 400 18 Q260 32 120 22 L70 14 Q20 10 0 0 Z"/>
<path d="M150 20 Q132 58 104 70 Q152 64 182 22 Z"/><path d="M330 20 Q322 60 294 74 Q346 64 362 20 Z"/>
<path d="M170 16 Q160 50 136 62 Q182 54 196 18 Z" fill-opacity=".55"/><path d="M350 18 Q345 52 322 64 Q370 56 380 18 Z" fill-opacity=".55"/>
<path d="M6 2 Q40 6 78 4" stroke="#0F1E2B" stroke-width="3" fill="none"/>
<circle cx="58" cy="-8" r="5" fill="#0F1E2B"/></g>"""

def trex(x, ground, w, color="var(--red)", slim=False):
    """ティラノサウルス型の肉食恐竜：大きな頭・短い前脚・水平の尾。箱の幅400を w に縮める。slim=True で細身"""
    s = w / 400
    ry = 34 if slim else 48
    head = "M0 -200 Q8 -232 60 -236 Q100 -234 112 -208 L118 -176 Q90 -170 60 -176 L10 -184 Z" if not slim else \
           "M8 -204 Q16 -228 58 -230 Q92 -228 102 -206 L106 -184 Q80 -180 56 -184 L16 -190 Z"
    return f"""<g transform="translate({x},{ground}) scale({s})" fill="{color}">
<path d="{head}"/>
<path d="M96 -210 Q130 -190 150 -160 L170 -150 L150 -130 Q120 -150 92 -178 Z"/>
<ellipse cx="200" cy="-150" rx="80" ry="{ry}"/>
<path d="M260 -176 Q340 -170 400 -150 Q340 -134 262 -122 Z"/>
<path d="M150 -132 L132 -112 L140 -108 L160 -126 Z"/>
<path d="M186 -120 L176 -60 L160 0 H190 L198 -60 L216 -116 Z"/><path d="M232 -120 L236 -60 L226 0 H256 L258 -60 L262 -124 Z"/></g>"""

# ---------- G01 年表：白亜紀の位置 ----------
def g01():
    L, R, W = 152, 58, 1680          # 1億5200万年前 → 5800万年前（帯の位置を決めるためだけの目盛り）
    x = lambda ma: (L - ma) / (L - R) * W
    k0, k1 = 143.1, 66.00
    by0, by1 = 236, 306              # 年表の帯の上下
    def flag(ma, y, lines, anchor="start", color="var(--ink)", y_from=None):
        """目盛りから旗のように文字を出す。lines=[(文字, 大きさ, 太さ, 色)]"""
        px = x(ma)
        dx = 12 if anchor == "start" else -12
        yy = y
        t = ""
        for txt, fs, fw, c in lines:
            yy += fs + 6
            t += f'<text x="{px+dx:.0f}" y="{yy}" font-size="{fs}" font-weight="{fw}" fill="{c}" text-anchor="{anchor}">{txt}</text>'
        top, bot = (y + 4, by0) if y < by0 else (by1, yy + 8)
        line = f'<line x1="{px:.0f}" y1="{top}" x2="{px:.0f}" y2="{bot}" stroke="{color}" stroke-width="3"/>'
        dot = f'<circle cx="{px:.0f}" cy="{by0 if y < by0 else by1}" r="8" fill="{color}"/>'
        return line + dot + t
    S, I, D = "var(--sand)", "var(--ink)", "var(--sub)"
    svg = f"""<svg width="1680" height="700" viewBox="0 0 1680 700" style="overflow:visible">
<rect x="0" y="{by0}" width="{x(k0):.0f}" height="{by1-by0}" fill="#2F5160"/>
<text x="{x(k0)/2:.0f}" y="{by0+46}" font-size="28" fill="var(--ink)" text-anchor="middle">ジュラ紀</text>
<rect x="{x(k0):.0f}" y="{by0-8}" width="{x(k1)-x(k0):.0f}" height="{by1-by0+16}" rx="10" fill="#4E7048" stroke="var(--sand)" stroke-width="4"/>
<text x="{(x(k0)+x(k1))/2:.0f}" y="{by0+52}" font-size="44" font-weight="700" fill="var(--ink)" text-anchor="middle">白亜紀</text>
<rect x="{x(k1):.0f}" y="{by0}" width="{W-x(k1):.0f}" height="{by1-by0}" fill="#4A4E5A"/>
<text x="{(x(k1)+W)/2:.0f}" y="{by0+46}" font-size="26" fill="var(--ink)" text-anchor="middle">新生代</text>
{flag(k0, 110, [("1億4310万年前", 30, 700, S), ("白亜紀の始まり", 24, 400, D)], color=S)}
{flag(k1, 110, [("6600万年前", 30, 700, S), ("白亜紀の終わり", 24, 400, D)], color=S)}
{flag(125, 0, [("約1億2500万年前", 26, 700, I), ("羽毛の恐竜・最初の花（中国・遼寧省）", 26, 400, I)])}
{flag(113.2, 110, [("1億1320万年前〜（アルビアン期）", 26, 700, I), ("花の植物が急に増え始める", 26, 400, I)])}
{flag(72, 0, [("約7200万年前", 26, 700, I), ("むかわ竜・ワカヤマソウリュウ", 26, 400, I)], anchor="end")}
{flag(95, 330, [("約9500万年前", 26, 700, I), ("スピノサウルス", 26, 400, I)])}
{flag(120, 420, [("約1億2000万年前", 26, 700, I), ("福井の恐竜", 26, 400, I), ("アプチアン期：1億2140万〜1億1320万年前", 22, 400, D)])}
{flag(70, 420, [("約7000万年前", 26, 700, I), ("ケツァルコアトルス", 26, 400, I)], anchor="end")}
<text x="0" y="590" font-size="24" fill="var(--sub)">長さを比べると（同じ縮尺）</text>
<rect x="{x(k0):.0f}" y="604" width="{x(k1)-x(k0):.0f}" height="40" rx="6" fill="#4E7048"/>
<text x="{x(k0)+16:.0f}" y="634" font-size="26" font-weight="700" fill="var(--ink)">白亜紀が続いた長さ　約7700万年</text>
<rect x="{x(k0):.0f}" y="654" width="{66*W/(L-R):.0f}" height="40" rx="6" fill="#4A4E5A"/>
<text x="{x(k0)+16:.0f}" y="684" font-size="26" font-weight="700" fill="var(--ink)">恐竜の絶滅から今日まで　6600万年</text>
</svg>"""
    body = f"""<h1 style="margin-bottom:10px">白亜紀はいつ？</h1>
<div>{svg}</div>"""
    page("G01_年表", body, "国際年代層序表 v2026/06 ／ Sun et al. (2002) Science ／ Hattori et al. (2023) ／ UCMP ／ Sereno et al. (2022) ／ Kobayashi et al. (2019) ほか")

# ---------- パンゲアの模式図（第3話と同じ形） ----------
PANGAEA = [(200, 80), (350, 46), (520, 56), (680, 88), (810, 140), (770, 205), (650, 232), (545, 268), (610, 312),
           (730, 345), (810, 390), (770, 465), (630, 545), (455, 578), (300, 545), (215, 460), (175, 360), (150, 250), (160, 150)]

def land_svg(extra="", cracks="", w=760, h=560, sc=0.8, ox=0, oy=0):
    P = [(px * sc + ox, py * sc + oy) for px, py in PANGAEA]
    return f"""<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<rect x="0" y="0" width="{w}" height="{h}" rx="30" fill="#163C52" stroke="#2C5A73" stroke-width="3"/>
<path d="{smooth_px(P)}" fill="#2F6E8A" stroke="#2F6E8A" stroke-width="22" stroke-linejoin="round"/>
<path d="{smooth_px(P)}" fill="#8A6A46" stroke="#B0906A" stroke-width="3"/>
{cracks}{extra}</svg>"""

# ---------- G02 分かれていく大陸 ----------
def g02():
    sc, ox, oy = 0.8, 20, 30
    def T(pts):
        return " ".join(f"{px*sc+ox:.0f},{py*sc+oy:.0f}" for px, py in pts)
    # 裂け目（海の色の太い線で陸を分ける）。位置は説明のための模式で、実際の裂け目の場所ではない
    c1 = [(140, 300), (260, 285), (360, 300), (470, 280), (548, 268)]
    c2 = [(470, 300), (460, 380), (500, 450), (470, 600)]
    cracks = (f'<polyline points="{T(c1)}" fill="none" stroke="#163C52" stroke-width="26" stroke-linejoin="round"/>'
              f'<polyline points="{T(c2)}" fill="none" stroke="#163C52" stroke-width="22" stroke-linejoin="round"/>'
              f'<polyline points="{T(c1)}" fill="none" stroke="var(--red)" stroke-width="4" stroke-dasharray="12 8"/>'
              f'<polyline points="{T(c2)}" fill="none" stroke="var(--red)" stroke-width="4" stroke-dasharray="12 8"/>')
    def arr(x1, y1, x2, y2):
        a = math.atan2(y2 - y1, x2 - x1)
        hx, hy = x2 - 22 * math.cos(a), y2 - 22 * math.sin(a)
        px, py = 13 * -math.sin(a), 13 * math.cos(a)
        return (f'<line x1="{x1}" y1="{y1}" x2="{hx:.0f}" y2="{hy:.0f}" stroke="var(--sand)" stroke-width="7" stroke-linecap="round"/>'
                f'<path d="M{x2} {y2} L{hx+px:.0f} {hy+py:.0f} L{hx-px:.0f} {hy-py:.0f} Z" fill="var(--sand)"/>')
    arrows = arr(380, 190, 380, 120) + arr(250, 380, 210, 440) + arr(480, 400, 540, 450)
    left = land_svg(w=720, h=540, sc=sc, ox=ox, oy=oy)
    right = land_svg(arrows, cracks, w=720, h=540, sc=sc, ox=ox, oy=oy)
    body = f"""<h1>大陸が分かれ始める　<small>ひとつにつながっていた大陸に、裂け目が入っていく（模式図）</small></h1>
<div style="display:flex;gap:30px;align-items:center;margin-top:-10px">
 <div style="text-align:center"><div style="font-size:32px;font-weight:700;margin-bottom:12px" class="sub">それまで</div>{left}</div>
 <div style="font-size:64px;padding-top:40px" class="sand">→</div>
 <div style="text-align:center"><div style="font-size:32px;font-weight:700;margin-bottom:12px" class="sand">白亜紀の初めには、もう裂け始めていた</div>{right}</div>
</div>
<div style="font-size:26px;margin-top:14px;line-height:1.5" class="sub">陸が離ればなれになり、生き物もそれぞれの土地で別の道を歩む。形・裂け目の位置は説明のための模式図（正確ではない）</div>"""
    page("G02_分かれていく大陸", body, "UC Museum of Paleontology \"The Cretaceous Period\"")

# ---------- G03 北アメリカを貫く海 ----------
def g03():
    # 北アメリカのおおまかな塊（実際の輪郭ではない）と、北の海から南の海へ続く浅い海の帯
    land = [(150, 60), (420, 30), (700, 50), (860, 110), (880, 240), (820, 380), (720, 470), (560, 540), (430, 560),
            (330, 520), (230, 430), (150, 300), (110, 170)]
    sea_band = "M470 0 C430 120 470 200 440 300 C410 400 460 470 450 600 L560 600 C570 470 520 400 550 300 C580 200 540 120 590 0 Z"
    svg = f"""<svg width="1000" height="600" viewBox="0 0 1000 600">
<defs><clipPath id="cl"><path d="{smooth_px(land)}"/></clipPath></defs>
<rect x="0" y="0" width="1000" height="600" rx="30" fill="#163C52" stroke="#2C5A73" stroke-width="3"/>
<path d="{smooth_px(land)}" fill="#8A6A46" stroke="#B0906A" stroke-width="3"/>
<path d="{sea_band}" fill="#3F87A3" clip-path="url(#cl)"/>
<path d="{sea_band}" fill="#3F87A3" opacity=".55"/>
<text x="500" y="300" font-size="34" font-weight="700" fill="var(--ink)" text-anchor="middle" paint-order="stroke" stroke="rgba(15,30,43,.55)" stroke-width="6">浅い海</text>
<text x="300" y="250" font-size="30" font-weight="700" fill="var(--ink)" text-anchor="middle">西の陸</text>
<text x="720" y="250" font-size="30" font-weight="700" fill="var(--ink)" text-anchor="middle">東の陸</text>
<text x="530" y="34" font-size="26" fill="var(--sea)" text-anchor="start" dx="70">北の海（北極海）へ</text>
<text x="500" y="590" font-size="26" fill="var(--sea)" text-anchor="end" dx="-70">南の海（いまのメキシコ湾）へ</text>
<path d="M500 60 V20 M486 34 L500 18 L514 34" stroke="var(--sea)" stroke-width="5" fill="none"/>
<path d="M505 540 V585 M491 571 L505 587 L519 571" stroke="var(--sea)" stroke-width="5" fill="none"/>
<circle cx="330" cy="330" r="12" fill="var(--sand)"/><text x="360" y="380" font-size="24" fill="var(--sand)" text-anchor="middle">恐竜たちが暮らした</text>
</svg>"""
    body = f"""<h1>北アメリカを貫く浅い海　<small>白亜紀の後半（模式図。陸と海の形は正確ではない）</small></h1>
<div style="display:flex;gap:56px;align-items:flex-start;margin-top:-14px">
 <div style="flex:none">{svg}</div>
 <div style="padding-top:60px">
  <div style="font-size:30px" class="sub">白亜紀の後半</div>
  <div style="font-size:40px;font-weight:700;margin-top:8px;line-height:1.4" class="sea">世界中で<br>海面が高かった</div>
  <div style="font-size:30px;margin-top:50px" class="sub">北アメリカの西部の気候</div>
  <div style="font-size:40px;font-weight:700;margin-top:8px;line-height:1.4" class="sand">暖かく、<br>季節ごとに雨</div>
  <div style="margin-top:46px">{badge("推定")}</div>
 </div>
</div>"""
    page("G03_北アメリカを貫く海", body, "Hooper Virtual Natural History Museum (Carleton University) \"Ceratopsid ecology\"")

# ---------- G04 花の植物が増える時期 ----------
def g04():
    L, R, W = 145, 50, 1680
    x = lambda ma: (L - ma) / (L - R) * W
    k0, k1 = 143.1, 66.00
    alb0, alb1 = 113.2, 100.5
    ay = 330
    svg = f"""<svg width="1680" height="560" viewBox="0 0 1680 560">
<rect x="{x(k0):.0f}" y="{ay-30}" width="{x(k1)-x(k0):.0f}" height="60" rx="8" fill="#4E7048"/>
<text x="{x(k0)+20:.0f}" y="{ay+12}" font-size="30" font-weight="700" fill="var(--ink)">白亜紀</text>
<rect x="{x(k1):.0f}" y="{ay-30}" width="{W-x(k1)-30:.0f}" height="60" fill="#4A4E5A"/>
<path d="M{W-30} {ay-30} L{W} {ay} L{W-30} {ay+30} Z" fill="#4A4E5A"/>
<text x="{x(k1)+20:.0f}" y="{ay+12}" font-size="28" fill="var(--ink)">新生代</text>
<rect x="{x(alb0):.0f}" y="{ay-46}" width="{x(alb1)-x(alb0):.0f}" height="92" rx="8" fill="var(--sand)" opacity=".85"/>
<text x="{x(k0):.0f}" y="{ay+76}" font-size="24" fill="var(--sub)" text-anchor="start">1億4310万年前</text>
<text x="{x(k1):.0f}" y="{ay+76}" font-size="24" fill="var(--sub)" text-anchor="middle">6600万年前</text>

<line x1="{x(125):.0f}" y1="{ay-30}" x2="{x(125):.0f}" y2="226" stroke="var(--green)" stroke-width="4"/>
<circle cx="{x(125):.0f}" cy="{ay}" r="12" fill="var(--green)"/>
<text x="{x(125)-10:.0f}" y="150" font-size="30" font-weight="700" fill="var(--green)" text-anchor="end">① 最初の化石</text>
<text x="{x(125)-10:.0f}" y="194" font-size="28" fill="var(--ink)" text-anchor="end">約1億2500万年前</text>

<line x1="{(x(alb0)+x(alb1))/2:.0f}" y1="{ay-46}" x2="{(x(alb0)+x(alb1))/2:.0f}" y2="226" stroke="var(--sand)" stroke-width="4"/>
<text x="{x(alb0)+10:.0f}" y="150" font-size="30" font-weight="700" fill="var(--sand)">② 急に種類を増やし始める</text>
<text x="{x(alb0)+10:.0f}" y="194" font-size="28" fill="var(--ink)">アルビアン期（白亜紀の中ごろ）　1億1320万〜1億50万年前</text>

<line x1="{x(55):.0f}" y1="{ay+30}" x2="{x(55):.0f}" y2="{ay+120}" stroke="var(--red)" stroke-width="4"/>
<circle cx="{x(55):.0f}" cy="{ay}" r="12" fill="var(--red)"/>
<text x="{x(55)+10:.0f}" y="{ay+164}" font-size="30" font-weight="700" fill="var(--red)" text-anchor="end">③ 森の主役になる</text>
<text x="{x(55)+10:.0f}" y="{ay+206}" font-size="28" fill="var(--ink)" text-anchor="end">新生代（恐竜の時代のあと）</text>
</svg>"""
    body = f"""<h1>花を咲かせる植物が増えていった時期　<small>3つの節目（種類の数のグラフではない）</small></h1>
<div style="margin-top:-70px">{svg}</div>
<div style="font-size:28px;margin-top:-4px" class="sub">白亜紀の終わりでも、景色の主役はまだシダやソテツの仲間などだった</div>"""
    page("G04_花の植物が増える時期", body, "UC Museum of Paleontology \"Angiosperms: Fossil Record\"・\"The Cretaceous Period\" ／ 国際年代層序表 v2026/06")

# ---------- G05 スピノサウルスの全長 ----------
def g05():
    m = 90            # 1mあたりのpx
    x0 = 40
    gy = 450          # 影の足もと
    def spino_flat(length, color, op=1):
        s = length * m / 600
        return (f'<g opacity="{op}"><g transform="translate({x0},{gy}) scale(1,0.45) translate({-x0},{-gy})">'
                f'{spino(x0, gy, length*m, color)}</g></g>')
    def bar(y, length, color, txt, val, more=False):
        b = f'<rect x="{x0}" y="{y}" width="{length*m:.0f}" height="44" rx="6" fill="{color}"/>'
        end = x0 + length * m
        if more:
            b += (f'<rect x="{end:.0f}" y="{y}" width="40" height="44" fill="{color}" opacity=".4"/>'
                  f'<path d="M{end+46:.0f} {y+6} L{end+70:.0f} {y+22} L{end+46:.0f} {y+38} Z" fill="{color}" opacity=".7"/>')
            end += 76
        return (b + f'<text x="{x0+18}" y="{y+32}" font-size="28" font-weight="700" fill="#0F1E2B">{txt}</text>'
                f'<text x="{end+18:.0f}" y="{y+36}" font-size="40" font-weight="700" fill="{color}">{val}</text>')
    ticks = "".join(f'<line x1="{x0+k*m}" y1="{gy+150}" x2="{x0+k*m}" y2="{gy+166}" stroke="var(--sub)" stroke-width="3"/>'
                    f'<text x="{x0+k*m}" y="{gy+200}" font-size="26" fill="var(--sub)" text-anchor="middle">{k}m</text>' for k in range(0, 16, 5))
    svg = f"""<svg width="1680" height="660" viewBox="0 0 1680 660">
{spino_flat(15, "#A88A5A", .45)}
{spino_flat(13.9, "var(--sand)")}
<line x1="0" y1="{gy}" x2="1680" y2="{gy}" stroke="var(--sub)" stroke-width="2"/>
{human(x0+15.9*m, gy, 1.7*m)}
<text x="{x0+15.9*m+8:.0f}" y="{gy-1.7*m-14:.0f}" font-size="24" fill="var(--sub)" text-anchor="middle">人</text>
{bar(gy+24, 15, "#A88A5A", "2014年の研究の復元", "15m超", True)}
{bar(gy+82, 13.9, "var(--sand)", "2022年の研究の復元", "14m足らず")}
<line x1="{x0}" y1="{gy+158}" x2="{x0+15*m}" y2="{gy+158}" stroke="var(--sub)" stroke-width="3"/>{ticks}
</svg>"""
    body = f"""<h1>スピノサウルスの全長　<small>研究によって見積もりが分かれる（薄い影＝2014年、濃い影＝2022年。姿はおおまか）</small></h1>
<div style="margin-top:-20px">{svg}</div>"""
    page("G05_スピノサウルスの全長", body, "Sereno et al. (2022) eLife 11:e80092 ／ Ibrahim et al. (2014) Science 345:1613")

# ---------- G06 骨の密度 ----------
def g06():
    def section(solid):
        if solid:
            core = '<circle cx="200" cy="200" r="150" fill="#E2D6BC"/>' + "".join(
                f'<circle cx="{200+r*math.cos(a):.0f}" cy="{200+r*math.sin(a):.0f}" r="4" fill="#C9BB9C"/>'
                for r in (40, 80, 115) for a in [i * math.pi / (4 + r // 30) for i in range(2 * (4 + r // 30))])
        else:
            core = ('<circle cx="200" cy="200" r="150" fill="#E2D6BC"/>'
                    '<circle cx="200" cy="200" r="105" fill="#0F1E2B" stroke="#C9BB9C" stroke-width="4"/>')
        return f'<svg width="340" height="340" viewBox="0 0 400 400">{core}<circle cx="200" cy="200" r="150" fill="none" stroke="#B0A07E" stroke-width="6"/></svg>'
    def card(svg, head, note, border="var(--line)", hc="var(--ink)"):
        return f"""<div class="card" style="flex:1;padding:24px 30px;text-align:center;border-color:{border}">
 <div style="font-size:36px;font-weight:700;color:{hc}">{head}</div>
 <div style="margin-top:16px">{svg}</div>
 <div style="font-size:32px;margin-top:14px;font-weight:700">{note}</div></div>"""
    body = f"""<h1>脚の骨の断面　<small>骨を輪切りにしたところ（模式図）</small></h1>
<div style="display:flex;gap:60px;align-items:stretch;height:520px;margin-top:-10px">
 {card(section(False), "陸の恐竜の脚の骨", "中が空洞")}
 {card(section(True), "スピノサウルスの脚の骨", "中までぎっしり詰まっている", "var(--sand)", "var(--sand)")}
</div>
<div style="font-size:30px;margin-top:22px;text-align:center">2022年の研究：骨がぎっしり詰まっている → <span class="sand">水にもぐって、えさを探していた</span>と考えた（推定）</div>"""
    page("G06_骨の密度", body, "Ibrahim et al. (2014) Science 345:1613 ／ Fabbri et al. (2022) Nature 603:852")

# ---------- G07 二つの説 ----------
def g07():
    def icon(under):
        s = '<svg width="520" height="200" viewBox="0 0 520 200">'
        if under:
            s += '<rect x="0" y="40" width="520" height="160" rx="16" fill="#1E4E66"/>'
            s += '<path d="M0 40 Q30 28 60 40 T120 40 T180 40 T240 40 T300 40 T360 40 T420 40 T480 40 T540 40" stroke="var(--sea)" stroke-width="4" fill="none"/>'
            s += f'<g transform="rotate(4 260 140)">{spino(110, 200, 300, "var(--sand)")}</g>'
        else:
            s += '<path d="M0 172 H250 Q275 172 295 186 L315 200 H0 Z" fill="#7E6A4C"/>'
            s += '<path d="M290 182 Q330 178 520 178 V200 H315 Z" fill="#1E4E66"/>'
            s += spino(60, 174, 300, "var(--sand)")
        return s + "</svg>"
    def card(head, svg, items, color):
        lis = "".join(f'<div style="font-size:26px;font-weight:700;margin-top:16px;color:{color}">{a}</div><div style="font-size:29px;line-height:1.45;margin-top:2px">{b}</div>' for a, b in items)
        return f"""<div class="card" style="flex:1;padding:22px 30px;border-color:{color}">
 <div style="font-size:40px;font-weight:700;color:{color};text-align:center">{head}</div>
 <div style="text-align:center;margin-top:8px">{svg}</div>{lis}</div>"""
    body = f"""<h1>スピノサウルスは水の中で暮らした？　<small>研究によって正反対の考え</small></h1>
<div style="display:flex;gap:30px;align-items:stretch;height:600px;margin-top:-14px">
 {card("水にもぐる狩人", icon(True), [("2020年の研究", "ひれのような尾。模型を水の中で動かす実験から、泳ぐための尾"), ("2022年の研究", "ぎっしり詰まった骨。水にもぐって、えさを探した")], "var(--sea)")}
 <div style="align-self:center;text-align:center;width:150px;flex:none"><div style="font-size:30px;font-weight:700;line-height:1.4" class="sand">論争は<br>続いている</div><div style="font-size:48px" class="sand">⇄</div></div>
 {card("水辺で待つ釣り人", icon(False), [("2022年の研究（全身の模型）", "深い水の中では体が不安定で、泳ぐのも遅い"), ("同じ研究", "陸では二本足。浅い水辺で待ち伏せ。<br>内陸の川の地層にも化石")], "var(--sand)")}
</div>"""
    page("G07_二つの説", body, "Ibrahim et al. (2020) Nature 581:67 ／ Fabbri et al. (2022) Nature 603:852 ／ Sereno et al. (2022) eLife 11:e80092")

# ---------- G08 日本の恐竜の年表 ----------
def g08():
    L, R, W = 130, 62, 1680
    x = lambda ma: (L - ma) / (L - R) * W
    ay = 120
    def card(px, top, w, place, items, color, align="left"):
        lis = "".join(f'<div style="font-size:28px;line-height:1.45;margin-top:6px">{t}</div>' for t in items)
        return f"""<div class="card" style="position:absolute;left:{px}px;top:{top}px;width:{w}px;padding:16px 24px;border-color:{color}">
 <div style="font-size:32px;font-weight:700;color:{color}">{place}</div>{lis}</div>"""
    fx, mx = x(120), x(72)
    svg = f"""<svg width="1680" height="170" viewBox="0 0 1680 170" style="position:absolute;left:0;top:0;overflow:visible">
<rect x="0" y="{ay-24}" width="{x(66):.0f}" height="48" rx="8" fill="#4E7048"/>
<text x="20" y="{ay+10}" font-size="26" fill="var(--ink)">白亜紀</text>
<rect x="{x(66):.0f}" y="{ay-24}" width="{W-x(66):.0f}" height="48" fill="#4A4E5A"/>
<line x1="{x(66):.0f}" y1="{ay-40}" x2="{x(66):.0f}" y2="{ay+40}" stroke="var(--sand)" stroke-width="4"/>
<text x="{x(66):.0f}" y="{ay-78}" font-size="24" fill="var(--sand)" text-anchor="middle">白亜紀の終わり</text><text x="{x(66):.0f}" y="{ay-48}" font-size="24" fill="var(--sand)" text-anchor="middle">6600万年前</text>
<circle cx="{fx:.0f}" cy="{ay}" r="16" fill="var(--sand)"/><circle cx="{mx:.0f}" cy="{ay}" r="16" fill="var(--sea)"/>
<text x="{fx:.0f}" y="{ay-46}" font-size="34" font-weight="700" fill="var(--sand)" text-anchor="middle">約1億2000万年前</text>
<text x="{mx:.0f}" y="{ay-46}" font-size="34" font-weight="700" fill="var(--sea)" text-anchor="end" dx="50">約7200万年前</text>
<line x1="{fx:.0f}" y1="{ay+16}" x2="{fx:.0f}" y2="170" stroke="var(--sand)" stroke-width="4"/>
<line x1="{mx:.0f}" y1="{ay+16}" x2="{mx:.0f}" y2="170" stroke="var(--sea)" stroke-width="4"/>
</svg>"""
    body = f"""<h1>日本で見つかった、白亜紀の化石　<small>年表で並べたもの（当時の日本の形と位置は、いまとは違う）</small></h1>
<div style="position:relative;height:620px;margin-top:-10px">{svg}
 {card(0, 170, 600, "福井県勝山市", ["フクイラプトル（2000年命名）", "ティラノミムス（2023年命名）"], "var(--sand)")}
 {card(960, 170, 720, "北海道むかわ町（約7200万年前）", ["カムイサウルス「むかわ竜」（2019年命名）", "フォスフォロサウルス<span class='sub' style='font-size:24px'>（海の爬虫類）</span>"], "var(--sea)")}
 {card(960, 380, 720, "和歌山県（7200万年以上前）", ["ワカヤマソウリュウ（2023年命名）<span class='sub' style='font-size:24px'>（海の爬虫類）</span>"], "var(--sea)")}
</div>"""
    page("G08_日本の恐竜の年表", body, "Azuma & Currie (2000) ／ Hattori et al. (2023) ／ Kobayashi et al. (2019) ／ Konishi et al. (2016, 2023) ／ 北海道大学 (2018)")

# ---------- G09 水深 ----------
def g09():
    # 横：陸 → 浜 → 浅い海 → 外側の大陸棚 → 深い海。縦の長さは誇張した模式図
    sea_top = 150
    d80, d200 = 290, 410   # 水深80m・200mにあたる線の高さ（模式）
    floor = (f"M0 120 L360 120 Q420 120 450 {sea_top} L560 215 L800 {d80+12} L1360 {d200-22} "
             f"L1520 640 L1680 660 V680 H0 Z")
    bx, by = 1120, 362     # 骨の印（海底の上）
    svg = f"""<svg width="1680" height="680" viewBox="0 0 1680 680">
<rect x="450" y="{sea_top}" width="1230" height="530" fill="#1E4E66"/>
<path d="M450 {sea_top} H1680" stroke="var(--sea)" stroke-width="4"/>
<rect x="800" y="{d80}" width="560" height="{d200-d80}" fill="var(--sand)" opacity=".16"/>
<path d="{floor}" fill="#6E5A40"/>
<path d="M0 120 L360 120 Q420 120 450 {sea_top}" stroke="#B0906A" stroke-width="4" fill="none"/>
<line x1="760" y1="{d80}" x2="1460" y2="{d80}" stroke="var(--sub)" stroke-width="2" stroke-dasharray="10 8"/>
<line x1="760" y1="{d200}" x2="1460" y2="{d200}" stroke="var(--sub)" stroke-width="2" stroke-dasharray="10 8"/>
<text x="1470" y="{d80+9}" font-size="26" fill="var(--ink)">水深 約80m</text>
<text x="1470" y="{d200+9}" font-size="26" fill="var(--ink)">水深 約200m</text>
<g transform="translate({bx},{by}) rotate(-8)"><rect x="-34" y="-7" width="68" height="14" rx="7" fill="var(--ink)"/>
<circle cx="-34" cy="-8" r="10" fill="var(--ink)"/><circle cx="-34" cy="8" r="10" fill="var(--ink)"/>
<circle cx="34" cy="-8" r="10" fill="var(--ink)"/><circle cx="34" cy="8" r="10" fill="var(--ink)"/></g>
<line x1="{bx}" y1="{by+26}" x2="{bx}" y2="470" stroke="var(--sand)" stroke-width="3"/>
<text x="{bx}" y="512" font-size="34" font-weight="700" fill="var(--sand)" text-anchor="middle">ここで見つかった</text>
<text x="{bx}" y="556" font-size="28" fill="var(--ink)" text-anchor="middle">水深 約80〜200mの海の底でできた地層</text>
<text x="180" y="90" font-size="34" font-weight="700" fill="var(--ink)" text-anchor="middle">陸</text>
<text x="640" y="{sea_top+46}" font-size="30" fill="var(--ink)" text-anchor="middle">浅い海</text>
<text x="1000" y="{sea_top+46}" font-size="30" fill="var(--ink)" text-anchor="middle">沖の海（外側の大陸棚）</text>
<path d="M300 112 C 520 50 860 60 1080 {sea_top-8}" stroke="var(--sand)" stroke-width="6" fill="none" stroke-dasharray="16 10"/>
<path d="M1100 {sea_top-2} L1068 {sea_top-24} L1064 {sea_top+4} Z" fill="var(--sand)"/>
<path d="M1108 {sea_top+70} L{bx} {by-30}" stroke="var(--sand)" stroke-width="4" fill="none" stroke-dasharray="8 8"/>
<text x="680" y="56" font-size="28" fill="var(--sand)" text-anchor="middle">陸の恐竜の体が、死んだあと海まで流された？（推定）</text>
</svg>"""
    body = f"""<h1>むかわ竜が見つかった場所　<small>海岸から沖への断面（模式図。深さは大げさに描いている）</small></h1>
<div style="margin-top:-60px">{svg}</div>"""
    page("G09_水深", body, "北海道大学・むかわ町穂別博物館 プレスリリース（2018年9月5日） ／ Kobayashi et al. (2019) Scientific Reports 9:12389")

# ---------- G10 モササウルスの大きさ ----------
def g10():
    m = 86
    x0 = 30
    by = 330
    bus_w = 11 * m
    bus = f"""<g transform="translate({x0},560)">
<rect x="0" y="-120" width="{bus_w}" height="104" rx="16" fill="none" stroke="var(--sub)" stroke-width="5"/>
{''.join(f'<rect x="{40+i*92}" y="-104" width="70" height="40" rx="6" fill="none" stroke="var(--sub)" stroke-width="3"/>' for i in range(10))}
<circle cx="150" cy="-14" r="24" fill="#0F1E2B" stroke="var(--sub)" stroke-width="5"/><circle cx="{bus_w-170}" cy="-14" r="24" fill="#0F1E2B" stroke="var(--sub)" stroke-width="5"/>
</g>"""
    ticks = "".join(f'<line x1="{x0+k*m}" y1="606" x2="{x0+k*m}" y2="622" stroke="var(--sub)" stroke-width="3"/>'
                    f'<text x="{x0+k*m}" y="656" font-size="26" fill="var(--sub)" text-anchor="middle">{k}m</text>' for k in range(0, 19, 5))
    svg = f"""<svg width="1680" height="670" viewBox="0 0 1680 670">
{mosa(x0, by-30, 11.5*m, "var(--sea)")}
<rect x="{x0}" y="{by+80}" width="{11*m}" height="30" fill="var(--sea)"/>
<rect x="{x0+11*m}" y="{by+80}" width="{1*m}" height="30" fill="var(--sea)" opacity=".7"/>
<rect x="{x0+12*m}" y="{by+80}" width="{5*m}" height="30" fill="var(--sea)" opacity=".18"/>
<rect x="{x0+17*m}" y="{by+80}" width="{1*m}" height="30" fill="none" stroke="var(--sea)" stroke-width="3" stroke-dasharray="6 5"/>
<text x="{x0+12*m+20}" y="{by-50}" font-size="44" font-weight="700" fill="var(--sea)">11〜12mほど</text>
<text x="{x0+18*m}" y="{by+62}" font-size="28" fill="var(--ink)" text-anchor="end">17〜18mとする見方も</text>

<text x="{x0+bus_w+20}" y="520" font-size="28" fill="var(--sub)">大型の路線バス（約11m）</text>
{bus}
<line x1="{x0}" y1="614" x2="{x0+18*m}" y2="614" stroke="var(--sub)" stroke-width="3"/>{ticks}
</svg>"""
    body = f"""<h1>最も大きなモササウルスの仲間　<small>モササウルス・ホフマニ。大きさは研究によって見積もりが分かれる（姿はおおまか）</small></h1>
<div style="margin-top:-110px">{svg}</div>"""
    page("G10_モササウルスの大きさ", body, "Natural History Museum (London) \"What is a mosasaur?\"")

# ---------- G11 成長の速さ ----------
def g11():
    x0, y0, W, H = 120, 560, 1180, 420     # 年齢0〜30歳の横軸
    ax = lambda age: x0 + age / 30 * W
    f = lambda age: 1 / (1 + math.exp(-(age - 13) / 2.2))
    pts = " ".join(f"{ax(a/10):.1f},{y0 - 20 - f(a/10) * (H - 40):.1f}" for a in range(0, 281))
    xm = ax(13); ym = y0 - 20 - 0.5 * (H - 40)
    ticks = "".join(f'<line x1="{ax(a):.0f}" y1="{y0}" x2="{ax(a):.0f}" y2="{y0+14}" stroke="var(--sub)" stroke-width="3"/>'
                    f'<text x="{ax(a):.0f}" y="{y0+48}" font-size="26" fill="var(--sub)" text-anchor="middle">{a}歳</text>' for a in (0, 10, 20, 30))
    svg = f"""<svg width="1680" height="640" viewBox="0 0 1680 640">
<line x1="{x0}" y1="{y0}" x2="{x0+W+30}" y2="{y0}" stroke="var(--sub)" stroke-width="3"/>
<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y0-H-20}" stroke="var(--sub)" stroke-width="3"/>
<text x="{x0-16}" y="{y0-H-30}" font-size="26" fill="var(--sub)" text-anchor="start">体重 ↑</text>
<text x="{x0+W+44}" y="{y0+9}" font-size="26" fill="var(--sub)" text-anchor="start">年齢 →</text>
{ticks}
<polyline points="{pts}" fill="none" stroke="var(--sand)" stroke-width="7" stroke-linejoin="round"/>
<line x1="{xm-90:.0f}" y1="{ym+150:.0f}" x2="{xm+90:.0f}" y2="{ym-150:.0f}" stroke="var(--red)" stroke-width="4" stroke-dasharray="10 8"/>
<circle cx="{xm:.0f}" cy="{ym:.0f}" r="12" fill="var(--red)"/>
<text x="{xm-30:.0f}" y="{ym-60:.0f}" font-size="34" font-weight="700" fill="var(--red)" text-anchor="end">最も速く育つ時期</text>
<text x="{xm-30:.0f}" y="{ym-16:.0f}" font-size="30" fill="var(--ink)" text-anchor="end">1日に 約2.1kg 増える</text>
<line x1="{ax(20):.0f}" y1="{y0}" x2="{ax(20):.0f}" y2="{y0-H+10}" stroke="var(--sea)" stroke-width="4" stroke-dasharray="8 6"/>
<text x="{ax(20)+14:.0f}" y="{y0-140}" font-size="32" font-weight="700" fill="var(--sea)">約20年で</text>
<text x="{ax(20)+14:.0f}" y="{y0-100}" font-size="28" fill="var(--ink)">骨が大人の体に</text>
<line x1="{ax(28):.0f}" y1="{y0}" x2="{ax(28):.0f}" y2="{y0-H+10}" stroke="var(--green)" stroke-width="4" stroke-dasharray="8 6"/>
<text x="{ax(28)+14:.0f}" y="{y0-H+40}" font-size="32" font-weight="700" fill="var(--green)">最長 約28歳</text>
</svg>"""
    body = f"""<h1>ティラノサウルスの育ち方　<small>骨に残る成長のしるしから（2004年の研究）。線は説明のための模式図</small></h1>
<div style="margin-top:-50px">{svg}</div>"""
    page("G11_成長の速さ", body, "Erickson et al. (2004) Nature 430:772")

# ---------- G12 かむ力 ----------
def g12():
    weight = """<svg width="420" height="430" viewBox="0 0 420 430">
<path d="M110 40 H310 L350 200 H70 Z" fill="#5A6470" stroke="var(--ink)" stroke-width="4"/>
<path d="M170 40 Q170 0 210 0 Q250 0 250 40" fill="none" stroke="var(--ink)" stroke-width="10"/>
<text x="210" y="148" font-size="56" font-weight="700" fill="var(--ink)" text-anchor="middle">約6トン</text>
<path d="M210 210 V260" stroke="var(--sand)" stroke-width="8"/><path d="M188 250 L210 282 L232 250 Z" fill="var(--sand)"/>
<path d="M160 300 Q210 286 260 300 L232 410 Q210 424 188 410 Z" fill="#F2EDE2"/>
<text x="300" y="380" font-size="26" fill="var(--sub)">歯</text>
</svg>"""
    body = f"""<h1>ティラノサウルスのかむ力　<small>あごの筋肉の模型をコンピューターで動かした推定（2012年の研究）</small></h1>
<div style="display:flex;gap:60px;align-items:center;margin-top:-10px">
 <div style="flex:1">
  <div style="font-size:32px" class="sub">奥の歯1本にかかる力</div>
  <div style="font-size:84px;font-weight:700;margin-top:6px;line-height:1.2" class="sand">3万5000〜<br>5万7000ニュートン</div>
  <div style="font-size:30px;margin-top:14px">陸の動物で見積もられた中で、飛び抜けて強い</div>
  <div class="card" style="display:inline-block;padding:20px 34px;margin-top:36px;font-size:34px;line-height:1.5">
   <b class="sand">5万7000ニュートン</b> ≒ <b>約6トン</b>の重さが<br>歯の先にのしかかる力</div>
  <div style="font-size:28px;margin-top:30px" class="sub">別の研究（2017年）：獲物の骨まで、くり返しかみ砕いて食べていた</div>
 </div>
 <div style="flex:none">{weight}</div>
</div>"""
    page("G12_かむ力", body, "Bates & Falkingham (2012) Biology Letters 8:660 ／ Gignac & Erickson (2017) Scientific Reports 7:2012")

# ---------- G13 子どもか別の恐竜か ----------
def g13():
    left = f"""<svg width="620" height="230" viewBox="0 0 620 230">
<line x1="10" y1="220" x2="610" y2="220" stroke="var(--sub)" stroke-width="3"/>
{trex(20, 220, 330, "var(--red)")}{trex(390, 220, 190, "#D98A6E", slim=True)}
<text x="485" y="40" font-size="26" fill="var(--sub)" text-anchor="middle">育ちざかりの子ども</text>
</svg>"""
    right = f"""<svg width="620" height="230" viewBox="0 0 620 230">
<line x1="10" y1="220" x2="610" y2="220" stroke="var(--sub)" stroke-width="3"/>
{trex(20, 220, 330, "var(--red)")}{trex(390, 220, 190, "var(--sea)", slim=True)}
<text x="485" y="40" font-size="26" fill="var(--sea)" text-anchor="middle" font-weight="700">別の恐竜？</text>
</svg>"""
    def card(year, svg, txt, color):
        return f"""<div class="card" style="flex:1;padding:22px 30px;border-color:{color}">
 <div style="font-size:34px;font-weight:700;color:{color}">{year}</div>
 <div style="text-align:center;margin-top:6px">{svg}</div>
 <div style="font-size:29px;line-height:1.5;margin-top:10px">{txt}</div></div>"""
    body = f"""<h1>子どものティラノサウルス？　<small>二つの研究</small></h1>
<div style="display:flex;gap:30px;align-items:stretch;height:500px;margin-top:-14px">
 {card("2021年の研究", left, "巨大な肉食恐竜のいる場所には、<br>中くらいの肉食恐竜が少ない。<br>そのすき間を、<b class='sand'>子どものティラノサウルス</b>が埋めていた？", "var(--sand)")}
 {card("2025年の研究", right, "子どもと考えられてきた化石の一部は、<br><b class='sea'>ナノティラヌス</b>という別の恐竜だった", "var(--sea)")}
</div>
<div style="font-size:32px;margin-top:24px;text-align:center"><span class="sand">正しければ</span>、育ち方や暮らし方をめぐる多くの考えを見直す必要がある　{badge("説が分かれている")}</div>"""
    page("G13_子どもか別の恐竜か", body, "Schroeder, Lyons & Smith (2021) Science 371:941 ／ Zanno & Napoli (2025) Nature 648:357")

# ---------- G14 化石の調査 ----------
def g14():
    data = [("トリケラトプス", 40, 72), ("ティラノサウルス", 24, 44), ("エドモントサウルス", 20, 36), ("テスケロサウルス", 8, 15),
            ("オルニトミムス", 5, 9), ("パキケファロサウルス", 1, 2), ("アンキロサウルス", 1, 2)]
    x0, sc, rh = 420, 26, 72
    rows = ""
    for i, (name, pct, n) in enumerate(data):
        y = 20 + i * rh
        hi = i < 2
        c = "var(--sand)" if i == 0 else "var(--red)" if i == 1 else "#5E7486"
        rows += (f'<text x="{x0-24}" y="{y+40}" font-size="{34 if hi else 30}" font-weight="{700 if hi else 400}" fill="var(--ink)" text-anchor="end">{name}</text>'
                 f'<rect x="{x0}" y="{y+8}" width="{max(pct*sc, 8)}" height="{50}" rx="6" fill="{c}"/>'
                 f'<text x="{x0+max(pct*sc, 8)+18}" y="{y+44}" font-size="{36 if hi else 28}" font-weight="{700 if hi else 400}" fill="{"var(--ink)" if hi else "var(--sub)"}">{pct}%<tspan font-size="24" fill="var(--sub)" font-weight="400">（{n}点）</tspan></text>')
    svg = f"""<svg width="1680" height="540" viewBox="0 0 1680 540">
<line x1="{x0}" y1="10" x2="{x0}" y2="{20+len(data)*rh}" stroke="var(--sub)" stroke-width="3"/>{rows}
</svg>"""
    body = f"""<h1>大型の恐竜の化石の割合　<small>モンタナ州ヘルクリーク層（1999〜2009年の調査）</small></h1>
<div style="margin-top:-10px">{svg}</div>
<div style="font-size:26px;margin-top:-6px" class="sub">（　）は見つかった化石の数</div>"""
    page("G14_化石の調査", body, "Horner, Goodwin & Myhrvold (2011) PLoS ONE 6:e16574")

for f in (g01, g02, g03, g04, g05, g06, g07, g08, g09, g10, g11, g12, g13, g14):
    f()
