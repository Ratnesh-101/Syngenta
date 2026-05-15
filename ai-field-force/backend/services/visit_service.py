


# services/visit_service.py

from core.deterministic.signal_normalizer  import *
from core.deterministic.override_rules     import apply_overrides
from core.deterministic.anomaly_detector   import run_anomaly_checks
from core.deterministic.nba_engine         import get_next_best_actions
from core.deterministic.explainer          import extract_top_reasons
from core.ml.feature_builder               import build_feature_vector
from core.ml.priority_scorer               import compute_vps
from core.ml.confidence                    import compute_confidence
from core.ml.weights                       import SIGNAL_WEIGHTS
from core.llm.briefing_chain               import run_briefing_chain
from core.llm.explainer_chain              import run_explainer_chain
from db.session                            import get_db

class VisitService:

    def generate_daily_priority_list(rep_id: str, date: str) -> list[dict]:
        entities = get_rep_territory(rep_id)         # DB fetch
        signals  = get_latest_signals(entities)       # Redis/DB
        weights  = get_current_weights(rep_id)        # starts as defaults

        scored = []
        for entity in entities:
            features  = build_feature_vector(entity, signals)
            vps       = compute_vps(features, weights)
            vps, overrides = apply_overrides(entity, vps)
            reasons   = extract_top_reasons(features, weights, overrides)
            confidence = compute_confidence(features)

            scored.append({
                "entity_id":    entity["id"],
                "vps":          vps,
                "reasons":      reasons,
                "confidence":   confidence,
                "features":     features,   # stored for explainability
            })

        # Sort by VPS descending, then sequence by geo-proximity
        ranked   = sorted(scored, key=lambda x: x["vps"], reverse=True)
        sequenced = apply_geo_sequence(ranked, rep_start_location(rep_id))

        return sequenced

    def get_visit_brief(self, entity_id: str, rep_id: str) -> dict:
        # calls LLM — slower, on demand
        ...

    def _geo_sequence(self, ranked: list, start: tuple) -> list:
        # greedy nearest-neighbor
        ...