#!/usr/bin/env python3
"""One-time setup: creates GHL location custom values for story email notifications.

Run once, then save the returned IDs to scripts/.env as:
  GHL_CV_STORY_NAME=<id>
  GHL_CV_STORY_RESULT=<id>
  GHL_CV_STORY_QUOTE=<id>
  GHL_CV_STORY_URL_EMAIL=<id>
  GHL_CV_STORY_URL_SOCIAL=<id>
  GHL_CV_STORY_URL_MEMBER=<id>
"""
import os, requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

API_KEY     = os.environ["GHL_API_KEY"]
LOCATION_ID = os.environ["GHL_LOCATION_ID"]
BASE_URL    = "https://services.leadconnectorhq.com"
HEADERS     = {"Authorization": f"Bearer {API_KEY}", "Version": "2021-07-28",
               "Accept": "application/json", "Content-Type": "application/json"}

FIELDS = [
    {"name": "story_name",       "value": ""},
    {"name": "story_result",     "value": ""},
    {"name": "story_quote",      "value": ""},
    {"name": "story_url_email",  "value": ""},  # UTM: utm_source=email
    {"name": "story_url_social", "value": ""},  # UTM: utm_source=social
    {"name": "story_url_member", "value": ""},  # UTM: utm_source=member (for member notification)
]

for field in FIELDS:
    r = requests.post(f"{BASE_URL}/locations/{LOCATION_ID}/customValues",
                      headers=HEADERS, json=field)
    print(field["name"], r.status_code, r.json().get("customValue", {}).get("id", r.text[:80]))
