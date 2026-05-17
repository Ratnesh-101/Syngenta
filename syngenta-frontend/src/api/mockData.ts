import type {
  AuthResponse,
  PriorityGrower,
  GrowerBrief,
  Anomaly,
  Device,
  ManagerOverview,
  RepMetrics,
  RepDetails,
  TopPriority,
} from '../types'

// ─── Auth ─────────────────────────────────────────────────────────────────────

export const MOCK_REP_AUTH: AuthResponse = {
  access_token: 'mock-rep-token-abc123',
  token_type: 'bearer',
  rep: { id: 'rep-1', name: 'Ramesh Kumar', email: 'rep@syngenta.com', phone: '9999999999', role: 'rep' },
}

export const MOCK_MANAGER_AUTH: AuthResponse = {
  access_token: 'mock-manager-token-xyz789',
  token_type: 'bearer',
  rep: { id: 'mgr-1', name: 'Priya Sharma', email: 'manager@syngenta.com', role: 'manager' },
}

// ─── Today's Priorities ───────────────────────────────────────────────────────

export const MOCK_PRIORITIES: PriorityGrower[] = [
  {
    entity_id: 'g-001',
    name: 'Suresh Patel',
    region: 'Nokha, Bikaner',
    vps_score: 92,
    rank: 1,
    reasons: ['High purchase history', 'Crop stress detected', 'Last visit 45 days ago'],
    anomaly_count: 2,
  },
  {
    entity_id: 'g-002',
    name: 'Mohan Lal Bishnoi',
    region: 'Deshnok, Bikaner',
    vps_score: 85,
    rank: 2,
    reasons: ['Competitor activity nearby', 'Renewal due'],
    anomaly_count: 1,
  },
  {
    entity_id: 'g-003',
    name: 'Ratan Singh Rathore',
    region: 'Kolayat, Bikaner',
    vps_score: 74,
    rank: 3,
    reasons: ['New product launch opportunity', 'Large landholding'],
    anomaly_count: 0,
  },
  {
    entity_id: 'g-004',
    name: 'Bhura Ram Jat',
    region: 'Lunkaransar, Bikaner',
    vps_score: 68,
    rank: 4,
    reasons: ['Payment pending', 'Low product usage'],
    anomaly_count: 1,
  },
  {
    entity_id: 'g-005',
    name: 'Girdhari Lal Swami',
    region: 'Poogal, Bikaner',
    vps_score: 61,
    rank: 5,
    reasons: ['Seasonal follow-up', 'Interested in wheat seeds'],
    anomaly_count: 0,
  },
  {
    entity_id: 'g-006',
    name: 'Nathu Ram Meghwal',
    region: 'Bajju, Bikaner',
    vps_score: 55,
    rank: 6,
    reasons: ['Demo requested last visit'],
    anomaly_count: 0,
  },
  {
    entity_id: 'g-007',
    name: 'Hari Shankar Purohit',
    region: 'Bikaner City',
    vps_score: 48,
    rank: 7,
    reasons: ['Regular customer', 'New season starting'],
    anomaly_count: 0,
  },
]

// ─── Grower Briefs ────────────────────────────────────────────────────────────

export const MOCK_BRIEFS: Record<string, GrowerBrief> = {
  'g-001': {
    entity_id: 'g-001',
    name: 'Suresh Patel',
    region: 'Nokha, Bikaner',
    phone: '9876543210',
    village: 'Nokha',
    crop: 'Cotton, Mustard',
    briefing:
      'Suresh is a high-value grower with 42 acres under cultivation. He purchased Syngenta herbicides worth ₹38,000 last season and has historically responded well to in-person demos. Satellite imagery from last week indicates early signs of aphid infestation in his cotton plots, which he may not yet be aware of. This is an urgent visit — addressing the pest issue and recommending KARATE or CHESS could prevent significant crop loss and build strong loyalty going into the rabi season.',
    nba_actions: [
      'Show aphid infestation data from satellite imagery — demonstrate the AI advantage',
      'Recommend KARATE Zeon 50 CS for immediate pest control',
      'Introduce CHESS 50 WG as a resistance management option',
      'Discuss advance booking discount for rabi mustard seed (deadline: 20 days)',
      'Collect soil sample for SYNGENTA Soil Health assessment',
    ],
  },
  'g-002': {
    entity_id: 'g-002',
    name: 'Mohan Lal Bishnoi',
    region: 'Deshnok, Bikaner',
    phone: '9812345678',
    village: 'Deshnok',
    crop: 'Mustard, Gram',
    briefing:
      'Mohan Lal is a loyal customer but a new agri-input retailer opened 2 km from his village last month, offering discounts on competitor products. He is due for his annual mustard seed renewal and has expressed interest in premium varieties. This visit is strategically important to retain his ₹55,000 annual spend. Lead with the performance data from his last two seasons to reinforce the value of Syngenta products over cheaper alternatives.',
    nba_actions: [
      'Share season performance comparison — Syngenta vs competitor yield data',
      'Offer renewal discount on SYNGENTA 45S46 mustard seed (10% loyalty pricing)',
      'Discuss AMISTAR fungicide bundling for better disease management',
      'Invite to Syngenta field demonstration event on 25th',
    ],
  },
  'g-003': {
    entity_id: 'g-003',
    name: 'Ratan Singh Rathore',
    region: 'Kolayat, Bikaner',
    phone: '9823456789',
    village: 'Kolayat',
    crop: 'Wheat, Cotton',
    briefing:
      'Ratan Singh is a progressive farmer with 78 acres and good credit history. He has not yet adopted Syngenta\'s premium seed portfolio, currently using a local variety. His wheat yield last season was 15% below district average — a clear opening for a conversation about high-yielding varieties. He has good word-of-mouth influence in Kolayat village and converting him could drive 3-4 referrals.',
    nba_actions: [
      'Present yield comparison data for HD-3086 vs local variety on similar soil',
      'Offer trial pack of GW-496 for one acre at no cost',
      'Explain CLARIVA seed treatment for nematode control',
      'Discuss crop insurance partnership available with Syngenta certified seeds',
    ],
  },
  'g-004': {
    entity_id: 'g-004',
    name: 'Bhura Ram Jat',
    region: 'Lunkaransar, Bikaner',
    phone: '9834567890',
    village: 'Lunkaransar',
    crop: 'Mustard',
    briefing:
      'Bhura Ram has an outstanding payment of ₹12,500 from the kharif season. Approach this visit diplomatically — his crop faced unexpected hailstorm damage in October and he\'s under financial stress. Offer a structured repayment plan rather than demanding full payment. His mustard sowing is due in 3 weeks and he still needs inputs — this is an opportunity to maintain the relationship while recovering dues.',
    nba_actions: [
      'Discuss flexible repayment: ₹6,000 now, ₹6,500 post-harvest',
      'Offer SYNGENTA credit line for this season\'s mustard inputs',
      'Share crop insurance claim form — he may qualify for last season\'s loss',
      'Book mustard seed order conditional on payment plan agreement',
    ],
  },
  'g-005': {
    entity_id: 'g-005',
    name: 'Girdhari Lal Swami',
    region: 'Poogal, Bikaner',
    phone: '9845678901',
    village: 'Poogal',
    crop: 'Wheat',
    briefing:
      'Girdhari Lal expressed interest in wheat seed varieties during your last visit in September. He is a careful buyer who researches before purchasing — bring printed performance data sheets. He farms 25 acres and is considering switching from his current supplier. A face-to-face demo with seed samples could close this conversion.',
    nba_actions: [
      'Bring physical seed samples of GW-322 and HD-2781',
      'Share printed yield trial data for Bikaner district',
      'Offer free soil testing as value-add',
      'Introduce to Syngenta\'s WhatsApp advisory service',
    ],
  },
  'g-006': {
    entity_id: 'g-006',
    name: 'Nathu Ram Meghwal',
    region: 'Bajju, Bikaner',
    phone: '9856789012',
    village: 'Bajju',
    crop: 'Bajra, Mustard',
    briefing:
      'Nathu Ram requested a product demonstration during your last visit but no follow-up occurred. He grows 18 acres of bajra and is open to new herbicide options for weed control. Conduct a quick field walkthrough and demonstrate DUAL GOLD if weed pressure is visible.',
    nba_actions: [
      'Conduct field demo of DUAL GOLD herbicide application',
      'Collect feedback on previous season bajra performance',
      'Log visit outcome and schedule follow-up in 2 weeks',
    ],
  },
  'g-007': {
    entity_id: 'g-007',
    name: 'Hari Shankar Purohit',
    region: 'Bikaner City',
    phone: '9867890123',
    village: 'Bikaner',
    crop: 'Vegetables, Wheat',
    briefing:
      'Hari Shankar is a consistent buyer with 12 acres near Bikaner city. Regular relationship visit — no urgent action items. Good time to introduce the new vegetable seed catalogue for the upcoming season and check on last season satisfaction.',
    nba_actions: [
      'Share new vegetable seed catalogue — tomato and onion varieties',
      'Check satisfaction with last season purchase',
      'Introduce Syngenta loyalty rewards program',
    ],
  },
}

// ─── Anomalies ────────────────────────────────────────────────────────────────

export const MOCK_ANOMALIES: Anomaly[] = [
  {
    entity_id: 'g-001',
    name: 'Suresh Patel',
    anomaly_type: 'Pest Infestation Risk',
    description: 'Satellite NDVI data shows 23% chlorophyll drop in cotton plots over 10 days. Pattern consistent with aphid infestation. Immediate scouting recommended.',
    severity: 'high',
    detected_at: new Date(Date.now() - 2 * 3_600_000).toISOString(),
    region: 'Nokha, Bikaner',
  },
  {
    entity_id: 'g-001',
    name: 'Suresh Patel',
    anomaly_type: 'Visit Gap Alert',
    description: 'Last recorded visit was 47 days ago. Grower VPS score has increased 18 points since then with no rep interaction logged.',
    severity: 'medium',
    detected_at: new Date(Date.now() - 24 * 3_600_000).toISOString(),
    region: 'Nokha, Bikaner',
  },
  {
    entity_id: 'g-002',
    name: 'Mohan Lal Bishnoi',
    anomaly_type: 'Competitor Activity',
    description: 'New retailer "Kisaan Agro Centre" opened 1.8 km from grower location. Competitive pricing on mustard seeds reported by 3 nearby growers.',
    severity: 'high',
    detected_at: new Date(Date.now() - 3 * 24 * 3_600_000).toISOString(),
    region: 'Deshnok, Bikaner',
  },
  {
    entity_id: 'g-004',
    name: 'Bhura Ram Jat',
    anomaly_type: 'Payment Overdue',
    description: 'Invoice #SYN-2024-0892 for ₹12,500 is 78 days overdue. Grower has not responded to 2 SMS reminders.',
    severity: 'medium',
    detected_at: new Date(Date.now() - 5 * 24 * 3_600_000).toISOString(),
    region: 'Lunkaransar, Bikaner',
  },
]

// ─── Devices ──────────────────────────────────────────────────────────────────

export const MOCK_DEVICES: Device[] = [
  {
    device_id: localStorage.getItem('field_force_device_id') || 'current-device',
    device_name: 'Chrome on Mac',
    device_platform: 'web',
    last_seen: new Date().toISOString(),
    is_current: true,
  },
  {
    device_id: 'device-old-android',
    device_name: 'Android Phone',
    device_platform: 'android',
    last_seen: new Date(Date.now() - 3 * 24 * 3_600_000).toISOString(),
    is_current: false,
  },
]

// ─── Manager ──────────────────────────────────────────────────────────────────

export const MOCK_OVERVIEW: ManagerOverview = {
  territory_health_score: 72,
  total_reps: 6,
  total_growers: 148,
  outcomes_last_30d: 94,
  avg_rating: 3.8,
  high_priority_count: 12,
}

export const MOCK_REPS: RepMetrics[] = [
  { rep_id: 'rep-1', name: 'Ramesh Kumar',   email: 'ramesh@syngenta.com',  total_growers: 32, outcomes_last_30d: 24, avg_rating: 4.2, performance_label: 'excellent' },
  { rep_id: 'rep-2', name: 'Anita Verma',    email: 'anita@syngenta.com',   total_growers: 28, outcomes_last_30d: 18, avg_rating: 3.9, performance_label: 'good' },
  { rep_id: 'rep-3', name: 'Deepak Sharma',  email: 'deepak@syngenta.com',  total_growers: 25, outcomes_last_30d: 11, avg_rating: 3.1, performance_label: 'needs_attention' },
  { rep_id: 'rep-4', name: 'Kavita Joshi',   email: 'kavita@syngenta.com',  total_growers: 30, outcomes_last_30d: 22, avg_rating: 4.0, performance_label: 'excellent' },
  { rep_id: 'rep-5', name: 'Sunil Meena',    email: 'sunil@syngenta.com',   total_growers: 18, outcomes_last_30d: 10, avg_rating: 3.5, performance_label: 'good' },
  { rep_id: 'rep-6', name: 'Pooja Choudhary',email: 'pooja@syngenta.com',   total_growers: 15, outcomes_last_30d: 9,  avg_rating: 3.3, performance_label: 'good' },
]

export const MOCK_TOP_PRIORITIES: TopPriority[] = [
  { entity_id: 'g-001', name: 'Suresh Patel',        region: 'Nokha',        vps_score: 92, rank: 1, assigned_rep: 'Ramesh Kumar',    anomaly_count: 2 },
  { entity_id: 'g-002', name: 'Mohan Lal Bishnoi',   region: 'Deshnok',      vps_score: 85, rank: 2, assigned_rep: 'Ramesh Kumar',    anomaly_count: 1 },
  { entity_id: 'g-010', name: 'Vijay Singh Bhati',   region: 'Bikaner City', vps_score: 81, rank: 3, assigned_rep: 'Anita Verma',     anomaly_count: 0 },
  { entity_id: 'g-011', name: 'Dhanpat Ram Godara',  region: 'Khajuwala',    vps_score: 79, rank: 4, assigned_rep: 'Kavita Joshi',    anomaly_count: 1 },
  { entity_id: 'g-012', name: 'Tejaram Choudhary',   region: 'Phalodi',      vps_score: 76, rank: 5, assigned_rep: 'Deepak Sharma',   anomaly_count: 2 },
]

export const MOCK_REP_DETAILS: Record<string, RepDetails> = {
  'rep-1': {
    rep: MOCK_REPS[0],
    priorities: MOCK_PRIORITIES.slice(0, 4),
    recent_outcomes: [
      { id: 'o-1', entity_name: 'Suresh Patel',       outcome_type: 'sale',             rating: 5, visited_at: new Date(Date.now() - 1 * 86_400_000).toISOString(), notes: 'Sold KARATE 500ml + CHESS 250g. Happy with demo.' },
      { id: 'o-2', entity_name: 'Ratan Singh Rathore', outcome_type: 'follow_up_needed', rating: 3, visited_at: new Date(Date.now() - 2 * 86_400_000).toISOString(), notes: 'Interested but wants to compare prices first.' },
      { id: 'o-3', entity_name: 'Bhura Ram Jat',      outcome_type: 'complaint',        rating: 2, visited_at: new Date(Date.now() - 4 * 86_400_000).toISOString(), notes: 'Unhappy with germination rate of last batch.' },
    ],
    anomalies: MOCK_ANOMALIES.slice(0, 2),
  },
}
// Fallback detail for any rep
for (const rep of MOCK_REPS) {
  if (!MOCK_REP_DETAILS[rep.rep_id]) {
    MOCK_REP_DETAILS[rep.rep_id] = {
      rep,
      priorities: MOCK_PRIORITIES.slice(0, 2),
      recent_outcomes: [
        { id: `o-${rep.rep_id}-1`, entity_name: 'Vijay Singh Bhati', outcome_type: 'sale', rating: 4, visited_at: new Date(Date.now() - 2 * 86_400_000).toISOString(), notes: 'Good visit, closed mustard seed order.' },
      ],
      anomalies: [],
    }
  }
}
