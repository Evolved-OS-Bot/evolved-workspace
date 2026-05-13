# Plan: Homepage 2026 Animation & Interactivity Redesign

**Created:** 2026-04-30
**Status:** Live (JS v31.0 deployed 2026-05-02) — Tiers 1, 2, 3 & 4 (partial) complete
**Request:** Add cinematic animation layer and interactive elements to the existing WordPress homepage without changing its foundational structure.

---

## Overview

### What This Plan Accomplishes

Transforms the existing static homepage into a cinematic, interactive experience by adding a GSAP-powered animation layer, interactive data visualisations, a draggable testimonial carousel, animated stats, and polished card hover states — all without restructuring the existing content. The animation is delivered through updates to `homepage.js` and `homepage-v4.html`, then pushed live via the existing SSH + direct DB write pipeline.

### Why This Matters

The homepage is the primary conversion surface for the SA pre-qualification funnel. A static page loses attention before the visitor reaches the CTA. Motion, interactivity, and data visualisation increase dwell time, build credibility, and signal that The Evolved is a premium, evidence-based studio — not a generic gym. This directly supports the goal of converting cold traffic into Strength Assessment bookings.

---

## Current State

### Relevant Existing Structure

- **`/wp-content/themes/blocksy-child/js/homepage.js`** — GSAP + Chart.js animations already written, but targeting class hooks (`.hero-headline`, `.evolved-section`, `.result-card`, etc.) that **do not exist** in the current homepage HTML. The JS is loaded but effectively doing nothing.
- **`/wp-content/themes/blocksy-child/functions.php`** — GSAP 3.12.5, ScrollTrigger, Chart.js 4.4.0, and `homepage.js` already enqueued on the front page. No new libraries needed for Tiers 1–3.
- **`/tmp/homepage-v4.html`** — Current homepage HTML. Has no class hooks, no `data-reveal` attributes, no canvas elements. Sections use plain inline-styled `<section>` tags.
- **`reference/infographic-sarcopenia-data.md`** — Full sarcopenia data table + annotation copy already written.
- **`reference/infographic-frequency-data.md`** — Training frequency data + annotation copy already written.
- **`reference/homepage-implementation.md`** — Blocksy child theme build guide including CSS custom properties.

### Gaps or Problems Being Addressed

1. `homepage.js` targets class hooks that don't exist in the HTML → animations never fire
2. No scroll-reveal on any section → page feels static as you scroll
3. Hero has no parallax or cinematic text reveal → first impression is flat
4. Journey and membership cards have no hover states → feel unclickable
5. "Why Muscle Matters" section uses static images → data visualisation is already built in JS but has no canvas to render into
6. Testimonials are a static 4-column grid → no movement, no momentum
7. No animated number counters → key stats (250g/year, 20kg, 40kg) are just text

---

## Proposed Changes

### Summary of Changes

- Add `data-reveal`, `data-reveal-stagger`, and semantic class hooks to all sections in `homepage-v4.html`
- Replace "Why Muscle Matters" static images with Chart.js canvas + age bracket button UI (sarcopenia) and frequency chart
- Add animated stat counters to key numbers across the page
- Add number counter elements to results section
- Wrap testimonial cards in a draggable carousel
- Rewrite `homepage.js` with: global scroll-reveal system, hero parallax + staggered text, card hover lift, carousel, chart reveal triggers, and number counters
- Update `style.css` with hover state CSS, carousel CSS, chart container CSS, and counter styles
- Push updated HTML + JS to live site via SSH DB write

### New Files to Create

| File Path | Purpose |
| --- | --- |
| `/tmp/homepage-v5.html` | Complete updated homepage HTML with all class hooks, canvas elements, and carousel structure |

### Files to Modify

| File Path | Changes |
| --- | --- |
| `SiteGround: blocksy-child/js/homepage.js` | Full rewrite — global reveal system, hero parallax, carousel, counters, chart triggers |
| `SiteGround: blocksy-child/style.css` | Add hover states, carousel CSS, chart container, counter styles |
| `SiteGround: blocksy-child/functions.php` | Bump `homepage.js` version string to bust cache |

### Files to Delete

None.

---

## Design Decisions

### Key Decisions Made

1. **`data-reveal` attribute approach over class-based hooks**: Adding `data-reveal` to elements is less intrusive than adding classes everywhere, and allows a single JS observer to handle all reveals. The attribute can carry a variant value (`data-reveal="fade-up"`, `data-reveal="fade-left"`, `data-reveal="scale"`) for per-element control.

2. **Cinematic tone for hero and copy, energetic tone for data**: Hero text reveals over ~1.2s with power3 easing. Stat counters run fast (0.8s). Chart lines draw on scroll with 1.4s duration. Result cards stagger in with momentum.

3. **No new JS libraries**: Swiper/Flickity not needed. GSAP Draggable (included in GSAP core) powers the testimonial carousel. This keeps the page load lean.

4. **Replace static Why Muscle Matters images with live charts**: The sarcopenia and frequency charts are already fully implemented in `homepage.js`. They just need `<canvas>` elements in the HTML and the age bracket button UI. This is the highest-impact Tier 3 item and is essentially free given the existing code.

5. **CSS hover states over JS hover events**: Card hover lift and overlay are pure CSS (`transform: translateY`, `::after` overlay). JS is not needed for hover — keeps interactions snappy and accessible.

6. **Version-bust `homepage.js` on deploy**: Change `"1.0"` to `"2.0"` in `wp_enqueue_script` so browser cache doesn't serve the old file.

7. **Tier 1 is self-contained and deployable independently**: Tiers 1–3 are structured as sequential steps. After Step 4 (Tier 1 complete), the site is in a valid improved state. Tiers 2–3 build on top.

### Alternatives Considered

- **Swiper.js carousel**: Rejected — adds ~40kb, requires CSS file, and GSAP Draggable achieves the same result with zero additional load.
- **CSS-only scroll animations (`@keyframes` + `IntersectionObserver`)**: Rejected — GSAP ScrollTrigger gives precise control over trigger points, scrub effects, and stagger. Already loaded, so no cost.
- **Video hero background**: Considered for future. Requires a video asset. Not in scope for this plan.

### Open Questions

None — user confirmed all tiers and tone direction. Tier 1 prioritised first.

---

## Step-by-Step Tasks

### Step 1: Write the updated homepage.js (full animation system)

Replace the current `homepage.js` entirely. The new file contains:

**1A — Global scroll-reveal system**
```javascript
// Single observer for all data-reveal elements
gsap.utils.toArray('[data-reveal]').forEach(el => {
    const variant = el.dataset.reveal || 'fade-up';
    const delay   = parseFloat(el.dataset.revealDelay || 0);
    const stagger = el.dataset.revealStagger;

    let from = { opacity: 0, duration: 0.85, ease: 'power3.out', delay };
    if (variant === 'fade-up')   from = { ...from, y: 48 };
    if (variant === 'fade-left') from = { ...from, x: -40 };
    if (variant === 'fade-right')from = { ...from, x: 40 };
    if (variant === 'scale')     from = { ...from, scale: 0.94 };

    if (stagger) {
        gsap.from(el.querySelectorAll('[data-reveal-child]'), {
            ...from, stagger: parseFloat(stagger),
            scrollTrigger: { trigger: el, start: 'top 82%', once: true }
        });
    } else {
        gsap.from(el, { ...from,
            scrollTrigger: { trigger: el, start: 'top 82%', once: true }
        });
    }
});
```

**1B — Hero parallax**
```javascript
// Background image parallax (scrub)
gsap.to('.hero-bg', {
    yPercent: 25,
    ease: 'none',
    scrollTrigger: { trigger: '.hero', start: 'top top', end: 'bottom top', scrub: true }
});

// Staggered hero text reveal (cinematic — line by line)
const heroTl = gsap.timeline({ defaults: { ease: 'power3.out' } });
heroTl
  .from('.hero-eyebrow', { opacity: 0, y: 20, duration: 0.7 }, 0.3)
  .from('.hero-headline', { opacity: 0, y: 40, duration: 1.0 }, 0.55)
  .from('.hero-sub',      { opacity: 0, y: 30, duration: 0.8 }, 0.9)
  .from('.hero-cta',      { opacity: 0, y: 20, duration: 0.7 }, 1.2)
  .from('.hero-disclaimer',{ opacity: 0, duration: 0.5 }, 1.5);

// CTA pulse loop
gsap.to('.hero-cta', {
    boxShadow: '0 0 0 8px rgba(228,51,136,0)', scale: 1.02,
    duration: 1.2, repeat: -1, yoyo: true, ease: 'sine.inOut', delay: 2.5
});
```

**1C — Animated number counters**
```javascript
gsap.utils.toArray('[data-count]').forEach(el => {
    const target = parseFloat(el.dataset.count);
    const prefix = el.dataset.countPrefix || '';
    const suffix = el.dataset.countSuffix || '';
    gsap.fromTo(el, { innerText: 0 }, {
        innerText: target, duration: 1.6, ease: 'power2.out', snap: { innerText: target < 10 ? 0.1 : 1 },
        onUpdate() { el.innerText = prefix + parseFloat(el.innerText).toFixed(target < 10 ? 1 : 0) + suffix; },
        scrollTrigger: { trigger: el, start: 'top 85%', once: true }
    });
});
```

**1D — Chart scroll-trigger reveal** (animate chart drawing on scroll)
```javascript
function revealChart(chart, trigger) {
    ScrollTrigger.create({
        trigger,
        start: 'top 75%',
        once: true,
        onEnter() {
            chart.data.datasets.forEach(ds => { ds.hidden = false; });
            chart.update();
        }
    });
}
// After initSarcopeniaChart() and initFrequencyChart() calls, pass returned chart instances to revealChart()
```

**1E — Testimonial draggable carousel**
```javascript
// Pure GSAP drag — no Swiper needed
(function initCarousel() {
    const track    = document.querySelector('.carousel-track');
    const cards    = document.querySelectorAll('.carousel-card');
    const prevBtn  = document.querySelector('.carousel-prev');
    const nextBtn  = document.querySelector('.carousel-next');
    if (!track || !cards.length) return;

    let current = 0;
    const total = cards.length;
    const cardW = () => cards[0].getBoundingClientRect().width + 24; // gap

    function goTo(index) {
        current = Math.max(0, Math.min(index, total - 1));
        gsap.to(track, { x: -current * cardW(), duration: 0.5, ease: 'power3.out' });
    }

    if (prevBtn) prevBtn.addEventListener('click', () => goTo(current - 1));
    if (nextBtn) nextBtn.addEventListener('click', () => goTo(current + 1));

    // Touch/drag support
    let startX = 0;
    track.addEventListener('touchstart', e => { startX = e.touches[0].clientX; }, { passive: true });
    track.addEventListener('touchend',   e => {
        const diff = startX - e.changedTouches[0].clientX;
        if (Math.abs(diff) > 50) goTo(diff > 0 ? current + 1 : current - 1);
    });
})();
```

**Actions:**
- SSH into SiteGround
- Write the complete new `homepage.js` to `blocksy-child/js/homepage.js`
- Keep existing sarcopenia and frequency chart code intact (merge, don't replace)
- Update version string in `functions.php` from `"1.0"` to `"2.0"`

**Files affected:**
- `SiteGround: /wp-content/themes/blocksy-child/js/homepage.js`
- `SiteGround: /wp-content/themes/blocksy-child/functions.php`

---

### Step 2: Update style.css with animation support styles

Add to the end of `blocksy-child/style.css`:

```css
/* ── REVEAL BASE STATE ─────────────────────────────────────── */
/* Elements with data-reveal start invisible — GSAP animates them in */
[data-reveal] { opacity: 0; }

/* ── HERO ──────────────────────────────────────────────────── */
.hero { position: relative; overflow: hidden; }
.hero-bg {
    position: absolute; inset: 0;
    background-size: cover; background-position: center;
    filter: brightness(0.35);
    will-change: transform;
}
.hero-eyebrow {
    font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.18em;
    color: #e43388; margin-bottom: 12px; opacity: 0;
}
.hero-headline { opacity: 0; }
.hero-sub      { opacity: 0; }
.hero-cta      { opacity: 0; transition: background 0.2s; }
.hero-disclaimer { opacity: 0; }

/* ── CARD HOVER LIFT ───────────────────────────────────────── */
.journey-card, .membership-card {
    transition: transform 0.28s cubic-bezier(0.25,0.8,0.25,1),
                box-shadow 0.28s cubic-bezier(0.25,0.8,0.25,1);
    cursor: pointer;
}
.journey-card:hover    { transform: translateY(-6px); box-shadow: 0 16px 40px rgba(228,51,136,0.25); }
.membership-card:hover { transform: translateY(-6px); box-shadow: 0 16px 40px rgba(228,51,136,0.2); }

/* Pink label overlay on journey card hover */
.journey-card .card-label {
    transition: background 0.25s;
}
.journey-card:hover .card-label { background: #c4206e; }

/* ── NUMBER COUNTERS ───────────────────────────────────────── */
.stat-number {
    font-family: 'PT Serif Caption', serif;
    font-size: clamp(2.4rem, 5vw, 4rem);
    color: #e43388; line-height: 1;
    display: block; margin-bottom: 8px;
}
.stat-label { color: #aaa; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.08em; }

/* ── CHART CONTAINERS ──────────────────────────────────────── */
.chart-section { position: relative; }
.chart-canvas-wrap {
    position: relative; background: #0d0d0d; border-radius: 8px;
    border: 1px solid #222; padding: 24px;
}
.chart-annotation {
    color: #aaa; font-size: 0.9rem; line-height: 1.75;
    margin-top: 20px; min-height: 3em;
    border-left: 2px solid #e43388; padding-left: 16px;
}
.age-btn-group { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 20px; }
.age-btn {
    background: #1a1a1a; border: 1px solid #333; color: #aaa;
    padding: 8px 16px; border-radius: 4px; font-size: 0.8rem;
    cursor: pointer; transition: all 0.2s; font-family: 'Lato', sans-serif;
}
.age-btn:hover { border-color: #e43388; color: #f5f0eb; }
.age-btn.active { background: #e43388; border-color: #e43388; color: #fff; }

/* ── TESTIMONIAL CAROUSEL ──────────────────────────────────── */
.carousel-viewport {
    overflow: hidden; position: relative; cursor: grab;
    border-radius: 8px;
}
.carousel-viewport:active { cursor: grabbing; }
.carousel-track {
    display: flex; gap: 24px; will-change: transform;
}
.carousel-card {
    flex: 0 0 calc(50% - 12px); min-width: 280px;
    background: #0d0d0d; border: 1px solid #222; border-radius: 8px;
    padding: 28px; position: relative;
}
@media (max-width: 640px) {
    .carousel-card { flex: 0 0 85vw; }
}
.carousel-controls {
    display: flex; justify-content: center; gap: 12px; margin-top: 24px;
}
.carousel-prev, .carousel-next {
    background: #1a1a1a; border: 1px solid #333; color: #f5f0eb;
    width: 44px; height: 44px; border-radius: 50%; font-size: 1.2rem;
    cursor: pointer; transition: all 0.2s; display: flex;
    align-items: center; justify-content: center;
}
.carousel-prev:hover, .carousel-next:hover {
    background: #e43388; border-color: #e43388;
}
```

**Actions:**
- SSH into SiteGround
- Append the above CSS to `blocksy-child/style.css` (do not replace existing styles)

**Files affected:**
- `SiteGround: /wp-content/themes/blocksy-child/style.css`

---

### Step 3: Build homepage-v5.html — add all class hooks and structural upgrades

Starting from `/tmp/homepage-v4.html`, make these targeted additions. **Do not change any text content or section order.**

**3A — Hero section rebuild**

Replace the current hero `<section>` with:
- Add class `hero` to the section
- Move background image from inline `background:url(...)` div to a separate `<div class="hero-bg">` element (enables GSAP parallax targeting by class)
- Add class `hero-eyebrow` to a new `<p>` above the H1: "Pick Your Journey"
- Add class `hero-headline` to the H1
- Add class `hero-sub` to the subheadline `<p>`
- Add class `hero-cta` to the CTA `<a>` button
- Add class `hero-disclaimer` to the "No gym tour" `<p>`

**3B — Add `data-reveal` to all sections**

Every `<section>` tag gets `data-reveal="fade-up"`. Headings within sections get `data-reveal="fade-up" data-reveal-delay="0.1"`. The stagger pattern applies to card containers.

Specific additions:
```html
<!-- About section heading -->
<h2 data-reveal="fade-up" ...>

<!-- How to Get Started steps container -->
<div data-reveal="fade-up" data-reveal-stagger="0.15">
  <div data-reveal-child ...>Step 1</div>
  <div data-reveal-child ...>Step 2</div>
  <div data-reveal-child ...>Step 3</div>
</div>

<!-- Old Way vs Evolved Way cards -->
<div data-reveal="fade-left" ...>The Old Way</div>
<div data-reveal="fade-right" ...>The Evolved Way</div>

<!-- Why Muscle Matters points -->
<div data-reveal="fade-up" data-reveal-stagger="0.12">
  <div data-reveal-child>Sarcopenia...</div>
  <div data-reveal-child>Stress...</div>
  <div data-reveal-child>Joints...</div>
  <div data-reveal-child>Bone Loss...</div>
</div>

<!-- FAQ items -->
<div data-reveal="fade-up" data-reveal-stagger="0.08">
  <details data-reveal-child>...</details>
  ...
</div>
```

**3C — Add journey and membership card classes**

Journey card wrapper `<div>`: add class `journey-card`
Journey card label bar `<div style="background:#e43388...">`: add class `card-label`
Membership card wrapper `<div>`: add class `membership-card`

**3D — Replace Why Muscle Matters static images with charts**

Replace the `<div>` column containing the two static images with:

```html
<!-- Sarcopenia Chart -->
<div class="chart-canvas-wrap" data-reveal="fade-up">
  <div class="age-btn-group">
    <button class="age-btn" data-age="20s">20s</button>
    <button class="age-btn active" data-age="30s">30s</button>
    <button class="age-btn" data-age="40s">40s</button>
    <button class="age-btn" data-age="50s">50s</button>
    <button class="age-btn" data-age="60s">60s</button>
    <button class="age-btn" data-age="70s+">70s+</button>
  </div>
  <canvas id="sarcopeniaChart" height="280"></canvas>
  <p id="sarcopeniaAnnotation" class="chart-annotation">Select your age bracket above to see what's possible for your body right now.</p>
  <div style="text-align:center;margin-top:24px;">
    <a href="https://go.theevolvedgym.com.au/strength-assessment" id="sarcopeniaCta" style="display:inline-block;background:#e43388;color:#fff;padding:14px 32px;border-radius:4px;font-family:'Lato',sans-serif;font-size:0.9rem;font-weight:700;text-decoration:none;">Book Your Strength Assessment</a>
  </div>
</div>

<!-- Frequency Chart -->
<div class="chart-canvas-wrap" style="margin-top:24px;" data-reveal="fade-up" data-reveal-delay="0.15">
  <canvas id="frequencyChart" height="220"></canvas>
  <p id="frequencyAnnotation" class="chart-annotation">Hover a curve to see the impact of training frequency on long-term results.</p>
</div>
```

**3E — Add animated number counters**

In the "Real Results" section, above the carousel cards, add a 3-stat counter row:

```html
<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:24px;text-align:center;margin-bottom:56px;" data-reveal="fade-up" data-reveal-stagger="0.15">
  <div data-reveal-child>
    <span class="stat-number" data-count="20" data-count-suffix="kg">0kg</span>
    <span class="stat-label">Weight lost — Tash</span>
  </div>
  <div data-reveal-child>
    <span class="stat-number" data-count="60" data-count-suffix="kg">0kg</span>
    <span class="stat-label">Squat — Vicki at 50</span>
  </div>
  <div data-reveal-child>
    <span class="stat-number" data-count="40" data-count-suffix="kg">0kg</span>
    <span class="stat-label">Lifts — Eleni at 63</span>
  </div>
</div>
```

Also add a counter to the "Why Muscle Matters" left column:
```html
<!-- Above the 4 sub-points -->
<div style="text-align:center;margin-bottom:32px;" data-reveal="scale">
  <span class="stat-number" data-count="250" data-count-suffix="g">0g</span>
  <span class="stat-label">muscle lost per year without training</span>
</div>
```

**3F — Testimonial carousel**

Replace the static 4-card grid in "Real Results" with:

```html
<div class="carousel-viewport" data-reveal="fade-up">
  <div class="carousel-track">
    <div class="carousel-card">
      <img src="[ruth-image]" ... style="width:100%;border-radius:6px;margin-bottom:16px;">
      <p style="color:#e43388;font-size:0.8rem;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;">Ruth, 2 Kids</p>
      <p style="color:#aaa;font-size:0.9rem;line-height:1.7;margin-top:10px;">"[quote]"</p>
    </div>
    <!-- Tash, Vicki, Eleni cards -->
  </div>
</div>
<div class="carousel-controls">
  <button class="carousel-prev" aria-label="Previous">&#8592;</button>
  <button class="carousel-next" aria-label="Next">&#8594;</button>
</div>
```

**Actions:**
- Read `/tmp/homepage-v4.html` fully
- Apply all 3A–3F changes
- Write result to `/tmp/homepage-v5.html`

**Files affected:**
- `/tmp/homepage-v5.html` (new)

---

### Step 4: Deploy Tier 1 — Upload JS, CSS, and HTML

Deploy in this order so the page is never broken mid-deploy:

```bash
SSH_CMD="ssh -i $KEY -p $PORT $USER@$HOST"
THEME="$PUBLIC_HTML/wp-content/themes/blocksy-child"

# 1. Upload new homepage.js
scp ... homepage.js $HOST:$THEME/js/homepage.js

# 2. Update functions.php (version bump to bust cache)
# Edit "1.0" → "2.0" in wp_enqueue_script for evolved-homepage

# 3. Append new CSS to style.css
$SSH_CMD "cat >> $THEME/style.css" < /tmp/evolved-new-styles.css

# 4. Upload and push new HTML to WordPress post ID 165
scp ... homepage-v5.html $HOST:$PUBLIC_HTML/homepage-v5.html
$SSH_CMD "cd $PUBLIC_HTML && wp eval 'global \$wpdb; \$wpdb->update(\$wpdb->posts, [\"post_content\" => file_get_contents(\"homepage-v5.html\")], [\"ID\" => 165]);'"

# 5. Flush cache
$SSH_CMD "cd $PUBLIC_HTML && wp cache flush && wp transient delete --all"
```

**Files affected:**
- `SiteGround: blocksy-child/js/homepage.js`
- `SiteGround: blocksy-child/functions.php`
- `SiteGround: blocksy-child/style.css`
- `SiteGround: public_html/homepage-v5.html` (temp)
- WordPress post ID 165 (content)

---

## Connections & Dependencies

### Files That Reference This Area

- `plans/2026-04-29-website-migration-redesign.md` — parent migration plan; this plan extends it
- `reference/homepage-implementation.md` — Blocksy child theme CSS/JS patterns
- `reference/infographic-sarcopenia-data.md` — sarcopenia chart data and annotation copy
- `reference/infographic-frequency-data.md` — frequency chart data and annotation copy
- `.claude/commands/migrate-ghl-page.md` — references the `homepage.js` animation pattern

### Updates Needed for Consistency

- Update `reference/homepage-implementation.md` to reflect the new animation system and class hooks
- Update `migrate-ghl-page.md` Known Gotchas to note the `data-reveal` pattern

### Impact on Existing Workflows

- The SA pre-qual bot SMS links (`go.theevolvedgym.com.au/strength-assessment`) are unchanged
- GHL custom values are unchanged — links still point to correct URLs
- DNS migration plan is unaffected — these are content-layer changes only

---

## Validation Checklist

- [ ] All sections fade in on scroll — no element is visible on page load before its trigger
- [ ] Hero background parallaxes as you scroll (moves slower than content)
- [ ] Hero text reveals line by line: eyebrow → headline → sub → CTA → disclaimer
- [ ] CTA button pulses with pink glow after text reveal completes
- [ ] Journey cards lift 6px on hover with pink glow shadow
- [ ] Membership cards lift 6px on hover with pink glow shadow
- [ ] Journey card pink label bar darkens on hover
- [ ] Sarcopenia chart renders (two lines visible, pink + grey)
- [ ] Clicking age bracket buttons highlights point on chart and shows annotation text
- [ ] Frequency chart renders with three curves
- [ ] Number counters animate from 0 when scrolled into view (250g, 20kg, 60kg, 40kg)
- [ ] Testimonial carousel: all 4 cards accessible via prev/next buttons
- [ ] Testimonial carousel: touch swipe works on mobile
- [ ] Google Reviews iframe auto-sizes (postMessage listener still working)
- [ ] FAQ accordion still opens/closes on click
- [ ] All CTA buttons link to `go.theevolvedgym.com.au/strength-assessment`
- [ ] No layout breakage on mobile (320px–430px viewport)
- [ ] No JavaScript errors in console

---

## Success Criteria

The implementation is complete when:

1. Scrolling through the page on desktop reveals each section with smooth entrance animation — no element is visible before its scroll trigger fires
2. The hero feels cinematic — background parallaxes, text reveals sequentially, CTA pulses with pink glow
3. The sarcopenia chart is live and interactive (age bracket buttons change chart state and annotation)
4. The testimonial carousel is draggable/tappable and shows all 4 members
5. Number counters animate on scroll for all key stats
6. Zero console errors, no broken layout on mobile

---

## Notes

**Tier execution order:** Steps 1–4 are Tier 1 (scroll-reveal + hero). The chart canvases (Step 3D) are Tier 3 elements but are included in the same HTML pass since the JS is already written. The carousel (Step 3F) is Tier 2. All tiers are implemented in a single `/implement` run since they share the same HTML file deployment.

**Future — Tier 4 (not in this plan):**
- Before/after image slider on Ruth and Vicki transformation photos (would need `gsap-draggable` or a CSS clip-path approach)
- Video loop in hero background (needs video asset from Megan)
- Horizontal scroll "drag to explore" gym photo gallery

**GSAP version note:** GSAP 3.12.5 is loaded. The Draggable plugin is part of GSAP core at this version — no additional CDN URL needed.

**Cache note:** SiteGround has SG Optimizer. After deploying, also clear the SG Optimizer cache from WP Admin → SG Optimizer → Caching if the manual cache flush doesn't propagate immediately.

---

## Implementation Log

### Session 1 (prior context — JS v1.0 → v28.0)

**What was built — well beyond the original plan:**

#### Video carousel
- Added `initVideoCarousel()` IIFE mirroring the photo carousel pattern
- YouTube facade pattern: static thumbnail + SVG play button → autoplay iframe on click via `data-vid` attribute
- Eleni video (WwEcN-oV_XM) added as first card; static Eleni embed section removed

#### Personalised 12-Month Results Curve (replaced static frequency chart)
The original plan called for a simple Chart.js frequency chart. This became a fully interactive personalisation engine:
- **Goal selector** — 5 goals: Lose Weight, Body Recomp, Bone Density, Get Stronger, Hyrox
- **Decade selector** — 20s / 30s / 40s / 50s / 60s
- **Experience level** — New to strength / Some experience / Experienced
- **Meal plan toggle** — shown for lose-weight and recomp goals only
- **5 training sliders** — Strength, HIIT, Pilates, Cardio, Hyrox (with pink fill gradient)
- **Chart.js curve** — exponential growth formula with per-goal effectiveness weights, decade modifiers, experience modifiers, meal plan factor
- **Formula:** `result(t) = peak × mealFactor × dec.peak × exp.peak × score × (1 - exp(-BASE_RATE × sqrt(score) × dec.rate × exp.rate × t))`

#### Tier 1 Personalisation (wired into single `refresh()` call)
- **Membership recommendation** — `rcHighlightMembership(experience)`: never Fit & Flexible; new→Fast Track, others→Sculpt & Strength. Pink border + "Recommended for you" badge on matching `.membership-card[data-mc]`
- **Final CTA copy** — `rcUpdateFinalCTA(goalId, decade)`: GSAP fade transition on `#final-cta-h2` and `#final-cta-sub`, copy nested by goal → decade
- **Profile panel** — `rcUpdateProfilePanel(goalId, decade, score)`: shows `#rc-profile-panel` with member name, blurb, anchor link. Lookup via `RC_PROFILE_STORIES[goalId][decade]` with `rcGetStory()` fallback to "default"

#### Member stories interview + mapping
- Conducted full interview to confirm decade and primary driver for all 24 members
- Created `reference/member-stories.md` with confirmed details, full blurbs, photo filenames, profile panel mapping table
- Key corrections: Katrina=20s, Ruth=30s, Megan=30s, Charmaine=30s, Tash=40s, Tammy=40s, Kylie=40s, Kerrie=40s, Jules=40s (get stronger — NOT hyrox), Johanna=40s (HYROX hero), Vicky=50s

#### Key fixes
- Membership logic: removed `RC_MEMBERSHIP_MAP`; Fast Track only for beginners/injuries
- Profile panel decade mismatch (Monique showing for 40s recomp): restructured `RC_PROFILE_STORIES` to nested goal→decade with fallback function
- HYROX story corrected from Jules → Johanna
- Carousel nav button spacing: added `margin-top:40px` to CTA wrapper

---

### Session 2 — 2026-05-02 (JS v29.0)

#### Profile panel updates
- **lose-weight × 40s** → Tash (doctor's warning, roller coaster dieting angle — replacing Karyn)
- **recomp × 40s** → Tammy (adenomyosis discovery angle)

#### Carousel cards — all copy rewritten to interview-verified stories
- **Katrina** — 20kg + "shop in the same stores as her friends / She did both"
- **Tash** — doctor's warning + roller coaster detail
- **Tammy** — came in stressed wanting body comp / didn't realise the connection to adenomyosis
- **Kylie** — first thing for herself / lower tummy bloat / better mum not more absent
- **Kerrie** — biggest fear was another premature birth (postpartum framing)
- **Megan** — "someone as healthy as me" quote + eating more was the unlock
- **Vicky** — 50th birthday photoshoot / Fast Track / extraordinary photos

#### Section reorder
Timetable moved from between Videos and Google Reviews to between We Don't Guess and Results Curve.

**Conversion funnel flow (current):**
Hero → About → Journey → How To Start → Old Way vs Evolved Way → Why Muscle Matters → Gym Photos → Real Results Carousel → Video Testimonials → Google Reviews → **We Don't Guess (3 pillars)** → **Timetable** → **Results Curve** → **Memberships** → FAQ → Final CTA

---

## Current State (as of 2026-05-02)

- **JS version:** v29.0 — live at `blocksy-child/js/homepage.js`
- **HTML:** live at WordPress post ID 165
- **Member stories reference:** `reference/member-stories.md` — 24 stories, confirmed decades, full blurbs

---

## Homepage Personalisation Roadmap

**Core principle:** Every interaction the visitor makes (goal, decade, training mix) builds a profile. That profile should ripple through the rest of the page — not just the chart. By the time they hit the final CTA, the page should feel like it was written specifically for them.

### Already Live (Tier 1)
- Membership card highlight — "Recommended for you" badge + pink border on matching card
- Final CTA headline + subtext updates dynamically by goal × decade
- "Based on your profile" story panel — surfaces the matching member story below the chart

### Already Live (Tier 2)
- **Results carousel reordering** — `rcReorderCarousel(goalId, decade)` in `homepage.js` — matching goal × decade cards bubble to front on every `refresh()` call. All carousel cards have `data-goal` and `data-decade` attributes.
- **FAQ personalisation** — `rcUpdateFAQ(goalId, decade)` in `homepage.js` — goal-specific FAQ items shown/hidden on selection. All conditional FAQ items have `data-faq-goal` and `data-faq-decade` attributes. Both functions called on every `refresh()` (lines 996–997 of `homepage.js`).

### Already Live (Tier 3)
- **Sticky profile bar** — fixed bottom strip slides up on first results curve interaction. Shows: "Your profile · [Goal] · [Decade] · [Experience]" + "Book Assessment →" CTA. Implemented as `rcUpdateProfileBar(goalId, decade, experience)` called from `refresh()`. HTML: `#profile-bar` / `#profile-bar-text` at end of page.
- **Pillar reordering** — "We Don't Guess" pillars (`#pillar-programming`, `#pillar-nutrition`, `#pillar-behaviour`) reorder via CSS `order` property on goal change. `rcUpdatePillars(goalId)` called from `refresh()`. Nutrition leads for lose-weight/recomp; programming leads for bone-density/get-stronger/hyrox.

### Already Live (Tier 4 — partial)
- **LocalStorage persistence** — `evolved_profile` key stores `{ goal, decade, exp }`. Restored on page load before chart init so button states and chart reflect previous visit immediately. Saved on every `refresh()` call.
- **URL-encoded profile params** — `rcUpdateCTALinks(goalId, decade, exp)` rewrites all `go.theevolvedgym.com.au/strength-assessment` hrefs on every `refresh()` to append `?goal=&decade=&exp=` params. Called from `refresh()`. Enables analytics segmentation and future GHL form pre-population.

### Already Live (Tier 4 — continued)
- **Video hero background** — looping MP4 (`hero-video.mp4`) already live at line 57–59 of homepage HTML. `autoplay muted loop playsinline` with poster fallback.

### Already Live (Tier 4 — continued)
- **Horizontal scroll gym photo gallery** — `initPhotoCarousel()` at line 222 of `homepage.js`. 12 photos, drag + touch + prev/next buttons, snap-to-card, GSAP scroll-reveal stagger. HTML: `.photo-viewport` → `.photo-track` → `.photo-card` × 12.

### Tier 4 — Remaining (blocked on assets)
- Before/after image slider on Ruth and Vicky transformation photos — needs the side-by-side before/after photo assets
