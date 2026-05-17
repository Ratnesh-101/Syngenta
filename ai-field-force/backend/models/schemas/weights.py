# backend/models/schemas/weights.py
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime


class WeightsCurrent(BaseModel):
    weights: Dict[str, float]
    last_updated_at: Optional[datetime] = None
    last_trigger: Optional[str] = None


class WeightHistoryItem(BaseModel):
    id: int
    rep_id: Optional[str] = None
    trigger: str
    outcome_id: Optional[int] = None
    weights: Dict[str, float]
    delta: Optional[Dict[str, float]] = None
    created_at: datetime

    class Config:
        from_attributes = True