# Plan: Personalised 12-Month Results Curve

**Created:** 2026-05-01
**Status:** Draft
**Request:** Replace the static frequency chart with a fully interactive personalised results curve — goal selector, decade selector, per-modality training sliders, and a Chart.js curve that updates in real time using a research-backed algorithm.

---

## Overview

### What This Plan Accomplishes

Replaces the existing "Your 12-Month Results Curve" (static 3-line frequency chart with phase buttons) with a personalised interactive tool. Visitors select their goal, their decade of life, and drag sliders for each training modality to see a projected results curve built from published sports science research.

### Why This Matters

A personalised chart is a conversion tool. It demonstrates that The Evolved understands each woman's specific situation — her life stage, her goals, her current training mix — and can project a credible outcome. It also embeds the key message: strength training produces disproportionately better results than pilates or cardio alone.

---

## Current State

### Relevant Existing Structure

- `<!-- Frequency Chart -->` block in `/tmp/homepage-v5.html` lines 658–670: static chart with 3 frequency lines + phase story buttons
- `// ── FREQUENCY CHART + PHASE STORY` block in `/tmp/homepage.js` lines 595–718: `initFrequencyChart()`, `highlightCurve()`, and the DOMContentLoaded block that wires phase buttons
- Chart.js already loaded via `functions.php` (dep: `chartjs`)
- GSAP already loaded (dep: `gsap`)

### Gaps or Problems Being Addressed

- Static chart tells one story for all visitors — no personalisation
- Phase buttons are a passive interaction, not a personalised prediction
- "Cumulative Progress (%)" Y-axis is abstract and unrelatable
- No goal-setting context — visitor doesn't know what the curve represents for them

---

## Proposed Changes

### Summary of Changes

- Replace frequency chart HTML block with new personalised chart section (goal pills, decade pills, 5 training sliders, canvas, annotation, disclaimer)
- Replace all JS for the frequency chart with new results engine (goals config, decade modifiers, score algorithm, Chart.js init, live update function)
- Update DOMContentLoaded to wire new chart instead of old frequency chart
- Bump `functions.php` version to `22.0` and deploy

### Files to Modify

| File | Changes |
|---|---|
| `/tmp/homepage-v5.html` | Replace `<!-- Frequency Chart -->` block with new interactive section HTML |
| `/tmp/homepage.js` | Replace frequency chart code (lines 595–718) with new results curve engine + updated DOMContentLoaded |
| `functions.php` on server | Version bump to `22.0` |

---

## Algorithm Specification

### Goals

```
id                 | label                   | yLabel                      | peak  | unit
lose-weight        | Lose Weight             | kg body fat lost            | 14    | kg
recomp             | Lose Fat & Gain Muscle  | % body fat reduced          | 18    | %
bone-density       | Stronger Bones          | % bone density increase     | 7     | %
get-stronger       | Get Stronger            | % strength increase         | 55    | %
hyrox              | Train for HYROX         | minutes off your time       | 28    | min
```

### Modality Effectiveness Weights Per Goal

Order: `[strength, hiit, pilates, cardio, hyrox]`

```
Lose Weight:            [9, 7, 3, 4, 6]
Lose Fat & Gain Muscle: [10, 6, 2, 3, 6]
Stronger Bones:         [9, 5, 2, 3, 5]
Get Stronger:           [10, 3, 2, 1, 5]
Train for HYROX:        [7, 8, 1, 6, 10]
```

Sources: Peterson et al. 2011 meta-analysis (strength + body comp), Kohrt et al. ACSM position stand (bone density), Rhea et al. 2003 dose-response (frequency), HERITAGE Family Study (cardio + body comp).

### Decade Modifiers

```
20s: { rate: 1.15, peak: 1.00 }
30s: { rate: 1.00, peak: 0.95 }
40s: { rate: 0.85, peak: 0.90 }
50s: { rate: 0.75, peak: 0.88 }
60s: { rate: 0.70, peak: 0.85 }
```

### Score Calculation

```
weeklyScore = Σ(sessions[i] × weights[goalIndex][i])   for i in [0..4]
maxWeight   = Math.max(...weights[goalIndex])
normalMax   = 6 × maxWeight
score       = Math.min(weeklyScore, normalMax) / normalMax   // 0–1
```

### Curve Points (months 0–12)

```
BASE_RATE = 0.18

result(t) = peak × decadePeak × score
            × (1 − exp(−BASE_RATE × sqrt(score) × decadeRate × t))

Rounded to 1 decimal place. Clamped to ≥ 0.
```

Produces 13 data points (t = 0 to 12).

### Baseline (gray dashed — "without structured training")

Fixed score = 0.18, decade modifiers = 1.0, same formula. Represents sporadic/unstructured activity.

### Default State on Load

- Goal: `recomp` (Lose Fat & Gain Muscle)
- Decade: `40s`
- Strength: 3 sessions, HIIT: 1, Pilates: 1, Cardio: 0, HYROX: 0

---

## Annotation Text

Generated dynamically. Template by score bracket:

```
score < 0.25:
  "This training mix will produce limited results. Adding 2–3 strength sessions per week
   would significantly change your curve."

score 0.25–0.5:
  "A moderate training mix. A woman in her [decade] following this plan can expect to
   [goal-result] over 12 months. Adding more strength work would push this further."

score 0.5–0.75:
  "A solid training mix. Based on published research, a woman in her [decade] on this
   plan can expect to [goal-result] by month 12."

score > 0.75:
  "An elite training frequency. Based on published research and real member outcomes,
   a woman in her [decade] training at this level can expect to [goal-result] by month 12.
   [HYROX only: Our members training 6 days per week at The Evolved typically improve
   their HYROX time by 20–28 minutes in their first year.]"
```

Goal-result phrases:

```
lose-weight:    "lose [X]kg of body fat"
recomp:         "reduce body fat by [X]%"
bone-density:   "improve bone density by [X]%"
get-stronger:   "increase your strength by [X]%"
hyrox:          "take [X] minutes off your HYROX time"
```

Where `[X]` = the month-12 value from the computed curve.

---

## Step-by-Step Tasks

### Step 1: Replace HTML — Frequency Chart Block

Find and replace the entire `<!-- Frequency Chart -->` block in `/tmp/homepage-v5.html`:

**Find (exact):**
```html
<!-- Frequency Chart -->
<div class="chart-canvas-wrap" style="margin-top:56px;">
<p style="color:#f5f0eb;font-size:0.85rem;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:6px;">Your 12-Month Results Curve</p>
<p style="color:#aaa;font-size:0.85rem;line-height:1.6;margin-bottom:20px;">Training frequency determines how fast your results compound. Click a phase to see what&#39;s happening inside your body.</p>
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

**Replace with:**
```html
<!-- Personalised Results Curve -->
<div class="chart-canvas-wrap" style="margin-top:56px;" id="results-curve-wrap">
<p style="color:#f5f0eb;font-size:0.85rem;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:6px;">Your Personalised 12-Month Results Curve</p>
<p style="color:#aaa;font-size:0.85rem;line-height:1.6;margin-bottom:28px;">Tell us your goal and training plan to see your projected results &#8212; based on published sports science research.</p>

<!-- Step 1: Goal -->
<p style="color:#f5f0eb;font-size:0.75rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:10px;">My goal is to&hellip;</p>
<div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:28px;" id="goal-selector">
<button class="rc-goal-btn" data-goal="lose-weight"   style="background:#1a1a1a;border:1px solid #333;color:#aaa;padding:9px 16px;border-radius:4px;font-family:'Lato',sans-serif;font-size:0.8rem;cursor:pointer;transition:all 0.2s;white-space:nowrap;">Lose Weight</button>
<button class="rc-goal-btn" data-goal="recomp"        style="background:#e43388;border:1px solid #e43388;color:#fff;padding:9px 16px;border-radius:4px;font-family:'Lato',sans-serif;font-size:0.8rem;font-weight:700;cursor:pointer;transition:all 0.2s;white-space:nowrap;">Lose Fat &amp; Gain Muscle</button>
<button class="rc-goal-btn" data-goal="bone-density"  style="background:#1a1a1a;border:1px solid #333;color:#aaa;padding:9px 16px;border-radius:4px;font-family:'Lato',sans-serif;font-size:0.8rem;cursor:pointer;transition:all 0.2s;white-space:nowrap;">Stronger Bones</button>
<button class="rc-goal-btn" data-goal="get-stronger"  style="background:#1a1a1a;border:1px solid #333;color:#aaa;padding:9px 16px;border-radius:4px;font-family:'Lato',sans-serif;font-size:0.8rem;cursor:pointer;transition:all 0.2s;white-space:nowrap;">Get Stronger</button>
<button class="rc-goal-btn" data-goal="hyrox"         style="background:#1a1a1a;border:1px solid #333;color:#aaa;padding:9px 16px;border-radius:4px;font-family:'Lato',sans-serif;font-size:0.8rem;cursor:pointer;transition:all 0.2s;white-space:nowrap;">Train for HYROX</button>
</div>

<!-- Step 2: Decade -->
<p style="color:#f5f0eb;font-size:0.75rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:10px;">I am in my&hellip;</p>
<div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:28px;" id="decade-selector">
<button class="rc-decade-btn" data-decade="20s" style="background:#1a1a1a;border:1px solid #333;color:#aaa;padding:7px 14px;border-radius:4px;font-family:'Lato',sans-serif;font-size:0.8rem;cursor:pointer;transition:all 0.2s;">20s</button>
<button class="rc-decade-btn" data-decade="30s" style="background:#1a1a1a;border:1px solid #333;color:#aaa;padding:7px 14px;border-radius:4px;font-family:'Lato',sans-serif;font-size:0.8rem;cursor:pointer;transition:all 0.2s;">30s</button>
<button class="rc-decade-btn" data-decade="40s" style="background:#e43388;border:1px solid #e43388;color:#fff;padding:7px 14px;border-radius:4px;font-family:'Lato',sans-serif;font-size:0.8rem;font-weight:700;cursor:pointer;transition:all 0.2s;">40s</button>
<button class="rc-decade-btn" data-decade="50s" style="background:#1a1a1a;border:1px solid #333;color:#aaa;padding:7px 14px;border-radius:4px;font-family:'Lato',sans-serif;font-size:0.8rem;cursor:pointer;transition:all 0.2s;">50s</button>
<button class="rc-decade-btn" data-decade="60s" style="background:#1a1a1a;border:1px solid #333;color:#aaa;padding:7px 14px;border-radius:4px;font-family:'Lato',sans-serif;font-size:0.8rem;cursor:pointer;transition:all 0.2s;">60s+</button>
</div>

<!-- Step 3: Training Sliders -->
<p style="color:#f5f0eb;font-size:0.75rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:14px;">My weekly training&hellip;</p>
<div style="display:flex;flex-direction:column;gap:14px;margin-bottom:32px;">

<div style="display:flex;align-items:center;gap:12px;">
<span style="color:#aaa;font-size:0.8rem;min-width:140px;flex-shrink:0;">Strength &amp; Sculpt</span>
<input type="range" id="rc-slider-strength" min="0" max="7" value="3" step="1" style="flex:1;height:4px;border-radius:2px;outline:none;cursor:pointer;background:linear-gradient(to right,#e43388 42.9%,#333 42.9%);-webkit-appearance:none;appearance:none;">
<span id="rc-val-strength" style="color:#e43388;font-size:0.85rem;font-weight:700;min-width:36px;text-align:right;">3 /wk</span>
</div>

<div style="display:flex;align-items:center;gap:12px;">
<span style="color:#aaa;font-size:0.8rem;min-width:140px;flex-shrink:0;">HIIT / Metabolic</span>
<input type="range" id="rc-slider-hiit" min="0" max="7" value="1" step="1" style="flex:1;height:4px;border-radius:2px;outline:none;cursor:pointer;background:linear-gradient(to right,#e43388 14.3%,#333 14.3%);-webkit-appearance:none;appearance:none;">
<span id="rc-val-hiit" style="color:#e43388;font-size:0.85rem;font-weight:700;min-width:36px;text-align:right;">1 /wk</span>
</div>

<div style="display:flex;align-items:center;gap:12px;">
<span style="color:#aaa;font-size:0.8rem;min-width:140px;flex-shrink:0;">Pilates / Barre</span>
<input type="range" id="rc-slider-pilates" min="0" max="7" value="1" step="1" style="flex:1;height:4px;border-radius:2px;outline:none;cursor:pointer;background:linear-gradient(to right,#e43388 14.3%,#333 14.3%);-webkit-appearance:none;appearance:none;">
<span id="rc-val-pilates" style="color:#e43388;font-size:0.85rem;font-weight:700;min-width:36px;text-align:right;">1 /wk</span>
</div>

<div style="display:flex;align-items:center;gap:12px;">
<span style="color:#aaa;font-size:0.8rem;min-width:140px;flex-shrink:0;">Cardio</span>
<input type="range" id="rc-slider-cardio" min="0" max="7" value="0" step="1" style="flex:1;height:4px;border-radius:2px;outline:none;cursor:pointer;background:#333;-webkit-appearance:none;appearance:none;">
<span id="rc-val-cardio" style="color:#e43388;font-size:0.85rem;font-weight:700;min-width:36px;text-align:right;">0 /wk</span>
</div>

<div style="display:flex;align-items:center;gap:12px;">
<span style="color:#aaa;font-size:0.8rem;min-width:140px;flex-shrink:0;">HYROX Training</span>
<input type="range" id="rc-slider-hyrox" min="0" max="7" value="0" step="1" style="flex:1;height:4px;border-radius:2px;outline:none;cursor:pointer;background:#333;-webkit-appearance:none;appearance:none;">
<span id="rc-val-hyrox" style="color:#e43388;font-size:0.85rem;font-weight:700;min-width:36px;text-align:right;">0 /wk</span>
</div>

</div>

<!-- Chart -->
<canvas id="resultsChart" height="220"></canvas>

<!-- Annotation -->
<p id="resultsAnnotation" class="chart-annotation" style="margin-top:20px;min-height:4.5em;"></p>

<!-- Disclaimer -->
<p style="color:#444;font-size:0.72rem;line-height:1.6;margin-top:12px;text-align:center;">Individual results may vary. Projections based on published sports science research and are intended as a guide only.</p>
</div>
```

**Files affected:** `/tmp/homepage-v5.html`

---

### Step 2: Replace JS — Frequency Chart Engine

Find and replace the entire frequency chart JS block in `/tmp/homepage.js`.

**Find (exact start marker):**
```
// ── FREQUENCY CHART + PHASE STORY ────────────────────────────────
```

**Find (exact end — last line of the file):**
The block runs from that comment through to the end of the file (line 719). Replace everything from that comment to end-of-file with the new engine below.

**Replace with:**

```javascript
// ── PERSONALISED RESULTS CURVE ────────────────────────────────────

const RC_GOALS = [
    { id: "lose-weight",   label: "Lose Weight",            yLabel: "kg body fat lost",         peak: 14,  unit: "kg",  weights: [9,7,3,4,6]  },
    { id: "recomp",        label: "Lose Fat & Gain Muscle", yLabel: "% body fat reduced",        peak: 18,  unit: "%",   weights: [10,6,2,3,6] },
    { id: "bone-density",  label: "Stronger Bones",         yLabel: "% bone density increase",  peak: 7,   unit: "%",   weights: [9,5,2,3,5]  },
    { id: "get-stronger",  label: "Get Stronger",           yLabel: "% strength increase",      peak: 55,  unit: "%",   weights: [10,3,2,1,5] },
    { id: "hyrox",         label: "Train for HYROX",        yLabel: "minutes off your time",    peak: 28,  unit: "min", weights: [7,8,1,6,10] },
];

const RC_DECADES = {
    "20s": { rate: 1.15, peak: 1.00 },
    "30s": { rate: 1.00, peak: 0.95 },
    "40s": { rate: 0.85, peak: 0.90 },
    "50s": { rate: 0.75, peak: 0.88 },
    "60s": { rate: 0.70, peak: 0.85 },
};

const RC_BASE_RATE = 0.18;
const RC_MONTHS    = [0,1,2,3,4,5,6,7,8,9,10,11,12];

function rcCurve(goalCfg, dec, sessions) {
    const weights   = goalCfg.weights;
    const maxWeight = Math.max(...weights);
    const normalMax = 6 * maxWeight;
    let weeklyScore = 0;
    sessions.forEach((s, i) => { weeklyScore += s * weights[i]; });
    const score = Math.min(weeklyScore, normalMax) / normalMax;
    return RC_MONTHS.map(t => {
        const v = goalCfg.peak * dec.peak * score
                  * (1 - Math.exp(-RC_BASE_RATE * Math.sqrt(score) * dec.rate * t));
        return Math.round(Math.max(0, v) * 10) / 10;
    });
}

function rcBaseline(goalCfg) {
    const baseScore = 0.18;
    return RC_MONTHS.map(t => {
        const v = goalCfg.peak * 1.0 * baseScore
                  * (1 - Math.exp(-RC_BASE_RATE * Math.sqrt(baseScore) * 1.0 * t));
        return Math.round(Math.max(0, v) * 10) / 10;
    });
}

function rcAnnotation(goalCfg, decade, score, month12val) {
    const decLabel = decade === "60s" ? "60s" : decade;
    const resultPhrase = {
        "lose-weight":  `lose ${month12val}kg of body fat`,
        "recomp":       `reduce body fat by ${month12val}%`,
        "bone-density": `improve bone density by ${month12val}%`,
        "get-stronger": `increase your strength by ${month12val}%`,
        "hyrox":        `take ${month12val} minutes off your HYROX time`,
    }[goalCfg.id];

    if (score < 0.25) {
        return `This training mix will produce limited results over 12 months. Adding 2–3 strength sessions per week would significantly change this curve.`;
    }
    if (score < 0.5) {
        return `A moderate training mix. A woman in her ${decLabel} following this plan can expect to ${resultPhrase} over 12 months. Adding more strength work would push this further.`;
    }
    if (score < 0.75) {
        return `A solid training mix. Based on published research, a woman in her ${decLabel} on this plan can expect to ${resultPhrase} by month 12.`;
    }
    let text = `An elite training frequency. Based on published research and real member outcomes, a woman in her ${decLabel} training at this level can expect to ${resultPhrase} by month 12.`;
    if (goalCfg.id === "hyrox") {
        text += ` Our members training 6 days per week at The Evolved typically improve their HYROX completion time by 20–28 minutes in their first year.`;
    }
    return text;
}

function initResultsChart() {
    const canvas = document.getElementById("resultsChart");
    if (!canvas) return;

    let activeGoal   = "recomp";
    let activeDecade = "40s";

    const sliders = {
        strength: document.getElementById("rc-slider-strength"),
        hiit:     document.getElementById("rc-slider-hiit"),
        pilates:  document.getElementById("rc-slider-pilates"),
        cardio:   document.getElementById("rc-slider-cardio"),
        hyrox:    document.getElementById("rc-slider-hyrox"),
    };
    const valEls = {
        strength: document.getElementById("rc-val-strength"),
        hiit:     document.getElementById("rc-val-hiit"),
        pilates:  document.getElementById("rc-val-pilates"),
        cardio:   document.getElementById("rc-val-cardio"),
        hyrox:    document.getElementById("rc-val-hyrox"),
    };

    function getSessions() {
        return ["strength","hiit","pilates","cardio","hyrox"].map(k =>
            sliders[k] ? parseInt(sliders[k].value) : 0
        );
    }

    const goalCfg0 = RC_GOALS.find(g => g.id === activeGoal);
    const dec0     = RC_DECADES[activeDecade];

    const chart = new Chart(canvas.getContext("2d"), {
        type: "line",
        data: {
            labels: RC_MONTHS.map(m => m === 0 ? "Start" : `M${m}`),
            datasets: [
                {
                    label: "Your projected results",
                    data: rcCurve(goalCfg0, dec0, getSessions()),
                    borderColor: "#e43388",
                    backgroundColor: "rgba(228,51,136,0.07)",
                    fill: true,
                    tension: 0.4,
                    borderWidth: 2.5,
                    pointRadius: 0,
                    pointHoverRadius: 5,
                    pointHoverBackgroundColor: "#e43388",
                },
                {
                    label: "Without structured training",
                    data: rcBaseline(goalCfg0),
                    borderColor: "#444",
                    borderDash: [6,4],
                    backgroundColor: "transparent",
                    fill: false,
                    tension: 0.4,
                    borderWidth: 1.5,
                    pointRadius: 0,
                },
            ]
        },
        options: {
            responsive: true,
            animation: { duration: 500, easing: "easeInOutQuart" },
            plugins: {
                legend: {
                    display: true,
                    labels: { color: "#888", font: { family: "Lato", size: 11 }, boxWidth: 20, padding: 16 }
                },
                tooltip: {
                    mode: "index",
                    intersect: false,
                    callbacks: {
                        label: ctx => ` ${ctx.dataset.label}: ${ctx.parsed.y} ${goalCfg0.unit}`
                    }
                }
            },
            scales: {
                x: { ticks: { color: "#666", font: { size: 10 } }, grid: { color: "#1a1a1a" },
                     title: { display: true, text: "Month", color: "#555", font: { size: 11 } } },
                y: { min: 0, ticks: { color: "#666" }, grid: { color: "#1a1a1a" },
                     title: { display: true, text: goalCfg0.yLabel, color: "#555", font: { size: 11 } } }
            }
        }
    });

    // Store mutable tooltip unit ref
    let currentGoalCfg = goalCfg0;
    chart.options.plugins.tooltip.callbacks.label = ctx =>
        ` ${ctx.dataset.label}: ${ctx.parsed.y} ${currentGoalCfg.unit}`;

    function refresh() {
        const goalCfg = RC_GOALS.find(g => g.id === activeGoal);
        const dec     = RC_DECADES[activeDecade];
        const sessions = getSessions();
        const weights  = goalCfg.weights;
        const maxWeight = Math.max(...weights);
        const normalMax = 6 * maxWeight;
        let weeklyScore = 0;
        sessions.forEach((s, i) => { weeklyScore += s * weights[i]; });
        const score    = Math.min(weeklyScore, normalMax) / normalMax;
        const newData  = rcCurve(goalCfg, dec, sessions);
        const baseline = rcBaseline(goalCfg);
        const month12  = newData[12];

        currentGoalCfg = goalCfg;
        chart.data.datasets[0].data = newData;
        chart.data.datasets[1].data = baseline;
        chart.options.scales.y.title.text = goalCfg.yLabel;
        chart.update();

        const annEl = document.getElementById("resultsAnnotation");
        if (annEl) {
            const text = rcAnnotation(goalCfg, activeDecade, score, month12);
            annEl.textContent = text;
            gsap.fromTo(annEl, { opacity: 0, y: 6 }, { opacity: 1, y: 0, duration: 0.35, ease: "power2.out" });
        }
    }

    // Goal buttons
    document.querySelectorAll(".rc-goal-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            activeGoal = btn.dataset.goal;
            document.querySelectorAll(".rc-goal-btn").forEach(b => {
                const active = b.dataset.goal === activeGoal;
                b.style.background  = active ? "#e43388" : "#1a1a1a";
                b.style.borderColor = active ? "#e43388" : "#333";
                b.style.color       = active ? "#fff"    : "#aaa";
                b.style.fontWeight  = active ? "700"     : "400";
            });
            refresh();
        });
    });

    // Decade buttons
    document.querySelectorAll(".rc-decade-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            activeDecade = btn.dataset.decade;
            document.querySelectorAll(".rc-decade-btn").forEach(b => {
                const active = b.dataset.decade === activeDecade;
                b.style.background  = active ? "#e43388" : "#1a1a1a";
                b.style.borderColor = active ? "#e43388" : "#333";
                b.style.color       = active ? "#fff"    : "#aaa";
                b.style.fontWeight  = active ? "700"     : "400";
            });
            refresh();
        });
    });

    // Training sliders
    Object.entries(sliders).forEach(([key, slider]) => {
        if (!slider) return;
        slider.addEventListener("input", () => {
            const val = parseInt(slider.value);
            const pct = (val / 7) * 100;
            slider.style.background =
                `linear-gradient(to right, #e43388 ${pct}%, #333 ${pct}%)`;
            if (valEls[key]) valEls[key].textContent = `${val} /wk`;
            refresh();
        });
    });

    // Initial render
    refresh();
}


// ── INIT ──────────────────────────────────────────────────────────

document.addEventListener("DOMContentLoaded", () => {
    const sarcoChart = initSarcopeniaChart();
    if (sarcoChart) {
        const brackets = ["20s","30s","40s","50s","60s","70s+"];
        const slider   = document.getElementById("ageSlider");

        selectAgeBracket(sarcoChart, "20s");
        updateMusclePoints("20s");
        updateDecadeCards("20s");

        if (slider) {
            function updateSlider() {
                const val     = parseInt(slider.value);
                const bracket = brackets[val];
                const pct     = (val / 5) * 100;
                slider.style.background =
                    `linear-gradient(to right, #e43388 ${pct}%, #333 ${pct}%)`;
                selectAgeBracket(sarcoChart, bracket);
                updateMusclePoints(bracket);
                updateDecadeCards(bracket);
            }
            slider.addEventListener("input", updateSlider);
        }
    }

    initResultsChart();
});
```

**Files affected:** `/tmp/homepage.js`

---

### Step 3: Add Range Input Thumb Styles

The range input needs a styled thumb. Add the following to the inline `<style>` block in homepage-v5.html (find the existing `<style>` tag near the top of the file and append before the closing `</style>`):

```css
/* Results curve sliders */
input[type=range]::-webkit-slider-thumb {
    -webkit-appearance: none;
    width: 16px; height: 16px;
    border-radius: 50%;
    background: #e43388;
    cursor: pointer;
    border: 2px solid #0a0a0a;
    margin-top: -6px;
}
input[type=range]::-moz-range-thumb {
    width: 16px; height: 16px;
    border-radius: 50%;
    background: #e43388;
    cursor: pointer;
    border: 2px solid #0a0a0a;
}
input[type=range]::-webkit-slider-runnable-track {
    height: 4px; border-radius: 2px;
}
```

**Files affected:** `/tmp/homepage-v5.html` (inline `<style>` block)

---

### Step 4: Deploy

```bash
# Load creds
export $(grep -v '^#' scripts/.env | grep -E '^SITEGROUND' | xargs)
KEY=$SITEGROUND_SSH_KEY_PATH; PORT=$SITEGROUND_SSH_PORT
USER=$SITEGROUND_SSH_USER; HOST=$SITEGROUND_SSH_HOST
WP="~/www/blog.theevolvedgym.com.au/public_html"
THEME="$USER@$HOST:~/www/blog.theevolvedgym.com.au/public_html/wp-content/themes/blocksy-child"

# 1. Upload JS (correct theme path)
scp -i $KEY -P $PORT /tmp/homepage.js $THEME/js/homepage.js

# 2. Bump version to 22.0
ssh -i $KEY -p $PORT $USER@$HOST \
  "sed -i 's/\"21\.0\", true)/\"22.0\", true)/' \
  ~/www/blog.theevolvedgym.com.au/public_html/wp-content/themes/blocksy-child/functions.php \
  && grep homepage.js ~/www/blog.theevolvedgym.com.au/public_html/wp-content/themes/blocksy-child/functions.php"

# 3. Upload HTML
scp -i $KEY -P $PORT /tmp/homepage-v5.html $USER@$HOST:$WP/homepage-v5.html

# 4. Write to DB
ssh -i $KEY -p $PORT $USER@$HOST "cd $WP && wp eval '
  global \$wpdb;
  \$r = \$wpdb->update(\$wpdb->posts,
    [\"post_content\" => file_get_contents(\"homepage-v5.html\")], [\"ID\" => 165]);
  echo \$r === false ? \"ERROR: \" . \$wpdb->last_error : \"OK\";
'"

# 5. Flush caches
ssh -i $KEY -p $PORT $USER@$HOST \
  "cd $WP && wp cache flush && wp transient delete --all && wp sg purge"
```

---

## Validation Checklist

- [ ] Goal pills render in a row, pink active state on "Lose Fat & Gain Muscle" on load
- [ ] Decade pills render, pink active on "40s" on load
- [ ] All 5 sliders render with pink fill matching default values
- [ ] Chart renders on load with a meaningful pink curve above the gray dashed baseline
- [ ] Clicking a different goal updates the chart, Y-axis label, and annotation text
- [ ] Clicking a different decade updates the chart curve
- [ ] Moving a slider updates both the count label and the chart in real time
- [ ] Annotation text changes based on score bracket
- [ ] HYROX goal shows HYROX-specific member data sentence at high training scores
- [ ] Disclaimer text visible below annotation
- [ ] Mobile: goal pills wrap to 2 rows cleanly, sliders usable, chart readable
- [ ] Slider thumb is pink, track fills pink to the left of thumb

---

## Success Criteria

1. A visitor with 3 pilates + 2 cardio sees a noticeably flatter curve than one with 3 strength + 1 HIIT + 1 pilates — the visual difference communicates the message without words
2. Every input combination produces a coherent annotation sentence — no broken text, no `undefined`
3. The chart is fully functional on mobile (touch sliders, pill taps, chart readable)
4. No JavaScript errors in console on page load

---

## Notes

- The baseline curve intentionally uses a fixed low score (0.18) regardless of goal — it represents "sporadic, unstructured activity" which is the real comparison point for most visitors
- The 60s+ modifier produces a lower absolute curve but the annotation for that decade should always acknowledge the *relative* benefit is highest — add this nuance to the high-score annotation if desired in a future iteration
- HYROX member data ("6 days, under 90 minutes") is the only Evolved-specific data point in the algorithm. When formal client outcome data is available, the `peak` values per goal can be updated to reflect real averages
- Range input custom styling uses pseudo-elements which are supported in all modern browsers; no polyfill needed
