import os
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from core.llm.prompts.explainer import EXPLAINER_PROMPT

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.3,
    api_key=os.getenv("OPENAI_API_KEY")
)

def run_explainer_chain(context: dict, reasons: list) -> str:
    prompt = PromptTemplate(
        input_variables=["name", "rank", "score_breakdown", "overrides"],
        template=EXPLAINER_PROMPT
    )
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({
        "name":            context.get("name", "this farmer"),
        "rank":            context.get("rank", "?"),
        "score_breakdown": format_breakdown(reasons),
        "overrides":       format_overrides(context.get("overrides", []))
    })

def format_breakdown(reasons: list) -> str:
    if not reasons:
        return "No signals available"
    return "\n".join(f"- {r}" for r in reasons)

def format_overrides(overrides: list) -> str:
    if not overrides:
        return "None"
    return "\n".join(f"- {o}" for o in overrides)