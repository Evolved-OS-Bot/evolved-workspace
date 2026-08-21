#!/usr/bin/env python3
"""
post_session_social.py
Posts a session build-in-public screenshot post to Instagram.

Uploads the local screenshot to imgbb to get a public URL,
then posts to Instagram feed via Meta Graph API.

Requires in scripts/.env:
  FB_PAGE_ACCESS_TOKEN
  IG_ACCOUNT_ID
  IMGBB_API_KEY  (free at imgbb.com/api)

Usage:
  python3 scripts/post_session_social.py \
    --image /path/to/screenshot.png \
    --caption "Caption text here" \
    [--dry-run]
"""

import os, base64, time, argparse, requests, tempfile
from pathlib import Path
from dotenv import load_dotenv
from PIL import Image

load_dotenv(Path(__file__).parent / ".env")

PAGE_TOKEN = os.environ["DADLETE_PAGE_TOKEN"]
IG_ID      = os.environ["DADLETE_IG_ACCOUNT_ID"]
IMGBB_KEY  = os.environ.get("IMGBB_API_KEY", "")
GRAPH      = "https://graph.facebook.com/v19.0"

HOOKS = [
    # 1. Curiosity gap
    "Most email sequences have a gap nobody checks for. Ours did.",
    # 2. Mid-action story
    "I built this system. Still found a problem in it today.",
    # 3. Contrarian
    "More emails won't fix a system that stops asking at the wrong moment.",
]

CTAS = [
    # 1. Follow — growth
    "Follow if you're building a business system by system.",
    # 2. Traffic — bio link
    "Full breakdown at aihero.au — link in bio.",
    # 3. Follow — variant
    "Follow along — building this in public one system at a time.",
]

HOOK_INDEX_FILE = Path(__file__).parent / ".hook_index"
CTA_INDEX_FILE  = Path(__file__).parent / ".cta_index"


def get_next(items, index_file):
    """Read current index, return item, advance index."""
    idx = int(index_file.read_text().strip()) if index_file.exists() else 0
    item = items[idx % len(items)]
    index_file.write_text(str((idx + 1) % len(items)))
    return item, idx


def apply_hook(caption):
    """Replace the first paragraph with the rotated hook; append rotated CTA."""
    hook, h_idx = get_next(HOOKS, HOOK_INDEX_FILE)
    cta,  c_idx = get_next(CTAS,  CTA_INDEX_FILE)
    paragraphs = caption.split("\n\n")
    paragraphs[0] = hook
    print(f"  Hook {h_idx + 1}/{len(HOOKS)}: {hook}")
    print(f"  CTA  {c_idx + 1}/{len(CTAS)}: {cta}")
    return "\n\n".join(paragraphs) + "\n\n" + cta


def prepare_image(image_path):
    """Ensure image aspect ratio fits Instagram feed (4:5 to 1.91:1). Pads with black if needed."""
    img = Image.open(image_path).convert("RGB")
    w, h = img.size
    ratio = w / h

    if ratio < 0.8:  # Too tall (narrower than 4:5) — pad sides to reach 4:5
        new_w = int(h * 0.8)
        padded = Image.new("RGB", (new_w, h), (0, 0, 0))
        padded.paste(img, ((new_w - w) // 2, 0))
        img = padded
    elif ratio > 1.91:  # Too wide — pad top/bottom to reach 1.91:1
        new_h = int(w / 1.91)
        padded = Image.new("RGB", (w, new_h), (0, 0, 0))
        padded.paste(img, (0, (new_h - h) // 2))
        img = padded

    tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
    img.save(tmp.name, "JPEG", quality=95)
    return tmp.name


def upload_image(image_path):
    """Upload local image to imgbb, return public URL."""
    if not IMGBB_KEY:
        raise RuntimeError("IMGBB_API_KEY not set in scripts/.env — get a free key at imgbb.com/api")

    image_path = prepare_image(image_path)

    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode("utf-8")

    r = requests.post(
        "https://api.imgbb.com/1/upload",
        data={"key": IMGBB_KEY, "image": image_data}
    )
    if not r.ok:
        raise RuntimeError(f"imgbb upload failed: {r.text[:200]}")

    url = r.json()["data"]["url"]
    print(f"  Image uploaded: {url}")
    return url


def post_instagram(caption, image_url, dry_run):
    if dry_run:
        print("=== INSTAGRAM FEED (screenshot) ===")
        print(caption)
        print(f"Image: {image_url}\n")
        return True

    # Create media container
    r = requests.post(
        f"{GRAPH}/{IG_ID}/media",
        data={"image_url": image_url, "caption": caption, "access_token": PAGE_TOKEN}
    )
    if not r.ok:
        print(f"  Instagram media container FAILED: {r.text[:200]}")
        return False

    container_id = r.json().get("id")
    print(f"  Container created: {container_id}")
    time.sleep(5)

    # Publish
    pub = requests.post(
        f"{GRAPH}/{IG_ID}/media_publish",
        data={"creation_id": container_id, "access_token": PAGE_TOKEN}
    )
    if pub.ok:
        print(f"  Instagram posted — ID: {pub.json().get('id')}")
        return True
    print(f"  Instagram FAILED: {pub.text[:200]}")
    return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--image",   required=True, help="Path to local screenshot file")
    parser.add_argument("--caption", required=True, help="Instagram caption text")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    image_path = Path(args.image)
    if not image_path.exists():
        print(f"ERROR: image not found at {image_path}")
        return

    print(f"Posting session to Instagram...")

    caption = apply_hook(args.caption)

    if args.dry_run:
        post_instagram(caption, f"[local: {image_path}]", dry_run=True)
        return

    print("Uploading screenshot...")
    image_url = upload_image(image_path)
    post_instagram(caption, image_url, dry_run=False)


if __name__ == "__main__":
    main()
