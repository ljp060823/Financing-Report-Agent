from langgraph.graph import StateGraph, END, START
from app.graph.state import AgentState
from app.agents.researcher import researcher_node
from app.agents.graph_reasoner import graph_reasoner_node
from app.agents.writer import writer_node
from app.agents.critic import critic_node
from app.tools import generate_pdf
from app.db import get_checkpointer

async def finalizer_node(state: AgentState):
    pdf_path = generate_pdf(state["final_report"])
    return {"final_pdf_path": pdf_path, "messages": [{"content": f"PDF已生成：{pdf_path}"}]}

def should_continue(state: AgentState):
    if state.get("human_feedback") or state["iteration"] >= 3:
        return "finalizer"
    return "writer"

graph_builder = StateGraph(AgentState)
graph_builder.add_node("researcher", researcher_node)
graph_builder.add_node("graph_reasoner", graph_reasoner_node)
graph_builder.add_node("writer", writer_node)
graph_builder.add_node("critic", critic_node)
graph_builder.add_node("finalizer", finalizer_node)

graph_builder.add_edge(START, "researcher")
graph_builder.add_edge("researcher", "graph_reasoner")
graph_builder.add_edge("graph_reasoner", "writer")
graph_builder.add_edge("writer", "critic")
graph_builder.add_conditional_edges("critic", should_continue, {"writer": "writer", "finalizer": "finalizer"})
graph_builder.add_edge("finalizer", END)

async def build_graph():
    graph = graph_builder.compile(
        checkpointer=await get_checkpointer(),
        interrupt_before=["critic"]
    )
    return graph