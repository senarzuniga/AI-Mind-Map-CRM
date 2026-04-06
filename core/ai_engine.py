"""AI Engine: transforms parsed text into structured hierarchical JSON using OpenAI."""
import json
import os
from pathlib import Path

from openai import OpenAI

PROMPTS_DIR = Path(__file__).parent.parent / "models" / "prompts"


def _load_prompt(filename: str) -> str:
    """Load a prompt template from the prompts directory."""
    path = PROMPTS_DIR / filename
    return path.read_text(encoding="utf-8")


def _get_client() -> OpenAI:
    """Create and return an OpenAI client."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY environment variable is not set. "
            "Please set it in your .env file or environment."
        )
    return OpenAI(api_key=api_key)


def _call_ai(prompt: str, model: str = "gpt-4o-mini") -> dict:
    """
    Call the OpenAI API and return parsed JSON.

    Raises ValueError if the response is not valid JSON.
    """
    client = _get_client()

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are a precise JSON generator. Always return valid JSON only, no markdown, no explanations.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content.strip()

    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        raise ValueError(f"AI returned invalid JSON: {e}\nContent: {content[:500]}")


def structure(parsed_text: str) -> dict:
    """
    Transform parsed text into a structured hierarchical JSON mind map.

    Returns a dict with the mind map structure.
    """
    prompt_template = _load_prompt("structure.txt")
    prompt = prompt_template.replace("{input_text}", parsed_text)
    return _call_ai(prompt)


def build_concept(concept: str) -> dict:
    """
    Build a structured explanation of a concept for Concept Mode.

    Returns a dict with definition, components, applications, actions, etc.
    """
    prompt_template = _load_prompt("concept_builder.txt")
    prompt = prompt_template.replace("{concept}", concept)
    return _call_ai(prompt)


def build_client_case(company_data: str) -> dict:
    """
    Generate a consulting client case analysis.

    Returns a dict with situation, problems, opportunities, approach, action_plan.
    """
    prompt_template = _load_prompt("client_case.txt")
    prompt = prompt_template.replace("{company_data}", company_data)
    return _call_ai(prompt)


def build_presentation(structured_data: dict, insights: dict, company_name: str = "") -> dict:
    """
    Generate a presentation structure from analysis data.

    Returns a dict with title and slides array.
    """
    client = _get_client()

    data_summary = json.dumps(
        {"structured": structured_data, "insights": insights}, indent=2
    )[:4000]

    prompt = f"""You are a consulting presentation expert.

Generate a structured presentation from the following analysis data for {company_name or 'the company'}.

Return ONLY valid JSON in this exact format:
{{
  "title": "Presentation title",
  "slides": [
    {{
      "title": "Slide title",
      "type": "title|overview|analysis|insights|recommendations|conclusion",
      "content": [
        "Bullet point 1",
        "Bullet point 2"
      ]
    }}
  ]
}}

Create 6-8 slides covering:
1. Executive Summary
2. Situation Overview
3. Key Findings
4. Sales & Revenue Insights
5. Financial Analysis
6. Operational Recommendations
7. Strategic Action Plan
8. Conclusion & Next Steps

Analysis data:
{data_summary}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a precise JSON generator. Always return valid JSON only.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.4,
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content.strip()
    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        raise ValueError(f"AI returned invalid JSON: {e}")
