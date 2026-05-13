# Homepage Implementation Guide — WordPress / Blocksy
**Version:** 1.0
**Created:** 2026-04-30
**Applies to:** theevolvedgym.com.au (post-migration)

---

## Stack

| Layer | Tool | Delivery |
|---|---|---|
| Theme | Blocksy + child theme | Installed on SiteGround |
| Animations | GSAP 3 + ScrollTrigger | CDN |
| Charts | Chart.js 4 | CDN |
| SEO | RankMath | Plugin |
| Page editor | WordPress block editor (Gutenberg) | — |

---

## Child Theme Setup

If the Blocksy child theme is not already created:

1. In SiteGround → WordPress → File Manager (or via SFTP)
2. Create `/wp-content/themes/blocksy-child/` directory
3. Create the following files:

### style.css
```css
/*
Theme Name: Blocksy Child
Template: blocksy
Version: 1.0
*/

/* ===================================================
   THE EVOLVED — HOMEPAGE STYLES
   =================================================== */

/* ---------- Colour tokens ---------- */
:root {
    --evolved-bg:        #0a0a0a;
    --evolved-bg-2:      #111111;
    --evolved-pink:      #e43388;
    --evolved-pink-dim:  #e4338855;
    --evolved-text:      #f5f0eb;
    --evolved-text-dim:  #aaaaaa;
    --evolved-border:    #222222;
}

/* ---------- Global resets ---------- */
html { scroll-behavior: smooth; }

body.home {
    background: var(--evolved-bg);
    color: var(--evolved-text);
    font-family: 'Lato', sans-serif;
}

/* ---------- Hide header nav on homepage only ---------- */
body.home .site-header,
body.home #header {
    display: none !important;
}

/* ---------- Sections ---------- */
.evolved-section {
    padding: 80px 24px;
    max-width: 900px;
    margin: 0 auto;
}

.evolved-section--dark {
    background: var(--evolved-bg-2);
    max-width: 100%;
    padding: 80px 24px;
}

.evolved-section--dark .section-inner {
    max-width: 900px;
    margin: 0 auto;
}

/* ---------- Hero ---------- */
.hero {
    position: relative;
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    overflow: hidden;
}

.hero-bg {
    position: absolute;
    inset: 0;
    background-size: cover;
    background-position: center;
    filter: brightness(0.35);
}

.hero-content {
    position: relative;
    z-index: 2;
    max-width: 720px;
    padding: 24px;
}

.hero-headline {
    font-family: 'PT Serif Caption', serif;
    font-size: clamp(2rem, 5vw, 3.5rem);
    line-height: 1.15;
    color: var(--evolved-text);
    margin-bottom: 24px;
    opacity: 0; /* GSAP animates this in */
}

.hero-subheadline {
    font-size: clamp(1rem, 2.5vw, 1.3rem);
    color: var(--evolved-text-dim);
    margin-bottom: 36px;
    line-height: 1.6;
    opacity: 0; /* GSAP animates this in */
}

.hero-disclaimer {
    font-size: 0.85rem;
    color: var(--evolved-text-dim);
    margin-top: 16px;
    opacity: 0; /* GSAP animates this in */
}

/* ---------- Buttons ---------- */
.btn-primary {
    display: inline-block;
    background: var(--evolved-pink);
    color: #fff;
    padding: 16px 36px;
    border-radius: 4px;
    font-family: 'Lato', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    letter-spacing: 0.03em;
    text-decoration: none;
    transition: background 0.2s ease, transform 0.1s ease;
}

.btn-primary:hover {
    background: #c42b76;
    color: #fff;
    transform: translateY(-1px);
}

/* ---------- Section headings ---------- */
.section-heading {
    font-family: 'PT Serif Caption', serif;
    font-size: clamp(1.5rem, 3.5vw, 2.4rem);
    color: var(--evolved-text);
    margin-bottom: 40px;
    line-height: 1.25;
}

/* ---------- Charts ---------- */
.chart-wrapper {
    background: var(--evolved-bg-2);
    border: 1px solid var(--evolved-border);
    border-radius: 8px;
    padding: 32px 24px;
    margin: 32px 0;
}

/* ---------- Age selector buttons ---------- */
.age-buttons {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin: 24px 0 16px;
}

.age-btn {
    padding: 10px 20px;
    border: 1px solid var(--evolved-border);
    background: transparent;
    color: var(--evolved-text-dim);
    border-radius: 4px;
    font-family: 'Lato', sans-serif;
    font-size: 0.9rem;
    cursor: pointer;
    transition: all 0.2s ease;
}

.age-btn:hover,
.age-btn.active {
    border-color: var(--evolved-pink);
    color: var(--evolved-pink);
    background: #e4338811;
}

/* ---------- Chart annotation ---------- */
.chart-annotation {
    font-size: 0.95rem;
    color: var(--evolved-text-dim);
    line-height: 1.7;
    margin: 20px 0;
    min-height: 2.5em;
    border-left: 3px solid var(--evolved-pink);
    padding-left: 16px;
    opacity: 0;
}

.chart-below-copy {
    font-size: 1rem;
    color: var(--evolved-text-dim);
    margin: 24px 0;
    line-height: 1.6;
}

/* ---------- 3-column grid (SA section) ---------- */
.three-col {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 32px;
    margin: 40px 0;
}

.three-col-item {
    border-top: 2px solid var(--evolved-pink);
    padding-top: 20px;
}

.three-col-item h3 {
    font-family: 'PT Serif Caption', serif;
    font-size: 1rem;
    color: var(--evolved-pink);
    margin-bottom: 12px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.three-col-item p {
    font-size: 0.95rem;
    color: var(--evolved-text-dim);
    line-height: 1.6;
}

/* ---------- Social proof cards ---------- */
.results-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
    gap: 24px;
    margin: 40px 0;
}

.result-card {
    background: var(--evolved-bg-2);
    border: 1px solid var(--evolved-border);
    border-radius: 8px;
    padding: 28px 24px;
    opacity: 0; /* GSAP stagger */
}

.result-card blockquote {
    font-size: 1rem;
    line-height: 1.65;
    color: var(--evolved-text);
    font-style: italic;
    margin: 0 0 16px;
    border: none;
    padding: 0;
}

.result-card cite {
    font-size: 0.85rem;
    color: var(--evolved-pink);
    font-style: normal;
}

.results-link {
    color: var(--evolved-pink);
    text-decoration: none;
    font-size: 0.9rem;
    border-bottom: 1px solid var(--evolved-pink-dim);
    transition: border-color 0.2s;
}

.results-link:hover {
    border-color: var(--evolved-pink);
}

/* ---------- Final CTA section ---------- */
.cta-final {
    text-align: center;
    background: var(--evolved-bg-2);
    padding: 100px 24px;
}

.cta-final .section-heading {
    margin-bottom: 16px;
}

.cta-final .cta-sub {
    font-size: 1rem;
    color: var(--evolved-text-dim);
    margin-bottom: 40px;
}

/* ---------- Footer (minimal) ---------- */
body.home .site-footer {
    background: #000;
    color: var(--evolved-text-dim);
    font-size: 0.8rem;
    padding: 32px 24px;
    text-align: center;
    border-top: 1px solid var(--evolved-border);
}

body.home .site-footer a {
    color: var(--evolved-text-dim);
    text-decoration: none;
}

/* ---------- Responsive ---------- */
@media (max-width: 600px) {
    .evolved-section {
        padding: 60px 16px;
    }
    .chart-wrapper {
        padding: 20px 12px;
    }
}
```

### functions.php
```php
<?php
// Blocksy Child Theme — The Evolved

// Enqueue parent theme styles
add_action('wp_enqueue_scripts', 'evolved_enqueue_styles');
function evolved_enqueue_styles() {
    wp_enqueue_style(
        'blocksy-parent-style',
        get_template_directory_uri() . '/style.css'
    );
}

// Enqueue CDN scripts (GSAP, Chart.js) on homepage only
add_action('wp_enqueue_scripts', 'evolved_enqueue_homepage_scripts');
function evolved_enqueue_homepage_scripts() {
    if (!is_front_page()) return;

    // GSAP + ScrollTrigger
    wp_enqueue_script(
        'gsap',
        'https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/gsap.min.js',
        [], null, true
    );
    wp_enqueue_script(
        'gsap-scrolltrigger',
        'https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/ScrollTrigger.min.js',
        ['gsap'], null, true
    );

    // Chart.js
    wp_enqueue_script(
        'chartjs',
        'https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js',
        [], null, true
    );

    // Homepage custom JS
    wp_enqueue_script(
        'evolved-homepage',
        get_stylesheet_directory_uri() . '/js/homepage.js',
        ['gsap', 'gsap-scrolltrigger', 'chartjs'],
        '1.0',
        true
    );
}

// Register Results custom post type
add_action('init', 'evolved_register_results_cpt');
function evolved_register_results_cpt() {
    register_post_type('results', [
        'labels'      => [
            'name'          => 'Results',
            'singular_name' => 'Result',
            'add_new_item'  => 'Add New Result',
            'edit_item'     => 'Edit Result',
        ],
        'public'       => true,
        'has_archive'  => true,
        'rewrite'      => ['slug' => 'results'],
        'supports'     => ['title', 'editor', 'thumbnail', 'custom-fields', 'excerpt'],
        'show_in_rest' => true,
        'menu_icon'    => 'dashicons-awards',
    ]);

    // Goal taxonomy
    register_taxonomy('goal', 'results', [
        'label'        => 'Goal',
        'rewrite'      => ['slug' => 'results/goal'],
        'public'       => true,
        'hierarchical' => false,
        'show_in_rest' => true,
    ]);

    // Life stage taxonomy
    register_taxonomy('life_stage', 'results', [
        'label'        => 'Life Stage',
        'rewrite'      => ['slug' => 'results/life-stage'],
        'public'       => true,
        'hierarchical' => false,
        'show_in_rest' => true,
    ]);
}
?>
```

---

## homepage.js

Create `/wp-content/themes/blocksy-child/js/homepage.js`:

```javascript
/**
 * homepage.js — The Evolved
 * Handles: GSAP scroll animations, sarcopenia chart, frequency chart
 */

gsap.registerPlugin(ScrollTrigger);

// ─── Hero animations ──────────────────────────────────────────────
gsap.timeline({ defaults: { ease: 'power3.out' } })
    .to('.hero-headline',    { opacity: 1, y: 0, duration: 1,    delay: 0.2 })
    .to('.hero-subheadline', { opacity: 1, y: 0, duration: 0.8 }, '-=0.5')
    .to('.hero-disclaimer',  { opacity: 1, y: 0, duration: 0.6 }, '-=0.4');

// Remove initial opacity: 0 in CSS requires the elements to start invisible
gsap.set(['.hero-headline', '.hero-subheadline', '.hero-disclaimer'], { y: 30 });

// ─── Section scroll animations ────────────────────────────────────
const sections = document.querySelectorAll('.evolved-section, .evolved-section--dark');
sections.forEach(section => {
    gsap.from(section.querySelector('.section-heading'), {
        opacity: 0,
        y: 40,
        duration: 0.8,
        ease: 'power3.out',
        scrollTrigger: {
            trigger: section,
            start: 'top 80%',
        },
    });
});

// ─── Chart wrappers slide in ──────────────────────────────────────
gsap.utils.toArray('.chart-wrapper').forEach(el => {
    gsap.from(el, {
        opacity: 0,
        x: -40,
        duration: 0.9,
        ease: 'power3.out',
        scrollTrigger: { trigger: el, start: 'top 85%' },
    });
});

// ─── Results cards stagger ────────────────────────────────────────
gsap.to('.result-card', {
    opacity: 1,
    y: 0,
    duration: 0.6,
    stagger: 0.15,
    ease: 'power3.out',
    scrollTrigger: {
        trigger: '.results-cards',
        start: 'top 80%',
    },
});
gsap.set('.result-card', { y: 30 });

// ─── Final CTA scale in ───────────────────────────────────────────
gsap.from('.cta-final .btn-primary', {
    scale: 0.9,
    opacity: 0,
    duration: 0.7,
    ease: 'back.out(1.5)',
    scrollTrigger: {
        trigger: '.cta-final',
        start: 'top 75%',
    },
});


// ─── Sarcopenia chart ─────────────────────────────────────────────
// (paste full initSarcopeniaChart() and selectAgeBracket() from
//  reference/infographic-sarcopenia-data.md here)


// ─── Frequency chart ──────────────────────────────────────────────
// (paste full initFrequencyChart() and highlightCurve() from
//  reference/infographic-frequency-data.md here)
```

---

## WordPress Page Setup

1. **Create new page:** WordPress admin → Pages → Add New
2. **Title:** "Home"
3. **Template:** Full Width (Blocksy full-width template — no sidebar, no header)
4. **Set as front page:** Settings → Reading → "A static page" → Front page: Home
5. **Build page sections using blocks:**
   - Custom HTML block for hero (with inline background image style)
   - Custom HTML blocks for each section (referencing CSS classes above)
   - Shortcode block for charts (or custom HTML with canvas elements)

6. **Disable header on homepage only:**
   - Blocksy Customizer → Header → Page-specific settings → Homepage: hide header
   - OR use the CSS rule already in style.css (`body.home .site-header { display: none }`)

---

## RankMath Homepage SEO

In RankMath meta box on the homepage:
- **Focus keyword:** `women's gym Brisbane` / `Brisbane women only gym`
- **Title:** `Brisbane's Leading Women-Only Gym | The Evolved`
- **Meta description:** `The Evolved is Brisbane's leading women-only strength training gym. Book your Strength Assessment and discover exactly where you're starting from.`
- **Schema:** Organization (auto from RankMath site settings)
- **Canonical:** `https://theevolvedgym.com.au/`

---

## CDN URLs (pinned versions — update if upgrading)

```
GSAP 3.12.5:
https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/gsap.min.js
https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/ScrollTrigger.min.js

Chart.js 4.4.0:
https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js
```

---

## Testing Checklist

- [ ] Hero image loads — no layout shift
- [ ] Hero GSAP animations fire on page load (not on scroll)
- [ ] Sarcopenia chart renders on load
- [ ] All 6 age buttons functional — annotation appears and fades in
- [ ] CTA pulse animation fires after age selection
- [ ] Frequency chart renders on load
- [ ] Hovering curves shows annotation
- [ ] All section headings animate in on scroll
- [ ] Result cards stagger in on scroll
- [ ] Final CTA scales in on scroll
- [ ] Mobile: all animations, charts, and buttons work on iOS Safari and Chrome Android
- [ ] Page header navigation is hidden
- [ ] Footer shows only: address, phone, ABN
- [ ] All CTA buttons link to `go.theevolvedgym.com.au/strength-assessment`
- [ ] Page loads under 3 seconds (check with PageSpeed Insights)
