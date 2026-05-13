# Migrate GHL Page to WordPress

Migrate a GHL (GoHighLevel) funnel page to a WordPress custom page template. Extracts the full page structure from a saved GHL HTML file, builds a complete WordPress-ready HTML file in one pass, and pushes it to the live site via SSH + direct DB write.

## Variables

source_html: $ARGUMENTS (path to the saved GHL page HTML, e.g., `/tmp/ghl-page.html`)

---

## Pre-Flight Checklist

Before writing any HTML, confirm all of these are in place:

- [ ] GHL HTML file is saved locally (e.g., `curl -o /tmp/ghl-page.html <url>`)
- [ ] SSH credentials in `scripts/.env`: `SITEGROUND_SSH_HOST`, `SITEGROUND_SSH_PORT`, `SITEGROUND_SSH_USER`, `SITEGROUND_SSH_KEY_PATH`
- [ ] WordPress post ID for the target page (run `wp post list --post_type=page` via SSH if unknown)
- [ ] `template-homepage.php` uses raw content output (see WordPress Gotchas below)

---

## Phase 1: Full Extraction (Do Not Skip)

Run ALL of these extractions before writing a single line of HTML. Output each result so it can be reviewed.

### 1A — Page Structure Map

Extract every H1/H2/H3 heading in document order. This is the complete section map.

```python
import re
with open('/tmp/ghl-page.html') as f:
    content = f.read()
body = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL)
body = re.sub(r'<style[^>]*>.*?</style>', '', body, flags=re.DOTALL)
body = re.sub(r'<!--.*?-->', '', body, flags=re.DOTALL)
headings = re.findall(r'<h([1-3])[^>]*>(.*?)</h\1>', body, re.DOTALL)
for level, text in headings:
    clean = re.sub(r'<[^>]+>', '', text).strip()
    if clean and len(clean) < 300:
        print(f"H{level}: {clean}")
```

### 1B — All Images

Map every image URL to its surrounding context (alt text, section heading).

```python
imgs = re.findall(r'filesafe\.space[^\s"\'<>]+\.(?:png|jpg|jpeg|webp)', content)
unique = sorted(set(imgs))
for img in unique:
    # Find context
    idx = content.find(img)
    ctx = content[max(0,idx-500):idx+200]
    ctx_clean = re.sub(r'<[^>]+>', ' ', ctx)
    ctx_clean = re.sub(r'\s+', ' ', ctx_clean).strip()
    print(f"\nIMG: https://assets.cdn.{img}")
    print(f"CTX: {ctx_clean[:200]}")
```

### 1C — All CTAs and Links

Find every button/link URL and its label.

```python
links = re.findall(r'href="([^"]+)"[^>]*>([^<]{3,80})', content)
seen = set()
for href, label in links:
    key = href.strip()
    if key not in seen and ('http' in key or key.startswith('/')):
        seen.add(key)
        print(f"{label.strip()[:60]} → {key}")
```

### 1D — Special Embeds

Find YouTube videos, Google Maps, review widgets, iframes.

```python
# YouTube
yt = re.findall(r'(?:youtube\.com/embed/|youtu\.be/)([a-zA-Z0-9_-]{11})', content)
print("YouTube IDs:", list(set(yt)))

# Maps embed
maps = re.findall(r'google\.com/maps/embed[^"\']+', content)
print("Maps:", maps[:1])

# Review widget
rw = re.findall(r'backend\.leadconnectorhq\.com/appengine/reviews/get_widget/\S+', content)
print("Reviews:", list(set(rw)))

# Other iframes
iframes = re.findall(r'<iframe[^>]+src="([^"]+)"', content)
for src in iframes:
    print("iframe:", src[:120])
```

### 1E — Full Text Content Per Section

Extract readable text section by section for copywriting reference.

```python
body = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL)
body = re.sub(r'<style[^>]*>.*?</style>', '', body, flags=re.DOTALL)
body = re.sub(r'<!--.*?-->', '', body, flags=re.DOTALL)
body = re.sub(r'<h([1-3])[^>]*>', r'\n[H\1] ', body)
body = re.sub(r'</h[1-3]>', '\n', body)
body = re.sub(r'<p[^>]*>', '\n', body)
body = re.sub(r'<li[^>]*>', '\n- ', body)
body = re.sub(r'<[^>]+>', ' ', body)
body = body.replace('&amp;', '&').replace('&nbsp;', ' ').replace('&#x27;', "'")
body = re.sub(r'\n{3,}', '\n\n', body)
body = re.sub(r'[ \t]+', ' ', body)
for line in body.split('\n'):
    line = line.strip()
    if line and len(line) > 5:
        print(line[:300])
```

### 1F — Contact Details

Find phone numbers, address, email in footer area.

```python
footer_idx = content.rfind('footer')
chunk = content[max(0, footer_idx-2000):]
# Phone
phones = re.findall(r'\d{4}\s?\d{3}\s?\d{3}', chunk)
# Address
addresses = re.findall(r'\d+\s+\w+\s+(?:Street|St|Avenue|Ave|Road|Rd)[^<]{0,50}', chunk)
print("Phones:", phones)
print("Addresses:", addresses)
```

---

## Phase 2: WordPress Setup Verification

SSH in and confirm the template is correct before building:

```bash
SSH="ssh -i $SITEGROUND_SSH_KEY_PATH -p $SITEGROUND_SSH_PORT $SITEGROUND_SSH_USER@$SITEGROUND_SSH_HOST"
THEME_PATH="/home/.../wp-content/themes/blocksy-child"

# Check template uses raw content output (not the_content())
$SSH "grep -n 'get_post_field\|the_content' $THEME_PATH/template-homepage.php"
```

**Required:** Template must use `echo get_post_field('post_content', get_the_ID())` — NOT `the_content()`.

If it uses `the_content()`, update it:
- `the_content()` runs `wpautop` which injects `<p>` tags around HTML, breaking flex/grid layouts
- Replace with `echo get_post_field('post_content', get_the_ID())` to output raw stored HTML

---

## Phase 3: Build Complete HTML (One Pass)

Build the full page HTML **in a single file** before pushing anything. Use `/tmp/homepage-final.html`.

### HTML Rules (Lessons Learned)

**1. Never put block elements inside `<a>` tags.**
wpautop and WordPress filters break this even with the raw output fix. Use the overlay pattern instead:

```html
<!-- CORRECT — div wrapper with overlay link -->
<div style="position:relative;border-radius:8px;overflow:hidden;">
  <a href="/destination" style="position:absolute;inset:0;z-index:2;" aria-label="Card title"></a>
  <img src="..." style="width:100%;height:420px;object-fit:cover;display:block;">
  <div style="background:#e43388;padding:14px;text-align:center;">
    <strong style="color:#fff;text-transform:uppercase;">LABEL</strong>
  </div>
</div>

<!-- WRONG — block elements inside <a> -->
<a href="/destination">
  <img src="...">
  <div>Label</div>  ← breaks
</a>
```

**2. Use `display:flex` for single-row card layouts, not CSS grid with auto-fit.**
`grid-template-columns:repeat(auto-fit,minmax(Xpx,1fr))` wraps when viewport is too narrow.
Use flex with `flex:1 1 0;min-width:Xpx` + `overflow-x:auto` on the container for mobile scrolling.

```html
<!-- Single-row cards that scroll on mobile -->
<div style="display:flex;gap:8px;overflow-x:auto;-webkit-overflow-scrolling:touch;padding:0 24px;">
  <div style="flex:1 1 0;min-width:180px;...">...</div>
  <div style="flex:1 1 0;min-width:180px;...">...</div>
</div>
```

**3. Inline the GHL reviews widget resize script.**
The iframe doesn't auto-size without the postMessage listener:

```html
<iframe id="msgsndr_reviews" src="https://backend.leadconnectorhq.com/appengine/reviews/get_widget/LOCATION_ID"
  frameborder="0" scrolling="no" style="width:100%;display:block;border:none;min-height:400px;"></iframe>
<script>
window.addEventListener('message', function(e) {
  var name = e.data[0], data = e.data[1];
  if (name === 'lc.setHeight' && data && data.id === 'lc_reviews_widget') {
    var iframes = document.querySelectorAll('#msgsndr_reviews');
    for (var i = 0; i < iframes.length; i++) {
      try {
        if (e.source === iframes[i].contentWindow) {
          iframes[i].style.height = data.height + 'px';
          break;
        }
      } catch(err) {}
    }
  }
}, false);
</script>
```

**4. Section max-width strategy.**
- Most sections: `max-width:900px;margin:0 auto;padding:80px 24px`
- Full-width card rows: section has `padding:80px 0`, heading container has `max-width` + `padding:0 24px`, card row has `padding:0 24px`

**5. Use HTML entities for special characters — never raw dashes, apostrophes, or ampersands.**
- Em dash: `&#8212;`
- En dash: `&#8211;`
- Apostrophe: `&#39;` or just `'` (safe in content)
- Ampersand in text: `&amp;`

### Section Build Order

Build sections in the exact order they appear on the GHL page (use the Phase 1A heading map). Common GHL gym page structure:

1. Hero (full viewport, background image, H1 + CTA)
2. About (who we are)
3. Journey/Life Stage cards (full-width flex row)
4. How to Get Started (3-step process)
5. Old Way vs New Way comparison
6. Why [core value] Matters (4 sub-points + images)
7. Gym photos grid
8. Real Results / Testimonials (+ YouTube embed if present)
9. Timetable / Schedule image
10. Google Reviews iframe (with resize script)
11. Evidence-based / Why Us section (3 pillars)
12. Memberships (flex row)
13. FAQ (native `<details>` accordion)
14. Final CTA section
15. Footer (logo + contact + Google Maps embed)

---

## Phase 4: Push to WordPress

```bash
# 1. Upload HTML to server
scp -i $KEY -P $PORT /tmp/homepage-final.html $USER@$HOST:/path/to/public_html/homepage-final.html

# 2. Write directly to DB (bypasses wp_kses_post sanitization)
ssh -i $KEY -p $PORT $USER@$HOST "cd /path/to/public_html && wp eval '
  global \$wpdb;
  \$r = \$wpdb->update(
    \$wpdb->posts,
    [\"post_content\" => file_get_contents(\"homepage-final.html\")],
    [\"ID\" => PAGE_ID]
  );
  echo \$r === false ? \"ERROR: \" . \$wpdb->last_error : \"OK\";
'"

# 3. Flush cache (always run ALL three — wp cache flush only clears object cache,
#    wp sg purge clears SiteGround's static page cache which serves stale HTML otherwise)
ssh -i $KEY -p $PORT $USER@$HOST "cd /path/to/public_html && wp cache flush && wp transient delete --all && wp sg purge"
```

---

## Phase 5: Verify (Before Declaring Done)

Screenshot comparison checklist — work through the page top to bottom:

- [ ] Hero: background image visible, headline + subheadline + CTA button
- [ ] Journey cards: all 5 in a single horizontal row, portrait images, pink label bars
- [ ] How to Get Started: 3 steps rendered correctly
- [ ] Old Way vs Evolved Way: 2-column comparison boxes
- [ ] Why Muscle Matters: 4 points + images side by side
- [ ] Gym photos: grid layout rendering
- [ ] Results: 4 member cards + YouTube embed
- [ ] Timetable image visible
- [ ] Google Reviews: iframe expanding to full content height
- [ ] Memberships: all 4 cards in a single horizontal row
- [ ] FAQ: accordion items render, clicking expands/collapses
- [ ] Footer: logo, contact details, Google Maps embed visible
- [ ] All CTA buttons link to correct URL
- [ ] All journey cards link to correct GHL landing pages
- [ ] Mobile: card rows scroll horizontally, no broken layouts

---

## Known Gotchas Reference

| Problem | Cause | Fix |
|---|---|---|
| Block elements inside `<a>` break layout | wpautop injects `<p>` tags | Use `<div>` wrapper + overlay `<a>` |
| Inline styles stripped (display:flex, filter, inset) | `wp_kses_post()` | Use `$wpdb->update()` direct DB write |
| Card rows wrap instead of staying single row | `auto-fit` grid with `minmax` | Use `display:flex` + `flex:1 1 0` |
| Reviews iframe cuts off | Missing postMessage resize listener | Inline the `lc.setHeight` script after iframe |
| Content looks broken on page | `the_content()` running wpautop | Switch template to `get_post_field()` |
| Images not loading | GHL CDN URL format | Use `https://assets.cdn.filesafe.space/...` not leadconnectorhq URL |
| SSH key passphrase error | Key has passphrase | Generate a new key with `-N ""` (no passphrase) |
