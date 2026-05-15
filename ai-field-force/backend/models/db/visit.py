from sqlalchemy import Column, String, DateTime, JSON
from db.session import Base
import uuid

class VisitPlan(Base):
    __tablename__ = "visit_plans"

    id                = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    rep_id            = Column(String)
    plan_date         = Column(String)
    ordered_entity_ids = Column(JSON)
    generated_at      = Column(DateTime)