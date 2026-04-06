"""Manager Agent: provides management-focused insights from structured data."""
from agents.base import run_agent


def run(structured_data: dict) -> dict:
    """
    Run the management agent on structured data.

    Returns a dict with priorities, actions, risks, and opportunities.
    """
    return run_agent("management_agent.txt", structured_data)
