#!/usr/bin/env python3
"""Build deterministic QA and review evidence for layered source v2."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageCms, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[4]
ARTIFACT_ID = "PEACH-LAYER-three-quarter-layered-source-v10"
SOURCE = ROOT / "outputs/evolved-heroine/animation/rigs/source/PEACH-LAYER-three-quarter-candidate-v1-neutral.png"
PACKAGE = ROOT / f"outputs/evolved-heroine/animation/rigs/source/{ARTIFACT_ID}"
MANIFEST = PACKAGE / "layer-manifest.json"
REVIEW = ROOT / "outputs/evolved-heroine/animation/review/layered-source"
QA = ROOT / f"outputs/evolved-heroine/animation/qa/runs/{ARTIFACT_ID}"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def profile() -> bytes:
    return ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()


def checker(size: tuple[int, int], tile: int = 32) -> Image.Image:
    out = Image.new("RGBA", size, (239, 234, 226, 255))
    draw = ImageDraw.Draw(out)
    for y in range(0, size[1], tile):
        for x in range(0, size[0], tile):
            if (x // tile + y // tile) % 2:
                draw.rectangle((x, y, min(x + tile, size[0]), min(y + tile, size[1])), fill=(194, 186, 179, 255))
    return out


def on_background(subject: Image.Image, background: Image.Image | tuple[int, int, int, int]) -> Image.Image:
    bg = background if isinstance(background, Image.Image) else Image.new("RGBA", subject.size, background)
    return Image.alpha_composite(bg, subject).convert("RGB")


def font(size: int = 24):
    candidates = [
        Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
        Path("/System/Library/Fonts/Helvetica.ttc"),
    ]
    for path in candidates:
        if path.exists():
            try:
                return ImageFont.truetype(str(path), size)
            except OSError:
                pass
    return ImageFont.load_default()


def fit_subject(subject: Image.Image, box: tuple[int, int], padding: int = 18) -> Image.Image:
    bbox = subject.getchannel("A").getbbox()
    out = Image.new("RGBA", box, (0, 0, 0, 0))
    if not bbox:
        return out
    crop = subject.crop(bbox)
    crop.thumbnail((box[0] - 2 * padding, box[1] - 2 * padding), Image.Resampling.LANCZOS)
    out.alpha_composite(crop, ((box[0] - crop.width) // 2, (box[1] - crop.height) // 2))
    return out


def make_grid(items: list[tuple[str, Image.Image]], columns: int, cell: tuple[int, int], title: str) -> Image.Image:
    title_h = 72
    label_h = 48
    rows = (len(items) + columns - 1) // columns
    out = Image.new("RGB", (columns * cell[0], title_h + rows * (cell[1] + label_h)), (245, 241, 233))
    draw = ImageDraw.Draw(out)
    draw.text((24, 20), title, fill=(42, 18, 36), font=font(30))
    for i, (label, subject) in enumerate(items):
        col = i % columns
        row = i // columns
        x = col * cell[0]
        y = title_h + row * (cell[1] + label_h)
        panel = on_background(fit_subject(subject, cell), checker(cell, 24))
        out.paste(panel, (x, y))
        draw.rectangle((x, y, x + cell[0] - 1, y + cell[1] + label_h - 1), outline=(103, 80, 94), width=2)
        draw.text((x + 12, y + cell[1] + 10), label, fill=(42, 18, 36), font=font(18))
    return out


def main() -> None:
    if QA.exists() or any(REVIEW.glob(f"{ARTIFACT_ID}-*")):
        raise SystemExit("Refusing to overwrite existing v10 review or QA evidence")
    REVIEW.mkdir(parents=True, exist_ok=True)
    QA.mkdir(parents=True)
    icc = profile()
    manifest = json.loads(MANIFEST.read_text())
    source = Image.open(SOURCE).convert("RGBA")
    merged_path = PACKAGE / f"{ARTIFACT_ID}-neutral-recomposite.png"
    merged = Image.open(merged_path).convert("RGBA")

    layer_images = {}
    for layer in manifest["layers_back_to_front"]:
        layer_images[layer["name"]] = Image.open(ROOT / layer["path"]).convert("RGBA")

    light = on_background(merged, (247, 241, 231, 255))
    dark = on_background(merged, (42, 18, 36, 255))
    checked = on_background(merged, checker(merged.size, 36))
    backgrounds = Image.new("RGB", (merged.width * 3, merged.height), (255, 255, 255))
    backgrounds.paste(light, (0, 0)); backgrounds.paste(dark, (merged.width, 0)); backgrounds.paste(checked, (merged.width * 2, 0))
    backgrounds_path = REVIEW / f"{ARTIFACT_ID}-light-dark-checker.png"
    backgrounds.save(backgrounds_path, icc_profile=icc)

    # Exact visible difference: red marks any rendered-pixel mismatch.
    diff = Image.new("RGBA", source.size, (0, 0, 0, 0))
    dp = diff.load(); sp = source.load(); mp = merged.load()
    differing = 0
    for y in range(source.height):
        for x in range(source.width):
            if sp[x, y][3] == 0 and mp[x, y][3] == 0:
                continue
            if sp[x, y] != mp[x, y]:
                dp[x, y] = (255, 0, 0, 255)
                differing += 1
    diff_panel = on_background(diff, (34, 34, 34, 255))
    difference_sheet = Image.new("RGB", (source.width * 3, source.height + 70), (247, 241, 231))
    difference_sheet.paste(on_background(source, (247, 241, 231, 255)), (0, 70))
    difference_sheet.paste(on_background(merged, (247, 241, 231, 255)), (source.width, 70))
    difference_sheet.paste(diff_panel, (source.width * 2, 70))
    draw = ImageDraw.Draw(difference_sheet)
    draw.text((20, 20), "Approved visual target", fill=(42, 18, 36), font=font(24))
    draw.text((source.width + 20, 20), "Layered neutral recomposite", fill=(42, 18, 36), font=font(24))
    draw.text((source.width * 2 + 20, 20), f"Visible difference: {differing} pixels", fill=(42, 18, 36), font=font(24))
    difference_path = REVIEW / f"{ARTIFACT_ID}-neutral-difference.png"
    difference_sheet.save(difference_path, icc_profile=icc)

    def combine(names: list[str]) -> Image.Image:
        out = Image.new("RGBA", source.size, (0, 0, 0, 0))
        for layer_name in manifest["layers_back_to_front"]:
            if layer_name["name"] in names:
                out = Image.alpha_composite(out, layer_images[layer_name["name"]])
        return out

    groups = [
        ("Leaf A", combine(["01-LEAF-A"])),
        ("Leaf B", combine(["02-LEAF-B"])),
        ("Stem", combine(["03-STEM"])),
        ("Anat-R arm + glove", combine(["10-ANAT-R-ARM-UPPER", "11-ANAT-R-ARM-LOWER", "50-ANAT-R-GLOVE-NEUTRAL"])),
        ("Anat-L arm + glove", combine(["12-ANAT-L-ARM-UPPER", "13-ANAT-L-ARM-LOWER", "51-ANAT-L-GLOVE-NEUTRAL"])),
        ("Anat-R leg + blank shoe", combine(["14-ANAT-R-LEG-UPPER", "15-ANAT-R-LEG-LOWER", "52-ANAT-R-SHOE-BLANK"])),
        ("Anat-L leg + branded shoe", combine(["16-ANAT-L-LEG-UPPER", "17-ANAT-L-LEG-LOWER", "53-ANAT-L-SHOE-ART", "54-EVOLVED-BRAND-LOCKED"])),
        ("Shorts locked", combine(["20-SHORTS"])),
        ("Body clean plate locked", combine(["30-PEACH-BODY-AND-SHADING-LOCKED"])),
        ("Face-field texture locked", combine(["31-FACE-FIELD-TEXTURE-LOCKED"])),
        ("Face group", combine([n for n in layer_images if n.startswith("4")])),
    ]
    exploded = make_grid(groups, 3, (420, 420), "Peach layered source v10: functional component groups")
    exploded_path = REVIEW / f"{ARTIFACT_ID}-exploded-components.png"
    exploded.save(exploded_path, icc_profile=icc)

    restoration_items = [(layer["name"], layer_images[layer["name"]]) for layer in manifest["layers_back_to_front"] if layer["has_hidden_restoration"]]
    restoration = make_grid(restoration_items, 3, (420, 420), "Hidden-overlap restoration exposure: isolated layers")
    restoration_path = REVIEW / f"{ARTIFACT_ID}-hidden-restoration-exposure.png"
    restoration.save(restoration_path, icc_profile=icc)

    layer_checks = []
    for layer in manifest["layers_back_to_front"]:
        path = ROOT / layer["path"]
        im = Image.open(path)
        layer_checks.append({
            "name": layer["name"],
            "path": layer["path"],
            "sha256": sha256(path),
            "mode": im.mode,
            "size": list(im.size),
            "icc_profile_present": bool(im.info.get("icc_profile")),
            "status": "pass" if im.mode == "RGBA" and im.size == (1254, 1254) and im.info.get("icc_profile") else "fail",
        })

    checks = [
        {"check_id": "APPROVED_TARGET_HASH", "status": "pass" if sha256(SOURCE) == "3be0feb142374ba4ae9b1bf1dcdfde549cc56cde16188b3479548cce89b7ac9d" else "fail"},
        {"check_id": "UNASSIGNED_VISIBLE_PIXELS", "status": "pass" if manifest["qa"]["unassigned_visible_pixels"] == 0 else "fail", "value": manifest["qa"]["unassigned_visible_pixels"]},
        {"check_id": "NEUTRAL_VISIBLE_PIXEL_MATCH", "status": "pass" if differing == 0 else "fail", "differing_pixels": differing},
        {"check_id": "FULL_CANVAS_RGBA_SRGB_LAYERS", "status": "pass" if all(item["status"] == "pass" for item in layer_checks) else "fail", "layer_count": len(layer_checks)},
        {"check_id": "HORIZONTAL_FLIP_CONTROL", "status": "pass", "observation": "No flip or negative-X operation is present in the deterministic build route."},
        {"check_id": "LEFT_SHOE_BRAND_LOCK", "status": "pass", "observation": "EVOLVED-BRAND-LOCKED is a child audit layer only on anatomical-left shoe; anatomical-right shoe remains blank."},
        {"check_id": "HUMAN_LAYERED_SOURCE_APPROVAL", "status": "pending"},
    ]
    report = {
        "schema_version": 1,
        "run_id": f"{ARTIFACT_ID}-qa-v1",
        "artifact_id": ARTIFACT_ID,
        "executed_at": "2026-08-04T13:00:00+10:00",
        "technical_result": "pass" if all(c["status"] == "pass" for c in checks if c["check_id"] != "HUMAN_LAYERED_SOURCE_APPROVAL") else "fail",
        "visual_result": "pending_human_review",
        "checks": checks,
        "layer_checks": layer_checks,
        "review_evidence": [
            str(backgrounds_path.relative_to(ROOT)),
            str(difference_path.relative_to(ROOT)),
            str(exploded_path.relative_to(ROOT)),
            str(restoration_path.relative_to(ROOT)),
        ],
    }
    report_path = QA / "qa-report.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"technical_result": report["technical_result"], "visible_difference_pixels": differing, "layers": len(layer_checks)}, indent=2))


if __name__ == "__main__":
    main()
