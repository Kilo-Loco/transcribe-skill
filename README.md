# transcribe-skill

A [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skill that transcribes audio and video **locally** using Apple SpeechAnalyzer on the Neural Engine. About 76x realtime, zero API cost, nothing leaves your Mac.

Self-contained: no MCP server, no Python packages, no API keys. It bundles a tiny Swift CLI that is built once on first use.

## Install

```bash
git clone https://github.com/Kilo-Loco/transcribe-skill ~/.claude/skills/transcribe
```

Restart Claude Code (or start a new session). Then just ask:

> transcribe ~/Movies/standup.mp4

Claude runs the script, reads the transcript, and does whatever you asked with it: clean it up, summarize it, pull quotes, write captions.

## Requirements

- macOS 26 or later on Apple Silicon
- `ffmpeg` — `brew install ffmpeg`
- Xcode Command Line Tools — `xcode-select --install` (Swift is used once to build the CLI)

## Use it without Claude

```bash
python3 ~/.claude/skills/transcribe/scripts/transcribe.py video.mp4 [--language en-US] [--out-dir DIR]
```

Outputs `video.txt`, `video.srt` (YouTube-ready captions), and `video.json` (word-level timestamps) next to the source.

## Related

Need search across past transcripts, audio slices, chapter generation, or an MCP server? See [transcription-mcp](https://github.com/Kilo-Loco/transcription-mcp), which this skill is extracted from.

## License

MIT
