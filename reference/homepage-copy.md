# Homepage Copy — The Evolved
**Version:** 1.0
**Created:** 2026-04-30
**Status:** Historical pre-V2 draft; superseded
**URL:** theevolvedgym.com.au (post-migration)

> This draft is preserved as implementation history. It is not the current
> homepage or CTA authority. Website V2 is built and live with a waitlist
> journey. Use `outputs/systems/website-v2-release-manifest.md`,
> `reference/conversion-funnel.md` and the mirrored post-165 source at
> `wordpress/website-v2/source/homepage-post/post-165.html`.

---

## Design Constraints

- No navigation menu — single-purpose conversion page
- Single CTA throughout: **"Book Your Strength Assessment"** → `go.theevolvedgym.com.au/strength-assessment`
- Australian English — no emojis, no exclamation marks except where noted
- Tone: warm, confident, expert — not salesy, not motivational poster
- Every line must earn its place — no filler

---

## Section 1 — Hero

**Layout:** Full-screen hero. Megan coaching photo (dark overlay). GSAP fade-in on load.

**Headline (H1):**
> Brisbane's Leading Women-Only Gym

*Note: Retain as-is — performing well in search.*

**Subheadline (H2):**
> Your Strength Assessment shows exactly where you're starting from — and what will make the biggest difference for you.

**CTA Button:**
> Book Your Strength Assessment

**Below button (small text):**
> No gym tour. No free trial. A real evaluation.

---

## Section 2 — The Science (Sarcopenia Infographic)

**Heading (H2):**
> After 30, you're losing muscle every year. Most women don't know how much.

**Infographic:** Interactive sarcopenia curve — see `reference/infographic-sarcopenia-data.md`

**Body copy (below infographic):**
> Muscle mass is the foundation of everything you're trying to achieve — your metabolism, your strength, your posture, your energy, and how well your body ages. The research is unambiguous: women lose 3–8% of muscle per decade from their 30s, and that rate accelerates after 50.
>
> The Strength Assessment measures exactly where you are on this curve — and builds a program designed to stop the decline and reverse it.

**CTA link:**
> Find out exactly where you stand → Book Your Strength Assessment

---

## Section 3 — Why Frequency Matters (Training Frequency Infographic)

**Heading (H2):**
> The difference between training once and three times a week isn't 3x the results — it's closer to 9x.

**Infographic:** Interactive training frequency curve — see `reference/infographic-frequency-data.md`

**Body copy (below infographic):**
> Progressive strength training with barbells and dumbbells is the cornerstone. Pilates, yoga, and cardio are complimentary — they support your training, but they cannot replace it.
>
> The minimum effective dose to see meaningful change is consistency at the right frequency. Your trainer maps this out for you after your Strength Assessment, based on your goals, your schedule, and where you're starting from.

**CTA link:**
> Your trainer will prescribe the right frequency → Book Your Strength Assessment

---

## Section 4 — What the Strength Assessment Is

**Heading (H2):**
> This is not a gym tour. Not a free trial.

**3-column layout:**

| Column 1 — What happens | Column 2 — What you discover | Column 3 — What comes next |
|---|---|---|
| A structured 60-minute evaluation with one of our trainers | Exactly where you are on the strength and muscle mass curve | A clear recommendation for the right program, frequency, and starting point |
| We measure your current strength, mobility, and movement quality | Where your body is strong and where it needs attention | If we believe we can help you, we map out your next step — no pressure |
| We review your goals, training history, and health context | How your current habits are working for or against your goals | You leave knowing what to do next — whether that's with us or not |

**Supporting copy:**
> The assessment is an hour of your time with a qualified strength trainer. We'll show you what we find — the full picture. If we think you're a good fit for our programs, we'll tell you what that looks like. If you're not ready, we'll tell you that too.

---

## Section 5 — Social Proof Teaser

**Heading (H2):**
> Real results from women in Brisbane

**Layout:** 3 featured result cards. Each card: member photo (optional), pull quote, name + age bracket + goal.

**Card 1 (placeholder — replace with real story):**
> "I came in after years of feeling weak and overwhelmed. 18 months later I'm deadlifting 80kg and I haven't felt this strong in my life."
> — Sarah, 54, Postmenopause

**Card 2 (placeholder):**
> "I didn't think I'd ever enjoy training. I do now. The structured approach made all the difference."
> — Emma, 38, Women in their 30s

**Card 3 (placeholder):**
> "My osteoporosis risk has decreased measurably. My doctor is impressed. I'm not surprised — this program is the real thing."
> — Diane, 61, Postmenopause

**Link below cards:**
> See more results → /results/

---

## Section 6 — Final CTA

**Layout:** Full-width dark section. Centred.

**Heading (H2):**
> Your Strength Assessment is the starting point.

**Body (1 sentence):**
> One hour. A complete picture of where you are. A clear path forward.

**CTA Button:**
> Book Your Strength Assessment

---

## SEO Notes

- H1: "Brisbane's Leading Women-Only Gym" — primary page keyword
- Page title: `Brisbane's Leading Women-Only Gym | The Evolved`
- Meta description: `The Evolved is Brisbane's leading women-only strength training gym. Book your Strength Assessment and discover exactly where you're starting from.`
- No internal nav links from homepage — by design
- Homepage is not part of the blog hierarchy — standalone conversion page

---

## Implementation Notes

- All CTAs link to `go.theevolvedgym.com.au/strength-assessment`
- Blocksy full-width page template (no sidebar, no header nav)
- Hero image: existing Megan coaching photo (confirm asset location in WordPress media library)
- Colours: `#0a0a0a` background, `#e43388` primary pink, `#f5f0eb` warm off-white body text
- Fonts: PT Serif Caption (headings), Lato (body) — retain existing
