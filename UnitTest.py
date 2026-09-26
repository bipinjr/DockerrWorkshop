"""Unit tests and retry wrapper for the LangGraph workshop agent."""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import pytest
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)


class LLMAPIError(RuntimeError):
    """Raised when the LLM backend call fails."""


def classify_node(state: dict[str, str]) -> dict[str, str]:
    question = state["question"].lower()
    category = "math" if any(word in question for word in ["add", "sum", "multiply", "plus"]) else "general"
    return {"category": category}


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type(LLMAPIError),
    reraise=True,
)
def call_llm_with_retry(prompt: str, llm: Any) -> str:
    """Call the model with retries and graceful API error handling."""
    try:
        response = llm.invoke(prompt)
        return response.content
    except Exception as exc:  # pragma: no cover - exercised through retry tests
        raise LLMAPIError(f"API call failed for prompt: {prompt}") from exc


def test_classify_math_question() -> None:
    result = classify_node({"question": "add 5 and 3"})
    assert result == {"category": "math"}


def test_classify_general_question() -> None:
    result = classify_node({"question": "What is Python?"})
    assert result == {"category": "general"}


def test_classify_empty_question_defaults_to_general() -> None:
    result = classify_node({"question": ""})
    assert result == {"category": "general"}


def test_call_llm_with_retry_returns_content() -> None:
    mock_llm = MagicMock()
    mock_llm.invoke.return_value.content = "Hello from LLM"

    result = call_llm_with_retry("Say hello", mock_llm)

    assert result == "Hello from LLM"
    mock_llm.invoke.assert_called_once_with("Say hello")


def test_call_llm_with_retry_raises_api_error_after_retries() -> None:
    mock_llm = MagicMock()
    mock_llm.invoke.side_effect = RuntimeError("temporary API issue")

    with pytest.raises(LLMAPIError, match="API call failed"):
        call_llm_with_retry("retry this", mock_llm)