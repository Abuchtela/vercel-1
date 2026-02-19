"""
ClawMode Integration - Economic tracking for nanobot agents.

This package integrates the ClawWork economic engine with the nanobot
agent framework, providing:
- Token cost tracking for every LLM call
- Task classification and valuation
- Work evaluation and payment
- Economic survival mechanics

Main components:
- ClawWorkAgentLoop: Subclasses nanobot's AgentLoop for cost tracking
- TaskClassifier: Classifies tasks and estimates value
- TrackedProvider: Wraps LLM provider to track token costs
- ClawWork tools: decide_activity, submit_work, learn, get_status
"""

__version__ = "0.1.0"

from .agent_loop import ClawWorkAgentLoop
from .task_classifier import TaskClassifier
from .provider_wrapper import TrackedProvider
from .tools import (
    decide_activity_tool,
    submit_work_tool,
    learn_tool,
    get_status_tool,
)

__all__ = [
    "ClawWorkAgentLoop",
    "TaskClassifier",
    "TrackedProvider",
    "decide_activity_tool",
    "submit_work_tool",
    "learn_tool",
    "get_status_tool",
]
