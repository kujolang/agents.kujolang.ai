#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOWL_BIN="${HOWL:-}"

if [[ -z "$HOWL_BIN" ]] && command -v howl >/dev/null 2>&1; then
	HOWL_BIN="$(command -v howl)"
fi
if [[ -z "$HOWL_BIN" && -x "$ROOT/../howl/bin/howl" ]]; then
	HOWL_BIN="$ROOT/../howl/bin/howl"
fi
if [[ -z "$HOWL_BIN" || ! -x "$HOWL_BIN" ]]; then
	echo "ERROR: set HOWL to an executable Howl launcher" >&2
	exit 1
fi

cd "$ROOT"
python3 scripts/generate-social-manifest.py
"$HOWL_BIN" validate --manifest howl.json
"$HOWL_BIN" render --manifest howl.json --out .howl-social --format svg

mkdir -p assets/images/social
find assets/images/social -maxdepth 1 -type f \( -name '*.png' -o -name '*.jpg' \) -delete

rasterize() {
	local source="$1"
	local destination="$2"
	if command -v magick >/dev/null 2>&1; then
		magick "$source" -resize 1200x630! -quality 88 "$destination"
	elif command -v sips >/dev/null 2>&1; then
		sips -s format jpeg -s formatOptions 88 "$source" --out "$destination" >/dev/null
	else
		echo "ERROR: install ImageMagick (macOS sips is also supported)" >&2
		exit 1
	fi
}

rendered=0
while IFS= read -r source; do
	name="$(basename "$source" .svg)"
	rasterize "$source" "assets/images/social/$name.jpg"
	rendered=$((rendered + 1))
done < <(find .howl-social -maxdepth 1 -type f -name '*.svg' | sort)

expected="$(python3 -c 'import json; print(len(json.load(open("howl.json"))["cards"]))')"
if [[ "$rendered" -ne "$expected" ]]; then
	echo "ERROR: rendered $rendered cards, expected $expected" >&2
	exit 1
fi

echo "Rendered $rendered social cards to assets/images/social"
