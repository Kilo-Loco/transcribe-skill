#!/bin/bash
# Build, ad-hoc sign, and publish SpeechCLI as a GitHub Release asset.
# Usage: scripts/release-cli.sh <tag>   e.g. scripts/release-cli.sh cli-v1
# Afterwards, paste the printed CLI_TAG / CLI_SHA256 into scripts/transcribe.py.
set -euo pipefail
TAG="${1:?usage: release-cli.sh <tag>}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/apple-speech-cli"
swift build -c release
BIN=".build/release/SpeechCLI"
codesign --force --sign - "$BIN"
SHA=$(shasum -a 256 "$BIN" | cut -d' ' -f1)
gh release create "$TAG" "$BIN#SpeechCLI (arm64, macOS 26+)" \
  --title "SpeechCLI $TAG" \
  --notes "Prebuilt Apple SpeechAnalyzer CLI. arm64, macOS 26+, ad-hoc signed. sha256: $SHA"
echo "CLI_TAG = \"$TAG\""
echo "CLI_SHA256 = \"$SHA\""
