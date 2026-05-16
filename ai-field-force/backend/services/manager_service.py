# backend/services/manager_service.py
from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy.orm import Session
from fastapi import HTTPException

from models.db.rep import Rep
from models.db.farmers import FarmerRetailer
from models.db.outcome import Outcome
from models.db.signal import Signal
from models.schemas.manager import (
    ManagerOverview,
    TerritoryHealthScore,
    RepMetrics,
    TopPriorityGrower,
)
from services.visit_service import VisitService
from services.signal_service import SignalService
from core.deterministic.anomaly_detector import run_anomaly_checks
from config import (
    HEALTH_WEIGHT_COVERAGE,
    HEALTH_WEIGHT_OUTCOMES,
    HEALTH_WEIGHT_URGENCY,
    HEALTH_COVERAGE_WINDOW_DAYS,
    HIGH_VPS_THRESHOLD,
    HEALTH_LABEL_GOOD,
    HEALTH_LABEL_WATCH,
)


class ManagerService:
    """Aggregates data across the rep_ids that a manager is allowed to see.

    Authorization happens at the route layer (require_role). This service
    receives `allowed_rep_ids` (already-scoped) and trusts it.
    """
    def __init__(self, db: Session):
        self.db = db
        self.visit_service = VisitService()

    # ---------- helpers ----------

    def _allowed_growers_query(self, allowed_rep_ids: List[str]):
        return self.db.query(FarmerRetailer).filter(
            FarmerRetailer.rep_id.in_(allowed_rep_ids)
        )

    def _allowed_outcomes_query(self, allowed_rep_ids: List[str]):
        return self.db.query(Outcome).filter(
            Outcome.rep_id.in_(allowed_rep_ids)
        )

    # ---------- overview ----------

    def overview(self, allowed_rep_ids: List[str]) -> ManagerOverview:
        if not allowed_rep_ids:
            # Manager with no assigned reps. Clean empty state.
            return ManagerOverview(
                territory_health=self._compute_health(0.0, None, 0, 0),
                total_reps=0,
                total_growers_under_management=0,
                total_outcomes_logged=0,
                outcomes_last_30d=0,
                average_outcome_rating=None,
                high_priority_growers_count=0,
                open_anomalies_count=0,
                last_activity_at=None,
            )

        # Basic counts
        total_reps = (
            self.db.query(Rep)
            .filter(Rep.rep_id.in_(allowed_rep_ids))
            .count()
        )
        growers = self._allowed_growers_query(allowed_rep_ids).all()
        total_growers = len(growers)

        outcomes = self._allowed_outcomes_query(allowed_rep_ids).all()
        total_outcomes = len(outcomes)

        cutoff_30d = datetime.utcnow() - timedelta(days=HEALTH_COVERAGE_WINDOW_DAYS)
        outcomes_last_30d_list = [o for o in outcomes if (o.recorded_at or o.visited_at) >= cutoff_30d]
        outcomes_last_30d = len(outcomes_last_30d_list)

        avg_rating = (
            round(sum(o.outcome_rating for o in outcomes) / len(outcomes), 2)
            if outcomes else None
        )

        # Compute VPS for each grower (reuse VisitService logic per rep_id)
        all_priorities = []
        for rep_id in allowed_rep_ids:
            try:
                all_priorities.extend(self.visit_service.generate_daily_priority_list(rep_id))
            except Exception:
                # Don't let one rep's failure kill the whole dashboard
                continue

        high_priority_count = sum(1 for p in all_priorities if p["vps"] >= HIGH_VPS_THRESHOLD)

        # Anomalies — count growers with ANY anomaly
        anomalies_count = sum(1 for p in all_priorities if p.get("anomalies"))

        # Last activity = most recent outcome timestamp
        last_activity = (
            max(o.synced_at or o.recorded_at or o.visited_at for o in outcomes)
            if outcomes else None
        )

        # Territory health score
        # Coverage = % of growers with an outcome in last N days
        visited_recently = {o.entity_id for o in outcomes_last_30d_list}
        coverage_pct = (
            (len(visited_recently) / total_growers * 100.0) if total_growers else 0.0
        )

        # High-priority unvisited
        high_priority_unvisited = sum(
            1 for p in all_priorities
            if p["vps"] >= HIGH_VPS_THRESHOLD and p["entity_id"] not in visited_recently
        )

        health = self._compute_health(
            coverage_pct=coverage_pct,
            avg_rating=avg_rating,
            high_priority_unvisited=high_priority_unvisited,
            total_high_priority=high_priority_count,
        )

        return ManagerOverview(
            territory_health=health,
            total_reps=total_reps,
            total_growers_under_management=total_growers,
            total_outcomes_logged=total_outcomes,
            outcomes_last_30d=outcomes_last_30d,
            average_outcome_rating=avg_rating,
            high_priority_growers_count=high_priority_count,
            open_anomalies_count=anomalies_count,
            last_activity_at=last_activity,
        )

    def _compute_health(
        self,
        coverage_pct: float,
        avg_rating: Optional[float],
        high_priority_unvisited: int,
        total_high_priority: int,
    ) -> TerritoryHealthScore:
        # Coverage component (0-100)
        coverage_score = max(0.0, min(100.0, coverage_pct))

        # Outcome quality component (rating 1-5 → 20-100)
        outcome_score = (avg_rating * 20.0) if avg_rating else 0.0
        outcome_score = max(0.0, min(100.0, outcome_score))

        # Urgency resolution component (penalize ignored high-priority growers)
        urgency_score = max(0.0, 100.0 - (high_priority_unvisited * 10.0))

        total = (
            HEALTH_WEIGHT_COVERAGE * coverage_score
            + HEALTH_WEIGHT_OUTCOMES * outcome_score
            + HEALTH_WEIGHT_URGENCY * urgency_score
        )
        total = round(total, 1)

        if total >= HEALTH_LABEL_GOOD:
            label = "healthy"
        elif total >= HEALTH_LABEL_WATCH:
            label = "watch_list"
        else:
            label = "needs_attention"

        return TerritoryHealthScore(
            score=total,
            label=label,
            components={
                "coverage_score":    round(coverage_score, 1),
                "outcome_score":     round(outcome_score, 1),
                "urgency_score":     round(urgency_score, 1),
                "coverage_pct":      round(coverage_pct, 1),
                "avg_rating":        avg_rating,
                "high_priority_unvisited": high_priority_unvisited,
                "total_high_priority":     total_high_priority,
            },
            weights={
                "coverage": HEALTH_WEIGHT_COVERAGE,
                "outcomes": HEALTH_WEIGHT_OUTCOMES,
                "urgency":  HEALTH_WEIGHT_URGENCY,
            },
        )

    # ---------- per-rep ----------

    def rep_metrics(self, allowed_rep_ids: List[str]) -> List[RepMetrics]:
        results = []
        cutoff_30d = datetime.utcnow() - timedelta(days=HEALTH_COVERAGE_WINDOW_DAYS)

        for rep_id in allowed_rep_ids:
            rep = self.db.query(Rep).filter(Rep.rep_id == rep_id).first()
            growers = self.db.query(FarmerRetailer).filter(FarmerRetailer.rep_id == rep_id).all()
            outcomes = self.db.query(Outcome).filter(Outcome.rep_id == rep_id).all()
            outcomes_last_30d = [o for o in outcomes if (o.recorded_at or o.visited_at) >= cutoff_30d]

            try:
                priorities = self.visit_service.generate_daily_priority_list(rep_id)
            except Exception:
                priorities = []

            high_priority = sum(1 for p in priorities if p["vps"] >= HIGH_VPS_THRESHOLD)
            anomalies = sum(1 for p in priorities if p.get("anomalies"))
            avg_rating = (
                round(sum(o.outcome_rating for o in outcomes) / len(outcomes), 2)
                if outcomes else None
            )
            last_activity = (
                max(o.synced_at or o.recorded_at or o.visited_at for o in outcomes)
                if outcomes else None
            )

            # Performance label: simple heuristic
            if len(outcomes_last_30d) == 0:
                perf = "needs_attention"
            elif len(outcomes_last_30d) < 3:
                perf = "low_activity"
            else:
                perf = "active"

            results.append(RepMetrics(
                rep_id=rep_id,
                name=rep.name if rep else f"Rep {rep_id}",
                territory_size=len(growers),
                outcomes_total=len(outcomes),
                outcomes_last_30d=len(outcomes_last_30d),
                average_rating=avg_rating,
                high_priority_count=high_priority,
                anomalies_count=anomalies,
                last_activity_at=last_activity,
                performance_label=perf,
            ))

        return results

    def rep_details(self, rep_id: str, allowed_rep_ids: List[str]) -> dict:
        if rep_id not in allowed_rep_ids:
            raise HTTPException(status_code=403, detail="You don't manage this rep")

        rep = self.db.query(Rep).filter(Rep.rep_id == rep_id).first()
        try:
            priorities = self.visit_service.generate_daily_priority_list(rep_id)
        except Exception as e:
            priorities = []

        recent_outcomes = (
            self.db.query(Outcome)
            .filter(Outcome.rep_id == rep_id)
            .order_by(Outcome.recorded_at.desc().nullslast(), Outcome.visited_at.desc())
            .limit(20)
            .all()
        )

        signal_svc = SignalService(self.db)
        anomalies_payload = signal_svc.get_anomalies(rep_id)

        return {
            "rep_id":         rep_id,
            "name":           rep.name if rep else None,
            "priority_list":  priorities,
            "recent_outcomes": [
                {
                    "id":              o.id,
                    "entity_id":       o.entity_id,
                    "outcome_rating":  o.outcome_rating,
                    "outcome_type":    o.outcome_type,
                    "actions_taken":   o.actions_taken,
                    "notes":           o.notes,
                    "recorded_at":     o.recorded_at,
                    "synced_at":       o.synced_at,
                }
                for o in recent_outcomes
            ],
            "anomalies":      anomalies_payload,
        }

    # ---------- top priorities across territory ----------

    def top_priorities(self, allowed_rep_ids: List[str], limit: int = 10) -> List[TopPriorityGrower]:
        all_items = []
        for rep_id in allowed_rep_ids:
            try:
                priorities = self.visit_service.generate_daily_priority_list(rep_id)
            except Exception:
                continue
            for p in priorities:
                all_items.append(TopPriorityGrower(
                    entity_id=p["entity_id"],
                    name=p["name"],
                    region=p["region"],
                    rep_id=rep_id,
                    vps=p["vps"],
                    rank_within_rep=p["rank"],
                    reasons=p.get("reasons", []),
                    confidence_label=p.get("confidence_label", "low"),
                ))

        # Sort by VPS desc, take top N
        all_items.sort(key=lambda x: x.vps, reverse=True)
        return all_items[:limit]