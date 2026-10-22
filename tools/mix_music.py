# 環境音（make_ambience.py の ambience.wav）の上に、要所だけ曲を重ねたBGMを作る
# 使い方: python -I tools/mix_music.py 01   → audio/ep01_draft/bgm.wav
# 組み立て: python -I tools/assemble.py --bgm audio/ep01_draft/bgm.wav
# 曲は audio/music/ に置く（YouTube オーディオライブラリ。曲だけを配れないので audio/ ごとリポジトリに入れない）
import json, subprocess, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRIPTS = {"01": "ep01_devon.txt", "02": "ep02_carboniferous.txt", "03": "ep03_permian.txt"}
# (曲ファイル, 台本の見出しの文字列, 鳴らす長さ秒（None は最後まで）, 見出しの何秒前から鳴らし始めるか)
CUES = {"03": [
    ("Event_Horizon.mp3", "# ===== 冒頭", 75, 0),
    ("False_Vacuum_Decay.mp3", "# ===== 4. 最大の絶滅", 70, 3),
    ("Laniakea.mp3", "# ===== 結び", None, 3),
], "02": [
    ("Event_Horizon.mp3", "# ===== 冒頭", 75, 0),
    ("False_Vacuum_Decay.mp3", "# ===== 9. 森が崩れる", 70, 3),
    ("Laniakea.mp3", "# ===== 結び", None, 3),
], "01": [
    ("Event_Horizon.mp3", "# ===== 冒頭", 75, 0),
    ("False_Vacuum_Decay.mp3", "# ===== 6. 海が息を止める", 70, 3),
    ("Laniakea.mp3", "# ===== 結び", None, 3),
]}
MUSIC_LUFS = -25   # 環境音（-24 LUFS）とほぼ同じ大きさで重ねる（全体はあとで組み立てツールがナレーションの20dB下にそろえる）
FADE_IN, FADE_OUT = 4, 8

def section_start(n, head):
    lines = (ROOT / "scripts" / SCRIPTS[n]).read_text(encoding="utf-8").split("\n")
    timing = json.load(open(ROOT / "audio" / f"ep{n}_draft" / "timing.json", encoding="utf-8"))
    starts = {r["line"]: r["start"] for r in timing}
    i = next(k for k, l in enumerate(lines, 1) if l.startswith(head))
    return starts[min(j for j in starts if j > i)] if i > 20 else 0.0

def main(n):
    amb = ROOT / "audio" / f"ep{n}_draft" / "ambience.wav"
    total = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(amb)],
                                 capture_output=True, text=True).stdout)
    cmd = ["ffmpeg", "-loglevel", "error", "-y", "-i", str(amb)]
    chains, labels = [], ["[0]"]
    for k, (f, head, dur, pre) in enumerate(CUES[n], 1):
        t0 = max(0.0, section_start(n, head) - pre)
        d = (total - t0) if dur is None else min(dur, total - t0)
        cmd += ["-i", str(ROOT / "audio" / "music" / f)]
        chains.append(f"[{k}]atrim=0:{d:.2f},asetpts=PTS-STARTPTS,loudnorm=I={MUSIC_LUFS}:TP=-3,aformat=sample_rates=48000:channel_layouts=stereo,"
                      f"afade=t=in:d={FADE_IN},afade=t=out:st={max(0, d - FADE_OUT):.2f}:d={FADE_OUT},adelay={int(t0 * 1000)}|{int(t0 * 1000)}[m{k}]")
        labels.append(f"[m{k}]")
        print(f"{f}: {int(t0 // 60)}:{int(t0 % 60):02d} から {d:.0f}秒")
    graph = ";".join(chains) + f";{''.join(labels)}amix=inputs={len(labels)}:normalize=0:duration=first,atrim=0:{total:.2f}[o]"
    out = ROOT / "audio" / f"ep{n}_draft" / "bgm.wav"
    subprocess.run(cmd + ["-filter_complex", graph, "-map", "[o]", "-c:a", "pcm_s16le", str(out)], check=True)
    print(out)

if __name__ == "__main__":
    main(sys.argv[1])
