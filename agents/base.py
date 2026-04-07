"""Shared base agent logic to avoid duplication across agent modules."""
import json
import os
from pathlib import Path

from openai import OpenAI

PROMPTS_DIR = Path(__file__).parent.parent / "models" / "prompts"

DEFAULT_RESPONSE = {
    "priorities": [],
    "actions": [],
    "risks": [],
    "opportunities": [],
}


def run_agent(prompt_file: str, structured_data: dict) -> dict:
    """
    Generic agent runner: loads a prompt template, injects structured data,
    calls the OpenAI API, and returns parsed JSON.

    Returns a dict with keys: priorities, actions, risks, opportunities.
    On error (missing API key, invalid JSON) returns DEFAULT_RESPONSE with an
    '_error' key describing the issue.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {**DEFAULT_RESPONSE, "_error": "OPENAI_API_KEY not set"}

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
        for key in DEFAULT_RESPONSE:
            if key not in result:
                result[key] = []
        return result
    except json.JSONDecodeError:
        return {**DEFAULT_RESPONSE, "_error": "Invalid JSON from AI"}
