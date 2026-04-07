"""Mind Map Builder: converts structured JSON into graph nodes and edges."""
from typing import Any


def build(structured_data: dict) -> dict:
    """
    Convert AI-structured JSON into a mind map with nodes and edges.

    Returns:
    {
        "nodes": [{"id": str, "label": str, "type": str, "level": int}],
        "edges": [{"source": str, "target": str}],
        "title": str
    }
    """
    nodes = []
    edges = []

    title = structured_data.get("title", "Mind Map")

    # Root node
    root_id = "root"
    nodes.append({"id": root_id, "label": title, "type": "root", "level": 0})

    level1_items = structured_data.get("level1", [])

    for i, topic in enumerate(level1_items):
        topic_name = topic.get("topic", f"Topic {i+1}")
        topic_id = f"topic_{i}"

        nodes.append({"id": topic_id, "label": topic_name, "type": "topic", "level": 1})
        edges.append({"source": root_id, "target": topic_id})

        level2_items = topic.get("level2", [])

        for j, component in enumerate(level2_items):
            comp_name = component.get("component", f"Component {j+1}")
            comp_id = f"comp_{i}_{j}"

            nodes.append(
                {"id": comp_id, "label": comp_name, "type": "component", "level": 2}
            )
            edges.append({"source": topic_id, "target": comp_id})

            level3_items = component.get("level3", [])

            for k, action_item in enumerate(level3_items):
                action_name = action_item.get("action", f"Action {k+1}")
                action_id = f"action_{i}_{j}_{k}"

                nodes.append(
                    {
                        "id": action_id,
                        "label": action_name,
                        "type": "action",
                        "level": 3,
                    }
                )
                edges.append({"source": comp_id, "target": action_id})

                level4_items = action_item.get("level4", [])

                for m, risk_item in enumerate(level4_items):
                    risk_name = risk_item.get("risk_or_metric", f"Risk {m+1}")
                    risk_type = risk_item.get("type", "risk")
                    risk_id = f"risk_{i}_{j}_{k}_{m}"

                    nodes.append(
                        {
                            "id": risk_id,
                            "label": risk_name,
                            "type": risk_type,
                            "level": 4,
                        }
                    )
                    edges.append({"source": action_id, "target": risk_id})

    return {"title": title, "nodes": nodes, "edges": edges}


def build_from_concept(concept_data: dict) -> dict:
    """
    Build a mind map from concept mode structured data.

    Returns the same nodes/edges format.
    """
    nodes = []
    edges = []

    concept_name = concept_data.get("concept", "Concept")
    root_id = "root"

    nodes.append({"id": root_id, "label": concept_name, "type": "root", "level": 0})

    # Definition node
    definition = concept_data.get("definition", "")
    if definition:
        def_id = "definition"
        nodes.append(
            {"id": def_id, "label": "Definition", "type": "topic", "level": 1}
        )
        edges.append({"source": root_id, "target": def_id})
        def_text_id = "def_text"
        # Truncate for display
        short_def = definition[:60] + "..." if len(definition) > 60 else definition
        nodes.append(
            {"id": def_text_id, "label": short_def, "type": "component", "level": 2}
        )
        edges.append({"source": def_id, "target": def_text_id})

    # Components
    components = concept_data.get("components", [])
    if components:
        comp_parent_id = "components"
        nodes.append(
            {
                "id": comp_parent_id,
                "label": "Components",
                "type": "topic",
                "level": 1,
            }
        )
        edges.append({"source": root_id, "target": comp_parent_id})

        for i, comp in enumerate(components):
            comp_id = f"comp_{i}"
            nodes.append(
                {
                    "id": comp_id,
                    "label": comp.get("name", f"Component {i+1}"),
                    "type": "component",
                    "level": 2,
                }
            )
            edges.append({"source": comp_parent_id, "target": comp_id})

            for j, example in enumerate(comp.get("examples", [])[:2]):
                ex_id = f"ex_{i}_{j}"
                nodes.append(
                    {"id": ex_id, "label": example, "type": "action", "level": 3}
                )
                edges.append({"source": comp_id, "target": ex_id})

    # Applications
    applications = concept_data.get("applications", [])
    if applications:
        app_parent_id = "applications"
        nodes.append(
            {
                "id": app_parent_id,
                "label": "Applications",
                "type": "topic",
                "level": 1,
            }
        )
        edges.append({"source": root_id, "target": app_parent_id})

        for i, app in enumerate(applications):
            app_id = f"app_{i}"
            nodes.append(
                {
                    "id": app_id,
                    "label": app.get("context", f"Application {i+1}"),
                    "type": "component",
                    "level": 2,
                }
            )
            edges.append({"source": app_parent_id, "target": app_id})

    # Actions
    actions = concept_data.get("actions", [])
    if actions:
        actions_parent_id = "actions"
        nodes.append(
            {
                "id": actions_parent_id,
                "label": "Actions",
                "type": "topic",
                "level": 1,
            }
        )
        edges.append({"source": root_id, "target": actions_parent_id})

        for i, action in enumerate(actions):
            act_id = f"act_{i}"
            nodes.append(
                {"id": act_id, "label": action, "type": "action", "level": 2}
            )
            edges.append({"source": actions_parent_id, "target": act_id})

    return {"title": concept_name, "nodes": nodes, "edges": edges}
