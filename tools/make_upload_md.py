# 投稿用の入力内容（タイトル・説明・タグ・設定）を video/epNN/epNN_upload.md に書き出す
# 使い方: python -I tools/make_upload_md.py 01
# 目次は台本の「# =====」「# -----」見出しの直後の行が始まる時刻（audio/epNN_draft/timing.json）から作る。章の名前は CHAPTERS で決める
# 参考文献は台本末尾の「# [n] ...」をそのまま並べ、doi:… は https://doi.org/… にする
import json, re, subprocess, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
n = sys.argv[1]
SCRIPT = ROOT / "scripts" / {"01": "ep01_devon.txt"}[n]
TIMING = ROOT / "audio" / f"ep{n}_draft" / "timing.json"
VIDEO = ROOT / "video" / f"ep{n}" / f"ep{n}_draft.mp4"

# 台本の見出し（# ===== 〜 =====）の順に、目次に出す名前。None は目次に出さない
CHAPTERS = {
    "01": ["オープニング", "デボン紀は「魚の時代」", "鎧の魚ダンクルオステウス", "この海の狩り", "3億8000万年前の礁",
           "礁の住人たち", "水辺に上がろうとした魚", "最初の森", "海から酸素が消える", "最後の海", "生き残った者たち", None],
}[n]
# 概要欄の字数を抑えるため、目次の参考文献から外す番号（台本には残す）
SKIP_REFS = {"01": {"16"}}[n]
TAGS = {"01": "デボン紀,ダンクルオステウス,古生物,古代生物,大量絶滅,ティクターリク,化石,恐竜以前,進化,ドキュメンタリー"}[n]
NOTES = {"01": [
    "・映像はAIで生成した画像を使った復元イメージです。画面右上に「確認（化石などで確かめられている）」「推定（研究者の推定・説が分かれる）」「演出（映像のための想像）」を表示しています。",
    "・体の色や細かな見た目の多くは分かっていません。",
    "・ナレーションは音声合成（VOICEVOX）です。",
    "・内容に誤りがあった場合は、固定コメントと概要欄で訂正します。",
]}[n]
LEAD = {"01": [
    "3億6000万年前の海で、頂点にいたのは「鎧の魚」でした。",
    "歯のない刃の顎、2023年に見直された体の大きさ、おなかで子を育てた魚、水辺に向かった魚、最初の森、そして2度の大量絶滅。最新の研究で、デボン紀の海をたどります。",
]}[n]

lines = SCRIPT.read_text(encoding="utf-8").split("\n")
timing = json.load(open(TIMING, encoding="utf-8"))
start_of = {r["line"]: r["start"] for r in timing}

# 見出しごとに、その後で最初に読む行の時刻
toc, k = [], 0
for i, l in enumerate(lines, 1):
    if l.startswith("# =====") or l.startswith("# -----"):
        name = CHAPTERS[k] if k < len(CHAPTERS) else None
        k += 1
        nxt = next((j for j in sorted(start_of) if j > i), None)
        if name and nxt is not None:
            t = 0 if not toc else max(0, start_of[nxt] - 0.3)
            toc.append(f"{int(t // 60)}:{int(t % 60):02d} {name}")

refs = []
for l in lines:
    m = re.match(r"# \[(\d+)\] (.+)", l)
    if m and not m.group(2).startswith("（") and m.group(1) not in SKIP_REFS:
        refs.append("・" + re.sub(r"doi:(10\.\S+)", r"https://doi.org/\1", m.group(2)))

title_m = re.search(r"#   A: (.+)", "\n".join(lines))
title = title_m.group(1).strip() if title_m else ""
desc = "\n".join(LEAD + ["", "▼目次"] + toc + ["", "▼参考文献"] + refs + ["", "▼この動画について"] + NOTES + ["", "音声：VOICEVOX:剣崎雌雄"])

dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(VIDEO)],
                           capture_output=True, text=True).stdout)
size = VIDEO.stat().st_size / 1e6
doc = f"""# 第{int(n)}話 投稿用の入力内容

- アップロードするファイル（すべて video/ep{n}/）
  - 動画：`ep{n}_draft.mp4`（1920×1080・30fps・{int(dur // 60)}分{int(dur % 60):02d}秒・{size:.1f}MB）
  - サムネイル：`ep{n}_thumbnail.png`（1280×720）
  - 字幕：`ep{n}_subtitles.srt`（日本語・タイミングあり）
- 目次の時刻は、ナレーションの時刻表から計算した値（動画の頭に何も足していない前提）
- タイトルは台本冒頭の案Aを仮に入れている。決まったら差し替える
- 説明は5,000字以内（YouTubeの上限）：現在 {len(desc)} 字

---

## タイトル（コピー用）
```
{title}
```

## 説明（コピー用）
```
{desc}
```

## タグ（コピー用・任意）
```
{TAGS}
```

---

## アップロード画面の設定
| 項目 | 選ぶもの |
|---|---|
| 再生リスト | なし（3〜4本たまったら「古代の地球」などの再生リストを作る） |
| 視聴者 | 「いいえ、子ども向けではありません」 |
| 改変されたコンテンツ（AIの使用） | **「はい」**（写実的なAI画像で、本物の映像と見間違える可能性があるため） |
| 自動チャプター | オン |
| カテゴリ | 教育 |
| 動画の言語 | 日本語 |
| ライセンス | 標準の YouTube ライセンス |
| ショート リミックス | リミックスを許可しない |
| コメント | オン／管理は標準／全員／人気順 |
| 字幕 | 「字幕」→「ファイルをアップロード」→「タイミングあり」で `ep{n}_subtitles.srt` |
"""
out = ROOT / "video" / f"ep{n}" / f"ep{n}_upload.md"
out.write_text(doc, encoding="utf-8")
print(out, len(desc), "字")
