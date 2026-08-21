<?php
/**
 * Results CPT archive — filterable hub at /results/
 * Hardcoded member grid with vanilla JS goal + life stage filtering.
 */

$p = 'https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/';
$members = [
  // 20s–30s
  ['name'=>'Alana',    'label'=>'London Bound, 20s',     'result'=>'Lost 12kg in 5 months — then moved to London and absolutely crushed it.',                        'goals'=>'weight-loss',           'stage'=>'20s-30s',     'color'=>'#0e1628','photo'=>$p.'alana-20s-6m.png',              'link'=>'/results/twenties-thirties-weight-loss-strength'],
  ['name'=>'Monique',  'label'=>'Uni Student, 20s',      'result'=>'Lost 12.8kg and doubled her squat from 26kg to 63kg in 5 months.',                               'goals'=>'aesthetics',            'stage'=>'20s-30s',     'color'=>'#0e1628','photo'=>$p.'monique-20s-transformation.png', 'link'=>'/results/twenties-thirties-aesthetics-glutes'],
  ['name'=>'Isabelle', 'label'=>'Gym Newbie, 20s',       'result'=>'Never set foot in a gym — thrived through community and consistency.',                            'goals'=>'strength',              'stage'=>'20s-30s',     'color'=>'#0e1628','photo'=>$p.'isabelle-20s-12m.png',           'link'=>'/results/twenties-thirties-strength-first-time'],
  ['name'=>'Nikki',    'label'=>'Bride, 20s',            'result'=>'Reached goal weight and ditched binge eating for good.',                                          'goals'=>'mental-health weight-loss','stage'=>'20s-30s',  'color'=>'#0e1628','photo'=>$p.'nikki-20s-18m.png',              'link'=>'/results/twenties-wedding-weight-loss-confidence'],
  ['name'=>'Emma',     'label'=>'Age 21, 20s',           'result'=>'Lost 1.6kg fat and built 1kg muscle — the scale barely moved.',                                   'goals'=>'aesthetics',            'stage'=>'20s-30s',     'color'=>'#0e1628','photo'=>$p.'emma-20s-6m.png',                 'link'=>'/results/twenties-body-recomposition-scale-didnt-move'],
  ['name'=>'Katrina',  'label'=>'FIFO Worker, 20s',      'result'=>'Lost 20kg while training four days a week on a mine site.',                                       'goals'=>'weight-loss',           'stage'=>'20s-30s',     'color'=>'#0e1628','photo'=>$p.'katrina-20s-12m.png',             'link'=>'/results/twenties-weight-loss-fifo-confidence'],
  ['name'=>'Rudra',    'label'=>'20s, Brisbane',         'result'=>'Moved to Brisbane not knowing anyone. Found her confidence — and a community that changed her mental health.', 'goals'=>'mental-health', 'stage'=>'20s-30s','color'=>'#0e1628','photo'=>'https://img.youtube.com/vi/yPJ2xlNtkxk/hqdefault.jpg', 'link'=>'/results/twenties-thirties-mental-health-gym'],
  ['name'=>'Katherine','label'=>'Teacher, 30s',          'result'=>'Lost 15kg in 6 months after years of on-again-off-again attempts.',                               'goals'=>'weight-loss',           'stage'=>'20s-30s',     'color'=>'#0e1628','photo'=>$p.'katherine-30s-6m.png',          'link'=>'/results/weight-loss-plateau-broken-strength'],
  ['name'=>'Charmaine','label'=>'Defence, 30s',          'result'=>'Lost 10kg in 6 months — through chronic back pain and a broken leg.',                            'goals'=>'weight-loss return-to-fitness','stage'=>'20s-30s','color'=>'#0e1628','photo'=>$p.'charmaine-30s-12m.png',        'link'=>'/results/return-to-fitness-after-injury'],
  ['name'=>'Kat',      'label'=>'2 Kids, 30s',           'result'=>'Said she might never have joined a gym — went from complete newbie to gym confident.',            'goals'=>'strength',              'stage'=>'20s-30s',     'color'=>'#0e1628','photo'=>$p.'kat-30s-6m.png',                 'link'=>'/results/thirties-mum-gym-confidence-strength'],
  ['name'=>'Leisa',    'label'=>'Personal Trainer, 30s', 'result'=>'Former powerlifter. Transformed her body composition and ran her first marathon at 12 months.',  'goals'=>'strength aesthetics',   'stage'=>'20s-30s',     'color'=>'#0e1628','photo'=>$p.'leisa-30s-transformation.png',    'link'=>'/results/thirties-strength-recomposition-marathon'],
  ['name'=>'Jess',    'label'=>'Age 29, Brisbane',      'result'=>'5 years of gym-going with no real results — found progressive overload, achieved body recomposition, and completed HYROX.',  'goals'=>'hyrox aesthetics strength', 'stage'=>'20s-30s',   'color'=>'#0e1628','photo'=>'https://img.youtube.com/vi/7ud-x3UXcfM/hqdefault.jpg', 'link'=>'/results/twenties-strength-recomposition-hyrox'],
  // Postpartum
  ['name'=>'Bec',     'label'=>'New Mum, 30s',           'result'=>'Lost her baby weight in 6 months to fit into her wedding dress — then kept going.',                'goals'=>'weight-loss',           'stage'=>'postpartum',  'color'=>'#0a1820','photo'=>$p.'bec-postpartum-before-after.png', 'link'=>'/results/postpartum-wedding-weight-loss'],
  ['name'=>'Ruth',     'label'=>'2 Kids, 30s',           'result'=>'Cut training from 9 hrs to 3 hrs — and dropped 4cm off her waist.',                              'goals'=>'return-to-fitness',     'stage'=>'postpartum',  'color'=>'#0a1820','photo'=>$p.'ruth-30s-12m.png',              'link'=>'/results/postpartum-return-to-fitness-strength-training'],
  ['name'=>'Emma',     'label'=>'2 Kids, 30s',           'result'=>'Stronger, healthier, and genuinely at peace with herself.',                                       'goals'=>'aesthetics mental-health','stage'=>'postpartum', 'color'=>'#0a1820','photo'=>$p.'emma-30s-2kids.png',              'link'=>'/results/thirties-recomposition-mindset-eating-more'],
  ['name'=>'Megan',    'label'=>'2 Kids, 30s',           'result'=>'Eating more and lifting heavy recovered her energy and overhauled her physique.',                 'goals'=>'energy aesthetics',     'stage'=>'postpartum',  'color'=>'#0a1820','photo'=>$p.'megan-30s-12m.png',             'link'=>'/results/energy-fatigue-strength-training'],
  // Pregnancy
  ['name'=>'Kerrie',   'label'=>'3 Kids, 40s',           'result'=>'Controlled gestational diabetes through pregnancy — 2 dress sizes postnatal.',                   'goals'=>'strength return-to-fitness','stage'=>'pregnancy','color'=>'#0a1508','photo'=>$p.'kerrie-40s-12m.png',             'link'=>'/results/pregnancy-safe-strength-training'],
  ['name'=>'Kylie',   'label'=>'4 Kids, 40s',           'result'=>'5kg gone, persistent bloat resolved — and a rhythm that made her a better mum.',                  'goals'=>'weight-loss',           'stage'=>'postpartum',  'color'=>'#0a1820','photo'=>$p.'kylie-40s-6m.png',               'link'=>'/results/postpartum-weight-loss-new-mum'],
  ['name'=>'Peta',     'label'=>'40s, Brisbane',         'result'=>'Wanted to do more strength training. Became an almost-daily habit — and her body changed in ways cardio never delivered.', 'goals'=>'aesthetics strength', 'stage'=>'perimenopause','color'=>'#1a0e28','photo'=>'https://img.youtube.com/vi/15q1XPdx1PU/hqdefault.jpg', 'link'=>'/results/forties-strength-recomposition-daily-ritual'],
  ['name'=>'Sophie',   'label'=>'40s, Brisbane',         'result'=>'Pivoted to landscaping in her 40s and trained to make her body equal to the job.',                              'goals'=>'strength return-to-fitness','stage'=>'perimenopause','color'=>'#1a0e28','photo'=>'https://img.youtube.com/vi/ATNysZlwUvg/hqdefault.jpg', 'link'=>'/results/forties-strength-career-change-landscaping'],
  // Perimenopause
  ['name'=>'Tash',     'label'=>'Night Shift Nurse, 40s','result'=>'Lost 20kg in 14 months. No treadmill. Now she can ride a roller coaster.',                        'goals'=>'weight-loss',           'stage'=>'perimenopause','color'=>'#1a0e28','photo'=>$p.'tash-40s-transformation.png',   'link'=>'/results/perimenopause-weight-loss-brisbane'],
  ['name'=>'Karyn',    'label'=>'2 Kids, 40s',           'result'=>'Lost 12kg and eliminated chronic fatigue and daily back pain.',                                   'goals'=>'weight-loss',           'stage'=>'perimenopause','color'=>'#1a0e28','photo'=>$p.'karyn-40s-12m.png',              'link'=>'/results/perimenopause-weight-loss-back-pain'],
  ['name'=>'Tammy',    'label'=>'2 Kids, 40s',           'result'=>'Dropped 2 dress sizes — and her adenomyosis symptoms disappeared entirely.',                      'goals'=>'hormonal-health aesthetics','stage'=>'perimenopause','color'=>'#1a0e28','photo'=>$p.'tammy-40s-6m.png',         'link'=>'/results/perimenopause-strength-hormonal-health'],
  ['name'=>'Simone',   'label'=>'4 Kids, 40s',           'result'=>'Training reduced her anxiety, improved her sleep, and reconnected her with her own strength.',    'goals'=>'mental-health',         'stage'=>'perimenopause','color'=>'#1a0e28','photo'=>$p.'simone-40s-4kids.png',          'link'=>'/results/perimenopause-energy-mental-health'],
  ['name'=>'Jules',    'label'=>'First Timer, 40s',      'result'=>'Started strength training for the first time at 40 — and built the body she had always wanted.',  'goals'=>'strength aesthetics',   'stage'=>'perimenopause','color'=>'#1a0e28','photo'=>'https://img.youtube.com/vi/pHSmb9jTKoc/hqdefault.jpg', 'link'=>'/results/perimenopause-first-time-strength-training-40s'],
  ['name'=>'Johanna',  'label'=>'Most Consistent, 40s',  'result'=>'6 days/week, 2.5 years. 100kg deadlift. HYROX under 90 min with her daughter.',                  'goals'=>'hyrox strength',        'stage'=>'perimenopause','color'=>'#1a0e28','photo'=>'https://img.youtube.com/vi/W6cDcI7I1zI/hqdefault.jpg', 'link'=>'/results/perimenopause-hyrox-strength-consistency'],
  // Postmenopause
  ['name'=>'Vicky',    'label'=>'Age 50',                'result'=>'Fitness-model lean, abs, 60kg squat, first chin-up — all in 7 weeks.',                           'goals'=>'aesthetics strength',   'stage'=>'postmenopause','color'=>'#1f0a15','photo'=>$p.'vicki-50s-6m.png',               'link'=>'/results/postmenopause-strength-return-to-fitness'],
  ['name'=>'Helen',    'label'=>'Active 60s',            'result'=>'Lost 7kg in 12 weeks despite moving house, rep hockey, and full-time work.',                      'goals'=>'weight-loss',           'stage'=>'postmenopause','color'=>'#1f0a15','photo'=>$p.'helen-50s-transformation.png',   'link'=>'/results/postmenopause-weight-loss-strength-training'],
  ['name'=>'Eleni',    'label'=>'Age 63',                'result'=>'Reversed her osteoporosis diagnosis. Stronger at 63 than she was at 43.',                         'goals'=>'bone-health strength',  'stage'=>'postmenopause','color'=>'#1f0a15','photo'=>$p.'eleni-60s-transformation.png',   'link'=>'/results/postmenopause-bone-health-osteoporosis'],
  ['name'=>'Michelle', 'label'=>'60s, Brisbane',        'result'=>'Cycled for years and thought that was enough. Discovered strength training — and has been getting stronger every month since.', 'goals'=>'strength', 'stage'=>'postmenopause','color'=>'#1f0a15','photo'=>'https://img.youtube.com/vi/W3_KlWQE5Gg/hqdefault.jpg', 'link'=>'/results/over-60-strength-longevity-brisbane'],
  ['name'=>'Jennifer', 'label'=>'Age 64, Brisbane',     'result'=>'Chiropractor referred her to a gym at 64. Her cervical spine pain — which years of treatment couldn\'t fix — resolved within months.', 'goals'=>'bone-health strength', 'stage'=>'postmenopause','color'=>'#1f0a15','photo'=>'https://img.youtube.com/vi/COIm1FmTYOc/hqdefault.jpg', 'link'=>'/results/over-60-bone-density-strength-training'],
  ['name'=>'Belinda',  'label'=>'50s, Brisbane',         'result'=>'Diagnosed with frozen shoulder and couldn\'t hold a glass of water. Now lifting 35kg and moving tonnes of gravel on weekends.', 'goals'=>'strength return-to-fitness', 'stage'=>'postmenopause','color'=>'#1f0a15','photo'=>'https://img.youtube.com/vi/CsICP4wSMG0/hqdefault.jpg', 'link'=>'/results/fifties-strength-frozen-shoulder-rehabilitation'],
  // 20s–30s (additional)
  ['name'=>'Orlagh',   'label'=>'20s, Brisbane',         'result'=>'Started from a baseline of nothing — no gym, no lingo, no sports background. Built genuine strength and confidence from scratch.', 'goals'=>'strength', 'stage'=>'20s-30s','color'=>'#0e1628','photo'=>'https://img.youtube.com/vi/WY01XSdmevk/hqdefault.jpg', 'link'=>'/results/twenties-strength-first-timer-safe-space'],
  ['name'=>'Tess',     'label'=>'30s, Brisbane',         'result'=>'Went from no exercise to a 75kg deadlift and a 37.5kg bench — and drove from Ipswich for a year rather than quit.',             'goals'=>'strength', 'stage'=>'20s-30s','color'=>'#0e1628','photo'=>'https://img.youtube.com/vi/O-ToRNZwB1w/hqdefault.jpg', 'link'=>'/results/thirties-strength-deadlift-desk-worker'],
  ['name'=>'Laura',    'label'=>'20s, Brisbane',         'result'=>'8-year martial artist who doubled her strength and slashed her recovery time — and leaves every session better than she arrived.', 'goals'=>'strength mental-health', 'stage'=>'20s-30s','color'=>'#0e1628','photo'=>'https://img.youtube.com/vi/G2vXxlVJ0nk/hqdefault.jpg', 'link'=>'/results/twenties-strength-martial-arts-mental-health'],
];

$goal_labels = [
  'weight-loss'     => 'Weight Loss',
  'strength'        => 'Get Stronger',
  'hyrox'           => 'Train for HYROX',
  'bone-health'     => 'Bone Health',
  'aesthetics'      => 'Body Recomposition',
  'mental-health'   => 'Mental Health',
  'energy'          => 'Energy',
  'hormonal-health' => 'Hormonal Health',
  'return-to-fitness' => 'Return to Fitness',
];

$stage_labels = [
  '20s-30s'       => '20s &amp; 30s',
  'perimenopause' => 'Perimenopause',
  'postmenopause' => 'Postmenopause',
  'postpartum'    => 'Postpartum',
  'pregnancy'     => 'Pregnancy',
];
?><!DOCTYPE html>
<html <?php language_attributes(); ?>>
<head>
<meta charset="<?php bloginfo('charset'); ?>">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Real Results. Real Women. | The Evolved All Female Gym</title>
<meta name="description" content="Browse transformation stories from members of The Evolved All Female Gym &#8212; strength training results for women across every life stage.">
<?php wp_head(); ?>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { background: #f5f5f5; color: #1a1a1a; font-family: "Inter","Open Sans",sans-serif; }

/* NAV */
.ev-res-nav { background: #111; padding: 14px 24px; display: flex; align-items: center; justify-content: space-between; }
.ev-res-nav a { color: rgba(255,255,255,0.55); font-size: 0.78rem; letter-spacing: 0.08em; text-transform: uppercase; text-decoration: none; }
.ev-res-nav a:hover { color: #e43388; }

/* HERO */
.ev-res-hero { background: #111; padding: 72px 32px 60px; text-align: center; }
.ev-res-hero .eyebrow { color: #e43388; font-size: 0.82rem; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; margin: 0 0 14px; }
.ev-res-hero h1 { color: #fff; font-family: "PT Serif Caption","Playfair Display",Georgia,serif; font-size: clamp(2rem,5vw,3rem); line-height: 1.1; margin: 0 0 16px; }
.ev-res-hero p { color: rgba(255,255,255,0.65); font-size: 1.05rem; max-width: 580px; margin: 0 auto; line-height: 1.75; }

/* FILTER BAR */
.ev-filter-bar { background: #fff; padding: 20px 24px; border-bottom: 1px solid #eee; position: sticky; top: 0; z-index: 100; box-shadow: 0 2px 12px rgba(0,0,0,0.06); }
.ev-filter-row { display: flex; align-items: center; gap: 10px; max-width: 1100px; margin: 0 auto; min-width: 0; }
.ev-filter-row + .ev-filter-row { margin-top: 8px; }
.ev-filter-label { font-size: 0.72rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: #888; white-space: nowrap; flex-shrink: 0; min-width: 56px; }
.ev-pills { display: flex; gap: 6px; overflow-x: auto; flex-wrap: nowrap; -webkit-overflow-scrolling: touch; scrollbar-width: none; padding-bottom: 2px; min-width: 0; }
.ev-pills::-webkit-scrollbar { display: none; }
.ev-pill { background: #f0f0f0; color: #555; border: none; cursor: pointer; padding: 7px 14px; border-radius: 100px; font-size: 0.78rem; font-weight: 600; letter-spacing: 0.04em; transition: all 0.15s; white-space: nowrap; flex-shrink: 0; }
.ev-pill:hover { background: rgba(228,51,136,0.12); color: #e43388; }
.ev-pill.active { background: #e43388; color: #fff; }
@media (max-width: 540px) {
  .ev-filter-bar { padding: 12px 16px; }
  .ev-filter-row + .ev-filter-row { margin-top: 6px; }
  .ev-filter-label { font-size: 0.68rem; min-width: 44px; }
  .ev-pill { padding: 6px 12px; font-size: 0.74rem; }
}

/* RESULTS COUNT */
.ev-res-count { text-align: center; padding: 20px; font-size: 0.82rem; color: #888; letter-spacing: 0.06em; }

/* GRID */
.ev-res-grid { display: grid; grid-template-columns: repeat(3,1fr); gap: 20px; max-width: 1100px; margin: 0 auto; padding: 0 24px 64px; }
@media (max-width: 900px) { .ev-res-grid { grid-template-columns: repeat(2,1fr); } }
@media (max-width: 540px) { .ev-res-grid { grid-template-columns: 1fr; } }

/* CARD */
.result-card { background: #fff; border-radius: 10px; overflow: hidden; display: flex; flex-direction: column; box-shadow: 0 1px 6px rgba(0,0,0,0.07); transition: transform 0.18s, box-shadow 0.18s; }
.result-card:hover { transform: translateY(-3px); box-shadow: 0 6px 24px rgba(0,0,0,0.12); }
.card-avatar { height: 180px; display: flex; align-items: center; justify-content: center; font-family: "PT Serif Caption","Playfair Display",Georgia,serif; font-size: 3rem; color: rgba(255,255,255,0.7); font-weight: 400; }
.card-photo { line-height: 0; }
.card-photo img { width: 100%; height: auto; display: block; }
.card-body { padding: 22px; flex: 1; display: flex; flex-direction: column; }
.card-tags { display: flex; flex-wrap: wrap; gap: 6px; margin: 0 0 12px; }
.card-tag-goal { background: rgba(228,51,136,0.1); color: #c01070; font-size: 0.7rem; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase; padding: 4px 10px; border-radius: 100px; }
.card-tag-stage { background: #f0f0f0; color: #666; font-size: 0.7rem; font-weight: 600; letter-spacing: 0.04em; text-transform: uppercase; padding: 4px 10px; border-radius: 100px; }
.card-name { font-family: "PT Serif Caption","Playfair Display",Georgia,serif; font-size: 1.2rem; color: #1a1a1a; margin: 0 0 2px; }
.card-label { font-size: 0.78rem; color: #888; margin: 0 0 14px; }
.card-result { font-size: 0.88rem; color: #333; line-height: 1.65; flex: 1; margin: 0 0 18px; font-style: italic; }
.card-link { display: inline-block; font-size: 0.78rem; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; color: #e43388 !important; text-decoration: none; }
.card-link:hover { text-decoration: underline; }

/* EMPTY STATE */
.ev-empty { text-align: center; padding: 80px 24px; display: none; }
.ev-empty h3 { font-size: 1.2rem; color: #555; margin: 0 0 12px; }
.ev-empty p { color: #888; font-size: 0.9rem; }

/* CTA SECTION */
.ev-res-cta { background: #111; padding: 80px 32px; text-align: center; }
.ev-res-cta h2 { color: #fff; font-family: "PT Serif Caption","Playfair Display",Georgia,serif; font-size: clamp(1.6rem,3.5vw,2.2rem); margin: 0 0 16px; }
.ev-res-cta p { color: rgba(255,255,255,0.65); font-size: 1rem; max-width: 520px; margin: 0 auto 28px; line-height: 1.75; }
.ev-res-cta a { display: inline-block; background: #e43388; color: #fff !important; font-weight: 700; font-size: 0.95rem; text-decoration: none; padding: 15px 36px; letter-spacing: 0.06em; text-transform: uppercase; }
</style>
</head>
<body <?php body_class('evolved-results-hub'); ?>>
<?php wp_body_open(); ?>

<nav class="ev-res-nav">
  <a href="/">&#8592; The Evolved</a>
  <a href="/results/">All Results</a>
</nav>

<div class="ev-res-hero">
  <p class="eyebrow">Member Transformations</p>
  <h1>Real Women. Real Results.</h1>
  <p>Every story below is a real member of The Evolved. Filter by your goal or life stage to find the one that feels like yours.</p>
</div>

<div class="ev-filter-bar">
  <div class="ev-filter-row">
    <span class="ev-filter-label">Goal</span>
    <div class="ev-pills" id="goal-pills">
      <button class="ev-pill active" data-filter="goal" data-value="all">All Goals</button>
      <?php foreach ($goal_labels as $val => $label): ?>
        <button class="ev-pill" data-filter="goal" data-value="<?php echo $val; ?>"><?php echo $label; ?></button>
      <?php endforeach; ?>
    </div>
  </div>
  <div class="ev-filter-row">
    <span class="ev-filter-label">Life Stage</span>
    <div class="ev-pills" id="stage-pills">
      <button class="ev-pill active" data-filter="stage" data-value="all">All Stages</button>
      <?php foreach ($stage_labels as $val => $label): ?>
        <button class="ev-pill" data-filter="stage" data-value="<?php echo $val; ?>"><?php echo $label; ?></button>
      <?php endforeach; ?>
    </div>
  </div>
</div>

<div class="ev-res-count" id="results-count"></div>

<div class="ev-res-grid" id="results-grid">

<?php
$multi_goal_labels = [
  'weight-loss'     => 'Weight Loss',
  'strength'        => 'Get Stronger',
  'hyrox'           => 'Train for HYROX',
  'bone-health'     => 'Bone Health',
  'aesthetics'      => 'Body Recomposition',
  'mental-health'   => 'Mental Health',
  'energy'          => 'Energy',
  'hormonal-health' => 'Hormonal Health',
  'return-to-fitness' => 'Return to Fitness',
];
foreach ($members as $m):
  $goals_arr = explode(' ', $m['goals']);
  $first_goal = $goals_arr[0];
  $goal_label = $multi_goal_labels[$first_goal] ?? $first_goal;
  $stage_label_text = strip_tags($stage_labels[$m['stage']] ?? $m['stage']);
  $initial = mb_strtoupper(mb_substr($m['name'], 0, 1));
  $is_external = strpos($m['link'], 'http') === 0;
  $link_label = $is_external ? 'Join The Waitlist &#8594;' : 'Read Her Story &#8594;';
?>
<div class="result-card" data-goal="<?php echo esc_attr($m['goals']); ?>" data-stage="<?php echo esc_attr($m['stage']); ?>">
<?php if (!empty($m['photo'])): ?>
  <div class="card-photo"><img src="<?php echo esc_url($m['photo']); ?>" alt="<?php echo esc_attr($m['name']); ?> transformation result at The Evolved Brisbane" loading="lazy"></div>
<?php else: ?>
  <div class="card-avatar" style="background:<?php echo $m['color']; ?>;"><?php echo $initial; ?></div>
<?php endif; ?>
  <div class="card-body">
    <div class="card-tags">
      <span class="card-tag-goal"><?php echo esc_html($goal_label); ?></span>
      <span class="card-tag-stage"><?php echo esc_html($stage_label_text); ?></span>
    </div>
    <h3 class="card-name"><?php echo esc_html($m['name']); ?></h3>
    <p class="card-label"><?php echo esc_html($m['label']); ?></p>
    <p class="card-result"><?php echo esc_html($m['result']); ?></p>
    <a href="<?php echo esc_url($m['link']); ?>" class="card-link"><?php echo $link_label; ?></a>
  </div>
</div>
<?php endforeach; ?>

</div>

<div class="ev-empty" id="empty-state">
  <h3>No stories match those filters yet.</h3>
  <p>We&rsquo;re adding more member stories every week. Try a different filter or <a href="/results/" style="color:#e43388;">view all results</a>.</p>
</div>

<div class="ev-res-cta">
  <h2>Ready to Write Your Own Story?</h2>
  <p>Spots at The Evolved are limited and currently by waitlist only. Join now and we&rsquo;ll be in touch as soon as a spot opens for you.</p>
  <a href="/">Join The Waitlist</a>
</div>

<script>
(function(){
  var activeGoal = 'all';
  var activeStage = 'all';

  var relatedGoals = {
    'weight-loss': ['aesthetics'],
    'aesthetics':  ['weight-loss']
  };

  function filterCards() {
    var cards = document.querySelectorAll('.result-card');
    var visible = 0;
    cards.forEach(function(card) {
      var goalAttr = card.getAttribute('data-goal') || '';
      var stageAttr = card.getAttribute('data-stage') || '';
      var goalsToMatch = activeGoal === 'all' ? [] : [activeGoal].concat(relatedGoals[activeGoal] || []);
      var goalMatch = activeGoal === 'all' || goalAttr.split(' ').some(function(g){ return goalsToMatch.indexOf(g) !== -1; });
      var stageMatch = activeStage === 'all' || stageAttr === activeStage;
      if (goalMatch && stageMatch) {
        card.style.display = 'flex';
        visible++;
      } else {
        card.style.display = 'none';
      }
    });
    var count = document.getElementById('results-count');
    var empty = document.getElementById('empty-state');
    if (visible === 0) {
      count.textContent = '';
      empty.style.display = 'block';
    } else {
      count.textContent = visible + ' ' + (visible === 1 ? 'story' : 'stories');
      empty.style.display = 'none';
    }
  }

  document.querySelectorAll('.ev-pill').forEach(function(btn) {
    btn.addEventListener('click', function() {
      var filter = btn.getAttribute('data-filter');
      var value = btn.getAttribute('data-value');
      if (filter === 'goal') {
        activeGoal = value;
        document.querySelectorAll('#goal-pills .ev-pill').forEach(function(b){ b.classList.remove('active'); });
      } else {
        activeStage = value;
        document.querySelectorAll('#stage-pills .ev-pill').forEach(function(b){ b.classList.remove('active'); });
      }
      btn.classList.add('active');
      filterCards();
    });
  });

  // Initial count
  filterCards();
})();
</script>

<?php wp_footer(); ?>
</body>
</html>
