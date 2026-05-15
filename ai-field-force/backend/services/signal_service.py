from sqlalchemy.orm import Session
from models.db.farmers import FarmerRetailer
from models.db.signal import Signal
from core.deterministic.anomaly_detector import run_anomaly_checks
import json


class SignalService:

    def __init__(self, db: Session):
        self.db = db

    def get_anomalies(self, rep_id: str) -> dict:
        # 1. Get all farmers for this rep
        farmers = self.db.query(FarmerRetailer).filter(
            FarmerRetailer.rep_id == rep_id
        ).all()

        results = []

        for farmer in farmers:
            # 2. Get latest signal for this farmer
            signal = self.db.query(Signal).filter(
                Signal.entity_id == farmer.id
            ).order_by(Signal.created_at.desc()).first()

            if not signal:
                continue

            payload = json.loads(signal.payload) if isinstance(signal.payload, str) else signal.payload

            # 3. Run anomaly checks
            anomalies = run_anomaly_checks(payload)

            if anomalies:
                results.append({
                    "entity_id": farmer.id,
                    "name":      farmer.name,
                    "region":    farmer.region,
                    "anomalies": anomalies
                })

        return {
            "rep_id":        rep_id,
            "total_flagged": len(results),
            "results":       results
        }