"""Conditional LangGraph agent workflow.

Workflow design on paper:
1. The user question enters the graph.
2. classify_node decides whether the request is math or general.
3. The router sends control to the correct node.
4. The selected node generates an answer.
5. The final state is validated with a Pydantic model.
"""

from typing import Literal, TypedDict

from langgraph.graph import END, StateGraph
from pydantic import BaseModel


class AgentResponse(BaseModel):
    question: str
    category: Literal["math", "general"]
    answer: str


class State(TypedDict):
    question: str
    category: Literal["math", "general"]
    answer: str


def classify_node(state: State) -> dict[str, str]:
    question = state["question"].lower()
    category = "math" if any(word in question for word in ["add", "sum", "multiply", "plus"]) else "general"
    return {"category": category}


def math_node(state: State) -> dict[str, str]:
    return {"answer": f"I will solve the math question: {state['question']} step by step."}


def general_node(state: State) -> dict[str, str]:
    return {"answer": f"Here is a helpful general answer for: {state['question']}"}


def route(state: State) -> Literal["math", "general"]:
    return state["category"]


def build_graph():
    graph = StateGraph(State)
    graph.add_node("classify", classify_node)
    graph.add_node("math", math_node)
    graph.add_node("general", general_node)

    graph.set_entry_point("classify")
    graph.add_conditional_edges(
        "classify",
        route,
        {
            "math": "math",
            "general": "general",
        },
    )
    graph.add_edge("math", END)
    graph.add_edge("general", END)
    return graph.compile()


if __name__ == "__main__":
    app = build_graph()
    result = app.invoke({"question": "add 5 and 3", "category": "general", "answer": ""})
    validated_result = AgentResponse(**result)
    print(validated_result.model_dump())