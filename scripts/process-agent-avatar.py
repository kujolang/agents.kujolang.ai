#!/usr/bin/env python3
"""Normalize a generated Kujo portrait into the site's avatar contract."""
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageOps


SIZE = (640, 640)
THRESHOLD = 192


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()

    with Image.open(args.source) as source:
        rgb = Image.new("RGB", source.size, "white")
        if source.mode == "RGBA":
            rgb.paste(source.convert("RGB"), mask=source.getchannel("A"))
        else:
            rgb.paste(source.convert("RGB"))
        fitted = ImageOps.fit(rgb, SIZE, method=Image.Resampling.LANCZOS)
        mono = ImageOps.autocontrast(fitted.convert("L"))
        stencil = mono.point(lambda value: 0 if value < THRESHOLD else 255, mode="1").convert("RGB")

    args.destination.parent.mkdir(parents=True, exist_ok=True)
    stencil.save(args.destination, format="WEBP", lossless=True, method=6)

    with Image.open(args.destination) as result:
        colors = result.convert("RGB").getcolors(maxcolors=3)
        if result.size != SIZE or colors is None or len(colors) > 2:
            raise RuntimeError(f"avatar contract failed: {args.destination}")

    print(args.destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
