<?php
/**
 * Single Results CPT template — /results/[slug]
 *
 * Header layout: two-column on desktop (text left, photo right).
 * Photo source: WordPress featured image (post thumbnail).
 * Post content: raw story HTML — pull quote → body → key results.
 */
$post_id    = get_the_ID();
$title      = get_the_title();
$goals      = wp_get_post_terms($post_id, 'goal',       ['fields' => 'names']);
$stages     = wp_get_post_terms($post_id, 'life_stage', ['fields' => 'names']);
$content    = get_post_field('post_content', $post_id);
$thumb_url  = get_the_post_thumbnail_url($post_id, 'full');
?><!DOCTYPE html>
<html <?php language_attributes(); ?>>
<head>
<meta charset="<?php bloginfo('charset'); ?>">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title><?php echo esc_html($title); ?> | The Evolved All Female Gym</title>
<?php
// Open Graph meta tags for story pages
$og_title       = $title . ' | The Evolved Brisbane';
$og_description = get_the_excerpt();
$og_image       = $thumb_url; // already fetched above
$og_url         = get_permalink();

// Fallback description: extract pull quote from blockquote in content
if (!$og_description) {
    preg_match('/<blockquote[^>]*>(.*?)<\/blockquote>/s', $content, $m);
    $og_description = !empty($m[1]) ? wp_strip_all_tags($m[1]) : get_bloginfo('description');
}

// Fallback image to site OG default if no featured image
if (!$og_image) {
    $og_image = 'https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/evolved-og-default.png';
}
?>
<meta property="og:type"               content="article">
<meta property="og:title"              content="<?php echo esc_attr($og_title); ?>">
<meta property="og:description"        content="<?php echo esc_attr($og_description); ?>">
<meta property="og:image"              content="<?php echo esc_url($og_image); ?>">
<meta property="og:url"                content="<?php echo esc_url($og_url); ?>">
<meta property="og:site_name"          content="The Evolved All Female Gym">
<meta name="twitter:card"              content="summary_large_image">
<meta name="twitter:title"             content="<?php echo esc_attr($og_title); ?>">
<meta name="twitter:description"       content="<?php echo esc_attr($og_description); ?>">
<meta name="twitter:image"             content="<?php echo esc_url($og_image); ?>">
<?php wp_head(); ?>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { background: #f5f5f5; color: #1a1a1a; font-family: "Inter","Open Sans",sans-serif; }

/* Nav */
.ev-story-nav { background: #111; padding: 14px 24px; display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.ev-story-nav a { color: rgba(255,255,255,0.55); font-size: 0.78rem; text-decoration: none; letter-spacing: 0.08em; text-transform: uppercase; }
.ev-story-nav a:hover { color: #e43388; }
.ev-story-nav .breadcrumb { color: rgba(255,255,255,0.3); font-size: 0.78rem; letter-spacing: 0.06em; text-transform: uppercase; }

/* ── TWO-COLUMN HERO ─────────────────────────────────────── */
.ev-story-split { display: grid; grid-template-columns: 1fr 1fr; background: #111; }
.ev-story-split-left {
  display: flex; flex-direction: column; justify-content: center;
  padding: 72px 56px;
}
.ev-story-split-left .eyebrow {
  color: #e43388; font-size: 0.8rem; font-weight: 700;
  letter-spacing: 0.14em; text-transform: uppercase; margin: 0 0 18px;
}
.ev-story-split-left h1 {
  color: #fff;
  font-family: "PT Serif Caption","Playfair Display",Georgia,serif;
  font-size: clamp(1.8rem, 3.5vw, 2.8rem);
  line-height: 1.1; margin: 0 0 28px;
}
.ev-story-tags { display: flex; flex-wrap: wrap; gap: 8px; }
.ev-tag { display: inline-block; padding: 6px 14px; border-radius: 100px; font-size: 0.76rem; font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase; }
.ev-tag-goal  { background: rgba(228,51,136,0.2); color: #e43388; }
.ev-tag-stage { background: rgba(255,255,255,0.1); color: rgba(255,255,255,0.65); }

.ev-story-split-right { overflow: hidden; }
.ev-story-split-right img {
  width: 100%; height: 100%; min-height: 420px;
  object-fit: cover; object-position: center top; display: block;
}

/* Fallback: no photo — full-width dark hero */
.ev-story-hero-fallback { background: #111; padding: 64px 32px 56px; text-align: center; }
.ev-story-hero-fallback .eyebrow { color: #e43388; font-size: 0.8rem; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; margin: 0 0 16px; }
.ev-story-hero-fallback h1 { color: #fff; font-family: "PT Serif Caption","Playfair Display",Georgia,serif; font-size: clamp(1.8rem,4.5vw,2.8rem); line-height: 1.1; margin: 0 0 24px; }
.ev-story-hero-fallback .ev-story-tags { justify-content: center; }

/* Mobile: stack photo above text */
@media (max-width: 768px) {
  .ev-story-split { grid-template-columns: 1fr; }
  .ev-story-split-right { order: -1; }
  .ev-story-split-right img { min-height: 280px; max-height: 420px; }
  .ev-story-split-left { padding: 48px 24px; }
}

/* ── STORY CONTENT ───────────────────────────────────────── */
/* Pull quote */
.ev-pull-quote { background: #0a0a0a; padding: 64px 32px; text-align: center; }
.ev-quote-mark { color: #e43388; font-size: 5rem; font-family: Georgia,serif; line-height: 0.4; display: block; margin-bottom: 20px; }
.ev-pull-quote blockquote { color: #f5f0eb; font-family: "PT Serif Caption","Playfair Display",Georgia,serif; font-size: clamp(1.2rem,2.8vw,1.7rem); line-height: 1.5; max-width: 720px; margin: 0 auto; font-style: italic; }
.ev-pull-quote .attribution { color: rgba(255,255,255,0.45); font-size: 0.82rem; margin-top: 24px; letter-spacing: 0.08em; text-transform: uppercase; }

/* Story body */
.ev-story-body { background: #fff; padding: 72px 32px; }
.ev-story-body-inner { max-width: 700px; margin: 0 auto; }
.ev-story-body p { color: #2a2a2a; font-size: 1.02rem; line-height: 1.9; margin: 0 0 22px; }
.ev-story-body p:last-child { margin-bottom: 0; }
.ev-story-body h3 { font-family: "PT Serif Caption","Playfair Display",Georgia,serif; font-size: 1.25rem; color: #1a1a1a; margin: 36px 0 14px; }

/* Key results */
.ev-key-results { background: #111; padding: 72px 32px; }
.ev-key-results h2 { color: #f5f0eb; font-family: "PT Serif Caption","Playfair Display",Georgia,serif; font-size: clamp(1.3rem,2.8vw,1.7rem); text-align: center; margin: 0 0 40px; }
.ev-key-results-grid { display: grid; grid-template-columns: repeat(3,1fr); gap: 20px; max-width: 820px; margin: 0 auto; }
@media (max-width: 640px) { .ev-key-results-grid { grid-template-columns: 1fr; } }
.ev-result-stat { background: rgba(255,255,255,0.05); border-radius: 8px; padding: 28px 20px; text-align: center; border-top: 3px solid #e43388; }
.ev-result-stat .stat-number { font-size: 2rem; font-weight: 700; color: #e43388; font-family: "PT Serif Caption","Playfair Display",Georgia,serif; display: block; margin-bottom: 8px; }
.ev-result-stat .stat-label { color: rgba(255,255,255,0.65); font-size: 0.85rem; line-height: 1.6; }

/* Bottom CTA */
.ev-story-cta-bar { background: #e43388; padding: 72px 32px; text-align: center; }
.ev-story-cta-bar h2 { color: #fff; font-family: "PT Serif Caption","Playfair Display",Georgia,serif; font-size: clamp(1.6rem,3.5vw,2.2rem); margin: 0 0 16px; }
.ev-story-cta-bar p { color: rgba(255,255,255,0.92); font-size: 1rem; line-height: 1.75; max-width: 520px; margin: 0 auto 28px; }
.ev-story-cta-bar a { display: inline-block; background: #fff; color: #e43388 !important; font-weight: 700; font-size: 0.95rem; text-decoration: none; padding: 15px 36px; letter-spacing: 0.06em; text-transform: uppercase; }

/* Footer bar */
.ev-story-footer-bar { background: #111; padding: 28px 32px; text-align: center; }
.ev-story-footer-bar a { color: rgba(255,255,255,0.45); font-size: 0.8rem; text-decoration: none; letter-spacing: 0.08em; text-transform: uppercase; }
.ev-story-footer-bar a:hover { color: #e43388; }
</style>
</head>
<body <?php body_class('evolved-story-page'); ?>>
<?php wp_body_open(); ?>

<nav class="ev-story-nav">
  <a href="/results/">&#8592; All Results</a>
  <span class="breadcrumb">The Evolved &rsaquo; Results</span>
</nav>

<?php if ($thumb_url): ?>
<div class="ev-story-split">
  <div class="ev-story-split-left">
    <p class="eyebrow">Member Story</p>
    <h1><?php echo esc_html($title); ?></h1>
    <div class="ev-story-tags">
      <?php foreach ($goals as $g): ?>
        <span class="ev-tag ev-tag-goal"><?php echo esc_html($g); ?></span>
      <?php endforeach; ?>
      <?php foreach ($stages as $s): ?>
        <span class="ev-tag ev-tag-stage"><?php echo esc_html($s); ?></span>
      <?php endforeach; ?>
    </div>
  </div>
  <div class="ev-story-split-right">
    <img src="<?php echo esc_url($thumb_url); ?>" alt="<?php echo esc_attr($title); ?> — The Evolved Brisbane">
  </div>
</div>
<?php else: ?>
<div class="ev-story-hero-fallback">
  <p class="eyebrow">Member Story</p>
  <h1><?php echo esc_html($title); ?></h1>
  <div class="ev-story-tags">
    <?php foreach ($goals as $g): ?>
      <span class="ev-tag ev-tag-goal"><?php echo esc_html($g); ?></span>
    <?php endforeach; ?>
    <?php foreach ($stages as $s): ?>
      <span class="ev-tag ev-tag-stage"><?php echo esc_html($s); ?></span>
    <?php endforeach; ?>
  </div>
</div>
<?php endif; ?>

<?php echo $content; ?>

<div class="ev-story-cta-bar">
  <h2>Your Story Could Be Next</h2>
  <p>Spots at The Evolved are limited and currently by waitlist only. Join now and we&rsquo;ll be in touch as soon as a spot opens for you.</p>
  <a href="/">Join The Waitlist</a>
</div>

<div class="ev-story-footer-bar">
  <a href="/results/">&#8592; Read more member stories</a>
</div>

<?php wp_footer(); ?>
</body>
</html>
