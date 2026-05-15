ALERT_SUMMARY_PROMPT = """
You are summarizing field alerts for a Syngenta territory manager.

Active anomalies across the territory:
{anomalies_list}

Write a 3-sentence morning briefing:
- What's the most urgent issue and where
- Any pattern across multiple farmers/retailers
- One recommended action for the manager to take today

Be specific. No vague statements. Under 80 words total.
"""
