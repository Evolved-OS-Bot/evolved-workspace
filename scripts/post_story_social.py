#!/usr/bin/env python3
"""
post_story_social.py
Posts a member story to Facebook and Instagram.

Automatically determines what to post based on what's provided:
  --image-url only  → photo feed post + image story (with link sticker)
  --video-url only  → reel + video story
  --image-url AND --video-url → reel + photo feed post + image story (link sticker) + video story

Add --stories to include Story posts. Without it, only feed posts are made.

Usage:
  python3 scripts/post_story_social.py \
    --name "Karyn" \
    --result "Lost 12kg and eliminated chronic back pain" \
    --quote "Take that first step. The change will be more profound than you imagine." \
    --url "https://theevolvedgym.com.au/results/perimenopause-weight-loss-back-pain" \
    --image-url "https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/karyn-photo.png" \
    --video-url "https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/karyn-reel.mp4" \
    --stories \
    --dry-run
"""

import os, time, argparse, requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

PAGE_TOKEN = os.environ["FB_PAGE_ACCESS_TOKEN"]
PAGE_ID    = os.environ["FB_PAGE_ID"]
IG_ID      = os.environ["IG_ACCOUNT_ID"]
GRAPH      = "https://graph.facebook.com/v19.0"

HASHTAGS = "#TheEvolvedGym #WomensStrengthTraining #Brisbane #RealResults #StrengthTraining"


def utm(url, name):
    slug = name.lower().replace(" ", "-")
    return f"{url}?utm_source=social&utm_medium=organic&utm_campaign=story-{slug}"


def ig_sized_url(image_url):
    """Use WordPress 300x300 thumbnail — Instagram API requires fast-downloading images."""
    if not image_url:
        return None
    if "." in image_url.split("/")[-1]:
        base, ext = image_url.rsplit(".", 1)
        return f"{base}-300x300.{ext}"
    return image_url


def ig_publish(container_id, label, poll=False):
    """Publish an Instagram media container. Optionally poll for video processing."""
    if poll:
        print(f"  Waiting for {label} to process...", end="", flush=True)
        for _ in range(12):  # up to 60s
            time.sleep(5)
            status = requests.get(
                f"{GRAPH}/{container_id}",
                params={"fields": "status_code", "access_token": PAGE_TOKEN},
            ).json().get("status_code")
            print(".", end="", flush=True)
            if status == "FINISHED":
                break
            if status == "ERROR":
                print(f"\n  {label} processing ERROR")
                return False
        print()
    else:
        time.sleep(5)

    pub = requests.post(
        f"{GRAPH}/{IG_ID}/media_publish",
        data={"creation_id": container_id, "access_token": PAGE_TOKEN},
    )
    if pub.ok:
        print(f"  {label} published — ID: {pub.json().get('id')}")
        return True
    print(f"  {label} publish FAILED: {pub.text[:200]}")
    return False


# ── FACEBOOK FEED ─────────────────────────────────────────────────────────────

def post_facebook_feed(name, result, quote, url, dry_run):
    link    = utm(url, name)
    message = (
        f'"{quote}"\n\n'
        f"{name} — {result}\n\n"
        f"Read her full story: {link}\n\n"
        f"Spots at The Evolved are by waitlist only. If this sounds like your story, join us.\n\n"
        f"{HASHTAGS}"
    )
    if dry_run:
        print("=== FACEBOOK FEED (photo) ===")
        print(message + "\n")
        return True
    r = requests.post(f"{GRAPH}/{PAGE_ID}/feed",
                      data={"message": message, "link": link, "access_token": PAGE_TOKEN})
    if r.ok:
        print(f"Facebook feed posted — ID: {r.json().get('id')}")
        return True
    print(f"Facebook feed FAILED: {r.text[:200]}")
    return False


def post_facebook_reel(name, result, quote, video_url, url, dry_run):
    link        = utm(url, name)
    description = (
        f'"{quote}"\n\n'
        f"{name} — {result}\n\n"
        f"Read her full story: {link}\n\n"
        f"Spots at The Evolved are by waitlist only. If this sounds like your story, join us.\n\n"
        f"{HASHTAGS}"
    )
    if dry_run:
        print("=== FACEBOOK REEL ===")
        print(description)
        print(f"Video: {video_url}\n")
        return True
    r = requests.post(
        f"{GRAPH}/{PAGE_ID}/videos",
        data={
            "file_url":        video_url,
            "description":     description,
            "content_tags":    "Reels",
            "access_token":    PAGE_TOKEN,
        },
    )
    if r.ok:
        print(f"Facebook reel posted — ID: {r.json().get('id')}")
        return True
    print(f"Facebook reel FAILED: {r.text[:200]}")
    return False


# ── INSTAGRAM FEED ────────────────────────────────────────────────────────────

def post_instagram_feed(name, result, quote, image_url, dry_run):
    sized   = ig_sized_url(image_url)
    caption = (
        f'"{quote}"\n\n'
        f"{name} — {result}\n\nLink in bio — read her full story.\n\n"
        f"{HASHTAGS}"
    )
    if dry_run:
        print("=== INSTAGRAM FEED (photo) ===")
        print(caption)
        print(f"Image: {sized}\n")
        return True
    if not sized:
        print("Instagram feed SKIPPED — no image URL")
        return False
    r = requests.post(f"{GRAPH}/{IG_ID}/media",
                      data={"image_url": sized, "caption": caption, "access_token": PAGE_TOKEN})
    if not r.ok:
        print(f"Instagram feed FAILED: {r.text[:200]}")
        return False
    return ig_publish(r.json().get("id"), "Instagram feed")


def post_instagram_reel(name, result, quote, video_url, dry_run):
    caption = (
        f'"{quote}"\n\n'
        f"{name} — {result}\n\n"
        f"Link in bio — read her full story.\n\n"
        f"{HASHTAGS}"
    )
    if dry_run:
        print("=== INSTAGRAM REEL ===")
        print(caption)
        print(f"Video: {video_url}\n")
        return True
    if not video_url:
        print("Instagram reel SKIPPED — no video URL")
        return False
    r = requests.post(
        f"{GRAPH}/{IG_ID}/media",
        data={
            "media_type":   "REELS",
            "video_url":    video_url,
            "caption":      caption,
            "access_token": PAGE_TOKEN,
        },
    )
    if not r.ok:
        print(f"Instagram reel container FAILED: {r.text[:200]}")
        return False
    return ig_publish(r.json().get("id"), "Instagram reel", poll=True)


# ── STORIES ───────────────────────────────────────────────────────────────────

def post_instagram_image_story(name, image_url, url, dry_run):
    """Image story with clickable link sticker — URL hidden, shows as 'Read her story →'."""
    sized    = ig_sized_url(image_url)
    link_url = utm(url, name)
    if dry_run:
        print("=== INSTAGRAM STORY (image + link sticker) ===")
        print(f"Image: {sized}")
        print(f"Link sticker: Read her story → {link_url}\n")
        return True
    if not sized:
        print("Instagram image story SKIPPED — no image URL")
        return False
    r = requests.post(
        f"{GRAPH}/{IG_ID}/media",
        data={
            "image_url":        sized,
            "media_type":       "STORIES",
            "link_sticker_url": link_url,
            "access_token":     PAGE_TOKEN,
        },
    )
    if not r.ok:
        print(f"Instagram image story FAILED: {r.text[:200]}")
        return False
    return ig_publish(r.json().get("id"), "Instagram image story")


def post_instagram_video_story(name, video_url, dry_run):
    if dry_run:
        print("=== INSTAGRAM STORY (video) ===")
        print(f"Video: {video_url}\n")
        return True
    if not video_url:
        print("Instagram video story SKIPPED — no video URL")
        return False
    r = requests.post(
        f"{GRAPH}/{IG_ID}/media",
        data={
            "video_url":    video_url,
            "media_type":   "STORIES",
            "access_token": PAGE_TOKEN,
        },
    )
    if not r.ok:
        print(f"Instagram video story FAILED: {r.text[:200]}")
        return False
    return ig_publish(r.json().get("id"), "Instagram video story", poll=True)


def post_facebook_story(name, image_url, video_url, dry_run):
    """Facebook Story — image preferred (link stickers not supported via API either way)."""
    asset = ig_sized_url(image_url) or video_url
    kind  = "image" if image_url else "video"
    if dry_run:
        print(f"=== FACEBOOK STORY ({kind}) ===")
        print(f"Asset: {asset}")
        print("Note: Facebook Stories via API do not support interactive link stickers.\n")
        return True
    if not asset:
        print("Facebook story SKIPPED — no image or video URL")
        return False

    if image_url:
        upload = requests.post(f"{GRAPH}/{PAGE_ID}/photos",
                               data={"url": asset, "published": "false", "access_token": PAGE_TOKEN})
        if not upload.ok:
            print(f"Facebook story upload FAILED: {upload.text[:200]}")
            return False
        r = requests.post(f"{GRAPH}/{PAGE_ID}/photo_stories",
                          data={"photo_id": upload.json().get("id"), "access_token": PAGE_TOKEN})
    else:
        r = requests.post(f"{GRAPH}/{PAGE_ID}/video_stories",
                          data={"file_url": asset, "video_state": "PUBLISHED", "access_token": PAGE_TOKEN})

    if r.ok:
        print(f"Facebook story posted — ID: {r.json().get('id')}")
        return True
    print(f"Facebook story FAILED: {r.text[:200]}")
    return False


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--name",      required=True)
    parser.add_argument("--result",    required=True)
    parser.add_argument("--quote",     required=True)
    parser.add_argument("--url",       required=True)
    parser.add_argument("--image-url", default=None, help="Member photo (PNG/JPG on SiteGround)")
    parser.add_argument("--video-url", default=None, help="MP4 video URL for Reels")
    parser.add_argument("--stories",   action="store_true", help="Also post Stories")
    parser.add_argument("--dry-run",   action="store_true")
    args = parser.parse_args()

    has_image = bool(args.image_url)
    has_video = bool(args.video_url)

    if not has_image and not has_video:
        print("ERROR: provide at least --image-url or --video-url")
        return

    print(f"Posting story: {args.name}")
    mode = "image + video" if (has_image and has_video) else ("video" if has_video else "image")
    print(f"Mode: {mode}" + (" + stories" if args.stories else "") + "\n")

    results = {}

    # ── Feed posts ──
    if has_video:
        results["FB reel"]   = post_facebook_reel(args.name, args.result, args.quote, args.video_url, args.url, args.dry_run)
        results["IG reel"]   = post_instagram_reel(args.name, args.result, args.quote, args.video_url, args.dry_run)
    if has_image:
        results["FB feed"]   = post_facebook_feed(args.name, args.result, args.quote, args.url, args.dry_run)
        results["IG feed"]   = post_instagram_feed(args.name, args.result, args.quote, args.image_url, args.dry_run)

    # ── Stories ──
    if args.stories:
        # Image story gets link sticker — preferred if available
        if has_image:
            results["IG story"] = post_instagram_image_story(args.name, args.image_url, args.url, args.dry_run)
        elif has_video:
            results["IG story"] = post_instagram_video_story(args.name, args.video_url, args.dry_run)

        if has_video and has_image:
            results["IG video story"] = post_instagram_video_story(args.name, args.video_url, args.dry_run)

        results["FB story"] = post_facebook_story(args.name, args.image_url, args.video_url, args.dry_run)

    print("\n── Results ──")
    for label, ok in results.items():
        print(f"  {label}: {'OK' if ok else 'FAILED'}")


if __name__ == "__main__":
    main()
