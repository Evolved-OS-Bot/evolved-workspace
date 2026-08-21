#!/usr/bin/env python3
"""Build checkerboard review sheets for an Evolved Heroine candidate batch."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


CELL_SIZE = 300
LABEL_HEIGHT = 42
GUTTER = 18
HEADER_HEIGHT = 64
CHECK_SIZE = 20
COLS = 4


def font(size: int) -> ImageFont.ImageFont:
    candidates = (
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
    )
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def checkerboard(size: int) -> Image.Image:
    image = Image.new("RGBA", (size, size), "#f4f4f4")
    draw = ImageDraw.Draw(image)
    for y in range(0, size, CHECK_SIZE):
        for x in range(0, size, CHECK_SIZE):
            if (x // CHECK_SIZE + y // CHECK_SIZE) % 2:
                draw.rectangle(
                    (x, y, x + CHECK_SIZE - 1, y + CHECK_SIZE - 1),
                    fill="#d8d8d8",
                )
    return image


def make_sheet(files: list[Path], title: str, output: Path) -> None:
    rows = (len(files) + COLS - 1) // COLS
    width = GUTTER + COLS * (CELL_SIZE + GUTTER)
    height = HEADER_HEIGHT + GUTTER + rows * (CELL_SIZE + LABEL_HEIGHT + GUTTER)
    sheet = Image.new("RGB", (width, height), "#202020")
    draw = ImageDraw.Draw(sheet)
    draw.text((GUTTER, 14), title, fill="white", font=font(28))

    for index, path in enumerate(files):
        row, col = divmod(index, COLS)
        x = GUTTER + col * (CELL_SIZE + GUTTER)
        y = HEADER_HEIGHT + GUTTER + row * (CELL_SIZE + LABEL_HEIGHT + GUTTER)
        panel = checkerboard(CELL_SIZE)
        candidate = Image.open(path).convert("RGBA")
        candidate.thumbnail((CELL_SIZE - 12, CELL_SIZE - 12), Image.Resampling.LANCZOS)
        px = (CELL_SIZE - candidate.width) // 2
        py = (CELL_SIZE - candidate.height) // 2
        panel.alpha_composite(candidate, (px, py))
        sheet.paste(panel.convert("RGB"), (x, y))
        asset_id = path.name.split("-", 1)[0]
        draw.text((x, y + CELL_SIZE + 8), asset_id, fill="white", font=font(20))

    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output, "PNG", optimize=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("batch_root", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()

    categories: list[tuple[str, list[Path]]] = []
    all_files: list[Path] = []
    for category_dir in sorted(path for path in args.batch_root.iterdir() if path.is_dir()):
        files = sorted((category_dir / "transparent").glob("*-candidate-v1.png"))
        if not files:
            continue
        categories.append((category_dir.name, files))
        all_files.extend(files)
        make_sheet(
            files,
            f"Evolved Heroine — {category_dir.name.replace('-', ' ').title()}",
            args.output_dir / f"{category_dir.name}-review-sheet.png",
        )

    make_sheet(
        all_files,
        f"Evolved Heroine — Remaining 42 Candidates ({len(all_files)} files)",
        args.output_dir / "remaining-42-contact-sheet.png",
    )


if __name__ == "__main__":
    main()
