# Update Metrics

Pull live KPI data from the Google Sheet and refresh `context/current-data.md`.

## Run

```bash
cd /Users/peterbrown/evolved-workspace && .venv/bin/python3 scripts/update_metrics.py
```

## After running

Read the updated `context/current-data.md` and summarise the key numbers:
- Total clients and mix (SGPT vs PT)
- Cash collected and estimated annual revenue
- Blended weekly revenue per client
- Net client movement (gains vs cancels)
- Lead and booking funnel highlights
- Any metrics that stand out or warrant attention
