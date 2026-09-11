#!/usr/bin/env python3
"""Transcribe an audio or video file locally with Apple SpeechAnalyzer.

Stdlib only. Requires macOS 26+, Apple Silicon, ffmpeg, and Swift (Xcode
Command Line Tools) for the one-time build of the bundled SpeechCLI.

Usage:
    python3 transcribe.py <media-file-or-url> [--language en-US] [--out-dir DIR]

Accepts a local file or a URL (YouTube, Vimeo, anything yt-dlp supports).
URLs are downloaded as audio with yt-dlp first (brew install yt-dlp).

Writes <name>.txt, <name>.srt and <name>.json next to the source file
(or into --out-dir; for URLs the default is the current directory) and
prints a short JSON summary to stdout.
"""

from __future__ import annotations

import argparse
import json
import platform
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
CLI_SRC = SKILL_ROOT / "apple-speech-cli"
CLI_BIN = CLI_SRC / ".build" / "release" / "SpeechCLI"


def die(msg: str) -> None:
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(1)


def check_platform() -> None:
    if platform.system() != "Darwin":
        die("requires macOS (Apple SpeechAnalyzer is macOS-only).")
    if int(platform.release().split(".")[0]) < 25:
        die("requires macOS 26 or later.")
    if platform.machine() != "arm64":
        die("requires Apple Silicon (Neural Engine).")
    if shutil.which("ffmpeg") is None:
        die("ffmpeg not found. Install with: brew install ffmpeg")


def ensure_cli() -> Path:
    if CLI_BIN.exists():
        return CLI_BIN
    if shutil.which("swift") is None:
        die("Swift toolchain not found. Install Xcode Command Line Tools: xcode-select --install")
    print("Building SpeechCLI (one-time, ~1 min)...", file=sys.stderr)
    r = subprocess.run(["swift", "build", "-c", "release"], cwd=CLI_SRC, capture_output=True, text=True)
    if r.returncode != 0 or not CLI_BIN.exists():
        die(f"SpeechCLI build failed:\n{r.stderr}")
    return CLI_BIN


def is_url(s: str) -> bool:
    return s.startswith(("http://", "https://"))


def download_url(url: str, out_dir: Path) -> Path:
    """Download the audio track of a URL with yt-dlp. Returns the local file."""
    if shutil.which("yt-dlp") is None:
        die("yt-dlp not found (needed for URLs). Install with: brew install yt-dlp")
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"Downloading audio from {url} ...", file=sys.stderr)
    r = subprocess.run(
        [
            "yt-dlp", "--no-playlist", "-f", "bestaudio/best",
            "-x", "--audio-format", "m4a",
            "--restrict-filenames",
            "-o", str(out_dir / "%(title).120s [%(id)s].%(ext)s"),
            "--print", "after_move:filepath", "--no-simulate", "--quiet",
            url,
        ],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        die(
            f"yt-dlp failed:\n{r.stderr[-2000:]}\n\n"
            "YouTube changes often; a 403 or extractor error usually means yt-dlp "
            "is out of date. Update it and retry: brew upgrade yt-dlp"
        )
    path = Path(r.stdout.strip().splitlines()[-1])
    if not path.exists():
        die(f"yt-dlp reported {path} but it does not exist")
    return path


def extract_audio(src: Path) -> tuple[Path, bool]:
    """Return (wav_path, is_temp)."""
    if src.suffix.lower() == ".wav":
        return src, False
    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    tmp.close()
    out = Path(tmp.name)
    r = subprocess.run(
        ["ffmpeg", "-i", str(src), "-ar", "16000", "-ac", "1", "-f", "wav", "-y", str(out)],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        out.unlink(missing_ok=True)
        die(f"ffmpeg failed:\n{r.stderr[-2000:]}")
    return out, True


def srt_time(s: float) -> str:
    h = int(s // 3600)
    m = int((s % 3600) // 60)
    sec = int(s % 60)
    ms = round((s % 1) * 1000)
    return f"{h:02d}:{m:02d}:{sec:02d},{ms:03d}"


def to_srt(segments: list[dict], max_duration: float = 4.0) -> str:
    words = [w for seg in segments for w in seg.get("words", [])]
    lines: list[str] = []
    if not words:
        for i, seg in enumerate(segments, 1):
            lines += [str(i), f"{srt_time(seg['start'])} --> {srt_time(seg['end'])}", seg.get("text", ""), ""]
        return "\n".join(lines)
    n, i = 0, 0
    while i < len(words):
        start_t = words[i]["start"]
        j = i
        for k in range(i, len(words)):
            if words[k]["end"] - start_t > max_duration and k > i:
                break
            j = k
        n += 1
        text = " ".join(w["word"] for w in words[i:j + 1])
        lines += [str(n), f"{srt_time(words[i]['start'])} --> {srt_time(words[j]['end'])}", text, ""]
        i = j + 1
    return "\n".join(lines)


def to_txt(segments: list[dict]) -> str:
    return "\n".join(
        (seg.get("text") or " ".join(w["word"] for w in seg.get("words", []))).strip()
        for seg in segments
    ).strip() + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file", help="audio/video file, or a URL (YouTube etc.)")
    ap.add_argument("--language", default="en-US", help="BCP-47 locale, e.g. en-US, es-ES (default: en-US)")
    ap.add_argument("--out-dir", help="directory for outputs (default: next to source, or cwd for URLs)")
    ap.add_argument("--keep-download", action="store_true", help="keep the downloaded audio file for URLs")
    args = ap.parse_args()

    check_platform()
    cli = ensure_cli()

    downloaded = False
    if is_url(args.file):
        out_dir = Path(args.out_dir).expanduser().resolve() if args.out_dir else Path.cwd()
        src = download_url(args.file, out_dir)
        downloaded = True
    else:
        src = Path(args.file).expanduser().resolve()
        if not src.exists():
            die(f"file not found: {src}")
        out_dir = Path(args.out_dir).expanduser().resolve() if args.out_dir else src.parent

    wav, is_temp = extract_audio(src)
    try:
        r = subprocess.run([str(cli), str(wav), args.language], capture_output=True, text=True, timeout=14400)
    finally:
        if is_temp:
            wav.unlink(missing_ok=True)
    if r.returncode != 0:
        die(f"SpeechCLI failed:\n{r.stderr[-2000:]}")

    data = json.loads(r.stdout)
    segments = data.get("segments", [])

    out_dir.mkdir(parents=True, exist_ok=True)
    stem = out_dir / src.stem
    txt_path, srt_path, json_path = stem.with_suffix(".txt"), stem.with_suffix(".srt"), stem.with_suffix(".json")

    txt = to_txt(segments)
    txt_path.write_text(txt)
    srt_path.write_text(to_srt(segments))
    json_path.write_text(json.dumps(data, indent=2))

    if downloaded and not args.keep_download:
        src.unlink(missing_ok=True)

    word_count = sum(len(s.get("words", [])) for s in segments)
    duration = float(data.get("duration") or (segments[-1]["end"] if segments else 0.0))
    print(json.dumps({
        "source": args.file,
        "txt": str(txt_path),
        "srt": str(srt_path),
        "json": str(json_path),
        "duration_seconds": round(duration, 1),
        "word_count": word_count,
        "language": data.get("language", args.language),
        "preview": txt[:500],
    }, indent=2))


if __name__ == "__main__":
    main()
