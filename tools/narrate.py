# AivisSpeech（127.0.0.1:10101）の「阿井田 茂」（ノーマル）で、台本の各行を演出付きで読み上げ、1本のWAVと行ごとのタイミングを出力する
# 使い方: python -I tools/narrate.py <台本.txt> <出力フォルダ>
# 台本の書式（1行1文。空行と # で始まる行は無視）:
#   [演出名] 本文      例: [名前] ダンクルオステウス。
#   演出名を省くと「標準」。演出名は下の PRESETS を参照
#   読みの修正は本文中に {表記|よみ} と書く  例: {三葉虫|さんようちゅう}
#   「# =====」で始まる行（章の見出し）の位置には、章の切れ目として SECTION_GAP 秒の無音を入れる
import json, sys, io, re, os, wave, urllib.request, urllib.parse
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ENGINE = os.environ.get("ENGINE", "http://127.0.0.1:10101")  # 2026-10-21 AivisSpeech に変更。VOICEVOX は ENGINE=http://127.0.0.1:50021
SPEAKER = int(os.environ.get("SPEAKER", 1310138976))  # 既定は 阿井田 茂「ノーマル」（2026-10-22 決定、ACML 1.0・クレジット任意）。銀芽「通常」は 38453057。VOICEVOX の剣崎雌雄は 21
PITCH_SHIFT = float(os.environ.get("PITCH_SHIFT", 0))  # 声を全体に低く（例 -0.05）
SECTION_GAP = 2.0  # 章の切れ目の無音（秒）
# 演出名: (速さ, 高さ, 抑揚, 前の間秒, 後の間秒)  2026-10-21 聞き比べで「D 場面ごとに演出」に決定
# 2026-10-22 阿井田 茂に変更：抑揚は銀芽の時の半分（聞き比べY）、高さは0（高さを変えると声がこもるため）
PRESETS = {
    "標準": (0.92, 0, 1.125, 0.1, 0.45),
    "提示": (0.88, 0, 1.10, 0.1, 0.8),    # 時代・場所の提示。ゆっくり、後に長い間
    "転換": (0.95, 0, 1.175, 0.9, 0.5),   # 「そのとき」など場面が動く文。前に間
    "溜め": (0.90, 0, 1.15, 0.1, 0.9),    # 正体を明かす直前。後に長い間
    "名前": (0.80, 0, 1.25, 0.1, 0.7),    # 生き物の名前など。ゆっくり強く
    "解説": (0.88, 0, 1.075, 0.8, 0.6),   # 確かな話か推測かの説明。落ち着いて
}
LINE_RE = re.compile(r'^\[(.+?)\]\s*(.*)$')
def post(path, params, body=None):
    url = ENGINE + path + "?" + urllib.parse.urlencode(params)
    data = json.dumps(body).encode() if body is not None else b""
    rq = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    return urllib.request.urlopen(rq, timeout=120).read()
def parse(path):
    rows = []
    for n, raw in enumerate(open(path, encoding='utf-8-sig'), 1):
        s = raw.strip()
        if s.startswith('# ====='):
            if rows: rows.append(dict(line=n, gap=SECTION_GAP))
            continue
        if not s or s.startswith('#'): continue
        m = LINE_RE.match(s)
        preset, text = (m.group(1), m.group(2)) if m else ("標準", s)
        if preset not in PRESETS: sys.exit(f"{n}行目: 未知の演出名 [{preset}]")
        display = re.sub(r'\{(.+?)\|(.+?)\}', r'\1', text)  # 字幕用
        speak = re.sub(r'\{(.+?)\|(.+?)\}', r'\2', text)    # 読み上げ用
        rows.append(dict(line=n, preset=preset, text=display, speak=speak))
    return rows
def main():
    src, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    frames, params, t, timing = [], None, 0.0, []
    for r in parse(src):
        if "gap" in r:
            if params:
                frames.append(bytes(1) * (int(params.framerate * r["gap"]) * params.sampwidth * params.nchannels))
                t += r["gap"]
            continue
        sp, pi, it, pre, post_ = PRESETS[r["preset"]]
        q = json.loads(post("/audio_query", {"text": r["speak"], "speaker": SPEAKER}))
        q.update(speedScale=sp, pitchScale=pi + PITCH_SHIFT, intonationScale=it, prePhonemeLength=pre, postPhonemeLength=post_)
        with wave.open(io.BytesIO(post("/synthesis", {"speaker": SPEAKER}, q))) as w:
            params = w.getparams(); f = w.readframes(w.getnframes())
            dur = w.getnframes() / w.getframerate()
        frames.append(f)
        timing.append(dict(line=r["line"], preset=r["preset"], text=r["text"], start=round(t, 3), end=round(t + dur, 3)))
        t += dur
        print(f'{r["line"]:>4} [{r["preset"]}] {dur:5.1f}s {r["text"][:40]}')
    with wave.open(os.path.join(out, "narration.wav"), "wb") as w:
        w.setparams(params); w.writeframes(b"".join(frames))
    json.dump(timing, open(os.path.join(out, "timing.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"合計 {t/60:.1f}分 -> {out}")
main()
