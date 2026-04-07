"""Finance Agent: provides finance-focused insights from structured data."""
from agents.base import run_agent


def run(structured_data: dict) -> dict:
    """
    Run the finance agent on structured data.

    Returns a dict with priorities, actions, risks, and opportunities.
    """
    return run_agent("finance_agent.txt", structured_data)
