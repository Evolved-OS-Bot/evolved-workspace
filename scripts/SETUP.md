# Metrics Script Setup

One-time setup. Takes approximately 10 minutes.

---

## 1. Install Python dependencies

From the workspace root:

```bash
pip install -r scripts/requirements.txt
```

---

## 2. Create a Google Cloud service account

1. Go to https://console.cloud.google.com/
2. Create a new project — name it "Evolved Metrics"
3. Enable the Google Sheets API: APIs & Services → Enable APIs → search "Google Sheets API" → Enable
4. Create a service account: APIs & Services → Credentials → Create Credentials → Service Account
   - Name: `evolved-metrics`
   - Skip optional fields → Done
5. Click the service account → Keys tab → Add Key → Create new key → JSON → download
6. Rename the downloaded file to `google_credentials.json`
7. Move it to `scripts/google_credentials.json`
8. Copy the service account email address (looks like `evolved-metrics@your-project.iam.gserviceaccount.com`)

---

## 3. Share the Google Sheet with the service account

1. Open the Brown & Casserly KPI spreadsheet
2. Click Share
3. Paste the service account email address
4. Set permission to **Editor** (needed to write formulas)
5. Click Send

---

## 4. Update scripts/.env

Copy `scripts/.env.example` to `scripts/.env` and fill in the values:

```bash
cp scripts/.env.example scripts/.env
```

Then edit `scripts/.env` — the values are already set correctly if you haven't changed the spreadsheet ID.

---

## 5. Test the connection

```bash
python scripts/test_connection.py
```

If it prints the sheet title, you're connected.

---

## 6. Insert KPI formulas (one-time)

```bash
python scripts/insert_formulas.py
```

This writes all COUNTIFS formulas into the KPI tab. Safe to re-run — it only overwrites the formula cells.

---

## 7. Set up the update-metrics alias

Add to your `~/.zshrc`:

```bash
alias update-metrics='cd ~/Downloads/claude-workspace-evolved && python scripts/update_metrics.py'
```

Then:

```bash
source ~/.zshrc
```

---

## Troubleshooting

- **"File not found: google_credentials.json"** — check the file is at `scripts/google_credentials.json`
- **"403 Forbidden"** — sheet not shared with service account email; repeat Step 3
- **"400 Bad Request on formula insert"** — check the KPI tab name matches exactly: `KPI's The Evolved`
- **"Current week column not found"** — sheet date format may differ; check row 1 of KPI tab
