
class VisitOutcome(BaseModel):
    entity_id:        str
    rep_id:           str
    visited_at:       datetime
    vps_at_visit:     float          # what score said
    actions_taken:    list[str]      # which NBA actions were executed
    outcome_rating:   int            # rep scores: 1–5
    outcome_type:     str            # "sale" | "complaint_resolved" | "intel" | "no_result"
    notes:            str
    signals_at_visit: dict           # snapshot of features used