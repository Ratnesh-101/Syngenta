# core/llm/prompts/anomaly_context.py

ANOMALY_CONTEXT_PROMPT = """
Given this farmer's recent history:
{visit_history_summary}

And today's signals:
{current_signals}

Identify ONE non-obvious anomaly or opportunity a field rep might miss.
Return JSON: {{"anomaly": "...", "action": "...", "confidence": 0.0-1.0}}
If nothing notable, return {{"anomaly": null}}
"""