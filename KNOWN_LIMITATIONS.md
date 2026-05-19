# Known Limitations

A reviewer-facing summary of what Kheti Compass does *not* do in Stage 1, why, and what we commit to in Stage 2. This file complements Section 7 of `solution_document.pdf`.

We surface these proactively rather than letting a reviewer discover them. Each item carries a **Stage 2 status** tag for cross-referencing with the commitments table in §6.4 of the solution document.

---

## Data limitations

### Synthetic `complaint_open` signal

The 30% rate of `complaint_open=true` for growers who haven't attended a recent campaign is a placeholder for a real complaint stream. The hackathon dataset does not include a complaint log. **[Stage 2: requires Syngenta CRM integration]** — the schema already has `complaint_open` as a first-class boolean signal; the work is integration, not modeling.

### Proxy `competitor_activity` signal

Inferred from the absence of `product_scan` and `offline_campaign_attended` flags in the grower record. A true signal would come from rep-reported competitor sightings. **[Stage 2: committed]** — Section 6.4, ~4 hours of work to add to the outcome form.

### Static `pest_alert_severity` table

Crop-specific severity values are looked up from a static table rather than live ICAR or Krishi Vigyan Kendra bulletins. **[Stage 2: committed]** — RSS ingestion + NLP extraction, ~2–3 days of work.

### District-granularity weather

Open-Meteo integration is live, but we cache results per district rather than per grower. All 27 growers in Bikaner share the same `weather_risk_score=0.44`. **[Stage 2: committed]** — switch to per-grower polygon coordinates and refresh cadence.

---

## Authentication limitations

### OTP delivery is stubbed

The phone OTP flow is end-to-end functional, but no SMS or WhatsApp message is sent. The OTP is returned in the API response when `DEV_MODE=true` for the demo deployment; production must integrate a real provider. **[Stage 2: committed]** — email OTP via SendGrid (chosen over SMS/WhatsApp because of zero compliance friction in India). Demo phone `9999999999` is pre-seeded so the flow can be demonstrated end-to-end.

### No refresh tokens

JWTs are issued with a 7-day expiry and no rotation. A production deployment needs short-lived access tokens + long-lived refresh tokens with per-device session management. **[Stage 2: committed]** — the `Device` table is already in place; the work is server-side token issuance and client-side rotation logic.

### No email verification on registration

Email + password registration accepts the email as trusted. Google OAuth accounts arrive pre-verified by Google. **[Stage 2: committed]** — bundled with the SMTP infrastructure needed for email OTP.

### Identity merge testing is one-directional

A rep who signs up with email + password and later logs in with Google gets merged into one account. The reverse direction (Google first, then password) works in code but is not as thoroughly tested. **[Stage 2: committed]** — coverage tests, ~0.5 day.

---

## Validation gap

### The learner is not yet field-validated

Our seeded outcomes (8 total over 11 days, all from REP_0338) are sufficient to demonstrate the math works — a verified live recalibration produced real deltas (`complaint_open: −0.038`, `revenue_potential: +0.042`). They are **not** sufficient to claim the learned weights are *better* than the defaults. A real validation requires either:

- A controlled rollout (some reps with the system, some without) tracked over 3–6 months, or
- A simulated outcome stream calibrated against historical Syngenta data, replayed in fast-forward

**[Stage 2: not committed]** — this gap cannot be closed by engineering alone. It requires a real deployment.

---

## Testing gap

### No automated test harness in Stage 1

Standard pytest unit tests are doable in 1–2 days; we did not run them for this hackathon. **[Stage 2: committed]** — Section 6.4 includes a pytest harness across `core/scoring`, `core/anomalies`, `core/ml/weight_updater`, `services/auth_service`, plus CI integration. The first thing a careful engineering manager would add post-shortlist.

---

## Deliberately scoped out

These were considered and excluded with **no Stage 2 commitment** — they are reasonable additions only if user research warrants them after a Phase 1 pilot.

### Native iOS / Android app

A responsive PWA gives ~95% of the native experience (offline storage, full-screen, home-screen install) at ~5% of the engineering cost. We would only build a native app if specific needs emerge — push notification reliability, deep camera integration for crop photos, or biometric login.

### Real-time websockets

Considered for the manager dashboard, ruled out because the data refresh cycle is hours-to-days, not seconds. Pull-to-refresh suffices.

---

## What we are *not* hiding

If a reviewer reads `core/auth/otp/console_sender.py`, they will see that the OTP delivery is `print(code)` — exactly what this file states.

If a reviewer reads `db/seed_data.py`, they will see synthetic complaint generation — exactly what this file states.

If a reviewer runs `pytest`, they will find no tests — exactly what this file states.

Being upfront here means there is no surprise for the reviewer and no defensive answer needed during evaluation.

---

## Contact

Questions about any limitation: Ratnesh Singh — `24f2008613@ds.study.iitm.ac.in`