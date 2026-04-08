"""Mind Map Builder: converts structured JSON into graph nodes and edges."""

# ── Semantic node styles ────────────────────────────────────────────────────
NODE_STYLES = {
    "root":        {"emoji": "🧠", "color": "#6D28D9"},  # purple – strategic
    "topic":       {"emoji": "🧭", "color": "#1D4ED8"},  # blue   – information
    "component":   {"emoji": "📊", "color": "#0E7490"},  # teal   – data
    "action":      {"emoji": "🎯", "color": "#15803D"},  # green  – positive
    "risk":        {"emoji": "⚠️",  "color": "#B91C1C"},  # red    – risk
    "metric":      {"emoji": "📈", "color": "#7C3AED"},  # purple – metric
    "insight":     {"emoji": "💡", "color": "#B45309"},  # amber  – insight
    "opportunity": {"emoji": "🚀", "color": "#047857"},  # green  – opportunity
    "definition":  {"emoji": "📖", "color": "#1D4ED8"},  # blue   – information
    "applications":{"emoji": "🔧", "color": "#0E7490"},  # teal
    "components":  {"emoji": "📦", "color": "#1D4ED8"},  # blue
    "actions":     {"emoji": "✅", "color": "#15803D"},  # green
}

# ── Semantic edge styles by (source_level, target_level) ───────────────────
EDGE_STYLES = {
    (0, 1): {"type": "flow",   "label": "expands",   "emoji": "➡️"},
    (1, 2): {"type": "impact", "label": "drives",    "emoji": "⚡"},
    (2, 3): {"type": "action", "label": "requires",  "emoji": "🎯"},
    (3, 4): {"type": "risk",   "label": "threatens", "emoji": "⚠️"},
}
DEFAULT_EDGE_STYLE = {"type": "flow", "label": "relates", "emoji": "→"}

# ── Overrides when the target node type is known ────────────────────────────
EDGE_TYPE_OVERRIDES = {
    "risk":        {"type": "risk",    "label": "threatens", "emoji": "⚠️"},
    "metric":      {"type": "insight", "label": "measures",  "emoji": "💡"},
    "insight":     {"type": "insight", "label": "generates", "emoji": "💡"},
    "opportunity": {"type": "loop",    "label": "creates",   "emoji": "🔄"},
}


def _enrich_node(node: dict) -> dict:
    """Add emoji and color fields to a node dict based on its type."""
    ntype = node.get("type", "action")
    style = NODE_STYLES.get(ntype, {"emoji": "🔹", "color": "#374151"})
    return {
        **node,
        "emoji": node.get("emoji") or style["emoji"],
        "color": node.get("color") or style["color"],
    }


def _enrich_edge(edge: dict, node_level_map: dict, node_type_map: dict) -> dict:
    """Add semantic type, label, and emoji to an edge dict."""
    if edge.get("type") and edge.get("emoji"):
        return edge  # already enriched

    src_level = node_level_map.get(edge["source"], 0)
    tgt_level = node_level_map.get(edge["target"], src_level + 1)
    tgt_type = node_type_map.get(edge["target"], "action")

    style = EDGE_TYPE_OVERRIDES.get(
        tgt_type,
        EDGE_STYLES.get((src_level, tgt_level), DEFAULT_EDGE_STYLE),
    )
    return {
        **edge,
        "type":  style["type"],
        "label": style["label"],
        "emoji": style["emoji"],
    }


def build(structured_data: dict) -> dict:
    """
    Convert AI-structured JSON into a mind map with nodes and edges.

    Returns:
    {
        "nodes": [{"id": str, "label": str, "type": str, "level": int,
                   "emoji": str, "color": str}],
        "edges": [{"source": str, "target": str, "type": str,
                   "label": str, "emoji": str}],
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

    # Enrich nodes and edges with semantic metadata
    nodes = [_enrich_node(n) for n in nodes]
    node_level_map = {n["id"]: n["level"] for n in nodes}
    node_type_map  = {n["id"]: n["type"]  for n in nodes}
    edges = [_enrich_edge(e, node_level_map, node_type_map) for e in edges]

    return {"title": title, "nodes": nodes, "edges": edges}


def build_from_concept(concept_data: dict) -> dict:
    """
    Build a mind map from concept mode structured data.

    Returns the same enriched nodes/edges format.
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
            {"id": def_id, "label": "📖 Definition", "type": "topic", "level": 1}
        )
        edges.append({"source": root_id, "target": def_id})
        def_text_id = "def_text"
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
                "label": "📦 Components",
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
                "label": "🔧 Applications",
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
                "label": "✅ Actions",
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

    # Enrich nodes and edges with semantic metadata
    nodes = [_enrich_node(n) for n in nodes]
    node_level_map = {n["id"]: n["level"] for n in nodes}
    node_type_map  = {n["id"]: n["type"]  for n in nodes}
    edges = [_enrich_edge(e, node_level_map, node_type_map) for e in edges]

    return {"title": concept_name, "nodes": nodes, "edges": edges}
