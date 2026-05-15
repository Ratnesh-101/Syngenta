EXPLAINER_PROMPT = """
A Syngenta field rep needs to understand why {name} was ranked #{rank} today.

Score breakdown (signal → contribution to score):
{score_breakdown}

Overrides applied: {overrides}

Write exactly 2 sentences explaining the ranking.
- Be specific — use actual values from the breakdown
- Sound like a smart colleague explaining to a peer
- Do not say "based on the data" or "according to the system"

Example of good output:
"Rajan jumped to #1 because his herbicide stock is nearly gone right before
sowing season — if you skip today, he'll buy from whoever shows up first."
"""