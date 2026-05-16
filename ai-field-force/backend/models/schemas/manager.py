# backend/models/schemas/manager.py
from pydantic import BaseModel
from typing import Optional, List, Literal
from datetime import datetime


# ---- overview ----

class TerritoryHealthScore(BaseModel):
    score: float                                   # 0-100
    label: Literal["healthy", "watch_list", "needs_attention"]
    components: dict                                # breakdown for explainability
    weights: dict                                   # what weights were used


class ManagerOverview(BaseModel):
    territory_health: TerritoryHealthScore
    total_reps: int
    total_growers_under_management: int
    total_outcomes_logged: int
    outcomes_last_30d: int
    average_outcome_rating: Optional[float] = None  # null if no outcomes
    high_priority_growers_count: int                # VPS >= HIGH_VPS_THRESHOLD
    open_anomalies_count: int
    last_activity_at: Optional[datetime] = None


# ---- per-rep ----

class RepMetrics(BaseModel):
    rep_id: str
    name: str
    territory_size: int
    outcomes_total: int
    outcomes_last_30d: int
    average_rating: Optional[float] = None
    high_priority_count: int
    anomalies_count: int
    last_activity_at: Optional[datetime] = None
    performance_label: Literal["active", "low_activity", "needs_attention"]


# ---- top priorities across territory ----

class TopPriorityGrower(BaseModel):
    entity_id: str
    name: str
    region: str
    rep_id: str           # which rep owns this grower
    vps: float
    rank_within_rep: int
    reasons: List[str] = []
    confidence_label: str