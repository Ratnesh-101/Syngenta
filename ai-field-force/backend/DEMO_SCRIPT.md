# Demo Script

Read this before going on stage. Two plans — pick based on whether the frontend is demo-ready.

---

## Pre-demo checklist (15 minutes before)

Run these in order. Don't skip.

```powershell
# 1. Fresh DB state with seeded data
cd backend
# Stop any running uvicorn (Ctrl+C in its terminal)
uvicorn main:app --reload
```

Look for ALL FOUR of these in startup:
```
✓ Database tables ready (auth + outcomes + devices + weight_history migrated)
✓ Demo rep ensured (rep@syngenta.com / 9999999999 / syngenta123)
✓ Demo manager ensured (manager@syngenta.com / manager123, manages [REP_0338])
✓ Demo outcomes seeded: created=8, skipped=0
```

If any is missing → STOP. Fix before demo.

**Then open these tabs:**
1. `http://localhost:8000/docs` — Swagger
2. Frontend URL if Plan A
3. README.md (in case judges ask "what is this?")
4. This file (for reference during demo)

**Have on hand:**
- Demo creds written on paper (don't fumble during stage):
  - Rep: `rep@syngenta.com` / `syngenta123`
  - Manager: `manager@syngenta.com` / `manager123`
- A grower ID to drill into: **`GRW_00774`** (rank #1, has a complaint open)
- Backup token-getter command in case Swagger Authorize fails

---

# PLAN A — Frontend works

Target time: 6 minutes. Tells one cohesive story.

## The narrative arc

**Setup (30s):** Meet Ravi. Field rep in Bikaner. 27 growers. Limited hours. The decision he makes every morning is: who do I visit first?

**Act 1 — Login & priorities (60s)**
- Open the app on phone-sized window (use Chrome DevTools mobile mode)
- "Three login options — password, WhatsApp OTP, Google. He's chosen WhatsApp because that's how he uses his phone."
- Log in via OTP using the console-mode flow (OTP printed in backend terminal — flip to that screen briefly to show "yes this is real")
- Land on today's priority list
- "Top 5 highlighted. Each has a VPS — Visit Priority Score. Each has reasons. Each has anomaly badges where applicable."

**Act 2 — Drill into a grower (90s)**
- Tap **GRW_00774**
- "Open complaint, last visit 70 days ago. The AI doesn't just rank — it briefs."
- Show LLM briefing
- "Recommended actions, ranked. The rep doesn't have to guess what to talk about."

**Act 3 — The offline moment (the strongest beat, 90s)**
- "Rural Bikaner has spotty connectivity. Watch this."
- Toggle airplane mode (or just disable network in Chrome DevTools)
- Log 2 outcomes — fill the form, submit, see "Queued — will sync when online"
- Header badge shows "2 pending"
- Turn airplane mode off
- App auto-syncs. Badge clears. Toast: "2 outcomes synced."
- "Behind the scenes: each outcome has a client UUID. The server is idempotent on (device_id, client_outcome_id) — replay the same batch twice, server reports them as duplicates. No double counting. Field-grade reliability."

**Act 4 — Manager view (75s)**
- Log out, log in as manager
- "Now Ravi's boss. He runs Bikaner with multiple reps in a real deployment."
- Dashboard shows:
  - Territory health score (point to it): **63.9, Watch List**
  - Components breakdown — coverage 29.6%, outcomes 4.0 avg, urgency intact
  - "These numbers are real. Each weight is tunable. We didn't pick the formula randomly — coverage and outcome quality dominate because together they tell 80% of the story."
- Click into the rep
- See recent outcomes, anomalies, priority list

**Act 5 — The ML proof (45s)**
- "Last thing — every project says 'we use AI.' We can prove it."
- Show `/weights/history` (in Swagger if no frontend page) — scroll through 8 snapshots
- "Each outcome captured the signal state at that grower at that moment. The Bayesian updater moved the priority weights. You can see the deltas — what the model learned from each outcome. Snapshot 6 was a no-interest outcome — most deltas went negative. Snapshot 1 was a sale where a complaint was open — complaint_open weight grew."

**Wrap (15s):** "Built for one rep. Scales to a manager. Audit trail end-to-end. Offline-resilient. Real ML. Demo creds on the README if you want to play with it."

## The lines to rehearse

These are the ones that land. Practice them out loud:

- *"This isn't a script with fake numbers — these signals were captured at the moment of each outcome."*
- *"The rep doesn't have to guess what to talk about."*
- *"Replay the same batch twice — the server tells you which ones it already had. Field-grade reliability."*
- *"Every weight is tunable. We didn't pick the formula randomly."*

## What to do if something breaks live

| Failure                            | Recovery line                                                  |
|------------------------------------|----------------------------------------------------------------|
| Frontend doesn't load              | "Frontend is rendering off this API — let me show you the API directly." → Switch to Plan B mid-stream |
| LLM briefing slow / errors         | "OpenAI's having a moment. The brief is cached behind the scenes; here's a stored one." → skip to next beat |
| OTP terminal not visible           | Skip airplane mode demo; pivot to "and the system handles this case too — let me show you in Swagger" |
| Authorize button fails             | Run the token-getter curl: `curl -X POST http://localhost:8000/auth/login/password -H "Content-Type: application/json" -d "{\"identifier\":\"rep@syngenta.com\",\"password\":\"syngenta123\"}"`, copy the token, paste into a header in DevTools |

---

# PLAN B — Swagger only (frontend not ready)

Target time: 5 minutes. The art here is **storytelling, not feature touring.** Don't read JSON. Tell what the data means.

## The narrative arc

**Setup (45s):**
- Open Swagger
- "Quick context: this is a field-ops system for Syngenta reps in rural Rajasthan. The hard part isn't building a CRUD app — it's deciding who to visit each day, capturing what happened, and learning from it. No frontend today; we'll walk through the API surface that powers it."

**Step 1 — Auth (45s)**
- "Three login methods, one account. Password, WhatsApp OTP, Google. They merge — sign in by phone, link Google later."
- Authorize button → log in as rep
- Hit `GET /auth/me`
- Point to `identities[]` array — "Same account, two ways in."

**Step 2 — The priority decision (60s)**
- Hit `GET /visits/today`
- "27 growers, ranked. Every one has a VPS, reasons, anomalies. No black box."
- Pick GRW_00774 — point to the reasons + anomalies arrays
- Hit `GET /visits/GRW_00774/brief`
- "Same data, run through an LLM — natural-language briefing the rep reads before knocking."

**Step 3 — Outcome + offline sync (90s) — the strongest beat**
- Hit `POST /outcomes/sync` with the demo body (see "demo payloads" below)
- "Three outcomes in a batch. Two real grower IDs, one fake."
- Point to response: 2 created, 1 failed. "The fake one is reported back specifically."
- Hit the SAME `POST /outcomes/sync` again with the same body
- "Watch what happens." → 0 created, 2 duplicates, 1 still fails
- "This is what offline sync requires. Field reps lose signal. The client retries. The server has to be idempotent. We are."

**Step 4 — Manager view (60s)**
- Authorize as manager
- Hit `GET /manager/overview`
- "One number: territory_health_score. **63.9, watch list.** Coverage 29.6%, outcomes averaging 4 out of 5, no high-priority growers unvisited."
- "Weights are tunable. The formula is in the README."
- Hit `GET /manager/priorities/top?limit=5` — "Top 5 priorities across the whole territory, with attribution to which rep owns each."

**Step 5 — The ML proof (60s)**
- Hit `GET /weights/history?limit=8`
- "Eight outcomes were seeded. Eight snapshots. Each captures the signal state at that moment, applies a Bayesian update, persists the delta."
- Scroll through snapshot 1 → snapshot 8
- "Snapshot 1 — a sale on a grower with an open complaint. Watch `complaint_open` go up by 0.02. The model learned: complaints predict sales."
- "Snapshot 6 — a no-interest outcome. Negative deltas across the board. The model walked away from those signals."
- "This is the learning trail. Auditable, deterministic, defensible."

**Wrap (15s):** "Backend's feature-complete. Frontend is in progress with a separate team. The API is documented, the demo creds are in the README, and the dataset is real Syngenta growers from Bikaner."

## Demo payloads to keep open

**Login (POST /auth/login/password):**
```json
{"identifier": "rep@syngenta.com", "password": "syngenta123"}
```

**Outcome sync batch (POST /outcomes/sync):**
```json
{
  "device_id": "demo-stage-phone",
  "device_name": "Stage demo phone",
  "device_platform": "android",
  "outcomes": [
    {
      "client_outcome_id": "stage-uuid-1",
      "entity_id": "GRW_00774",
      "outcome_rating": 5,
      "outcome_type": "sale",
      "actions_taken": ["product_demo"],
      "recorded_at": "2026-05-15T10:00:00Z"
    },
    {
      "client_outcome_id": "stage-uuid-2",
      "entity_id": "GRW_02680",
      "outcome_rating": 4,
      "outcome_type": "complaint_resolved",
      "actions_taken": ["follow_up"],
      "recorded_at": "2026-05-15T14:00:00Z"
    },
    {
      "client_outcome_id": "stage-uuid-3",
      "entity_id": "FAKE_GROWER",
      "outcome_rating": 4,
      "outcome_type": "sale",
      "actions_taken": [],
      "recorded_at": "2026-05-15T16:00:00Z"
    }
  ]
}
```

**Manager login (POST /auth/login/password):**
```json
{"identifier": "manager@syngenta.com", "password": "manager123"}
```

---

# Common questions judges ask

Be ready for these. Short, confident answers.

**Q: How does the priority score actually work?**
> 8 signals, each weighted. Signals are pest alerts, inventory shortage, days since last visit, weather risk, complaint status, crop stage sensitivity, revenue potential, competitor activity. The dot product gives VPS. Hard override rules can push it higher (open complaint = floor of 90).

**Q: Where does the data come from?**
> Real Syngenta dataset — 27 growers in Bikaner, real retailer inventory, real visit logs, real crop calendars. Weather is acknowledged as randomized — no weather CSV in the source.

**Q: Is the LLM in the loop for ranking?**
> No, and that's deliberate. LLM is only for natural-language briefings and explanations. The priority list is deterministic, weighted, and explainable. Letting an LLM rank would mean a different list every time — wrong for a field tool.

**Q: How does it learn?**
> Bayesian update after every recorded outcome. The grower's signal state at outcome time gets multiplied by a normalized rating (-1 to +1), scaled by a learning rate, and added to the weights. Renormalize to sum to 1. The trail is in `/weights/history`.

**Q: What about real WhatsApp delivery?**
> The OTP sender is pluggable. Console mode for demo. The Twilio adapter is one file — we'd ship it the day we want real SMS, after WABA verification.

**Q: How do you handle a stolen phone?**
> Device tracking. Every sync attempt is tied to a `device_id`. The rep can see all their linked devices via `/devices`. Admin can revoke any device — next sync attempt from that ID gets a 403.

**Q: How would this scale?**
> Postgres instead of SQLite, Redis for the OTP store, an actual job queue for batch recalibration. Architecture doesn't change — we kept services pure and core modules dependency-free for this reason.

**Q: Why isn't there real-time push?**
> Field reps have spotty connectivity. Push without offline-first is a worse experience. We built offline-first first. Push is a follow-on if connectivity holds.

---

# Don't say these things on stage

- "We were going to add X but ran out of time" — even if true, judges hear "incomplete project"
- "The frontend team didn't deliver" — never blame teammates publicly
- "It's just a hackathon" — undersells your own work
- Any technical detail you can't defend if asked a follow-up
- "AI ✨" or other marketing-speak

---

# After the demo

- Hand judges a card with the GitHub URL and README link
- "Demo creds are in the README — please log in and click around"
- Thank them by name if you can