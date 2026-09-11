---
name: transcribe
description: >
  Transcribe any audio or video file locally on a Mac using Apple SpeechAnalyzer
  (Neural Engine). Use when the user asks to transcribe, caption, subtitle, or
  "understand what is said in" a video/audio file, or wants an .srt or .txt
  transcript. Runs ~76x realtime, zero API cost, nothing leaves the machine.
license: MIT
compatibility: macOS 26+, Apple Silicon, ffmpeg, Xcode Command Line Tools (Swift) for a one-time build.
---

# Transcribe

Local, on-device transcription. No MCP server, no API key, no pip install.

## Run

```bash
python3 <skill-root>/scripts/transcribe.py "/absolute/path/to/video.mp4"
```

`<skill-root>` is the directory containing this SKILL.md (typically
`~/.claude/skills/transcribe`). Options:

- `--language es-ES` for a non-English locale (default `en-US`)
- `--out-dir DIR` to write outputs somewhere other than next to the source

The first run builds the bundled Swift CLI (~1 min). Later runs start instantly.

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
- `swift` missing: `xcode-select --install`
- SpeechAnalyzer may download a language model on first use for a new locale.
  This needs network once; then it is cached by macOS.

Do not modify `apple-speech-cli/` or rebuild manually. The script handles it.
