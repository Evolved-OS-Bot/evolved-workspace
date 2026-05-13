# Plan: Pick Your Journey — 2026 Upgrade

**Created:** 2026-05-03
**Status:** Implemented
**Request:** Replace the static navigate-away life stage cards with a two-step in-page selector (life stage → goal), wire selections into the existing personalisation engine, add contextual waitlist CTAs throughout the page.

---

## Overview

### What This Plan Accomplishes

The Pick Your Journey section becomes a two-step in-page selector: visitors choose their life stage (Teenager, 20-30s, Pregnancy, Peri-Menopause, Post-Menopause), then choose their goal (all 5 available regardless of life stage). On selection, the entire homepage personalises in real-time via the existing `refresh()` engine. The GHL funnel pages remain as the conversion endpoint but receive a warm, pre-qualified visitor with profile params in the URL. Contextual waitlist CTAs are threaded through 4 key sections of the page as a lower-friction alternative to the book-now CTA.

### Why This Matters

Pick Your Journey is the highest-converting interaction on the homepage. Currently it only captures life stage and immediately navigates away — the visitor leaves before seeing the 14 video testimonials, transformation gallery, personalised results curve, or any of the social proof. The upgrade keeps the segment intelligence that makes it work, adds the goal dimension that was missing, and lets the entire page do its job as a warm-up before the GHL funnel close.

---

## Current State

### Relevant Existing Structure

**Homepage files:**
- `/tmp/homepage-v5.html` — WordPress post 165 content (deployed via `wp eval`)
- `/tmp/homepage.js` — Blocksy child theme JS at `/wp-content/themes/blocksy-child/js/homepage.js`

**Pick Your Journey — current HTML (lines 104–148, `homepage-v5.html`):**
- 5 photo cards: Teenager, 20-30s, Pregnancy, Peri-Menopause, Post-Menopause
- Each card has an `<a>` overlay linking to a GHL funnel page
- Cards are purely navigational — no JS interaction, no profile system connection

**GHL landing page URL structure:**

There are 10 landing pages — 5 organic (`-o`) and 5 paid (`-p`). Each has its own GHL form, lead intake workflow, and tagging. Paid traffic is sent directly to `-p` pages via ad links — it never touches the homepage. The homepage is organic-only traffic. Therefore all homepage CTAs always link to `-o` pages.

| Life Stage | Organic (homepage) | Paid (direct from ads) |
|---|---|---|
| Teenager | `theevolvedgym.com.au/teen-30dnnc-o` | `theevolvedgym.com.au/teen-30dnnc-p` |
| 20-30s | `theevolvedgym.com.au/20s30s-30dnnc-o` | `theevolvedgym.com.au/20s30s-30dnnc-p` |
| Pregnancy | `theevolvedgym.com.au/pregnancy-30dnnc-o` | `theevolvedgym.com.au/pregnancy-30dnnc-p` |
| Peri-Menopause | `theevolvedgym.com.au/perimenopause-30dnnc-o` | `theevolvedgym.com.au/perimenopause-30dnnc-p` |
| Post-Menopause | `theevolvedgym.com.au/post-menopause-30dnnc-o` | `theevolvedgym.com.au/post-menopause-30dnnc-p` |

**Existing personalisation engine (`homepage.js`):**
- `RC_GOALS` — 5 goal configs: lose-weight, recomp, bone-density, get-stronger, hyrox
- `RC_DECADES` — 5 decade configs: 20s, 30s, 40s, 50s, 60s
- `refresh()` — master update function called on every selection; updates: chart, profile panel, carousel order, video order, FAQ, pillars, profile bar, all CTA links, localStorage
- `rcUpdateCTALinks()` — rewrites all `a[href*="go.theevolvedgym.com.au/strength-assessment"]` with `?goal=&decade=&exp=` params
- `localStorage("evolved_profile")` — persists `{ goal, decade, exp }` across sessions

**Existing CTAs in page (all link to SA booking):**
- Line 75: Hero — "Book Your Strength Assessment"
- Line 206: How to Get Started — "Book Your Strength Assessment"
- Line 291: Sarcopenia chart — "See Where You Fall on This Curve"
- Line 318: Post-sarcopenia — "Book Your Strength Assessment"
- Line 966: Final CTA — dynamically updated by `rcUpdateFinalCTA()`
- Profile bar (bottom sticky) — "Book Assessment →"

**Current JS version:** 36.0 (functions.php)

### Gaps or Problems Being Addressed

1. **Goal not captured** — life stage selection fires navigation immediately; no goal dimension is collected
2. **Navigation abandons the page** — visitor leaves before seeing social proof, personalised projection, or any of the content built for their profile
3. **Personalisation engine is disconnected** — the homepage's `refresh()` system is never triggered by Pick Your Journey clicks
4. **GHL funnels receive cold traffic** — no profile context arrives with the visitor
5. **No mid-page conversion option** — if a visitor scrolls past Pick Your Journey without clicking, the next CTA is at the bottom of How to Get Started (line 206). No low-friction alternative for the "almost convinced" visitor.

---

## Proposed Changes

### Summary of Changes

- Replace the 5 navigate-away photo cards with a 2-step in-page selector (life stage → goal)
- Life stage selection maps to a decade and reveals the goal step — does NOT navigate away
- Goal selection calls `refresh()` to personalise the entire page
- A confirmation panel appears below the selector showing: personalised headline, matched member story snippet, and a CTA that routes to the appropriate GHL funnel with params
- Add `pyjSelectLifeStage()` and `pyjSelectGoal()` JS functions
- Add `rcUpdateWaitlistCTAs()` function for mid-page CTA copy updates
- Add 4 waitlist CTA blocks in HTML (after Why Muscle Matters, after Real Results Carousel, after Video Testimonials, after Google Reviews)
- All waitlist CTAs use a configurable URL and update their copy based on active profile
- Bump JS version to 37.0

### New Files to Create

None — all changes are to existing files.

### Files to Modify

| File | Changes |
|---|---|
| `/tmp/homepage-v5.html` | Replace Pick Your Journey section HTML; add 4 waitlist CTA blocks |
| `/tmp/homepage.js` | Add `pyjSelectLifeStage()`, `pyjSelectGoal()`, `rcUpdateWaitlistCTAs()`; call `rcUpdateWaitlistCTAs()` inside `refresh()`; bump version in deploy step |
| `/wp-content/themes/blocksy-child/functions.php` | Bump JS version 36.0 → 37.0 (via SSH sed) |

---

## Design Decisions

### Key Decisions Made

1. **All 5 goals available for every life stage** — no filtering. A pregnant woman may want bone density. A teenager may want body recomp. The gym doesn't assume intent; it asks.

2. **Life stage sets the decade; goal is user-chosen** — life stage maps to a default decade (see mapping below) which pre-sets the personalisation context. The goal is always explicitly selected by the user.

3. **Life stage photo cards preserved but become selectors** — the photos are part of what makes the section convert. They stay. The change is behavioral: clicking a card no longer navigates, it selects and reveals the goal step. A subtle "Select →" prompt replaces the invisible full-card overlay link.

4. **Goal tiles styled to match rc-goal-btn** — uses the same button style as the Results Curve goal selector for visual consistency and to prime visitors for the Results Curve interaction further down the page.

5. **Confirmation panel, not modal** — after both selections are made, a confirmation panel slides in below the selector (not a popup). It shows: a personalised one-line headline, the matched member story snippet (from `rcGetStory()`), and the CTA to the GHL funnel. This keeps the visitor on the page and curious to scroll.

6. **Waitlist CTAs link to the life-stage-specific landing pages, not a generic URL** — there is no single waitlist URL. There are 10: 5 life stages × 2 traffic sources (organic `-o` / paid `-p`). The waitlist CTAs therefore cannot link anywhere useful until a life stage is selected. Pre-selection state: CTAs show but prompt the visitor to pick a life stage first. Post-selection state: CTAs link to the correct life-stage page.

7. **Homepage is organic-only — always use `-o` URLs** — paid traffic goes directly to `-p` landing pages via ad links and never hits the homepage. No traffic source detection needed. All homepage CTAs hardcode `-o` page URLs.

8. **`rcUpdateCTALinks()` already handles all SA booking links** — the goal selection via Pick Your Journey will call `refresh()` which calls `rcUpdateCTALinks()`. The GHL landing page CTA in the confirmation panel uses the life stage URL (different domain), so it gets its params added separately in `pyjSelectGoal()`.

8. **Life stage → decade default mapping:**
   | Life Stage | Default Decade | Rationale |
   |---|---|---|
   | Teenager | 20s | Under 20, closest bracket |
   | 20-30s | 20s | Default to younger end; Results Curve can refine |
   | Pregnancy | 30s | Most pregnancies occur in 30s; hormonal context aligns |
   | Peri-Menopause | 40s | Typically 40-52; 40s is the most common bracket |
   | Post-Menopause | 60s | Most post-menopausal members are 55+; 60s best fit |

9. **`exp` (experience) is NOT set by Pick Your Journey** — it remains at the persisted or default value. The Results Curve is the right place to set experience level, not at the top of the page before the visitor has explored.

### Alternatives Considered

- **Full replacement with a grid selector (no photos)** — cleaner UI but discards the visual identification element that's been proven to convert. Rejected.
- **Filtering goals per life stage** — rejected by user. Every life stage gets every goal.
- **Navigate-away still as primary action** — rejected. The entire point is keeping visitors on the page to see the social proof and personalised content.

### Open Questions

1. **Experience level for Pick Your Journey selections** — Teenager and Pregnancy specifically may warrant forcing `exp = "new"` since those visitors are very likely new to strength training. Recommend defaulting these two life stages to `"new"` experience while leaving all others at persisted/default. Confirm before implementing Step 1.

---

## Step-by-Step Tasks

### Step 1: Add JS functions to `homepage.js`

Add three new functions to `homepage.js` before `initResultsChart()`:

**`PYJ_LIFE_STAGES` config object:**
```js
const PYJ_LIFE_STAGES = {
    "teenager":      { label: "Teenager",       decade: "20s", exp: "new", url: "https://theevolvedgym.com.au/teen-30dnnc-o"         },
    "20s30s":        { label: "20s – 30s",       decade: "20s", exp: null,  url: "https://theevolvedgym.com.au/20s30s-30dnnc-o"        },
    "pregnancy":     { label: "Pregnancy",       decade: "30s", exp: "new", url: "https://theevolvedgym.com.au/pregnancy-30dnnc-o"     },
    "perimenopause": { label: "Peri-Menopause",  decade: "40s", exp: null,  url: "https://theevolvedgym.com.au/perimenopause-30dnnc-o" },
    "postmenopause": { label: "Post-Menopause",  decade: "60s", exp: null,  url: "https://theevolvedgym.com.au/post-menopause-30dnnc-o"},
};

function pyjLandingUrl(stage, goalId) {
    return stage.url + "?goal=" + encodeURIComponent(goalId) + "&decade=" + encodeURIComponent(stage.decade);
}
```

**`pyjSelectLifeStage(stageId)`:**
```js
function pyjSelectLifeStage(stageId) {
    const stage = PYJ_LIFE_STAGES[stageId];
    if (!stage) return;

    // Visual: highlight selected life stage tile
    document.querySelectorAll(".pyj-stage-btn").forEach(btn => {
        const on = btn.dataset.stage === stageId;
        btn.style.border    = on ? "2px solid #e43388" : "2px solid transparent";
        btn.style.transform = on ? "scale(1.03)" : "scale(1)";
        btn.querySelector(".pyj-check").style.display = on ? "block" : "none";
    });

    // Store selected stage on the section element for use in pyjSelectGoal
    const section = document.getElementById("pyj-section");
    if (section) section.dataset.activeStage = stageId;

    // Show the goal selection step with animation
    const goalStep = document.getElementById("pyj-goal-step");
    if (goalStep && goalStep.style.display === "none") {
        goalStep.style.display = "block";
        gsap.fromTo(goalStep, { opacity: 0, y: 16 }, { opacity: 1, y: 0, duration: 0.5, ease: "power3.out" });
    }

    // Hide confirmation panel if re-selecting life stage
    const confirm = document.getElementById("pyj-confirm");
    if (confirm) confirm.style.display = "none";
}
```

**`pyjSelectGoal(goalId)`:**
```js
function pyjSelectGoal(goalId) {
    const section    = document.getElementById("pyj-section");
    const stageId    = section ? section.dataset.activeStage : null;
    const stage      = PYJ_LIFE_STAGES[stageId];
    if (!stage) return;

    // Visual: highlight selected goal tile
    document.querySelectorAll(".pyj-goal-btn").forEach(btn => {
        const on = btn.dataset.goal === goalId;
        btn.style.background = on ? "#e43388"  : "transparent";
        btn.style.color      = on ? "#fff"      : "#f5f0eb";
        btn.style.border     = on ? "2px solid #e43388" : "2px solid #333";
    });

    // Set the active profile via the Results Curve variables
    // We dispatch a custom event that initResultsChart() listens for
    document.dispatchEvent(new CustomEvent("pyj:profileSet", {
        detail: {
            goal:   goalId,
            decade: stage.decade,
            exp:    stage.exp  // null = keep existing persisted value
        }
    }));

    // Build the confirmation CTA URL — routes to correct organic or paid landing page
    const ctaUrl = pyjLandingUrl(stage, goalId);

    // Build personalised confirmation copy
    const goalCfg    = RC_GOALS.find(g => g.id === goalId);
    const goalLabel  = goalCfg ? goalCfg.label : goalId;
    const story      = rcGetStory(goalId, stage.decade);
    const headlineTpl = {
        "teenager":      "Your strength journey starts here.",
        "20s30s":        "Your path is set. Here's what's possible.",
        "pregnancy":     "Train smart. Stay strong. Come back stronger.",
        "perimenopause": "Perimenopause changes your body. Strength training changes it back.",
        "postmenopause": "Your strongest chapter starts now.",
    };
    const headline = headlineTpl[stageId] || "Your path is set.";

    // Populate and show confirmation panel
    const confirm = document.getElementById("pyj-confirm");
    if (confirm) {
        const h3    = document.getElementById("pyj-confirm-h3");
        const sub   = document.getElementById("pyj-confirm-sub");
        const btn   = document.getElementById("pyj-confirm-cta");
        const scroll = document.getElementById("pyj-scroll-hint");
        if (h3)    h3.textContent    = headline;
        if (sub && story) sub.innerHTML = "<strong>" + story.name + ":</strong> " + story.blurb;
        if (btn) {
            btn.href        = ctaUrl;
            btn.textContent = "See the " + stage.label + " path \u2192";
        }
        confirm.style.display = "block";
        gsap.fromTo(confirm, { opacity: 0, y: 16 }, { opacity: 1, y: 0, duration: 0.5, ease: "power3.out" });
        if (scroll) {
            gsap.fromTo(scroll, { opacity: 0 }, { opacity: 1, duration: 0.6, delay: 0.6 });
        }
    }
}
```

**`rcUpdateWaitlistCTAs(goalId, decade)`:**

Waitlist CTAs link to the life-stage-specific landing page (organic or paid variant), not a generic URL. If no life stage has been selected yet (no `activeStage` on the section element), CTAs show a prompt to pick a life stage first.

```js
function rcUpdateWaitlistCTAs(goalId, decade) {
    const section     = document.getElementById("pyj-section");
    const activeStage = section ? section.dataset.activeStage : null;
    const stage       = activeStage ? PYJ_LIFE_STAGES[activeStage] : null;

    document.querySelectorAll(".waitlist-cta-btn").forEach(btn => {
        if (stage) {
            btn.href        = pyjLandingUrl(stage, goalId);
            btn.textContent = "Join the " + stage.label + " waitlist \u2192";
            btn.style.opacity       = "1";
            btn.style.pointerEvents = "auto";
        } else {
            // No stage selected yet — prompt to scroll up and pick
            btn.href        = "#pyj-section";
            btn.textContent = "Choose your stage to join the waitlist \u2191";
            btn.style.opacity       = "0.6";
            btn.style.pointerEvents = "auto";
        }
    });
}
```

**Wire `pyj:profileSet` event listener inside `initResultsChart()`:**
Add after the existing button event listeners but before the final `refresh()` call:
```js
document.addEventListener("pyj:profileSet", function(e) {
    const { goal, decade, exp } = e.detail;
    if (goal   && RC_GOALS.find(g => g.id === goal))   activeGoal   = goal;
    if (decade && RC_DECADES[decade])                  activeDecade = decade;
    if (exp    && RC_EXPERIENCE[exp])                  activeExperience = exp;
    syncBtnStates();
    refresh();
    // Soft-scroll to sarcopenia chart so the personalisation is immediately visible
    const chart = document.getElementById("sarcopeniaChart");
    if (chart) chart.scrollIntoView({ behavior: "smooth", block: "center" });
});
```

**Add `rcUpdateWaitlistCTAs` call inside `refresh()`:**
```js
rcUpdateWaitlistCTAs(activeGoal, activeDecade);
```

**Files affected:**
- `/tmp/homepage.js`

---

### Step 2: Replace Pick Your Journey HTML

Replace the entire `<!-- PICK YOUR JOURNEY -->` section (lines 104–148) in `homepage-v5.html`.

**New section structure:**

```html
<!-- PICK YOUR JOURNEY -->
<section id="pyj-section" style="background:#0a0a0a;padding:80px 0;">
<div style="max-width:960px;margin:0 auto;padding:0 24px;">

  <!-- Heading (unchanged) -->
  <h2 data-reveal="fade-up" style="font-family:'PT Serif Caption',serif;font-size:clamp(1.5rem,3vw,2.2rem);color:#f5f0eb;margin-bottom:12px;text-align:center;">Choose the stage you're in &amp; we'll guide you from there.</h2>
  <p data-reveal="fade-up" data-reveal-delay="0.1" style="color:#aaa;margin-bottom:48px;max-width:600px;margin-left:auto;margin-right:auto;text-align:center;">Our programs are designed for women and built on research, not random workouts. <strong style="color:#e43388;">No fads. No contracts.</strong> <em><strong>Just real results.</strong></em></p>

  <!-- STEP 1: Life Stage Cards -->
  <p style="color:#555;font-size:0.72rem;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:20px;text-align:center;">Step 1 — Which stage are you in?</p>
  <div style="display:flex;gap:8px;overflow-x:auto;-webkit-overflow-scrolling:touch;padding-bottom:4px;">

    <!-- Teenager -->
    <div class="pyj-stage-btn" data-stage="teenager" onclick="pyjSelectLifeStage('teenager')"
         style="position:relative;flex:1 1 0;min-width:160px;border-radius:8px;overflow:hidden;cursor:pointer;border:2px solid transparent;transition:border 0.25s,transform 0.25s;">
      <img src="https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/684f94e224f68255bceeddb4.png" alt="Teenager strength training" style="width:100%;height:360px;object-fit:cover;display:block;">
      <div style="background:#e43388;padding:12px 16px;text-align:center;"><strong style="color:#fff;font-size:0.8rem;text-transform:uppercase;letter-spacing:0.12em;">Teenager</strong></div>
      <div style="background:#f4c2d8;padding:10px 16px;text-align:center;"><span style="color:#6b0030;font-size:0.72rem;text-transform:uppercase;letter-spacing:0.08em;font-weight:600;">Start Smart &amp; Strong</span></div>
      <div class="pyj-check" style="display:none;position:absolute;top:10px;right:10px;background:#e43388;color:#fff;border-radius:50%;width:24px;height:24px;font-size:0.9rem;line-height:24px;text-align:center;">&#10003;</div>
    </div>

    <!-- 20s-30s -->
    <div class="pyj-stage-btn" data-stage="20s30s" onclick="pyjSelectLifeStage('20s30s')"
         style="position:relative;flex:1 1 0;min-width:160px;border-radius:8px;overflow:hidden;cursor:pointer;border:2px solid transparent;transition:border 0.25s,transform 0.25s;">
      <img src="https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/684f94e2653a2c0a48193159.png" alt="20s and 30s strength training" style="width:100%;height:360px;object-fit:cover;display:block;">
      <div style="background:#e43388;padding:12px 16px;text-align:center;"><strong style="color:#fff;font-size:0.8rem;text-transform:uppercase;letter-spacing:0.12em;">20&#8211;30&#8217;s</strong></div>
      <div style="background:#f4c2d8;padding:10px 16px;text-align:center;"><span style="color:#6b0030;font-size:0.72rem;text-transform:uppercase;letter-spacing:0.08em;font-weight:600;">Look Fit &amp; Feel Strong</span></div>
      <div class="pyj-check" style="display:none;position:absolute;top:10px;right:10px;background:#e43388;color:#fff;border-radius:50%;width:24px;height:24px;font-size:0.9rem;line-height:24px;text-align:center;">&#10003;</div>
    </div>

    <!-- Pregnancy -->
    <div class="pyj-stage-btn" data-stage="pregnancy" onclick="pyjSelectLifeStage('pregnancy')"
         style="position:relative;flex:1 1 0;min-width:160px;border-radius:8px;overflow:hidden;cursor:pointer;border:2px solid transparent;transition:border 0.25s,transform 0.25s;">
      <img src="https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/684f94e255f965da3724b416.png" alt="Pregnancy strength training" style="width:100%;height:360px;object-fit:cover;display:block;">
      <div style="background:#e43388;padding:12px 16px;text-align:center;"><strong style="color:#fff;font-size:0.8rem;text-transform:uppercase;letter-spacing:0.12em;">Pregnancy</strong></div>
      <div style="background:#f4c2d8;padding:10px 16px;text-align:center;"><span style="color:#6b0030;font-size:0.72rem;text-transform:uppercase;letter-spacing:0.08em;font-weight:600;">Train for Motherhood</span></div>
      <div class="pyj-check" style="display:none;position:absolute;top:10px;right:10px;background:#e43388;color:#fff;border-radius:50%;width:24px;height:24px;font-size:0.9rem;line-height:24px;text-align:center;">&#10003;</div>
    </div>

    <!-- Peri-Menopause -->
    <div class="pyj-stage-btn" data-stage="perimenopause" onclick="pyjSelectLifeStage('perimenopause')"
         style="position:relative;flex:1 1 0;min-width:160px;border-radius:8px;overflow:hidden;cursor:pointer;border:2px solid transparent;transition:border 0.25s,transform 0.25s;">
      <img src="https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/684f94e2bb12536fee9bb3bd.png" alt="Perimenopause strength training" style="width:100%;height:360px;object-fit:cover;display:block;">
      <div style="background:#e43388;padding:12px 16px;text-align:center;"><strong style="color:#fff;font-size:0.8rem;text-transform:uppercase;letter-spacing:0.12em;">Peri-Menopause</strong></div>
      <div style="background:#f4c2d8;padding:10px 16px;text-align:center;"><span style="color:#6b0030;font-size:0.72rem;text-transform:uppercase;letter-spacing:0.08em;font-weight:600;">Balance Body &amp; Build Strength</span></div>
      <div class="pyj-check" style="display:none;position:absolute;top:10px;right:10px;background:#e43388;color:#fff;border-radius:50%;width:24px;height:24px;font-size:0.9rem;line-height:24px;text-align:center;">&#10003;</div>
    </div>

    <!-- Post-Menopause -->
    <div class="pyj-stage-btn" data-stage="postmenopause" onclick="pyjSelectLifeStage('postmenopause')"
         style="position:relative;flex:1 1 0;min-width:160px;border-radius:8px;overflow:hidden;cursor:pointer;border:2px solid transparent;transition:border 0.25s,transform 0.25s;">
      <img src="https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/684f94e2bb12535c329bb3be.png" alt="Post-menopause strength training" style="width:100%;height:360px;object-fit:cover;display:block;">
      <div style="background:#e43388;padding:12px 16px;text-align:center;"><strong style="color:#fff;font-size:0.8rem;text-transform:uppercase;letter-spacing:0.12em;">Post-Menopause</strong></div>
      <div style="background:#f4c2d8;padding:10px 16px;text-align:center;"><span style="color:#6b0030;font-size:0.72rem;text-transform:uppercase;letter-spacing:0.08em;font-weight:600;">Feel Younger Again</span></div>
      <div class="pyj-check" style="display:none;position:absolute;top:10px;right:10px;background:#e43388;color:#fff;border-radius:50%;width:24px;height:24px;font-size:0.9rem;line-height:24px;text-align:center;">&#10003;</div>
    </div>

  </div><!-- end stage cards -->

  <!-- STEP 2: Goal Selection (hidden until step 1 complete) -->
  <div id="pyj-goal-step" style="display:none;margin-top:40px;">
    <p style="color:#555;font-size:0.72rem;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:20px;text-align:center;">Step 2 — What's your primary goal?</p>
    <div style="display:flex;flex-wrap:wrap;gap:10px;justify-content:center;">
      <button class="pyj-goal-btn" data-goal="lose-weight"  onclick="pyjSelectGoal('lose-weight')"  style="background:transparent;color:#f5f0eb;border:2px solid #333;border-radius:4px;padding:12px 20px;font-family:'Lato',sans-serif;font-size:0.85rem;font-weight:700;cursor:pointer;letter-spacing:0.04em;transition:all 0.2s;">Lose Weight</button>
      <button class="pyj-goal-btn" data-goal="recomp"       onclick="pyjSelectGoal('recomp')"       style="background:transparent;color:#f5f0eb;border:2px solid #333;border-radius:4px;padding:12px 20px;font-family:'Lato',sans-serif;font-size:0.85rem;font-weight:700;cursor:pointer;letter-spacing:0.04em;transition:all 0.2s;">Lose Fat &amp; Gain Muscle</button>
      <button class="pyj-goal-btn" data-goal="get-stronger" onclick="pyjSelectGoal('get-stronger')" style="background:transparent;color:#f5f0eb;border:2px solid #333;border-radius:4px;padding:12px 20px;font-family:'Lato',sans-serif;font-size:0.85rem;font-weight:700;cursor:pointer;letter-spacing:0.04em;transition:all 0.2s;">Get Stronger</button>
      <button class="pyj-goal-btn" data-goal="bone-density" onclick="pyjSelectGoal('bone-density')" style="background:transparent;color:#f5f0eb;border:2px solid #333;border-radius:4px;padding:12px 20px;font-family:'Lato',sans-serif;font-size:0.85rem;font-weight:700;cursor:pointer;letter-spacing:0.04em;transition:all 0.2s;">Stronger Bones</button>
      <button class="pyj-goal-btn" data-goal="hyrox"        onclick="pyjSelectGoal('hyrox')"        style="background:transparent;color:#f5f0eb;border:2px solid #333;border-radius:4px;padding:12px 20px;font-family:'Lato',sans-serif;font-size:0.85rem;font-weight:700;cursor:pointer;letter-spacing:0.04em;transition:all 0.2s;">Train for HYROX</button>
    </div>
  </div>

  <!-- Confirmation Panel (hidden until step 2 complete) -->
  <div id="pyj-confirm" style="display:none;margin-top:40px;background:#0d0d0d;border:1px solid #222;border-radius:8px;padding:32px;">
    <h3 id="pyj-confirm-h3" style="font-family:'PT Serif Caption',serif;color:#f5f0eb;font-size:1.2rem;margin-bottom:12px;"></h3>
    <p id="pyj-confirm-sub" style="color:#aaa;font-size:0.88rem;line-height:1.7;margin-bottom:28px;"></p>
    <div style="display:flex;align-items:center;gap:16px;flex-wrap:wrap;">
      <a id="pyj-confirm-cta" href="#" style="background:#e43388;color:#fff;padding:14px 28px;border-radius:4px;font-family:'Lato',sans-serif;font-size:0.9rem;font-weight:700;text-decoration:none;letter-spacing:0.04em;">See your path &#8594;</a>
      <span id="pyj-scroll-hint" style="color:#555;font-size:0.8rem;opacity:0;">or keep scrolling to see what's possible &#8595;</span>
    </div>
  </div>

</div>
</section>
```

**Files affected:**
- `/tmp/homepage-v5.html`

---

### Step 3: Add waitlist CTA blocks to HTML

Add 4 waitlist CTA blocks at the end of these sections. Each block is a minimal dark strip with a single `<a class="waitlist-cta-btn">`.

**Shared block template** (adapt text per position):
```html
<div style="background:#0d0d0d;border-top:1px solid #1a1a1a;padding:40px 24px;text-align:center;">
  <p style="color:#aaa;font-size:0.88rem;margin-bottom:16px;">Limited spots available each month.</p>
  <a class="waitlist-cta-btn" href="https://go.theevolvedgym.com.au/waitlist" style="display:inline-block;border:2px solid #e43388;color:#e43388;padding:12px 28px;border-radius:4px;font-family:'Lato',sans-serif;font-size:0.85rem;font-weight:700;text-decoration:none;letter-spacing:0.04em;transition:all 0.2s;">Join the Waitlist &#8594;</a>
</div>
```

**Placement:**
1. After `<!-- WHY MUSCLE MATTERS -->` section close (`</section>`, line ~322 after chart CTA)
2. After `<!-- REAL RESULTS — CAROUSEL -->` section close (after the carousel `</section>`)
3. After `<!-- VIDEO TESTIMONIALS -->` section close
4. After `<!-- GOOGLE REVIEWS -->` section close

The `rcUpdateWaitlistCTAs()` function (added in Step 1) will dynamically update the `href` and `textContent` of every `.waitlist-cta-btn` on each `refresh()` call.

**Files affected:**
- `/tmp/homepage-v5.html`

---

### Step 4: Add mobile CSS

Add to the `<style>` block at the top of `homepage-v5.html` (inside the existing `@media (max-width: 640px)` block):

```css
/* PYJ mobile */
.pyj-stage-btn img { height: 260px !important; }
#pyj-goal-step button { font-size: 0.8rem !important; padding: 10px 14px !important; }
#pyj-confirm { padding: 24px 16px !important; }
#pyj-confirm-h3 { font-size: 1rem !important; }
```

**Files affected:**
- `/tmp/homepage-v5.html`

---

### Step 5: Deploy `homepage.js`

```bash
scp -P 18765 -i ~/.ssh/siteground-evolved /tmp/homepage.js \
  u2424-sxatvnipapmi@gsydm1063.siteground.biz:/home/u2424-sxatvnipapmi/www/blog.theevolvedgym.com.au/public_html/wp-content/themes/blocksy-child/js/homepage.js
```

Bump version 36.0 → 37.0 and flush caches:
```bash
ssh -p 18765 -i ~/.ssh/siteground-evolved u2424-sxatvnipapmi@gsydm1063.siteground.biz "
  cd '/home/u2424-sxatvnipapmi/www/blog.theevolvedgym.com.au/public_html'
  sed -i 's/\"36\.0\"/\"37.0\"/' wp-content/themes/blocksy-child/functions.php
  wp cache flush && wp transient delete --all && wp sg purge
"
```

---

### Step 6: Deploy `homepage-v5.html`

```bash
scp -P 18765 -i ~/.ssh/siteground-evolved /tmp/homepage-v5.html \
  u2424-sxatvnipapmi@gsydm1063.siteground.biz:/home/u2424-sxatvnipapmi/www/blog.theevolvedgym.com.au/public_html/homepage-v5.html

ssh -p 18765 -i ~/.ssh/siteground-evolved u2424-sxatvnipapmi@gsydm1063.siteground.biz "
  cd '/home/u2424-sxatvnipapmi/www/blog.theevolvedgym.com.au/public_html'
  wp eval 'global \$wpdb; \$wpdb->update(\$wpdb->posts, [\"post_content\" => file_get_contents(\"/home/u2424-sxatvnipapmi/www/blog.theevolvedgym.com.au/public_html/homepage-v5.html\")], [\"ID\" => 165]);'
  wp cache flush && wp transient delete --all && wp sg purge
"
```

---

### Step 7: Validation

Verify live at `https://theevolvedgym.com.au`:

1. Life stage cards display as before (photos visible, no blank areas)
2. Clicking a life stage card does NOT navigate away — goal step slides in below
3. Selected life stage card shows pink border + checkmark
4. All 5 goal buttons appear regardless of which life stage was selected
5. Selecting a goal triggers page personalisation (profile bar appears, heading updates)
6. Confirmation panel shows: personalised headline, matched member story, CTA button
7. Confirmation CTA link contains `?goal=&decade=&stage=` params
8. Scrolling down: video carousel order reflects goal/decade selection
9. Results Curve (position 12): decade and goal pre-match the Pick Your Journey selection
10. 4 waitlist CTA blocks visible at correct positions
11. Waitlist CTA text updates after goal selection
12. Mobile: cards scroll horizontally, goal buttons wrap, confirmation panel readable

---

## Connections & Dependencies

### Files That Reference This Area

- `plans/2026-04-30-homepage-animation-redesign.md` — tracks Tier 3 & 4 personalisation status
- `context/` — no direct references to Pick Your Journey
- The 5 GHL funnel pages (`theevolvedgym.com.au/teen-30dnnc-o` etc.) — remain unchanged; they are now the downstream endpoint for warm, pre-qualified visitors

### Updates Needed for Consistency

- `plans/2026-04-30-homepage-animation-redesign.md` — update status to reflect Pick Your Journey is now part of the personalisation system
- If/when the GHL funnel pages are updated to consume `{{params.goal}}` and `{{params.stage}}`, those pages will need conditional content blocks matching the goal options

### Impact on Existing Workflows

- The existing `refresh()` function is called by Pick Your Journey via `pyj:profileSet` event — no changes to `refresh()` itself
- The `rcUpdateCTALinks()` function already handles all SA booking links — the confirmation panel CTA routes to the GHL funnel (different URL), so it gets params separately in `pyjSelectGoal()`
- localStorage profile persistence means: if a returning visitor has a profile saved, the Results Curve will show their saved profile — but the Pick Your Journey section will show no pre-selected state (by design; they should re-select to update if desired)

---

## Validation Checklist

- [ ] Life stage cards no longer navigate on click — goal step appears instead
- [ ] All 5 goal buttons visible for every life stage
- [ ] Profile bar appears after goal selection
- [ ] Confirmation panel headline matches the selected life stage
- [ ] Confirmation CTA URL contains goal + decade + stage params
- [ ] Scrolling to video carousel: videos are reordered by selection
- [ ] Scrolling to Results Curve: decade pre-matches life stage mapping
- [ ] 4 waitlist CTA blocks present at the correct sections
- [ ] Waitlist CTA `href` updates after goal selection
- [ ] Mobile horizontal scroll on life stage cards works
- [ ] Mobile goal buttons wrap cleanly on small screens
- [ ] No console errors on load or interaction
- [ ] JS v37.0 confirmed in browser DevTools Network tab

---

## Success Criteria

1. A visitor can select their life stage and goal without leaving the homepage, and the page visibly personalises around their selection
2. Clicking the confirmation CTA routes to the correct GHL funnel page with `?goal=&decade=&stage=` params in the URL
3. Four waitlist CTA blocks are visible at key scroll positions and update their copy after profile selection

---

## Notes

- **Homepage is organic-only** — paid traffic goes directly to `-p` pages via ad links. The homepage always uses `-o` URLs. If this assumption ever changes (e.g. a paid campaign links to the homepage), the `PYJ_LIFE_STAGES` config and `pyjLandingUrl()` are the only places that need updating.
- **GHL landing pages receive `?goal=&decade=` params** — these are new. The existing GHL forms will ignore unknown params, so this is safe immediately. Future improvement: add GHL conditional content blocks on each landing page reading `{{params.goal}}` to personalise the headline and member story on arrival. This turns the warm handoff into a warm landing.
- **Waitlist CTA pre-selection state** — before a life stage is picked, the mid-page waitlist buttons show "Choose your stage to join the waitlist ↑" and anchor back to the PYJ section. This nudges the visitor back up to complete step 1 rather than dead-ending. After selection they update to the correct life-stage link.
- **Teenager + Pregnancy exp default** — these two life stages force `exp: "new"` which highlights the FastTrack membership and shows a higher-gradient results projection. Appropriate since these visitors are almost always new to structured strength training.

---

## Implementation Notes

**Implemented:** 2026-05-03

### Summary

- Added `PYJ_LIFE_STAGES` config, `pyjLandingUrl()`, `pyjSelectLifeStage()`, `pyjSelectGoal()`, and `rcUpdateWaitlistCTAs()` to `/tmp/homepage.js` before `initResultsChart()`
- Added `pyj:profileSet` CustomEvent listener inside `initResultsChart()` closure to bridge PYJ selections into the Results Curve personalisation engine
- Added `rcUpdateWaitlistCTAs()` call inside `refresh()` so waitlist CTA links update on every profile change
- Replaced static Pick Your Journey cards with two-step in-page selector (life stage → goal) in `/tmp/homepage-v5.html`
- Added confirmation panel with personalised headline, member story snippet, and CTA link to correct GHL organic landing page with `?goal=&decade=` params
- Added 4 waitlist CTA blocks: after Why Muscle Matters, Real Results Carousel, Video Testimonials, Google Reviews
- Added mobile CSS for PYJ stage images, goal buttons, and confirmation panel
- Deployed `homepage.js` via SCP to SiteGround, bumped version 36.0 → 37.0 in `functions.php`
- Deployed `homepage-v5.html` to WordPress post ID 165 via `wp eval`, flushed all caches

### Deviations from Plan

- Removed UTM-based organic/paid routing — user confirmed paid traffic never hits the homepage. All PYJ URLs hardcoded to `-o` organic landing pages.
- `rcUpdateWaitlistCTAs()` takes `(goalId, decade)` rather than the full stage object, for simpler integration with the `refresh()` call signature.

### Issues Encountered

- Initial Edit tool match for waitlist CTA after Real Results Carousel was ambiguous (two sections shared the same closing pattern). Resolved by including the next section's comment as disambiguating context in `old_string`.
- **Future: auto-select life stage from URL param** — if Instagram/Facebook ads link directly to the homepage with `?stage=perimenopause`, the Pick Your Journey section can read this on load and auto-select + skip to the goal step. Not in scope now but easy to add given the architecture.
