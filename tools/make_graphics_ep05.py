# 第5話（ジュラ紀）の図（G01〜G16）をHTMLで作り、Edge（ヘッドレス）で1920x1080のPNGに変換する
# 使い方: python -I tools/make_graphics_ep05.py   （ONLY=G01,G07 のように指定すると、その図だけ作り直す）
# 数値はすべて scripts/ep05_jurassic.txt のナレーションと factcheck_ep05.md に一致させること（そこに無い数字は足さない）
# 画面下約200pxは字幕用、右上（右から約350px・上から約150px）は信頼度の表示用に空ける
# 土台は tools/make_graphics_ep03.py（配色・フォント・出典の位置・Edgeでの書き出しは同じ）
import subprocess, pathlib, html, tempfile, time, os, math

ONLY = [x for x in os.environ.get("ONLY", "").split(",") if x]
ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "images" / "ep05"
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

# 時代の帯の色（第3話の年表と同じ系統）
C_TRI, C_JUR, C_CRE = "#4A4E5A", "#3E6B4A", "#3E5F7A"
C_J1, C_J2, C_J3 = "#35603F", "#4A7A50", "#5E8E5C"

# ---------- 生き物の単純な影（どれも向きは左） ----------
def sauropod(x, ground, w, neck="flat", color="var(--sand)"):
    """首の長い恐竜（竜脚類）：小さな頭・長い首・長い尾・四本足。全長（頭の先〜尾の先）が w になる。
    neck="flat" は首を水平に近く、"up" は首を高く持ち上げた姿"""
    s = w / 1000
    if neck == "up":
        nk = ('<path d="M410 -212 Q330 -340 272 -500 L304 -512 Q374 -350 442 -172 Z"/>'
              '<ellipse cx="266" cy="-516" rx="36" ry="16" transform="rotate(-14 266 -516)"/>')
    else:
        nk = ('<path d="M420 -228 Q240 -262 62 -258 L62 -236 Q240 -232 405 -168 Z"/>'
              '<ellipse cx="44" cy="-247" rx="38" ry="16"/>')
    return f"""<g transform="translate({x},{ground}) scale({s})" fill="{color}">
{nk}
<ellipse cx="530" cy="-188" rx="172" ry="62" transform="rotate(-4 530 -188)"/>
<path d="M684 -228 Q850 -215 1000 -128 Q845 -185 684 -166 Z"/>
<path d="M412 -175 L404 0 H440 L450 -175 Z"/><path d="M458 -170 L456 0 H484 L490 -170 Z" opacity=".75"/>
<path d="M592 -190 L586 0 H630 L638 -190 Z"/><path d="M640 -185 L640 0 H672 L678 -185 Z" opacity=".75"/></g>"""

def stego(x, ground, w, color="var(--sand)", plate="var(--sand)"):
    """ステゴサウルス：背中に2列の板、尾の先にとげ、小さな頭、四本足。全長 w"""
    s = w / 1000
    plates = ""
    for i, (px, ph) in enumerate([(300, 70), (360, 105), (425, 135), (495, 150), (565, 140), (635, 115), (700, 85), (760, 60)]):
        dx = 18 if i % 2 else -18
        op = ".6" if i % 2 else "1"
        plates += f'<path d="M{px-34+dx} -300 Q{px+dx} {-300-ph*1.25} {px+34+dx} -300 Z" fill="{plate}" opacity="{op}"/>'
    return f"""<g transform="translate({x},{ground}) scale({s})" fill="{color}">
{plates}
<path d="M240 -250 Q330 -340 520 -330 Q700 -320 790 -250 Q860 -200 1000 -205 L1000 -190 Q860 -170 780 -175 Q560 -150 360 -170 Q260 -180 240 -250 Z"/>
<path d="M260 -230 Q160 -230 110 -205 Q70 -190 60 -170 Q110 -160 170 -170 Q230 -180 280 -195 Z"/>
<circle cx="100" cy="-188" r="7" fill="#0F1E2B"/>
<path d="M300 -190 L290 0 H330 L345 -185 Z"/><path d="M620 -200 L615 0 H665 L680 -205 Z"/>
<path d="M940 -205 L985 -275 L960 -200 Z M900 -200 L935 -265 L925 -198 Z M945 -190 L995 -140 L960 -192 Z M905 -188 L945 -130 L928 -190 Z"/></g>"""

def archaeo(x, y, s, color="var(--sand)", ink="var(--ink)"):
    """始祖鳥：羽根の翼（持ち上げた姿）・歯のある口・骨の入った長い尾（両側に羽根）・手にかぎ爪の指。600x420 の箱、向きは左"""
    tailf = "".join(f'<ellipse cx="{400+i*36}" cy="{232+i*2.2:.0f}" rx="26" ry="9" transform="rotate(-24 {400+i*36} {232+i*2.2:.0f})"/>'
                    f'<ellipse cx="{400+i*36}" cy="{266+i*2.2:.0f}" rx="26" ry="9" transform="rotate(24 {400+i*36} {266+i*2.2:.0f})"/>' for i in range(6))
    wing = "M282 212 L240 140 L205 92 L178 60 L230 46 L282 50 L326 70 L356 104 L366 146 L350 186 L305 214 Z"
    seps = "".join(f'<path d="M{ax} {ay} L{bx} {by}" stroke="#0F1E2B" stroke-width="3" opacity=".5"/>' for ax, ay, bx, by in
                   [(205, 92, 280, 50), (222, 116, 326, 70), (240, 140, 356, 104), (258, 165, 366, 146), (272, 190, 350, 186)])
    teeth = "".join(f'<path d="M{112+i*9} 160 l3 7 l3 -7 z" fill="{ink}"/>' for i in range(4))
    return f"""<g transform="translate({x},{y}) scale({s})" fill="{color}">
<g opacity=".85">{tailf}</g>
<path d="M370 232 Q480 242 600 252 L600 264 Q480 262 370 262 Z"/>
<path d="M318 282 L310 380 M342 282 L352 378" stroke="{color}" stroke-width="12" stroke-linecap="round"/>
<path d="M310 380 l-26 6 M310 380 l18 8 M352 378 l-24 8 M352 378 l20 6" stroke="{color}" stroke-width="7" stroke-linecap="round"/>
<ellipse cx="310" cy="244" rx="86" ry="50" transform="rotate(-8 310 244)"/>
<path d="M250 222 Q208 196 186 166 L206 152 Q230 184 272 204 Z"/>
<ellipse cx="172" cy="156" rx="38" ry="23"/>
<path d="M144 146 L106 160 L144 168 Z"/>{teeth}
<circle cx="166" cy="148" r="5" fill="#0F1E2B"/>
<path d="{wing}" opacity=".92"/>{seps}
<path d="M186 66 q-22 -2 -26 16 M182 60 q-18 -12 -32 -2 M188 56 q-6 -20 -24 -18" stroke="{ink}" stroke-width="5" fill="none" stroke-linecap="round"/></g>"""

def bird_icon(x, y, s, color="var(--sea)"):
    """いまの鳥（小鳥の横向き）。100x80 の箱"""
    return f"""<g transform="translate({x},{y}) scale({s})" fill="{color}">
<ellipse cx="52" cy="44" rx="30" ry="20"/><circle cx="26" cy="28" r="14"/><path d="M14 26 L0 30 L14 34 Z"/>
<path d="M78 40 L100 30 L96 50 Z"/><path d="M40 36 Q62 22 84 40 Q62 44 40 46 Z" fill="#0F1E2B" opacity=".35"/>
<path d="M48 62 L46 78 M58 62 L60 78" stroke="{color}" stroke-width="4"/></g>"""

def feathered_dino(x, y, s, color="var(--sand)", ink="var(--ink)"):
    """羽毛の小さな恐竜（アンキオルニスの単純な影）：二本足、前脚と後ろ脚に長い羽根。200x150 の箱"""
    return f"""<g transform="translate({x},{y}) scale({s})" fill="{color}">
<ellipse cx="100" cy="70" rx="40" ry="24"/><path d="M70 60 Q50 40 40 30 L52 24 Q66 40 84 54 Z"/>
<ellipse cx="38" cy="24" rx="18" ry="11"/><path d="M24 20 L8 25 L24 30 Z"/>
<path d="M136 66 Q170 70 200 78 Q170 82 136 80 Z"/>
<path d="M86 74 L60 110 L70 112 L96 80 Z" opacity=".8"/><path d="M60 110 L40 118 L66 116 Z" fill="{ink}" opacity=".8"/>
<path d="M108 88 L112 140 M116 88 L124 140" stroke="{color}" stroke-width="7"/>
<path d="M112 110 L92 132 M124 112 L106 136" stroke="{ink}" stroke-width="4" opacity=".8"/></g>"""

def plant_dino(x, y, s, color="var(--green)", ink="var(--ink)"):
    """二本足の小さな植物食の恐竜（クリンダドロメウスの単純な影）：頭や胸に糸のような羽毛、尾にうろこ。200x150"""
    fuzz = "".join(f'<path d="M{30+i*9} {46-((i*7)%10)} l-4 -12" stroke="{ink}" stroke-width="3"/>' for i in range(7))
    scales = "".join(f'<path d="M{142+i*12} {76+i*1.2:.0f} q6 -8 12 0" stroke="#0F1E2B" stroke-width="2.5" fill="none"/>' for i in range(4))
    return f"""<g transform="translate({x},{y}) scale({s})" fill="{color}">
<ellipse cx="100" cy="72" rx="42" ry="26"/><path d="M68 60 Q52 46 42 38 L54 30 Q68 44 84 54 Z"/>
<ellipse cx="38" cy="34" rx="20" ry="12"/>
<path d="M138 64 Q172 70 200 82 Q172 88 138 84 Z"/>{scales}
<path d="M80 86 L74 108 M88 88 L84 108" stroke="{color}" stroke-width="5"/>
<path d="M108 92 L112 142 M120 92 L128 142" stroke="{color}" stroke-width="8"/>{fuzz}</g>"""

def pterosaur(x, y, s, color="var(--sea)"):
    """翼竜：膜の翼、長い尾。200x120 の箱（上から見た形）"""
    return f"""<g transform="translate({x},{y}) scale({s})" fill="{color}">
<path d="M100 50 Q60 20 0 34 Q50 46 86 70 Z"/><path d="M100 50 Q140 20 200 34 Q150 46 114 70 Z"/>
<ellipse cx="100" cy="62" rx="14" ry="24"/><path d="M92 40 L100 6 L108 40 Z"/>
<path d="M100 84 L100 118" stroke="{color}" stroke-width="4"/><path d="M94 116 L100 124 L106 116 Z"/></g>"""

def mammal(x, y, s, color="var(--sand)"):
    """小さな哺乳類の仲間（横向き、毛に覆われた体）。160x80 の箱"""
    return f"""<g transform="translate({x},{y}) scale({s})" fill="{color}">
<ellipse cx="86" cy="46" rx="52" ry="26"/><ellipse cx="36" cy="40" rx="24" ry="17"/><path d="M14 38 L0 44 L14 48 Z"/>
<circle cx="30" cy="34" r="3" fill="#0F1E2B"/><circle cx="44" cy="26" r="7"/>
<path d="M60 66 L56 80 M110 66 L114 80" stroke="{color}" stroke-width="7" stroke-linecap="round"/></g>"""

def time_axis(L, R, W, top, bands, ticks, band_h=70, tick_h=150):
    """年代の帯と目盛り（年代は「何百万年前」）。bands=[(古い, 新しい, 色, 名前, 文字の大きさ)]、
    ticks=[(年代, 文字, 色, 寄せ方 "c"/"l"/"r")]"""
    x = lambda ma: (L - ma) / (L - R) * W
    out = ""
    for a, b, bg, name, fs in bands:
        out += (f'<div style="position:absolute;left:{x(a):.0f}px;top:{top}px;width:{x(b)-x(a):.0f}px;height:{band_h}px;background:{bg};'
                f'display:flex;align-items:center;justify-content:center;font-size:{fs}px;white-space:nowrap;overflow:hidden">{name}</div>')
    for ma, txt, color, al in ticks:
        out += f'<div style="position:absolute;left:{x(ma)-2:.0f}px;top:{top-10}px;width:4px;height:{tick_h}px;background:{color}"></div>'
        if al == "l":
            pos = f"left:{x(ma)-6:.0f}px;text-align:left"
        elif al == "r":
            pos = f"left:{x(ma)-334:.0f}px;text-align:right"
        else:
            pos = f"left:{x(ma)-170:.0f}px;text-align:center"
        out += f'<div style="position:absolute;{pos};top:{top+tick_h}px;width:340px;font-size:28px;line-height:1.35;color:{color}">{txt}</div>'
    return out, x

# ---------- G01 年表：ジュラ紀の位置 ----------
def g01():
    L, R, W = 206, 138.5, 1680
    ax, x = time_axis(L, R, W, 330, [
        (L, 201.4, C_TRI, "三畳紀", 30),
        (201.4, 174.7, C_J1, "ジュラ紀 前期", 34),
        (174.7, 161.5, C_J2, "中期", 34),
        (161.5, 143.1, C_J3, "後期", 34),
        (143.1, R, C_CRE, "白亜紀", 30),
    ], [
        (201.4, "<b>約2億140万年前</b>", "var(--sand)", "l"),
        (174.7, "約1億7470万年前<br><span style='font-size:24px'>中期の始まり</span>", "var(--sub)", "c"),
        (161.5, "約1億6150万年前<br><span style='font-size:24px'>後期の始まり</span>", "var(--sub)", "c"),
        (143.1, "<b>約1億4310万年前</b>", "var(--sand)", "r"),
    ])
    def ev(ma, row, txt, color, al="c", ma2=None):
        top = 20 if row == 0 else 160
        c = x(ma)
        if ma2 is not None:
            c2 = x(ma2)
            mark = (f'<div style="position:absolute;left:{c:.0f}px;top:{top+86}px;width:{c2-c:.0f}px;height:12px;background:{color};border-radius:6px"></div>'
                    f'<div style="position:absolute;left:{(c+c2)/2-2:.0f}px;top:{top+98}px;width:4px;height:{330-top-98:.0f}px;background:{color}"></div>')
            c = (c + c2) / 2
        else:
            mark = f'<div style="position:absolute;left:{c-2:.0f}px;top:{top+86}px;width:4px;height:{330-top-86:.0f}px;background:{color}"></div>'
        if al == "l":
            pos = f"left:{c-10:.0f}px;text-align:left"
        elif al == "r":
            pos = f"left:{c-390:.0f}px;text-align:right"
        else:
            pos = f"left:{c-200:.0f}px;text-align:center"
        return mark + f'<div style="position:absolute;{pos};top:{top}px;width:400px;font-size:28px;line-height:1.35;color:{color}">{txt}</div>'
    body = f"""<h1>ジュラ紀はいつ？　<small>三畳紀のすぐあとに続いた時代</small></h1>
<div style="position:relative;height:600px;margin-top:-20px">
 {ev(201.6, 0, "<b>三畳紀の終わりの大量絶滅</b><br>約2億160万年前", "var(--red)", "l")}
 {ev(180, 1, "<b>首の長い恐竜が主役に</b><br>約1億8000万年前ごろ", "var(--green)")}
 {ev(157, 0, "<b>モリソン層の時代</b><br>約1億5700万〜1億5000万年前", "var(--sea)", "c", 150)}
 {ev(150, 1, "<b>始祖鳥</b><br>約1億5000万年前", "var(--sand)", "l")}
 {ax}
</div>"""
    page("G01_年表", body, "国際年代層序表 v2026/06 ／ Olsen et al. (2022) Sci. Adv. ／ Pol et al. (2020) Proc. R. Soc. B ／ Trujillo & Kowallis (2015) ／ NHM")

# ---------- パンゲアの模式図（第3話 G02・G18 と同じ形） ----------
# 「すべてがひとつにつながった陸」を表すだけの単純な形。実際の輪郭ではない（いまの大陸の形も描かない）
PANGAEA = [(200, 80), (350, 46), (520, 56), (680, 88), (810, 140), (770, 205), (650, 232), (545, 268), (610, 312),
           (730, 345), (810, 390), (770, 465), (630, 545), (455, 578), (300, 545), (215, 460), (175, 360), (150, 250), (160, 150)]
# 北と南を分ける裂け目の線（模式。右側は東の海の入り江につながる）
RIFT = [(0, 262), (150, 252), (260, 272), (380, 256), (470, 270), (560, 262), (700, 262), (1000, 262)]

def pangaea_panel(idp, split, w=780, h=520):
    s, ox, oy = 0.78, 40, 30
    d = smooth_px(PANGAEA)
    def land(clip=None, dy=0):
        cp = f' clip-path="url(#{clip})"' if clip else ""
        return (f'<g transform="translate(0,{dy})"><g{cp}>'
                f'<path d="{d}" fill="#2F6E8A" stroke="#2F6E8A" stroke-width="26" stroke-linejoin="round"/>'
                f'<path d="{d}" fill="#8A6A46" stroke="#B0906A" stroke-width="3"/></g></g>')
    fwd = " ".join(f"L{px} {py}" for px, py in RIFT)            # 西 → 東
    back = " ".join(f"L{px} {py}" for px, py in reversed(RIFT))  # 東 → 西
    defs = (f'<radialGradient id="{idp}sea" cx="50%" cy="45%" r="60%"><stop offset="0" stop-color="#1B4660"/><stop offset="1" stop-color="#14354A"/></radialGradient>'
            f'<clipPath id="{idp}n" clipPathUnits="userSpaceOnUse"><path d="M0 -100 L1000 -100 {back} Z"/></clipPath>'
            f'<clipPath id="{idp}s" clipPathUnits="userSpaceOnUse"><path d="M0 1000 {fwd} L1000 1000 Z"/></clipPath>')
    if split:
        inner = (land(f"{idp}n", -30) + land(f"{idp}s", 30) +
                 '<text x="430" y="150" font-size="56" font-weight="700" fill="var(--ink)" text-anchor="middle" paint-order="stroke" stroke="rgba(15,30,43,.6)" stroke-width="8">ローラシア</text>'
                 '<text x="470" y="470" font-size="56" font-weight="700" fill="var(--ink)" text-anchor="middle" paint-order="stroke" stroke="rgba(15,30,43,.6)" stroke-width="8">ゴンドワナ</text>'
                 '<text x="935" y="140" font-size="34" fill="var(--sea)" text-anchor="end">北</text>'
                 '<text x="935" y="505" font-size="34" fill="var(--sea)" text-anchor="end">南</text>')
    else:
        inner = (land() + '<text x="460" y="330" font-size="64" font-weight="700" fill="var(--ink)" text-anchor="middle" '
                 'paint-order="stroke" stroke="rgba(15,30,43,.6)" stroke-width="8">パンゲア</text>')
    return f"""<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<defs>{defs}</defs>
<rect x="0" y="0" width="{w}" height="{h}" rx="30" fill="url(#{idp}sea)" stroke="#2C5A73" stroke-width="3"/>
<g transform="translate({ox},{oy}) scale({s})">{inner}</g></svg>"""

# ---------- G02 大陸の分裂 ----------
def g02():
    body = f"""<h1>大陸が二つに分かれていく　<small>二億年前ごろから（形は簡略化した模式図）</small></h1>
<div style="display:flex;gap:40px;align-items:flex-start;margin-top:-10px">
 <div style="text-align:center"><div style="font-size:34px;font-weight:700;margin-bottom:14px" class="sub">前回まで：ひとつの大陸</div>{pangaea_panel("a", False)}</div>
 <div style="font-size:72px;align-self:center;padding-top:40px" class="sand">→</div>
 <div style="text-align:center"><div style="font-size:34px;font-weight:700;margin-bottom:14px" class="sand">ジュラ紀：北と南に裂けていく</div>{pangaea_panel("b", True)}</div>
</div>
<div style="font-size:26px;margin-top:22px" class="sub">大陸の形と位置は、研究による復元をもとにしたおおまかな模式図（輪郭は正確ではない）</div>"""
    page("G02_大陸の分裂", body, "U.S. Geological Survey \"This Dynamic Earth: Historical perspective\"")

# ---------- G03 大西洋の始まり（断面の模式図） ----------
def g03():
    def sec(stage):
        gap = {1: 0, 2: 70, 3: 210}[stage]
        cx = 230
        lx, rx = cx - gap / 2, cx + gap / 2
        s = '<svg width="460" height="300" viewBox="0 0 460 300">'
        s += '<rect x="0" y="170" width="460" height="130" fill="#6A3A2E"/>'            # 地下の熱い岩（マントル）
        if stage == 1:
            s += f'<path d="M0 70 H460 V170 H0 Z" fill="#8A6A46"/>'
            s += f'<path d="M{cx-40} 70 L{cx} 140 L{cx+40} 70 Z" fill="#0F1E2B"/>'
            s += f'<path d="M{cx-14} 168 L{cx} 146 L{cx+14} 168" fill="var(--red)"/>'
            s += f'<path d="M{cx-90} 40 H{cx-170} M{cx+90} 40 H{cx+170}" stroke="var(--sand)" stroke-width="6"/>'
            s += f'<path d="M{cx-160} 28 L{cx-178} 40 L{cx-160} 52 M{cx+160} 28 L{cx+178} 40 L{cx+160} 52" stroke="var(--sand)" stroke-width="6" fill="none"/>'
        else:
            s += f'<path d="M0 70 H{lx-20} L{lx} 150 V170 H0 Z" fill="#8A6A46"/>'
            s += f'<path d="M460 70 H{rx+20} L{rx} 150 V170 H460 Z" fill="#8A6A46"/>'
            s += f'<path d="M{lx-20} 70 L{lx} 150 H{rx} L{rx+20} 70 Z" fill="#24506A"/>'           # 海の水
            s += f'<rect x="{lx}" y="150" width="{gap}" height="20" fill="#3A3F48"/>'               # 新しい海の底
            s += f'<path d="M{cx} 168 V156" stroke="var(--red)" stroke-width="8"/>'
            s += f'<path d="M{cx-12} 162 L{cx} 148 L{cx+12} 162" fill="var(--red)"/>'
            if stage == 3:
                s += '<text x="70" y="58" font-size="26" fill="var(--ink)" text-anchor="middle">北アメリカ</text>'
                s += '<text x="390" y="58" font-size="26" fill="var(--ink)" text-anchor="middle">アフリカ</text>'
                s += f'<text x="{cx}" y="118" font-size="28" font-weight="700" fill="var(--sea)" text-anchor="middle">大西洋</text>'
        s += '<text x="12" y="294" font-size="20" fill="#D8B8A8">地下の熱い岩</text>'
        return s + "</svg>"
    body = f"""<h1>大西洋の始まり　<small>大陸が裂けて、海が生まれる（断面の模式図）</small></h1>
<div style="display:flex;align-items:stretch;height:500px;margin-top:-10px">{steps_row([
        (sec(1), "① 大陸が裂ける", "北アメリカとアフリカの<br>あいだに裂け目"),
        (sec(2), "② 新しい海の底", "裂け目に、新しい<br>海の底ができる"),
        (sec(3), "③ 少しずつ広がる", "いまの大西洋の<br>始まり"),
    ], pic_h=300)}</div>
<div style="font-size:30px;margin-top:24px;text-align:center">始まりは <b class="sand">約1億9000万年前</b> とする研究も、<b class="sand">もっとあと</b> とする見方もある</div>"""
    page("G03_大西洋の始まり", body, "Labails et al. (2010) Earth and Planetary Science Letters 297:355 ／ Withjack et al. (1998) AAPG Bulletin 82:817")

# ---------- G04 花の起源の議論 ----------
def g04():
    L, R, W = 265, 125, 1680
    x = lambda ma: (L - ma) / (L - R) * W
    t_pt, t_tj, t_jk = 251.902, 201.4, 143.1      # ペルム紀/三畳紀の境は帯の位置を決めるためだけ（数字は出さない）
    rows = f"""
<div style="position:absolute;left:0;top:0;font-size:30px;font-weight:700" class="sea">いまの植物の遺伝子から、さかのぼって計算</div>
<div style="position:absolute;left:{x(256):.0f}px;top:52px;width:{x(149)-x(256):.0f}px;height:56px;border-radius:28px;
 background:linear-gradient(90deg,rgba(79,157,181,.15),rgba(79,157,181,.75) 20%,rgba(79,157,181,.75) 80%,rgba(79,157,181,.15));
 display:flex;align-items:center;justify-content:center;font-size:30px;font-weight:700">2億5600万〜1億4900万年前のどこか</div>

<div style="position:absolute;left:{x(201.4)+10:.0f}px;top:150px;font-size:30px;font-weight:700;color:#E07A60">中国の「ジュラ紀の花」の報告</div>
<div style="position:absolute;left:{x(201.4)+40:.0f}px;top:200px;width:64px;height:64px;border-radius:50%;border:4px dashed #E07A60;
 display:flex;align-items:center;justify-content:center;font-size:40px;font-weight:700;color:#E07A60">？</div>
<div style="position:absolute;left:{x(201.4)+124:.0f}px;top:210px;font-size:28px">ジュラ紀の前半。本当に花かどうかは議論中</div>

<div style="position:absolute;left:{x(137)-1000:.0f}px;width:1060px;text-align:right;top:300px;font-size:30px;font-weight:700" class="sand">確かな最も古い化石（花粉）</div>
<div style="position:absolute;left:{x(137):.0f}px;top:352px;width:{x(133)-x(137):.0f}px;height:56px;border-radius:8px;background:var(--sand)"></div>
<div style="position:absolute;left:{x(137)-1000:.0f}px;width:980px;text-align:right;top:362px;font-size:28px">白亜紀の初め（約1億3700万〜1億3300万年前）</div>
"""
    ax, _ = time_axis(L, R, W, 470, [
        (L, t_pt, "#5A4A40", "", 26),
        (t_pt, t_tj, C_TRI, "三畳紀", 30),
        (t_tj, t_jk, C_J2, "ジュラ紀", 34),
        (t_jk, R, C_CRE, "白亜紀", 30),
    ], [
        (t_tj, "約2億140万年前", "var(--sub)", "c"),
        (t_jk, "約1億4310万年前", "var(--sub)", "c"),
    ], band_h=60, tick_h=90)
    body = f"""<h1>花はいつ生まれた？　<small>化石と遺伝子の計算で、答えが食い違っている</small></h1>
<div style="position:relative;height:640px;margin-top:-16px">{rows}{ax}
 <div style="position:absolute;left:0;top:540px;font-size:24px" class="sub">ペルム紀</div>
</div>"""
    page("G04_花の起源の議論", body, "Barba-Montoya et al. (2018) New Phytologist 218:819 ／ Coiro et al. (2019) New Phytologist 223:83 ／ Fu et al. (2018) eLife 7:e38827")

# ---------- G05 首の長い恐竜が主役になるまで ----------
def g05():
    L, R, W = 205, 170, 1680
    x = lambda ma: (L - ma) / (L - R) * W
    cards = [
        ("三畳紀の終わりの<br>大量絶滅", "約2億160万年前", "var(--red)", x(201.6)),
        ("南の大陸で<br>大規模な火山活動", "約1億8400万〜<br>1億8000万年前", "#E07A60", (x(184) + x(180)) / 2),
        ("気候が大きく乱れ、<br>植物の種類が減る", "そのあと", "var(--sand)", (x(180) + x(176.5)) / 2),
        ("首の長い恐竜が<br>大型の植物食動物の主役に", "ジュラ紀の前半の<br>終わりごろ", "var(--green)", x(175.3)),
    ]
    cw, gap = 390, 40
    html_cards = ""
    lines = ""
    for i, (head, when, color, tx) in enumerate(cards):
        left = i * (cw + gap)
        html_cards += f"""<div class="card" style="position:absolute;left:{left}px;top:0;width:{cw}px;height:250px;padding:22px 20px;text-align:center;border-color:{color}">
 <div style="font-size:28px;font-weight:700;line-height:1.4">{head}</div>
 <div style="font-size:28px;margin-top:14px;line-height:1.35;color:{color}">{when}</div></div>"""
        if i < 3:
            html_cards += f'<div style="position:absolute;left:{left+cw+2}px;top:96px;width:{gap-4}px;text-align:center;font-size:40px" class="sand">→</div>'
        lines += f'<path d="M{left+cw/2:.0f} 252 L{tx:.0f} 404" stroke="{color}" stroke-width="4" fill="none"/><circle cx="{tx:.0f}" cy="410" r="10" fill="{color}"/>'
    volc = f'<div style="position:absolute;left:{x(184):.0f}px;top:398px;width:{x(180)-x(184):.0f}px;height:24px;background:#E07A60;opacity:.8;border-radius:6px"></div>'
    clim = (f'<div style="position:absolute;left:{x(180):.0f}px;top:404px;width:{x(176.8)-x(180):.0f}px;height:12px;'
            f'background:repeating-linear-gradient(90deg,var(--sand) 0 14px,transparent 14px 24px)"></div>')
    ax, _ = time_axis(L, R, W, 440, [
        (L, 201.4, C_TRI, "三畳紀", 28),
        (201.4, 174.7, C_J1, "ジュラ紀 前期", 32),
        (174.7, R, C_J2, "中期", 28),
    ], [
        (201.4, "約2億140万年前", "var(--sub)", "l"),
        (174.7, "約1億7470万年前", "var(--sub)", "c"),
    ], band_h=56, tick_h=80)
    body = f"""<h1>首の長い恐竜が主役になるまで　<small>2020年の研究（アルゼンチンの地層から）</small></h1>
<div style="position:relative;height:640px;margin-top:-16px">
 <svg width="1680" height="440" style="position:absolute;left:0;top:0">{lines}</svg>
 {html_cards}{volc}{clim}{ax}
</div>"""
    page("G05_首の長い恐竜が主役になるまで", body, "Pol et al. (2020) Proceedings of the Royal Society B 287:20202310 ／ Olsen et al. (2022) Science Advances 8:eabo6342")

# ---------- G06 モリソン層 ----------
def g06():
    states = ["アリゾナ", "コロラド", "カンザス", "モンタナ", "ネブラスカ", "ニューメキシコ",
              "ノースダコタ", "オクラホマ", "サウスダコタ", "テキサス", "ユタ", "ワイオミング"]
    cells = "".join(f'<div style="font-size:32px;padding:10px 0;{"color:var(--sand);font-weight:700" if s == "コロラド" else ""}">{s}</div>' for s in states)
    L, R, W = 165, 140, 690
    x = lambda ma: (L - ma) / (L - R) * W
    tl = f"""<div style="position:relative;height:250px;margin-top:20px">
 <div style="position:absolute;left:{x(157):.0f}px;top:0;width:{x(150)-x(157):.0f}px;height:150px;background:var(--sea);opacity:.35;border-radius:10px"></div>
 <div style="position:absolute;left:{x(165):.0f}px;top:60px;width:{x(161.5)-x(165):.0f}px;height:50px;background:{C_J2};display:flex;align-items:center;justify-content:center;font-size:24px">中期</div>
 <div style="position:absolute;left:{x(161.5):.0f}px;top:60px;width:{x(143.1)-x(161.5):.0f}px;height:50px;background:{C_J3};display:flex;align-items:center;justify-content:center;font-size:26px">ジュラ紀 後期</div>
 <div style="position:absolute;left:{x(143.1):.0f}px;top:60px;width:{x(140)-x(143.1):.0f}px;height:50px;background:{C_CRE}"></div>
 <div style="position:absolute;left:{(x(157)+x(150))/2-260:.0f}px;width:520px;top:166px;text-align:center;font-size:30px;font-weight:700" class="sea">約1億5700万〜1億5000万年前</div>
</div>"""
    body = f"""<h1>モリソン層　<small>川やあふれた水が運んだ泥や砂が、いま地層として残る</small></h1>
<div style="display:flex;gap:44px;align-items:stretch;height:620px;margin-top:-10px">
 <div class="card" style="flex:1;padding:26px 36px">
  <div style="font-size:32px;font-weight:700" class="sand">アメリカ西部の 12の州 にまたがる</div>
  <div style="display:grid;grid-template-columns:1fr 1fr 1fr;column-gap:20px;margin-top:20px">{cells}</div>
  <div style="font-size:24px;margin-top:16px" class="sub">（州の名前の一覧。地図ではない）</div>
 </div>
 <div style="flex:1;display:flex;flex-direction:column;gap:30px">
  <div class="card" style="padding:26px 36px">
   <div style="font-size:28px" class="sub">名前の由来</div>
   <div style="font-size:36px;font-weight:700;margin-top:10px;line-height:1.4">コロラド州の<span class="sand">モリソン</span>という町の<br>近くで調べられた</div>
  </div>
  <div class="card" style="padding:26px 36px;flex:1">
   <div style="font-size:28px" class="sub">地層ができた時代</div>{tl}
  </div>
 </div>
</div>"""
    page("G06_モリソン層", body, "U.S. Geological Survey, Geolex \"Morrison\" ／ Trujillo & Kowallis (2015) Geology of the Intermountain West 2:1")

# ---------- G07 ディプロドクスの大きさ ----------
def g07():
    m = 50                       # 1メートルあたりのpx
    x0 = 40
    dl = 25 * m
    bus = 11 * m
    g1, g2 = 350, 560
    def bus_svg(bx):
        win = "".join(f'<rect x="{bx+56+i*58}" y="{g2-118}" width="42" height="44" rx="6" fill="#1B3446"/>' for i in range(8))
        return (f'<rect x="{bx}" y="{g2-140}" width="{bus-6}" height="124" rx="16" fill="var(--sea)"/>{win}'
                f'<rect x="{bx+10}" y="{g2-118}" width="32" height="86" rx="4" fill="#1B3446"/>'
                f'<circle cx="{bx+100}" cy="{g2-16}" r="22" fill="#0F1E2B" stroke="var(--sub)" stroke-width="5"/>'
                f'<circle cx="{bx+bus-110}" cy="{g2-16}" r="22" fill="#0F1E2B" stroke="var(--sub)" stroke-width="5"/>')
    def bracket(a, b, y, color):
        return f'<path d="M{a} {y} H{b} M{a} {y-14} V{y+14} M{b} {y-14} V{y+14}" stroke="{color}" stroke-width="4"/>'
    tx1, tx2 = x0 + dl + 50, x0 + 2 * bus + 50
    svg = f"""<svg width="1680" height="620" viewBox="0 0 1680 620">
<line x1="20" y1="{g1}" x2="1660" y2="{g1}" stroke="var(--sub)" stroke-width="3"/>
{sauropod(x0, g1, dl)}
{bracket(x0, x0+dl, g1+30, "var(--sand)")}
<text x="{tx1}" y="{g1-150}" font-size="38" font-weight="700" fill="var(--sand)">ディプロドクス</text>
<text x="{tx1}" y="{g1-90}" font-size="44" font-weight="700" fill="var(--ink)">全長 25m前後</text>
<text x="{tx1}" y="{g1-42}" font-size="26" fill="var(--sub)">博物館の表記は 24〜26m</text>
<line x1="20" y1="{g2}" x2="1660" y2="{g2}" stroke="var(--sub)" stroke-width="3"/>
{bus_svg(x0)}{bus_svg(x0+bus)}
{bracket(x0, x0+2*bus, g2+30, "var(--sea)")}
<text x="{tx2}" y="{g2-90}" font-size="38" font-weight="700" fill="var(--sea)">大きな路線バス 2台</text>
<text x="{tx2}" y="{g2-36}" font-size="44" font-weight="700" fill="var(--ink)">約11m × 2 ＝ 約22m</text>
</svg>"""
    body = f"""<h1>ディプロドクスの大きさ　<small>大きな路線バスを2台並べたよりも長い（同じ縮尺）</small></h1>
<div style="margin-top:-30px">{svg}</div>"""
    page("G07_ディプロドクスの大きさ", body, "Natural History Museum (London) \"Diplodocus\" ／ \"How big was Diplodocus carnegii?\"")

# ---------- G08 長い首と小さな頭 ----------
def g08():
    reach = f"""<svg width="420" height="250" viewBox="0 0 420 250">
<path d="M140 150 m-120 0 a120 120 0 0 1 240 0" fill="var(--green)" fill-opacity=".18" stroke="var(--green)" stroke-width="4" stroke-dasharray="10 8"/>
{sauropod(80, 240, 330)}
<path d="M30 100 Q20 60 60 40" stroke="var(--green)" stroke-width="4" fill="none"/><path d="M48 34 L64 38 L56 52" fill="none" stroke="var(--green)" stroke-width="4"/>
</svg>"""
    chew = """<svg width="220" height="220" viewBox="0 0 220 220">
<ellipse cx="110" cy="120" rx="80" ry="40" fill="var(--sand)"/><path d="M30 120 L0 110 L0 130 Z" fill="var(--sand)"/>
<circle cx="80" cy="108" r="6" fill="#0F1E2B"/>
<path d="M40 128 H150" stroke="#0F1E2B" stroke-width="4"/>
<path d="M140 60 l30 -30 M150 70 l40 -16 M150 90 l46 0" stroke="var(--green)" stroke-width="6" stroke-linecap="round"/>
</svg>"""
    head = """<svg width="220" height="220" viewBox="0 0 220 220">
<ellipse cx="110" cy="110" rx="80" ry="44" fill="none" stroke="var(--sub)" stroke-width="4" stroke-dasharray="10 8"/>
<ellipse cx="90" cy="112" rx="42" ry="22" fill="var(--sand)"/><circle cx="76" cy="106" r="5" fill="#0F1E2B"/>
<text x="110" y="200" font-size="26" fill="var(--sub)" text-anchor="middle">小さく、軽い</text></svg>"""
    neck = f"""<svg width="300" height="220" viewBox="0 0 300 220">{sauropod(10, 210, 280)}</svg>"""
    body = f"""<h1>巨人の秘密：長い首と小さな頭　<small>2011年の研究がまとめた、大きくなれた理由のうちの二つ</small></h1>
<div style="display:flex;gap:30px;height:620px;margin-top:-16px">
 <div class="card" style="flex:none;width:520px;padding:24px 30px;text-align:center">
  <div style="font-size:34px;font-weight:700;text-align:left" class="sand">① 長い首</div>
  <div style="margin-top:20px">{reach}</div>
  <div style="font-size:30px;margin-top:20px;line-height:1.45">体を動かさずに、首だけで<br>広い範囲の植物を食べる</div>
  <div style="font-size:26px;margin-top:12px;line-height:1.45" class="sub">ほかの動物が届かない葉にも届いた</div>
 </div>
 <div class="card" style="flex:1;padding:24px 30px">
  <div style="font-size:34px;font-weight:700" class="sand">② 噛まない</div>
  <div style="display:flex;align-items:center;justify-content:space-between;margin-top:30px">
   <div style="text-align:center;width:260px">{chew}<div style="font-size:30px;font-weight:700;margin-top:8px;line-height:1.35">噛まずに<br>飲み込む</div></div>
   <div style="font-size:52px" class="sand">→</div>
   <div style="text-align:center;width:260px">{head}<div style="font-size:30px;font-weight:700;margin-top:8px;line-height:1.35">頭を小さく<br>軽くできる</div></div>
   <div style="font-size:52px" class="sand">→</div>
   <div style="text-align:center;width:300px">{neck}<div style="font-size:30px;font-weight:700;margin-top:8px;line-height:1.35">首を長くしても<br>支えられる</div></div>
  </div>
 </div>
</div>"""
    page("G08_長い首と小さな頭", body, "Sander et al. (2011) Biological Reviews 86:117")

# ---------- G09 成長の速さ ----------
def g09():
    def panel(label, big, note, color):
        return f"""<div class="card" style="flex:1;padding:40px 40px;text-align:center;border-color:{color}">
 <div style="font-size:34px;line-height:1.4">{label}</div>
 <div style="font-size:110px;font-weight:700;margin-top:40px;color:{color};line-height:1.1">{big}</div>
 <div style="font-size:28px;margin-top:36px;line-height:1.5" class="sub">{note}</div></div>"""
    body = f"""<h1>巨人の秘密：成長の速さ　<small>骨の断面に残る成長の跡から（推定）</small></h1>
<div style="display:flex;gap:50px;height:540px;margin-top:-10px">
 {panel("大人の大きさになるまで", "40年未満", "四十年もかからなかった", "var(--sand)")}
 {panel("成長が最も速い時期の<br>1年に増える体重", '500kg<span style="font-size:72px">〜</span>2t', "五百キログラムから二トンほど（可能性）", "var(--sea)")}
</div>"""
    page("G09_成長の速さ", body, "Sander et al. (2011) Biological Reviews 86:117 ／ Griebeler, Klein & Sander (2013) PLoS ONE 8:e67012")

# ---------- G10 首の角度 ----------
def g10():
    def card(neck, head, year, note, color):
        svg = f'<svg width="660" height="400" viewBox="0 0 660 400"><line x1="10" y1="380" x2="650" y2="380" stroke="var(--sub)" stroke-width="3"/>{sauropod(70, 380, 560, neck, color)}</svg>'
        return f"""<div class="card" style="flex:1;padding:22px 26px;text-align:center">
 <div style="height:400px">{svg}</div>
 <div style="font-size:36px;font-weight:700;margin-top:6px;color:{color}">{head}</div>
 <div style="font-size:28px;margin-top:10px;line-height:1.45">{year}</div>
 <div style="font-size:26px;margin-top:4px;line-height:1.45" class="sub">{note}</div></div>"""
    body = f"""<h1>首をどんな角度で持っていた？　<small>研究によって考えが分かれている</small></h1>
<div style="display:flex;gap:24px;align-items:stretch;height:640px;margin-top:-16px">
 {card("up", "高く持ち上げていた説", "2009年の研究", "いまの動物の首の姿勢と比べて", "var(--sand)")}
 <div style="align-self:center;width:120px;text-align:center;font-size:32px;font-weight:700;line-height:1.4" class="sub">議論は<br>続いて<br>いる</div>
 {card("flat", "水平に近かった説", "1999年の研究", "低いところの植物を食べていた", "var(--sea)")}
</div>"""
    page("G10_首の角度", body, "Taylor, Wedel & Naish (2009) Acta Palaeontologica Polonica 54:213 ／ Stevens & Parrish (1999) Science 284:798")

# ---------- G11 板の役割 ----------
def g11():
    heat = "".join(f'<path d="M{x} 70 q-12 -18 0 -36 q12 -18 0 -36" stroke="#E07A60" stroke-width="5" fill="none"/>' for x in (230, 300, 370))
    left_svg = f'<svg width="600" height="300" viewBox="0 0 600 300"><line x1="10" y1="290" x2="590" y2="290" stroke="var(--sub)" stroke-width="3"/>{stego(40, 290, 520, "var(--sub)", "#E07A60")}{heat}</svg>'
    eye = ('<g transform="translate(470,40)"><ellipse cx="40" cy="30" rx="40" ry="24" fill="none" stroke="var(--sand)" stroke-width="5"/>'
           '<circle cx="40" cy="30" r="12" fill="var(--sand)"/></g>')
    right_svg = f'<svg width="600" height="300" viewBox="0 0 600 300"><line x1="10" y1="290" x2="590" y2="290" stroke="var(--sub)" stroke-width="3"/>{stego(40, 290, 520, "var(--sand)", "var(--sand)")}{eye}</svg>'
    body = f"""<h1>ステゴサウルスの板は何のため？　<small>背中に並ぶ、骨でできた大きな板</small></h1>
<div style="display:flex;gap:30px;align-items:stretch;height:620px;margin-top:-16px">
 <div class="card" style="flex:1;padding:24px 30px;text-align:center;opacity:.55">
  <div style="font-size:32px;font-weight:700" class="sub">かつての考え</div>
  <div style="margin-top:16px">{left_svg}</div>
  <div style="font-size:36px;font-weight:700;margin-top:16px">体温の調節</div>
  <div style="font-size:28px;margin-top:10px;line-height:1.45" class="sub">体の熱を逃がしたり、<br>体を温めたりする</div>
 </div>
 <div style="font-size:56px;align-self:center" class="sand">→</div>
 <div class="card" style="flex:1;padding:24px 30px;text-align:center;border-color:var(--sand)">
  <div style="font-size:32px;font-weight:700" class="sand">2005年の研究（板の骨の内部を調べた）</div>
  <div style="margin-top:16px">{right_svg}</div>
  <div style="font-size:36px;font-weight:700;margin-top:16px">種類の見分け・相手に見せる</div>
  <div style="font-size:28px;margin-top:10px;line-height:1.45" class="sub">体温の調節に使われたことは、<br>あってもまれだった</div>
 </div>
</div>"""
    page("G11_板の役割", body, "Main, de Ricqlès, Horner & Padian (2005) Paleobiology 31:291")

# ---------- G12 年代の並び ----------
def g12():
    L, R, W = 173, 146, 1680
    x = lambda ma: (L - ma) / (L - R) * W
    ay = 360
    def ev(ma, above, icon, head, when, color, al="c", ma2=None):
        c = x(ma) if ma2 is None else (x(ma) + x(ma2)) / 2
        if ma2 is not None:
            mark = f'<rect x="{x(ma):.0f}" y="{ay-12}" width="{x(ma2)-x(ma):.0f}" height="24" rx="12" fill="{color}"/>'
        else:
            mark = f'<circle cx="{c:.0f}" cy="{ay}" r="16" fill="{color}"/>'
        if above:
            stem = f'<line x1="{c:.0f}" y1="{ay-20}" x2="{c:.0f}" y2="{ay-70}" stroke="{color}" stroke-width="4"/>'
            ty = 18
        else:
            stem = f'<line x1="{c:.0f}" y1="{ay+20}" x2="{c:.0f}" y2="{ay+70}" stroke="{color}" stroke-width="4"/>'
            ty = ay + 82
        if al == "r":
            pos = f"left:{c+60-420:.0f}px;text-align:right"
        elif al == "l":
            pos = f"left:{c-60:.0f}px;text-align:left"
        else:
            pos = f"left:{c-210:.0f}px;text-align:center"
        lbl = (f'<div style="position:absolute;{pos};top:{ty}px;width:420px">'
               f'<div style="height:150px;display:flex;align-items:flex-end;justify-content:{ {"r":"flex-end","l":"flex-start"}.get(al, "center") }">{icon}</div>'
               f'<div style="font-size:30px;font-weight:700;color:{color};margin-top:6px">{head}</div>'
               f'<div style="font-size:26px;line-height:1.35">{when}</div></div>')
        if not above:
            lbl = (f'<div style="position:absolute;{pos};top:{ty}px;width:420px">'
                   f'<div style="font-size:30px;font-weight:700;color:{color}">{head}</div>'
                   f'<div style="font-size:26px;line-height:1.35">{when}</div>'
                   f'<div style="height:130px;display:flex;align-items:flex-start;margin-top:8px;justify-content:{ {"r":"flex-end","l":"flex-start"}.get(al, "center") }">{icon}</div></div>')
        return mark + stem, lbl
    ic = lambda inner, w=200, h=130: f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}">{inner}</svg>'
    items = [
        ev(170, True, ic(pterosaur(0, 0, 1.0)), "スカイ島の大型翼竜", "約1億7000万年前", "var(--sea)", "l"),
        ev(168, False, ic(plant_dino(0, 0, 0.86)), "クリンダドロメウス", "約1億6800万〜1億6600万年前", "var(--green)", "l", 166),
        ev(160, True, ic(feathered_dino(0, 0, 0.86)), "アンキオルニス", "約1億6000万年前", "var(--sand)"),
        ev(150, False, ic(archaeo(0, 0, 0.3), 200, 130), "始祖鳥", "約1億5000万年前", "#E8C98C", "r"),
    ]
    marks = "".join(m for m, _ in items)
    lbls = "".join(l for _, l in items)
    svg = f"""<svg width="1680" height="660" viewBox="0 0 1680 660" style="position:absolute;left:0;top:0">
<rect x="0" y="{ay-34}" width="{x(161.5):.0f}" height="68" fill="{C_J2}" opacity=".55"/>
<rect x="{x(161.5):.0f}" y="{ay-34}" width="{W-x(161.5):.0f}" height="68" fill="{C_J3}" opacity=".55"/>
<text x="16" y="{ay+48}" font-size="24" fill="var(--sub)">ジュラ紀 中期</text>
<text x="{W-16}" y="{ay-44}" font-size="24" fill="var(--sub)" text-anchor="end">ジュラ紀 後期</text>
<line x1="{x(161.5):.0f}" y1="{ay-46}" x2="{x(161.5):.0f}" y2="{ay+46}" stroke="var(--sub)" stroke-width="3" stroke-dasharray="6 5"/>
<path d="M{x(161):.0f} {ay} H{x(151):.0f}" stroke="var(--sand)" stroke-width="6" stroke-dasharray="4 8" opacity=".8"/>
<line x1="0" y1="{ay}" x2="{W-10}" y2="{ay}" stroke="var(--sub)" stroke-width="3"/>
<path d="M{W-20} {ay-12} L{W} {ay} L{W-20} {ay+12}" fill="var(--sub)"/>
{marks}</svg>"""
    body = f"""<h1>羽毛の恐竜と始祖鳥の年代　<small>空の住人たちが現れた順番</small></h1>
<div style="position:relative;height:660px;margin-top:-40px">{svg}{lbls}
 <div style="position:absolute;left:{x(160)-200:.0f}px;width:560px;top:{ay+46}px;font-size:22px;line-height:1.35" class="sub">点線：アンキオルニスの年代は資料によって<br>約1億6100万〜1億5100万年前と幅がある</div>
</div>"""
    page("G12_年代の並び", body, "Jagielska et al. (2022) Current Biology ／ Cincotta et al. (2019) PeerJ ／ Hu et al. (2009) Nature ／ NHM \"Anchiornis\" \"Archaeopteryx\"")

# ---------- G13 鳥と恐竜の特徴 ----------
def g13():
    S = 1.6
    ox, oy = 470, 10
    P = lambda px, py: (ox + px * S, oy + py * S)
    def lab(pt, tx, ty, txt, color, anchor):
        x1, y1 = P(*pt)
        return (f'<circle cx="{x1:.0f}" cy="{y1:.0f}" r="9" fill="{color}" stroke="#0F1E2B" stroke-width="3"/>'
                f'<path d="M{x1:.0f} {y1:.0f} L{tx} {ty}" stroke="{color}" stroke-width="3"/>'
                f'<text x="{tx + (-12 if anchor == "end" else 12)}" y="{ty+12}" font-size="38" font-weight="700" fill="{color}" text-anchor="{anchor}">{txt}</text>')
    svg = f"""<svg width="1680" height="700" viewBox="0 0 1680 700">
{archaeo(ox, oy, S, "#B49A70")}
{lab((320, 80), 1180, 90, "羽根", "var(--sea)", "start")}
{lab((290, 160), 1180, 220, "翼", "var(--sea)", "start")}
{lab((122, 164), 380, 340, "口に歯", "var(--sand)", "end")}
{lab((166, 60), 380, 120, "かぎ爪のある指", "var(--sand)", "end")}
{lab((540, 258), 1300, 560, "骨の入った長い尾", "var(--sand)", "start")}
</svg>"""
    body = f"""<h1>始祖鳥：鳥と恐竜の特徴をあわせ持つ　<small>ドイツ南部、約1億5000万年前</small></h1>
<div style="position:relative;margin-top:-50px">{svg}
 <div class="card" style="position:absolute;left:0;top:480px;padding:18px 26px;font-size:30px;line-height:1.6">
  <div><span class="sea" style="font-weight:700">■ 鳥の特徴</span>　羽根・翼</div>
  <div><span class="sand" style="font-weight:700">■ 恐竜の特徴</span>　歯・骨の入った長い尾・かぎ爪のある指</div></div>
</div>"""
    page("G13_鳥と恐竜の特徴", body, "Natural History Museum (London) \"Archaeopteryx\" ／ \"What were the first birds like?\"")

# ---------- G14 鳥は恐竜 ----------
def g14():
    rx, ry = 40, 330          # 根元（恐竜）
    th_x, th_y = 380, 210     # 肉食恐竜の仲間の分かれ目
    tip = 1130
    ys = {"anchi": 70, "archaeo": 230, "bird": 390}
    orn_y = 560
    svg = f"""<svg width="1680" height="680" viewBox="0 0 1680 680">
<path d="M{rx+170} {ry} H{th_x-160}" stroke="var(--ink)" stroke-width="8"/>
<path d="M{th_x-160} {ry} V{orn_y} H{tip}" stroke="var(--sub)" stroke-width="8" fill="none"/>
<path d="M{th_x-160} {ry} V{th_y} H{th_x}" stroke="var(--sand)" stroke-width="8" fill="none"/>
<path d="M{th_x} {th_y} V{ys['anchi']} H{tip}" stroke="var(--sand)" stroke-width="8" fill="none"/>
<path d="M{th_x} {th_y} H{th_x+260} V{ys['archaeo']} H{tip}" stroke="var(--sand)" stroke-width="8" fill="none"/>
<path d="M{th_x+260} {th_y} V{ys['bird']} H{tip}" stroke="var(--sea)" stroke-width="8" fill="none"/>
<circle cx="{th_x-160}" cy="{ry}" r="12" fill="var(--ink)"/>
<circle cx="{th_x}" cy="{th_y}" r="12" fill="var(--sand)"/><circle cx="{th_x+260}" cy="{th_y}" r="10" fill="var(--sand)"/>
<rect x="{th_x-20}" y="{ys['anchi']-50}" width="{tip-th_x+540}" height="{ys['bird']-ys['anchi']+100}" rx="24" fill="var(--sand)" fill-opacity=".06" stroke="var(--sand)" stroke-width="3" stroke-dasharray="12 10"/>
<text x="{th_x+10}" y="{ys['bird']+90}" font-size="28" font-weight="700" fill="var(--sand)">肉食恐竜の仲間（獣脚類）</text>
<g transform="translate({tip+20},{ys['anchi']-60})">{feathered_dino(0, 0, 0.75)}</g>
<text x="{tip+190}" y="{ys['anchi']+12}" font-size="36" font-weight="700" fill="var(--ink)">アンキオルニス</text>
<g>{archaeo(tip+20, ys['archaeo']-70, 0.27)}</g>
<text x="{tip+190}" y="{ys['archaeo']+2}" font-size="36" font-weight="700" fill="var(--ink)">始祖鳥</text>
<text x="{tip+190}" y="{ys['archaeo']+42}" font-size="26" fill="#E07A60">最初の鳥かどうかは議論</text>
<g>{bird_icon(tip+40, ys['bird']-40, 1.1)}</g>
<text x="{tip+190}" y="{ys['bird']+12}" font-size="36" font-weight="700" fill="var(--sea)">いまの鳥</text>
<g transform="translate({tip+20},{orn_y-70})">{plant_dino(0, 0, 0.75)}</g>
<text x="{tip+190}" y="{orn_y-2}" font-size="34" font-weight="700" fill="var(--sub)">クリンダドロメウス</text>
<text x="{tip+190}" y="{orn_y+36}" font-size="24" fill="var(--sub)">鳥とは遠い仲間</text>
</svg>"""
    body = f"""<h1>鳥は恐竜の一員　<small>鳥は、肉食恐竜の仲間から生まれた</small></h1>
<div style="position:relative;margin-top:-30px">{svg}
 <div class="card" style="position:absolute;left:0;top:{ry-50}px;width:200px;padding:16px 10px;font-size:34px;font-weight:700;text-align:center">恐竜</div>
</div>"""
    page("G14_鳥は恐竜", body, "Natural History Museum (London) \"What were the first birds like?\" ／ Field Museum (2025) ／ Godefroit et al. (2014) Science 345:451")

# ---------- G15 哺乳類の多様な暮らし ----------
def g15():
    swim = f"""<svg width="300" height="210" viewBox="0 0 300 210">
<rect x="0" y="100" width="300" height="110" fill="#24506A"/>
<path d="M0 100 q25 -12 50 0 t50 0 t50 0 t50 0 t50 0 t50 0" stroke="var(--sea)" stroke-width="4" fill="none"/>
{mammal(40, 64, 1.1)}
<path d="M196 112 Q250 100 290 118 Q250 140 196 124 Z" fill="var(--sand)"/>
<path d="M214 114 l8 12 M232 110 l8 14 M252 110 l8 14 M270 113 l6 10" stroke="#0F1E2B" stroke-width="2.5"/></svg>"""
    glide = f"""<svg width="300" height="210" viewBox="0 0 300 210">
<path d="M150 105 L40 60 Q30 110 60 150 Z M150 105 L260 60 Q270 110 240 150 Z" fill="var(--sand)" opacity=".55"/>
<ellipse cx="150" cy="105" rx="26" ry="52" fill="var(--sand)"/><circle cx="150" cy="48" r="20" fill="var(--sand)"/>
<path d="M150 156 L150 200" stroke="var(--sand)" stroke-width="7"/>
<path d="M126 80 L40 60 M174 80 L260 60 M128 136 L60 150 M172 136 L240 150" stroke="var(--sand)" stroke-width="6"/></svg>"""
    dig = f"""<svg width="300" height="210" viewBox="0 0 300 210">
<rect x="0" y="40" width="300" height="170" fill="#5A4636"/>
<path d="M30 140 Q100 90 190 120 Q250 140 290 120" stroke="#3A2C22" stroke-width="56" fill="none" stroke-linecap="round"/>
{mammal(70, 92, 1.0)}
<path d="M72 138 l-14 8 M72 138 l-10 14 M72 138 l-2 16" stroke="var(--ink)" stroke-width="4" stroke-linecap="round"/>
<circle cx="250" cy="70" r="6" fill="#7A6450"/><circle cx="40" cy="190" r="8" fill="#7A6450"/><circle cx="270" cy="180" r="5" fill="#7A6450"/></svg>"""
    L, R, W = 201.4, 143.1, 1680
    x = lambda ma: (L - ma) / (L - R) * W
    band = f"""<div style="position:relative;height:150px;margin-top:26px">
 <div style="position:absolute;left:0;top:0;width:{x(174.7):.0f}px;height:52px;background:{C_J1};display:flex;align-items:center;justify-content:center;font-size:28px">ジュラ紀 前期</div>
 <div style="position:absolute;left:{x(174.7):.0f}px;top:0;width:{x(161.5)-x(174.7):.0f}px;height:52px;background:{C_J2};display:flex;align-items:center;justify-content:center;font-size:28px">中期</div>
 <div style="position:absolute;left:{x(161.5):.0f}px;top:0;width:{W-x(161.5):.0f}px;height:52px;background:{C_J3};display:flex;align-items:center;justify-content:center;font-size:28px">後期</div>
 <div style="position:absolute;left:{x(190):.0f}px;top:66px;width:{x(165)-x(190):.0f}px;height:20px;border-radius:10px;background:linear-gradient(90deg,rgba(217,183,121,.2),var(--sand) 35%,var(--sand) 65%,rgba(217,183,121,.2))"></div>
 <div style="position:absolute;left:{x(190):.0f}px;width:{x(165)-x(190):.0f}px;text-align:center;top:94px;font-size:28px;font-weight:700" class="sand">歯やあごの形の変化が、とても速かった時期</div>
</div>"""
    body = f"""<h1>恐竜の足元の、哺乳類に近い仲間　<small>小さくても、さまざまな暮らしを試していた</small></h1>
<div style="display:flex;align-items:stretch;height:440px;gap:36px;margin-top:-16px">{steps_row([
        (swim, "泳ぐ", "カストロカウダ<br>ジュラ紀の中ごろ・中国"),
        (glide, "滑空する", "手足のあいだの皮ふの膜<br>ジュラ紀の後半・中国"),
        (dig, "土を掘る", "モグラのように<br>ジュラ紀の後半・中国"),
    ], arrow="", pic_h=210)}</div>
{band}"""
    page("G15_哺乳類の多様な暮らし", body, "Ji et al. (2006) Science ／ Meng et al. (2017) Nature ／ Luo et al. (2015) Science ／ Close et al. (2015) Current Biology")

# ---------- G16 歯の成長の跡 ----------
def g16():
    tooth = f"""<svg width="760" height="620" viewBox="0 0 760 620">
<path d="M120 40 Q220 0 320 40 Q340 120 320 190 Q300 300 270 420 Q255 470 225 470 Q200 470 195 420 Q190 330 175 300 Q160 330 155 420 Q150 470 125 470 Q100 470 90 420 Q70 300 80 190 Q60 110 120 40 Z" fill="#E8E0CE"/>
<path d="M95 190 Q200 175 315 190" stroke="#B8AC94" stroke-width="4" fill="none"/>
<path d="M160 70 Q200 60 240 70 Q250 140 230 200 Q200 210 170 200 Q150 140 160 70 Z" fill="#C88A7A" opacity=".55"/>
<circle cx="120" cy="330" r="62" fill="none" stroke="var(--sand)" stroke-width="5"/>
<path d="M175 350 L440 380" stroke="var(--sand)" stroke-width="4"/>
<g transform="translate(560,380)">
 <circle r="170" fill="#D8CCB4" stroke="var(--sand)" stroke-width="6"/>
 <clipPath id="zc"><circle r="166"/></clipPath>
 <g clip-path="url(#zc)">{''.join(f'<path d="M{-200+i*26} -200 Q{-150+i*26} 0 {-200+i*26} 200" stroke="#6A5440" stroke-width="{6 if i % 2 else 3}" fill="none"/>' for i in range(16))}</g>
</g>
<text x="200" y="520" font-size="28" fill="var(--sub)" text-anchor="middle">歯の断面（模式図）</text>
</svg>"""
    def res(head, big, color):
        return f"""<div class="card" style="padding:26px 36px;border-color:{color}">
 <div style="font-size:32px">{head}</div>
 <div style="font-size:64px;font-weight:700;margin-top:10px;color:{color}">{big}</div></div>"""
    body = f"""<h1>歯に残る、年輪のような成長の跡　<small>クルサトドン：スカイ島、ジュラ紀の中ごろ（2024年の研究）</small></h1>
<div style="display:flex;gap:40px;align-items:flex-start;margin-top:-30px">
 <div style="flex:none;position:relative">{tooth}
  <div style="position:absolute;left:380px;top:110px;width:360px;text-align:center;font-size:30px;font-weight:700;line-height:1.35" class="sand">歯の根元のまわりの<br>年輪のような成長の跡</div></div>
 <div style="flex:1;display:flex;flex-direction:column;gap:26px;padding-top:70px">
  {res("大人：死んだときの年齢", "およそ7歳", "var(--sand)")}
  {res("子ども：死んだときの年齢", "生後7か月〜2年", "var(--sea)")}
  <div style="font-size:28px;line-height:1.5" class="sub">同じくらいの大きさのいまの小さな哺乳類より、<br>ゆっくり育ち、ずっと長く生きられたらしい</div>
 </div>
</div>"""
    page("G16_歯の成長の跡", body, "Panciroli et al. (2024) Nature 632:815")

for f in (g01, g02, g03, g04, g05, g06, g07, g08, g09, g10, g11, g12, g13, g14, g15, g16):
    f()
