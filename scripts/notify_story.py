#!/usr/bin/env python3
"""
notify_story.py
Triggers a GHL story email notification to contacts matching a life stage tag.

Usage:
  python3 scripts/notify_story.py \
    --stage perimenopause \
    --name "Karyn" \
    --result "Lost 12kg and eliminated chronic back pain" \
    --quote "Take that first step. The change will be more profound than you imagine." \
    --url "https://theevolvedgym.com.au/results/perimenopause-weight-loss-back-pain"

Optional:
  --member-email karyn@example.com   Send "your story is live" to the featured member
  --dry-run                          Preview contacts without sending
"""

import os, sys, time, argparse, requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

API_KEY     = os.environ["GHL_API_KEY"]
LOCATION_ID = os.environ["GHL_LOCATION_ID"]
CV_IDS      = {
    "story_name":       os.environ["GHL_CV_STORY_NAME"],
    "story_result":     os.environ["GHL_CV_STORY_RESULT"],
    "story_quote":      os.environ["GHL_CV_STORY_QUOTE"],
    "story_url_email":  os.environ["GHL_CV_STORY_URL_EMAIL"],
    "story_url_social": os.environ["GHL_CV_STORY_URL_SOCIAL"],
    "story_url_member": os.environ["GHL_CV_STORY_URL_MEMBER"],
}
# GHL PUT /customValues requires name + value
CV_NAMES    = {
    "story_name":       "story_name",
    "story_result":     "story_result",
    "story_quote":      "story_quote",
    "story_url_email":  "story_url_email",
    "story_url_social": "story_url_social",
    "story_url_member": "story_url_member",
}
MEMBER_TEMPLATE_ID = os.environ["GHL_TEMPLATE_MEMBER_NOTIFY"]

BASE_URL = "https://services.leadconnectorhq.com"
HEADERS  = {
    "Authorization": f"Bearer {API_KEY}",
    "Version":       "2021-07-28",
    "Accept":        "application/json",
    "Content-Type":  "application/json",
}

# Maps story life stage slug → (GHL demographic tags, trigger tag)
STAGE_MAP = {
    "teen":          (["teen"],                                   "notify-story-teen"),
    "20s-30s":       (["20/30s"],                                 "notify-story-2030s"),
    "pregnancy":     (["planning pregnancy", "pregnant"],         "notify-story-pregnancy"),
    "postpartum":    (["postpartum"],                             "notify-story-postpartum"),
    "perimenopause": (["perimenopause"],                          "notify-story-perimenopause"),
    "postmenopause": (["postmenopause"],                          "notify-story-postmenopause"),
}


def set_custom_value(key, value):
    cv_id = CV_IDS[key]
    name  = CV_NAMES[key]
    r = requests.put(
        f"{BASE_URL}/locations/{LOCATION_ID}/customValues/{cv_id}",
        headers=HEADERS,
        json={"name": name, "value": value},
    )
    if not r.ok:
        print(f"  WARN: failed to set custom value {key}: {r.text[:120]}")


def search_contacts_by_tag(tag, limit=100):
    """Returns list of contact dicts with the given tag and a non-empty email."""
    contacts = []
    start_after = None
    start_after_id = None
    while True:
        params = {"locationId": LOCATION_ID, "tag": tag, "limit": limit}
        if start_after:
            params["startAfter"]   = start_after
            params["startAfterId"] = start_after_id
        r = requests.get(
            f"{BASE_URL}/contacts/",
            headers=HEADERS,
            params=params,
            timeout=30,
        )
        if not r.ok:
            print(f"  WARN: search failed for tag '{tag}': {r.text[:120]}")
            break
        data  = r.json()
        batch = [c for c in data.get("contacts", []) if c.get("email")]
        contacts.extend(batch)
        meta  = data.get("meta", {})
        if not meta.get("nextPage") or not meta.get("startAfter"):
            break
        start_after    = meta["startAfter"]
        start_after_id = meta["startAfterId"]
    return contacts


def add_tag(contact_id, tag):
    r = requests.post(
        f"{BASE_URL}/contacts/{contact_id}/tags",
        headers=HEADERS,
        json={"tags": [tag]},
    )
    return r.ok


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage",        required=True, choices=list(STAGE_MAP.keys()))
    parser.add_argument("--name",         required=True)
    parser.add_argument("--result",       required=True)
    parser.add_argument("--quote",        required=True)
    parser.add_argument("--url",          required=True, help="Base story URL (no UTM)")
    parser.add_argument("--member-email", default=None,  help="Featured member's email for 'story is live' notification")
    parser.add_argument("--dry-run",      action="store_true", help="Preview contacts without sending")
    args = parser.parse_args()

    demographic_tags, trigger_tag = STAGE_MAP[args.stage]

    # Build UTM-tagged URLs
    name_slug = args.name.lower().replace(" ", "-")
    base = args.url.rstrip("/")
    url_email  = f"{base}?utm_source=email&utm_medium=crm&utm_campaign=story-{name_slug}"
    url_social = f"{base}?utm_source=social&utm_medium=organic&utm_campaign=story-{name_slug}"
    url_member = f"{base}?utm_source=member&utm_medium=email&utm_campaign=story-{name_slug}"

    # Step 1: Set location custom values
    print(f"Setting story custom values...")
    set_custom_value("story_name",       args.name)
    set_custom_value("story_result",     args.result)
    set_custom_value("story_quote",      args.quote)
    set_custom_value("story_url_email",  url_email)
    set_custom_value("story_url_social", url_social)
    set_custom_value("story_url_member", url_member)
    print(f"  Done.")

    # Step 2: Collect matching contacts (union of all demographic tags)
    all_contacts = {}
    for tag in demographic_tags:
        print(f"Searching contacts with tag: '{tag}'...")
        batch = search_contacts_by_tag(tag)
        for c in batch:
            all_contacts[c["id"]] = c
        print(f"  Found {len(batch)} contacts.")

    total = len(all_contacts)
    print(f"\nTotal unique contacts to notify: {total}")

    if args.dry_run:
        print("\nDRY RUN — no tags added. Contacts that would be notified:")
        for c in list(all_contacts.values())[:10]:
            print(f"  {c.get('firstName','')} {c.get('lastName','')} <{c.get('email','')}>")
        if total > 10:
            print(f"  ... and {total - 10} more.")
        return

    # Step 3: Add trigger tag to each contact
    print(f"\nAdding trigger tag '{trigger_tag}' to {total} contacts...")
    success = 0
    for i, contact in enumerate(all_contacts.values()):
        ok = add_tag(contact["id"], trigger_tag)
        if ok:
            success += 1
        else:
            print(f"  WARN: failed for {contact.get('email', contact['id'])}")
        # Rate limit: GHL API allows ~10 req/s
        if (i + 1) % 10 == 0:
            time.sleep(1)

    print(f"\nDone. {success}/{total} contacts tagged — GHL workflows will send emails.")
    print(f"Story: {args.name} — {args.url}")

    # Step 4: Send "your story is live" to the featured member
    if args.member_email:
        print(f"\nSending member notification to {args.member_email}...")
        r = requests.get(
            f"{BASE_URL}/contacts/search",
            headers=HEADERS,
            params={"locationId": LOCATION_ID, "query": args.member_email, "limit": 1},
        )
        contacts_found = r.json().get("contacts", []) if r.ok else []
        if contacts_found:
            contact_id = contacts_found[0]["id"]
            send_r = requests.post(
                f"{BASE_URL}/conversations/messages",
                headers=HEADERS,
                json={
                    "type":       "Email",
                    "contactId":  contact_id,
                    "templateId": MEMBER_TEMPLATE_ID,
                },
            )
            if send_r.ok:
                print(f"  Member notification sent.")
            else:
                print(f"  WARN: member send failed: {send_r.text[:120]}")
        else:
            print(f"  WARN: no GHL contact found for {args.member_email} — skipping member notification.")


if __name__ == "__main__":
    main()
