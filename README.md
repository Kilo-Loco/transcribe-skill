# transcribe-skill

A [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skill that transcribes audio, video, and YouTube links **locally** using Apple SpeechAnalyzer on the Neural Engine. About 76x realtime, zero API cost, nothing leaves your Mac.

Self-contained: no MCP server, no Python packages, no API keys, no Xcode. On first use it downloads a ~160 KB prebuilt CLI (sha256-verified) from this repo's Releases. Prefer to compile it yourself? Pass `--build-from-source`; the Swift source is in the repo.

## Install

```bash
git clone https://github.com/Kilo-Loco/transcribe-skill ~/.claude/skills/transcribe
```

Restart Claude Code (or start a new session). Then just ask:

> transcribe ~/Movies/standup.mp4

> summarize https://www.youtube.com/watch?v=jNQXAC9IVRw

Claude runs the script, reads the transcript, and does whatever you asked with it: clean it up, summarize it, pull quotes, write captions.

## Requirements

- macOS 26 or later on Apple Silicon
- `ffmpeg` — `brew install ffmpeg`
- Xcode Command Line Tools — only if you want `--build-from-source` instead of the prebuilt binary
- `yt-dlp` for URLs — `brew install yt-dlp` (keep it updated; YouTube breaks old versions)

## Use it without Claude

```bash
python3 ~/.claude/skills/transcribe/scripts/transcribe.py video.mp4 [--language en-US] [--out-dir DIR]
python3 ~/.claude/skills/transcribe/scripts/transcribe.py "https://youtu.be/..." --out-dir ~/Downloads
```

Outputs `video.txt`, `video.srt` (YouTube-ready captions), and `video.json` (word-level timestamps) next to the source.

## Related

Need search across past transcripts, audio slices, chapter generation, or an MCP server? See [transcription-mcp](https://github.com/Kilo-Loco/transcription-mcp), which this skill is extracted from.

## How the binary is built

`scripts/release-cli.sh <tag>` compiles `apple-speech-cli/`, ad-hoc signs it, publishes it as a GitHub Release asset, and prints the sha256 to pin in `scripts/transcribe.py`. The binary links only Apple system frameworks.

## License

MIT
