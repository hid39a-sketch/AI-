# 本編から区間を切り出して、縦長（1080x1920）のショート動画を作る
# 使い方: python -I tools/make_short.py ep01_dunk   → video/shorts/ep01_dunk.mp4
# 本編の映像（字幕・信頼度の表示入り）を中央に置き、上下はぼかした同じ映像で埋め、上に見出し、下に案内を入れる
import subprocess, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
FONT = r"C\:/Windows/Fonts/YuGothB.ttc"
# 名前: (本編, [(開始秒, 終了秒), ...], 見出し2行, 下の案内)
SHORTS = {
    "ep01_dunk": ("ep01", [(17.6, 34.6), (137.2, 178.2)], ("歯がないのに", "魚で最強のかむ力"), "続きは本編で（チャンネルから）"),
    "ep02_giant_bugs": ("ep02", [(368.9, 392.4), (490.9, 509.4)], ("長さ2.6mのヤスデ", "3億年前の巨大な虫"), "続きは本編で（チャンネルから）"),
    "ep03_sail": ("ep03", [(22.9, 50.8), (226.5, 256.0)], ("背中に帆", "でも恐竜じゃない"), "続きは本編で（チャンネルから）"),
}

def main(name):
    ep, segs, (h1, h2), foot = SHORTS[name]
    src = ROOT / "video" / ep / f"{ep}_draft.mp4"
    out = ROOT / "video" / "shorts" / f"{name}.mp4"
    out.parent.mkdir(parents=True, exist_ok=True)
    parts, labels = [], []
    for i, (a, b) in enumerate(segs):
        d = b - a
        parts.append(f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS,fade=t=in:d=0.3,fade=t=out:st={d - 0.3:.2f}:d=0.3[v{i}];"
                     f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.3,afade=t=out:st={d - 0.3:.2f}:d=0.3[a{i}];")
        labels.append(f"[v{i}][a{i}]")
    txt = lambda t, y, size, color="white": (f"drawtext=fontfile='{FONT}':text='{t}':fontsize={size}:fontcolor={color}:"
                                            f"borderw=8:bordercolor=black:x=(w-text_w)/2:y={y}")
    graph = ("".join(parts) + "".join(labels) + f"concat=n={len(segs)}:v=1:a=1[cv][ca];"
             "[cv]split[c1][c2];"
             "[c1]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=30:3,eq=brightness=-0.15[bg];"
             "[c2]scale=1080:-2[fg];"
             "[bg][fg]overlay=0:(H-h)/2,"
             + txt(h1, 230, 96) + "," + txt(h2, 350, 110, "0xFFD24A") + "," + txt(foot, 1560, 54) + "[v]")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(src), "-filter_complex", graph, "-map", "[v]", "-map", "[ca]",
                    "-c:v", "libx264", "-crf", "20", "-preset", "medium", "-r", "30", "-c:a", "aac", "-b:a", "192k",
                    "-movflags", "+faststart", str(out)], check=True)
    print(out)

if __name__ == "__main__":
    main(sys.argv[1])
