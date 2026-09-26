"""Alt LangGraph example for a simple routed agent workflow."""

from typing import Literal, TypedDict

from langgraph.graph import END, StateGraph
from pydantic import BaseModel


class AgentResponse(BaseModel):
    user_input: str
    category: Literal["greeting", "question"]
    response: str


class AgentState(TypedDict):
    user_input: str
    category: Literal["greeting", "question"]
    response: str


def classify_node(state: AgentState) -> dict[str, str]:
    text = state["user_input"].lower()
    category = "greeting" if any(word in text for word in ["hi", "hello", "hey"]) else "question"
    return {"category": category}


def greeting_node(state: AgentState) -> dict[str, str]:
    return {"response": f"Hello, {state['user_input']}! Welcome to agentic AI."}


def question_node(state: AgentState) -> dict[str, str]:
    return {"response": f"Thanks for your question: {state['user_input']}"}


def route(state: AgentState) -> Literal["greeting", "question"]:
    return state["category"]


def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("classify", classify_node)
    graph.add_node("greeting", greeting_node)
    graph.add_node("question", question_node)

    graph.set_entry_point("classify")
    graph.add_conditional_edges("classify", route, {"greeting": "greeting", "question": "question"})
    graph.add_edge("greeting", END)
    graph.add_edge("question", END)
    return graph.compile()


if __name__ == "__main__":
    app = build_graph()
    result = app.invoke({"user_input": "hello there", "category": "greeting", "response": ""})
    validated_result = AgentResponse(**result)
    print(validated_result.model_dump())