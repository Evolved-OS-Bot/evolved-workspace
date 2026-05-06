<?php
/**
 * Template Name: Trainer Page (Full Width)
 *
 * Post content: page-specific sections (hero → story → CTA → FAQ)
 * Template appends shared sections matching homepage design exactly:
 *   - Real Women. Real Results. (transformation carousel)
 *   - In Their Own Words (video carousel)
 *   - Google Reviews
 *   - Footer
 *
 * To add a new video: add a .video-card block to the video carousel below.
 * To add a transformation: add a .carousel-card block to the results carousel.
 * Both update all trainer pages automatically.
 */
?><!DOCTYPE html>
<html <?php language_attributes(); ?>>
<head>
<meta charset="<?php bloginfo('charset'); ?>">
<meta name="viewport" content="width=device-width, initial-scale=1">
<?php wp_head(); ?>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { background: #0a0a0a; color: #1a1a1a; font-family: "Inter", "Open Sans", sans-serif; }
@media (max-width: 640px) {
  .tr-footer-grid { grid-template-columns: 1fr !important; }
}
</style>
</head>
<body <?php body_class('evolved-trainer-page'); ?>>
<?php wp_body_open(); ?>
<main>
<?php
while (have_posts()) {
    the_post();
    echo get_post_field('post_content', get_the_ID());
}
?>
</main>


<!-- ─── REAL WOMEN. REAL RESULTS. ───────────────────────────────── -->
<section style="background:#111;padding:80px 0;">
<div style="max-width:960px;margin:0 auto;padding:0 24px;">
<h2 style="font-family:'PT Serif Caption',serif;font-size:clamp(1.5rem,3vw,2.2rem);color:#1a1a1a;text-align:center;margin-bottom:12px;">Real Women. Real Results.</h2>
<p style="color:#aaa;text-align:center;margin-bottom:48px;">Here&#39;s what happens when women stop guessing and start training with structure.</p>
</div>
<div style="padding:0 24px;">
<div class="carousel-viewport" style="overflow:hidden;position:relative;cursor:grab;user-select:none;">
<div class="carousel-track" style="display:flex;flex-wrap:nowrap;gap:12px;will-change:transform;">

<div class="carousel-card" data-goal="recomp" data-decade="20s" style="flex:0 0 calc(33.333% - 8px);min-width:200px;text-align:center;">
<img src="https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/monique-20s-transformation.png" alt="Monique transformation at The Evolved Brisbane" style="width:100%;aspect-ratio:1/1;object-fit:cover;border-radius:8px;margin-bottom:16px;display:block;">
<p style="color:#e43388;font-size:0.8rem;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;">Monique, Uni Student</p>
<p style="color:#aaa;font-size:0.85rem;line-height:1.65;margin-top:8px;">Returning to the gym after years away, balancing uni and work, Monique wanted her strength back. Post-Japan, she locked in on training and nutrition &#8212; lost 12.8kg in 5 months and doubled her squat from 26kg to 63kg.</p>
</div>

<div class="carousel-card" data-goal="lose-weight" data-decade="20s" style="flex:0 0 calc(33.333% - 8px);min-width:200px;text-align:center;">
<img src="https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/katrina-20s-12m.png" alt="Katrina FIFO transformation at The Evolved Brisbane" style="width:100%;aspect-ratio:1/1;object-fit:cover;border-radius:8px;margin-bottom:16px;display:block;">
<p style="color:#e43388;font-size:0.8rem;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;">Katrina, FIFO Worker</p>
<p style="color:#aaa;font-size:0.85rem;line-height:1.65;margin-top:8px;">Working FIFO on-site, Katrina trained four days a week and said goodbye to takeaway &#8212; even from the mine site. She wanted to lose 20kg and be able to shop in the same stores as her friends. A quiet achiever who let her results do the talking. She did both.</p>
</div>

<div class="carousel-card" data-goal="recomp" data-decade="30s" style="flex:0 0 calc(33.333% - 8px);min-width:200px;text-align:center;">
<img src="https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/ruth-30s-12m.png" alt="Ruth transformation at The Evolved Brisbane" style="width:100%;aspect-ratio:1/1;object-fit:cover;border-radius:8px;margin-bottom:16px;display:block;">
<p style="color:#e43388;font-size:0.8rem;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;">Ruth, 2 Kids</p>
<p style="color:#aaa;font-size:0.85rem;line-height:1.65;margin-top:8px;">After her second child, Ruth was training 9 hours a week and burning out. She cut to 3 hours, shifted focus to recovery and nutrition, dropped 4cm off her waist &#8212; and finally found the balance she&#39;d been chasing.</p>
</div>

<div class="carousel-card" data-goal="gain-muscle" data-decade="30s" style="flex:0 0 calc(33.333% - 8px);min-width:200px;text-align:center;">
<img src="https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/megan-30s-12m.png" alt="Megan transformation at The Evolved Brisbane" style="width:100%;aspect-ratio:1/1;object-fit:cover;border-radius:8px;margin-bottom:16px;display:block;">
<p style="color:#e43388;font-size:0.8rem;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;">Megan, 2 Kids</p>
<p style="color:#aaa;font-size:0.85rem;line-height:1.65;margin-top:8px;">Chronic exhaustion had Megan at breaking point. &#8220;Someone as healthy as me shouldn&#39;t feel this way.&#8221; The big unlock: she wasn&#39;t eating enough. Eating more and lifting heavy overhauled her physique, reclaimed her energy, and gave her the vitality she thought she&#39;d lost for good.</p>
</div>

<div class="carousel-card" data-goal="lose-weight" data-decade="30s" style="flex:0 0 calc(33.333% - 8px);min-width:200px;text-align:center;">
<img src="https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/charmaine-30s-12m.png" alt="Charmaine transformation at The Evolved Brisbane" style="width:100%;aspect-ratio:1/1;object-fit:cover;border-radius:8px;margin-bottom:16px;display:block;">
<p style="color:#e43388;font-size:0.8rem;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;">Charmaine, Defence</p>
<p style="color:#aaa;font-size:0.85rem;line-height:1.65;margin-top:8px;">A remote-working defence force mum battling chronic back pain and a broken leg &#8212; Charmaine had every reason to quit. Instead she adapted, stayed consistent, and lost 10kg in 6 months. No excuses. Just progress.</p>
</div>

<div class="carousel-card" data-goal="lose-weight" data-decade="40s" style="flex:0 0 calc(33.333% - 8px);min-width:200px;text-align:center;">
<img src="https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/tash-40s-transformation.png" alt="Tash 20kg transformation at The Evolved Brisbane" style="width:100%;aspect-ratio:1/1;object-fit:cover;border-radius:8px;margin-bottom:16px;display:block;">
<p style="color:#e43388;font-size:0.8rem;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;">Tash, Night Shift Nurse</p>
<p style="color:#aaa;font-size:0.85rem;line-height:1.65;margin-top:8px;">Her doctor&#39;s warning was stark: lose weight or your heart condition deteriorates within five years. As a night-shift nurse addicted to Coca-Cola, Tash chose strength over cardio &#8212; and lost 20kg in 14 months without a single treadmill session. Her personal goal underneath it all: to finally be able to ride a roller coaster. She can now.</p>
</div>

<div class="carousel-card" data-goal="recomp" data-decade="40s" style="flex:0 0 calc(33.333% - 8px);min-width:200px;text-align:center;">
<img src="https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/tammy-40s-6m.png" alt="Tammy transformation at The Evolved Brisbane" style="width:100%;aspect-ratio:1/1;object-fit:cover;border-radius:8px;margin-bottom:16px;display:block;">
<p style="color:#e43388;font-size:0.8rem;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;">Tammy, 2 Kids</p>
<p style="color:#aaa;font-size:0.85rem;line-height:1.65;margin-top:8px;">Tammy came in stressed and wanting to change how her body looked. She didn&#39;t realise the connection between her body composition and her adenomyosis. Through consistent strength training and eating well, her inflammation reduced, her painful periods disappeared entirely, and she dropped two dress sizes. A body goal led to a life-changing health discovery.</p>
</div>

<div class="carousel-card" data-goal="recomp" data-decade="40s" style="flex:0 0 calc(33.333% - 8px);min-width:200px;text-align:center;">
<img src="https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/kylie-40s-6m.png" alt="Kylie transformation at The Evolved Brisbane" style="width:100%;aspect-ratio:1/1;object-fit:cover;border-radius:8px;margin-bottom:16px;display:block;">
<p style="color:#e43388;font-size:0.8rem;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;">Kylie, 4 Kids</p>
<p style="color:#aaa;font-size:0.85rem;line-height:1.65;margin-top:8px;">Four kids and a habit of putting herself last &#8212; Kylie decided to do something just for herself for the first time. She came in wanting to get rid of persistent lower tummy bloat. The 5kg loss wasn&#39;t a defined goal, but that&#39;s when the bloat disappeared and she felt better than ever. Through the process she found a rhythm that made her a better mum, not a more absent one.</p>
</div>

<div class="carousel-card" data-goal="recomp" data-decade="40s" style="flex:0 0 calc(33.333% - 8px);min-width:200px;text-align:center;">
<img src="https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/kerrie-40s-12m.png" alt="Kerrie transformation at The Evolved Brisbane" style="width:100%;aspect-ratio:1/1;object-fit:cover;border-radius:8px;margin-bottom:16px;display:block;">
<p style="color:#e43388;font-size:0.8rem;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;">Kerrie, 3 Kids</p>
<p style="color:#aaa;font-size:0.85rem;line-height:1.65;margin-top:8px;">Kerrie&#39;s biggest fear was another premature birth. When gestational diabetes appeared, it became the moment everything changed. She committed through pregnancy &#8212; and it paid off. Two dress sizes in 12 months, controlled gestational diabetes, and a faster postnatal recovery. Her goal for Christmas: a size 10 swimsuit. She nailed it.</p>
</div>

<div class="carousel-card" data-goal="recomp" data-decade="50s" style="flex:0 0 calc(33.333% - 8px);min-width:200px;text-align:center;">
<img src="https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/vicki-50s-6m.png" alt="Vicky transformation at The Evolved Brisbane aged 50" style="width:100%;aspect-ratio:1/1;object-fit:cover;border-radius:8px;margin-bottom:16px;display:block;">
<p style="color:#e43388;font-size:0.8rem;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;">Vicky, Age 50</p>
<p style="color:#aaa;font-size:0.85rem;line-height:1.65;margin-top:8px;">Vicky gave herself one goal for her 50th: a fitness photoshoot that showed exactly what she was capable of. She enrolled in Fast Track, committed completely, and in 7 weeks unlocked visible abs, a 60kg squat, and her first ever chin-up. The photoshoot happened. The photos are extraordinary.</p>
</div>

<div class="carousel-card" data-goal="lose-weight" data-decade="60s" style="flex:0 0 calc(33.333% - 8px);min-width:200px;text-align:center;">
<img src="https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/helen-50s-transformation.png" alt="Helen transformation at The Evolved Brisbane" style="width:100%;aspect-ratio:1/1;object-fit:cover;border-radius:8px;margin-bottom:16px;display:block;">
<p style="color:#e43388;font-size:0.8rem;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;">Helen, Grandma</p>
<p style="color:#aaa;font-size:0.85rem;line-height:1.65;margin-top:8px;">Moving house, state rep hockey, full-time work, and volunteering &#8212; Helen&#39;s 12 weeks were anything but ideal. She showed up anyway, made progress every session, and lost 7kg. Life will always be busy. You can still put yourself first.</p>
</div>

<div class="carousel-card" data-goal="bone-density" data-decade="60s" style="flex:0 0 calc(33.333% - 8px);min-width:200px;text-align:center;">
<img src="https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/eleni-60s-transformation.png" alt="Eleni transformation at The Evolved Brisbane aged 63" style="width:100%;aspect-ratio:1/1;object-fit:cover;border-radius:8px;margin-bottom:16px;display:block;">
<p style="color:#e43388;font-size:0.8rem;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;">Eleni, Osteoporosis</p>
<p style="color:#aaa;font-size:0.85rem;line-height:1.65;margin-top:8px;">Diagnosed with osteoporosis, Leni stepped up from Pilates to strength training. From the moment she walked into The Evolved it felt right &#8212; down-to-earth, no frills. Strength and mental wellbeing both transformed. Stronger at 63 than she was at 43.</p>
</div>

<div class="carousel-card" data-goal="lose-weight" data-decade="20s" style="flex:0 0 calc(33.333% - 8px);min-width:200px;text-align:center;">
<img src="https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/nikki-20s-18m.png" alt="Nikki transformation at The Evolved Brisbane" style="width:100%;aspect-ratio:1/1;object-fit:cover;border-radius:8px;margin-bottom:16px;display:block;">
<p style="color:#e43388;font-size:0.8rem;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;">Nikki, Bride</p>
<p style="color:#aaa;font-size:0.85rem;line-height:1.65;margin-top:8px;">Nikki&#39;s wedding prep became a quest for confidence, not just a dress size. She reached her goal weight, tackled social dining guilt-free, and ditched binge eating for good. She felt genuine joy on her wedding day &#8212; and found abs she didn&#39;t know she had.</p>
</div>

<div class="carousel-card" data-goal="recomp" data-decade="20s" style="flex:0 0 calc(33.333% - 8px);min-width:200px;text-align:center;">
<img src="https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/emma-20s-6m.png" alt="Emma transformation at The Evolved Brisbane" style="width:100%;aspect-ratio:1/1;object-fit:cover;border-radius:8px;margin-bottom:16px;display:block;">
<p style="color:#e43388;font-size:0.8rem;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;">Emma, Age 21</p>
<p style="color:#aaa;font-size:0.85rem;line-height:1.65;margin-top:8px;">Emma lost just 600g on the scales &#8212; but the real story was underneath. She burned 1.6kg of fat and built 1kg of muscle, reshaping her body in ways the scale could never show. Proof that body composition matters more than weight.</p>
</div>

<div class="carousel-card" data-goal="get-stronger" data-decade="30s" style="flex:0 0 calc(33.333% - 8px);min-width:200px;text-align:center;">
<img src="https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/kat-30s-6m.png" alt="Kat transformation at The Evolved Brisbane" style="width:100%;aspect-ratio:1/1;object-fit:cover;border-radius:8px;margin-bottom:16px;display:block;">
<p style="color:#e43388;font-size:0.8rem;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;">Kat, 2 Kids</p>
<p style="color:#aaa;font-size:0.85rem;line-height:1.65;margin-top:8px;">Kat said she might never have joined a gym without The Evolved&#39;s influence. Starting with two sessions a week, she built confidence session by session until the weights felt like home. Gym newbie to gym confident &#8212; and it shows.</p>
</div>

<div class="carousel-card" data-goal="lose-weight" data-decade="30s" style="flex:0 0 calc(33.333% - 8px);min-width:200px;text-align:center;">
<img src="https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/katherine-30s-6m.png" alt="Katherine transformation at The Evolved Brisbane" style="width:100%;aspect-ratio:1/1;object-fit:cover;border-radius:8px;margin-bottom:16px;display:block;">
<p style="color:#e43388;font-size:0.8rem;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;">Katherine, Teacher</p>
<p style="color:#aaa;font-size:0.85rem;line-height:1.65;margin-top:8px;">Years of on-again-off-again training felt like failure. But each attempt made Katherine stronger. Then something clicked &#8212; she committed fully and lost 15kg in just 6 months. Every restart was a step closer. She just didn&#39;t know how close she was.</p>
</div>

<div class="carousel-card" data-goal="lose-weight" data-decade="40s" style="flex:0 0 calc(33.333% - 8px);min-width:200px;text-align:center;">
<img src="https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/karyn-40s-12m.png" alt="Karyn transformation at The Evolved Brisbane" style="width:100%;aspect-ratio:1/1;object-fit:cover;border-radius:8px;margin-bottom:16px;display:block;">
<p style="color:#e43388;font-size:0.8rem;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;">Karyn, 2 Kids</p>
<p style="color:#aaa;font-size:0.85rem;line-height:1.65;margin-top:8px;">Surviving on 3-4 hours sleep, battling chronic fatigue and joint pain, Karyn ditched quick fixes and built sustainable habits instead. Lost 12kg, eliminated daily back pain, and created healthier family routines. Her advice: take that first step. The change will be more profound than you imagine.</p>
</div>

<div class="carousel-card" data-goal="recomp" data-decade="30s" style="flex:0 0 calc(33.333% - 8px);min-width:200px;text-align:center;">
<img src="https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/emma-30s-2kids.png" alt="Emma transformation at The Evolved Brisbane" style="width:100%;aspect-ratio:1/1;object-fit:cover;border-radius:8px;margin-bottom:16px;display:block;">
<p style="color:#e43388;font-size:0.8rem;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;">Emma, 2 Kids</p>
<p style="color:#aaa;font-size:0.85rem;line-height:1.65;margin-top:8px;">Emma believed eating less and training more was the answer &#8212; until exhaustion and stagnation proved otherwise. At The Evolved she discovered nourishing her body, training smart, and embracing self-kindness were the real catalysts. Now she stands stronger, healthier, and genuinely at peace with herself.</p>
</div>

<div class="carousel-card" data-goal="recomp" data-decade="40s" style="flex:0 0 calc(33.333% - 8px);min-width:200px;text-align:center;">
<img src="https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/simone-40s-4kids.png" alt="Simone transformation at The Evolved Brisbane" style="width:100%;aspect-ratio:1/1;object-fit:cover;border-radius:8px;margin-bottom:16px;display:block;">
<p style="color:#e43388;font-size:0.8rem;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;">Simone, 4 Kids</p>
<p style="color:#aaa;font-size:0.85rem;line-height:1.65;margin-top:8px;">Four kids, a nursing career, and a habit of putting herself last &#8212; Simone once felt lost and overwhelmed by self-doubt. Training became her sanctuary. It improved her sleep, reduced her anxiety, and reminded her she had the strength within all along.</p>
</div>

<div class="carousel-card" data-goal="get-stronger" data-decade="60s" style="flex:0 0 calc(33.333% - 8px);min-width:200px;text-align:center;">
<img src="https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/helen-new-gym.png" alt="Helen transformation at The Evolved Brisbane" style="width:100%;aspect-ratio:1/1;object-fit:cover;border-radius:8px;margin-bottom:16px;display:block;">
<p style="color:#e43388;font-size:0.8rem;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;">Helen, New to Gym</p>
<p style="color:#aaa;font-size:0.85rem;line-height:1.65;margin-top:8px;">Helen had never stepped foot in a gym before. She knew she wanted to get stronger but had no idea where to start. Six months later, she&#39;d lost 14.3kg and was confidently deadlifting 90kg. More than the weight she lifted, she gained belief in herself.</p>
</div>

<div class="carousel-card" data-goal="lose-weight" data-decade="20s" style="flex:0 0 calc(33.333% - 8px);min-width:200px;text-align:center;">
<img src="https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/alana-20s-6m.png" alt="Alana transformation at The Evolved Brisbane" style="width:100%;aspect-ratio:1/1;object-fit:cover;border-radius:8px;margin-bottom:16px;display:block;">
<p style="color:#e43388;font-size:0.8rem;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;">Alana, London Bound</p>
<p style="color:#aaa;font-size:0.85rem;line-height:1.65;margin-top:8px;">Alana had a plan: move to London and live life on her terms. She knew that life required strength, confidence, and a body she was proud of. Six months, 10kg down, and a completely transformed version of herself. She moved to London. She&#39;s absolutely crushing it.</p>
</div>

<div class="carousel-card" data-goal="get-stronger" data-decade="20s" style="flex:0 0 calc(33.333% - 8px);min-width:200px;text-align:center;">
<img src="https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/isabelle-20s-12m.png" alt="Isabelle transformation at The Evolved Brisbane" style="width:100%;aspect-ratio:1/1;object-fit:cover;border-radius:8px;margin-bottom:16px;display:block;">
<p style="color:#e43388;font-size:0.8rem;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;">Isabelle, Gym Newbie</p>
<p style="color:#aaa;font-size:0.85rem;line-height:1.65;margin-top:8px;">Standing at a crossroads before starting full-time work, Isabelle looked at her before photo and chose the path she actually wanted &#8212; strong, confident, and in control. She&#39;d never set foot in a gym. But with a community of women behind her and consistency as her guide, she absolutely thrived.</p>
</div>

<div class="carousel-card" data-goal="get-stronger" data-decade="30s" style="flex:0 0 calc(33.333% - 8px);min-width:200px;text-align:center;">
<img src="https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/leisa-30s-transformation.png" alt="Leisa transformation at The Evolved Brisbane" style="width:100%;aspect-ratio:1/1;object-fit:cover;border-radius:8px;margin-bottom:16px;display:block;">
<p style="color:#e43388;font-size:0.8rem;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;">Leisa, Personal Trainer</p>
<p style="color:#aaa;font-size:0.85rem;line-height:1.65;margin-top:8px;">A fitness professional and former powerlifter, Leisa wanted what powerlifting couldn&#39;t give her &#8212; leaner, stronger, and full of energy. She immersed herself in The Evolved programme and small group training. Twelve months later she&#39;d decreased inflammation, transformed her body composition, and ran her first marathon.</p>
</div>

</div><!-- /carousel-track -->
</div><!-- /carousel-viewport -->

<div class="carousel-nav" style="display:flex;gap:12px;justify-content:center;margin-top:20px;">
<button class="carousel-prev" style="background:#1a1a1a;border:1px solid #333;color:#1a1a1a;width:44px;height:44px;border-radius:50%;cursor:pointer;font-size:1.1rem;display:flex;align-items:center;justify-content:center;" aria-label="Previous">&#8249;</button>
<button class="carousel-next" style="background:#1a1a1a;border:1px solid #333;color:#1a1a1a;width:44px;height:44px;border-radius:50%;cursor:pointer;font-size:1.1rem;display:flex;align-items:center;justify-content:center;" aria-label="Next">&#8250;</button>
</div>

<div style="text-align:center;margin-top:40px;">
<a href="/#pyj-section" style="display:inline-block;background:#e43388;color:#fff;padding:18px 40px;border-radius:4px;font-family:'Lato',sans-serif;font-size:1rem;font-weight:700;text-decoration:none;">Join the Waitlist</a>
</div>

</div><!-- /padding wrapper -->

<div style="background:#0d0d0d;border-top:1px solid #1a1a1a;padding:40px 24px;text-align:center;margin-top:40px;">
<p style="color:#aaa;font-size:0.88rem;margin-bottom:16px;">Limited spots available each month.</p>
<a href="/#pyj-section" style="display:inline-block;border:2px solid #e43388;color:#e43388;padding:12px 28px;border-radius:4px;font-family:'Lato',sans-serif;font-size:0.85rem;font-weight:700;text-decoration:none;letter-spacing:0.04em;">Choose your stage to join the waitlist &#8593;</a>
</div>
</section>


<!-- ─── IN THEIR OWN WORDS (14 videos) ──────────────────────────── -->
<section style="background:#0a0a0a;padding:80px 0;">
<div style="max-width:960px;margin:0 auto;padding:0 24px;">
<h2 style="font-family:'PT Serif Caption',serif;font-size:clamp(1.5rem,3vw,2.2rem);color:#1a1a1a;text-align:center;margin-bottom:12px;">In Their Own Words</h2>
<p style="color:#aaa;text-align:center;margin-bottom:48px;">Hit play and hear what our women say about The Evolved.</p>
</div>
<div style="padding:0 24px;">
<div class="video-viewport" style="overflow:hidden;position:relative;cursor:grab;user-select:none;">
<div class="video-track" style="display:flex;flex-wrap:nowrap;gap:12px;will-change:transform;">

<div class="video-card" style="flex:0 0 calc(33.333% - 8px);min-width:200px;">
<div class="video-facade" data-vid="WwEcN-oV_XM" style="position:relative;border-radius:8px;overflow:hidden;background:#000;cursor:pointer;"><img src="https://i.ytimg.com/vi/WwEcN-oV_XM/hqdefault.jpg" alt="Eleni testimonial" style="width:100%;aspect-ratio:9/16;object-fit:cover;display:block;" loading="lazy"><div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;background:rgba(0,0,0,0.3);"><div style="width:56px;height:56px;background:#e43388;border-radius:50%;display:flex;align-items:center;justify-content:center;"><svg viewBox="0 0 24 24" style="width:24px;height:24px;fill:#fff;margin-left:4px;"><path d="M8 5v14l11-7z"/></svg></div></div></div>
<p style="color:#e43388;font-size:0.8rem;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;margin-top:12px;">Eleni</p>
<p style="color:#aaa;font-size:0.85rem;line-height:1.65;margin-top:6px;">Strength training at 63 and feeling 30 years younger. Eleni swapped Pilates for The Evolved &#8212; and hasn&#39;t looked back.</p>
</div>

<div class="video-card" style="flex:0 0 calc(33.333% - 8px);min-width:200px;">
<div class="video-facade" data-vid="CsICP4wSMG0" style="position:relative;border-radius:8px;overflow:hidden;background:#000;cursor:pointer;"><img src="https://i.ytimg.com/vi/CsICP4wSMG0/hqdefault.jpg" alt="Belinda testimonial" style="width:100%;aspect-ratio:9/16;object-fit:cover;display:block;" loading="lazy"><div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;background:rgba(0,0,0,0.3);"><div style="width:56px;height:56px;background:#e43388;border-radius:50%;display:flex;align-items:center;justify-content:center;"><svg viewBox="0 0 24 24" style="width:24px;height:24px;fill:#fff;margin-left:4px;"><path d="M8 5v14l11-7z"/></svg></div></div></div>
<p style="color:#e43388;font-size:0.8rem;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;margin-top:12px;">Belinda</p>
<p style="color:#aaa;font-size:0.85rem;line-height:1.65;margin-top:6px;">From not being able to hold a glass of water to lifting 35kg &#8212; strength training gave Belinda back her independence, her energy, and her life.</p>
</div>

<div class="video-card" style="flex:0 0 calc(33.333% - 8px);min-width:200px;">
<div class="video-facade" data-vid="yPJ2xlNtkxk" style="position:relative;border-radius:8px;overflow:hidden;background:#000;cursor:pointer;"><img src="https://i.ytimg.com/vi/yPJ2xlNtkxk/hqdefault.jpg" alt="Rudra testimonial" style="width:100%;aspect-ratio:9/16;object-fit:cover;display:block;" loading="lazy"><div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;background:rgba(0,0,0,0.3);"><div style="width:56px;height:56px;background:#e43388;border-radius:50%;display:flex;align-items:center;justify-content:center;"><svg viewBox="0 0 24 24" style="width:24px;height:24px;fill:#fff;margin-left:4px;"><path d="M8 5v14l11-7z"/></svg></div></div></div>
<p style="color:#e43388;font-size:0.8rem;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;margin-top:12px;">Rudra</p>
<p style="color:#aaa;font-size:0.85rem;line-height:1.65;margin-top:6px;">Moving to Brisbane, Rudra felt lost &#8212; until she found The Evolved. Six months on, her body&#39;s stronger, her mind&#39;s clearer, and she finally belongs.</p>
</div>

<div class="video-card" style="flex:0 0 calc(33.333% - 8px);min-width:200px;">
<div class="video-facade" data-vid="pHSmb9jTKoc" style="position:relative;border-radius:8px;overflow:hidden;background:#000;cursor:pointer;"><img src="https://i.ytimg.com/vi/pHSmb9jTKoc/hqdefault.jpg" alt="Jules testimonial" style="width:100%;aspect-ratio:9/16;object-fit:cover;display:block;" loading="lazy"><div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;background:rgba(0,0,0,0.3);"><div style="width:56px;height:56px;background:#e43388;border-radius:50%;display:flex;align-items:center;justify-content:center;"><svg viewBox="0 0 24 24" style="width:24px;height:24px;fill:#fff;margin-left:4px;"><path d="M8 5v14l11-7z"/></svg></div></div></div>
<p style="color:#e43388;font-size:0.8rem;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;margin-top:12px;">Jules</p>
<p style="color:#aaa;font-size:0.85rem;line-height:1.65;margin-top:6px;">Turned 40, had never touched a weight in her life &#8212; and fell completely in love with strength training and the all-female environment.</p>
</div>

<div class="video-card" style="flex:0 0 calc(33.333% - 8px);min-width:200px;">
<div class="video-facade" data-vid="W6cDcI7I1zI" style="position:relative;border-radius:8px;overflow:hidden;background:#000;cursor:pointer;"><img src="https://i.ytimg.com/vi/W6cDcI7I1zI/hqdefault.jpg" alt="Johanna testimonial" style="width:100%;aspect-ratio:9/16;object-fit:cover;display:block;" loading="lazy"><div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;background:rgba(0,0,0,0.3);"><div style="width:56px;height:56px;background:#e43388;border-radius:50%;display:flex;align-items:center;justify-content:center;"><svg viewBox="0 0 24 24" style="width:24px;height:24px;fill:#fff;margin-left:4px;"><path d="M8 5v14l11-7z"/></svg></div></div></div>
<p style="color:#e43388;font-size:0.8rem;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;margin-top:12px;">Johanna</p>
<p style="color:#aaa;font-size:0.85rem;line-height:1.65;margin-top:6px;">Life-changing. Lifts over 100kg. Completed Hyrox in under 90 minutes. The community keeps her accountable every single week.</p>
</div>

<div class="video-card" style="flex:0 0 calc(33.333% - 8px);min-width:200px;">
<div class="video-facade" data-vid="WY01XSdmevk" style="position:relative;border-radius:8px;overflow:hidden;background:#000;cursor:pointer;"><img src="https://i.ytimg.com/vi/WY01XSdmevk/hqdefault.jpg" alt="Orlagh testimonial" style="width:100%;aspect-ratio:9/16;object-fit:cover;display:block;" loading="lazy"><div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;background:rgba(0,0,0,0.3);"><div style="width:56px;height:56px;background:#e43388;border-radius:50%;display:flex;align-items:center;justify-content:center;"><svg viewBox="0 0 24 24" style="width:24px;height:24px;fill:#fff;margin-left:4px;"><path d="M8 5v14l11-7z"/></svg></div></div></div>
<p style="color:#e43388;font-size:0.8rem;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;margin-top:12px;">Orlagh</p>
<p style="color:#aaa;font-size:0.85rem;line-height:1.65;margin-top:6px;">Started from zero &#8212; no gym knowledge, no sporting background. The women-only space was the drawcard.</p>
</div>

<div class="video-card" style="flex:0 0 calc(33.333% - 8px);min-width:200px;">
<div class="video-facade" data-vid="W3_KlWQE5Gg" style="position:relative;border-radius:8px;overflow:hidden;background:#000;cursor:pointer;"><img src="https://i.ytimg.com/vi/W3_KlWQE5Gg/hqdefault.jpg" alt="Michelle testimonial" style="width:100%;aspect-ratio:9/16;object-fit:cover;display:block;" loading="lazy"><div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;background:rgba(0,0,0,0.3);"><div style="width:56px;height:56px;background:#e43388;border-radius:50%;display:flex;align-items:center;justify-content:center;"><svg viewBox="0 0 24 24" style="width:24px;height:24px;fill:#fff;margin-left:4px;"><path d="M8 5v14l11-7z"/></svg></div></div></div>
<p style="color:#e43388;font-size:0.8rem;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;margin-top:12px;">Michelle</p>
<p style="color:#aaa;font-size:0.85rem;line-height:1.65;margin-top:6px;">Used to only cycle &#8212; now trains 4 days a week and loves every session. The soreness that never went away? Gone.</p>
</div>

<div class="video-card" style="flex:0 0 calc(33.333% - 8px);min-width:200px;">
<div class="video-facade" data-vid="15q1XPdx1PU" style="position:relative;border-radius:8px;overflow:hidden;background:#000;cursor:pointer;"><img src="https://i.ytimg.com/vi/15q1XPdx1PU/hqdefault.jpg" alt="Peta testimonial" style="width:100%;aspect-ratio:9/16;object-fit:cover;display:block;" loading="lazy"><div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;background:rgba(0,0,0,0.3);"><div style="width:56px;height:56px;background:#e43388;border-radius:50%;display:flex;align-items:center;justify-content:center;"><svg viewBox="0 0 24 24" style="width:24px;height:24px;fill:#fff;margin-left:4px;"><path d="M8 5v14l11-7z"/></svg></div></div></div>
<p style="color:#e43388;font-size:0.8rem;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;margin-top:12px;">Peta</p>
<p style="color:#aaa;font-size:0.85rem;line-height:1.65;margin-top:6px;">&#8220;I came for strength training, but I stayed for the people.&#8221; No ego. Just progress at your own pace, surrounded by good women.</p>
</div>

<div class="video-card" style="flex:0 0 calc(33.333% - 8px);min-width:200px;">
<div class="video-facade" data-vid="O-ToRNZwB1w" style="position:relative;border-radius:8px;overflow:hidden;background:#000;cursor:pointer;"><img src="https://i.ytimg.com/vi/O-ToRNZwB1w/hqdefault.jpg" alt="Tess testimonial" style="width:100%;aspect-ratio:9/16;object-fit:cover;display:block;" loading="lazy"><div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;background:rgba(0,0,0,0.3);"><div style="width:56px;height:56px;background:#e43388;border-radius:50%;display:flex;align-items:center;justify-content:center;"><svg viewBox="0 0 24 24" style="width:24px;height:24px;fill:#fff;margin-left:4px;"><path d="M8 5v14l11-7z"/></svg></div></div></div>
<p style="color:#e43388;font-size:0.8rem;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;margin-top:12px;">Tess</p>
<p style="color:#aaa;font-size:0.85rem;line-height:1.65;margin-top:6px;">Sedentary and feeling terrible &#8212; now benching 37.5kg and deadlifting 75kg. She drove from Ipswich every day. That&#39;s how good it is.</p>
</div>

<div class="video-card" style="flex:0 0 calc(33.333% - 8px);min-width:200px;">
<div class="video-facade" data-vid="G2vXxlVJ0nk" style="position:relative;border-radius:8px;overflow:hidden;background:#000;cursor:pointer;"><img src="https://i.ytimg.com/vi/G2vXxlVJ0nk/hqdefault.jpg" alt="Laura testimonial" style="width:100%;aspect-ratio:9/16;object-fit:cover;display:block;" loading="lazy"><div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;background:rgba(0,0,0,0.3);"><div style="width:56px;height:56px;background:#e43388;border-radius:50%;display:flex;align-items:center;justify-content:center;"><svg viewBox="0 0 24 24" style="width:24px;height:24px;fill:#fff;margin-left:4px;"><path d="M8 5v14l11-7z"/></svg></div></div></div>
<p style="color:#e43388;font-size:0.8rem;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;margin-top:12px;">Laura</p>
<p style="color:#aaa;font-size:0.85rem;line-height:1.65;margin-top:6px;">Joined to get stronger for martial arts. Left with better mental strength, cardiovascular health, and coaches who genuinely cheer for every PB.</p>
</div>

<div class="video-card" style="flex:0 0 calc(33.333% - 8px);min-width:200px;">
<div class="video-facade" data-vid="59YWpXOY2SQ" style="position:relative;border-radius:8px;overflow:hidden;background:#000;cursor:pointer;"><img src="https://i.ytimg.com/vi/59YWpXOY2SQ/hqdefault.jpg" alt="Eleni 2 Years On" style="width:100%;aspect-ratio:9/16;object-fit:cover;display:block;" loading="lazy"><div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;background:rgba(0,0,0,0.3);"><div style="width:56px;height:56px;background:#e43388;border-radius:50%;display:flex;align-items:center;justify-content:center;"><svg viewBox="0 0 24 24" style="width:24px;height:24px;fill:#fff;margin-left:4px;"><path d="M8 5v14l11-7z"/></svg></div></div></div>
<p style="color:#e43388;font-size:0.8rem;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;margin-top:12px;">Eleni &#8212; 2 Years On</p>
<p style="color:#aaa;font-size:0.85rem;line-height:1.65;margin-top:6px;">Update: Eleni no longer has osteoporosis in her spine. She went from Pilates to doing things she never thought possible &#8212; including her first chin-up.</p>
</div>

<div class="video-card" style="flex:0 0 calc(33.333% - 8px);min-width:200px;">
<div class="video-facade" data-vid="COIm1FmTYOc" style="position:relative;border-radius:8px;overflow:hidden;background:#000;cursor:pointer;"><img src="https://i.ytimg.com/vi/COIm1FmTYOc/hqdefault.jpg" alt="Jennifer 64" style="width:100%;aspect-ratio:9/16;object-fit:cover;display:block;" loading="lazy"><div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;background:rgba(0,0,0,0.3);"><div style="width:56px;height:56px;background:#e43388;border-radius:50%;display:flex;align-items:center;justify-content:center;"><svg viewBox="0 0 24 24" style="width:24px;height:24px;fill:#fff;margin-left:4px;"><path d="M8 5v14l11-7z"/></svg></div></div></div>
<p style="color:#e43388;font-size:0.8rem;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;margin-top:12px;">Jennifer, 64</p>
<p style="color:#aaa;font-size:0.85rem;line-height:1.65;margin-top:6px;">Chronic neck pain, headaches, and temporary deafness &#8212; gone. Strength training did what years of treatment couldn&#39;t.</p>
</div>

<div class="video-card" style="flex:0 0 calc(33.333% - 8px);min-width:200px;">
<div class="video-facade" data-vid="5QkcZC8AE8s" style="position:relative;border-radius:8px;overflow:hidden;background:#000;cursor:pointer;"><img src="https://i.ytimg.com/vi/5QkcZC8AE8s/hqdefault.jpg" alt="Alana testimonial" style="width:100%;aspect-ratio:9/16;object-fit:cover;display:block;" loading="lazy"><div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;background:rgba(0,0,0,0.3);"><div style="width:56px;height:56px;background:#e43388;border-radius:50%;display:flex;align-items:center;justify-content:center;"><svg viewBox="0 0 24 24" style="width:24px;height:24px;fill:#fff;margin-left:4px;"><path d="M8 5v14l11-7z"/></svg></div></div></div>
<p style="color:#e43388;font-size:0.8rem;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;margin-top:12px;">Alana</p>
<p style="color:#aaa;font-size:0.85rem;line-height:1.65;margin-top:6px;">12kg and two dress sizes in 5 months. Came in with back pain so bad she couldn&#39;t deadlift. Now lifting 55kg RDLs and doing her first chin-ups.</p>
</div>

<div class="video-card" style="flex:0 0 calc(33.333% - 8px);min-width:200px;">
<div class="video-facade" data-vid="ATNysZlwUvg" style="position:relative;border-radius:8px;overflow:hidden;background:#000;cursor:pointer;"><img src="https://i.ytimg.com/vi/ATNysZlwUvg/hqdefault.jpg" alt="Sophie testimonial" style="width:100%;aspect-ratio:9/16;object-fit:cover;display:block;" loading="lazy"><div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;background:rgba(0,0,0,0.3);"><div style="width:56px;height:56px;background:#e43388;border-radius:50%;display:flex;align-items:center;justify-content:center;"><svg viewBox="0 0 24 24" style="width:24px;height:24px;fill:#fff;margin-left:4px;"><path d="M8 5v14l11-7z"/></svg></div></div></div>
<p style="color:#e43388;font-size:0.8rem;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;margin-top:12px;">Sophie</p>
<p style="color:#aaa;font-size:0.85rem;line-height:1.65;margin-top:6px;">Switching careers to landscaping in her late 40s meant getting strong wasn&#39;t optional. Watch what she can carry now.</p>
</div>

</div><!-- /video-track -->
</div><!-- /video-viewport -->

<div style="display:flex;gap:12px;justify-content:center;margin-top:28px;">
<button class="video-prev" style="background:#1a1a1a;border:1px solid #333;color:#1a1a1a;width:44px;height:44px;border-radius:50%;cursor:pointer;font-size:1.1rem;display:flex;align-items:center;justify-content:center;" aria-label="Previous">&#8249;</button>
<button class="video-next" style="background:#1a1a1a;border:1px solid #333;color:#1a1a1a;width:44px;height:44px;border-radius:50%;cursor:pointer;font-size:1.1rem;display:flex;align-items:center;justify-content:center;" aria-label="Next">&#8250;</button>
</div>
</div>
</section>


<!-- ─── CAROUSEL JS (results + video, no GSAP needed) ───────────── -->
<script>
(function() {
  function initCarousel(viewportSel, trackSel, prevSel, nextSel, facadeSel) {
    var viewport = document.querySelector(viewportSel);
    var track    = viewport ? viewport.querySelector(trackSel) : null;
    if (!viewport || !track) return;
    var cards = Array.from(track.children);
    var current = 0, startX = 0, isDragging = false, dragDelta = 0;
    function gap() { return 12; }
    function cardW() { return cards[0].getBoundingClientRect().width + gap(); }
    function visible() { return Math.round(viewport.offsetWidth / cardW()); }
    function maxIdx() { return Math.max(0, cards.length - visible()); }
    function goTo(idx) {
      current = Math.max(0, Math.min(idx, maxIdx()));
      track.style.transition = 'transform 0.45s cubic-bezier(0.25,0.46,0.45,0.94)';
      track.style.transform  = 'translateX(' + -(current * cardW()) + 'px)';
    }
    var prevBtn = document.querySelector(prevSel);
    var nextBtn = document.querySelector(nextSel);
    if (prevBtn) prevBtn.addEventListener('click', function() { goTo(current - 1); });
    if (nextBtn) nextBtn.addEventListener('click', function() { goTo(current + 1); });
    viewport.addEventListener('mousedown',  function(e) { isDragging = true; startX = e.clientX; dragDelta = 0; viewport.style.cursor = 'grabbing'; });
    viewport.addEventListener('mousemove',  function(e) { if (!isDragging) return; dragDelta = e.clientX - startX; });
    viewport.addEventListener('mouseup',    function() { settle(); });
    viewport.addEventListener('mouseleave', function() { if (isDragging) settle(); });
    viewport.addEventListener('touchstart', function(e) { startX = e.touches[0].clientX; isDragging = true; dragDelta = 0; }, { passive: true });
    viewport.addEventListener('touchmove',  function(e) { if (!isDragging) return; dragDelta = e.touches[0].clientX - startX; }, { passive: true });
    viewport.addEventListener('touchend',   function() { settle(); });
    function settle() {
      isDragging = false; viewport.style.cursor = 'grab';
      var t = cardW() * 0.2;
      if (dragDelta < -t) goTo(current + 1); else if (dragDelta > t) goTo(current - 1); else goTo(current);
      dragDelta = 0;
    }
    if (facadeSel) {
      track.querySelectorAll(facadeSel).forEach(function(facade) {
        facade.addEventListener('click', function() {
          if (Math.abs(dragDelta) > 5) return;
          var vid = this.dataset.vid;
          if (!vid) return;
          this.innerHTML = '<iframe src="https://www.youtube.com/embed/' + vid + '?autoplay=1&rel=0" frameborder="0" allow="accelerometer;autoplay;clipboard-write;encrypted-media;gyroscope;picture-in-picture" allowfullscreen style="width:100%;aspect-ratio:9/16;display:block;border:none;"></iframe>';
          this.style.cursor = 'default';
        });
      });
    }
  }
  initCarousel('.carousel-viewport', '.carousel-track', '.carousel-prev', '.carousel-next', null);
  initCarousel('.video-viewport',    '.video-track',    '.video-prev',    '.video-next',    '.video-facade');
})();
</script>


<!-- ─── GOOGLE REVIEWS ───────────────────────────────────────────── -->
<section style="background:#111;padding:72px 32px;">
  <div style="max-width:960px;margin:0 auto;">
    <h2 style="font-family:'PT Serif Caption','Playfair Display',Georgia,serif;font-size:clamp(1.5rem,3vw,2.2rem);color:#1a1a1a;text-align:center;margin-bottom:40px;">What Our Members Say</h2>
    <iframe id="ev-reviews-iframe" src="https://backend.leadconnectorhq.com/appengine/reviews/get_widget/6Ku1uU0Xc45zq0KlTikJ" frameborder="0" scrolling="no" style="width:100%;display:block;border:none;min-height:400px;" title="Google Reviews"></iframe>
  </div>
</section>
<script>
window.addEventListener('message', function(e) {
  var name = e.data[0], data = e.data[1];
  if (name === 'lc.setHeight' && data && data.id === 'lc_reviews_widget') {
    var iframe = document.getElementById('ev-reviews-iframe');
    if (iframe && e.source === iframe.contentWindow) iframe.style.height = data.height + 'px';
  }
}, false);
</script>


<!-- ─── FAQ ──────────────────────────────────────────────────────── -->
<section style="background:#f7f7f7;padding:80px 32px;">
  <div style="max-width:760px;margin:0 auto;">
    <h2 style="font-family:'PT Serif Caption','Playfair Display',Georgia,serif;font-size:clamp(1.6rem,3.5vw,2.2rem);color:#1a1a1a;text-align:center;margin:0 0 40px;">Frequently Asked Questions</h2>
    <style>
      .tr-faq-item { border-bottom:1px solid #ddd; }
      .tr-faq-item:first-of-type { border-top:1px solid #ddd; }
      .tr-faq-item summary { padding:20px 0; font-size:1.05rem; font-weight:600; color:#1a1a1a; display:flex; justify-content:space-between; align-items:center; gap:16px; cursor:pointer; list-style:none; }
      .tr-faq-item summary::-webkit-details-marker { display:none; }
      .tr-faq-item summary::after { content:'+'; font-size:1.5rem; color:#e43388; flex-shrink:0; line-height:1; transition:transform 0.2s; }
      .tr-faq-item[open] summary::after { transform:rotate(45deg); }
      .tr-faq-body { padding:0 0 20px; font-size:1rem; line-height:1.8; color:#444; }
    </style>

    <details class="tr-faq-item">
    <summary>Can I come and see the gym before booking a Strength Assessment?</summary>
    <div class="tr-faq-body">
    <p style="color:#444;font-size:0.9rem;line-height:1.75;margin-top:16px;">We understand the desire to see a space before stepping into it &#8212; especially if gyms haven't always felt welcoming. We're a small, specialist facility that runs by appointment only, so we're not set up for casual drop-ins. But what we can offer you is something far more useful: a Strength Assessment where you walk away knowing exactly what your body needs and what's genuinely possible for you.</p>
    <p style="color:#444;font-size:0.9rem;line-height:1.75;margin-top:12px;">Joining the waitlist is free, takes 30 seconds, and carries zero obligation. If a spot opens and the timing isn't right &#8212; no pressure at all. When you do come in, you'll leave with your exact starting point, a realistic picture of what's possible, and a clear timeframe to your goal &#8212; regardless of whether you join. That clarity alone is worth the visit.</p>
    </div>
    </details>
    
        <details class="tr-faq-item">
    <summary>How much does it cost?</summary>
    <div class="tr-faq-body">
    <p style="color:#444;font-size:0.9rem;line-height:1.75;margin-top:16px;">We don't give prices before we understand what you need &#8212; that would be like a doctor writing a prescription before the consultation. Pricing depends on your goals, training history, any injuries or medical conditions, and what program will actually get you there.</p>
    <p style="color:#444;font-size:0.9rem;line-height:1.75;margin-top:12px;">The Strength Assessment is where that conversation happens. You'll get a clear picture of your starting point, what we recommend, and what it costs &#8212; then you decide. No pressure, no obligation. For context: 1:1 personal training in Brisbane runs $100&#8211;$150 per hour. Our members train as many times as they like each week, across 24 timetable sessions, for less than a single 1:1 session.</p>
    </div>
    </details>
    
        <details class="tr-faq-item">
    <summary>What is a Strength Assessment?</summary>
    <div class="tr-faq-body">
    <p style="color:#444;font-size:0.9rem;line-height:1.75;margin-top:16px;">It&#8217;s a short, guided session with one of our female coaches &#8212; not a gym tour, not a sales pitch. Four things happen:</p>
    <ul style="color:#444;font-size:0.9rem;line-height:1.85;margin-top:12px;padding-left:20px;">
      <li><strong style="color:#1a1a1a;">Where are we starting?</strong> A guided strength and movement check-up. No pressure, no judgement.</li>
      <li><strong style="color:#1a1a1a;">What is your next step?</strong> Personalised guidance on improving energy, posture, and physical confidence.</li>
      <li><strong style="color:#1a1a1a;">Do you have concerns?</strong> Expert answers to your training or body-change questions &#8212; honestly, no spin.</li>
      <li><strong style="color:#1a1a1a;">Can we fast-track this?</strong> A clear game plan for moving forward &#8212; whether you join or not.</li>
    </ul>
    <p style="color:#444;font-size:0.9rem;line-height:1.75;margin-top:12px;">We offer 5 of these per week. You&#8217;ll leave with your exact starting point, a realistic picture of what&#8217;s possible, and a clear timeframe &#8212; regardless of whether you join.</p>
    </div>
    </details>
    
        <details class="tr-faq-item">
    <summary>Are there any joining fees?</summary>
    <div class="tr-faq-body">
    <p style="color:#444;font-size:0.9rem;line-height:1.75;margin-top:16px;">None. No joining fees, no admin charges, no hidden costs of any kind. The price you're quoted at your Strength Assessment is the price you pay &#8212; for your training, and nothing else. What you see is what you get.</p>
    </div>
    </details>
    
        <details class="tr-faq-item">
    <summary>I&#8217;m already training elsewhere. What makes this different?</summary>
    <div class="tr-faq-body">
    <p style="color:#444;font-size:0.9rem;line-height:1.75;margin-top:16px;">Most gyms give you a workout. It's random every week, and you're left to figure out whether it's working. At The Evolved, you get a 12-month roadmap grounded in real science and built around the longevity markers that matter for women. We start with a 1-on-1 Strength Assessment so your program is safe, sustainable, and specific to you. Our training is periodised and phased &#8212; backed by the world's leading experts in women's strength and ageing. You'll never burn out, always make progress, and feel in full control of your body.</p>
    </div>
    </details>
    
        <details class="tr-faq-item">
    <summary>Are there any lock-in contracts?</summary>
    <div class="tr-faq-body">
    <p style="color:#444;font-size:0.9rem;line-height:1.75;margin-top:16px;">No lock-ins &#8212; just a 30-day cancellation notice across all services. This gives us space to plan your training properly and gives you room to push through the tough weeks without quitting on your goals too soon.</p>
    </div>
    </details>
    
        <details class="tr-faq-item">
    <summary>Is this like a regular gym?</summary>
    <div class="tr-faq-body">
    <p style="color:#444;font-size:0.9rem;line-height:1.75;margin-top:16px;">Not at all. We're not a commercial gym with crowds, confusing equipment, or $10 swipe-and-sweat memberships. This is female-specific coaching designed for your body, stage of life, and long-term health. You'll train in small groups with expert guidance to ensure your form is perfect and you're safely pushing yourself. The atmosphere is supportive &#8212; trainers and fellow members pushing each other, not competing.</p>
    </div>
    </details>
    
        <details class="tr-faq-item">
    <summary>Am I too old to start strength training?</summary>
    <div class="tr-faq-body">
    <p style="color:#444;font-size:0.9rem;line-height:1.75;margin-top:16px;">Our youngest member is 14. Our most experienced woman is 72. We cater to all women regardless of size, shape, fitness level, or age. The group who find it hardest to build lean muscle mass are women over 40 &#8212; and not coincidentally, this is the group who benefit most from properly structured strength training. Our entire system is designed around the unique needs of perimenopausal, postmenopausal, and ageing women. You'll feel stronger, move better, and stay independent &#8212; at any age.</p>
    </div>
    </details>
    
        <details class="tr-faq-item">
    <summary>I haven&#8217;t exercised in 10+ years&#8230; is this too advanced for me?</summary>
    <div class="tr-faq-body">
    <p style="color:#444;font-size:0.9rem;line-height:1.75;margin-top:16px;">Not at all. You'll begin with a Strength Assessment where we meet you exactly where you're at &#8212; no pressure, no expectations. Our beginner-friendly onboarding focuses on movement confidence, not performance. You'll feel safe, seen, and supported from Day 1. If it's been a while, we'll likely recommend our Fast Track membership, which includes one-on-one personal training each week &#8212; the best way to learn faster, adapt exercises to your body, and build confidence from scratch. You'll be working out with a group of women just like you.</p>
    </div>
    </details>
    
        <details class="tr-faq-item">
    <summary>I&#8217;ve had injuries or chronic pain&#8230; can I still join?</summary>
    <div class="tr-faq-body">
    <p style="color:#444;font-size:0.9rem;line-height:1.75;margin-top:16px;">Yes &#8212; and in fact, that's one of the most common reasons women come to us. We specialise in form correction, injury prevention, and training around pain or limitations. Our coaches are experts in safe, intelligent strength training and work closely with physios and allied health professionals. Already have a treatment team? We're happy to collaborate. Low-impact strength training, focusing on form and gradual progression, can help strengthen the muscles around your joints and reduce pain over time.</p>
    </div>
    </details>
    
        <details class="tr-faq-item">
    <summary>Will lifting weights make me bulky?</summary>
    <div class="tr-faq-body">
    <p style="color:#444;font-size:0.9rem;line-height:1.75;margin-top:16px;">This is one of the most common concerns we hear &#8212; and it's completely understandable. The short answer: no. Building the kind of muscle that looks "bulky" requires years of very specific training, very high calorie intake, and often hormonal support. Women's physiology simply doesn't work that way naturally. What strength training does build is a lean, toned, shapely body that gets stronger and more capable every week.</p>
    <p style="color:#444;font-size:0.9rem;line-height:1.75;margin-top:12px;">In fact, the bigger risk for women as they age is losing muscle &#8212; which slows metabolism, affects posture, and reduces independence over time. Strength training is how you hold onto what matters most. The goal isn't to get bigger. It's to get stronger, leaner, and feel great in your body.</p>
    </div>
    </details>

  </div>
</section>


<!-- ─── FOOTER ───────────────────────────────────────────────────── -->
<footer style="background:#0d0d0d;padding:64px 32px;">
  <div style="max-width:1100px;margin:0 auto;">
    <div class="tr-footer-grid" style="display:grid;grid-template-columns:1fr 1fr;gap:48px;align-items:start;">
      <div>
        <img src="https://theevolvedgym.com.au/logo.png" alt="The Evolved All Female Gym" style="max-width:180px;margin-bottom:20px;display:block;" onerror="this.style.display='none'">
        <p style="color:#aaa;font-size:0.9rem;line-height:1.75;margin-bottom:20px;">Brisbane&#39;s leading women-only gym. Evidence-based strength training for real women at every stage of life.</p>
        <p style="color:#aaa;font-size:0.85rem;margin-bottom:6px;"><strong style="color:#e43388;">Address:</strong> 7 Paris Street, West End QLD 4101</p>
        <p style="color:#aaa;font-size:0.85rem;margin-bottom:6px;"><strong style="color:#e43388;">Phone:</strong> <a href="tel:0483968880" style="color:#aaa;text-decoration:none;">0483 968 880</a></p>
        <p style="color:#aaa;font-size:0.85rem;margin-bottom:20px;"><strong style="color:#e43388;">Email:</strong> <a href="mailto:info@theevolvedgym.com.au" style="color:#aaa;text-decoration:none;">info@theevolvedgym.com.au</a></p>
        <a href="/#pyj-section" style="display:inline-block;background:#e43388;color:#fff;font-weight:700;font-size:0.9rem;text-decoration:none;padding:12px 24px;letter-spacing:0.05em;text-transform:uppercase;">Join the Priority List</a>
      </div>
      <div>
        <iframe src="https://www.google.com/maps/embed?pb=!1m14!1m8!1m3!1d227.85171657797738!2d153.007864!3d-27.48099!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x6b9150a212182a39%3A0xb51d2c6cb0d956a4!2sThe%20Evolved%20All%20Female%20Personal%20Training%20%26%20Gym!5e1!3m2!1sen!2sus!4v1750151566632!5m2!1sen!2sus" width="100%" height="300" style="border:0;border-radius:8px;display:block;" allowfullscreen loading="lazy" referrerpolicy="no-referrer-when-downgrade" title="The Evolved All Female Gym"></iframe>
      </div>
    </div>
    <div style="border-top:1px solid #1a1a1a;margin-top:40px;padding-top:24px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;">
      <p style="color:#555;font-size:0.8rem;margin:0;">&#169; <?php echo date('Y'); ?> The Evolved All Female Gym. All rights reserved.</p>
      <div style="display:flex;gap:20px;">
        <a href="/legal" style="color:#555;font-size:0.8rem;text-decoration:none;">Terms &amp; Privacy</a>
        <a href="https://evolved-woman.theevolvedgym.com.au/" style="color:#555;font-size:0.8rem;text-decoration:none;">Blog</a>
        <a href="/team" style="color:#555;font-size:0.8rem;text-decoration:none;">Meet the Team</a>
      </div>
    </div>
  </div>
</footer>

<?php wp_footer(); ?>
</body>
</html>
