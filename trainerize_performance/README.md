# Trainerize Performance Railway Service

This read-only shadow service refreshes recent Trainerize evidence and generates
aggregate performance, inactivity, reassessment and remarkable-result signals
from a minimal private evidence store. It also publishes protected raw Strength
Assessment observations for Hub-owned Evolved Standards classification. It has
no member-system write path.

The separate Railway service `Trainerize Performance Refresh` runs at
5:15 am and 5:15 pm Brisbane time. It calls the authenticated `/refresh` endpoint, waits
for completion and exits. No scheduler runs inside this service or Codex.

Each refresh replaces the active roster, collects the prior 21 days of tracked
workouts, updates the compact longitudinal store, refreshes recent Strength
Assessment exercise and nearby bodyweight evidence, runs the report and
publishes aggregate measures plus protected raw standards evidence to the
operating-data hub. Trainerize does not normalise aliases or classify standards;
the Hub owns component rules, sufficiency, confidence and reporting. The latest
protected refresh state is available from `/refresh/latest`.

The bundle is generated with:

```bash
python scripts/build_trainerize_performance_bundle.py \
  --output-dir /private/tmp/trainerize-performance-bundle
```

The bundle is the bootstrap and recovery artifact. It remains identified
private data and may be uploaded only to the authenticated `/admin/bundle`
endpoint. The service verifies every checksum and SQLite database before
atomically replacing the prior bundle.
