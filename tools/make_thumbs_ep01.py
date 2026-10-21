# 第1話のサムネイル案（1280x720）をHTMLで作り、Edge（ヘッドレス）でPNGにする
# 使い方: python -I tools/make_thumbs_ep01.py   → video/ep01/thumb_A.png など
# 文字は大きく短く（スマホの一覧で読める大きさ）。右下はYouTubeの再生時間の表示に隠れるので文字を置かない
import subprocess, pathlib, tempfile, time

ROOT = pathlib.Path(__file__).resolve().parent.parent
IMG = ROOT / "images" / "ep01"
OUT = ROOT / "video" / "ep01"
SRC = OUT / "thumb_src"
SRC.mkdir(parents=True, exist_ok=True)
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

CSS = """*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1280px;height:720px;overflow:hidden;background:#000;font-family:"Noto Sans JP","Yu Gothic","Meiryo",sans-serif}
.bg{position:absolute;inset:0;background-size:cover;background-position:center}
.shade{position:absolute;inset:0}
.t{position:absolute;color:#fff;font-weight:900;line-height:1.08;letter-spacing:.01em;
 text-shadow:0 0 18px rgba(0,0,0,.9),0 4px 0 #000,4px 0 0 #000,-4px 0 0 #000,0 -4px 0 #000}
.y{color:#FFD24A}.r{color:#FF6B4A}
.tag{position:absolute;left:40px;top:34px;background:#C8644B;color:#fff;font-weight:800;font-size:34px;padding:6px 18px;border-radius:8px}
"""

def thumb(name, img, body, shade="linear-gradient(90deg,rgba(0,0,0,.75) 0%,rgba(0,0,0,.35) 55%,rgba(0,0,0,0) 80%)", pos="center"):
    doc = f"""<!doctype html><html lang="ja"><head><meta charset="utf-8"><style>{CSS}</style></head><body>
<div class="bg" style="background-image:url('{(IMG / img).as_uri()}');background-position:{pos}"></div>
<div class="shade" style="background:{shade}"></div>{body}</body></html>"""
    p = SRC / f"{name}.html"
    p.write_text(doc, encoding="utf-8")
    png = OUT / f"{name}.png"
    if png.exists():
        png.unlink()
    profile = tempfile.mkdtemp(prefix="kodai_edge_")
    subprocess.run([EDGE, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--user-data-dir={profile}",
                    "--force-device-scale-factor=1", "--window-size=1280,720", "--virtual-time-budget=3000",
                    "--allow-file-access-from-files", f"--screenshot={png}", p.as_uri()],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)
    for _ in range(30):
        if png.exists() and png.stat().st_size > 0:
            break
        time.sleep(0.5)
    print("ok" if png.exists() else "FAILED", png.name)

# A：タイトル案A「海の頂点はサメではなく鎧の魚」
thumb("thumb_A", "S10_刃の顎.png",
      '<div class="tag">3億6000万年前</div>'
      '<div class="t" style="left:40px;top:120px;font-size:96px">海の頂点は<br><span class="y">サメじゃない</span></div>'
      '<div class="t" style="left:40px;top:370px;font-size:76px">「<span class="r">鎧の魚</span>」<br>だった</div>',
      shade="linear-gradient(90deg,rgba(0,0,0,.8) 0%,rgba(0,0,0,.4) 45%,rgba(0,0,0,0) 70%)", pos="70% center")

# B：タイトル案B「歯がないのに最強」
thumb("thumb_B", "S19_一瞬の捕食.png",
      '<div class="t" style="left:40px;top:60px;font-size:120px"><span class="y">歯がない</span>のに</div>'
      '<div class="t" style="left:40px;top:210px;font-size:150px"><span class="r">最強</span></div>'
      '<div class="t" style="left:44px;top:430px;font-size:54px">あなたは生き延びられるか</div>',
      shade="linear-gradient(90deg,rgba(0,0,0,.8) 0%,rgba(0,0,0,.3) 50%,rgba(0,0,0,0) 75%)", pos="65% center")

# C：大きさの見直しを前に出す案（「10m説」→「3〜4m」）
thumb("thumb_C", "S13_古い復元.png",
      '<div class="t" style="left:40px;top:60px;font-size:110px"><span style="text-decoration:line-through;text-decoration-thickness:12px;text-decoration-color:#FF6B4A">10m</span>の怪物</div>'
      '<div class="t" style="left:40px;top:220px;font-size:84px">本当は<span class="y">3〜4m</span>だった</div>'
      '<div class="t" style="left:44px;top:430px;font-size:52px">最新研究で変わった「海の王者」</div>',
      shade="linear-gradient(180deg,rgba(0,0,0,.55) 0%,rgba(0,0,0,.25) 60%,rgba(0,0,0,.1) 100%)")
