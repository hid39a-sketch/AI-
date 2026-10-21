# 古代生物チャンネルの動画を組み立てる（静止画＋ゆっくりした動き＋ナレーション＋字幕＋信頼度表示 → MP4）
#
# 使い方:
#   python -I kodai_channel/tools/assemble.py                       # ep01 を本番の画像で書き出す
#   python -I kodai_channel/tools/assemble.py --bgm 曲.mp3           # BGM を混ぜる（ナレーションより約20dB小さく）
#   python -I kodai_channel/tools/assemble.py --bgm 曲.mp3 --bgm-gap 24   # BGM をさらに小さく（差を24dBに）
#   python -I kodai_channel/tools/assemble.py --allow-missing       # まだ無い画像は仮画像（「画像なし」＋ファイル名）で代用
#   python -I kodai_channel/tools/assemble.py --test                # ダミー画像で通し確認（test_assets/ を使う）
#   python -I kodai_channel/tools/assemble.py --ep ep02             # 別の回（audio/ep02_draft, image_prompts/ep02_shots.csv, images/ep02）
#   そのほか --audio-dir / --shots / --images / --out で個別に指定できる。--jobs で同時に作るカット数（既定6）
#   ダミー素材は python -I kodai_channel/tools/test_assets/make_test_assets.py で作り直せる
#
# 入力:
#   audio/<ep>_draft/narration.wav, timing.json（tools/narrate.py の出力。各行の line/preset/text/start/end 秒）
#   image_prompts/<ep>_shots.csv  列: shot_id, start_line, end_line, file, motion, label
#     start_line/end_line は timing.json の line（台本の行番号）。カットは start_line の読み始めから次のカットの読み始めまで出る
#     motion: zoom_in（ゆっくり寄る）/ zoom_out（ゆっくり引く）/ pan_left / pan_right（左右へ流す）/ static（動かさない）
#     label : 画面右上に出す信頼度  確認（緑）/ 推定（黄）/ 演出（灰）。空欄なら出さない
#   images/<ep>/<file>  16:9 推奨（違う比率は中央で切り抜いて画面を埋める）
#
# 出力:
#   video/<ep>/<ep>_draft.mp4（1920x1080・30fps）、video/<ep>/<ep>_subtitles.srt（YouTube アップロード用）
#   video/<ep>/work/ に途中ファイル。カット（shots/*.mp4）は画像・動き・長さが同じなら使い回す
#
# 字幕の分け方は youtube_research/tools/subs_split.py（研究室の窓）と同じ内容を埋め込んでいる（python -I では import できないため）
import argparse, csv, hashlib, json, re, subprocess, sys, time, pathlib
from concurrent.futures import ThreadPoolExecutor

ROOT = pathlib.Path(__file__).resolve().parent.parent      # kodai_channel/
TOOLS = ROOT / "tools"
W, H, FPS = 1920, 1080, 30
XF = 15            # クロスフェードのコマ数（0.5秒）
TAIL = 2.0         # 最後の行のあと、余韻として映像を残す秒数
SS = 4             # ズーム・パンのとき、いったん何倍に拡大してから動かすか（揺れを目立たなくする）
ZOOM = 1.08        # zoom_in / zoom_out の拡大率（1.0 ⇔ 1.08）
PANZ = 1.12        # pan のときの拡大率（この余白の分だけ左右に動く）
CHUNK = 12         # クロスフェードは何カットずつまとめて処理するか（一度に開くファイル数を抑える）
MOTIONS = {"zoom_in", "zoom_out", "pan_left", "pan_right", "static"}

# 信頼度表示（ASS の色は &HAABBGGRR）。文字色, 背景色
LABELS = {"確認": ("&H00FFFFFF", "&H20327D2E"),   # 緑 #2E7D32
          "推定": ("&H00202020", "&H1030C2F2"),                      # 黄 #F2C230
          "演出": ("&H00FFFFFF", "&H306B6B6B")}                      # 灰 #6B6B6B
FONT = "Yu Gothic"

def run(cmd, cwd=None):
    r = subprocess.run(cmd, cwd=cwd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    if r.returncode:
        sys.exit("ffmpeg が失敗しました:\n" + " ".join(map(str, cmd)) + "\n" + r.stderr.decode("utf-8", "replace")[-3000:])

def ts(sec, srt=False):
    h, rem = divmod(sec, 3600); m, s = divmod(rem, 60)
    if srt:
        ms = int(round(sec * 1000)) % 1000
        return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{ms:03d}"
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"

# ---- 字幕の分け方（tools/subs_split.py と同じ内容。言葉の途中では切らない） ----
def _kind(ch):
    if re.match(r"[ぁ-ゟ]", ch): return "h"     # ひらがな
    if re.match(r"[゠-ヿ]", ch): return "k"     # カタカナ（ー を含む）
    if re.match(r"[一-鿿々〆]", ch): return "c"  # 漢字
    if re.match(r"[0-9０-９,.，．%％]", ch): return "d"   # 数字
    if re.match(r"[A-Za-zＡ-Ｚａ-ｚ]", ch): return "a"
    return "p"                                          # 記号・空白

_SMALL = set("ぁぃぅぇぉっゃゅょゎァィゥェォッャュョヮーヶ")
_PART = set("はがをにでともへやの")
_PART2 = ("から", "まで", "より", "など", "だけ", "ほど", "しか", "こそ", "さえ", "ずつ")
_OPEN, _CLOSE = "「『（(", "」』）)"

def _score(s, i):
    """s[:i] と s[i:] の間で切るときの良さ。0 は切ってはいけない"""
    if i <= 0 or i >= len(s):
        return 0
    a, b = s[i - 1], s[i]
    if b in _SMALL or b in "、。，．！？・" or b in _CLOSE:
        return 0
    if a in _OPEN:
        return 0
    o = s.rfind("「", 0, i); cl = s.rfind("」", 0, i)
    if o > cl:                                           # かぎかっこの中
        end = s.find("」", i)
        if end != -1 and end - o <= 16:
            return 0                                     # 短い「〜」の中では切らない
    if s[i - 1:i + 1] in ("とい", "とお", "てい", "てお", "てく", "てし", "ても", "でも", "ので", "のに"):
        return 0                                         # 「という」「している」などの途中
    if a == "　" or b == "　":
        return 5
    if a in "、，":
        if b == "と" and s[i + 1:i + 2] not in ("て", "も", "こ", "き"):
            return 0.5                                   # 「〜した、と述べた」の「と」は前に付ける
        return 4
    if a == "の" and s[i:i + 2] == "よう":
        return 0                                         # 「〜のような」
    if a in _CLOSE + "！？":
        return 0 if _kind(b) == "h" else 3.5               # 「〜」のすぐ後の助詞は離さない
    ka, kb = _kind(a), _kind(b)
    if ka == "d" and kb in "ckp":
        return 0                                         # 数字と単位（20パーセント・4年間）は離さない
    if ka == kb and ka in "ckda":
        return 0                                         # 漢字どうし・カタカナどうし・数字どうし・英字どうし
    # 助詞として切ってよいか：直前が漢字・カタカナなど（名詞＋助詞）か、「から」「まで」などのとき
    noun_part = a in _PART and i >= 2 and _kind(s[i - 2]) != "h" and s[i - 2:i] not in ("では", "には", "とは")
    two_part = s[i - 2:i] in _PART2 and b not in _PART
    if a in "でにとへ" and b in "はもの" or s[i - 1:i + 1] in ("でき", "にな", "とな"):
        return 0                                         # 「では」「にも」「できる」「になる」の途中
    if s[i - 1:i + 1] in ("とし", "とさ", "る舞"):
        return 0                                         # 「として」「とされる」「振る舞う」の途中
    if a in "にや" and i >= 3 and _kind(s[i - 3]) == "d" and _kind(b) == "d":
        return 0                                         # 「4回に1回」「3人や4人」はまとめる
    if ka == "h" and kb == "h":
        if noun_part or two_part:
            return 1.5 if a in "はがをにでとも" or two_part else 1
        return 0                                         # ひらがなの途中（「まと/めた」「当ては/まる」など語の途中の可能性が高い）
    if ka == "h" and kb in "ckda":
        if noun_part or two_part:
            return 1.5 if a == "の" else 2.5             # 「目の/前」のような「の」は少し避ける
        if a in _PART:
            return 1
        if a in "いきしちひみりぎじびえけせねめれげべ":
            return 0                                     # 「やり/直す」「受け/入れる」のような複合語の途中
        return 0.3                                       # 「〜する/方法」などは、ほかに切れ目がないときだけ
    if ka in "ckd" and kb == "h":
        return 0                                         # 漢字のあとの送りがな・助詞は離さない
    return 1

def _best_cut(s, target, lo, hi):
    best, bi = None, None
    for i in range(max(1, lo), min(len(s), hi) + 1):
        sc = _score(s, i)
        if sc <= 0:
            continue
        v = sc * 3 - abs(i - target)
        if best is None or v > best:
            best, bi = v, i
    return bi

def _sentences(text):
    """句点（。！？）で文に分ける。閉じかっこは前の文に付け、かっこの中・かっこの直後に助詞が続く所では分けない"""
    out, cur, depth, i = [], "", 0, 0
    while i < len(text):
        ch = text[i]; cur += ch
        if ch in _OPEN:
            depth += 1
        elif ch in _CLOSE:
            depth = max(0, depth - 1)
        if ch in "。！？":
            while i + 1 < len(text) and text[i + 1] in "。！？":
                i += 1; cur += text[i]
            j = i
            d = depth
            while j + 1 < len(text) and text[j + 1] in _CLOSE and d > 0:
                j += 1; d -= 1
            nxt = text[j + 1] if j + 1 < len(text) else ""
            if d == 0 and not (j > i and _kind(nxt) == "h"):
                cur += text[i + 1:j + 1]; i = j; depth = d
                out.append(cur); cur = ""
        i += 1
    if cur.strip():
        out.append(cur)
    return [p for p in out if p.strip()]

def split_sub(text, limit=30, line=22):
    """字幕用に文を分ける：句点で分け、長ければ言葉の切れ目で分け、2行に収まる長さにそろえる"""
    out = []
    for p in _sentences(text):
        p = p.rstrip("。") if not p.endswith(("」", "』", "）", ")")) else p
        while len(p) > limit:
            n = -(-len(p) // limit)                      # 何個に分けるか
            cut = _best_cut(p, len(p) / n, 6, len(p) - 4)
            if cut is None or cut > line * 2:
                cut = _best_cut(p, min(limit, len(p) - 4), 4, min(line * 2, len(p) - 2)) or min(limit, len(p) - 2)
            out.append(p[:cut]); p = p[cut:]
        if p:
            out.append(p)
    return out

def wrap2(c, line=22):
    """1行が長いときは、言葉の切れ目のうち真ん中に近いところで改行する"""
    if len(c) <= line:
        return c
    cut = _best_cut(c, len(c) / 2, max(4, len(c) - line - 2), min(len(c) - 4, line + 2))
    if cut is None:
        cut = _best_cut(c, len(c) / 2, 3, len(c) - 3) or len(c) // 2
    return c[:cut].rstrip("　") + "\\N" + c[cut:].lstrip("　")

def sub_events(timing):
    """timing.json の各行を字幕の単位に分け、文字数に比例して表示時間を割り振る"""
    events = []
    for x in timing:
        chunks = split_sub(x["text"])
        if not chunks:
            continue
        dur = x["end"] - x["start"]; n = sum(len(c) for c in chunks); t = x["start"]
        line_ev = []
        for c in chunks:
            d = dur * len(c) / n
            line_ev.append([t, t + d, c]); t += d
        # 1秒未満しか出ない字幕は、同じ行の次（無ければ前）の字幕とまとめる
        i = 0
        while i < len(line_ev):
            a, b, c = line_ev[i]
            if b - a < 1.0 and len(line_ev) > 1:
                if i + 1 < len(line_ev) and len(c) + len(line_ev[i + 1][2]) <= 44:
                    line_ev[i + 1] = [a, line_ev[i + 1][1], c + "　" + line_ev[i + 1][2]]
                    line_ev.pop(i); continue
                if i > 0 and len(c) + len(line_ev[i - 1][2]) <= 44:
                    line_ev[i - 1] = [line_ev[i - 1][0], b, line_ev[i - 1][2] + "　" + c]
                    line_ev.pop(i); continue
            i += 1
        events += [tuple(e) for e in line_ev]
    return events

# ---- カット表 ----
def placeholder(sid, file, label, out_dir):
    """画像がまだ無いカットの代わり：暗い灰色に「画像なし」とファイル名を書いた 1920x1080 の画像"""
    out_dir.mkdir(parents=True, exist_ok=True)
    p = out_dir / f"{sid}.png"
    if not p.exists():
        safe = lambda s: s.replace("\\", "/").replace(":", "\\:").replace("'", "’").replace("%", "％")
        font = "fontfile='C\\:/Windows/Fonts/YuGothB.ttc'"
        vf = (f"drawgrid=w=160:h=160:t=2:c=white@0.12,"
              f"drawtext={font}:text='画像なし（{safe(sid)}・{safe(label or '表示なし')}）':fontsize=72:fontcolor=white:x=(w-tw)/2:y=h*0.30,"
              f"drawtext={font}:text='{safe(file)}':fontsize=56:fontcolor=white@0.8:x=(w-tw)/2:y=h*0.45")
        run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", f"color=c=0x2b3036:s={W}x{H}", "-vf", vf, "-frames:v", "1", str(p)])
    return p

def load_shots(path, timing, images, missing_dir=None):
    rows = list(csv.DictReader(open(path, encoding="utf-8-sig", newline="")))
    if not rows:
        sys.exit(f"カット表が空です: {path}")
    lines = [x["line"] for x in timing]
    shots, problems, missing = [], [], []
    for r in rows:
        r = {k.strip(): (v or "").strip() for k, v in r.items() if k}
        sid = r.get("shot_id", "?")
        try:
            sl, el = int(r["start_line"]), int(r["end_line"])
        except (KeyError, ValueError):
            problems.append(f"{sid}: start_line / end_line が数字ではありません"); continue
        motion = r.get("motion") or "static"
        if motion not in MOTIONS:
            problems.append(f"{sid}: motion「{motion}」は使えません（{' / '.join(sorted(MOTIONS))}）"); continue
        label = r.get("label", "")
        if label and label not in LABELS:
            problems.append(f"{sid}: label「{label}」は使えません（確認 / 推定 / 演出 / 空欄）"); continue
        img = images / r.get("file", "")
        if not r.get("file") or not img.is_file():
            if missing_dir is None:
                problems.append(f"{sid}: 画像がありません {img}"); continue
            missing.append(r.get("file") or sid)
            img = placeholder(sid, r.get("file", ""), label, missing_dir)
        idx = next((i for i, n in enumerate(lines) if n >= sl), None)
        if idx is None:
            problems.append(f"{sid}: start_line {sl} 以降の行が timing.json にありません"); continue
        shots.append(dict(id=sid, sl=sl, el=el, idx=idx, img=img, motion=motion, label=label))
    if problems:
        sys.exit("カット表に問題があります:\n  " + "\n  ".join(problems))
    if missing:
        print(f"注意: 画像が無い {len(missing)} カットは仮画像（画像なし）で代用します: {', '.join(missing)}")
    shots.sort(key=lambda s: s["idx"])
    # 抜け・重なりの確認（止めずに知らせる。抜けた行は前のカットがそのまま出続ける）
    for a, b in zip(shots, shots[1:]):
        if a["idx"] == b["idx"]:
            sys.exit(f"{a['id']} と {b['id']} が同じ行から始まっています")
        gap = [n for n in lines if a["el"] < n < b["sl"]]
        if gap:
            print(f"注意: 行 {gap[0]}〜{gap[-1]} はどのカットにも入っていません（{a['id']} が出続けます）")
        if a["el"] >= b["sl"]:
            print(f"注意: {a['id']}（〜{a['el']}行）と {b['id']}（{b['sl']}行〜）が重なっています。{b['id']} の開始で切り替えます")
    if shots[-1]["el"] < lines[-1]:
        print(f"注意: 最後のカット {shots[-1]['id']} は {shots[-1]['el']} 行までですが、最後まで出し続けます")
    return shots

# ---- 1カット分の映像（ゆっくりした動き付き） ----
def motion_filter(motion, frames):
    if motion == "static":
        return f"scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H},setsar=1,format=yuv420p"
    p = f"(on/{max(1, frames - 1)})"
    p = f"(0.5-0.5*cos(PI*{p}))"                         # 始めと終わりをなめらかに（ease in-out）
    if motion == "zoom_in":
        z, x = f"1+({ZOOM}-1)*{p}", "iw/2-(iw/zoom/2)"
    elif motion == "zoom_out":
        z, x = f"{ZOOM}-({ZOOM}-1)*{p}", "iw/2-(iw/zoom/2)"
    elif motion == "pan_right":                          # 視点が右へ動く
        z, x = f"{PANZ}", f"(iw-iw/zoom)*{p}"
    else:                                                # pan_left：視点が左へ動く
        z, x = f"{PANZ}", f"(iw-iw/zoom)*(1-{p})"
    return (f"scale={W * SS}:{H * SS}:force_original_aspect_ratio=increase:flags=lanczos,crop={W * SS}:{H * SS},setsar=1,"
            f"zoompan=z='{z}':x='{x}':y='ih/2-(ih/zoom/2)':d={frames}:s={W}x{H}:fps={FPS},format=yuv420p")

def render_shot(shot, frames, shot_dir):
    st = shot["img"].stat()
    key = f"{shot['img'].resolve()}|{st.st_size}|{st.st_mtime_ns}|{shot['motion']}|{frames}|{SS}|{ZOOM}|{PANZ}"
    clip = shot_dir / f"{shot['id']}_{hashlib.sha1(key.encode()).hexdigest()[:10]}.mp4"
    if clip.exists():
        return clip, False
    tmp = clip.with_suffix(".part.mp4")
    pre = ["-loop", "1", "-framerate", str(FPS)] if shot["motion"] == "static" else []
    run(["ffmpeg", "-y", "-v", "error", *pre, "-i", str(shot["img"]), "-vf", motion_filter(shot["motion"], frames),
         "-frames:v", str(frames), "-r", str(FPS), "-c:v", "libx264", "-preset", "fast", "-crf", "16",
         "-g", str(FPS * 2), str(tmp)])
    tmp.replace(clip)
    return clip, True

def xfade_join(clips, offsets, out, keep, t_abs, cwd):
    """clips を順に XF コマのクロスフェードでつなぎ、keep=(最初のコマ, 最後のコマ＋1) の範囲だけを、
    字幕（cwd/subs.ass）を焼き込んで書き出す。offsets[k] は k 番目のクリップが始まる時刻（先頭からの秒）、
    t_abs は書き出す範囲の先頭が本編の何秒目か（字幕の時刻合わせ）"""
    args, fc, prev = [], [], "[0:v]"
    for c in clips:
        args += ["-i", str(c)]
    for k in range(1, len(clips)):
        fc.append(f"{prev}[{k}:v]xfade=transition=fade:duration={XF / FPS:.6f}:offset={offsets[k]:.6f}[x{k}]")
        prev = f"[x{k}]"
    fc.append(f"{prev}trim=start_frame={keep[0]}:end_frame={keep[1]},setpts=PTS-STARTPTS+{t_abs:.6f}/TB,"
              f"subtitles=subs.ass,setpts=PTS-STARTPTS[v]")
    run(["ffmpeg", "-y", "-v", "error", *args, "-filter_complex", ";".join(fc), "-map", "[v]",
         "-r", str(FPS), "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", str(out)], cwd=cwd)

def write_ass(events, label_spans, path):
    styles = [f"Style: Default,{FONT},60,&H00FFFFFF,&H00FFFFFF,&H70000000,&H70000000,-1,0,0,0,100,100,0,0,3,10,0,2,160,160,44,1"]
    for name, (fg, bg) in LABELS.items():
        # 右上の小さな札（BorderStyle 3 = 文字の後ろに箱。Outline が箱の余白）
        styles.append(f"Style: L_{name},{FONT},38,{fg},{fg},{bg},{bg},-1,0,0,0,100,100,2,0,3,12,0,9,0,52,46,1")
    ass = ["[Script Info]", "ScriptType: v4.00+", f"PlayResX: {W}", f"PlayResY: {H}", "WrapStyle: 0", "ScaledBorderAndShadow: yes", "",
           "[V4+ Styles]",
           "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
           *styles, "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    for a, b, label in label_spans:
        ass.append(f"Dialogue: 1,{ts(a)},{ts(b)},L_{label},,0,0,0,,{label}")
    for a, b, c in events:
        ass.append(f"Dialogue: 0,{ts(a)},{ts(b)},Default,,0,0,0,,{wrap2(c)}")
    path.write_text("\n".join(ass), encoding="utf-8-sig")

def main():
    ap = argparse.ArgumentParser(description="古代生物チャンネルの動画を組み立てる")
    ap.add_argument("--ep", default="ep01")
    ap.add_argument("--test", action="store_true", help="tools/test_assets のダミーのカット表と画像を使う")
    ap.add_argument("--audio-dir"); ap.add_argument("--shots"); ap.add_argument("--images"); ap.add_argument("--out")
    ap.add_argument("--bgm", help="BGM の音声ファイル（短ければ繰り返す）")
    ap.add_argument("--bgm-gap", type=float, default=20.0, help="ナレーションより何dB小さくするか（既定20）")
    ap.add_argument("--jobs", type=int, default=6, help="同時に作るカット数")
    ap.add_argument("--allow-missing", action="store_true", help="画像が無いカットを仮画像（画像なし）で代用する。既定では止まる")
    a = ap.parse_args()

    ep = a.ep
    aud = pathlib.Path(a.audio_dir) if a.audio_dir else ROOT / "audio" / f"{ep}_draft"
    if a.test:
        shots_csv = pathlib.Path(a.shots) if a.shots else TOOLS / "test_assets" / f"{ep}_shots_test.csv"
        images = pathlib.Path(a.images) if a.images else TOOLS / "test_assets" / "images"
        out_dir = pathlib.Path(a.out) if a.out else ROOT / "video" / f"{ep}_test"
    else:
        shots_csv = pathlib.Path(a.shots) if a.shots else ROOT / "image_prompts" / f"{ep}_shots.csv"
        images = pathlib.Path(a.images) if a.images else ROOT / "images" / ep
        out_dir = pathlib.Path(a.out) if a.out else ROOT / "video" / ep
    name = f"{ep}_test" if a.test else ep
    work = out_dir / "work"; shot_dir = work / "shots"
    shot_dir.mkdir(parents=True, exist_ok=True)
    t_start = time.time()

    timing = json.load(open(aud / "timing.json", encoding="utf-8"))
    narration = aud / "narration.wav"
    adur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(narration)],
                                capture_output=True, text=True, check=True).stdout.strip())
    total = max(adur, timing[-1]["end"] + TAIL)
    nf = round(total * FPS)
    shots = load_shots(shots_csv, timing, images, work / "placeholders" if a.allow_missing else None)

    # 切り替え位置（コマ単位）。切り替えの0.5秒は、次のカットの読み始めをまたぐように置く
    bounds = [0] + [round(timing[s["idx"]]["start"] * FPS) for s in shots[1:]] + [nf]
    for i in range(1, len(bounds)):
        if bounds[i] - bounds[i - 1] < XF + 2:
            sys.exit(f"{shots[i - 1]['id']} の表示が短すぎます（{(bounds[i] - bounds[i - 1]) / FPS:.2f}秒）。0.6秒以上にしてください")
    starts = [0] + [b - XF // 2 for b in bounds[1:-1]]                  # 各クリップの最初のコマ
    ends = [b + (XF - XF // 2) for b in bounds[1:-1]] + [nf]            # 各クリップの最後のコマ＋1
    print(f"全体 {total:.1f}秒 / カット {len(shots)} 個 / 書き出し先 {out_dir}")

    # ---- 字幕（ASSは焼き込み用、SRTはYouTubeアップロード用）と信頼度表示 ----
    events = sub_events(timing)
    label_spans = [(bounds[i] / FPS, bounds[i + 1] / FPS, s["label"]) for i, s in enumerate(shots) if s["label"]]
    write_ass(events, label_spans, work / "subs.ass")
    srt = []
    for i, (s0, s1, c) in enumerate(events, 1):
        srt += [str(i), f"{ts(s0, True)} --> {ts(s1, True)}", wrap2(c).replace("\\N", "\n"), ""]
    (out_dir / f"{name}_subtitles.srt").write_text("\n".join(srt), encoding="utf-8")
    print(f"字幕 {len(events)} 件 / 信頼度表示 {len(label_spans)} 区間")

    # ---- カットごとの映像（同時に複数作る） ----
    t0 = time.time()
    done = [0]
    def job(i):
        clip, made = render_shot(shots[i], ends[i] - starts[i], shot_dir)
        done[0] += 1
        print(f"  [{done[0]:3d}/{len(shots)}] {shots[i]['id']:<8} {starts[i] / FPS:7.2f}-{ends[i] / FPS:7.2f}s "
              f"{shots[i]['motion']:<9} {shots[i]['label'] or '-':<2} {'作成' if made else '使い回し'}", flush=True)
        return clip
    with ThreadPoolExecutor(max(1, a.jobs)) as ex:
        clips = list(ex.map(job, range(len(shots))))
    print(f"カット作成 {time.time() - t0:.0f}秒")

    # ---- クロスフェードでつなぎ、字幕・信頼度表示を焼き込む ----
    # CHUNK 個ずつに分け、各まとまりは前後のカットを1つずつ余分に含めてフェードしたうえで
    # 「最初のカットの切り替え位置〜次のまとまりの切り替え位置」だけを書き出す。まとまり同士は再エンコードせずに連結する
    # （まとまりの境目はカットの切り替え位置なので、字幕・信頼度表示の途中で画質が変わることはない）
    t0 = time.time()
    groups = [(i, min(i + CHUNK, len(clips))) for i in range(0, len(clips), CHUNK)]
    def join_group(gi):
        g0, g1 = groups[gi]
        ks = list(range(max(0, g0 - 1), min(len(clips), g1 + 1)))
        base = starts[ks[0]]
        out = work / f"part_{gi:02d}.mp4"
        xfade_join([clips[k].resolve() for k in ks], [(starts[k] - base) / FPS for k in ks], out.resolve(),
                   (bounds[g0] - base, bounds[g1] - base), bounds[g0] / FPS, work)
        return out
    with ThreadPoolExecutor(max(1, min(a.jobs, len(groups)))) as ex:
        parts = list(ex.map(join_group, range(len(groups))))
    (work / "list.txt").write_text("\n".join(f"file '{p.name}'" for p in parts), encoding="utf-8")
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", "list.txt", "-c", "copy", "video_noaudio.mp4"], cwd=work)
    print(f"つなぎ {time.time() - t0:.0f}秒")

    # ---- 仕上げ：ナレーション（-14 LUFS）＋BGM を付ける（映像は再エンコードしない） ----
    t0 = time.time()
    final = out_dir / f"{name}_draft.mp4"
    inputs = ["-i", "video_noaudio.mp4", "-i", str(narration.resolve())]
    afc = "[1:a]aresample=48000,loudnorm=I=-14:TP=-1.5:LRA=11,apad"
    if a.bgm:
        inputs += ["-stream_loop", "-1", "-i", str(pathlib.Path(a.bgm).resolve())]
        fade_st = max(0.0, total - 4)
        afc += ("[n];[2:a]aresample=48000,aformat=channel_layouts=stereo,"
                f"atrim=0:{total:.3f},loudnorm=I={-14 - a.bgm_gap:.1f}:TP=-6:LRA=11,"
                f"afade=t=in:d=2,afade=t=out:st={fade_st:.3f}:d=4[b];"
                "[n]aformat=channel_layouts=stereo[n2];[n2][b]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.89")
    afc += "[a]"
    run(["ffmpeg", "-y", "-v", "error", *inputs,
         "-filter_complex", afc, "-map", "0:v", "-map", "[a]", "-t", f"{total:.3f}", "-c:v", "copy",
         "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", str(final)], cwd=work)
    print(f"仕上げ {time.time() - t0:.0f}秒")
    print(f"完成 {final}  {total:.1f}秒  （全体の処理 {time.time() - t_start:.0f}秒）")

if __name__ == "__main__":
    main()
