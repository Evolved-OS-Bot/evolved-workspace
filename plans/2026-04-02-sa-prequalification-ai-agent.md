# Plan: SA Pre-Qualification AI Agent
**Created:** 2026-04-02
**Status:** Scoped — Not Started
**Depends on:** `2026-04-02-strength-assessment-workflow-rebuild.md` (integration points already built in)

---

## Objective

Build a Claude-powered conversational SMS agent that replaces the manual admin pre-qualification conversation between the Goals SMS reply and the 24hr READY prompt. The agent runs the full 4-stage pre-qual script, captures structured data into GHL custom values, and generates a trainer brief before each session — with zero admin involvement.

This agent also supersedes the five disconnected, fixed one-email `Goal:` nurture workflows. Do not reconnect or expand those workflows. During implementation, review their email copy and story references for worthwhile material to add to the approved success-story library; after the AI path is live and tested, dependency-check and archive the legacy workflows through a separate approved cleanup.

---

## Problem Being Solved

The current manual pre-qual process is high quality but:
- Requires admin to be available and responsive during business hours
- Consistency depends on the individual running the conversation
- Trainer briefs are produced manually and inconsistently
- No structured data is captured — knowledge lives in chat history

The AI agent delivers the same quality conversation 24/7, captures everything structured, and auto-generates the trainer brief.

---

## How It Works

```
1. Contact replies to SMS Goals in GHL
2. GHL workflow fires webhook → POST to agent service
   Payload: contact_id, contact_name, contact_phone, goals_reply, appointment_datetime
3. Agent service calls Claude API
   - System prompt: pre-qual script + persona + data extraction rules
   - Message: contact's goals reply
4. Claude generates response → agent sends SMS via GHL Conversations API
5. Contact replies again → GHL inbound message webhook fires → agent receives
6. Conversation continues turn-by-turn until agent determines pre-qual complete
7. Claude extracts structured data → agent writes SA: custom values to GHL
8. Agent adds tag: pre-qual complete → GHL workflow resumes
9. Night before session → agent generates trainer brief → sends as internal GHL notification
```

---

## Architecture

### Service
- **Language:** Python
- **Framework:** Flask (lightweight webhook receiver)
- **Deployment:** Railway (same platform as Discord bot)
- **Process:** Single always-on web service

### State Management
- Conversation history stored per contact in SQLite (local, persistent across restarts)
- Key: GHL contact ID
- Stores: message history (role/content), pre-qual stage, extracted fields so far
- Cleanup: archive conversations older than 90 days

### Inbound SMS Routing
GHL fires a webhook on every inbound message from a contact. The agent needs to:
1. Receive the webhook
2. Check if this contact has an active pre-qual conversation in progress
3. If yes → continue the conversation
4. If no → ignore (message handled by GHL normally)

This means the agent only intercepts messages for contacts in an active pre-qual session.

### Conversation Termination
Claude is instructed to respond with a structured JSON block when all required fields are gathered:

```json
{
  "conversation_complete": true,
  "extracted": {
    "primary_goal": "...",
    "motivation": "...",
    "weight_loss_target": "...",
    "commitment_score": 8,
    "medical_conditions": "...",
    "medications": "...",
    "injuries": "...",
    "injury_current_status": "...",
    "movements_to_avoid": "...",
    "aggravating_movements": "...",
    "training_history": "structured",
    "pt_experience": true,
    "group_experience": false,
    "last_trained": "6 months ago",
    "support_preference": "1:1",
    "obstacles": "...",
    "readiness": "high"
  },
  "final_sms": "Great — we have everything we need. Your trainer will be fully prepared for your assessment. See you soon!"
}
```

The service parses this, writes values to GHL, sends the final SMS, and adds the `pre-qual complete` tag.

---

## Claude System Prompt (draft)

```
You are a pre-qualification assistant for The Evolved, an all-female personal training gym in Australia. You are conducting a friendly SMS pre-qualification conversation with a woman who has just booked a Strength Assessment.

Your goal is to run through the 4-stage pre-qualification script below, gathering all required information before their session. You are warm, professional, and direct — not robotic. You reference what they say back to them. You never interrogate — you guide.

PERSONA:
- You are from The Evolved team
- Warm, knowledgeable, confident
- Australian English — no emojis, clean text only
- Short SMS-appropriate messages (2-4 sentences max per message)

SHARED CONVERSATION STATE:
- Read the complete pre-qualification conversation before every reply
- Identify which stage requirements have already been answered naturally
- If a team member or the prospect has added a newer message, reassess the stage from that message
- Continue from the first incomplete requirement
- Never repeat an answered question or restart the sequence because the responder has changed
- Ask no more than one or two connected questions per message

STAGE 1 — ACKNOWLEDGE & ANCHOR
Read their goals reply. Acknowledge specifically what they said. Highlight what the Strength Assessment will reveal for their specific situation. If their reply is vague, ask one clarifying question before moving on.

STAGE 2 — CONTEXT GATHERING (work through in order, skip if already answered)
A. GOALS & MOTIVATION
- Which of your goals is most important to you right now?
- Are you wanting to lose more than 5kg or less than 5kg? (if weight loss mentioned)
- Is the strength goal coming from a specific feeling or situation?
- What has made this important enough for you to do something about it now? (skip only when the motivation is already clear)
- On a scale of 1-10, how committed are you to changing this right now? (ask after the goal and motivation are clear)

B. MEDICAL (only if medical condition disclosed)
- Are you on any medication for [condition] that affects your blood pressure, heart rate or physical activity?
- Are symptoms currently flared up or under control?

C. INJURY (only if injury disclosed)
- What originally happened, and roughly when did it occur?
- Is it currently painful, flared up, or limiting movement?
- Are there movements they have been told to avoid or that regularly aggravate it?
- When multiple injuries are disclosed, clarify each one across multiple messages rather than sending a long list of questions
- If an injury is recent, significant, or currently limiting, ask whether a health professional has provided exercise restrictions
- Never diagnose, interpret medical information, or promise that training will resolve an injury

D. EXERCISE HISTORY
- Are you currently training or have you strength trained before?
- Was that structured (with a coach/program) or self-guided?
- Any 1:1 PT or group training experience?
- When did you last train consistently?

E. SUPPORT PREFERENCE
- Do you think you need 1:1 support, a group environment, or a bit of both?

F. SOCIAL PROOF
- Once context gathering is mostly complete, send the best-matching approved success story for the prospect's goal and life stage

G. OBSTACLES & READINESS
- If you were offered a spot after your assessment, would you be in a position to get started — or is there anything coming up that might get in the way?

PRICING:
- Do not introduce pricing when the prospect has not asked about it and has not expressed price sensitivity
- If the prospect asks generally about price before context gathering is complete, acknowledge the question and continue from the next incomplete requirement
- If the prospect expresses genuine affordability concern, use the approved minimum-$99 qualification response and record the outcome
- When context gathering is complete and pricing has been requested, provide the approved category range or minimum
- Never present the full package-price ladder or itemise package names and prices during pre-qualification
- If the appropriate pricing information is unclear, pause and escalate to Peter

CONVERSATION REPAIR:
- If the prospect says she already provided information, acknowledge the mistake and apologise once
- Reference the information accurately to demonstrate that it has now been read
- Answer any current direct question that is appropriate at that point
- Continue from the next incomplete requirement without asking her to repeat herself

STAGE 3 — PRE-FRAME
Once data is gathered, send this (adapt naturally to the conversation):
"Just so you know what to expect — the Strength Assessment isn't a gym tour or a free trial. It's a structured evaluation where we measure your current strength, mobility and movement quality. We'll show you exactly where you're strong and where you need attention. If we believe we can help you, we'll map out your next step from there."

STAGE 4 — COMPLETE
When all required fields are gathered, respond with a JSON block (not visible to the contact) plus a final SMS message:
{ "conversation_complete": true, "extracted": { ... }, "final_sms": "..." }

Required fields before completing: primary_goal, motivation, commitment_score, training_history, support_preference, obstacles.
Optional (capture if disclosed): medical_conditions, medications, injuries, injury_current_status, movements_to_avoid, aggravating_movements, weight_loss_target.
```

---

## GHL Custom Values to Create

All in a new folder: **`2.2 SA Pre-Qual`**

| Field Name | Type | Notes |
|---|---|---|
| SA: Primary Goal | TEXT | Free text from conversation |
| SA: Motivation | TEXT | Why the goal matters now |
| SA: Weight Loss Target | RADIO | >5kg / <5kg / Not applicable |
| SA: Commitment Score | NUMERICAL | 1–10 |
| SA: Medical Conditions | TEXT | Free text |
| SA: Medications | TEXT | Free text |
| SA: Injuries | TEXT | Free text |
| SA: Injury Current Status | TEXT | Current pain, flare-up, or limitations |
| SA: Movements to Avoid | TEXT | Free text |
| SA: Aggravating Movements | TEXT | Movements that currently aggravate disclosed injuries |
| SA: Training History | RADIO | Structured / Self-guided / None |
| SA: PT Experience | RADIO | Yes / No |
| SA: Group Experience | RADIO | Yes / No |
| SA: Last Trained | TEXT | Free text |
| SA: Support Preference | RADIO | 1:1 / Group / Hybrid |
| SA: Obstacles | TEXT | Free text |
| SA: Readiness | RADIO | High / Medium / Low |
| SA: Pre-Qual Conversation | LARGE_TEXT | Full conversation transcript |

**Tags (must exist in GHL):**
- `pre-qual complete`
- `pre-qual skipped`

---

## Trainer Brief Format

Auto-generated by Claude from captured custom values, sent as GHL internal notification to assigned coach before session:

```
SA TRAINER BRIEF — [Contact Name] — [Appointment Date/Time]

GOAL: [SA: Primary Goal]
MOTIVATION: [SA: Motivation]
Weight loss target: [SA: Weight Loss Target]
Commitment: [SA: Commitment Score]/10

TRAINING HISTORY: [SA: Training History]
PT experience: [SA: PT Experience] | Group: [SA: Group Experience]
Last trained: [SA: Last Trained]

HEALTH:
Medical: [SA: Medical Conditions]
Medications: [SA: Medications]
Injuries: [SA: Injuries]
Current status: [SA: Injury Current Status]
Avoid: [SA: Movements to Avoid]
Aggravated by: [SA: Aggravating Movements]

SUPPORT PREFERENCE: [SA: Support Preference]
OBSTACLES: [SA: Obstacles]
READINESS: [SA: Readiness]
```

---

## GHL Webhook Setup

Two webhooks needed in GHL:

**Webhook 1 — Pre-Qual Start (fires from workflow)**
- Trigger: After SMS Goals reply received
- Action: Custom Webhook in GHL workflow
- Endpoint: `https://[agent-service]/prequalification/start`
- Payload: `{ contact_id, contact_name, contact_phone, goals_reply, appointment_datetime }`

**Webhook 2 — Inbound Message (fires on every inbound SMS)**
- Trigger: GHL Settings → Integrations → Webhooks → `InboundMessage`
- Endpoint: `https://[agent-service]/prequalification/inbound`
- Payload: GHL standard inbound message schema
- Agent checks: is this contact in an active pre-qual session? If no → ignore.

---

## Build Order

| Step | Task | Status |
|---|---|---|
| 1 | Create GHL custom field folder `2.2 SA Pre-Qual` and all SA: fields | ⬜ To Do |
| 2 | Create `pre-qual complete` and `pre-qual skipped` tags in GHL | ⬜ To Do |
| 3 | Set up Railway service — Flask app skeleton, health check endpoint | ⬜ To Do |
| 4 | Build SQLite conversation state store | ⬜ To Do |
| 5 | Build `/prequalification/start` endpoint — receives webhook, starts Claude conversation, sends first SMS | ⬜ To Do |
| 6 | Build `/prequalification/inbound` endpoint — receives reply, continues Claude conversation | ⬜ To Do |
| 7 | Build conversation completion handler — parse JSON, write GHL custom values, add tag | ⬜ To Do |
| 8 | Build trainer brief generator — reads custom values, generates brief, sends internal notification | ⬜ To Do |
| 9 | Add webhook 1 to GHL workflow (after Goals SMS reply) | ⬜ To Do |
| 10 | Add webhook 2 in GHL Settings (inbound message listener) | ⬜ To Do |
| 11 | Test end-to-end with a real contact (Peter as test subject) | ⬜ To Do |
| 12 | Monitor first 10 live conversations — tune system prompt as needed | ⬜ To Do |

---

## Dependencies

- GHL API Private Integration Token (PIT) — already in `scripts/.env`
- Claude API key — needed, get from Anthropic console
- Railway account — already used for Discord bot
- GHL `2. Strength Assessment` workflow with webhook step + `pre-qual complete` tag wait (see rebuild plan)

---

## Unsure Escalation — Architectural Requirement

When the agent encounters a situation not covered by the SOP, it must:

1. Pause — hold the prospect's conversation without replying
2. Notify Peter via Discord (dedicated escalation channel or DM) with context + suggested options
3. Wait for Peter's Discord reply
4. Draft a new Coaching Note from Peter's guidance
5. Confirm the draft rule with Peter via Discord before saving
6. Write the confirmed rule to `outputs/systems/sa-prequalification-sop.md` (Coaching Notes section)
7. Send the approved reply to the prospect via GHL

**Implementation requirements:**
- Agent needs a Discord webhook or bot integration to post escalation messages
- Agent needs write access to `sa-prequalification-sop.md` (local file or GitHub API)
- Peter's Discord reply triggers the agent to resume — requires a listener (local Discord bot `on_message` handler in `#prequal-escalations` channel, or similar)
- Holding message sent to prospect if delay exceeds ~5 minutes during business hours

**This makes the SOP self-improving:** every novel conversation that triggers an escalation adds a new rule. The system gets better with every edge case.

---

## Notes

- The inbound webhook fires on ALL inbound messages — the agent must only respond to contacts with an active pre-qual session. All others are ignored.
- SQLite is sufficient for current volume. If contacts > 1000/month sustained, consider Postgres.
- Claude model to use: `claude-sonnet-4-6` — best balance of quality and cost for conversational use.
- Token costs at current volume (estimated 30 conversations/month, ~20 messages each): minimal — <$5/month.
- The pre-qual SOP lives at `outputs/systems/sa-prequalification-sop.md` — this is the system prompt source. Updates to the SOP are reflected immediately without redeployment.
- Conversation transcripts stored in `SA: Pre-Qual Conversation` custom field for audit and coach review.
- **Website profile data (SA: Website Goal / Decade / Experience) is context, not a substitute for conversation.** Even if these fields are pre-populated from the homepage URL params, the bot must still ask about and clarify goals through the conversation. The website selection is low-friction and self-reported — the bot conversation is where intent is confirmed, nuanced, and made actionable. `SA: Primary Goal` (from conversation) is the authoritative field; `SA: Website Goal` is a useful signal for the coach to compare stated vs. explored intent.
