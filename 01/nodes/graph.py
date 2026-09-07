from typing import Literal

from langgraph.graph import StateGraph, START, END

from state import PostState

from nodes.topic import get_topic
from nodes.generator import generate_post
from nodes.evaluator import evaluate_post
from nodes.improver import improve_post
from nodes.publisher import publish_to_x


# -------------------------
# Routing
# -------------------------

def quality_check(state: PostState) -> Literal["improve", "publish"]:

    score = state.get("score", 0)
    attempts = state.get("attempts", 0)

    # Don't loop forever
    if score >= 8:
        return "publish"

    if attempts >= 3:
        return "publish"

    return "improve"


# -------------------------
# Final post node
# -------------------------

def prepare_final_post(state):

    return {
        "final_post": state["draft"]
    }


# -------------------------
# Graph
# -------------------------

builder = StateGraph(PostState)


builder.add_node("topic", get_topic)
builder.add_node("generate", generate_post)
builder.add_node("evaluate", evaluate_post)
builder.add_node("improve", improve_post)
builder.add_node("finalize", prepare_final_post)
builder.add_node("publish", publish_to_x)


builder.add_edge(START, "topic")

builder.add_edge("topic", "generate")

builder.add_edge("generate", "evaluate")


builder.add_conditional_edges(
    "evaluate",
    quality_check,
    {
        "improve": "improve",
        "publish": "finalize"
    }
)


builder.add_edge("improve", "evaluate")

builder.add_edge("finalize", "publish")

builder.add_edge("publish", END)


graph = builder.compile()

