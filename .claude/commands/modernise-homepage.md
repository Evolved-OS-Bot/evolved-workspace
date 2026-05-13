# Modernise Homepage — Animation, Video & Interactivity

Add cinematic animation, a video hero, interactive charts, and scroll-reveal to an existing WordPress homepage. Works on top of an already-deployed static HTML page (e.g. one built by `/migrate-ghl-page`). Pushes all changes via SSH + direct DB write.

## Variables

page_id: $ARGUMENTS (WordPress post ID of the homepage, e.g. `165`)

---

## Pre-Flight Checklist

- [ ] SSH credentials in `scripts/.env`: `SITEGROUND_SSH_HOST`, `SITEGROUND_SSH_PORT`, `SITEGROUND_SSH_USER`, `SITEGROUND_SSH_KEY_PATH`
- [ ] GSAP 3.12+, ScrollTrigger, and Chart.js enqueued in `functions.php` (front page only)
- [ ] `homepage.js` enqueued from the child theme's `js/` folder
- [ ] Template uses `echo get_post_field('post_content', get_the_ID())` — not `the_content()` (see `/migrate-ghl-page` gotchas)
- [ ] Current homepage HTML saved locally (pull from server if needed: `scp ... homepage-current.html`)
- [ ] Video file on Mac (if adding video hero)

---

## Part A: Video Hero

### A1 — Prepare the Video File

iPhone footage is always Dolby Vision / BT.2020 HLG. Standard H.264 conversion keeps the HDR metadata, which Chrome renders as black on SDR displays. **Always use the colorspace conversion filter.**

```bash
ffmpeg -y -i '/path/to/input.MOV' \
  -c:v libx264 \
  -profile:v high \
  -pix_fmt yuv420p \
  -crf 26 \
  -preset slow \
  -vf "scale=1920:-2,colorspace=all=bt709:iall=bt2020" \
  -an \
  -movflags +faststart \
  /tmp/hero-video.mp4
```

Verify the output shows `yuv420p(tv, bt709)` — NOT `bt2020` or `arib-std-b67`:

```bash
ffmpeg -i /tmp/hero-video.mp4 2>&1 | grep "Video:"
```

Target: ~5MB for a 20-30 second clip. If over 8MB, increase `-crf` to 28.

**If stitching multiple clips:** Edit on iPhone in CapCut first (no music, no text, no filters, export 1080p), then AirDrop to Mac and run the command above. Landscape (16:9) clips are preferred over portrait (9:16) for a full-width hero.

**If the video plays on a bare test page but not on the homepage:** The issue is CSS, not the file. Use the test page pattern to isolate:

```html
<!DOCTYPE html><html><head><style>body{margin:0;background:#000;}video{width:100%;display:block;}</style></head>
<body><video autoplay muted loop playsinline controls><source src="VIDEO_URL" type="video/mp4"></video></body></html>
```

### A2 — Upload to WordPress

```bash
scp -i $KEY -P $PORT /tmp/hero-video.mp4 \
  $USER@$HOST:/path/to/public_html/wp-content/uploads/YYYY/MM/hero-video.mp4
```

### A3 — Hero HTML Structure

Use this exact structure. **Never nest the video inside a CSS-class wrapper.** The video, overlay, and text must be direct children of the section with explicit z-index — no class dependencies.

```html
<section class="hero" style="position:relative;min-height:100vh;display:flex;align-items:center;justify-content:center;text-align:center;background:#0a0a0a;overflow:hidden;">

<!-- z-index:0 — video fills section -->
<video autoplay muted loop playsinline preload="auto"
  poster="FALLBACK_IMAGE_URL"
  style="position:absolute;top:0;left:0;width:100%;height:100%;object-fit:cover;object-position:center;z-index:0;">
  <source src="VIDEO_URL" type="video/mp4">
</video>

<!-- z-index:1 — dark overlay, adjust opacity for readability -->
<div style="position:absolute;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.6);z-index:1;"></div>

<!-- z-index:2 — text content -->
<div style="position:relative;z-index:2;max-width:740px;padding:32px 24px;">
  <p class="hero-eyebrow">Tagline · Location</p>
  <h1 class="hero-headline" style="font-family:'PT Serif Caption',serif;font-size:clamp(2rem,5vw,3.5rem);color:#f5f0eb;line-height:1.15;margin-bottom:16px;">Headline</h1>
  <p class="hero-sub" style="font-size:1.1rem;color:#ccc;margin-bottom:40px;line-height:1.7;max-width:600px;margin-left:auto;margin-right:auto;">Subheadline</p>
  <a class="hero-cta" href="/cta-url" style="display:inline-block;background:#e43388;color:#fff;padding:18px 40px;border-radius:4px;font-family:'Lato',sans-serif;font-size:1rem;font-weight:700;text-decoration:none;">CTA Button</a>
  <p class="hero-disclaimer" style="font-size:0.85rem;color:#666;margin-top:16px;">Disclaimer text</p>
</div>
</section>
```

**Known gotchas:**
| Problem | Cause | Fix |
|---|---|---|
| Video plays on test page but black on homepage | Double `filter:brightness()` — one on video, one on a CSS class | Remove filter from CSS class; use only the overlay div |
| Video black in Chrome/Safari | BT.2020 HLG color metadata still embedded | Use `colorspace=all=bt709:iall=bt2020` in ffmpeg |
| Poster shows then goes black | Video loads and attempts HDR rendering | Same as above — color space issue |
| Video shows but text invisible | z-index conflict | Use explicit `z-index:0/1/2` inline, no class dependencies |

---

## Part B: GSAP Animation Layer

### B1 — CSS to append to `style.css`

```css
/* ── Homepage Animation Layer ─────────────────────────────────── */
[data-reveal] { opacity: 0; }
.hero { position: relative; overflow: hidden; min-height: 100vh; }
.hero-eyebrow { font-size:0.75rem;text-transform:uppercase;letter-spacing:0.18em;color:#e43388;margin-bottom:12px;opacity:0;transform:translateY(20px); }
.hero-headline, .hero-sub, .hero-cta, .hero-disclaimer { opacity:0;transform:translateY(30px); }
.journey-card, .membership-card { transition:transform 0.28s cubic-bezier(0.25,0.8,0.25,1),box-shadow 0.28s cubic-bezier(0.25,0.8,0.25,1);cursor:pointer; }
.journey-card:hover { transform:translateY(-6px);box-shadow:0 16px 40px rgba(228,51,136,0.25); }
.membership-card:hover { transform:translateY(-6px);box-shadow:0 16px 40px rgba(228,51,136,0.2); }
.journey-card .card-label { transition:background 0.25s; }
.journey-card:hover .card-label { background:#c4206e; }
.stat-number { font-family:'PT Serif Caption',serif;font-size:clamp(2.4rem,5vw,4rem);color:#e43388;line-height:1;display:block;margin-bottom:8px; }
.stat-label { color:#aaa;font-size:0.85rem;text-transform:uppercase;letter-spacing:0.08em; }
.chart-canvas-wrap { position:relative;background:#0d0d0d;border-radius:8px;border:1px solid #222;padding:24px; }
.chart-annotation { color:#aaa;font-size:0.9rem;line-height:1.75;margin-top:20px;min-height:3em;border-left:2px solid #e43388;padding-left:16px; }
.age-btn { background:#1a1a1a;border:1px solid #333;color:#aaa;padding:8px 16px;border-radius:4px;font-size:0.8rem;cursor:pointer;transition:all 0.2s; }
.age-btn.active { background:#e43388;border-color:#e43388;color:#fff; }
.carousel-viewport { overflow:hidden;position:relative;cursor:grab;user-select:none; }
.carousel-viewport:active { cursor:grabbing; }
.carousel-track { display:flex;gap:24px;will-change:transform; }
.carousel-card { flex:0 0 calc(50% - 12px);min-width:280px;background:#0d0d0d;border:1px solid #222;border-radius:8px;padding:28px; }
.carousel-nav { display:flex;gap:12px;justify-content:center;margin-top:20px; }
.carousel-prev, .carousel-next { background:#1a1a1a;border:1px solid #333;color:#f5f0eb;width:44px;height:44px;border-radius:50%;cursor:pointer;font-size:1.1rem;transition:all 0.2s;display:flex;align-items:center;justify-content:center; }
.carousel-prev:hover, .carousel-next:hover { background:#e43388;border-color:#e43388; }
@media(max-width:640px) { .carousel-card { flex:0 0 100%;min-width:260px; } }
```

Append via SSH (do not overwrite):
```bash
cat /tmp/homepage-animation.css >> $THEME/style.css
```

### B2 — `homepage.js` structure

The JS file has five sections. Keep all five — they work together:

**1A — Global scroll-reveal** (`data-reveal` attribute system)
- Add `data-reveal="fade-up|fade-left|fade-right|scale"` to any element
- Add `data-reveal-stagger` to a parent + `data-reveal-child` to each child for staggered groups
- Add `data-reveal-delay="0.1"` for per-element delay offset

**1B — Hero parallax + staggered text reveal**
- Targets `.hero-eyebrow`, `.hero-headline`, `.hero-sub`, `.hero-cta`, `.hero-disclaimer` in sequence
- CTA gets a pink box-shadow pulse loop after the timeline completes
- Skip parallax when using video hero (video motion provides dynamism; scrubbing video looks odd)

**1C — Animated number counters**
- Markup: `<span class="stat-number" data-count="500" data-count-suffix="+">0</span>`
- Triggers once on scroll via ScrollTrigger

**1D — Chart scroll-trigger reveal**
- Wraps chart canvas elements in a fade-up reveal on scroll
- Charts themselves animate on first render (Chart.js `animation.duration`)

**1E — Draggable testimonial carousel**
- Targets `.carousel-viewport` / `.carousel-track` / `.carousel-card`
- Touch + mouse drag support built in
- Prev/Next buttons: `.carousel-prev` / `.carousel-next`

**Version bump:** Always increment the version string in `functions.php` after updating `homepage.js` to bust browser cache:
```php
// Change "1.0" → "2.0" → "3.0" etc.
wp_enqueue_script("evolved-homepage", ... , "2.0", true);
```

### B3 — HTML class hooks required

Every animation targets a class or `data-` attribute. Before deploying JS, verify these exist in the HTML:

| Class / Attribute | Where | What it does |
|---|---|---|
| `class="hero"` | Hero `<section>` | Parallax container |
| `class="hero-eyebrow/headline/sub/cta/disclaimer"` | Hero text elements | Staggered reveal |
| `data-reveal="fade-up"` | Section headings, paragraphs | Scroll-reveal |
| `data-reveal-stagger` + `data-reveal-child` | Grid/list parents + children | Staggered group reveal |
| `class="journey-card"` + `class="card-label"` | Journey card divs | Hover lift + label colour |
| `class="membership-card"` | Membership card divs | Hover lift |
| `data-count="500" data-count-suffix="+"` | Stat number spans | Animated counter |
| `class="stat-number"` + `class="stat-label"` | Stat elements | Counter styling |
| `id="sarcopeniaChart"` + `id="frequencyChart"` | `<canvas>` elements | Chart render targets |
| `class="carousel-viewport/track/card"` | Testimonial carousel | Draggable carousel |
| `class="carousel-prev/next"` | Nav buttons | Carousel controls |

**The most common failure:** JS loads and targets classes that don't exist in the HTML → animations silently do nothing. Always verify class hooks are present before debugging JS.

---

## Part C: Interactive Charts

### C1 — Sarcopenia Chart (Why Muscle Matters section)

The sarcopenia chart uses a **range slider** (not buttons) to select age decade. The slider fills pink left-of-thumb via a JS-updated `linear-gradient` on the `background` property.

```html
<div class="chart-canvas-wrap" style="margin-bottom:32px;">
  <p style="color:#f5f0eb;font-size:0.85rem;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:16px;">Muscle Mass Over Time</p>
  <canvas id="sarcopeniaChart" height="220"></canvas>
  <div style="margin-top:20px;">
    <p style="color:#aaa;font-size:0.8rem;text-align:center;margin-bottom:14px;letter-spacing:0.06em;">&#8592;&nbsp;&nbsp;Drag to find your decade&nbsp;&nbsp;&#8594;</p>
    <input type="range" id="ageSlider" min="0" max="5" step="1" value="0"
      style="width:100%;cursor:pointer;-webkit-appearance:none;appearance:none;height:4px;border-radius:2px;outline:none;background:linear-gradient(to right,#e43388 0%,#333 0%);">
    <div style="display:flex;justify-content:space-between;margin-top:10px;padding:0 2px;">
      <span style="color:#555;font-size:0.72rem;">20s</span>
      <span style="color:#555;font-size:0.72rem;">30s</span>
      <span style="color:#555;font-size:0.72rem;">40s</span>
      <span style="color:#555;font-size:0.72rem;">50s</span>
      <span style="color:#555;font-size:0.72rem;">60s</span>
      <span style="color:#555;font-size:0.72rem;">70s+</span>
    </div>
  </div>
  <p id="sarcopeniaAnnotation" class="chart-annotation"></p>
  <div style="text-align:center;margin-top:16px;">
    <a id="sarcopeniaCta" href="https://go.theevolvedgym.com.au/strength-assessment"
      style="display:inline-block;background:#e43388;color:#fff;padding:12px 28px;border-radius:4px;font-size:0.85rem;font-weight:700;text-decoration:none;">See Where You Fall on This Curve</a>
  </div>
</div>
```

Add slider thumb CSS to the inline `<style>` block (not stylesheet — cache):
```css
#ageSlider::-webkit-slider-thumb { -webkit-appearance:none;width:24px;height:24px;border-radius:50%;background:#e43388;cursor:pointer;border:2px solid #111;box-shadow:0 0 0 3px rgba(228,51,136,0.25); }
#ageSlider::-moz-range-thumb { width:24px;height:24px;border-radius:50%;background:#e43388;cursor:pointer;border:2px solid #111;box-shadow:0 0 0 3px rgba(228,51,136,0.25); }
```

JS slider handler (inside DOMContentLoaded):
```javascript
const brackets = ["20s","30s","40s","50s","60s","70s+"];
const slider   = document.getElementById("ageSlider");
selectAgeBracket(sarcoChart, "20s");
updateMusclePoints("20s");
updateDecadeCards("20s");
if (slider) {
    slider.addEventListener("input", function() {
        const val     = parseInt(this.value);
        const bracket = brackets[val];
        const pct     = (val / 5) * 100;
        this.style.background = `linear-gradient(to right, #e43388 ${pct}%, #333 ${pct}%)`;
        selectAgeBracket(sarcoChart, bracket);
        updateMusclePoints(bracket);
        updateDecadeCards(bracket);
    });
}
```

### C2 — Frequency Chart (We Don't Guess We Guide section)

The frequency chart lives **outside** the Why Muscle Matters section — place it at the bottom of the "We Don't Guess We Guide" evidence section, above the CTA. It uses **phase story buttons** instead of hover interaction.

```html
<div class="chart-canvas-wrap" style="margin-top:56px;">
  <p style="color:#f5f0eb;font-size:0.85rem;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:6px;">Your 12-Month Results Curve</p>
  <p style="color:#aaa;font-size:0.85rem;line-height:1.6;margin-bottom:20px;">Training frequency determines how fast your results compound. Click a phase to see what's happening inside your body.</p>
  <canvas id="frequencyChart" height="220"></canvas>
  <p style="color:#555;font-size:0.75rem;line-height:1.6;margin-top:10px;text-align:center;">Index combines strength, body composition, and fitness gains &#8212; normalized to 100 at peak.</p>
  <div style="display:flex;gap:10px;justify-content:center;margin-top:24px;flex-wrap:wrap;">
    <button class="phase-btn" data-phase="learn" style="background:#e43388;border:1px solid #e43388;color:#fff;padding:8px 18px;border-radius:4px;font-family:'Lato',sans-serif;font-size:0.8rem;font-weight:700;cursor:pointer;letter-spacing:0.04em;transition:all 0.2s;">Weeks 1&#8211;12</button>
    <button class="phase-btn" data-phase="consistent" style="background:#1a1a1a;border:1px solid #333;color:#aaa;padding:8px 18px;border-radius:4px;font-family:'Lato',sans-serif;font-size:0.8rem;cursor:pointer;letter-spacing:0.04em;transition:all 0.2s;">Weeks 13&#8211;26</button>
    <button class="phase-btn" data-phase="compound" style="background:#1a1a1a;border:1px solid #333;color:#aaa;padding:8px 18px;border-radius:4px;font-family:'Lato',sans-serif;font-size:0.8rem;cursor:pointer;letter-spacing:0.04em;transition:all 0.2s;">Month 6&#8211;12</button>
  </div>
  <p id="frequencyAnnotation" class="chart-annotation" style="margin-top:20px;min-height:4.5em;"></p>
</div>
```

**Do NOT add `data-reveal` to the frequency chart div** — `initChartReveal()` in the JS already handles both charts. Adding `data-reveal` creates two competing animations and the chart stays dark.

Phase annotations JS (add before `initFrequencyChart`):
```javascript
const phaseAnnotations = {
    learn:      "The first 12 weeks are about your brain, not your biceps. Your nervous system is learning new movement patterns — this is where rapid strength gains come from.",
    consistent: "Weeks 13 to 26 are where your first 12 weeks pay off. Consistency starts to compound. Visible body composition changes begin here.",
    compound:   "At the 6-month mark, every cell in your body is being replaced by a stronger version. Results compound non-linearly from here. This is a 12-month story."
};
```

Phase button handler (inside DOMContentLoaded, after `initFrequencyChart()`):
```javascript
const freqChart = initFrequencyChart();
if (freqChart) {
    const phaseBtns = document.querySelectorAll(".phase-btn");
    const annEl     = document.getElementById("frequencyAnnotation");
    function setPhase(phase) {
        phaseBtns.forEach(b => {
            const active = b.dataset.phase === phase;
            b.style.background  = active ? "#e43388" : "#1a1a1a";
            b.style.borderColor = active ? "#e43388" : "#333";
            b.style.color       = active ? "#fff"    : "#aaa";
            b.style.fontWeight  = active ? "700"     : "400";
        });
        if (annEl) {
            annEl.textContent = phaseAnnotations[phase];
            gsap.fromTo(annEl, { opacity: 0, y: 8 }, { opacity: 1, y: 0, duration: 0.4, ease: "power2.out" });
        }
    }
    phaseBtns.forEach(btn => btn.addEventListener("click", () => setPhase(btn.dataset.phase)));
    setPhase("learn");
}
```

**Frequency chart data:** Min effective dose line = 20 (represents 2x/week). Y-axis label: `"Cumulative Progress (%)"`. Tooltip callback should filter out the min dose line: `ctx.dataset.label.startsWith("Min.") ? null : ...`

---

## Part G: Decade-Dynamic Content System (Why Muscle Matters)

The Why Muscle Matters section has three layers of content that all update in sync when the age slider moves:

1. **Four bullet points** — tailored copy per decade
2. **Hero transformation** — one before/after image (or quote block) per decade
3. **Secondary transformation cards** — up to 3 additional before/afters per decade

### G1 — HTML structure

Add IDs to the four bullet point `<h3>` and `<p>` elements:
```html
<h3 id="mp-1-h" ...>Heading</h3>
<p  id="mp-1-p" ...>Body copy</p>
<!-- repeat for mp-2, mp-3, mp-4 -->
```

Hero transformation slot (above bullet points, inside `.muscle-text`):
```html
<div id="decade-transform" style="display:none;margin-bottom:32px;">
  <img id="decade-transform-img" src="" alt="" style="width:100%;border-radius:6px;display:block;object-fit:cover;">
  <p id="decade-transform-caption" style="color:#555;font-size:0.75rem;margin-top:10px;text-align:center;letter-spacing:0.04em;"></p>
</div>
<div id="decade-quote" style="display:none;margin-bottom:32px;border-left:2px solid #e43388;padding:20px 24px;background:#0d0d0d;border-radius:0 6px 6px 0;">
  <p id="decade-quote-text" style="color:#f5f0eb;font-size:0.9rem;line-height:1.85;font-style:italic;margin-bottom:14px;"></p>
  <p id="decade-quote-name" style="color:#e43388;font-size:0.75rem;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;"></p>
</div>
```

Secondary cards row (below the `.muscle-grid`, before the section CTA):
```html
<div id="decade-cards-row" style="display:none;margin-top:48px;">
  <p style="color:#555;font-size:0.72rem;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:20px;text-align:center;">More results from this decade</p>
  <div class="decade-cards-flex" style="display:flex;gap:16px;">
    <div id="dc-1" style="flex:1 1 0;min-width:0;display:none;"><img id="dc-1-img" src="" alt="" style="width:100%;border-radius:6px;object-fit:cover;aspect-ratio:1/1;display:block;"><p id="dc-1-cap" style="color:#555;font-size:0.72rem;margin-top:8px;text-align:center;letter-spacing:0.04em;"></p></div>
    <div id="dc-2" style="flex:1 1 0;min-width:0;display:none;"><img id="dc-2-img" src="" alt="" style="width:100%;border-radius:6px;object-fit:cover;aspect-ratio:1/1;display:block;"><p id="dc-2-cap" style="color:#555;font-size:0.72rem;margin-top:8px;text-align:center;letter-spacing:0.04em;"></p></div>
    <div id="dc-3" style="flex:1 1 0;min-width:0;display:none;"><img id="dc-3-img" src="" alt="" style="width:100%;border-radius:6px;object-fit:cover;aspect-ratio:1/1;display:block;"><p id="dc-3-cap" style="color:#555;font-size:0.72rem;margin-top:8px;text-align:center;letter-spacing:0.04em;"></p></div>
  </div>
</div>
```

Add to inline `<style>` block:
```css
@media (max-width: 768px) {
  .decade-cards-flex { flex-direction: column !important; }
}
```

### G2 — JS data objects

```javascript
// Bullet point copy — keyed by bracket, 4 points each
const musclePoints = {
    "20s":  [ { h: "Heading", p: "Body" }, ... ],  // 4 entries
    "30s":  [ ... ],
    "40s":  [ ... ],
    "50s":  [ ... ],
    "60s":  [ ... ],
    "70s+": [ ... ]
};

// Hero transformation — image OR quote per decade (null = hidden)
const transformationImages = {
    "20s":  { src: "URL", alt: "Alt text", caption: "Name — X months" },
    "30s":  { src: "URL", alt: "...", caption: "..." },
    "40s":  { src: "URL", alt: "...", caption: "..." },
    "50s":  { src: "URL", alt: "...", caption: "..." },
    "60s":  { src: "URL", alt: "...", caption: "..." },
    "70s+": { quote: "Quote text here.", name: "Member name" }  // text quote fallback
};

// Secondary cards — up to 3 per decade (fewer is fine, extras stay hidden)
const transformationCards = {
    "20s":  [ { src: "URL", alt: "...", caption: "Name — X months" }, ... ],
    "30s":  [ ... ],
    "40s":  [ ... ],
    "50s":  [ ... ],   // can have 1, 2, or 3 — missing slots hidden automatically
    "60s":  [],        // empty = section hidden entirely
    "70s+": []
};
```

### G3 — Update functions

```javascript
function updateMusclePoints(bracket) {
    const pts = musclePoints[bracket];
    if (!pts) return;
    pts.forEach((pt, i) => {
        const h = document.getElementById(`mp-${i+1}-h`);
        const p = document.getElementById(`mp-${i+1}-p`);
        if (h) h.textContent = pt.h;
        if (p) {
            p.textContent = pt.p;
            gsap.fromTo(p, { opacity: 0, y: 8 }, { opacity: 1, y: 0, duration: 0.45, ease: "power2.out", delay: i * 0.07 });
        }
    });

    // Hero transformation (image or quote)
    const entry     = transformationImages[bracket];
    const imgWrap   = document.getElementById("decade-transform");
    const quoteWrap = document.getElementById("decade-quote");
    if (imgWrap)   imgWrap.style.display   = "none";
    if (quoteWrap) quoteWrap.style.display = "none";
    if (entry && entry.src) {
        document.getElementById("decade-transform-img").src = entry.src;
        document.getElementById("decade-transform-img").alt = entry.alt || "";
        document.getElementById("decade-transform-caption").textContent = entry.caption || "";
        imgWrap.style.display = "block";
        gsap.fromTo(imgWrap, { opacity: 0, y: 12 }, { opacity: 1, y: 0, duration: 0.5, ease: "power2.out" });
    } else if (entry && entry.quote) {
        document.getElementById("decade-quote-text").textContent = "\u201C" + entry.quote + "\u201D";
        document.getElementById("decade-quote-name").textContent = "\u2014 " + entry.name;
        quoteWrap.style.display = "block";
        gsap.fromTo(quoteWrap, { opacity: 0, y: 12 }, { opacity: 1, y: 0, duration: 0.5, ease: "power2.out" });
    }
}

function updateDecadeCards(bracket) {
    const cards = transformationCards[bracket] || [];
    const row   = document.getElementById("decade-cards-row");
    if (!row) return;
    let anyVisible = false;
    [1, 2, 3].forEach(n => {
        const slot = document.getElementById(`dc-${n}`);
        const data = cards[n - 1];
        if (!slot) return;
        if (data) {
            document.getElementById(`dc-${n}-img`).src = data.src;
            document.getElementById(`dc-${n}-img`).alt = data.alt || "";
            document.getElementById(`dc-${n}-cap`).textContent = data.caption || "";
            slot.style.display = "block";
            anyVisible = true;
        } else {
            slot.style.display = "none";
        }
    });
    row.style.display = anyVisible ? "block" : "none";
    if (anyVisible) gsap.fromTo(row, { opacity: 0, y: 16 }, { opacity: 1, y: 0, duration: 0.5, ease: "power2.out" });
}
```

### G4 — Adding transformation images

Upload each image individually via scp — **never use a multi-file batch scp command** (it treats the last destination as a directory and corrupts the upload):

```bash
# CORRECT — one file per scp call
scp -i $KEY -P $PORT "/path/to/Name_Decade_Duration.png" $USER@$HOST:$WP/wp-content/uploads/YYYY/MM/name-decade-Xm.png

# WRONG — creates a directory at the last destination path
scp -i $KEY -P $PORT file1.png $BASE/dest1.png file2.png $BASE/dest2.png file3.png $BASE/dest3.png
```

If a directory was accidentally created at the target path, remove it before re-uploading:
```bash
ssh ... "rm -rf $WP/wp-content/uploads/YYYY/MM/name-decade-Xm.png"
scp ... file.png $USER@$HOST:.../name-decade-Xm.png
```

**Quote fallback:** When a before/after image isn't available for a decade, use a real member quote in `transformationImages` with `{ quote: "...", name: "Member name" }`. It renders as a pink left-bordered card.

**Copy source:** Bullet point copy for each decade is derived from the demographic email sequences. Match voice and language to the sequence for that life stage:
- 20s → Teenage/NNC + 20s & 30s sequences
- 30s → 20s & 30s sequence
- 40s → Perimenopause sequence ("you are not broken" framing)
- 50s → Perimenopause + Post Menopause ("sarcopenia" named directly, "never too late but too late to keep waiting")
- 60s → Post Menopause ("body that thrives not holds up", "confidence is a side effect")
- 70s+ → Post Menopause ("you didn't break, you evolved", functional independence)

---

## Part D: Deploy

```bash
KEY=$SITEGROUND_SSH_KEY_PATH
PORT=$SITEGROUND_SSH_PORT
USER=$SITEGROUND_SSH_USER
HOST=$SITEGROUND_SSH_HOST
WP="/home/$USER/www/blog.theevolvedgym.com.au/public_html"
THEME="$WP/wp-content/themes/blocksy-child"

# 1. Upload JS — CRITICAL: upload to THEME/js/, NOT to public_html root
# Wrong: $USER@$HOST:$WP/homepage.js          ← WordPress never reads this
# Right: $USER@$HOST:$THEME/js/homepage.js     ← this is what functions.php enqueues
scp -i $KEY -P $PORT /tmp/homepage.js $USER@$HOST:$THEME/js/homepage.js

# After uploading JS, bump the version in functions.php to bust browser cache:
ssh -i $KEY -p $PORT $USER@$HOST "sed -i 's/\"[0-9]*\.[0-9]*\"/\"NEW_VER\"/' $THEME/functions.php"
# (replace NEW_VER with the next version number, e.g. 19.0, 20.0)

# 2. Append CSS (check it hasn't already been appended)
ssh -i $KEY -p $PORT $USER@$HOST "grep -c 'Animation Layer' $THEME/style.css || cat /tmp/homepage-animation.css >> $THEME/style.css"

# 3. Upload HTML + write to DB
scp -i $KEY -P $PORT /tmp/homepage-vN.html $USER@$HOST:$WP/homepage-vN.html
ssh -i $KEY -p $PORT $USER@$HOST "cd $WP && wp eval '
  global \$wpdb;
  \$r = \$wpdb->update(\$wpdb->posts, [\"post_content\" => file_get_contents(\"homepage-vN.html\")], [\"ID\" => PAGE_ID]);
  echo \$r === false ? \"ERROR: \" . \$wpdb->last_error : \"OK rows=\" . \$r;
'"

# 4. Flush ALL caches (must run all three — each clears a different layer)
ssh -i $KEY -p $PORT $USER@$HOST "cd $WP && wp cache flush && wp transient delete --all && wp sg purge"
```

**Cache flush layers:**
| Command | What it clears |
|---|---|
| `wp cache flush` | WordPress object cache (WP_Object_Cache) |
| `wp transient delete --all` | Transients stored in DB |
| `wp sg purge` | SiteGround dynamic + static page cache — **must include this or the live site serves a stale HTML snapshot** |

---

## Part E: Mobile Optimisation

Mobile is always a separate pass — do this after desktop is approved.

### Card rows: horizontal scroll → vertical stack

Card rows use `display:flex;overflow-x:auto` for desktop. On mobile they must stack vertically. **Use an inline `<style>` block at the top of the HTML** — not a stylesheet append. SiteGround serves CSS files with a 1-year cache header; inline styles are always fresh.

Add `class="card-row"` to every horizontal card container, then add this block at the very top of the HTML:

```html
<style>
@media (max-width: 768px) {
  .card-row {
    flex-direction: column !important;
    overflow-x: visible !important;
    padding: 0 16px !important;
  }
  .card-row > div {
    min-width: 0 !important;
    width: 100% !important;
    flex: none !important;
  }

  /* Journey cards — square crop on mobile */
  .card-row .journey-card img,
  .card-row .membership-card img {
    height: auto !important;
    aspect-ratio: 1/1 !important;
    width: 100% !important;
    object-fit: cover !important;
  }

  /* Testimonial carousel images — square on mobile */
  .carousel-card img {
    height: auto !important;
    aspect-ratio: 1/1 !important;
    width: 100% !important;
    object-fit: cover !important;
  }

  /* Gym photo grid — square on mobile */
  .gym-photos img {
    height: auto !important;
    aspect-ratio: 1/1 !important;
    width: 100% !important;
    object-fit: cover !important;
  }
}
</style>
```

### Proven aspect ratios

| Context | Desktop | Mobile |
|---|---|---|
| Journey cards (portrait) | `height:420px` inline | `1/1` square |
| Membership cards | `height:220px` inline | `1/1` square |
| Testimonial/result cards | `width:100%` (natural) | `1/1` square |
| Gym photos grid | `height:200px` inline | `1/1` square |
| Timetable image | natural | leave as-is (content must be readable) |
| YouTube embed | `padding-bottom:56.25%` | leave as-is |

The `1/1` square ratio was confirmed perfect across all card types. If images need to be taller, step up: `1/1` → `4/5` → `3/4` → `2/3` → `9/16`. If shorter: `1/1` → `5/4` → `4/3` → `16/9`.

### Classes to add to HTML

| Element | Class to add |
|---|---|
| Journey cards container `<div>` | `card-row` |
| Membership cards container `<div>` | `card-row` |
| Gym photos grid `<div>` | `gym-photos` |

### Two-column sections on mobile

Sections using `display:grid;grid-template-columns:1fr 1fr` should collapse to a single column on mobile. If column order matters (e.g. charts should appear above text), use CSS `order` to reorder — do not restructure the HTML.

**Pattern: collapse + reorder**

Add distinct classes to the grid container and each child column:

```html
<div class="muscle-grid" style="display:grid;grid-template-columns:1fr 1fr;gap:32px;">
  <div class="muscle-text"><!-- text points --></div>
  <div class="muscle-charts"><!-- charts --></div>
</div>
```

Then in the inline `<style>` block:

```css
@media (max-width: 768px) {
  .muscle-grid { grid-template-columns: 1fr !important; }
  .muscle-charts { order: -1; }  /* charts appear first on mobile */
  .muscle-text   { order: 1; }   /* text points appear second */
}
```

**Rule:** always use `order` for reordering — never duplicate or restructure HTML for mobile. The desktop order (text left, charts right) stays intact; mobile reverses via `order` only.

For sections where column order doesn't matter, a single class is enough:

```css
@media (max-width: 768px) {
  .two-col { grid-template-columns: 1fr !important; }
}
```

---

## Part F: Verification Checklist

- [ ] Video autoplays silently on desktop (Chrome, Safari, Firefox)
- [ ] Poster image shows on mobile / before video loads
- [ ] Text is readable over video (adjust overlay opacity if needed: `rgba(0,0,0,0.X)`)
- [ ] Hero eyebrow → headline → sub → CTA reveal in sequence on page load
- [ ] Scroll down: each section fades in as it enters viewport
- [ ] Journey cards lift on hover, label darkens
- [ ] Membership cards lift on hover
- [ ] Stat counters animate when scrolled into view
- [ ] Sarcopenia chart renders; dragging age slider updates chart highlight + annotation + bullet points + hero transformation + secondary cards simultaneously
- [ ] Frequency chart renders in "We Don't Guess We Guide" section (not Why Muscle Matters)
- [ ] Phase buttons (Weeks 1–12 / Weeks 13–26 / Month 6–12) update annotation text with GSAP fade
- [ ] Decade-dynamic bullet points update on slider move with staggered cascade
- [ ] Hero transformation image (or quote block) appears/disappears per decade
- [ ] Secondary transformation cards row appears only for decades with images; hidden otherwise
- [ ] Secondary cards stack to single column on mobile
- [ ] Testimonial carousel drags/swipes; prev/next buttons work
- [ ] **Mobile: journey cards stack vertically, square images**
- [ ] **Mobile: membership cards stack vertically, square images**
- [ ] **Mobile: gym photos are square**
- [ ] **Mobile: no horizontal overflow on any section**
- [ ] **Mobile: two-column sections collapse to single column**

---

## Part G: Copy & Tone Principles

These principles were established during a full copy pass against the Ally avatar and brand positioning documents. Apply them whenever writing or editing homepage copy.

### Brand Voice in Practice

- **Empathy first, solution second.** Open with acknowledgement of her situation before offering the answer. Especially important in FAQs.
- **Pair every physical result with an emotional/life outcome.** The body result is proof; the life change is the story she wants for herself. ("She lost 14kg" → "and gained belief in herself.")
- **Use direct second-person.** "You" and "your" throughout — never passive or third-person.
- **Avoid clinical jargon.** Academic credential drops (e.g. "based on research out of M.I.T.") feel impersonal. Say what it does for her, not where it came from.
- **No negative phrasing that implies past failure.** Never "you've tried and failed." Always "this time is different because..."

### Copy Structure Patterns That Work Well

| Section | What Works |
|---|---|
| Hero | Life-stage acknowledgement + pain ("sick of fads") + transformation promise |
| Old Way vs Evolved Way | Two-column contrast shows her current frustration and the alternative in one glance |
| Why Muscle Matters | Each stat/heading must match the body copy — a heading that promises hormones must deliver hormones content |
| Transformation stories | Specific, authentic, emotional. Name + life context + physical result + life outcome |
| FAQ | Empathy opener → honest transparency → value framing → zero obligation |
| Memberships heading | "Not Sure Where To Start?" removes overwhelm and meets Ally at her uncertainty |
| Final CTA | Short, concrete, zero hype. "One hour. A complete picture. A clear path forward." |

### Tone Consistency Markers

Use these as a gut-check before publishing any homepage copy:
- Does it sound like a trusted female friend who happens to be an expert?
- Does it acknowledge her challenge before offering the solution?
- Could the word "transform" be replaced with something more specific and human?
- Is there any phrasing that implies she should already be doing this / has failed?

### Copy Changes Made (2026-05-02)

**FAQs (7 rewrites):**
- "Can I see the gym": Added empathetic opener about feeling welcome
- "What happens on first visit": "We'll be straight with you: we may not always have a spot available"
- "Are there any joining fees": Expanded to full transparent paragraph
- "Will lifting weights make me bulky": Reframed from testosterone-deficit framing to positive empowerment
- "Do you offer nutrition support": Removed pitch-y result claims; what's included + why it works
- "Perimenopause symptoms": Added 2-paragraph structure with empathetic opener
- "Osteoporosis safety": Added empathetic opener about it being an important question

**Why Muscle Matters — "Stress Hijacks Your Hormones":**
- Old body copy talked about dementia risk (heading/content mismatch)
- Fixed: body copy now delivers on heading promise — cortisol, stress-driven fat storage, disrupted sleep, hormonal regulation through strength training

**Behaviour Science pillar:**
- Removed MIT credential drop; replaced with what the approach does for her

---

## Known Gotchas Reference

| Problem | Cause | Fix |
|---|---|---|
| Video black in browser | Dolby Vision BT.2020 HLG metadata | Use `colorspace=all=bt709:iall=bt2020` in ffmpeg |
| Video plays on test page, black on site | Double `filter:brightness()` stacking | Remove filter from CSS class; use overlay div only |
| Animations silently not firing | Class hooks missing from HTML | Verify every class in the B3 table exists in HTML |
| Page looks the same after deploy | SiteGround page cache | Always run `wp sg purge` after every change |
| CSS styles stripped | `wp_kses_post` sanitization | Use `$wpdb->update()` direct DB write, never `wp_insert_post` |
| `rows=0` on DB write | Content identical to what's already stored | Not an error — check live page; if stale, run `wp sg purge` |
| Mobile CSS changes not applying | SiteGround serves CSS with 1-year cache header | Put responsive CSS in an inline `<style>` block in the HTML, not in style.css |
| Cards still scrolling horizontally on mobile | `overflow-x:auto` and `min-width` inline styles win over stylesheet CSS | Use `!important` in the inline `<style>` block |
| Frequency chart dark / never visible | `data-reveal` on chart div + `initChartReveal()` both set opacity:0 — animations compete | Remove `data-reveal` from the frequency chart wrapper; `initChartReveal()` handles it |
| Multi-file scp creates a directory at destination | scp with multiple source files treats last argument as destination directory | Always upload transformation images one file per scp call |
| Decade content not updating on slider move | `updateMusclePoints` / `updateDecadeCards` not called in slider handler | Call all three update functions from the same `input` event listener on `#ageSlider` |
