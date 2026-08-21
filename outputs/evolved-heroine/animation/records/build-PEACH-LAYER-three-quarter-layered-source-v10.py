#!/usr/bin/env python3
"""Build the revised Peach three-quarter full-canvas RGBA layer package.

The approved visual target is never modified. Visible pixels are assigned to
exactly one semantic layer. Hidden overlap restoration is restricted to pixels
fully covered by a foreground layer in the approved neutral composition.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import zipfile
from collections import deque
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, tostring

from PIL import Image, ImageCms, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / "outputs/evolved-heroine/animation/rigs/source/PEACH-LAYER-three-quarter-candidate-v1-neutral.png"
PACKAGE = ROOT / "outputs/evolved-heroine/animation/rigs/source/PEACH-LAYER-three-quarter-layered-source-v10"
LAYERS = PACKAGE / "layers"
ARTIFACT_ID = "PEACH-LAYER-three-quarter-layered-source-v10"
EXPECTED_SOURCE_SHA256 = "3be0feb142374ba4ae9b1bf1dcdfde549cc56cde16188b3479548cce89b7ac9d"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def blank_mask(size: tuple[int, int]) -> Image.Image:
    return Image.new("L", size, 0)


def polygon(size: tuple[int, int], points: list[tuple[int, int]]) -> Image.Image:
    m = blank_mask(size)
    ImageDraw.Draw(m).polygon(points, fill=255)
    return m


def rectangle(size: tuple[int, int], box: tuple[int, int, int, int]) -> Image.Image:
    m = blank_mask(size)
    ImageDraw.Draw(m).rectangle(box, fill=255)
    return m


def ellipse(size: tuple[int, int], box: tuple[int, int, int, int]) -> Image.Image:
    m = blank_mask(size)
    ImageDraw.Draw(m).ellipse(box, fill=255)
    return m


def mask_and(a: Image.Image, b: Image.Image) -> Image.Image:
    return Image.new("L", a.size, 0).point(lambda _: 0) if a.size != b.size else Image.frombytes(
        "L", a.size, bytes(min(x, y) for x, y in zip(a.tobytes(), b.tobytes()))
    )


def mask_subtract(a: Image.Image, b: Image.Image) -> Image.Image:
    return Image.frombytes("L", a.size, bytes(x if y == 0 else 0 for x, y in zip(a.tobytes(), b.tobytes())))


def mask_or(a: Image.Image, b: Image.Image) -> Image.Image:
    return Image.frombytes("L", a.size, bytes(max(x, y) for x, y in zip(a.tobytes(), b.tobytes())))


def threshold_alpha(alpha: Image.Image, minimum: int = 1) -> Image.Image:
    return alpha.point(lambda p: 255 if p >= minimum else 0)


def color_select(image: Image.Image, region: Image.Image, predicate) -> Image.Image:
    rgba = image.load()
    reg = region.load()
    out = blank_mask(image.size)
    dst = out.load()
    for y in range(image.height):
        for x in range(image.width):
            if reg[x, y] and predicate(*rgba[x, y]):
                dst[x, y] = 255
    return out


def copy_with_mask(image: Image.Image, mask: Image.Image) -> Image.Image:
    out = image.copy()
    src_alpha = image.getchannel("A")
    out.putalpha(Image.frombytes("L", image.size, bytes(min(a, m) for a, m in zip(src_alpha.tobytes(), mask.tobytes()))))
    return out


def average_rgb(image: Image.Image, mask: Image.Image) -> tuple[int, int, int, int]:
    px = image.load()
    mp = mask.load()
    total = [0, 0, 0]
    count = 0
    for y in range(image.height):
        for x in range(image.width):
            if mp[x, y] and px[x, y][3] > 240:
                total[0] += px[x, y][0]
                total[1] += px[x, y][1]
                total[2] += px[x, y][2]
                count += 1
    if not count:
        return (242, 125, 73, 255)
    return tuple(round(v / count) for v in total) + (255,)


def average_rgb_filtered(image: Image.Image, mask: Image.Image, predicate) -> tuple[int, int, int, int]:
    px = image.load()
    mp = mask.load()
    total = [0, 0, 0]
    count = 0
    for y in range(image.height):
        for x in range(image.width):
            r, g, b, a = px[x, y]
            if mp[x, y] and a > 240 and predicate(r, g, b, a):
                total[0] += r; total[1] += g; total[2] += b
                count += 1
    if not count:
        return average_rgb(image, mask)
    return tuple(round(v / count) for v in total) + (255,)


def inpaint_nearest(image: Image.Image, holes: Image.Image, valid_region: Image.Image) -> Image.Image:
    """Fill holes with nearest non-hole source pixel inside valid_region."""
    out = image.copy()
    hp = holes.load()
    vp = valid_region.load()
    src = image.load()
    dst = out.load()
    q: deque[tuple[int, int]] = deque()
    owner: dict[tuple[int, int], tuple[int, int]] = {}
    for y in range(image.height):
        for x in range(image.width):
            if not hp[x, y] or not vp[x, y]:
                continue
            for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                if 0 <= nx < image.width and 0 <= ny < image.height and vp[nx, ny] and not hp[nx, ny] and src[nx, ny][3] > 240:
                    owner[(x, y)] = (nx, ny)
                    q.append((x, y))
                    break
    while q:
        x, y = q.popleft()
        ox, oy = owner[(x, y)]
        dst[x, y] = src[ox, oy]
        for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if 0 <= nx < image.width and 0 <= ny < image.height and hp[nx, ny] and vp[nx, ny] and (nx, ny) not in owner:
                owner[(nx, ny)] = (ox, oy)
                q.append((nx, ny))
    return out


def save_png(image: Image.Image, path: Path, icc_profile: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, format="PNG", optimize=False, icc_profile=icc_profile)


def make_ora(layer_paths: list[tuple[str, Path]], merged: Path, out: Path) -> None:
    root = Element("image", {"version": "0.0.1", "w": "1254", "h": "1254", "name": ARTIFACT_ID})
    stack = SubElement(root, "stack", {"name": "PEACH-3Q-ROOT"})
    # OpenRaster stack order is top-to-bottom.
    for name, path in reversed(layer_paths):
        SubElement(stack, "layer", {"name": name, "src": f"data/{path.name}", "visibility": "visible", "composite-op": "svg:src-over"})
    with zipfile.ZipFile(out, "w") as z:
        z.writestr("mimetype", "image/openraster", compress_type=zipfile.ZIP_STORED)
        z.writestr("stack.xml", tostring(root, encoding="utf-8", xml_declaration=True))
        z.write(merged, "mergedimage.png", compress_type=zipfile.ZIP_DEFLATED)
        with Image.open(merged) as im:
            thumb = im.copy()
            thumb.thumbnail((256, 256))
            thumb_path = PACKAGE / "thumbnail.png"
            thumb.save(thumb_path, format="PNG")
        z.write(thumb_path, "Thumbnails/thumbnail.png", compress_type=zipfile.ZIP_DEFLATED)
        for _, path in layer_paths:
            z.write(path, f"data/{path.name}", compress_type=zipfile.ZIP_DEFLATED)
    thumb_path.unlink()


def main() -> int:
    if PACKAGE.exists():
        raise SystemExit(f"Refusing to overwrite existing versioned package: {PACKAGE}")
    if sha256(SOURCE) != EXPECTED_SOURCE_SHA256:
        raise SystemExit("Approved source hash mismatch")

    source = Image.open(SOURCE).convert("RGBA")
    size = source.size
    if size != (1254, 1254):
        raise SystemExit(f"Unexpected source size: {size}")
    source_alpha = threshold_alpha(source.getchannel("A"), 1)
    opaque_source = threshold_alpha(source.getchannel("A"), 255)
    icc_profile = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()

    desired: dict[str, Image.Image] = {}
    # Back-to-front functional construction. L/R are anatomical.
    desired["01-LEAF-A"] = polygon(size, [(417, 145), (496, 145), (550, 139), (611, 174), (625, 239), (565, 231), (514, 238), (463, 218), (430, 185)])
    desired["02-LEAF-B"] = polygon(size, [(649, 178), (708, 143), (778, 145), (864, 148), (871, 172), (835, 213), (774, 235), (713, 222), (658, 240)])
    desired["03-STEM"] = polygon(size, [(591, 93), (657, 83), (672, 111), (671, 160), (654, 241), (612, 242), (608, 160), (591, 120)])

    desired["10-ANAT-R-ARM-UPPER"] = polygon(size, [(445, 552), (505, 566), (494, 657), (458, 669), (426, 651)])
    desired["11-ANAT-R-ARM-LOWER"] = polygon(size, [(426, 626), (493, 629), (483, 721), (429, 716), (411, 686)])
    desired["12-ANAT-L-ARM-UPPER"] = polygon(size, [(776, 527), (823, 527), (851, 614), (825, 658), (781, 642), (763, 570)])
    desired["13-ANAT-L-ARM-LOWER"] = polygon(size, [(789, 610), (850, 590), (865, 689), (832, 721), (784, 700), (770, 657)])

    desired["14-ANAT-R-LEG-UPPER"] = polygon(size, [(526, 677), (622, 677), (624, 827), (563, 835), (531, 775)])
    desired["15-ANAT-R-LEG-LOWER"] = polygon(size, [(548, 790), (624, 790), (621, 950), (548, 954)])
    desired["16-ANAT-L-LEG-UPPER"] = polygon(size, [(638, 679), (739, 680), (754, 820), (691, 835), (650, 781)])
    desired["17-ANAT-L-LEG-LOWER"] = polygon(size, [(671, 790), (752, 790), (766, 952), (691, 956)])

    desired["20-SHORTS"] = polygon(size, [(501, 588), (752, 587), (742, 748), (638, 748), (622, 724), (610, 748), (519, 747)])
    body_region = polygon(size, [(384, 354), (405, 278), (467, 229), (550, 214), (628, 232), (696, 214), (782, 225), (848, 277), (887, 362), (877, 493), (833, 580), (764, 631), (676, 660), (625, 670), (563, 652), (486, 615), (429, 548), (394, 464)])
    desired["30-PEACH-BODY-AND-SHADING-LOCKED"] = body_region
    face_field = polygon(size, [(474, 275), (668, 275), (730, 330), (733, 475), (671, 521), (505, 521), (420, 470), (420, 345)])
    # Placeholder retains z-order immediately above the body clean plate.
    desired["31-FACE-FIELD-TEXTURE-LOCKED"] = blank_mask(size)

    dark = lambda r, g, b, a: a > 0 and r < 105 and g < 95 and b < 90
    cream = lambda r, g, b, a: a > 0 and r > 190 and g > 165 and b > 115
    blush = lambda r, g, b, a: a > 0 and r > 185 and g < 125 and b < 115
    desired["40-ANAT-R-EYE"] = color_select(source, polygon(size, [(447, 324), (475, 307), (527, 324), (551, 378), (543, 432), (507, 455), (470, 434), (451, 389)]), lambda r, g, b, a: dark(r, g, b, a) or cream(r, g, b, a))
    desired["41-ANAT-L-EYE"] = color_select(source, polygon(size, [(590, 326), (625, 308), (679, 323), (708, 369), (699, 422), (663, 452), (618, 442), (594, 400)]), lambda r, g, b, a: dark(r, g, b, a) or cream(r, g, b, a))
    desired["42-ANAT-R-PUPIL"] = color_select(source, ellipse(size, (492, 340, 548, 438)), dark)
    desired["43-ANAT-L-PUPIL"] = color_select(source, ellipse(size, (638, 340, 698, 438)), dark)
    desired["44-ANAT-R-BROW"] = color_select(source, polygon(size, [(486, 282), (528, 281), (549, 310), (536, 317), (516, 298), (494, 306)]), dark)
    desired["45-ANAT-L-BROW"] = color_select(source, polygon(size, [(620, 283), (664, 282), (687, 304), (678, 315), (652, 299), (628, 307)]), dark)
    desired["46-ANAT-R-CHEEK"] = color_select(source, ellipse(size, (429, 410, 492, 472)), blush)
    desired["47-ANAT-L-CHEEK"] = color_select(source, ellipse(size, (653, 418, 726, 477)), blush)
    desired["48-NOSE-FIXED"] = color_select(source, rectangle(size, (522, 423, 585, 468)), dark)
    desired["49-MOUTH-NEUTRAL"] = color_select(source, rectangle(size, (520, 462, 641, 516)), dark)

    # The source is flattened, so antialiased feature edges contain blended
    # peach/ink colours. Expand only the already hand-bounded feature masks by
    # two pixels to capture those fringes and prevent remnants in the body
    # clean plate. Expanded source pixels travel with their feature layer and
    # therefore still recompose exactly at neutral.
    for face_name in (
        "40-ANAT-R-EYE", "41-ANAT-L-EYE", "42-ANAT-R-PUPIL",
        "43-ANAT-L-PUPIL", "44-ANAT-R-BROW", "45-ANAT-L-BROW",
        "46-ANAT-R-CHEEK", "47-ANAT-L-CHEEK", "48-NOSE-FIXED",
        "49-MOUTH-NEUTRAL",
    ):
        desired[face_name] = desired[face_name].filter(ImageFilter.MaxFilter(5))

    face_feature_union = blank_mask(size)
    for face_name in (
        "40-ANAT-R-EYE", "41-ANAT-L-EYE", "42-ANAT-R-PUPIL",
        "43-ANAT-L-PUPIL", "44-ANAT-R-BROW", "45-ANAT-L-BROW",
        "46-ANAT-R-CHEEK", "47-ANAT-L-CHEEK", "48-NOSE-FIXED",
        "49-MOUTH-NEUTRAL",
    ):
        face_feature_union = mask_or(face_feature_union, desired[face_name])
    desired["31-FACE-FIELD-TEXTURE-LOCKED"] = mask_subtract(face_field, face_feature_union)

    desired["50-ANAT-R-GLOVE-NEUTRAL"] = polygon(size, [(399, 662), (487, 659), (502, 711), (499, 779), (471, 831), (426, 824), (398, 782), (395, 718)])
    desired["51-ANAT-L-GLOVE-NEUTRAL"] = polygon(size, [(763, 667), (858, 665), (876, 712), (869, 778), (830, 834), (782, 827), (752, 787), (755, 722)])
    desired["52-ANAT-R-SHOE-BLANK"] = polygon(size, [(413, 882), (620, 879), (659, 951), (654, 1024), (601, 1050), (472, 1046), (409, 1016)])
    desired["53-ANAT-L-SHOE-ART"] = polygon(size, [(670, 878), (801, 877), (885, 932), (904, 1028), (873, 1078), (752, 1084), (678, 1045), (663, 978)])
    brand_region = polygon(size, [(697, 959), (792, 964), (804, 1019), (704, 1017)])
    desired["54-EVOLVED-BRAND-LOCKED"] = color_select(source, brand_region, lambda r, g, b, a: a > 0 and r > 220 and g > 155 and b > 110)

    # Restrict all semantic masks to source coverage.
    for name in list(desired):
        desired[name] = mask_and(desired[name], source_alpha)

    order = list(desired.keys())
    claimed = blank_mask(size)
    visible_masks: dict[str, Image.Image] = {}
    for name in reversed(order):
        visible_masks[name] = mask_subtract(desired[name], claimed)
        claimed = mask_or(claimed, desired[name])
    unassigned = mask_subtract(source_alpha, claimed)
    unassigned_initial_count = sum(1 for p in unassigned.tobytes() if p)
    # Audited path masks deliberately stop short of some antialiased contour
    # pixels. Assign those pixels to the nearest semantic mask bbox, with the
    # frontmost layer winning exact-distance ties. No colour inference is used.
    mask_pixels = {name: visible_masks[name].load() for name in order}
    bboxes = {name: desired[name].getbbox() for name in order}
    unassigned_pixels = unassigned.load()
    for y in range(size[1]):
        for x in range(size[0]):
            if not unassigned_pixels[x, y]:
                continue
            best_name = None
            best_score = None
            for z_index, name in enumerate(order):
                bbox = bboxes[name]
                if bbox is None:
                    continue
                left, top, right, bottom = bbox
                dx = left - x if x < left else x - (right - 1) if x >= right else 0
                dy = top - y if y < top else y - (bottom - 1) if y >= bottom else 0
                score = (dx * dx + dy * dy, -z_index)
                if best_score is None or score < best_score:
                    best_score = score
                    best_name = name
            if best_name is None:
                raise RuntimeError(f"No semantic owner for visible pixel {(x, y)}")
            mask_pixels[best_name][x, y] = 255
    reassigned = blank_mask(size)
    for name in order:
        reassigned = mask_or(reassigned, visible_masks[name])
    unassigned_count = sum(1 for p in mask_subtract(source_alpha, reassigned).tobytes() if p)

    face_holes = blank_mask(size)
    for name in ("40-ANAT-R-EYE", "41-ANAT-L-EYE", "42-ANAT-R-PUPIL", "43-ANAT-L-PUPIL", "44-ANAT-R-BROW", "45-ANAT-L-BROW", "46-ANAT-R-CHEEK", "47-ANAT-L-CHEEK", "48-NOSE-FIXED", "49-MOUTH-NEUTRAL"):
        face_holes = mask_or(face_holes, visible_masks[name])
    warm_peach = lambda r, g, b, a: a > 240 and r > 190 and 75 < g < 190 and b < 135 and r - g > 45
    corner_colors = {
        "top_left": average_rgb_filtered(source, rectangle(size, (420, 270, 480, 320)), warm_peach),
        "top_right": average_rgb_filtered(source, rectangle(size, (690, 270, 745, 320)), warm_peach),
        "bottom_left": average_rgb_filtered(source, rectangle(size, (420, 500, 490, 555)), warm_peach),
        "bottom_right": average_rgb_filtered(source, rectangle(size, (680, 500, 750, 555)), warm_peach),
    }
    body_restored = Image.new("RGBA", size, (0, 0, 0, 0))
    restored_px = body_restored.load()
    face_field_px = face_field.load()
    face_bbox = face_field.getbbox()
    if face_bbox is None:
        raise RuntimeError("Face field is empty")
    left, top, right, bottom = face_bbox
    for y in range(top, bottom):
        v = (y - top) / max(1, bottom - top - 1)
        for x in range(left, right):
            if not face_field_px[x, y]:
                continue
            u = (x - left) / max(1, right - left - 1)
            channels = []
            for channel in range(3):
                top_value = corner_colors["top_left"][channel] * (1 - u) + corner_colors["top_right"][channel] * u
                bottom_value = corner_colors["bottom_left"][channel] * (1 - u) + corner_colors["bottom_right"][channel] * u
                channels.append(round(top_value * (1 - v) + bottom_value * v))
            restored_px[x, y] = (*channels, 255)

    hidden_specs = {
        "01-LEAF-A": [(ellipse(size, (598, 211, 630, 247)), "30-PEACH-BODY-AND-SHADING-LOCKED")],
        "02-LEAF-B": [(ellipse(size, (654, 210, 686, 246)), "30-PEACH-BODY-AND-SHADING-LOCKED")],
        "03-STEM": [(rectangle(size, (629, 218, 655, 254)), "30-PEACH-BODY-AND-SHADING-LOCKED")],
        "10-ANAT-R-ARM-UPPER": [
            (ellipse(size, (447, 558, 490, 611)), "30-PEACH-BODY-AND-SHADING-LOCKED"),
            (ellipse(size, (441, 614, 482, 660)), "11-ANAT-R-ARM-LOWER"),
        ],
        "11-ANAT-R-ARM-LOWER": [(ellipse(size, (429, 673, 470, 709)), "50-ANAT-R-GLOVE-NEUTRAL")],
        "12-ANAT-L-ARM-UPPER": [
            (ellipse(size, (777, 540, 818, 597)), "30-PEACH-BODY-AND-SHADING-LOCKED"),
            (ellipse(size, (791, 611, 833, 657)), "13-ANAT-L-ARM-LOWER"),
        ],
        "13-ANAT-L-ARM-LOWER": [(ellipse(size, (801, 676, 843, 711)), "51-ANAT-L-GLOVE-NEUTRAL")],
        "14-ANAT-R-LEG-UPPER": [
            (polygon(size, [(525, 674), (614, 674), (614, 736), (550, 736)]), "__SOURCE_OPAQUE__"),
            (ellipse(size, (557, 789, 611, 834)), "15-ANAT-R-LEG-LOWER"),
        ],
        "15-ANAT-R-LEG-LOWER": [(ellipse(size, (557, 890, 608, 927)), "52-ANAT-R-SHOE-BLANK")],
        "16-ANAT-L-LEG-UPPER": [
            (polygon(size, [(647, 674), (740, 674), (713, 736), (647, 736)]), "__SOURCE_OPAQUE__"),
            (ellipse(size, (681, 790, 733, 836)), "17-ANAT-L-LEG-LOWER"),
        ],
        "17-ANAT-L-LEG-LOWER": [(ellipse(size, (708, 897, 758, 934)), "53-ANAT-L-SHOE-ART")],
    }

    layer_paths: list[tuple[str, Path]] = []
    metadata_layers = []
    for index, name in enumerate(order):
        visible = copy_with_mask(source, visible_masks[name])
        has_hidden_restoration = False
        if name in hidden_specs:
            hidden_mask = blank_mask(size)
            for shape, cover_name in hidden_specs[name]:
                if cover_name is None:
                    hidden_mask = mask_or(hidden_mask, shape)
                elif cover_name == "__SOURCE_OPAQUE__":
                    hidden_mask = mask_or(hidden_mask, mask_and(shape, opaque_source))
                else:
                    cover = mask_and(desired[cover_name], opaque_source)
                    hidden_mask = mask_or(hidden_mask, mask_and(shape, cover))
            if hidden_mask.getbbox():
                if "LEAF" in name:
                    fill_color = average_rgb_filtered(source, visible_masks[name], lambda r, g, b, a: g > 90 and r < 225 and b < 140 and g > b)
                elif name == "03-STEM":
                    fill_color = average_rgb_filtered(source, visible_masks[name], lambda r, g, b, a: r > 125 and 35 < g < 150 and b < 75)
                else:
                    fill_color = average_rgb_filtered(source, visible_masks[name], warm_peach)
                fill = Image.new("RGBA", size, fill_color)
                fill.putalpha(hidden_mask)
                visible = Image.alpha_composite(fill, visible)
                has_hidden_restoration = True
        if name == "30-PEACH-BODY-AND-SHADING-LOCKED":
            restored = copy_with_mask(body_restored, face_field)
            visible = Image.alpha_composite(restored, visible)
            has_hidden_restoration = True
        elif name in {"40-ANAT-R-EYE", "41-ANAT-L-EYE"}:
            pupil_name = "42-ANAT-R-PUPIL" if "R-EYE" in name else "43-ANAT-L-PUPIL"
            pupil_hole = visible_masks[pupil_name]
            eye_fill = Image.new("RGBA", size, (255, 245, 211, 0))
            eye_fill.putalpha(mask_and(pupil_hole, opaque_source))
            visible = Image.alpha_composite(eye_fill, visible)
        path = LAYERS / f"{index:02d}-{name}.png"
        save_png(visible, path, icc_profile)
        bbox = visible.getchannel("A").getbbox()
        layer_paths.append((name, path))
        metadata_layers.append({
            "name": name,
            "z_index_back_to_front": index,
            "path": str(path.relative_to(ROOT)),
            "sha256": sha256(path),
            "canvas": [1254, 1254],
            "bbox": list(bbox) if bbox else None,
            "laterality": "anatomical_right" if "ANAT-R" in name else "anatomical_left" if "ANAT-L" in name else None,
            "locked": name in {"30-PEACH-BODY-AND-SHADING-LOCKED", "31-FACE-FIELD-TEXTURE-LOCKED", "54-EVOLVED-BRAND-LOCKED"},
            "has_hidden_restoration": has_hidden_restoration,
        })

    merged = Image.new("RGBA", size, (0, 0, 0, 0))
    for _, path in layer_paths:
        merged = Image.alpha_composite(merged, Image.open(path).convert("RGBA"))
    merged_path = PACKAGE / f"{ARTIFACT_ID}-neutral-recomposite.png"
    save_png(merged, merged_path, icc_profile)

    # Pixel comparison ignores RGB values only when both pixels are fully
    # transparent; those values have no rendered meaning. Alpha is always
    # compared.
    src_pixels = source.load()
    merged_pixels = merged.load()
    differing_bytes = 0
    max_delta = 0
    differing_visible_pixels = 0
    for y in range(size[1]):
        for x in range(size[0]):
            src_pixel = src_pixels[x, y]
            merged_pixel = merged_pixels[x, y]
            if src_pixel[3] == 0 and merged_pixel[3] == 0:
                continue
            deltas = [abs(a - b) for a, b in zip(src_pixel, merged_pixel)]
            byte_diffs = sum(delta != 0 for delta in deltas)
            if byte_diffs:
                differing_visible_pixels += 1
                differing_bytes += byte_diffs
                max_delta = max(max_delta, max(deltas))

    ora_path = PACKAGE / f"{ARTIFACT_ID}.ora"
    make_ora(layer_paths, merged_path, ora_path)

    manifest = {
        "schema_version": 1,
        "artifact_id": ARTIFACT_ID,
        "status": "candidate_technical_qa",
        "construction_method": "deterministic hand-path regions, nearest semantic assignment for contour antialias pixels, exclusive visible-pixel ownership, and fixed hidden-overlap restoration",
        "approved_visual_target": {
            "path": str(SOURCE.relative_to(ROOT)),
            "sha256": EXPECTED_SOURCE_SHA256,
            "approval_record": "outputs/evolved-heroine/animation/qa/approvals/PEACH-LAYER-three-quarter-candidate-v1-visual-target-approval-2026-08-04.json",
        },
        "source_format": "full-canvas 8-bit RGBA PNG layers with embedded sRGB profile",
        "motion_ingest": "Import full-canvas PNG layers directly; PSD derivative remains conditional on isolated canary validation.",
        "canvas": [1254, 1254],
        "horizontal_flip_allowed": False,
        "brand_control": "Evolved is locked to anatomical-left shoe only",
        "layers_back_to_front": metadata_layers,
        "qa": {
            "initial_contour_pixels_reassigned_to_nearest_semantic_layer": unassigned_initial_count,
            "unassigned_visible_pixels": unassigned_count,
            "neutral_recomposite_differing_visible_pixels": differing_visible_pixels,
            "neutral_recomposite_differing_rgba_bytes": differing_bytes,
            "neutral_recomposite_max_channel_delta": max_delta,
            "neutral_recomposite_sha256": sha256(merged_path),
            "openraster_sha256": sha256(ora_path),
            "promotion_blocked_until_human_approval": True,
        },
    }
    manifest_path = PACKAGE / "layer-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest["qa"], indent=2))
    return 0 if unassigned_count == 0 and differing_bytes == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
