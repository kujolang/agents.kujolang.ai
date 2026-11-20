#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
mkdir -p assets/slack-portraits
for portrait in content/media/agents/*.webp; do
	name="$(basename "$portrait" .webp)"
	destination="assets/slack-portraits/$name.png"
	if command -v magick >/dev/null 2>&1; then
		magick "$portrait" "$destination"
	else
		sips -s format png "$portrait" --out "$destination" >/dev/null
	fi
done
