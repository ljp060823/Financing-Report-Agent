from typing import TypedDict, Annotated, List
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    messages: Annotated[List, add_messages]
    research_results: List[dict]
    graph_results: str
    draft: str
    critique: str
    iteration: int = 0
    final_report: str
    final_pdf_path: str | None
    human_feedback: str | None
    user_id: str