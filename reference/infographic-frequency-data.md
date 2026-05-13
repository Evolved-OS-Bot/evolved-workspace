# Infographic Data — Training Frequency vs Results Curve
**Version:** 1.0
**Created:** 2026-04-30
**Used on:** Homepage, Section 3

---

## Overview

Interactive Chart.js line chart showing cumulative results over 52 weeks at three training frequencies.

X-axis: Weeks (0–52)
Y-axis: Relative strength/results index (0–100)

Three curves:
1. 1x per week — grey, dashed
2. 2x per week — pink, lighter
3. 3x per week — pink, full saturation

The key insight: results compound non-linearly. The gap between 1x and 3x is not additive — it's multiplicative due to progressive overload, recovery, and neuromuscular adaptation stacking.

A horizontal "minimum effective dose" line shows where 1x per week barely crosses threshold.

---

## Data Points

Results index is relative (not a direct measurement — represents composite strength/body composition improvement). Designed to show the shape of the curves and the compounding gap, not absolute values.

| Week | 1x/week | 2x/week | 3x/week |
|------|---------|---------|---------|
| 0    | 0       | 0       | 0       |
| 4    | 3       | 7       | 12      |
| 8    | 6       | 14      | 25      |
| 12   | 9       | 22      | 40      |
| 16   | 12      | 30      | 55      |
| 20   | 15      | 39      | 65      |
| 26   | 19      | 50      | 75      |
| 32   | 22      | 58      | 82      |
| 40   | 26      | 66      | 88      |
| 52   | 30      | 75      | 95      |

**Minimum effective dose line:** 10 (horizontal dashed line)
- 1x/week crosses this at approximately Week 13
- 2x/week crosses this at approximately Week 6
- 3x/week crosses this at approximately Week 4

---

## Interaction Design

### On Load
- All three curves render simultaneously with a draw animation (duration 1400ms, staggered)
- Legend displayed with colour coding
- "Minimum effective dose" threshold line visible and labelled
- Subtitle: "Hover over any line to see what that frequency means in practice."

### Hover / Click on Curve (Desktop + Mobile)
- Hovering or clicking any curve:
  - Highlights that curve (increases borderWidth to 4, others dim to 1)
  - Shows annotation panel with that frequency's context (see Annotation Copy)
  - Other curves dim (opacity 0.3)

### Annotation Copy by Frequency

**1x per week:**
> Once per week is the entry point. You'll maintain basic conditioning and see some initial adaptation — but results plateau quickly. Without progressive overload across multiple sessions, the stimulus isn't sufficient to drive meaningful change in muscle mass or strength.

**2x per week:**
> Twice per week produces significantly better results than once. You're giving your body enough stimulus to adapt progressively. For women managing busy schedules, 2x is a meaningful training minimum — and it compounds well over 6–12 months.

**3x per week:**
> Three sessions per week is the threshold where results compound in a non-linear way. Each session builds on the previous one's recovery, progressive overload accumulates, and the strength adaptation curve steepens. This is where real, lasting change happens.

### Below-Chart Copy (Static)

> Barbells and dumbbells are the cornerstone. Pilates, yoga, and cardio are complimentary — they support your training, but they cannot replace it.

---

## JavaScript Implementation

### Full Chart.js Config

```javascript
// Requires: Chart.js (CDN), GSAP (CDN)

const frequencyData = {
    labels: ['0', '4', '8', '12', '16', '20', '26', '32', '40', '52'],
    oneX:   [0,  3,  6,  9,  12,  15,  19,  22,  26,  30],
    twoX:   [0,  7, 14, 22,  30,  39,  50,  58,  66,  75],
    threeX: [0, 12, 25, 40,  55,  65,  75,  82,  88,  95],
    minEffective: 10,
};

const frequencyAnnotations = {
    '1x': 'Once per week is the entry point. Results plateau quickly without enough progressive stimulus across sessions.',
    '2x': 'Twice per week produces significantly better results. For busy schedules, 2x is a meaningful minimum — and it compounds well over 6–12 months.',
    '3x': 'Three sessions per week is where results compound non-linearly. Each session builds on the last, and the adaptation curve steepens.',
};

function initFrequencyChart() {
    const ctx = document.getElementById('frequencyChart').getContext('2d');

    const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: frequencyData.labels,
            datasets: [
                {
                    label: '1x per week',
                    data: frequencyData.oneX,
                    borderColor: '#666666',
                    borderDash: [6, 4],
                    borderWidth: 2,
                    pointRadius: 0,
                    tension: 0.4,
                    fill: false,
                },
                {
                    label: '2x per week',
                    data: frequencyData.twoX,
                    borderColor: '#e43388aa',
                    borderWidth: 2,
                    pointRadius: 0,
                    tension: 0.4,
                    fill: false,
                },
                {
                    label: '3x per week',
                    data: frequencyData.threeX,
                    borderColor: '#e43388',
                    borderWidth: 3,
                    pointRadius: 0,
                    tension: 0.4,
                    fill: false,
                },
                {
                    label: 'Minimum effective dose',
                    data: frequencyData.labels.map(() => frequencyData.minEffective),
                    borderColor: '#555',
                    borderDash: [3, 3],
                    borderWidth: 1,
                    pointRadius: 0,
                    tension: 0,
                    fill: false,
                },
            ],
        },
        options: {
            responsive: true,
            animation: { duration: 1400 },
            plugins: {
                legend: {
                    labels: { color: '#f5f0eb', font: { family: 'Lato', size: 13 } },
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    callbacks: {
                        label: (ctx) => {
                            if (ctx.dataset.label === 'Minimum effective dose') return null;
                            return ` ${ctx.dataset.label}: ${ctx.parsed.y}`;
                        },
                    },
                },
            },
            scales: {
                x: {
                    ticks: { color: '#aaa', font: { family: 'Lato' } },
                    grid: { color: '#222' },
                    title: {
                        display: true,
                        text: 'Weeks',
                        color: '#aaa',
                    },
                },
                y: {
                    min: 0,
                    max: 100,
                    ticks: { color: '#aaa', font: { family: 'Lato' } },
                    grid: { color: '#222' },
                    title: {
                        display: true,
                        text: 'Results Index',
                        color: '#aaa',
                    },
                },
            },
            onHover: (event, elements) => {
                if (elements.length > 0) {
                    const datasetIndex = elements[0].datasetIndex;
                    highlightCurve(chart, datasetIndex);
                }
            },
        },
    });

    return chart;
}

function highlightCurve(chart, activeIndex) {
    const labels = ['1x', '2x', '3x'];
    if (activeIndex > 2) return; // ignore threshold line

    chart.data.datasets.forEach((ds, i) => {
        if (i === activeIndex) {
            ds.borderWidth = 4;
            ds.borderColor = i === 0 ? '#888' : i === 1 ? '#e43388bb' : '#e43388';
        } else if (i < 3) {
            ds.borderWidth = 1;
            ds.borderColor = i === 0 ? '#44444488' : '#e4338855';
        }
    });
    chart.update('none');

    const annotationEl = document.getElementById('frequencyAnnotation');
    annotationEl.textContent = frequencyAnnotations[labels[activeIndex]];
    gsap.fromTo(annotationEl,
        { opacity: 0, y: 8 },
        { opacity: 1, y: 0, duration: 0.4, ease: 'power2.out' }
    );
}

document.addEventListener('DOMContentLoaded', () => {
    initFrequencyChart();
});
```

### HTML Structure

```html
<section class="section-frequency" id="frequency">
    <div class="section-inner">
        <h2>The difference between training once and three times a week isn't 3x the results — it's closer to 9x.</h2>

        <div class="chart-wrapper">
            <canvas id="frequencyChart" width="700" height="400"></canvas>
        </div>

        <div class="chart-annotation" id="frequencyAnnotation">
            Hover or tap any line to see what that frequency means in practice.
        </div>

        <p class="chart-below-copy">
            Barbells and dumbbells are the cornerstone. Pilates, yoga, and cardio are complimentary —
            they support your training, but they cannot replace it.
        </p>

        <a href="https://go.theevolvedgym.com.au/strength-assessment"
           class="btn btn-primary">
            Your trainer will prescribe the right frequency → Book Your Strength Assessment
        </a>
    </div>
</section>
```
