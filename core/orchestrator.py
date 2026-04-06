"""Orchestrator: coordinates the full analysis pipeline."""
import sys
from pathlib import Path

# Ensure the project root is on the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import ai_engine, mindmap_builder, parser
from agents import finance_agent, manager_agent, ops_agent, sales_agent


class Orchestrator:
    """
    Coordinates the complete analysis pipeline:
    Input → Parse → AI Structure → Mind Map → Multi-Agent Insights
    """

    def run(self, input_data) -> tuple:
        """
        Run the full analysis pipeline.

        Args:
            input_data: str, bytes, or Path — the raw input

        Returns:
            (mindmap: dict, insights: dict, structured_data: dict)
        """
        # Step 1: Parse input
        parsed = parser.parse(input_data)

        if not parsed:
            raise ValueError("Input is empty after parsing.")

        # Step 2: AI structuring
        structured = ai_engine.structure(parsed)

        # Step 3: Build mind map
        mindmap = mindmap_builder.build(structured)

        # Step 4: Run multi-agent insights
        insights = {
            "sales": sales_agent.run(structured),
            "finance": finance_agent.run(structured),
            "operations": ops_agent.run(structured),
            "management": manager_agent.run(structured),
        }

        return mindmap, insights, structured

    def run_concept(self, concept: str) -> tuple:
        """
        Run the concept analysis pipeline.

        Returns:
            (mindmap: dict, concept_data: dict)
        """
        concept_data = ai_engine.build_concept(concept)
        mindmap = mindmap_builder.build_from_concept(concept_data)
        return mindmap, concept_data
