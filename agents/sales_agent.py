"""Sales Agent: provides sales-focused insights from structured data."""
import json
import os
from pathlib import Path

from openai import OpenAI

PROMPTS_DIR = Path(__file__).parent.parent / "models" / "prompts"

_DEFAULT_RESPONSE = {
    "priorities": [],
    "actions": [],
    "risks": [],
    "opportunities": [],
}


def run(structured_data: dict) -> dict:
    """
    Run the sales agent on structured data.

    Returns a dict with priorities, actions, risks, and opportunities.
    """
    return _run_agent("sales_agent.txt", structured_data)


def _run_agent(prompt_file: str, structured_data: dict) -> dict:
    """Generic agent runner that loads a prompt and calls the AI."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {**_DEFAULT_RESPONSE, "_error": "OPENAI_API_KEY not set"}

    prompt_template = (PROMPTS_DIR / prompt_file).read_text(encoding="utf-8")
    data_str = json.dumps(structured_data, indent=2)[:3000]
    prompt = prompt_template.replace("{structured_data}", data_str)

    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a precise JSON generator. Return valid JSON only.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.4,
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content.strip()
    try:
        result = json.loads(content)
        # Ensure all required keys exist
        for key in _DEFAULT_RESPONSE:
            if key not in result:
                result[key] = []
        return result
    except json.JSONDecodeError:
        return {**_DEFAULT_RESPONSE, "_error": "Invalid JSON from AI"}
