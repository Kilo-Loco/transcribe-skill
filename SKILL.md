---
name: transcribe
description: >
  Transcribe any audio or video file locally on a Mac using Apple SpeechAnalyzer
  (Neural Engine). Use when the user asks to transcribe, caption, subtitle, or
  "understand what is said in" a video/audio file or a YouTube/Vimeo link, or
  wants an .srt or .txt transcript. Runs ~76x realtime, zero API cost, and
  local files never leave the machine.
license: MIT
compatibility: macOS 26+, Apple Silicon, ffmpeg. yt-dlp for URLs. No Xcode needed (prebuilt binary is downloaded on first run).
---

# Transcribe

Local, on-device transcription. No MCP server, no API key, no pip install.

## Invocation

Invoked as `/transcribe $ARGUMENTS`.

- If `$ARGUMENTS` is a file path or URL, run the script on it immediately.
  Extra words after the path are the user's request for what to do with the
  transcript (e.g. `/transcribe talk.mp4 summarize in 5 bullets`).
- If `$ARGUMENTS` is empty, ask for a file path or URL. Do not guess a file.

## Run

```bash
python3 <skill-root>/scripts/transcribe.py "/absolute/path/to/video.mp4"
python3 <skill-root>/scripts/transcribe.py "https://www.youtube.com/watch?v=..."
```

`<skill-root>` is the directory containing this SKILL.md (typically
`~/.claude/skills/transcribe`). Options:

- `--language es-ES` for a non-English locale (default `en-US`)
- `--out-dir DIR` to write outputs somewhere other than next to the source
  (for URLs the default is the current directory, so prefer passing this)
- `--keep-download` to keep the downloaded audio when the input is a URL

The first run downloads a ~160 KB prebuilt SpeechCLI binary from this repo's
GitHub Releases into `bin/` and verifies its sha256. Later runs start instantly.
If the download fails (no network, proxy), it falls back to compiling the
bundled Swift source, which needs Xcode Command Line Tools. Pass
`--build-from-source` to skip the download and compile deliberately.

## What it produces

Next to the source file (or in `--out-dir`):

- `<name>.txt` — raw transcript, one segment per line
- `<name>.srt` — captions in ~4 second chunks, ready for YouTube upload
- `<name>.json` — word-level timestamps and confidences

Stdout is a JSON summary with the output paths, duration, word count, and a
500-character preview.

## After transcribing

1. Read the `.txt` file with the Read tool. For long files read it in chunks.
2. Clean up capitalization and punctuation and add paragraph breaks at topic
   changes. Do **not** guess word corrections from text alone. The Neural Engine
   output is usually more accurate than a guess from context.
3. Answer the user's actual question: present the cleaned transcript, summarize,
   pull quotes with timestamps from the `.json`, or whatever they asked for.

## Requirements and failure modes

The script fails fast with a specific message for each of these:

- Not macOS 26+ on Apple Silicon: SpeechAnalyzer is unavailable. Say so; do not
  try to substitute a cloud service without asking.
- `ffmpeg` missing: `brew install ffmpeg`
- Download blocked and `swift` missing: either allow access to github.com,
  set `TRANSCRIBE_CLI_URL` to an internal mirror of the binary, or install
  Xcode Command Line Tools (`xcode-select --install`) and rerun.
- `yt-dlp` missing (URLs only): `brew install yt-dlp`
- yt-dlp 403 or extractor error: YouTube changed something and yt-dlp is stale.
  Run `brew upgrade yt-dlp` and retry. This is the most common URL failure.
- SpeechAnalyzer may download a language model on first use for a new locale.
  This needs network once; then it is cached by macOS.

Do not modify `apple-speech-cli/`, `bin/`, or rebuild manually. The script handles it.
