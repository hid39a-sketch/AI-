# チャンネルのバナー（2560x1440）をHTMLで作り、Edge（ヘッドレス）でPNGにする
# 使い方: python -I tools/make_channel_art.py   → images/channel/banner_2560.png と、見え方の確認用 banner_check_*.png
# YouTube のバナーは、どの画面でも必ず見えるのは中央の 1546x423（x 507〜2053, y 508〜931）だけ。文字はこの中に入れる
import subprocess, pathlib, tempfile, time

ROOT = pathlib.Path(__file__).resolve().parent.parent
D = ROOT / "images" / "channel"
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
BG = (D / "banner_bg_raw.png").as_uri()

HTML = f"""<!doctype html><html lang="ja"><head><meta charset="utf-8"><style>
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:2560px;height:1440px;overflow:hidden;background:#0d1b33}}
.bg{{position:absolute;inset:0;background:url('{BG}') center/cover no-repeat}}
.shade{{position:absolute;left:880px;top:508px;width:800px;height:423px;
  background:radial-gradient(ellipse at center,rgba(8,18,34,.55) 0%,rgba(8,18,34,0) 70%)}}
.box{{position:absolute;left:507px;top:508px;width:1546px;height:423px;display:flex;flex-direction:column;
  align-items:center;justify-content:center;text-align:center;color:#F2EEE4}}
.t{{font-family:"Yu Mincho","YuMincho","Noto Serif JP","MS PMincho",serif;font-weight:700;font-size:132px;letter-spacing:.08em;
  text-shadow:0 4px 18px rgba(0,0,0,.85),0 0 3px rgba(0,0,0,.9)}}
.s{{font-family:"Noto Sans JP","Yu Gothic","Meiryo",sans-serif;font-weight:500;font-size:46px;letter-spacing:.35em;margin-top:14px;
  color:#D9C79A;text-shadow:0 2px 10px rgba(0,0,0,.9)}}
.c{{font-family:"Noto Sans JP","Yu Gothic","Meiryo",sans-serif;font-size:30px;letter-spacing:.12em;margin-top:22px;color:#C9D6E0;
  text-shadow:0 2px 8px rgba(0,0,0,.9)}}
</style></head><body><div class="bg"></div><div class="shade"></div>
<div class="box"><div class="t">化石の向こう側</div><div class="s">太古の地球を歩く</div>
<div class="c">最新の研究で、確かなことと推測を分けて伝える古生物ドキュメンタリー</div></div></body></html>"""

src = D / "banner_src.html"
src.write_text(HTML, encoding="utf-8")
png = D / "banner_2560.png"
if png.exists():
    png.unlink()
profile = tempfile.mkdtemp(prefix="kodai_edge_")
subprocess.run([EDGE, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--user-data-dir={profile}",
                "--force-device-scale-factor=1", "--window-size=2560,1440", "--virtual-time-budget=3000",
                "--allow-file-access-from-files", f"--screenshot={png}", src.as_uri()],
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
for _ in range(40):
    if png.exists() and png.stat().st_size > 0:
        break
    time.sleep(0.5)
print("ok" if png.exists() else "FAILED", png)
