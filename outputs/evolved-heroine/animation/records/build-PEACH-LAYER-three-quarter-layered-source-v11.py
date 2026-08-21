#!/usr/bin/env python3
"""Build the non-destructive v11 shoe-opacity correction from approved v10.

The repair changes alpha only in enclosed, low-opacity regions of the two shoe
artworks. It does not redraw Peach, modify exterior transparency, touch the
locked brand layer, or overwrite the approved v10 package.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import zipfile
from collections import deque
from datetime import datetime
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, tostring
from zoneinfo import ZoneInfo

from PIL import Image, ImageCms, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[4]
V10_ID = "PEACH-LAYER-three-quarter-layered-source-v10"
V11_ID = "PEACH-LAYER-three-quarter-layered-source-v11"
V10 = ROOT / f"outputs/evolved-heroine/animation/rigs/approved/{V10_ID}"
V11 = ROOT / f"outputs/evolved-heroine/animation/rigs/source/{V11_ID}"
REVIEW = ROOT / "outputs/evolved-heroine/animation/review/layered-source"
QA = ROOT / f"outputs/evolved-heroine/animation/qa/runs/{V11_ID}"
EXPECTED_V10_NEUTRAL_SHA256 = "e0693adf9bc2f694f8e01c0e109f44268c3c8c5d9a667f801b382d3643dd4180"
EXPECTED_BRAND_SHA256 = "1d860384a579b5ad633a49f21fabc481ab65d11184c4433af5d1b321e22493da"

SHOE_SPECS = {
    "52-ANAT-R-SHOE-BLANK": {
        "filename": "26-52-ANAT-R-SHOE-BLANK.png",
        "roi": (400, 860, 670, 1065),
        "interior_polygons": (
            # Tongue.
            ((511, 907), (518, 891), (543, 882), (568, 888), (582, 903), (582, 925), (562, 936), (531, 931)),
            # Toe, vamp, and quarter fabric; deliberately inset from the
            # antialiased exterior contour and outsole.
            ((436, 975), (448, 952), (473, 937), (504, 929), (535, 932), (561, 929), (593, 934), (620, 947), (633, 968), (630, 995), (608, 1008), (568, 1017), (520, 1017), (478, 1009), (446, 997)),
        ),
    },
    "53-ANAT-L-SHOE-ART": {
        "filename": "27-53-ANAT-L-SHOE-ART.png",
        "roi": (650, 860, 920, 1100),
        "interior_polygons": (
            # Tongue only. The branded shoe upper was already opaque and the
            # locked lettering remains a separate untouched layer.
            ((690, 912), (699, 895), (727, 885), (758, 889), (779, 902), (785, 920), (777, 938), (744, 945), (710, 934)),
        ),
    },
}
ALPHA_THRESHOLDS = (1, 248)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def now_brisbane() -> str:
    return datetime.now(ZoneInfo("Australia/Brisbane")).isoformat(timespec="seconds")


def srgb_profile() -> bytes:
    return ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()


def enclosed_low_alpha_pixels(
    alpha: Image.Image,
    roi: tuple[int, int, int, int],
    threshold: int,
) -> set[tuple[int, int]]:
    """Return low-alpha pixels not connected to the ROI boundary."""
    x0, y0, x1, y1 = roi
    low = {
        (x, y)
        for y in range(y0, y1)
        for x in range(x0, x1)
        if alpha.getpixel((x, y)) < threshold
    }
    exterior: set[tuple[int, int]] = set()
    queue: deque[tuple[int, int]] = deque()
    for x in range(x0, x1):
        for point in ((x, y0), (x, y1 - 1)):
            if point in low and point not in exterior:
                exterior.add(point)
                queue.append(point)
    for y in range(y0, y1):
        for point in ((x0, y), (x1 - 1, y)):
            if point in low and point not in exterior:
                exterior.add(point)
                queue.append(point)
    while queue:
        x, y = queue.popleft()
        for point in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if point in low and point not in exterior:
                exterior.add(point)
                queue.append(point)
    return low - exterior


def polygon_pixels(
    size: tuple[int, int],
    polygons: tuple[tuple[tuple[int, int], ...], ...],
) -> set[tuple[int, int]]:
    mask = Image.new("1", size, 0)
    draw = ImageDraw.Draw(mask)
    for points in polygons:
        draw.polygon(points, fill=1)
    return {
        (x, y)
        for y in range(size[1])
        for x in range(size[0])
        if mask.getpixel((x, y))
    }


def composite(layer_paths: list[Path]) -> Image.Image:
    merged = Image.new("RGBA", (1254, 1254), (0, 0, 0, 0))
    for path in layer_paths:
        merged = Image.alpha_composite(merged, Image.open(path).convert("RGBA"))
    return merged


def make_ora(layer_records: list[dict], merged_path: Path, out_path: Path) -> None:
    root = Element("image", {"version": "0.0.1", "w": "1254", "h": "1254", "name": V11_ID})
    stack = SubElement(root, "stack", {"name": "PEACH-3Q-ROOT"})
    for record in reversed(layer_records):
        path = ROOT / record["path"]
        SubElement(
            stack,
            "layer",
            {
                "name": record["name"],
                "src": f"data/{path.name}",
                "visibility": "visible",
                "composite-op": "svg:src-over",
            },
        )
    with zipfile.ZipFile(out_path, "w") as archive:
        archive.writestr("mimetype", "image/openraster", compress_type=zipfile.ZIP_STORED)
        archive.writestr("stack.xml", tostring(root, encoding="utf-8", xml_declaration=True))
        archive.write(merged_path, "mergedimage.png", compress_type=zipfile.ZIP_DEFLATED)
        thumb = Image.open(merged_path).convert("RGBA")
        thumb.thumbnail((256, 256), Image.Resampling.LANCZOS)
        thumb_path = V11 / "thumbnail.png"
        thumb.save(thumb_path, format="PNG")
        archive.write(thumb_path, "Thumbnails/thumbnail.png", compress_type=zipfile.ZIP_DEFLATED)
        thumb_path.unlink()
        for record in layer_records:
            path = ROOT / record["path"]
            archive.write(path, f"data/{path.name}", compress_type=zipfile.ZIP_DEFLATED)


def checker(size: tuple[int, int], tile: int = 24) -> Image.Image:
    image = Image.new("RGBA", size, (242, 239, 234, 255))
    draw = ImageDraw.Draw(image)
    for y in range(0, size[1], tile):
        for x in range(0, size[0], tile):
            if (x // tile + y // tile) % 2:
                draw.rectangle((x, y, x + tile - 1, y + tile - 1), fill=(187, 182, 178, 255))
    return image


def on_background(subject: Image.Image, background: Image.Image | tuple[int, int, int, int]) -> Image.Image:
    canvas = background if isinstance(background, Image.Image) else Image.new("RGBA", subject.size, background)
    return Image.alpha_composite(canvas, subject).convert("RGB")


def font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for candidate in (
        Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf"),
        Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
        Path("/System/Library/Fonts/Helvetica.ttc"),
    ):
        if candidate.exists():
            try:
                return ImageFont.truetype(str(candidate), size)
            except OSError:
                pass
    return ImageFont.load_default()


def build_review(
    v10_neutral: Image.Image,
    v11_neutral: Image.Image,
    repair_pixels: set[tuple[int, int]],
    icc_profile: bytes,
) -> list[Path]:
    REVIEW.mkdir(parents=True, exist_ok=True)
    crop_box = (390, 845, 925, 1110)
    scale = 2
    crop_size = ((crop_box[2] - crop_box[0]) * scale, (crop_box[3] - crop_box[1]) * scale)

    def checked_crop(subject: Image.Image) -> Image.Image:
        crop = subject.crop(crop_box).resize(crop_size, Image.Resampling.NEAREST)
        return on_background(crop, checker(crop_size, 24))

    heat = Image.new("RGBA", v11_neutral.size, (0, 0, 0, 0))
    heat_pixels = heat.load()
    for x, y in repair_pixels:
        heat_pixels[x, y] = (255, 35, 114, 255)
    heat_crop = heat.crop(crop_box).resize(crop_size, Image.Resampling.NEAREST)
    heat_panel = on_background(heat_crop, (35, 26, 35, 255))

    title_h = 92
    panel_w, panel_h = crop_size
    sheet = Image.new("RGB", (panel_w * 3, title_h + panel_h), (247, 242, 233))
    sheet.paste(checked_crop(v10_neutral), (0, title_h))
    sheet.paste(checked_crop(v11_neutral), (panel_w, title_h))
    sheet.paste(heat_panel, (panel_w * 2, title_h))
    draw = ImageDraw.Draw(sheet)
    labels = (
        "V10 — checker leaking through",
        "V11 — enclosed shoe artwork opaque",
        f"Alpha-only repair mask — {len(repair_pixels):,} px",
    )
    for index, label in enumerate(labels):
        draw.text((index * panel_w + 24, 27), label, fill=(45, 22, 39), font=font(28))
        draw.rectangle(
            (index * panel_w, title_h, (index + 1) * panel_w - 1, title_h + panel_h - 1),
            outline=(87, 64, 80),
            width=2,
        )
    closeup_path = REVIEW / f"{V11_ID}-shoe-opacity-review.png"
    sheet.save(closeup_path, icc_profile=icc_profile)

    backgrounds = Image.new("RGB", (1254 * 3, 1254), (255, 255, 255))
    backgrounds.paste(on_background(v11_neutral, (247, 241, 231, 255)), (0, 0))
    backgrounds.paste(on_background(v11_neutral, (42, 18, 36, 255)), (1254, 0))
    backgrounds.paste(on_background(v11_neutral, checker(v11_neutral.size, 36)), (2508, 0))
    backgrounds_path = REVIEW / f"{V11_ID}-light-dark-checker.png"
    backgrounds.save(backgrounds_path, icc_profile=icc_profile)
    return [closeup_path, backgrounds_path]


def main() -> None:
    if V11.exists() or QA.exists() or any(REVIEW.glob(f"{V11_ID}-*")):
        raise SystemExit("Refusing to overwrite an existing v11 package, QA run, or review artifact")

    v10_neutral_path = V10 / f"{V10_ID}-neutral-recomposite.png"
    brand_path = V10 / "layers/28-54-EVOLVED-BRAND-LOCKED.png"
    if sha256(v10_neutral_path) != EXPECTED_V10_NEUTRAL_SHA256:
        raise SystemExit("Approved v10 neutral hash mismatch")
    if sha256(brand_path) != EXPECTED_BRAND_SHA256:
        raise SystemExit("Approved locked-brand hash mismatch")

    v10_manifest = json.loads((V10 / "layer-manifest.json").read_text())
    v10_neutral = Image.open(v10_neutral_path).convert("RGBA")
    neutral_alpha = v10_neutral.getchannel("A")
    icc = Image.open(v10_neutral_path).info.get("icc_profile") or srgb_profile()

    repair_masks: dict[str, set[tuple[int, int]]] = {}
    for layer_name, spec in SHOE_SPECS.items():
        pixels: set[tuple[int, int]] = set()
        for threshold in ALPHA_THRESHOLDS:
            pixels |= enclosed_low_alpha_pixels(neutral_alpha, spec["roi"], threshold)
        audited_interior = polygon_pixels(v10_neutral.size, spec["interior_polygons"])
        repair_masks[layer_name] = pixels & audited_interior

    V11.mkdir(parents=True)
    layers_dir = V11 / "layers"
    shutil.copytree(V10 / "layers", layers_dir)

    layer_records = []
    non_shoe_hash_match = True
    alpha_only_change = True
    for record in v10_manifest["layers_back_to_front"]:
        updated = dict(record)
        source_path = V10 / "layers" / Path(record["path"]).name
        target_path = layers_dir / source_path.name
        before_hash = sha256(source_path)
        if record["name"] in repair_masks:
            image = Image.open(target_path).convert("RGBA")
            original_pixels = list(image.get_flattened_data())
            pixels = image.load()
            for x, y in repair_masks[record["name"]]:
                r, g, b, _ = pixels[x, y]
                pixels[x, y] = (r, g, b, 255)
            image.save(target_path, format="PNG", optimize=False, icc_profile=icc)
            changed_pixels = list(image.get_flattened_data())
            alpha_only_change &= all(
                before[:3] == after[:3]
                for before, after in zip(original_pixels, changed_pixels)
            )
        else:
            non_shoe_hash_match &= sha256(target_path) == before_hash
        updated["path"] = str(target_path.relative_to(ROOT))
        updated["sha256"] = sha256(target_path)
        updated["opacity_correction_pixels"] = len(repair_masks.get(record["name"], set()))
        layer_records.append(updated)

    layer_paths = [ROOT / record["path"] for record in layer_records]
    v11_neutral = composite(layer_paths)
    v11_neutral_path = V11 / f"{V11_ID}-neutral-recomposite.png"
    v11_neutral.save(v11_neutral_path, format="PNG", optimize=False, icc_profile=icc)

    repair_union = set().union(*repair_masks.values())
    v10_pixels = v10_neutral.load()
    v11_pixels = v11_neutral.load()
    alpha_differences = set()
    differing_pixels_from_v10 = 0
    differing_rgba_bytes_from_v10 = 0
    maximum_channel_delta_from_v10 = 0
    rgb_differences_outside_repair = 0
    alpha_differences_outside_repair = 0
    for y in range(1254):
        for x in range(1254):
            before = v10_pixels[x, y]
            after = v11_pixels[x, y]
            deltas = tuple(abs(a - b) for a, b in zip(before, after))
            if any(deltas):
                differing_pixels_from_v10 += 1
                differing_rgba_bytes_from_v10 += sum(delta != 0 for delta in deltas)
                maximum_channel_delta_from_v10 = max(maximum_channel_delta_from_v10, max(deltas))
            if before[3] != after[3]:
                alpha_differences.add((x, y))
                if (x, y) not in repair_union:
                    alpha_differences_outside_repair += 1
            if before[:3] != after[:3] and (x, y) not in repair_union:
                rgb_differences_outside_repair += 1

    brand_unchanged = sha256(layers_dir / brand_path.name) == EXPECTED_BRAND_SHA256
    v11_manifest = dict(v10_manifest)
    v11_manifest.update(
        {
            "artifact_id": V11_ID,
            "status": "awaiting_human_layered_source_approval",
            "construction_method": (
                "Approved v10 layered source plus deterministic alpha-only restoration "
                "inside enclosed low-opacity shoe artwork; exterior alpha and locked brand preserved"
            ),
            "correction_basis": {
                "source_artifact_id": V10_ID,
                "source_path": str(V10.relative_to(ROOT)),
                "source_neutral_sha256": EXPECTED_V10_NEUTRAL_SHA256,
                "defect": "Checkerboard showed through distressed shoe fabric and both tongues because low alpha was baked into the source artwork.",
                "approval_required": True,
                "rig_construction_resumption_blocked_until_approval": True,
            },
            "layers_back_to_front": layer_records,
            "qa": {
                **v10_manifest["qa"],
                "neutral_recomposite_sha256": sha256(v11_neutral_path),
                "neutral_recomposite_differing_visible_pixels": differing_pixels_from_v10,
                "neutral_recomposite_differing_rgba_bytes": differing_rgba_bytes_from_v10,
                "neutral_recomposite_max_channel_delta": maximum_channel_delta_from_v10,
                "neutral_comparison_basis": (
                    "Intentional corrective difference from approved v10; v10 was exact to the "
                    "original visual target but retained defective shoe alpha."
                ),
                "corrective_difference_from_v10": True,
                "shoe_internal_opacity_repair_pixels": {
                    name: len(pixels) for name, pixels in repair_masks.items()
                },
                "shoe_internal_opacity_repair_pixels_total": len(repair_union),
                "neutral_alpha_differences_from_v10": len(alpha_differences),
                "alpha_differences_outside_repair_mask": alpha_differences_outside_repair,
                "rgb_differences_outside_repair_mask": rgb_differences_outside_repair,
                "shoe_layer_rgb_channels_unchanged": alpha_only_change,
                "all_non_shoe_layer_files_byte_identical_to_v10": non_shoe_hash_match,
                "locked_brand_layer_byte_identical_to_v10": brand_unchanged,
                "exterior_alpha_preserved": alpha_differences_outside_repair == 0,
            },
        }
    )
    manifest_path = V11 / "layer-manifest.json"
    manifest_path.write_text(json.dumps(v11_manifest, indent=2) + "\n")

    ora_path = V11 / f"{V11_ID}.ora"
    make_ora(layer_records, v11_neutral_path, ora_path)
    v11_manifest["qa"]["openraster_sha256"] = sha256(ora_path)
    manifest_path.write_text(json.dumps(v11_manifest, indent=2) + "\n")
    review_paths = build_review(v10_neutral, v11_neutral, repair_union, icc)

    checks = [
        {
            "check_id": "V10_APPROVED_SOURCE_HASH",
            "status": "pass",
            "sha256": EXPECTED_V10_NEUTRAL_SHA256,
        },
        {
            "check_id": "ALPHA_ONLY_SHOE_LAYER_CHANGE",
            "status": "pass" if alpha_only_change else "fail",
        },
        {
            "check_id": "EXTERIOR_ALPHA_PRESERVED",
            "status": "pass" if alpha_differences_outside_repair == 0 else "fail",
            "differences_outside_repair_mask": alpha_differences_outside_repair,
            "repair_mask_constraint": "Audited inset shoe-interior polygons only",
        },
        {
            "check_id": "RGB_OUTSIDE_REPAIR_PRESERVED",
            "status": "pass" if rgb_differences_outside_repair == 0 else "fail",
            "differences_outside_repair_mask": rgb_differences_outside_repair,
        },
        {
            "check_id": "NON_SHOE_LAYERS_BYTE_IDENTICAL",
            "status": "pass" if non_shoe_hash_match else "fail",
            "unchanged_layer_count": 27,
        },
        {
            "check_id": "LEFT_SHOE_BRAND_LOCK_BYTE_IDENTICAL",
            "status": "pass" if brand_unchanged else "fail",
            "sha256": sha256(layers_dir / brand_path.name),
        },
        {
            "check_id": "HUMAN_LAYERED_SOURCE_APPROVAL",
            "status": "pending",
        },
    ]
    technical_result = (
        "pass"
        if all(check["status"] == "pass" for check in checks if check["check_id"] != "HUMAN_LAYERED_SOURCE_APPROVAL")
        else "fail"
    )
    QA.mkdir(parents=True)
    qa_report = {
        "schema_version": 1,
        "run_id": f"{V11_ID}-qa-v1",
        "artifact_id": V11_ID,
        "executed_at": now_brisbane(),
        "technical_result": technical_result,
        "visual_result": "pending_human_review",
        "repair_method": {
            "alpha_thresholds": list(ALPHA_THRESHOLDS),
            "topology": "Only low-alpha pixels enclosed from the exterior within each audited shoe ROI",
            "pixels_by_layer": {name: len(pixels) for name, pixels in repair_masks.items()},
            "total_pixels": len(repair_union),
        },
        "checks": checks,
        "review_evidence": [str(path.relative_to(ROOT)) for path in review_paths],
    }
    qa_path = QA / "qa-report.json"
    qa_path.write_text(json.dumps(qa_report, indent=2) + "\n")

    source_record = {
        "schema_version": 1,
        "artifact_id": V11_ID,
        "status": "awaiting_human_layered_source_approval",
        "created_at": now_brisbane(),
        "correction_of": {
            "artifact_id": V10_ID,
            "approved_snapshot_path": str(V10.relative_to(ROOT)),
            "approved_snapshot_unchanged": True,
        },
        "package": {
            "layer_manifest": {
                "path": str(manifest_path.relative_to(ROOT)),
                "sha256": sha256(manifest_path),
            },
            "openraster": {
                "path": str(ora_path.relative_to(ROOT)),
                "sha256": sha256(ora_path),
            },
            "neutral_recomposite": {
                "path": str(v11_neutral_path.relative_to(ROOT)),
                "sha256": sha256(v11_neutral_path),
            },
            "layer_count": 29,
            "layer_format": "1254x1254 8-bit RGBA PNG with embedded sRGB profile",
        },
        "controls": {
            "horizontal_flip_allowed": False,
            "negative_x_scale_allowed": False,
            "left_shoe_brand_layer_unchanged": brand_unchanged,
            "human_approval_required_before_rig_use": True,
        },
        "qa_report": str(qa_path.relative_to(ROOT)),
        "promotion_blocked_until_human_approval": True,
    }
    record_path = V11 / "source-package-record.json"
    record_path.write_text(json.dumps(source_record, indent=2) + "\n")
    # Refresh the manifest hash after the source record is written; the record
    # intentionally does not participate in its own checksum.

    print(
        json.dumps(
            {
                "artifact_id": V11_ID,
                "technical_result": technical_result,
                "repair_pixels_by_layer": {
                    name: len(pixels) for name, pixels in repair_masks.items()
                },
                "total_repair_pixels": len(repair_union),
                "alpha_differences_outside_repair_mask": alpha_differences_outside_repair,
                "rgb_differences_outside_repair_mask": rgb_differences_outside_repair,
                "locked_brand_unchanged": brand_unchanged,
                "neutral_sha256": sha256(v11_neutral_path),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
