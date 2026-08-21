/**
 * homepage.js — The Evolved v2.0
 * GSAP scroll animations + hero parallax + counters + carousel + charts
 */

gsap.registerPlugin(ScrollTrigger);


// ── 1A — GLOBAL SCROLL-REVEAL SYSTEM ─────────────────────────────
// Add data-reveal="fade-up|fade-left|fade-right|scale" to any element.
// Add data-reveal-stagger to a parent + data-reveal-child to each child
// for staggered group reveals.

(function initReveal() {
    // Single elements
    document.querySelectorAll("[data-reveal]").forEach(el => {
        const variant = el.dataset.reveal;
        const delay   = parseFloat(el.dataset.revealDelay || "0");
        const vars    = { opacity: 0, duration: 0.85, ease: "power3.out", delay };

        if (variant === "fade-up")    { vars.y = 40; }
        if (variant === "fade-left")  { vars.x = -40; }
        if (variant === "fade-right") { vars.x = 40; }
        if (variant === "scale")      { vars.scale = 0.9; }

        gsap.from(el, {
            ...vars,
            scrollTrigger: { trigger: el, start: "top 88%", once: true }
        });
    });

    // Staggered groups
    document.querySelectorAll("[data-reveal-stagger]").forEach(parent => {
        const children = parent.querySelectorAll("[data-reveal-child]");
        if (!children.length) return;
        const stagger = parseFloat(parent.dataset.revealStagger || "0.12");

        gsap.from(children, {
            opacity: 0, y: 30, duration: 0.7, ease: "power3.out",
            stagger,
            scrollTrigger: { trigger: parent, start: "top 85%", once: true }
        });
    });
})();


// ── 1B — HERO PARALLAX + STAGGERED TEXT REVEAL ───────────────────

(function initHero() {
    const bg = document.querySelector(".hero-bg");
    if (bg) {
        gsap.to(bg, {
            yPercent: 20,
            ease: "none",
            scrollTrigger: {
                trigger: ".hero",
                start: "top top",
                end: "bottom top",
                scrub: true
            }
        });
    }

    const tl = gsap.timeline({ defaults: { ease: "power3.out" } });
    const eyebrow    = document.querySelector(".hero-eyebrow");
    const headline   = document.querySelector(".hero-headline");
    const sub        = document.querySelector(".hero-sub");
    const cta        = document.querySelector(".hero-cta");
    const disclaimer = document.querySelector(".hero-disclaimer");

    if (eyebrow)    tl.to(eyebrow,    { opacity: 1, y: 0, duration: 0.6 }, 0.3);
    if (headline)   tl.to(headline,   { opacity: 1, y: 0, duration: 0.9 }, 0.6);
    if (sub)        tl.to(sub,        { opacity: 1, y: 0, duration: 0.75 }, 1.0);
    if (cta)        tl.to(cta,        { opacity: 1, y: 0, duration: 0.6 }, 1.4);
    if (disclaimer) tl.to(disclaimer, { opacity: 1, y: 0, duration: 0.5 }, 1.7);

    // CTA pulse after reveal
    if (cta) {
        tl.call(() => {
            gsap.to(cta, {
                boxShadow: "0 0 0 8px rgba(228,51,136,0)",
                duration: 1.2,
                repeat: -1,
                yoyo: false,
                ease: "power2.out",
                onRepeat() {
                    gsap.set(cta, { boxShadow: "0 0 0 0px rgba(228,51,136,0.5)" });
                }
            });
        }, [], 2.2);
    }
})();


// ── 1C — ANIMATED NUMBER COUNTERS ────────────────────────────────
// Markup: <span class="stat-number" data-count="500" data-count-suffix="+">0</span>

(function initCounters() {
    document.querySelectorAll("[data-count]").forEach(el => {
        const target = parseInt(el.dataset.count, 10);
        const suffix = el.dataset.countSuffix || "";

        ScrollTrigger.create({
            trigger: el,
            start: "top 85%",
            once: true,
            onEnter() {
                gsap.fromTo(el,
                    { innerText: 0 },
                    {
                        innerText: target,
                        duration: 1.8,
                        ease: "power2.out",
                        snap: { innerText: 1 },
                        onUpdate() {
                            el.textContent = Math.round(parseFloat(el.innerText)) + suffix;
                        },
                        onComplete() {
                            el.textContent = target + suffix;
                        }
                    }
                );
            }
        });
    });
})();


// ── 1D — CHART SCROLL-TRIGGER REVEAL ─────────────────────────────

(function initChartReveal() {
    ["sarcopeniaChart", "frequencyChart"].forEach(id => {
        const canvas = document.getElementById(id);
        if (!canvas) return;
        const wrap = canvas.closest(".chart-canvas-wrap") || canvas.parentElement;
        gsap.from(wrap, {
            opacity: 0, y: 40, duration: 0.9, ease: "power3.out",
            scrollTrigger: { trigger: wrap, start: "top 85%", once: true }
        });
    });
})();


// ── 1E — TESTIMONIAL DRAGGABLE CAROUSEL ──────────────────────────

(function initCarousel() {
    const viewport = document.querySelector(".carousel-viewport");
    if (!viewport) return;

    const track    = viewport.querySelector(".carousel-track");
    const cards    = Array.from(track.querySelectorAll(".carousel-card"));
    const prevBtn  = document.querySelector(".carousel-prev");
    const nextBtn  = document.querySelector(".carousel-next");
    if (!track || !cards.length) return;

    const gap       = 24;
    let current     = 0;
    let startX      = 0;
    let isDragging  = false;
    let dragDelta   = 0;

    function cardWidth() {
        return cards[0].getBoundingClientRect().width + gap;
    }

    function maxIndex() {
        return Math.max(0, cards.length - Math.round(viewport.offsetWidth / cardWidth()));
    }

    function goTo(index, instant) {
        current = Math.max(0, Math.min(index, maxIndex()));
        gsap.to(track, {
            x: -(current * cardWidth()),
            duration: instant ? 0 : 0.45,
            ease: "power3.out"
        });
    }

    if (prevBtn) prevBtn.addEventListener("click", () => goTo(current - 1));
    if (nextBtn) nextBtn.addEventListener("click", () => goTo(current + 1));

    // Expose reset for carousel reorder
    window.__carouselGoTo = (idx, instant) => goTo(idx, instant);

    // Button hover states
    [prevBtn, nextBtn].forEach(btn => {
        if (!btn) return;
        btn.addEventListener("mouseenter", () => { btn.style.background = "#e43388"; btn.style.borderColor = "#e43388"; });
        btn.addEventListener("mouseleave", () => { btn.style.background = "#1a1a1a"; btn.style.borderColor = "#333"; });
    });

    // Touch / drag
    viewport.addEventListener("mousedown",  e => { isDragging = true; startX = e.clientX; viewport.style.cursor = "grabbing"; });
    viewport.addEventListener("mousemove",  e => { if (!isDragging) return; dragDelta = e.clientX - startX; });
    viewport.addEventListener("mouseup",    () => settle());
    viewport.addEventListener("mouseleave", () => { if (isDragging) settle(); });

    viewport.addEventListener("touchstart", e => { startX = e.touches[0].clientX; isDragging = true; }, { passive: true });
    viewport.addEventListener("touchmove",  e => { if (!isDragging) return; dragDelta = e.touches[0].clientX - startX; }, { passive: true });
    viewport.addEventListener("touchend",   () => settle());

    function settle() {
        isDragging = false;
        viewport.style.cursor = "grab";
        const threshold = cardWidth() * 0.25;
        if (dragDelta < -threshold) goTo(current + 1);
        else if (dragDelta > threshold) goTo(current - 1);
        else goTo(current);
        dragDelta = 0;
    }

    // Scroll-reveal the cards
    gsap.from(cards, {
        opacity: 0, y: 30, duration: 0.7, ease: "power3.out", stagger: 0.1,
        scrollTrigger: { trigger: viewport, start: "top 85%", once: true }
    });
})();


// ── 1F — GYM PHOTO CAROUSEL ───────────────────────────────────────

(function initPhotoCarousel() {
    const viewport = document.querySelector(".photo-viewport");
    if (!viewport) return;

    const track   = viewport.querySelector(".photo-track");
    const cards   = Array.from(track.querySelectorAll(".photo-card"));
    const prevBtn = document.querySelector(".photo-prev");
    const nextBtn = document.querySelector(".photo-next");
    if (!track || !cards.length) return;

    const gap      = 12;
    let current    = 0;
    let startX     = 0;
    let isDragging = false;
    let dragDelta  = 0;

    function cardWidth() {
        return cards[0].getBoundingClientRect().width + gap;
    }

    function visibleCount() {
        return Math.round(viewport.offsetWidth / cardWidth());
    }

    function maxIndex() {
        return Math.max(0, cards.length - visibleCount());
    }

    function goTo(index, instant) {
        current = Math.max(0, Math.min(index, maxIndex()));
        gsap.to(track, {
            x: -(current * cardWidth()),
            duration: instant ? 0 : 0.45,
            ease: "power3.out"
        });
    }

    if (prevBtn) prevBtn.addEventListener("click", () => goTo(current - 1));
    if (nextBtn) nextBtn.addEventListener("click", () => goTo(current + 1));

    viewport.addEventListener("mousedown",  e => { isDragging = true; startX = e.clientX; viewport.style.cursor = "grabbing"; });
    viewport.addEventListener("mousemove",  e => { if (!isDragging) return; dragDelta = e.clientX - startX; });
    viewport.addEventListener("mouseup",    () => settle());
    viewport.addEventListener("mouseleave", () => { if (isDragging) settle(); });

    viewport.addEventListener("touchstart", e => { startX = e.touches[0].clientX; isDragging = true; }, { passive: true });
    viewport.addEventListener("touchmove",  e => { if (!isDragging) return; dragDelta = e.touches[0].clientX - startX; }, { passive: true });
    viewport.addEventListener("touchend",   () => settle());

    function settle() {
        isDragging = false;
        viewport.style.cursor = "grab";
        const threshold = cardWidth() * 0.2;
        if (dragDelta < -threshold) goTo(current + 1);
        else if (dragDelta > threshold) goTo(current - 1);
        else goTo(current);
        dragDelta = 0;
    }

    // Hover states on nav buttons
    [prevBtn, nextBtn].forEach(btn => {
        if (!btn) return;
        btn.addEventListener("mouseenter", () => { btn.style.background = "#e43388"; btn.style.borderColor = "#e43388"; });
        btn.addEventListener("mouseleave", () => { btn.style.background = "#1a1a1a"; btn.style.borderColor = "#333"; });
    });

    // Scroll-reveal
    gsap.from(cards, {
        opacity: 0, scale: 0.95, duration: 0.6, ease: "power3.out", stagger: 0.06,
        scrollTrigger: { trigger: viewport, start: "top 85%", once: true }
    });
})();


// ── 1G — VIDEO CAROUSEL ───────────────────────────────────────────

(function initVideoCarousel() {
    const viewport = document.querySelector(".video-viewport");
    if (!viewport) return;

    const track   = viewport.querySelector(".video-track");
    const cards   = Array.from(track.querySelectorAll(".video-card"));
    const prevBtn = document.querySelector(".video-prev");
    const nextBtn = document.querySelector(".video-next");
    if (!track || !cards.length) return;

    const gap      = 12;
    let current    = 0;
    let startX     = 0;
    let isDragging = false;
    let dragDelta  = 0;

    function cardWidth() {
        return cards[0].getBoundingClientRect().width + gap;
    }

    function visibleCount() {
        return Math.round(viewport.offsetWidth / cardWidth());
    }

    function maxIndex() {
        return Math.max(0, cards.length - visibleCount());
    }

    function goTo(index, instant) {
        current = Math.max(0, Math.min(index, maxIndex()));
        gsap.to(track, {
            x: -(current * cardWidth()),
            duration: instant ? 0 : 0.45,
            ease: "power3.out"
        });
    }

    if (prevBtn) prevBtn.addEventListener("click", () => goTo(current - 1));
    if (nextBtn) nextBtn.addEventListener("click", () => goTo(current + 1));

    viewport.addEventListener("mousedown",  e => { isDragging = true; startX = e.clientX; viewport.style.cursor = "grabbing"; });
    viewport.addEventListener("mousemove",  e => { if (!isDragging) return; dragDelta = e.clientX - startX; });
    viewport.addEventListener("mouseup",    () => settle());
    viewport.addEventListener("mouseleave", () => { if (isDragging) settle(); });

    viewport.addEventListener("touchstart", e => { startX = e.touches[0].clientX; isDragging = true; }, { passive: true });
    viewport.addEventListener("touchmove",  e => { if (!isDragging) return; dragDelta = e.touches[0].clientX - startX; }, { passive: true });
    viewport.addEventListener("touchend",   () => settle());

    function settle() {
        isDragging = false;
        viewport.style.cursor = "grab";
        const threshold = cardWidth() * 0.2;
        if (dragDelta < -threshold) goTo(current + 1);
        else if (dragDelta > threshold) goTo(current - 1);
        else goTo(current);
        dragDelta = 0;
    }

    // Hover states on nav buttons
    [prevBtn, nextBtn].forEach(btn => {
        if (!btn) return;
        btn.addEventListener("mouseenter", () => { btn.style.background = "#e43388"; btn.style.borderColor = "#e43388"; });
        btn.addEventListener("mouseleave", () => { btn.style.background = "#1a1a1a"; btn.style.borderColor = "#333"; });
    });

    window.__videoCarouselGoTo = (idx, instant) => goTo(idx, instant);

    // Video facade — replace thumbnail with autoplay iframe on click
    track.querySelectorAll(".video-facade").forEach(facade => {
        facade.addEventListener("click", function() {
            const vid = this.dataset.vid;
            if (!vid) return;
            this.innerHTML = '<iframe src="https://www.youtube.com/embed/' + vid + '?autoplay=1&rel=0" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen style="width:100%;aspect-ratio:9/16;display:block;border:none;"></iframe>';
            this.style.cursor = "default";
        });
    });

    // Scroll-reveal
    gsap.from(cards, {
        opacity: 0, scale: 0.95, duration: 0.6, ease: "power3.out", stagger: 0.06,
        scrollTrigger: { trigger: viewport, start: "top 85%", once: true }
    });
})();


// ── MUSCLE POINTS — PER-DECADE COPY ──────────────────────────────

const musclePoints = {
    "20s": [
        { h: "Your Prime Muscle-Building Years",  p: "You're in the window most women don't know is closing. What you build now shapes how strong, confident, and capable your body will be for the rest of your life. Skip this decade and you risk trading muscle for body fat, strength for sluggishness, and clarity for brain fog." },
        { h: "A Better Brain, Not Just a Better Body", p: "Strength training sharpens your focus, reduces mood crashes, and improves concentration. You're not just training for how you look — you're building a brain that performs, a mindset that holds, and a future-proofed version of you." },
        { h: "Joints That Last a Lifetime",       p: "Strong muscles are your joints' primary protection. Build the connective tissue strength now that keeps your knees, hips, and back healthy through decades of sport, life, and movement. The wear that shows up at 40 starts with what you do — or don't do — in your 20s." },
        { h: "Peak Bone Density Closes at 30",    p: "The window to build your maximum bone density closes around age 30. Every session now is a deposit you'll draw on in your 50s and 60s. Build your base. Build your muscle. Build YOU." }
    ],
    "30s": [
        { h: "The Window Is Still Open — But Closing", p: "Muscle loss begins around 30 — quietly, up to 250g per year. Your 20s and 30s are your prime time for muscle-building. Skip it now and you risk trading muscle for fat, strength for sluggishness, and clarity for brain fog. The gap between trained and untrained is already opening." },
        { h: "Strength Is Stress Medicine",       p: "Your 30s are often peak-demand years — career, family, everything at once. Strength training regulates cortisol, stabilises your hormones, and gives you the energy and resilience to run at the pace life is asking of you. It's not a luxury. It's maintenance." },
        { h: "Protect Your Future Joints",        p: "The joint wear that surfaces at 50 starts silently in your 30s. Progressive loading builds the muscular support around your knees, hips, and spine that keeps you moving well for the decades ahead." },
        { h: "Last Chance to Build Bone",         p: "Your 30s are the final decade where you can meaningfully increase bone density. After this, the goal shifts from building to preserving. Train now and you'll have significantly more to protect when it matters most." }
    ],
    "40s": [
        { h: "You Are Not Broken",                p: "Since puberty, this is the biggest hormonal shift you'll experience. The fogginess, low mood, and flat energy you might be feeling? That's your body asking for support, structure, and strength — not a sign you're past your prime. You're right on time." },
        { h: "Your Body Is Asking for Strength",  p: "Muscle isn't just about tone. It fuels your bones, sharpens your memory, lifts your mood, and keeps you resilient through perimenopause. What happens in your 40s shapes the next 20, 30, even 40 years of your life." },
        { h: "Your Joints Are Feeling the Shift", p: "Hormonal changes in your 40s affect joint lubrication and connective tissue. Targeted strength work rebuilds the muscular support your knees, hips, and lower back need to stay pain-free and functional." },
        { h: "Preservation Window Is Open",       p: "Estrogen is beginning to decline — and bone density goes with it. Resistance training is one of the most effective interventions available to slow this process before it accelerates in your 50s." }
    ],
    "50s": [
        { h: "It's Called Sarcopenia",            p: "Sarcopenia — the gradual, accelerating loss of muscle — moves fastest through your 50s. It doesn't care if you've been eating clean. Without training, losses of 1–2% per year compound into significant changes in strength, metabolism, and body composition." },
        { h: "Never Too Late — But Too Late to Keep Waiting", p: "Muscle fuels your bones, sharpens your memory, lifts your mood, and keeps you resilient through menopause. It's never too late to start. But it is too late to keep waiting." },
        { h: "Fall Prevention Starts Now",        p: "The balance, coordination, and leg strength you build in your 50s determines your injury risk in your 60s and 70s. Hip fractures that change lives are often traced back to muscle weakness that began here." },
        { h: "Bone Loss Is Accelerating",         p: "You hit peak bone density at 30. If you haven't been strength training consistently since then, you've already lost some of it. Progressive loading can slow the decline significantly — and in many cases, reverse it." }
    ],
    "60s": [
        { h: "This Decade Defines Your 70s",      p: "The gap between trained and untrained women is now 18 percentage points of muscle mass. Women who maintain structured training through their 60s move, think, and feel dramatically differently. A body that doesn't just hold up — but thrives." },
        { h: "Confidence Is a Side Effect",       p: "Confidence in your clothes and out of them. A sharper, more focused brain. A body that feels capable and like yours again. These are documented outcomes of consistent strength training — at any age, including yours." },
        { h: "Stay Structurally Sound",           p: "Joint integrity and balance are critical in your 60s. Consistent training gives you stronger hips, knees, and ankles — and dramatically lower risk of the falls and fractures that derail independence." },
        { h: "It's Never Too Late. But It's Too Late to Wait.", p: "Bone density, muscle mass, and functional independence all respond to training. Not next Monday. Not next year. The best time to start was 10 years ago. The next best time is right now." }
    ],
    "70s+": [
        { h: "You Can Still Build Muscle",        p: "Research consistently shows women in their 70s and 80s build meaningful muscle with progressive training. The trained woman at 70 reflects the fitness of an untrained woman at 55. You're not where you need to stay — you're where you choose to start." },
        { h: "A Sharper Brain at Every Age",      p: "Fewer energy crashes. Sharper focus. A body that feels capable and confident. These aren't reserved for younger women — they're the documented outcomes of consistent strength training. A sense of self that glows from the inside out." },
        { h: "Functional Independence Is the Goal", p: "The ability to rise from a chair, climb stairs, and move without assistance is directly tied to lower-body strength. Training preserves the functional capacity that determines your independence — and your quality of life." },
        { h: "You Didn't Break. You Evolved.",    p: "It's never too late. Women who begin strength training in their 70s see measurable improvements in bone density, balance, and fracture resistance within months. Now let's build." }
    ]
};

const transformationImages = {
    "pregnancy":     { src: "https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/bec-postpartum-before-after.png", alt: "Bec's transformation at The Evolved", caption: "Bec — 6 months" },
    "perimenopause": { src: "https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/tash-40s-transformation.png",  alt: "Tash's transformation at The Evolved",    caption: "Tash — 12 months" },
    "postmenopause": { src: "https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/vicki-50s-6m.png",              alt: "Vicky's transformation at The Evolved",   caption: "Vicky — 6 months" },
    "20s":  { src: "https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/monique-20s-transformation.png", alt: "Monique's transformation at The Evolved", caption: "Monique — 18 months" },
    "30s":  { src: "https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/leisa-30s-transformation.png", alt: "Leisa's transformation at The Evolved", caption: "Leisa — 6 months" },
    "40s":  { src: "https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/tash-40s-transformation.png", alt: "Tash's transformation at The Evolved", caption: "Tash — 12 months" },
    "50s":  { src: "https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/helen-50s-transformation.png", alt: "Helen's transformation at The Evolved", caption: "Helen — 12 months" },
    "60s":  { src: "https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/eleni-60s-transformation.png", alt: "Eleni's transformation at The Evolved", caption: "Eleni — 12 months" },
    "70s+": { quote: "I wasn't sure my knee would let me train properly. But the coaches just adapt — every session, they work around it without making it a big deal. The women here keep me accountable in the best way. We show up for each other. And being strong means I can get down on the floor with my grandkids, play, move, keep up. That's what it's all for.", name: "Sharon" }
};

const transformationCards = {
    // Stage overrides — always shown first when a life stage is selected
    "pregnancy":     [
        { src: "https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/bec-postpartum-before-after.png", alt: "Bec's transformation",   caption: "Bec — 6 months" },
        { src: "https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/kerrie-40s-12m.png",              alt: "Kerrie's transformation", caption: "Kerrie — 12 months" },
        { src: "https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/kylie-40s-6m.png",                alt: "Kylie's transformation",  caption: "Kylie — 6 months" }
    ],
    "perimenopause": [
        { src: "https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/tash-40s-transformation.png", alt: "Tash's transformation",   caption: "Tash — 12 months" },
        { src: "https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/tammy-40s-6m.png",            alt: "Tammy's transformation",  caption: "Tammy — 6 months" },
        { src: "https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/karyn-40s-12m.png",           alt: "Karyn's transformation",  caption: "Karyn — 12 months" }
    ],
    "postmenopause": [
        { src: "https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/vicki-50s-6m.png",             alt: "Vicky's transformation", caption: "Vicky — 6 months" },
        { src: "https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/helen-50s-transformation.png", alt: "Helen's transformation", caption: "Helen — 12 months" },
        { src: "https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/eleni-60s-transformation.png", alt: "Eleni's transformation", caption: "Eleni — 18 months" }
    ],
    // Decade fallbacks — filled to 3 using closest relevant
    "20s":  [
        { src: "https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/katrina-20s-12m.png",  alt: "Katrina's transformation", caption: "Katrina — 12 months" },
        { src: "https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/isabelle-20s-12m.png", alt: "Isabelle's transformation", caption: "Isabelle — 12 months" },
        { src: "https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/alana-20s-6m.png",     alt: "Alana's transformation",    caption: "Alana — 6 months" }
    ],
    "30s":  [
        { src: "https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/ruth-30s-12m.png",      alt: "Ruth's transformation",      caption: "Ruth — 12 months" },
        { src: "https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/megan-30s-12m.png",     alt: "Megan's transformation",     caption: "Megan — 12 months" },
        { src: "https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/charmaine-30s-12m.png", alt: "Charmaine's transformation", caption: "Charmaine — 12 months" }
    ],
    "40s":  [
        { src: "https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/tammy-40s-6m.png",            alt: "Tammy's transformation", caption: "Tammy — 6 months" },
        { src: "https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/tash-40s-transformation.png", alt: "Tash's transformation",  caption: "Tash — 12 months" },
        { src: "https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/karyn-40s-12m.png",           alt: "Karyn's transformation", caption: "Karyn — 12 months" }
    ],
    "50s":  [
        { src: "https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/vicki-50s-6m.png",             alt: "Vicky's transformation", caption: "Vicky — 6 months" },
        { src: "https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/helen-50s-transformation.png", alt: "Helen's transformation", caption: "Helen — 12 months" },
        { src: "https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/tammy-40s-6m.png",            alt: "Tammy's transformation", caption: "Tammy — 6 months" }
    ],
    "60s":  [
        { src: "https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/eleni-60s-transformation.png", alt: "Eleni's transformation", caption: "Eleni — 18 months" },
        { src: "https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/helen-50s-transformation.png", alt: "Helen's transformation", caption: "Helen — 12 months" },
        { src: "https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/vicki-50s-6m.png",             alt: "Vicky's transformation", caption: "Vicky — 6 months" }
    ],
    "70s+": [
        { src: "https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/eleni-60s-transformation.png", alt: "Eleni's transformation", caption: "Eleni — 18 months" },
        { src: "https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/helen-50s-transformation.png", alt: "Helen's transformation", caption: "Helen — 12 months" },
        { src: "https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/vicki-50s-6m.png",             alt: "Vicky's transformation", caption: "Vicky — 6 months" }
    ]
};

function updateDecadeCards(bracket) {
    const stageId = window.__pyjStageId || null;
    const cards = (stageId && transformationCards[stageId]) ? transformationCards[stageId] : (transformationCards[bracket] || []);
    const row   = document.getElementById("decade-cards-row");
    if (!row) return;

    let anyVisible = false;
    [1, 2, 3].forEach(n => {
        const slot = document.getElementById(`dc-${n}`);
        const img  = document.getElementById(`dc-${n}-img`);
        const cap  = document.getElementById(`dc-${n}-cap`);
        const data = cards[n - 1];
        if (!slot) return;
        if (data) {
            img.src = data.src;
            img.alt = data.alt || "";
            if (cap) cap.textContent = data.caption || "";
            slot.style.display = "block";
            anyVisible = true;
        } else {
            slot.style.display = "none";
        }
    });

    if (anyVisible) {
        row.style.display = "block";
        gsap.fromTo(row, { opacity: 0, y: 16 }, { opacity: 1, y: 0, duration: 0.5, ease: "power2.out" });
    } else {
        row.style.display = "none";
    }
}

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

    const stageOverride = window.__pyjStageId && transformationImages[window.__pyjStageId] ? window.__pyjStageId : null;
    const entry     = transformationImages[stageOverride || bracket];
    const imgWrap   = document.getElementById("decade-transform");
    const quoteWrap = document.getElementById("decade-quote");

    // Reset both
    if (imgWrap)   imgWrap.style.display   = "none";
    if (quoteWrap) quoteWrap.style.display = "none";

    if (entry && entry.src) {
        const imgEl = document.getElementById("decade-transform-img");
        const cap   = document.getElementById("decade-transform-caption");
        imgEl.src = entry.src;
        imgEl.alt = entry.alt || "";
        if (cap) cap.textContent = entry.caption || "";
        imgWrap.style.display = "block";
        gsap.fromTo(imgEl,
            { scale: 0.9, filter: "brightness(0.15)", clipPath: "inset(6% 0 6% 0 round 6px)" },
            { scale: 1,   filter: "brightness(1)",    clipPath: "inset(0% 0 0% 0 round 6px)",
              duration: 1.1, ease: "power3.out" }
        );
        gsap.fromTo(imgWrap, { opacity: 0 }, { opacity: 1, duration: 0.4, ease: "power2.out" });
    } else if (entry && entry.quote) {
        const qText = document.getElementById("decade-quote-text");
        const qName = document.getElementById("decade-quote-name");
        if (qText) qText.textContent = "\u201C" + entry.quote + "\u201D";
        if (qName) qName.textContent = "\u2014 " + entry.name;
        quoteWrap.style.display = "block";
        gsap.fromTo(quoteWrap, { opacity: 0, y: 12 }, { opacity: 1, y: 0, duration: 0.5, ease: "power2.out" });
    }
}


// ── SARCOPENIA CHART ──────────────────────────────────────────────

const sarcopeniaData = {
    labels: ["20","30","40","50","60","70","80"],
    noTraining:   [100,97,91,82,70,56,42],
    withTraining: [100,99,97,93,88,80,70],
};

const ageBrackets = {
    "20s": 0, "30s": 1, "40s": 2, "50s": 3, "60s": 4, "70s+": 5
};

const sarcopeniaAnnotations = {
    "20s":  "You are at or near peak muscle mass right now. The window to build your foundation is open — the habits you form now compound over decades.",
    "30s":  "Muscle loss has begun — slowly. Most women in their 30s do not notice it yet. The gap between the two curves is still small, and this is the best time to close it permanently.",
    "40s":  "Without training, women in their 40s have typically lost 9% of their peak muscle mass. With consistent strength training, that loss is less than 3%. The Strength Assessment shows exactly where you fall.",
    "50s":  "After 50, muscle loss accelerates. Women without a structured program can lose 18% of peak muscle mass by this decade. The good news: it is reversible.",
    "60s":  "The gap between the two curves is now 18 percentage points — the difference in metabolism, bone density, fall risk, and functional independence.",
    "70s+": "Strength training at 70+ builds muscle, improves bone density, and extends functional independence. The curve for trained women at 70 is where untrained women are at 55."
};

function initSarcopeniaChart() {
    const canvas = document.getElementById("sarcopeniaChart");
    if (!canvas) return null;
    return new Chart(canvas.getContext("2d"), {
        type: "line",
        data: {
            labels: sarcopeniaData.labels,
            datasets: [
                { label: "Without strength training", data: sarcopeniaData.noTraining,
                  borderColor: "#888", borderDash: [6,4], borderWidth: 2, pointRadius: 0, tension: 0.4, fill: false },
                { label: "With consistent strength training", data: sarcopeniaData.withTraining,
                  borderColor: "#e43388", borderWidth: 3, pointRadius: 0, tension: 0.4, fill: false },
            ]
        },
        options: {
            responsive: true,
            animation: { duration: 1200 },
            plugins: {
                legend: { labels: { color: "#f5f0eb", font: { family: "Lato", size: 13 } } },
                tooltip: { enabled: false }
            },
            scales: {
                x: { ticks: { color: "#aaa" }, grid: { color: "#222" }, title: { display: true, text: "Age", color: "#aaa" } },
                y: { min: 30, max: 105, ticks: { color: "#aaa", callback: v => v + "%" }, grid: { color: "#222" },
                     title: { display: true, text: "Relative Muscle Mass", color: "#aaa" } }
            }
        }
    });
}

function selectAgeBracket(chart, bracket) {
    const index = ageBrackets[bracket];
    chart.data.datasets[0].pointRadius = chart.data.datasets[0].data.map((_,i) => i===index ? 8 : 0);
    chart.data.datasets[0].pointBackgroundColor = "#888";
    chart.data.datasets[1].pointRadius = chart.data.datasets[1].data.map((_,i) => i===index ? 10 : 0);
    chart.data.datasets[1].pointBackgroundColor = "#e43388";
    chart.update();
    const el = document.getElementById("sarcopeniaAnnotation");
    if (el) {
        el.textContent = sarcopeniaAnnotations[bracket];
        gsap.fromTo(el, { opacity: 0, y: 10 }, { opacity: 1, y: 0, duration: 0.5, ease: "power2.out" });
    }
    if (false) {
    }
}


// ── TIER 1 PERSONALISATION ────────────────────────────────────────

const RC_EXPERIENCE = {
    "new":         { rate: 1.20, peak: 1.00, membership: "fasttrack"    },
    "some":        { rate: 1.00, peak: 1.00, membership: "sculptstrength" },
    "experienced": { rate: 0.85, peak: 0.82, membership: "sculptstrength" },
};

function rcHighlightMembership(experience) {
    const target = RC_EXPERIENCE[experience] ? RC_EXPERIENCE[experience].membership : "sculptstrength";
    document.querySelectorAll(".membership-card").forEach(card => {
        const isTarget = card.dataset.mc === target;
        card.style.border     = isTarget ? "1px solid #e43388" : "1px solid #222";
        card.style.boxShadow  = isTarget ? "0 8px 32px rgba(228,51,136,0.2)" : "none";
        let badge = card.querySelector(".rc-rec-badge");
        if (isTarget && !badge) {
            badge = document.createElement("div");
            badge.className = "rc-rec-badge";
            badge.style.cssText = "position:absolute;top:12px;left:12px;z-index:3;background:#e43388;color:#fff;font-family:'Lato',sans-serif;font-size:0.65rem;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;padding:4px 10px;border-radius:3px;pointer-events:none;";
            badge.textContent = "Recommended for you";
            card.appendChild(badge);
        } else if (!isTarget && badge) {
            badge.remove();
        }
    });
}

const RC_CTA_COPY = {
    "lose-weight": {
        "20s": { h: "Stop spinning your wheels. Start seeing results.",                         sub: "One assessment. A clear plan. Real weight loss \u2014 without the guesswork." },
        "30s": { h: "Stop spinning your wheels. Start seeing results.",                         sub: "One assessment. A clear plan. Real weight loss \u2014 without the guesswork." },
        "40s": { h: "Ready to lose the weight without losing your life to it?",                 sub: "One hour. A complete picture of where you are. A clear path forward." },
        "50s": { h: "It\u2019s never too late to change what your next 20 years look like.",    sub: "One assessment. A personalised plan built around where you are right now." },
        "60s": { h: "It\u2019s never too late to change what your next 20 years look like.",    sub: "One assessment. A personalised plan built around where you are right now." },
    },
    "recomp": {
        "20s": { h: "Build the body you\u2019ve always wanted \u2014 muscle first, everything else follows.", sub: "One assessment. A plan that actually works for your goals and your body." },
        "30s": { h: "Build the body you\u2019ve always wanted \u2014 muscle first, everything else follows.", sub: "One assessment. A plan that actually works for your goals and your body." },
        "40s": { h: "Less fat. More muscle. More energy. It\u2019s all possible in your 40s.",  sub: "One assessment. A complete picture of where you are. A clear path forward." },
        "50s": { h: "Stronger, leaner, and more capable than you\u2019ve been in years.",       sub: "One assessment. A personalised plan built for peri- and post-menopausal women." },
        "60s": { h: "Stronger, leaner, and more capable than you\u2019ve been in years.",       sub: "One assessment. A personalised plan built for peri- and post-menopausal women." },
    },
    "gain-muscle": {
        "20s": { h: "Build the muscle that changes your strength, shape, and energy.",          sub: "One assessment. A program built to add real muscle \u2014 not just numbers on a scale." },
        "30s": { h: "Build the muscle that changes your strength, shape, and energy.",          sub: "One assessment. A program built to add real muscle \u2014 not just numbers on a scale." },
        "40s": { h: "The strongest version of yourself starts with the right program.",         sub: "One assessment. A personalised plan that builds muscle and fights the effects of ageing." },
        "50s": { h: "More muscle means more of everything \u2014 energy, strength, independence.", sub: "One assessment. A personalised plan for building real strength in your 50s." },
        "60s": { h: "Muscle is the architecture of a long, strong, independent life.",          sub: "One assessment. A program that builds strength and protects the next 20 years." },
    },
    "bone-density": {
        "default": { h: "Build the strength that protects the next 30 years of your life.",    sub: "One assessment. A clear picture of where your bones and body are right now." },
    },
    "get-stronger": {
        "default": { h: "Strength isn\u2019t a gift. It\u2019s built. Let\u2019s build yours.", sub: "One assessment. A personalised strength program that actually progresses." },
    },
    "hyrox": {
        "default": { h: "Ready to compete at your first HYROX \u2014 or take serious time off your next one?", sub: "One assessment. A training plan built for performance, not just fitness." },
    },
};

function rcUpdateFinalCTA(goalId, decade) {
    const h2El  = document.getElementById("final-cta-h2");
    const subEl = document.getElementById("final-cta-sub");
    if (!h2El || !subEl) return;
    const goalCopy = RC_CTA_COPY[goalId];
    if (!goalCopy) return;
    const copy = goalCopy[decade] || goalCopy["default"];
    if (!copy) return;
    if (h2El.textContent !== copy.h) {
        gsap.to(h2El, { opacity: 0, y: -6, duration: 0.18, onComplete: () => {
            h2El.textContent = copy.h;
            gsap.to(h2El, { opacity: 1, y: 0, duration: 0.3, ease: "power2.out" });
        }});
    }
    if (subEl.textContent !== copy.sub) {
        gsap.to(subEl, { opacity: 0, duration: 0.18, onComplete: () => {
            subEl.textContent = copy.sub;
            gsap.to(subEl, { opacity: 1, duration: 0.3, ease: "power2.out" });
        }});
    }
}

const RC_PROFILE_STORIES = {
    "lose-weight": {
        "20s": { name: "Katrina",   blurb: "Working FIFO on-site, Katrina trained four days a week and said goodbye to takeaway \u2014 even from the mine site. She wanted to lose 20\u202fkg and shop in the same stores as her friends. A quiet achiever who let her results do the talking.", anchor: ".carousel-viewport" },
        "30s": { name: "Katherine", blurb: "Years of on-again-off-again training felt like failure. But each attempt made her stronger. Then something clicked \u2014 she committed fully and lost 15\u202fkg in just 6 months. Every restart was a step closer.", anchor: ".carousel-viewport" },
        "40s": { name: "Tash",      blurb: "Her doctor\u2019s warning was stark: lose weight or your heart condition deteriorates within five years. As a night-shift nurse addicted to Coca-Cola, Tash chose strength over cardio \u2014 and lost 20\u202fkg in 14 months without a single treadmill session. Her personal goal underneath it all: to finally ride a roller coaster. She can now.", anchor: ".carousel-viewport" },
        "50s": { name: "Vicky",     blurb: "Gave herself 7 weeks to get fitness-model lean for her 50th birthday photoshoot. Smarter training and better nutrition delivered abs, a 60\u202fkg squat, and her first chin-up \u2014 right on deadline.", anchor: ".carousel-viewport" },
        "60s": { name: "Helen",     blurb: "Moving house, state rep hockey, full-time work, and volunteering \u2014 Helen\u2019s 12 weeks were anything but ideal. She showed up anyway and lost 7\u202fkg. Life will always be busy. You can still put yourself first.", anchor: ".carousel-viewport" },
    },
    "recomp": {
        "20s": { name: "Monique",   blurb: "Balancing uni and work, Monique lost 12.8\u202fkg in 5 months and doubled her squat from 26\u202fkg to 63\u202fkg \u2014 at the same time. The scale and the barbell moved together.", anchor: ".carousel-viewport" },
        "30s": { name: "Ruth",      blurb: "Was training 9 hours a week and seeing nothing. She wanted the results she was working so hard for. Cut to 3 hours, trained smarter, and dropped 4\u202fcm off her waist. The work wasn\u2019t the problem \u2014 the approach was.", anchor: ".carousel-viewport" },
        "40s": { name: "Tammy",     blurb: "Tammy came in stressed and wanting to change how her body looked. She didn\u2019t realise the connection between her body composition and her adenomyosis. Through consistent strength training and eating well, her inflammation reduced, her painful periods disappeared entirely, and she dropped two dress sizes. A body goal led to a life-changing health discovery.", anchor: ".carousel-viewport" },
        "50s": { name: "Vicky",     blurb: "Gave herself 7 weeks to get fitness-model lean for her 50th birthday photoshoot. Smarter training and better nutrition delivered abs, a 60\u202fkg squat, and her first chin-up \u2014 right on deadline.", anchor: ".carousel-viewport" },
        "60s": { name: "Eleni",     blurb: "Diagnosed with osteoporosis at 63, Eleni stepped up from Pilates to strength training. 18 months later, her DEXA scan confirmed her spine had improved from osteoporosis to osteopenia. Strength and mental wellbeing both transformed.", anchor: ".carousel-viewport" },
    },
    "gain-muscle": {
        "20s": { name: "Katrina",  blurb: "Working FIFO on-site didn\u2019t stop Katrina building the strongest version of herself. She trained four days a week \u2014 even from the mine site. She didn\u2019t just lose 20\u202fkg. She built the muscle underneath that now defines her physique.", anchor: ".carousel-viewport" },
        "30s": { name: "Megan",    blurb: "Chronic exhaustion had Megan convinced she needed to eat less and train more. The opposite was true. Eating more and lifting heavy overhauled her physique, reclaimed her energy, and gave her the vitality she thought she\u2019d lost for good.", anchor: ".carousel-viewport" },
        "40s": { name: "Jules",    blurb: "Jules had never lifted weights before she walked in just before turning 40. Five years as a foundation member later \u2014 she\u2019s the one telling new members: \u201cYou only live once \u2014 give it a go.\u201d The muscle she\u2019s built since has changed everything.", anchor: ".carousel-viewport" },
        "50s": { name: "Vicky",    blurb: "In 7 weeks at 50, Vicky unlocked visible abs, a 60\u202fkg squat, and her first-ever chin-up. What\u2019s possible when you train to build rather than just burn? More than most women in their 50s realise.", anchor: ".carousel-viewport" },
        "60s": { name: "Eleni",    blurb: "Diagnosed with osteoporosis at 63, Eleni stepped up to heavy strength training. 18 months later her DEXA scan confirmed her spine had improved from osteoporosis to osteopenia. Muscle isn\u2019t just about how you look \u2014 it\u2019s the architecture of a long, strong life.", anchor: ".carousel-viewport" },
    },
    "bone-density": {
        "default": { name: "Eleni", blurb: "Diagnosed with osteoporosis at 63, Eleni stepped up from Pilates to strength training. 18 months later, her DEXA scan confirmed her spine had improved from osteoporosis to osteopenia. The diagnosis that could have defined her decline became the starting point of her strongest chapter.", anchor: ".carousel-viewport" },
    },
    "get-stronger": {
        "20s": { name: "Isabelle",  blurb: "Standing at a crossroads before starting full-time work, Isabelle had never set foot in a gym. With a community of women behind her and consistency as her guide, she absolutely thrived.", anchor: ".carousel-viewport" },
        "30s": { name: "Leisa",     blurb: "A former powerlifter who wanted what powerlifting couldn\u2019t give her \u2014 leaner, stronger, full of energy. Twelve months later she\u2019d transformed her body composition and ran her first marathon.", anchor: ".carousel-viewport" },
        "40s": { name: "Jules",     blurb: "Jules had never lifted weights before she walked in just before turning 40. She\u2019s been a foundation member for over five years. \u201cYou only live once \u2014 give it a go.\u201d She still says that to every new member.", anchor: ".carousel-viewport" },
        "50s": { name: "Belinda",   blurb: "Diagnosed with frozen shoulder in her 50s, she could barely hold a glass of water in one hand. She had never been to a gym. She built to 35kg — and now moves tonnes of gravel on weekends.", anchor: ".carousel-viewport" },
        "60s": { name: "Eleni",     blurb: "Eleni came in with an osteoporosis diagnosis at 63. 18 months of consistent strength training later, her DEXA scan confirmed her spine had improved from osteoporosis to osteopenia. The body responds at every age.", anchor: ".carousel-viewport" },
    },
    "hyrox": {
        "20s": { name: "Jess", blurb: "Five years of gym-going with no structure or real results. Once she found progressive overload at The Evolved, everything clicked \u2014 body recomposition, first chin-up, and HYROX completed with her partner within a year.", anchor: ".video-viewport" },
        "default": { name: "Johanna", blurb: "Came in wanting to get stronger and fitter. Became the most consistent member \u2014 6 days a week for 2.5 years. That consistency led to a Spartan race, then HYROX the following year, completed alongside her eldest daughter in under 90 minutes.", anchor: ".video-viewport" },
    },
};

function rcGetStory(goalId, decade) {
    const goalStories = RC_PROFILE_STORIES[goalId];
    if (!goalStories) return null;
    return goalStories[decade] || goalStories["default"] || null;
}

// ── CAROUSEL REORDER ─────────────────────────────────────────────────────
function rcReorderCarousel(goalId, decade) {
    const track = document.querySelector(".carousel-track");
    if (!track) return;
    const stageId = window.__pyjStageId || null;
    const cards = Array.from(track.querySelectorAll(".carousel-card"));
    const scored = cards.map(card => ({
        card,
        score: (stageId && card.dataset.stage === stageId ? 5 : 0)
             + (card.dataset.goal === goalId ? 2 : 0)
             + (card.dataset.decade === decade ? 1 : 0)
    }));
    scored.sort((a, b) => b.score - a.score);
    scored.forEach(({ card }) => track.appendChild(card));
    if (typeof window.__carouselGoTo === "function") window.__carouselGoTo(0, true);
}

function rcReorderVideos(goalId, decade) {
    const track = document.querySelector(".video-track");
    if (!track) return;
    const cards = Array.from(track.querySelectorAll(".video-card"));
    const scored = cards.map(card => ({
        card,
        score: (card.dataset.goal === goalId ? 2 : 0) + (card.dataset.decade === decade ? 1 : 0)
    }));
    scored.sort((a, b) => b.score - a.score);
    scored.forEach(({ card }) => track.appendChild(card));
    if (typeof window.__videoCarouselGoTo === "function") window.__videoCarouselGoTo(0, true);
}

// ── FAQ PERSONALISATION ───────────────────────────────────────────────────
// Universal top 3 for every goal × decade combination.
// Everyone scrolling to FAQs wants price and more info.
// The answer is always: assess first → not a sales pitch → spots are limited.
// Q1=cost, Q2=first visit, Q0=can I see the gym (waitlist/scarcity)
const RC_FAQ_PRIORITY = [1, 2, 0];

function rcUpdateFAQ(goalId, decade) {
    const container = document.getElementById("faq-list");
    if (!container) return;
    const staticItems = Array.from(container.querySelectorAll("details:not([data-faq-goal])"));
    const goalItems   = Array.from(container.querySelectorAll("details[data-faq-goal]"));
    const priority    = RC_FAQ_PRIORITY;

    // Clear highlights
    staticItems.forEach(el => { el.style.borderLeft = ""; el.style.paddingLeft = ""; });

    // Show/hide goal-specific items — respect both goal AND decade gates
    goalItems.forEach(el => {
        const goals   = el.dataset.faqGoal.split(",").map(g => g.trim());
        const decades = el.dataset.faqDecade ? el.dataset.faqDecade.split(",").map(d => d.trim()) : null;
        const show    = goals.includes(goalId) && (!decades || decades.includes(decade));
        el.style.display = show ? "" : "none";
    });

    if (!priority.length) return;
    const priorityItems = priority.map(i => staticItems[i]).filter(Boolean);
    priorityItems.forEach(el => container.insertBefore(el, container.firstChild));
    priorityItems.forEach(el => { el.style.borderLeft = "3px solid #e43388"; el.style.paddingLeft = "12px"; });
}

const RC_EXP_LABELS = { "new": "New to strength", "some": "Some experience", "experienced": "Experienced" };

function rcUpdateCTALinks(goalId, decade, experience) {
    const stageId     = window.__pyjStageId || null;
    const stage       = stageId ? PYJ_LIFE_STAGES[stageId] : null;
    const stageMatches = stage && stage.decade === decade;

    document.querySelectorAll(".primary-cta-btn").forEach(link => {
        if (stageMatches) {
            link.href = pyjLandingUrl(stage, goalId);
            const isSticky = link.style.flexShrink === "0";
            link.textContent = isSticky
                ? "Join the " + stage.label + " List \u2192"
                : "Join the " + stage.label + " Waitlist \u2192";
        } else {
            link.href = "#pyj-section";
            const isSticky = link.style.flexShrink === "0";
            link.textContent = isSticky ? "Join the Waitlist \u2192" : "Join the Waitlist";
        }
    });
}

function rcUpdatePillars(goalId) {
    const p = document.getElementById("pillar-programming");
    const n = document.getElementById("pillar-nutrition");
    const b = document.getElementById("pillar-behaviour");
    if (!p || !n || !b) return;
    const orders = {
        "lose-weight":  { p: 2, n: 1, b: 3 },
        "recomp":       { p: 2, n: 1, b: 3 },
        "gain-muscle":  { p: 1, n: 2, b: 3 },
        "bone-density": { p: 1, n: 3, b: 2 },
        "get-stronger": { p: 1, n: 3, b: 2 },
        "hyrox":        { p: 1, n: 2, b: 3 },
    };
    const o = orders[goalId] || { p: 1, n: 2, b: 3 };
    p.style.order = o.p;
    n.style.order = o.n;
    b.style.order = o.b;
}

function rcUpdateProfileBar(goalId, decade, experience) {
    const bar  = document.getElementById("profile-bar");
    const text = document.getElementById("profile-bar-text");
    if (!bar || !text) return;
    const goalCfg    = RC_GOALS.find(g => g.id === goalId);
    const goalLabel  = goalCfg ? goalCfg.label : goalId;
    const expLabel   = RC_EXP_LABELS[experience] || experience;
    const stageId    = window.__pyjStageId || null;
    const stageLabel = stageId && PYJ_LIFE_STAGES[stageId] ? PYJ_LIFE_STAGES[stageId].label : null;
    const prefix     = stageLabel ? stageLabel + " \u00b7 " : "";
    text.textContent = prefix + goalLabel + " \u00b7 " + decade + " \u00b7 " + expLabel;
    if (bar.style.display === "none" || bar.style.display === "") {
        bar.style.display = "flex";
        gsap.fromTo(bar, { y: 60, opacity: 0 }, { y: 0, opacity: 1, duration: 0.5, ease: "power3.out" });
    }
}

function rcUpdateProfilePanel(goalId, decade, score) {
    const panel   = document.getElementById("rc-profile-panel");
    const summary = document.getElementById("rc-profile-summary");
    const storyEl = document.getElementById("rc-profile-story");
    const linkEl  = document.getElementById("rc-profile-link");
    const photoEl = document.getElementById("rc-profile-photo");
    if (!panel) return;
    if (score < 0.1) { panel.style.display = "none"; return; }
    const stageId2  = window.__pyjStageId || null;
    const stage2    = stageId2 ? PYJ_LIFE_STAGES[stageId2] : null;
    const story = (stage2 && stage2.story) ? stage2.story : rcGetStory(goalId, decade);
    if (!story) { panel.style.display = "none"; return; }
    const goalLabel = RC_GOALS.find(g => g.id === goalId) ? RC_GOALS.find(g => g.id === goalId).label : goalId;
    if (summary) summary.textContent = decade + " \u00b7 " + goalLabel;
    if (storyEl) storyEl.textContent = story.blurb;
    if (linkEl) {
        linkEl.textContent = "See " + story.name + "\u2019s story \u2192";
        linkEl.onclick = function(e) {
            e.preventDefault();
            var target = document.querySelector(story.anchor);
            if (target) target.scrollIntoView({ behavior: "smooth", block: "center" });
        };
    }
    if (photoEl) {
        const photoUrl = PYJ_STORY_PHOTOS[story.name] || null;
        if (photoUrl) {
            photoEl.src = photoUrl;
            photoEl.alt = story.name;
            photoEl.style.display = "block";
        } else {
            photoEl.style.display = "none";
        }
    }
    if (panel.style.display === "none") {
        panel.style.display = "block";
        gsap.fromTo(panel, { opacity: 0, y: 10 }, { opacity: 1, y: 0, duration: 0.4, ease: "power2.out" });
    }
}


// ── PERSONALISED RESULTS CURVE ────────────────────────────────────

const RC_GOALS = [
    { id: "recomp",       label: "Lose Fat & Gain Muscle", yLabel: "% body fat reduced",       peak: 18,  unit: "%",   weights: [10,6,2,3,6], mealPlanFactor: 1.55 },
    { id: "gain-muscle",  label: "Gain Muscle",            yLabel: "kg lean muscle added",     peak: 5,   unit: "kg",  weights: [10,4,2,1,4], mealPlanFactor: 1.3  },
    { id: "bone-density", label: "Stronger Bones",         yLabel: "% bone density increase", peak: 7,   unit: "%",   weights: [9,5,2,3,5]  },
    { id: "get-stronger", label: "Get Stronger",           yLabel: "% strength increase",     peak: 55,  unit: "%",   weights: [10,3,2,1,5] },
    { id: "hyrox",        label: "Train for HYROX",        yLabel: "minutes off your time",   peak: 28,  unit: "min", weights: [7,8,1,6,10] },
    { id: "lose-weight",  label: "Lose Weight",            yLabel: "kg body fat lost",        peak: 14,  unit: "kg",  weights: [9,7,3,4,6],  mealPlanFactor: 1.75 },
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

function rcCurve(goalCfg, dec, exp, sessions, mealPlan) {
    const weights   = goalCfg.weights;
    const maxWeight = Math.max(...weights);
    const normalMax = 6 * maxWeight;
    let weeklyScore = 0;
    sessions.forEach((s, i) => { weeklyScore += s * weights[i]; });
    const score      = Math.min(weeklyScore, normalMax) / normalMax;
    const mealFactor = (mealPlan && goalCfg.mealPlanFactor) ? goalCfg.mealPlanFactor : 1.0;
    return RC_MONTHS.map(t => {
        const v = goalCfg.peak * mealFactor * dec.peak * exp.peak * score
                  * (1 - Math.exp(-RC_BASE_RATE * Math.sqrt(score) * dec.rate * exp.rate * t));
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

function rcAnnotation(goalCfg, decade, score, month12val, mealPlan, experience) {
    const decLabel = decade === "60s" ? "60s" : decade;
    const resultPhrase = {
        "lose-weight":  `lose ${month12val}kg of body fat`,
        "recomp":       `reduce body fat by ${month12val}%`,
        "gain-muscle":  `add ${month12val}kg of lean muscle`,
        "bone-density": `improve bone density by ${month12val}%`,
        "get-stronger": `increase strength by ${month12val}%`,
        "hyrox":        `take ${month12val} minutes off your HYROX time`,
    }[goalCfg.id];

    // Meal plan-specific annotation for eligible goals
    if (mealPlan && goalCfg.mealPlanFactor) {
        if (score < 0.25) {
            return `Adding The Evolved Smart Meal Plan is a strong move \u2014 but pairing it with at least 2\u20133 strength sessions per week is where the real results happen. Even a moderate training mix with the meal plan produces meaningful change.`;
        }
        if (score < 0.5) {
            return `Good combination. Members following The Evolved Smart Meal Plan alongside a training mix like this typically see visible changes within 8\u201312 weeks. A woman in her ${decLabel} can expect to ${resultPhrase} over 12 months.`;
        }
        if (goalCfg.id === "lose-weight") {
            return `This is the combination that drives real transformation. Members of The Evolved following our Smart Meal Plan alongside structured training have lost an average of 10\u202fkg in 6 months and 20\u202fkg over 12 months. Training fuels the muscle. Nutrition determines the fat loss.`;
        }
        if (goalCfg.id === "recomp") {
            return `Body recomposition accelerates significantly with structured nutrition. Members following The Evolved Smart Meal Plan alongside strength-focused training have achieved an average of 10\u202fkg of fat loss in 6 months and 20\u202fkg over 12 months \u2014 while gaining muscle. The meal plan is the multiplier.`;
        }
        if (goalCfg.id === "gain-muscle") {
            return `Nutrition is the single biggest lever for muscle gain. Members following The Evolved Smart Meal Plan alongside a strength-focused program consistently see better body composition \u2014 more muscle built, less fat accumulated. The training builds the muscle. The meal plan feeds it.`;
        }
    }

    if (score < 0.25) {
        return "This training mix will produce limited results over 12 months. Adding 2\u20133 strength sessions per week would significantly change this curve.";
    }
    if (score < 0.5) {
        return `A moderate training mix. A woman in her ${decLabel} following this plan can expect to ${resultPhrase} over 12 months. Adding more strength work would push this further.`;
    }
    if (score < 0.75) {
        return `A solid training mix. Based on published research, a woman in her ${decLabel} on this plan can expect to ${resultPhrase} by month 12.`;
    }
    let text = `An elite training frequency. Based on published research and real member outcomes, a woman in her ${decLabel} training at this level can expect to ${resultPhrase} by month 12.`;
    if (goalCfg.id === "hyrox") {
        text += " Our members training 6 days per week at The Evolved typically improve their HYROX completion time by 20\u201328 minutes in their first year.";
    }

    // Experience-level suffix
    if (experience === "new") {
        text += " As someone new to strength training, expect a significant spike in the first 8\u201312 weeks \u2014 neural adaptation means your body learns fast before the deeper physical changes begin.";
    } else if (experience === "experienced") {
        text += " As an experienced trainer, the law of diminishing returns applies \u2014 incremental gains are harder-won. But your floor is already well above average, and the right program compounds that advantage.";
    }
    return text;
}

// ── PICK YOUR JOURNEY 2026 ────────────────────────────────────────

const PYJ_LIFE_STAGES = {
    "teenager":      { label: "Teenager",       decade: "20s", exp: null, url: "https://theevolvedgym.com.au/teen-30dnnc-o"         },
    "20s30s":        { label: "20s \u2013 30s",  decade: "20s", exp: null,  url: "https://theevolvedgym.com.au/20s30s-30dnnc-o"        },
    "pregnancy":     { label: "Pregnancy",       decade: "30s", exp: null, url: "https://theevolvedgym.com.au/pregnancy-30dnnc-o",     story: { name: "Kerrie", blurb: "Fear of another premature baby drove her in. She committed to her health through pregnancy — controlled gestational diabetes, recovered faster after birth, and dropped two dress sizes in 12\u202fmonths. Her Christmas goal was a size 10 swimsuit. She nailed it." } },
    "perimenopause": { label: "Peri-Menopause",  decade: "40s", exp: null,  url: "https://theevolvedgym.com.au/perimenopause-30dnnc-o" },
    "postmenopause": { label: "Post-Menopause",  decade: "50s", exp: null,  url: "https://theevolvedgym.com.au/post-menopause-30dnnc-o"},
};

function pyjLandingUrl(stage, goalId) {
    return stage.url + "?goal=" + encodeURIComponent(goalId) + "&decade=" + encodeURIComponent(stage.decade);
}

const PYJ_STORY_PHOTOS = {
    "Katrina":  "https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/katrina-20s-12m.png",
    "Katherine":"https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/katherine-30s-6m.png",
    "Tash":     "https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/tash-40s-transformation.png",
    "Vicky":    "https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/vicki-50s-6m.png",
    "Helen":    "https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/helen-60s-transformation.png",
    "Bec":      "https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/bec-postpartum-before-after.png",
    "Monique":  "https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/monique-20s-transformation.png",
    "Ruth":     "https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/ruth-30s-12m.png",
    "Tammy":    "https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/tammy-40s-6m.png",
    "Eleni":    "https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/eleni-60s-transformation.png",
    "Isabelle": "https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/isabelle-20s-12m.png",
    "Leisa":    "https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/leisa-30s-transformation.png",
    "Megan":    "https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/megan-30s-12m.png",
    "Kerrie":   "https://blog.theevolvedgym.com.au/wp-content/uploads/2026/04/kerrie-40s-12m.png",
    "Jules":    "https://i.ytimg.com/vi/pHSmb9jTKoc/hqdefault.jpg",
    "Johanna":  "https://i.ytimg.com/vi/W6cDcI7I1zI/hqdefault.jpg",
    "Jess":     "https://i.ytimg.com/vi/7ud-x3UXcfM/hqdefault.jpg",
    "Belinda":  "https://i.ytimg.com/vi/CsICP4wSMG0/hqdefault.jpg",
    "Orlagh":   "https://i.ytimg.com/vi/WY01XSdmevk/hqdefault.jpg",
    "Peta":     "https://i.ytimg.com/vi/15q1XPdx1PU/hqdefault.jpg",
    "Tess":     "https://i.ytimg.com/vi/O-ToRNZwB1w/hqdefault.jpg",
    "Laura":    "https://i.ytimg.com/vi/G2vXxlVJ0nk/hqdefault.jpg",
    "Sophie":   "https://i.ytimg.com/vi/ATNysZlwUvg/hqdefault.jpg",
};

function pyjSelectLifeStage(stageId) {
    const stage = PYJ_LIFE_STAGES[stageId];
    if (!stage) return;
    window.__pyjStageId = stageId;

    document.querySelectorAll(".pyj-stage-btn").forEach(btn => {
        const on = btn.dataset.stage === stageId;
        btn.style.border    = on ? "2px solid #e43388" : "2px solid transparent";
        btn.style.transform = on ? "scale(1.03)" : "scale(1)";
        const chk = btn.querySelector(".pyj-check");
        if (chk) chk.style.display = on ? "block" : "none";
    });

    const section = document.getElementById("pyj-section");
    if (section) section.dataset.activeStage = stageId;

    const goalStep = document.getElementById("pyj-goal-step");
    if (goalStep) {
        if (goalStep.style.display === "none") {
            goalStep.style.display = "block";
            gsap.fromTo(goalStep, { opacity: 0, y: 16 }, { opacity: 1, y: 0, duration: 0.5, ease: "power3.out" });
        }
        setTimeout(() => {
            const y = goalStep.getBoundingClientRect().top + window.pageYOffset - 80;
            gsap.to("html, body", { scrollTop: y, duration: 0.5, ease: "power2.out" });
        }, 300);
    }

    const confirm = document.getElementById("pyj-confirm");
    if (confirm) confirm.style.display = "none";

    const expStep = document.getElementById("pyj-exp-step");
    if (expStep) expStep.style.display = "none";

    window.__pyjGoalId = null;

    // Notify both charts to preselect this decade
    document.dispatchEvent(new CustomEvent("pyj:stageDecade", { detail: { decade: stage.decade } }));
}

function pyjSelectGoal(goalId) {
    const section = document.getElementById("pyj-section");
    const stageId = section ? section.dataset.activeStage : null;
    const stage   = PYJ_LIFE_STAGES[stageId];
    if (!stage) return;

    window.__pyjGoalId = goalId;

    document.querySelectorAll(".pyj-goal-btn").forEach(btn => {
        const on = btn.dataset.goal === goalId;
        btn.style.background = on ? "#e43388"  : "transparent";
        btn.style.color      = on ? "#fff"      : "#f5f0eb";
        btn.style.border     = on ? "2px solid #e43388" : "2px solid #333";
    });

    // Hide confirm, show Step 3 experience selector
    const confirm = document.getElementById("pyj-confirm");
    if (confirm) confirm.style.display = "none";

    const expStep = document.getElementById("pyj-exp-step");
    if (expStep) {
        if (expStep.style.display === "none") {
            expStep.style.display = "block";
            gsap.fromTo(expStep, { opacity: 0, y: 16 }, { opacity: 1, y: 0, duration: 0.5, ease: "power3.out" });
        }
        // Reset exp buttons to unselected state
        document.querySelectorAll(".pyj-exp-btn").forEach(btn => {
            btn.style.background = "transparent";
            btn.style.color      = "#f5f0eb";
            btn.style.border     = "2px solid #333";
        });
        setTimeout(function() {
            const y = expStep.getBoundingClientRect().top + window.pageYOffset - 80;
            gsap.to("html, body", { scrollTop: y, duration: 0.5, ease: "power2.out" });
        }, 300);
    }
}

function pyjSelectExperience(expId) {
    const section = document.getElementById("pyj-section");
    const stageId = section ? section.dataset.activeStage : null;
    const stage   = PYJ_LIFE_STAGES[stageId];
    const goalId  = window.__pyjGoalId;
    if (!stage || !goalId) return;

    document.querySelectorAll(".pyj-exp-btn").forEach(btn => {
        const on = btn.dataset.exp === expId;
        btn.style.background = on ? "#e43388"  : "transparent";
        btn.style.color      = on ? "#fff"      : "#f5f0eb";
        btn.style.border     = on ? "2px solid #e43388" : "2px solid #333";
    });

    document.dispatchEvent(new CustomEvent("pyj:profileSet", {
        detail: { goal: goalId, decade: stage.decade, exp: expId }
    }));

    const ctaUrl  = pyjLandingUrl(stage, goalId);
    const story   = stage.story || rcGetStory(goalId, stage.decade);
    const headlineTpl = {
        "teenager":      "Your strength journey starts here.",
        "20s30s":        "Your path is set. Here\u2019s what\u2019s possible.",
        "pregnancy":     "Train smart. Stay strong. Come back stronger.",
        "perimenopause": "Perimenopause changes your body. Strength training changes it back.",
        "postmenopause": "Your strongest chapter starts now.",
    };
    const headline = headlineTpl[stageId] || "Your path is set.";

    const confirm = document.getElementById("pyj-confirm");
    if (confirm) {
        const h3     = document.getElementById("pyj-confirm-h3");
        const sub    = document.getElementById("pyj-confirm-sub");
        const btn    = document.getElementById("pyj-confirm-cta");
        const scroll = document.getElementById("pyj-scroll-hint");
        const photoUrl = story ? (PYJ_STORY_PHOTOS[story.name] || null) : null;
        const photoEl  = document.getElementById("pyj-confirm-photo");
        if (photoEl) {
            if (photoUrl) { photoEl.src = photoUrl; photoEl.alt = (story ? story.name : "") + " transformation"; photoEl.style.display = "block"; }
            else { photoEl.style.display = "none"; }
        }
        if (h3) h3.textContent = headline;
        if (sub && story) sub.innerHTML = "<strong>" + story.name + ":</strong> " + story.blurb;
        if (btn) { btn.href = ctaUrl; btn.textContent = "JOIN THE WAIT LIST"; }
        confirm.style.display = "block";
        gsap.fromTo(confirm, { opacity: 0, y: 16 }, { opacity: 1, y: 0, duration: 0.5, ease: "power3.out" });
        if (scroll) gsap.fromTo(scroll, { opacity: 0 }, { opacity: 1, duration: 0.6, delay: 0.6 });
        setTimeout(function() {
            const y = confirm.getBoundingClientRect().top + window.pageYOffset - 80;
            gsap.to("html, body", { scrollTop: y, duration: 0.5, ease: "power2.out" });
        }, 300);
    }
}
function rcUpdateWaitlistCTAs(goalId, decade) {
    const stageId = window.__pyjStageId || null;
    const stage   = stageId ? PYJ_LIFE_STAGES[stageId] : null;
    // Only use the PYJ stage if it still matches the active decade — guards against
    // the user manually changing decade in the Results Curve after a PYJ selection.
    const stageMatches = stage && stage.decade === decade;

    document.querySelectorAll(".waitlist-cta-btn").forEach(btn => {
        if (stageMatches) {
            btn.href        = pyjLandingUrl(stage, goalId);
            btn.textContent = "Join the " + stage.label + " waitlist \u2192";
        } else {
            btn.href        = "#pyj-section";
            btn.textContent = "Choose your stage to join the waitlist \u2191";
        }
    });
}

function initResultsChart() {
    const canvas = document.getElementById("resultsChart");
    if (!canvas) return;

    let activeGoal       = "recomp";
    let activeDecade     = "40s";
    let activeExperience = "some";
    let mealPlanActive   = false;

    // Restore saved profile
    try {
        const saved = JSON.parse(localStorage.getItem("evolved_profile_v2") || "{}");
        if (saved.goal   && RC_GOALS.find(g => g.id === saved.goal))  activeGoal       = saved.goal;
        if (saved.decade && RC_DECADES[saved.decade])                  activeDecade     = saved.decade;
        if (saved.exp    && RC_EXPERIENCE[saved.exp])                  activeExperience = saved.exp;
    } catch(e) {}

    const mealPlanRow    = document.getElementById("meal-plan-row");
    const mealPlanToggle = document.getElementById("meal-plan-toggle");

    const sliderIds = ["strength","hiit","pilates","hyrox"];
    const sliders = {};
    const valEls  = {};
    sliderIds.forEach(k => {
        sliders[k] = document.getElementById("rc-slider-" + k);
        valEls[k]  = document.getElementById("rc-val-"    + k);
    });

    function getSessions() {
        return sliderIds.map(k => sliders[k] ? parseInt(sliders[k].value) : 0);
    }

    const goalCfg0 = RC_GOALS.find(g => g.id === activeGoal);
    const dec0     = RC_DECADES[activeDecade];
    let   currentGoalCfg = goalCfg0;

    const chart = new Chart(canvas.getContext("2d"), {
        type: "line",
        data: {
            labels: RC_MONTHS.map(m => m === 0 ? "Start" : "M" + m),
            datasets: [
                {
                    label: "Your projected results",
                    data: rcCurve(goalCfg0, dec0, RC_EXPERIENCE["some"], getSessions(), false),
                    borderColor: "#e43388",
                    backgroundColor: "rgba(228,51,136,0.07)",
                    fill: true, tension: 0.4, borderWidth: 2.5,
                    pointRadius: 0, pointHoverRadius: 5,
                    pointHoverBackgroundColor: "#e43388",
                },
                {
                    label: "Without structured training",
                    data: rcBaseline(goalCfg0),
                    borderColor: "#444",
                    borderDash: [6,4],
                    backgroundColor: "transparent",
                    fill: false, tension: 0.4, borderWidth: 1.5,
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
                    mode: "index", intersect: false,
                    callbacks: {
                        label: ctx => " " + ctx.dataset.label + ": " + ctx.parsed.y + " " + currentGoalCfg.unit
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

    function refresh() {
        const goalCfg  = RC_GOALS.find(g => g.id === activeGoal);
        const dec      = RC_DECADES[activeDecade];
        const sessions = getSessions();
        const weights  = goalCfg.weights;
        const maxWeight = Math.max(...weights);
        const normalMax = 6 * maxWeight;
        let weeklyScore = 0;
        sessions.forEach((s, i) => { weeklyScore += s * weights[i]; });
        const score   = Math.min(weeklyScore, normalMax) / normalMax;
        const exp     = RC_EXPERIENCE[activeExperience] || RC_EXPERIENCE["some"];
        const newData = rcCurve(goalCfg, dec, exp, sessions, mealPlanActive);
        const month12 = newData[12];

        currentGoalCfg = goalCfg;
        chart.data.datasets[0].data = newData;
        chart.data.datasets[1].data = rcBaseline(goalCfg);
        chart.options.scales.y.title.text = goalCfg.yLabel;
        chart.update();

        // Show/hide meal plan toggle based on goal
        if (mealPlanRow) {
            const hasMealPlan = !!goalCfg.mealPlanFactor;
            mealPlanRow.style.display = hasMealPlan ? "block" : "none";
            if (!hasMealPlan && mealPlanActive) {
                mealPlanActive = false;
                if (mealPlanToggle) {
                    mealPlanToggle.style.background  = "#1a1a1a";
                    mealPlanToggle.style.borderColor = "#333";
                    mealPlanToggle.style.color       = "#aaa";
                    mealPlanToggle.textContent       = "+ I\u2019m following The Evolved Smart Meal Plan";
                }
            }
        }

        const annEl = document.getElementById("resultsAnnotation");
        if (annEl) {
            annEl.textContent = rcAnnotation(goalCfg, activeDecade, score, month12, mealPlanActive, activeExperience);
            gsap.fromTo(annEl, { opacity: 0, y: 6 }, { opacity: 1, y: 0, duration: 0.35, ease: "power2.out" });
        }

        rcHighlightMembership(activeExperience);
        rcUpdateFinalCTA(activeGoal, activeDecade);
        rcUpdateProfilePanel(activeGoal, activeDecade, score);
        rcReorderCarousel(activeGoal, activeDecade);
        rcReorderVideos(activeGoal, activeDecade);
        rcUpdateFAQ(activeGoal, activeDecade);
        rcUpdatePillars(activeGoal);
        rcUpdateProfileBar(activeGoal, activeDecade, activeExperience);
        rcUpdateCTALinks(activeGoal, activeDecade, activeExperience);
        rcUpdateWaitlistCTAs(activeGoal, activeDecade);
        try { localStorage.setItem("evolved_profile_v2", JSON.stringify({ goal: activeGoal, decade: activeDecade, exp: activeExperience })); } catch(e) {}
    }

    // Goal buttons
    document.querySelectorAll(".rc-goal-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            activeGoal = btn.dataset.goal;
            document.querySelectorAll(".rc-goal-btn").forEach(b => {
                const on = b.dataset.goal === activeGoal;
                b.style.background  = on ? "#e43388" : "#1a1a1a";
                b.style.borderColor = on ? "#e43388" : "#333";
                b.style.color       = on ? "#fff"    : "#aaa";
                b.style.fontWeight  = on ? "700"     : "400";
            });
            refresh();
        });
    });

    // Decade buttons
    const bracketOrder = ["20s","30s","40s","50s","60s"];
    document.querySelectorAll(".rc-decade-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            activeDecade = btn.dataset.decade;
            document.querySelectorAll(".rc-decade-btn").forEach(b => {
                const on = b.dataset.decade === activeDecade;
                b.style.background  = on ? "#e43388" : "#1a1a1a";
                b.style.borderColor = on ? "#e43388" : "#333";
                b.style.color       = on ? "#fff"    : "#aaa";
                b.style.fontWeight  = on ? "700"     : "400";
            });

            // Sync sarcopenia slider to match
            const slider = document.getElementById("ageSlider");
            if (slider) {
                const idx = bracketOrder.indexOf(activeDecade);
                if (idx !== -1) {
                    slider.value = idx;
                    const pct = (idx / 4) * 100;
                    slider.style.background = "linear-gradient(to right, #e43388 " + pct + "%, #333 " + pct + "%)";
                    if (typeof selectAgeBracket === "function" && window.__sarcoChart) {
                        selectAgeBracket(window.__sarcoChart, activeDecade);
                    }
                    updateMusclePoints(activeDecade);
                    updateDecadeCards(activeDecade);
                }
            }

            refresh();
        });
    });

    // Experience buttons
    document.querySelectorAll(".rc-exp-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            activeExperience = btn.dataset.exp;
            document.querySelectorAll(".rc-exp-btn").forEach(b => {
                const on = b.dataset.exp === activeExperience;
                b.style.background  = on ? "#e43388" : "#1a1a1a";
                b.style.borderColor = on ? "#e43388" : "#333";
                b.style.color       = on ? "#fff"    : "#aaa";
                b.style.fontWeight  = on ? "700"     : "400";
            });
            refresh();
        });
    });

    // Meal plan toggle
    if (mealPlanToggle) {
        mealPlanToggle.addEventListener("click", () => {
            mealPlanActive = !mealPlanActive;
            mealPlanToggle.style.background  = mealPlanActive ? "#e43388" : "#1a1a1a";
            mealPlanToggle.style.borderColor = mealPlanActive ? "#e43388" : "#333";
            mealPlanToggle.style.color       = mealPlanActive ? "#fff"    : "#aaa";
            mealPlanToggle.style.fontWeight  = mealPlanActive ? "700"     : "400";
            mealPlanToggle.textContent = mealPlanActive
                ? "\u2713 Following The Evolved Smart Meal Plan"
                : "+ I\u2019m following The Evolved Smart Meal Plan";
            refresh();
        });
    }

    // Training sliders
    sliderIds.forEach(key => {
        const slider = sliders[key];
        if (!slider) return;
        slider.addEventListener("input", () => {
            const val = parseInt(slider.value);
            const pct = (val / 7) * 100;
            slider.style.background =
                "linear-gradient(to right, #e43388 " + pct + "%, #333 " + pct + "%)";
            if (valEls[key]) valEls[key].textContent = val + " /wk";
            refresh();
        });
    });

    // Sync button visual states to (possibly restored) active values
    function syncBtnStates() {
        document.querySelectorAll(".rc-goal-btn").forEach(b => {
            const on = b.dataset.goal === activeGoal;
            b.style.background = on ? "#e43388" : "#1a1a1a"; b.style.borderColor = on ? "#e43388" : "#333";
            b.style.color = on ? "#fff" : "#aaa"; b.style.fontWeight = on ? "700" : "400";
        });
        document.querySelectorAll(".rc-decade-btn").forEach(b => {
            const on = b.dataset.decade === activeDecade;
            b.style.background = on ? "#e43388" : "#1a1a1a"; b.style.borderColor = on ? "#e43388" : "#333";
            b.style.color = on ? "#fff" : "#aaa"; b.style.fontWeight = on ? "700" : "400";
        });
        document.querySelectorAll(".rc-exp-btn").forEach(b => {
            const on = b.dataset.exp === activeExperience;
            b.style.background = on ? "#e43388" : "#1a1a1a"; b.style.borderColor = on ? "#e43388" : "#333";
            b.style.color = on ? "#fff" : "#aaa"; b.style.fontWeight = on ? "700" : "400";
        });
    }
    document.addEventListener("pyj:profileSet", function(e) {
        const { goal, decade, exp } = e.detail;
        if (goal   && RC_GOALS.find(g => g.id === goal))   activeGoal       = goal;
        if (decade && RC_DECADES[decade])                  activeDecade     = decade;
        if (exp    && RC_EXPERIENCE[exp])                  activeExperience = exp;
        syncBtnStates();
        refresh();
        const confirmEl = document.getElementById("pyj-confirm");
        if (confirmEl) setTimeout(() => confirmEl.scrollIntoView({ behavior: "smooth", block: "nearest" }), 300);
    });

    document.addEventListener("pyj:stageDecade", function(e) {
        const { decade } = e.detail;
        if (decade && RC_DECADES[decade]) {
            activeDecade = decade;
            syncBtnStates();
            refresh();
        }
    });

    syncBtnStates();
    refresh();
}


// ── INIT ──────────────────────────────────────────────────────────

document.addEventListener("DOMContentLoaded", () => {
    const sarcoChart = initSarcopeniaChart();
    window.__sarcoChart = sarcoChart;
    if (sarcoChart) {
        const brackets = ["20s","30s","40s","50s","60s"];
        const slider   = document.getElementById("ageSlider");

        selectAgeBracket(sarcoChart, "20s");
        updateMusclePoints("20s");
        updateDecadeCards("20s");

        if (slider) {
            function updateSlider() {
                const val     = parseInt(slider.value);
                const bracket = brackets[val];
                const pct     = (val / 4) * 100;
                slider.style.background =
                    "linear-gradient(to right, #e43388 " + pct + "%, #333 " + pct + "%)";
                selectAgeBracket(sarcoChart, bracket);
                updateMusclePoints(bracket);
                updateDecadeCards(bracket);

                // Sync the results curve decade selector
                const rcBtn = document.querySelector('.rc-decade-btn[data-decade="' + bracket + '"]');
                if (rcBtn) rcBtn.click();
            }
            slider.addEventListener("input", updateSlider);
        }
    }

    // Preselect decade in sarcopenia chart when PYJ stage is chosen
    document.addEventListener("pyj:stageDecade", function(e) {
        const { decade } = e.detail;
        if (!decade) return;
        const brackets = ["20s","30s","40s","50s","60s"];
        const idx = brackets.indexOf(decade);
        if (idx === -1) return;
        const slider = document.getElementById("ageSlider");
        if (sarcoChart) {
            selectAgeBracket(sarcoChart, decade);
            updateMusclePoints(decade);
            updateDecadeCards(decade);
        }
        if (slider) {
            slider.value = idx;
            const pct = (idx / 4) * 100;
            slider.style.background = "linear-gradient(to right, #e43388 " + pct + "%, #333 " + pct + "%)";
        }
    });

    initResultsChart();
});
