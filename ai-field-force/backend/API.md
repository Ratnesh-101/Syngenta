# API Reference

Base URL (dev): `http://localhost:8000`
All protected routes: `Authorization: Bearer <access_token>` header.
Token expiry: 7 days. Get one from any of the login endpoints.

---

## Auth

### `POST /auth/register/password`
Create a new account with email + password. Also creates an (unverified) phone identity for the same account.

```json
// Request
{
  "name": "Ravi Kumar",
  "email": "ravi@example.com",
  "phone": "9876543210",
  "password": "secret123",
  "rep_id": "REP_0339"   // optional, links to Syngenta territory
}

// Response (201)
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "expires_in_minutes": 10080,
  "rep": { /* RepProfile, see GET /auth/me */ }
}
```

Errors: `409` email/phone already registered, `400` invalid phone.

### `POST /auth/login/password`
```json
{"identifier": "rep@syngenta.com", "password": "syngenta123"}
// OR
{"identifier": "9999999999", "password": "syngenta123"}
```
Returns same shape as register. `401` on bad creds.

### `POST /auth/otp/send`
```json
// Request
{"phone": "9999999999"}

// Response (200) — in DEV_MODE, dev_otp is included so frontend can auto-fill
{
  "phone": "9999999999",
  "expires_in_seconds": 300,
  "sent_via": "console",
  "dev_otp": "483921"      // null in production
}
```
Rate limited: 30s cooldown, 5/hour per phone. Returns `429` when limits hit.

### `POST /auth/otp/verify`
```json
// Request
{"phone": "9999999999", "code": "483921"}

// Response (200) — same TokenResponse shape
```
Auto-creates a new account on first successful verify with `name: "User <last 4 digits>"`. `400` on wrong/expired/used code.

### `POST /auth/google/verify`
Frontend gets an `id_token` from Google's JS SDK, posts it here.
```json
// Request
{"id_token": "eyJhbGc..."}

// Response (200) — TokenResponse
```
Auto-links to existing account if email matches. `401` invalid token, `400` unverified email.

### `GET /auth/me`
Returns the current authenticated user's profile.
```json
{
  "id": "uuid",
  "rep_id": "REP_0338",
  "name": "Demo Rep",
  "primary_email": "rep@syngenta.com",
  "role": "rep",                       // "rep" | "manager" | "admin"
  "managed_rep_ids": [],               // populated for managers
  "is_active": true,
  "created_at": "2026-05-15T...",
  "identities": [
    {"provider": "password",     "identifier": "rep@syngenta.com", "verified_at": "..."},
    {"provider": "whatsapp_otp", "identifier": "9999999999",       "verified_at": "..."}
  ]
}
```

### Account linking (auth required)

- `POST /auth/link/google` — body: `{"id_token": "..."}` → links Google to current account
- `POST /auth/link/phone/send` — body: `{"phone": "..."}` → sends OTP
- `POST /auth/link/phone/verify` — body: `{"phone": "...", "code": "..."}` → attaches phone

Returns `RepProfile` on success, `409` if the identity is already on another account.

---

## Visits

### `GET /visits/today` (auth required, role=rep)
Returns the rep's ranked daily priority list — 27 growers, sorted by VPS desc.

```json
[
  {
    "entity_id": "GRW_00774",
    "name": "Grower 00774",
    "region": "Bikaner, Rajasthan",
    "vps": 90,
    "reasons": ["Open complaint requires immediate visit", "Overdue visit — last contact over 30 days ago"],
    "confidence_label": "low",
    "anomalies": [
      {"type": "visit_gap_exceeded", "severity": "high", "message": "No visit in 3+ weeks during active crop season"}
    ],
    "rank": 1,
    "visit_sequence_position": 1
  }
]
```

403 if account has no `rep_id` linked.

### `GET /visits/{entity_id}/brief`
LLM-generated visit briefing for one grower.
```json
{
  "entity_id": "GRW_00774",
  "name": "Grower 00774",
  "briefing": "Long-form paragraph...",
  "nba_actions": [
    {"action": "discuss_complaint", "rationale": "...", "priority": "high"}
  ]
}
```

### `GET /visits/{entity_id}/explain?rank=1`
Explains why a grower is at the given rank.

### `GET /visits/today/export`
Offline-ready dump of today's list with `exported_at` timestamp.

---

## Outcomes

### `POST /outcomes/record` (auth required, role=rep)
Single-outcome submission for online use. Internally calls `/sync` with one item.
```json
// Request
{
  "entity_id": "GRW_00774",
  "outcome_rating": 5,
  "outcome_type": "sale",                     // free-form, conventions: sale | follow_up_needed | no_interest | complaint_resolved
  "actions_taken": ["product_demo"],
  "actions_accepted": ["product_demo"],
  "notes": "Closed deal on fungicide",
  // Optional sync hints — supply for idempotency:
  "client_outcome_id": "uuid-from-client",
  "device_id": "client-device-uuid",
  "recorded_at": "2026-05-15T10:00:00Z"
}

// Response (200)
{
  "status": "created",                        // or "duplicate"
  "outcome_id": 42,
  "entity_id": "GRW_00774",
  "outcome_rating": 5,
  "success": true,
  "recommendation_acceptance_rate": 1.0,
  "client_outcome_id": "uuid-from-client",
  "device_id": "client-device-uuid"
}
```

### `POST /outcomes/sync` (auth required, role=rep)
Bulk-sync offline outcomes. **The primary path** — frontend should use this even for single-item submissions when possible.
```json
// Request
{
  "device_id": "phone-uuid",                  // client-generated, stable across sessions
  "device_name": "Ravi's phone",              // optional but recommended
  "device_platform": "android",               // android | ios | web
  "outcomes": [
    {
      "client_outcome_id": "outcome-uuid-1",  // REQUIRED — generated on-device when recorded
      "entity_id": "GRW_00774",
      "outcome_rating": 5,
      "outcome_type": "sale",
      "actions_taken": ["demo"],
      "actions_accepted": ["demo"],           // optional
      "notes": "...",                         // optional
      "recorded_at": "2026-05-15T10:00:00Z"   // when it actually happened, not now
    }
  ]
}

// Response (200) — mixed-status, frontend should mark each separately
{
  "synced_at": "2026-05-15T19:00:00Z",
  "device_id": "phone-uuid",
  "total": 1,
  "created_count": 1,
  "duplicate_count": 0,
  "failed_count": 0,
  "results": [
    {
      "client_outcome_id": "outcome-uuid-1",
      "server_outcome_id": 42,
      "status": "created",                     // "created" | "duplicate" | "failed"
      "error": null                            // populated when status == "failed"
    }
  ]
}
```

**Idempotency:** `(device_id, client_outcome_id)` is unique. Replaying the same batch returns `status: "duplicate"` with the original `server_outcome_id`. Frontend uses this to safely retry without double-counting.

**Errors per item are returned in `results[]`** — the response itself stays 200 as long as the batch was well-formed. A 4xx is reserved for malformed requests or auth failures.

### `GET /outcomes/recent?limit=10`
Current rep's most recent outcomes, newest first.

---

## Signals

### `GET /signals/anomalies` (auth required, role=rep)
All growers in the rep's territory with one or more detected anomalies.
```json
{
  "rep_id": "REP_0338",
  "total_flagged": 27,
  "results": [
    {
      "entity_id": "GRW_00774",
      "name": "Grower 00774",
      "region": "Bikaner, Rajasthan",
      "anomalies": [{"type": "visit_gap_exceeded", "severity": "high", "message": "..."}]
    }
  ]
}
```

---

## Weights

### `GET /weights/current` (auth required, any role)
The current signal weights driving the priority list.
```json
{
  "weights": {
    "pest_alert_severity": 0.2122,
    "inventory_shortage_level": 0.1308,
    "days_since_last_visit": 0.1779,
    "weather_risk_score": 0.1374,
    "complaint_open": 0.0807,
    "crop_stage_sensitivity": 0.1313,
    "revenue_potential": 0.0564,
    "competitor_activity": 0.0733
  },
  "last_updated_at": "2026-05-15T17:36:32",
  "last_trigger": "outcome_logged"
}
```

### `GET /weights/history?limit=20`
The learning trail. Each entry = one snapshot, tied to an outcome that triggered it.
```json
[
  {
    "id": 8,
    "rep_id": "REP_0338",
    "trigger": "outcome_logged",                 // or "manual_recalibration"
    "outcome_id": 8,                              // null for recalibrations
    "weights": { /* full weights dict at this point */ },
    "delta": {                                    // per-key change vs previous snapshot, null if no change
      "competitor_activity": 0.0338,
      "pest_alert_severity": -0.014
    },
    "created_at": "2026-05-15T17:36:32"
  }
]
```

### `POST /weights/recalibrate` (auth required, role=manager OR admin)
Aggregates the last 7 days of outcomes into the weights and writes a `manual_recalibration` snapshot.
```json
{
  "status": "recalibrated",
  "outcomes_used": 8,
  "period_days": 7,
  "updated_weights": { /* ... */ },
  "snapshot_id": 9,
  "delta": { /* ... */ }
}
```
Returns `403` if the caller is a regular rep.

---

## Devices

### `GET /devices/` (auth required)
List devices linked to current account.
```json
[
  {
    "id": "phone-ravi-abc-123",
    "name": "Ravi's phone",
    "platform": "android",
    "is_revoked": false,
    "first_seen_at": "2026-05-10T08:00:00",
    "last_seen_at": "2026-05-15T18:00:00",
    "last_sync_at": "2026-05-15T17:00:00",
    "sync_count": "14"
  }
]
```

### `DELETE /devices/{device_id}` (auth required)
Revokes a device. Subsequent sync attempts from that ID get 403.

---

## Manager

All require `role=manager` or `role=admin`. Returns `403` for reps.

### `GET /manager/overview`
Top-level dashboard.
```json
{
  "territory_health": {
    "score": 63.9,                              // 0-100
    "label": "watch_list",                       // "healthy" | "watch_list" | "needs_attention"
    "components": {
      "coverage_score": 29.6,
      "outcome_score": 80,
      "urgency_score": 100,
      "coverage_pct": 29.6,
      "avg_rating": 4,
      "high_priority_unvisited": 0,
      "total_high_priority": 5
    },
    "weights": {"coverage": 0.4, "outcomes": 0.4, "urgency": 0.2}
  },
  "total_reps": 1,
  "total_growers_under_management": 27,
  "total_outcomes_logged": 8,
  "outcomes_last_30d": 8,
  "average_outcome_rating": 4,
  "high_priority_growers_count": 5,
  "open_anomalies_count": 27,
  "last_activity_at": "2026-05-15T17:28:31"
}
```

### `GET /manager/reps`
Per-rep performance.
```json
[
  {
    "rep_id": "REP_0338",
    "name": "Demo Rep",
    "territory_size": 27,
    "outcomes_total": 8,
    "outcomes_last_30d": 8,
    "average_rating": 4,
    "high_priority_count": 5,
    "anomalies_count": 27,
    "last_activity_at": "2026-05-15T17:28:31",
    "performance_label": "active"               // "active" | "low_activity" | "needs_attention"
  }
]
```

### `GET /manager/reps/{rep_id}/details`
Drill into one rep. Returns priority list + recent outcomes + anomalies. Returns `403` if the manager isn't assigned to that rep.

### `GET /manager/priorities/top?limit=10`
Top N highest-VPS growers across all managed reps, with `rep_id` attribution.

---

## Error format

Standard FastAPI shape:
```json
{"detail": "Account not linked to a Syngenta rep ID. Contact your administrator."}
```

For validation errors (422):
```json
{
  "detail": [
    {"loc": ["body", "email"], "msg": "field required", "type": "value_error.missing"}
  ]
}
```

## Status codes you'll see

| Code | Meaning                                        | When                                                      |
|------|------------------------------------------------|-----------------------------------------------------------|
| 200  | Success                                        | Most GET / POST responses                                 |
| 201  | Created                                        | `/auth/register/password`                                 |
| 400  | Bad request                                    | Invalid OTP, expired OTP, invalid phone format            |
| 401  | Unauthorized                                   | Missing/invalid/expired JWT                               |
| 403  | Forbidden                                      | Wrong role, account not linked, revoked device            |
| 404  | Not found                                      | Device not found                                          |
| 409  | Conflict                                       | Email/phone/Google sub already linked to another account  |
| 422  | Validation error                               | Pydantic body validation failed                           |
| 429  | Too many requests                              | OTP cooldown / hourly limit                               |

---

## Quick-start for frontend integrators

```typescript
// 1. Login
const { access_token } = await fetch('http://localhost:8000/auth/login/password', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({identifier: 'rep@syngenta.com', password: 'syngenta123'})
}).then(r => r.json());

localStorage.setItem('token', access_token);

// 2. Every protected request
const res = await fetch('http://localhost:8000/visits/today', {
  headers: {'Authorization': `Bearer ${localStorage.getItem('token')}`}
});

// 3. Sync queue (the offline-first pattern)
const queue = JSON.parse(localStorage.getItem('outcome_queue') || '[]');
if (queue.length > 0) {
  const result = await fetch('http://localhost:8000/outcomes/sync', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    },
    body: JSON.stringify({
      device_id: localStorage.getItem('device_id') || crypto.randomUUID(),
      device_platform: 'web',
      outcomes: queue
    })
  }).then(r => r.json());

  // Remove successfully-created and duplicate items from the local queue
  const synced = new Set(
    result.results
      .filter(r => r.status === 'created' || r.status === 'duplicate')
      .map(r => r.client_outcome_id)
  );
  const remaining = queue.filter(o => !synced.has(o.client_outcome_id));
  localStorage.setItem('outcome_queue', JSON.stringify(remaining));
}
```