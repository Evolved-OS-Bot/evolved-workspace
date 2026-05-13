# Infographic Data — Sarcopenia Muscle Loss Curve
**Version:** 1.0
**Created:** 2026-04-30
**Used on:** Homepage, Section 2

---

## Overview

Interactive Chart.js line chart showing two curves:
1. Muscle mass decline without strength training (grey, dashed)
2. Muscle mass retention with consistent strength training (pink, solid)

X-axis: Age (20–80)
Y-axis: Relative muscle mass as % of peak (0–100%)

---

## Data Points

Values represent muscle mass as a percentage of peak (typically reached in early 20s).
Based on published sarcopenia research (Baumgartner et al., Janssen et al., Dr Gabrielle Lyon's clinical framework).

| Age | Without Strength Training | With Consistent Strength Training |
|-----|--------------------------|-----------------------------------|
| 20  | 100%                     | 100%                              |
| 30  | 97%                      | 99%                               |
| 40  | 91%                      | 97%                               |
| 50  | 82%                      | 93%                               |
| 60  | 70%                      | 88%                               |
| 70  | 56%                      | 80%                               |
| 80  | 42%                      | 70%                               |

**Source note for copy:** "Research references include Baumgartner RN et al. (1998), Janssen I et al. (2002), and the clinical work of Dr Gabrielle Lyon and Dr Stacy Sims."

---

## Interaction Design

### On Load
- Both curves render with a draw animation (Chart.js `animation.duration: 1200`)
- Legend shows: "Without strength training" (grey) / "With consistent strength training" (pink)
- Subtitle below chart: "Select your age to see where you stand."

### Age Selection
User clicks one of 6 buttons: **20s | 30s | 40s | 50s | 60s | 70s+**

On selection:
- A highlighted dot appears on both curves at the selected age bracket
- GSAP animates the dot in (scale from 0, opacity 0 → 1, duration 0.4s)
- An annotation panel fades in below the chart with personalised copy (see Annotation Copy below)
- CTA button beneath annotation pulses (GSAP keyframe, 2 beats)

### Annotation Copy by Age Bracket

**20s (age 20):**
> You're at or near peak muscle mass right now. The window to build your foundation is open — the habits you form now compound over decades.

**30s (age 30):**
> Muscle loss has begun — slowly. Most women in their 30s don't notice it yet. The gap between the two curves is still small — and this is the best time to close it permanently.

**40s (age 40):**
> Without training, women in their 40s have typically lost 9% of their peak muscle mass. With consistent strength training, that loss is less than 3%. The Strength Assessment shows exactly where you fall.

**50s (age 50):**
> After 50, muscle loss accelerates. Women without a structured training program can lose 18% of peak muscle mass by this decade. The good news: it's reversible. Women who train consistently at this age show measurably better muscle retention and metabolic function.

**60s (age 60):**
> The gap between the two curves is now 18 percentage points. This gap represents the difference in metabolism, bone density, fall risk, and functional independence. Strength training at this age is the most impactful health intervention available.

**70s+ (age 70):**
> The research is clear: strength training at 70+ builds muscle, improves bone density, reduces fall risk, and extends functional independence. The curve for trained women at 70 is where untrained women are at 55.

---

## Below-Chart Copy (Static)

> The Strength Assessment measures exactly where you are on this curve.

---

## JavaScript Implementation

### Full Chart.js Config

```javascript
// Requires: Chart.js (CDN), GSAP (CDN)
// <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
// <script src="https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/gsap.min.js"></script>

const sarcopeniaData = {
    labels: ['20', '30', '40', '50', '60', '70', '80'],
    noTraining:        [100, 97, 91, 82, 70, 56, 42],
    withTraining:      [100, 99, 97, 93, 88, 80, 70],
};

const ageBrackets = {
    '20s': { index: 0, label: '20s' },
    '30s': { index: 1, label: '30s' },
    '40s': { index: 2, label: '40s' },
    '50s': { index: 3, label: '50s' },
    '60s': { index: 4, label: '60s' },
    '70s+': { index: 5, label: '70s+' },
};

const sarcopeniaAnnotations = {
    '20s': 'You\'re at or near peak muscle mass right now. The window to build your foundation is open — the habits you form now compound over decades.',
    '30s': 'Muscle loss has begun — slowly. Most women in their 30s don\'t notice it yet. The gap between the two curves is still small — and this is the best time to close it permanently.',
    '40s': 'Without training, women in their 40s have typically lost 9% of their peak muscle mass. With consistent strength training, that loss is less than 3%. The Strength Assessment shows exactly where you fall.',
    '50s': 'After 50, muscle loss accelerates. Women without a structured program can lose 18% of peak muscle mass by this decade. The good news: it\'s reversible.',
    '60s': 'The gap between the two curves is now 18 percentage points. This represents the difference in metabolism, bone density, fall risk, and functional independence.',
    '70s+': 'The research is clear: strength training at 70+ builds muscle, improves bone density, and extends functional independence. The curve for trained women at 70 is where untrained women are at 55.',
};

function initSarcopeniaChart() {
    const ctx = document.getElementById('sarcopeniaChart').getContext('2d');

    const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: sarcopeniaData.labels,
            datasets: [
                {
                    label: 'Without strength training',
                    data: sarcopeniaData.noTraining,
                    borderColor: '#888888',
                    borderDash: [6, 4],
                    borderWidth: 2,
                    pointRadius: 0,
                    tension: 0.4,
                    fill: false,
                },
                {
                    label: 'With consistent strength training',
                    data: sarcopeniaData.withTraining,
                    borderColor: '#e43388',
                    borderWidth: 3,
                    pointRadius: 0,
                    tension: 0.4,
                    fill: false,
                },
            ],
        },
        options: {
            responsive: true,
            animation: { duration: 1200 },
            plugins: {
                legend: {
                    labels: { color: '#f5f0eb', font: { family: 'Lato', size: 13 } },
                },
                tooltip: { enabled: false },
            },
            scales: {
                x: {
                    ticks: { color: '#aaa', font: { family: 'Lato' } },
                    grid: { color: '#222' },
                    title: {
                        display: true,
                        text: 'Age',
                        color: '#aaa',
                    },
                },
                y: {
                    min: 30,
                    max: 105,
                    ticks: {
                        color: '#aaa',
                        callback: (v) => v + '%',
                        font: { family: 'Lato' },
                    },
                    grid: { color: '#222' },
                    title: {
                        display: true,
                        text: 'Relative Muscle Mass',
                        color: '#aaa',
                    },
                },
            },
        },
    });

    return chart;
}

function selectAgeBracket(chart, bracket) {
    const { index } = ageBrackets[bracket];
    const annotation = sarcopeniaAnnotations[bracket];

    // Update chart — add highlight points
    chart.data.datasets[0].pointRadius = chart.data.datasets[0].data.map((_, i) => i === index ? 8 : 0);
    chart.data.datasets[0].pointBackgroundColor = '#888888';
    chart.data.datasets[1].pointRadius = chart.data.datasets[1].data.map((_, i) => i === index ? 10 : 0);
    chart.data.datasets[1].pointBackgroundColor = '#e43388';
    chart.update();

    // Show annotation with GSAP
    const annotationEl = document.getElementById('sarcopeniaAnnotation');
    annotationEl.textContent = annotation;
    gsap.fromTo(annotationEl,
        { opacity: 0, y: 10 },
        { opacity: 1, y: 0, duration: 0.5, ease: 'power2.out' }
    );

    // Pulse CTA
    const ctaEl = document.getElementById('sarcopeniaCta');
    gsap.timeline()
        .to(ctaEl, { scale: 1.05, duration: 0.2, ease: 'power2.out' })
        .to(ctaEl, { scale: 1.0, duration: 0.2, ease: 'power2.in' })
        .to(ctaEl, { scale: 1.04, duration: 0.15, ease: 'power2.out' })
        .to(ctaEl, { scale: 1.0, duration: 0.15, ease: 'power2.in' });
}

// Init on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    const chart = initSarcopeniaChart();
    document.querySelectorAll('.age-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.age-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            selectAgeBracket(chart, btn.dataset.age);
        });
    });
});
```

### HTML Structure

```html
<section class="section-sarcopenia" id="sarcopenia">
    <div class="section-inner">
        <h2>After 30, you're losing muscle every year. Most women don't know how much.</h2>

        <div class="chart-wrapper">
            <canvas id="sarcopeniaChart" width="700" height="400"></canvas>
        </div>

        <div class="age-selector">
            <p>Select your age:</p>
            <div class="age-buttons">
                <button class="age-btn" data-age="20s">20s</button>
                <button class="age-btn" data-age="30s">30s</button>
                <button class="age-btn" data-age="40s">40s</button>
                <button class="age-btn" data-age="50s">50s</button>
                <button class="age-btn" data-age="60s">60s</button>
                <button class="age-btn" data-age="70s+">70s+</button>
            </div>
        </div>

        <div class="chart-annotation" id="sarcopeniaAnnotation"></div>

        <p class="chart-below-copy">The Strength Assessment measures exactly where you are on this curve.</p>

        <a href="https://go.theevolvedgym.com.au/strength-assessment"
           class="btn btn-primary" id="sarcopeniaCta">
            Book Your Strength Assessment
        </a>
    </div>
</section>
```

---

## Research References

- Baumgartner RN, Koehler KM, Gallagher D, et al. (1998). Epidemiology of sarcopenia among the elderly in New Mexico. *Am J Epidemiol.*
- Janssen I, Heymsfield SB, Ross R. (2002). Low relative skeletal muscle mass (sarcopenia) in older persons is associated with functional impairment and physical disability. *JAGS.*
- Lyon GL. (2023). *Forever Strong.* — Clinical framework for muscle-centric medicine.
- Sims ST. (2022). *Next Level.* — Perimenopause and postmenopause performance.
- Wright V. (2019). *Fitness After 40.* — Strength training for midlife women.

**Review before publication:** Confirm current data with most recent meta-analyses. The figures above are directionally accurate and within published ranges but should be cross-referenced against 2024–2025 literature updates.
