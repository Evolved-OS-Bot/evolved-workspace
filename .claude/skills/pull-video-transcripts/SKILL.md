---
name: pull-video-transcripts
description: Pull clean transcripts from YouTube videos using yt-dlp and parse VTT captions to plain text. Use when the user provides YouTube URLs or video IDs and wants transcripts extracted — for testimonial videos, member stories, content repurposing, or any YouTube caption extraction task. Also handles writing structured transcript entries into reference/member-stories.md when working with The Evolved gym video assets.
---

# Pull Video Transcripts

## Requirements

- `yt-dlp` installed (`brew install yt-dlp` on macOS)
- Videos must have auto-generated or manual captions available

## Workflow

### 1. Pull VTT captions

```bash
OUTPUT_DIR=/tmp/yt-transcripts
mkdir -p $OUTPUT_DIR

yt-dlp \
  --skip-download \
  --write-auto-subs \
  --sub-lang en \
  --sub-format vtt \
  -o "$OUTPUT_DIR/%(id)s" \
  <URL_OR_ID> [<URL_OR_ID> ...]
```

For YouTube Shorts, use the full URL (e.g. `https://youtube.com/shorts/ABC123`).

Output files are named `<video_id>.en.vtt`.

### 2. Parse to clean text

Use the bundled script:

```bash
python3 .claude/skills/pull-video-transcripts/scripts/parse_vtt.py /tmp/yt-transcripts/<id>.en.vtt
```

Or parse a batch in Python:

```python
import subprocess, os
for f in sorted(os.listdir("/tmp/yt-transcripts")):
    if f.endswith(".vtt"):
        result = subprocess.run(
            ["python3", ".claude/skills/pull-video-transcripts/scripts/parse_vtt.py",
             f"/tmp/yt-transcripts/{f}"],
            capture_output=True, text=True
        )
        print(f"\n=== {f} ===\n{result.stdout.strip()}")
```

### 3. Review and identify speakers

Auto-captions often mishear names. Cross-reference with:
- Video card subtext (names and ages shown on screen)
- User-provided metadata
- Context clues in the transcript itself

Common mishearing patterns: "Rudra" → "Rue", "Peta" → "Peter".

### 4. Writing to member-stories.md (The Evolved)

When documenting testimonials in `reference/member-stories.md`, follow this structure:

```markdown
### [Name] — Card [N] — Transcript

[Age/decade], [goal]. [1-sentence context].

**Key quotes:**
- "[direct quote]"
- "[direct quote]"

**Best used for:** [goal] [decade]. [1-2 sentences on strongest use case and pull quotes].
```

Update the Video Assets table at the top of the `## Video Assets` section: change `Pending` → `See below` for each completed entry.

## Notes

- VTT auto-captions deduplicate consecutive repeated lines — the parser handles this
- If a video has no captions, yt-dlp will report an error; no `.vtt` file will appear in the output dir
- Shorts and regular YouTube videos both work with the same yt-dlp flags
- For batch pulls, pass all URLs as space-separated arguments in one yt-dlp call
