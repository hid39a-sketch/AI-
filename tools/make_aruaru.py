# ショート「古代あるある」（縦長 1080x1920）を作る
# 使い方: python -I tools/make_aruaru.py shinseki   → video/shorts/aruaru_shinseki.mp4
# 上に「古代あるある」と、あるあるの一言。真ん中に本編の画像（16:9）、下に読み上げている文の字幕
# 文は AivisSpeech（阿井田 茂）で新しく読み上げる。{表記|よみ} で読みを直せる。事実は各回の台本（事実確認済み）から取る
import io, json, os, re, subprocess, sys, tempfile, wave, pathlib, urllib.request, urllib.parse

ROOT = pathlib.Path(__file__).resolve().parent.parent
ENGINE, SPEAKER = "http://127.0.0.1:10101", 1310138976
FONT = r"C\:/Windows/Fonts/YuGothB.ttc"
# 演出名: (速さ, 抑揚, 前の間, 後の間)。本編の narrate.py の値に合わせ、ショート向けに少し速め
PRESETS = {"標準": (0.98, 1.125, 0.05, 0.35), "溜め": (0.95, 1.15, 0.05, 0.6), "名前": (0.88, 1.25, 0.05, 0.5)}

# 名前: (あるある見出し, [(演出, 文, 画像), ...])。画像は images/ からの相対パス
SHORTS = {
    "shinseki": ("親戚の顔、わからない", [
        ("溜め", "親戚の顔、正直よくわからない。", "ep03/S10_ディメトロドン.png"),
        ("標準", "では、こちらの方。背中に帆を持つ、ディメトロドンです。", "ep03/S02_帆の影.png"),
        ("溜め", "恐竜に見えますが、恐竜ではありません。", "ep03/S13_帆の骨格.png"),
        ("標準", "最初の恐竜が現れるより、数千万年も前に、姿を消していました。", "ep03/G01_年表.png"),
        ("標準", "それどころか、恐竜やトカゲよりも、私たち{哺乳類|ほにゅうるい}に近い仲間です。", "ep03/G04_二つの道.png"),
        ("標準", "{頭の骨|あたまのほね}の、{目|め}の後ろにある穴。この特徴は、形を変えて、あなたの{頭の骨|あたまのほね}にも残っています。", "ep03/G03_頭の骨の穴.png"),
        ("標準", "ただし、あなたのご先祖に、帆があったわけではありません。", "ep03/S14_朝日と帆.png"),
        ("溜め", "遠い親戚、意外なところにいました。", "ep03/S10_ディメトロドン.png"),
    ]),
}
FOOT = "続きは本編で（チャンネルから）"

def post(path, params, body=None):
    rq = urllib.request.Request(ENGINE + path + "?" + urllib.parse.urlencode(params),
                                data=json.dumps(body).encode() if body is not None else b"",
                                headers={"Content-Type": "application/json"}, method="POST")
    return urllib.request.urlopen(rq, timeout=120).read()

def speak(text, preset, out):
    sp, it, pre, post_ = PRESETS[preset]
    q = json.loads(post("/audio_query", {"text": re.sub(r"\{(.+?)\|(.+?)\}", r"\2", text), "speaker": SPEAKER}))
    q.update(speedScale=sp, pitchScale=0, intonationScale=it, prePhonemeLength=pre, postPhonemeLength=post_)
    data = post("/synthesis", {"speaker": SPEAKER}, q)
    out.write_bytes(data)
    with wave.open(io.BytesIO(data)) as w:
        return w.getnframes() / w.getframerate()

def wrap(text, width=13):
    # 字幕を1行13字ほどで折り返す。読点・句点のあとで切れるなら優先する
    lines, cur = [], ""
    for ch in text:
        cur += ch
        if len(cur) >= width and ch in "、。" or len(cur) >= width + 3:
            lines.append(cur); cur = ""
    if cur:
        lines.append(cur)
    for k in range(1, len(lines)):  # 行の頭に句読点が来たら前の行へ送る
        while lines[k] and lines[k][0] in "、。":
            lines[k - 1] += lines[k][0]; lines[k] = lines[k][1:]
    return "\n".join(l for l in lines if l)

def main(name):
    head, segs = SHORTS[name]
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="aruaru_"))
    parts = []
    for i, (preset, text, img) in enumerate(segs):
        wav = tmp / f"{i:02d}.wav"
        dur = speak(text, preset, wav) + 0.15
        sub = tmp / f"{i:02d}.txt"
        sub.write_text(wrap(re.sub(r"\{(.+?)\|(.+?)\}", r"\1", text)), encoding="utf-8", newline="\n")  # CRLF だと drawtext が空行を入れる
        hd = tmp / "head.txt"
        hd.write_text(head, encoding="utf-8")
        ft = tmp / "foot.txt"
        ft.write_text(FOOT, encoding="utf-8")
        esc = lambda p: str(p).replace("\\", "/").replace(":", "\\:")
        graph = ("[0:v]split[a][b];"
                 "[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=30:3,eq=brightness=-0.2[bg];"
                 f"[b]scale=1080:-2,zoompan=z='1+0.0006*on':d={int(dur * 30) + 1}:s=1080x608:fps=30[fg];"
                 "[bg][fg]overlay=0:620,"
                 f"drawtext=fontfile='{FONT}':text='古代あるある':fontsize=64:fontcolor=0xFFD24A:borderw=6:bordercolor=black:x=(w-text_w)/2:y=230,"
                 f"drawtext=fontfile='{FONT}':textfile='{esc(hd)}':fontsize=92:fontcolor=white:borderw=8:bordercolor=black:x=(w-text_w)/2:y=330,"
                 f"drawtext=fontfile='{FONT}':textfile='{esc(sub)}':fontsize=62:line_spacing=18:fontcolor=white:borderw=6:bordercolor=black:x=(w-text_w)/2:y=1300,"
                 f"drawtext=fontfile='{FONT}':textfile='{esc(ft)}':fontsize=44:fontcolor=0xDDDDDD:borderw=5:bordercolor=black:x=(w-text_w)/2:y=1700,"
                 "format=yuv420p[v]")
        mp4 = tmp / f"{i:02d}.mp4"
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-loop", "1", "-t", f"{dur:.3f}", "-i", str(ROOT / "images" / img),
                        "-i", str(wav), "-filter_complex", graph, "-map", "[v]", "-map", "1:a", "-af", "apad",
                        "-t", f"{dur:.3f}", "-r", "30", "-c:v", "libx264", "-crf", "20", "-c:a", "aac", "-b:a", "192k",
                        "-ar", "48000", "-ac", "2", str(mp4)], check=True)
        parts.append(mp4)
        print(f"{i} {dur:4.1f}s {text[:30]}")
    lst = tmp / "list.txt"
    lst.write_text("".join(f"file '{p.as_posix()}'\n" for p in parts), encoding="utf-8")
    out = ROOT / "video" / "shorts" / f"aruaru_{name}.mp4"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
                    "-af", "loudnorm=I=-14:TP=-1.5", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(out)], check=True)
    print(out)

if __name__ == "__main__":
    main(sys.argv[1])
