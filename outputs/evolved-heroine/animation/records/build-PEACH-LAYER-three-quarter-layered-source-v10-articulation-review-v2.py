#!/usr/bin/env python3
"""Create non-rig articulation stress evidence from layered source v6."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageCms, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[4]
ARTIFACT_ID = "PEACH-LAYER-three-quarter-layered-source-v10"
PACKAGE = ROOT / f"outputs/evolved-heroine/animation/rigs/source/{ARTIFACT_ID}"
MANIFEST = PACKAGE / "layer-manifest.json"
REVIEW = ROOT / "outputs/evolved-heroine/animation/review/layered-source"
QA = ROOT / f"outputs/evolved-heroine/animation/qa/runs/{ARTIFACT_ID}"
OUT = REVIEW / f"{ARTIFACT_ID}-articulation-stress-sheet-v2.png"
REPORT = QA / "articulation-source-test-v2.json"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def font(size: int):
    path = Path("/System/Library/Fonts/Supplemental/Arial.ttf")
    try:
        return ImageFont.truetype(str(path), size)
    except OSError:
        return ImageFont.load_default()


def rotate(layer: Image.Image, angle: float, pivot: tuple[int, int]) -> Image.Image:
    return layer.rotate(angle, resample=Image.Resampling.BICUBIC, center=pivot, expand=False)


def translate(layer: Image.Image, dx: int, dy: int) -> Image.Image:
    out = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    out.alpha_composite(layer, (dx, dy))
    return out


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("Refusing to overwrite articulation evidence")
    manifest = json.loads(MANIFEST.read_text())
    ordered_names = [entry["name"] for entry in manifest["layers_back_to_front"]]
    layers = {entry["name"]: Image.open(ROOT / entry["path"]).convert("RGBA") for entry in manifest["layers_back_to_front"]}

    pivots = {
        "ANAT-R-ARM-root": (469, 583), "ANAT-R-ARM-bend": (460, 638),
        "ANAT-L-ARM-root": (796, 565), "ANAT-L-ARM-bend": (812, 636),
        "ANAT-R-LEG-root": (582, 680), "ANAT-R-LEG-bend": (582, 810),
        "ANAT-L-LEG-root": (678, 680), "ANAT-L-LEG-bend": (706, 811),
        "LEAF-A": (614, 226), "LEAF-B": (670, 226), "STEM": (642, 230),
    }

    def compose(rotations=None, translations=None):
        rotations = rotations or {}
        translations = translations or {}
        out = Image.new("RGBA", (1254, 1254), (0, 0, 0, 0))
        for name in ordered_names:
            layer = layers[name]
            if name in rotations:
                angle, pivot = rotations[name]
                layer = rotate(layer, angle, pivot)
            if name in translations:
                layer = translate(layer, *translations[name])
            out = Image.alpha_composite(out, layer)
        return out

    anat_r_arm = ["10-ANAT-R-ARM-UPPER", "11-ANAT-R-ARM-LOWER", "50-ANAT-R-GLOVE-NEUTRAL"]
    anat_l_arm = ["12-ANAT-L-ARM-UPPER", "13-ANAT-L-ARM-LOWER", "51-ANAT-L-GLOVE-NEUTRAL"]
    anat_r_lower_arm = ["11-ANAT-R-ARM-LOWER", "50-ANAT-R-GLOVE-NEUTRAL"]
    anat_l_lower_arm = ["13-ANAT-L-ARM-LOWER", "51-ANAT-L-GLOVE-NEUTRAL"]
    anat_r_leg = ["14-ANAT-R-LEG-UPPER", "15-ANAT-R-LEG-LOWER", "52-ANAT-R-SHOE-BLANK"]
    anat_l_leg = ["16-ANAT-L-LEG-UPPER", "17-ANAT-L-LEG-LOWER", "53-ANAT-L-SHOE-ART", "54-EVOLVED-BRAND-LOCKED"]
    anat_r_lower_leg = ["15-ANAT-R-LEG-LOWER", "52-ANAT-R-SHOE-BLANK"]
    anat_l_lower_leg = ["17-ANAT-L-LEG-LOWER", "53-ANAT-L-SHOE-ART", "54-EVOLVED-BRAND-LOCKED"]

    poses = [("Neutral exact source", compose())]
    rotations = {name: (20, pivots["ANAT-R-ARM-root"]) for name in anat_r_arm}
    rotations.update({name: (-20, pivots["ANAT-L-ARM-root"]) for name in anat_l_arm})
    poses.append(("Arm roots: 20° outward", compose(rotations)))
    rotations = {name: (-20, pivots["ANAT-R-ARM-bend"]) for name in anat_r_lower_arm}
    rotations.update({name: (20, pivots["ANAT-L-ARM-bend"]) for name in anat_l_lower_arm})
    poses.append(("Arm bends: 20°", compose(rotations)))
    rotations = {name: (12, pivots["ANAT-R-LEG-root"]) for name in anat_r_leg}
    rotations.update({name: (-12, pivots["ANAT-L-LEG-root"]) for name in anat_l_leg})
    poses.append(("Leg roots: 12° outward", compose(rotations)))
    rotations = {name: (-15, pivots["ANAT-R-LEG-bend"]) for name in anat_r_lower_leg}
    rotations.update({name: (15, pivots["ANAT-L-LEG-bend"]) for name in anat_l_lower_leg})
    poses.append(("Leg bends: 15°", compose(rotations)))
    poses.append(("Leaves 8° + stem 4°", compose({
        "01-LEAF-A": (8, pivots["LEAF-A"]),
        "02-LEAF-B": (-8, pivots["LEAF-B"]),
        "03-STEM": (4, pivots["STEM"]),
    })))
    poses.append(("Pupils: upper-left safe test", compose(translations={"42-ANAT-R-PUPIL": (-8, -5), "43-ANAT-L-PUPIL": (-8, -5)})))
    poses.append(("Pupils: lower-right safe test", compose(translations={"42-ANAT-R-PUPIL": (8, 5), "43-ANAT-L-PUPIL": (8, 5)})))

    columns, cell_w, cell_h, label_h = 3, 420, 420, 44
    rows = (len(poses) + columns - 1) // columns
    sheet = Image.new("RGB", (columns * cell_w, 70 + rows * (cell_h + label_h)), (247, 241, 231))
    draw = ImageDraw.Draw(sheet)
    draw.text((22, 18), "Layered-source stress poses: mechanics preview only, not rig approval", fill=(42, 18, 36), font=font(27))
    observations = []
    for i, (label, pose) in enumerate(poses):
        thumb = pose.copy()
        thumb.thumbnail((cell_w - 20, cell_h - 20), Image.Resampling.LANCZOS)
        bg = Image.new("RGBA", (cell_w, cell_h), (247, 241, 231, 255))
        bg.alpha_composite(thumb, ((cell_w - thumb.width) // 2, (cell_h - thumb.height) // 2))
        x = (i % columns) * cell_w
        y = 70 + (i // columns) * (cell_h + label_h)
        sheet.paste(bg.convert("RGB"), (x, y))
        draw.rectangle((x, y, x + cell_w - 1, y + cell_h + label_h - 1), outline=(92, 70, 85), width=2)
        draw.text((x + 10, y + cell_h + 9), label, fill=(42, 18, 36), font=font(17))
        bbox = pose.getchannel("A").getbbox()
        observations.append({"label": label, "alpha_bbox": list(bbox) if bbox else None, "canvas_clipped": bool(bbox and (bbox[0] == 0 or bbox[1] == 0 or bbox[2] == 1254 or bbox[3] == 1254))})

    icc = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()
    sheet.save(OUT, icc_profile=icc)
    report = {
        "schema_version": 1,
        "artifact_id": ARTIFACT_ID,
        "test_type": "pre_rig_source_articulation_stress",
        "status": "awaiting_human_visual_review",
        "scope": "Tests concealed source coverage only; does not approve pivots, deformation, rig controls, or any reusable motion.",
        "observations": observations,
        "technical_result": "pass" if not any(item["canvas_clipped"] for item in observations) else "fail",
        "review_sheet": str(OUT.relative_to(ROOT)),
        "review_sheet_sha256": sha256(OUT),
    }
    REPORT.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"technical_result": report["technical_result"], "poses": len(poses), "review_sheet_sha256": report["review_sheet_sha256"]}, indent=2))


if __name__ == "__main__":
    main()
