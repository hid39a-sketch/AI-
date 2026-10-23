# 場面ごとの環境音をffmpegで合成し、台本の章の時刻に合わせてつないだBGMを1本作る（権利はすべて自前）
# 使い方: python -I tools/make_ambience.py 01            → audio/ep01_draft/ambience.wav
#         python -I tools/make_ambience.py --samples      → voice_samples/bgm/amb_<名前>.wav（各30秒の試聴版）
# 組み立て: python -I tools/assemble.py --bgm audio/ep01_draft/ambience.wav
# 章の区切りは台本の「# =====」「# -----」見出し。各章にどの音を当てるかは SCENES で決める
import json, subprocess, sys, pathlib, tempfile, os

ROOT = pathlib.Path(__file__).resolve().parent.parent
SR = 48000
XF = 6.0  # 場面の切り替えのクロスフェード（秒）

def noise(color, amp=0.5):
    return f"anoisesrc=color={color}:amplitude={amp}:sample_rate={SR}"

def sine(f):
    return f"sine=frequency={f}:sample_rate={SR}"

# 音の部品: (入力の作り方, そのあとのフィルター)。音量の揺らぎは volume の式で付ける（tremolo は 0.1Hz 未満が使えないため）
def drone(freqs, base=0.3):
    parts = []
    for i, f in enumerate(freqs):
        period = [20, 14, 9, 7, 11][i % 5]
        parts.append((sine(f), f"volume='{base / (i + 1):.3f}*(0.55+0.45*sin(2*PI*t/{period}+{i}))':eval=frame"))
    return parts

def water(cut=350, amp=0.7, period=13):
    return [(noise("brown", 0.6), f"lowpass=f={cut},lowpass=f={cut},volume='{amp}*(0.7+0.3*sin(2*PI*t/{period}))':eval=frame")]

def bubbles(every=2.3, freq=900, amp=0.25):
    # 帯域を絞った白色雑音を、短く間欠的に鳴らす（周期をずらした2系統で不規則に聞こえるように）
    g = f"if(lt(mod(t,{every}),0.05),1,0)+if(lt(mod(t+0.9,{every * 1.37:.2f}),0.03),0.7,0)"
    return [(noise("white", 0.5), f"bandpass=f={freq}:width_type=q:w=4,volume='{amp}*({g})':eval=frame")]

def waves(period=6.5, amp=0.5):
    return [(noise("pink", 0.6), f"lowpass=f=1400,highpass=f=120,volume='{amp}*pow(0.5+0.5*sin(2*PI*t/{period}),2)':eval=frame")]

def wind(amp=0.35, period=11):
    return [(noise("pink", 0.5), f"bandpass=f=700:width_type=q:w=0.8,volume='{amp}*(0.4+0.6*pow(0.5+0.5*sin(2*PI*t/{period}),2))':eval=frame")]

def buzz(amp=0.06, freq=2400, period=5):
    # 遠くの羽音（高い帯域の雑音を、ゆっくり強弱させる）
    return [(noise("white", 0.4), f"bandpass=f={freq}:width_type=q:w=6,volume='{amp}*pow(0.5+0.5*sin(2*PI*t/{period}),3)':eval=frame")]

def drips(amp=0.15):
    g = "if(lt(mod(t,3.1),0.012),1,0)+if(lt(mod(t+1.7,4.7),0.012),0.8,0)+if(lt(mod(t+0.4,5.9),0.012),0.6,0)"
    return [(sine(1400), f"volume='{amp}*({g})':eval=frame,aecho=0.6:0.5:180:0.3")]

# 場面ごとの音（A音を基準に、明るい場面は5度・オクターブ、暗い場面は低く短3度）
TEXTURES = {
    "shallow": water(500, 0.6) + drone([55, 82.41, 110, 164.81], 0.30) + bubbles(3.1, 1100, 0.12),
    "deep":    water(260, 0.8, 17) + drone([41.2, 61.74, 82.41], 0.34),
    "reef":    water(700, 0.5) + drone([65.41, 98, 130.81, 196], 0.26) + bubbles(1.7, 1300, 0.18),
    "shore":   waves(6.5, 0.45) + wind(0.18, 13) + drone([55, 82.41, 110], 0.16),
    "forest":  wind(0.30, 11) + drips(0.12) + drone([49, 73.42, 98], 0.14),
    "murky":   water(300, 0.75, 19) + drone([43.65, 51.91, 65.41], 0.30),
    "dark":    water(200, 0.85, 23) + drone([36.71, 43.65, 55], 0.32),
    "swamp":   water(420, 0.45, 15) + drips(0.10) + buzz(0.05, 2400, 6) + drone([49, 73.42, 98, 146.83], 0.18),
    "dry":     wind(0.40, 9) + drone([41.2, 61.74, 82.41], 0.20),
    "calm":    water(600, 0.5) + drone([55, 82.41, 110, 138.59, 164.81], 0.26) + bubbles(4.3, 1000, 0.08),
}

# 台本の見出しの順に当てる音（ep01：冒頭,1,2,2b,3,3b,4,5,6,7,結び,参考文献）
# ep03：冒頭,1,2,3,4,5,6,7,8,結び,参考文献（乾いた内陸→グロッソプテリスの森→絶滅の海→火山→生き残り→回復）
# ep04〜06：冒頭,1〜9（ep05は1〜8）,結び,参考文献
SCENES = {"04": ["dry", "dry", "deep", "shore", "forest", "dry", "swamp", "calm", "dark", "dry", "calm", None],
          "05": ["swamp", "shore", "forest", "deep", "dry", "dry", "forest", "forest", "calm", "calm", None],
          "06": ["swamp", "shallow", "forest", "forest", "swamp", "forest", "deep", "shore", "forest", "dry", "calm", None],
          "03": ["dry", "dry", "dry", "forest", "murky", "dark", "murky", "dry", "shore", "calm", None],
          "02": ["swamp", "swamp", "calm", "swamp", "forest", "shore", "calm", "murky", "forest", "dry", "calm", None],
          "01": ["shallow", "shallow", "shallow", "deep", "reef", "reef", "shore", "forest", "murky", "dark", "calm", None]}
SCRIPTS = {"01": "ep01_devon.txt", "02": "ep02_carboniferous.txt", "03": "ep03_permian.txt", "04": "ep04_triassic.txt", "05": "ep05_jurassic.txt", "06": "ep06_cretaceous.txt"}

def render(name, dur, out):
    parts = TEXTURES[name]
    cmd = ["ffmpeg", "-loglevel", "error", "-y"]
    for src, _ in parts:
        cmd += ["-f", "lavfi", "-t", f"{dur:.3f}", "-i", src]
    chains = [f"[{i}]{flt}[p{i}]" for i, (_, flt) in enumerate(parts)]
    mix = "".join(f"[p{i}]" for i in range(len(parts)))
    graph = ";".join(chains) + f";{mix}amix=inputs={len(parts)}:normalize=0,aecho=0.8:0.7:1200|1900:0.35|0.25,loudnorm=I=-24:TP=-3,aformat=sample_rates={SR}:channel_layouts=stereo[o]"
    subprocess.run(cmd + ["-filter_complex", graph, "-map", "[o]", "-c:a", "pcm_s16le", str(out)], check=True)

def sections(n):
    lines = (ROOT / "scripts" / SCRIPTS[n]).read_text(encoding="utf-8").split("\n")
    timing = json.load(open(ROOT / "audio" / f"ep{n}_draft" / "timing.json", encoding="utf-8"))
    starts = {r["line"]: r["start"] for r in timing}
    total = timing[-1]["end"] + 3.0
    secs, k = [], 0
    for i, l in enumerate(lines, 1):
        if l.startswith("# =====") or l.startswith("# -----"):
            name = SCENES[n][k] if k < len(SCENES[n]) else None
            k += 1
            nxt = next((j for j in sorted(starts) if j > i), None)
            if name and nxt is not None:
                t = 0.0 if not secs else starts[nxt]
                if secs and secs[-1][0] == name:
                    continue  # 同じ音が続くときはつなげたまま
                secs.append((name, t))
    return [(name, t, (secs[i + 1][1] if i + 1 < len(secs) else total)) for i, (name, t) in enumerate(secs)]

def build(n):
    secs = sections(n)
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="amb_"))
    files = []
    for i, (name, a, b) in enumerate(secs):
        dur = (b - a) + (XF if i + 1 < len(secs) else 0) + (XF if i > 0 else 0) / 2
        f = tmp / f"{i:02d}_{name}.wav"
        render(name, dur, f)
        files.append(f)
        print(f"{int(a // 60)}:{int(a % 60):02d}〜{int(b // 60)}:{int(b % 60):02d} {name}")
    # 順にクロスフェードでつなぐ。切り替えの中心が章の始まりに来るよう、各場面を XF/2 早めに始めている
    cmd = ["ffmpeg", "-loglevel", "error", "-y"]
    for f in files:
        cmd += ["-i", str(f)]
    graph, prev = [], "[0]"
    for i in range(1, len(files)):
        out = f"[x{i}]"
        graph.append(f"{prev}[{i}]acrossfade=d={XF}:c1=tri:c2=tri{out}")
        prev = out
    out = ROOT / "audio" / f"ep{n}_draft" / "ambience.wav"
    fade_out = secs[-1][2] - 6
    graph.append(f"{prev}afade=t=in:d=3,afade=t=out:st={fade_out:.2f}:d=6,atrim=0:{secs[-1][2]:.2f}[o]")
    subprocess.run(cmd + ["-filter_complex", ";".join(graph), "-map", "[o]", "-c:a", "pcm_s16le", str(out)], check=True)
    print(out)

if __name__ == "__main__":
    if sys.argv[1] == "--samples":
        d = ROOT / "voice_samples" / "bgm"
        d.mkdir(parents=True, exist_ok=True)
        for name in TEXTURES:
            render(name, 30, d / f"amb_{name}.wav")
            print("ok", name)
    else:
        build(sys.argv[1])
