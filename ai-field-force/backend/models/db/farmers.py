from sqlalchemy import Column, String, Float, DateTime, Enum
from db.session import Base

class FarmerRetailer(Base):
    __tablename__ = "farmers_retailers"

    id              = Column(String, primary_key=True)
    name            = Column(String)
    type            = Column(Enum("farmer", "retailer", "distributor"))
    lat             = Column(Float)
    lng             = Column(Float)
    region          = Column(String)
    rep_id          = Column(String)
    last_visited_at = Column(DateTime, nullable=True)