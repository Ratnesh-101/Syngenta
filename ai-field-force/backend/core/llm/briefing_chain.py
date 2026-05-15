

# core/llm/briefing_chain.py

from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
from core.llm.prompts.briefing import BRIEFING_PROMPT

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

def run_briefing_chain(context: dict, nba_actions: list) -> str:
    prompt = PromptTemplate(
        input_variables=["entity_profile", "signal_summary", "nba_actions"],
        template=BRIEFING_PROMPT
    )
    chain = LLMChain(llm=llm, prompt=prompt)
    return chain.run(
        entity_profile=format_profile(context),
        signal_summary=format_signals(context),
        nba_actions=format_actions(nba_actions)
    )

def format_profile(ctx: dict) -> str:
    return f"{ctx['name']} | {ctx['type']} | Region: {ctx.get('region', 'unknown')}"

def format_signals(ctx: dict) -> str:
    s = ctx["signals"]
    return (
        f"Pest: {s.get('pest_alert_severity', 'none')} | "
        f"Stock shortage: {s.get('inventory_shortage_level', 0):.0%} | "
        f"Days since visit: {s.get('days_since_last_visit', '?')} | "
        f"Crop stage: {s.get('crop_stage', 'unknown')}"
    )

def format_actions(actions: list) -> str:
    return "\n".join(
        f"{i+1}. {a['action']}: {a['detail']}"
        for i, a in enumerate(actions)
    )