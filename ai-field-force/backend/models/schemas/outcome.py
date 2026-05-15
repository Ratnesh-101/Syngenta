from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class VisitOutcome(BaseModel):
    entity_id:        str
    rep_id:           str
    visited_at:       datetime
    vps_at_visit:     float
    actions_taken:    list[str]
    outcome_rating:   int
    outcome_type:     str
    notes:            str
    signals_at_visit: dict


class OutcomeRecord(BaseModel):
    entity_id:        str
    rep_id:           str
    outcome_rating:   int
    outcome_type:     str
    actions_taken:    list[str]
    actions_accepted: list[str] = []   # which NBA recommendations rep actually followed
    notes:            Optional[str] = None