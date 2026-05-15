
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