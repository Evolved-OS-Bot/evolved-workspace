# Website V2 Source Mirror

This directory is the version-controlled, clean source mirror for the Evolved
Website V2 already live at `https://blog.theevolvedgym.com.au/`.

## Contents

- `source/homepage-post/post-165.html`: database-owned homepage content
  exported from WordPress post ID 165.
- `source/blocksy-child/`: complete deployed Blocksy child theme captured on
  3 August 2026.
- `SOURCE_SHA256SUMS.txt`: byte-level hashes for the governed mirror.

The files were copied from the checksum-verified Phase 1 production snapshot:

`data/private/website-migration-baselines/2026-08-03-phase1/wordpress/`

This directory intentionally excludes WordPress core, plugins, uploads,
database content, server configuration and credentials. Those belong in the
protected recovery baseline, not Git.

## Operating Rule

Read `outputs/systems/website-v2-release-manifest.md` before using or changing
these files.

Do not deploy a file directly from production and leave this mirror stale.
After an authorised live change, read back production, update the matching
source file, refresh the hashes, append the release register and run:

```bash
python3 scripts/check_website_v2_drift.py
python3 scripts/check_website_v2_drift.py --live
```

The first command is local and read-only. The second adds read-only verification
of the public homepage.
