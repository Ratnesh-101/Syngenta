
from pydantic import BaseModel
from typing import Optional

class VisitCard(BaseModel):
    entity_id:              str
    name:                   str
    vps:                    float
    rank:                   int
    reasons:                list[str]
    confidence_label:       str         # "high" | "medium" | "low"
    anomalies:              list[dict]
    visit_sequence_position: int
    data_freshness:         str

class VisitBrief(BaseModel):
    entity_id:      str
    briefing:       str                 # LLM output
    nba_actions:    list[dict]
    explainer:      str                 # LLM natural language explanation

class ScoreBreakdown(BaseModel):
    entity_id:      str
    score_breakdown: list[dict]         # signal, raw, weight, contribution
    total_vps:      float
    overrides:      list[str]