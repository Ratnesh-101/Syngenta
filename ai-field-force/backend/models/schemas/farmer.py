from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class FarmerOut(BaseModel):
    id:              str
    name:            str
    type:            str
    lat:             float
    lng:             float
    region:          str
    rep_id:          str
    last_visited_at: Optional[datetime]

    class Config:
        from_attributes = True