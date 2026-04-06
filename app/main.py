"""
AI Mind Map CRM — Main Streamlit Application
Modes: Analysis | Presentation | Concept
"""
import json
import os
import sys
from pathlib import Path

# Ensure project root is on sys.path when running from app/
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

import streamlit as st
from dotenv import load_dotenv

load_dotenv(ROOT / ".env")

from core import ai_engine, mindmap_builder, orchestrator, presentation_builder
from utils import memory_store
from utils.file_loader import load_file

# ─── Constants ───────────────────────────────────────────────────────────────
TEXT_PREVIEW_LENGTH = 1000

# ─── Page config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Mind Map CRM",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Helpers ────────────────────────────────────────────────────────────────

def _render_mindmap_html(mindmap: dict) -> str:
    """Render the mind map as an interactive HTML using PyVis."""
    try:
        from pyvis.network import Network

        node_colors = {
            "root": "#FF6B35",
            "topic": "#4ECDC4",
            "component": "#45B7D1",
            "action": "#96CEB4",
            "risk": "#FF6B6B",
            "metric": "#DDA0DD",
        }

        net = Network(height="600px", width="100%", bgcolor="#1e1e2e", font_color="white")
        net.set_options("""
        {
          "physics": {
            "enabled": true,
            "solver": "forceAtlas2Based",
            "forceAtlas2Based": {
              "gravitationalConstant": -50,
              "centralGravity": 0.01,
              "springLength": 120,
              "springConstant": 0.08,
              "damping": 0.4
            },
            "stabilization": {"iterations": 150}
          },
          "interaction": {"hover": true, "tooltipDelay": 100},
          "nodes": {"font": {"size": 12}},
          "edges": {"smooth": {"type": "dynamic"}}
        }
        """)

        for node in mindmap.get("nodes", []):
            color = node_colors.get(node.get("type", "action"), "#96CEB4")
            size = max(10, 30 - node.get("level", 0) * 5)
            net.add_node(
                node["id"],
                label=node["label"],
                color=color,
                size=size,
                title=f"Type: {node.get('type', '')} | Level: {node.get('level', '')}",
            )

        for edge in mindmap.get("edges", []):
            net.add_edge(edge["source"], edge["target"], color="#555577")

        # Write to temp file and read back
        tmp_path = ROOT / "outputs" / "mindmaps" / "_current.html"
        tmp_path.parent.mkdir(parents=True, exist_ok=True)
        net.save_graph(str(tmp_path))

        return tmp_path.read_text(encoding="utf-8")

    except ImportError:
        return "<p style='color:white'>PyVis not installed. Run: pip install pyvis</p>"


def _export_json(data: dict, filename: str) -> bytes:
    return json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")


def _export_pdf_report(
    company_name: str, structured_data: dict, insights: dict
) -> bytes:
    """Generate a simple PDF report using reportlab."""
    try:
        from io import BytesIO

        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.lib.units import inch
        from reportlab.platypus import (
            Paragraph,
            SimpleDocTemplate,
            Spacer,
            Table,
            TableStyle,
        )

        buf = BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=letter)
        styles = getSampleStyleSheet()

        heading1 = ParagraphStyle(
            "Heading1Custom",
            parent=styles["Heading1"],
            fontSize=18,
            spaceAfter=12,
        )
        heading2 = ParagraphStyle(
            "Heading2Custom",
            parent=styles["Heading2"],
            fontSize=14,
            spaceAfter=8,
        )
        normal = styles["Normal"]

        story = []
        story.append(Paragraph(f"AI Mind Map CRM Report", heading1))
        story.append(Paragraph(f"Company: {company_name}", heading2))
        story.append(Spacer(1, 0.2 * inch))

        # Structured Data Summary
        story.append(Paragraph("Analysis Overview", heading2))
        title = structured_data.get("title", "N/A")
        story.append(Paragraph(f"<b>Title:</b> {title}", normal))
        story.append(Spacer(1, 0.1 * inch))

        for topic in structured_data.get("level1", [])[:5]:
            story.append(Paragraph(f"• {topic.get('topic', '')}", normal))

        story.append(Spacer(1, 0.2 * inch))

        # Insights per agent
        agent_names = {
            "sales": "Sales Insights",
            "finance": "Finance Insights",
            "operations": "Operations Insights",
            "management": "Management Insights",
        }

        for agent_key, agent_title in agent_names.items():
            agent_data = insights.get(agent_key, {})
            if not agent_data:
                continue

            story.append(Paragraph(agent_title, heading2))

            for section in ["priorities", "actions", "risks", "opportunities"]:
                items = agent_data.get(section, [])
                if items:
                    story.append(
                        Paragraph(f"<b>{section.capitalize()}:</b>", normal)
                    )
                    for item in items:
                        story.append(Paragraph(f"  – {item}", normal))

            story.append(Spacer(1, 0.15 * inch))

        doc.build(story)
        buf.seek(0)
        return buf.read()

    except ImportError:
        return b"reportlab not installed. Run: pip install reportlab"


# ─── Sidebar ────────────────────────────────────────────────────────────────

def render_sidebar():
    st.sidebar.title("🧠 AI Mind Map CRM")
    st.sidebar.markdown("---")

    mode = st.sidebar.radio(
        "Select Mode",
        ["📊 Analysis Mode", "🎯 Presentation Mode", "💡 Concept Mode", "📁 CRM Memory"],
        index=0,
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("**Settings**")

    api_key_input = st.sidebar.text_input(
        "OpenAI API Key",
        type="password",
        value=os.getenv("OPENAI_API_KEY", ""),
        help="Enter your OpenAI API key. Alternatively, set OPENAI_API_KEY in .env file.",
    )
    if api_key_input:
        os.environ["OPENAI_API_KEY"] = api_key_input

    st.sidebar.markdown("---")
    st.sidebar.caption("v1.0 · Built with Streamlit + OpenAI")

    return mode


# ─── Analysis Mode ──────────────────────────────────────────────────────────

def render_analysis_mode():
    st.title("📊 Analysis Mode")
    st.markdown(
        "Upload a document or enter text to generate a structured mind map with AI-driven insights."
    )

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Input")
        input_method = st.radio("Input Method", ["Text Input", "File Upload"])

        company_name = st.text_input("Company Name", placeholder="e.g. Acme Corp")
        company_id = st.text_input(
            "Company ID",
            placeholder="e.g. acme_corp",
            help="Used as the key in CRM memory",
        )

        input_text = ""

        if input_method == "Text Input":
            input_text = st.text_area(
                "Enter text, strategy, or description",
                height=200,
                placeholder="Paste your business text, strategy document, or analysis here...",
            )
        else:
            uploaded_file = st.file_uploader(
                "Upload PDF, TXT, or Markdown",
                type=["pdf", "txt", "md", "markdown"],
            )
            if uploaded_file:
                try:
                    input_text = load_file(uploaded_file)
                    st.success(f"✅ Loaded {len(input_text):,} characters")
                    with st.expander("Preview text"):
                        st.text(input_text[:TEXT_PREVIEW_LENGTH] + ("..." if len(input_text) > TEXT_PREVIEW_LENGTH else ""))
                except Exception as e:
                    st.error(f"Error loading file: {e}")

        run_btn = st.button("🚀 Run Analysis", use_container_width=True, type="primary")

    with col2:
        if run_btn:
            if not input_text.strip():
                st.warning("Please enter some text or upload a file.")
                return

            if not os.getenv("OPENAI_API_KEY"):
                st.error("OpenAI API key is required. Set it in the sidebar.")
                return

            orch = orchestrator.Orchestrator()

            with st.spinner("Running analysis pipeline..."):
                try:
                    progress = st.progress(0, text="Parsing input...")
                    mindmap, insights, structured = orch.run(input_text)
                    progress.progress(100, text="Complete!")

                    st.session_state["mindmap"] = mindmap
                    st.session_state["insights"] = insights
                    st.session_state["structured"] = structured
                    st.session_state["company_name"] = company_name or "Unknown Company"
                    st.session_state["company_id"] = company_id or "unknown"
                    st.session_state["input_text"] = input_text

                    # Auto-save to CRM
                    if company_id:
                        memory_store.save_analysis(
                            company_id=company_id,
                            company_name=company_name or company_id,
                            input_text=input_text,
                            structured_data=structured,
                            mindmap=mindmap,
                            insights=insights,
                        )
                        st.success(f"✅ Analysis saved to CRM as '{company_id}'")

                except Exception as e:
                    st.error(f"Analysis failed: {e}")
                    return

        # Display results if available
        if "mindmap" in st.session_state:
            _display_analysis_results()


def _display_analysis_results():
    mindmap = st.session_state["mindmap"]
    insights = st.session_state["insights"]
    structured = st.session_state["structured"]
    company_name = st.session_state.get("company_name", "")

    tab1, tab2, tab3, tab4 = st.tabs(
        ["🗺️ Mind Map", "💡 Insights", "📋 Structured Data", "📥 Export"]
    )

    with tab1:
        st.subheader(f"Mind Map: {mindmap.get('title', '')}")
        html = _render_mindmap_html(mindmap)
        st.components.v1.html(html, height=620, scrolling=False)

        # Legend
        with st.expander("Legend"):
            cols = st.columns(5)
            legend = [
                ("🟠", "Root"),
                ("🟦", "Topic"),
                ("🔵", "Component"),
                ("🟢", "Action"),
                ("🔴", "Risk/Metric"),
            ]
            for col, (icon, label) in zip(cols, legend):
                col.markdown(f"{icon} {label}")

    with tab2:
        st.subheader("Multi-Agent Insights")
        agent_tabs = st.tabs(["💼 Sales", "💰 Finance", "⚙️ Operations", "🎯 Management"])

        agent_keys = ["sales", "finance", "operations", "management"]
        agent_icons = {
            "priorities": "🎯",
            "actions": "✅",
            "risks": "⚠️",
            "opportunities": "🚀",
        }

        for agent_tab, agent_key in zip(agent_tabs, agent_keys):
            with agent_tab:
                agent_data = insights.get(agent_key, {})
                if "_error" in agent_data:
                    st.error(agent_data["_error"])
                    continue

                for section, icon in agent_icons.items():
                    items = agent_data.get(section, [])
                    if items:
                        st.markdown(f"**{icon} {section.capitalize()}**")
                        for item in items:
                            st.markdown(f"- {item}")
                        st.markdown("")

    with tab3:
        st.subheader("Structured Data")
        st.json(structured)

    with tab4:
        st.subheader("Export")
        col1, col2, col3 = st.columns(3)

        with col1:
            json_data = _export_json(
                {"structured": structured, "mindmap": mindmap, "insights": insights},
                "analysis.json",
            )
            st.download_button(
                "📄 Download JSON",
                data=json_data,
                file_name=f"{company_name or 'analysis'}_mindmap.json",
                mime="application/json",
                use_container_width=True,
            )

        with col2:
            html_content = _render_mindmap_html(mindmap).encode("utf-8")
            st.download_button(
                "🗺️ Download Mind Map (HTML)",
                data=html_content,
                file_name=f"{company_name or 'mindmap'}.html",
                mime="text/html",
                use_container_width=True,
            )

        with col3:
            pdf_data = _export_pdf_report(company_name, structured, insights)
            st.download_button(
                "📑 Download PDF Report",
                data=pdf_data,
                file_name=f"{company_name or 'report'}_report.pdf",
                mime="application/pdf",
                use_container_width=True,
            )


# ─── Presentation Mode ──────────────────────────────────────────────────────

def render_presentation_mode():
    st.title("🎯 Presentation Mode")
    st.markdown("Generate consulting presentation slides from an analysis.")

    if "structured" not in st.session_state:
        st.info(
            "No analysis loaded. Run an analysis in **Analysis Mode** first, or load from CRM Memory."
        )

        # Allow loading from CRM
        companies = memory_store.list_companies()
        if companies:
            st.markdown("**Or load from CRM:**")
            company_options = {
                f"{c['company_name']} ({c['company_id']})": c["company_id"]
                for c in companies
            }
            selected = st.selectbox("Select company", list(company_options.keys()))
            if st.button("Load"):
                record = memory_store.load_analysis(company_options[selected])
                if record:
                    st.session_state["structured"] = record["structured_data"]
                    st.session_state["insights"] = record["insights"]
                    st.session_state["mindmap"] = record["mindmap"]
                    st.session_state["company_name"] = record["company_name"]
                    st.rerun()
        return

    company_name = st.session_state.get("company_name", "Company")
    structured = st.session_state["structured"]
    insights = st.session_state["insights"]

    if st.button("🎨 Generate Presentation", type="primary"):
        if not os.getenv("OPENAI_API_KEY"):
            st.error("OpenAI API key is required.")
            return

        with st.spinner("Generating presentation..."):
            try:
                presentation = ai_engine.build_presentation(
                    structured, insights, company_name
                )
                st.session_state["presentation"] = presentation
            except Exception as e:
                st.error(f"Error: {e}")
                return

    if "presentation" in st.session_state:
        presentation = st.session_state["presentation"]
        slides = presentation.get("slides", [])

        st.markdown(f"## {presentation.get('title', 'Presentation')}")
        st.markdown("---")

        # Slide navigation
        if slides:
            slide_titles = [f"Slide {i+1}: {s.get('title', '')}" for i, s in enumerate(slides)]
            current_slide = st.select_slider("Navigate slides", options=range(len(slides)),
                                              format_func=lambda i: slide_titles[i])

            slide = slides[current_slide]

            # Slide card
            with st.container():
                st.markdown(
                    f"""
                    <div style='
                        background: linear-gradient(135deg, #1e3a5f 0%, #0d1b2a 100%);
                        border-radius: 12px;
                        padding: 2rem;
                        min-height: 300px;
                        border: 1px solid #2a4a7f;
                        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
                    '>
                        <h2 style='color: #4ECDC4; margin-bottom: 1rem;'>{slide.get("title", "")}</h2>
                        {"".join(f"<p style='color: #e0e0e0; margin: 0.5rem 0;'>• {item}</p>" for item in slide.get("content", []))}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            st.markdown("---")

            # Export
            md_content = presentation_builder.presentation_to_markdown(presentation)
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    "📄 Download as Markdown",
                    data=md_content.encode("utf-8"),
                    file_name=f"{company_name}_presentation.md",
                    mime="text/markdown",
                    use_container_width=True,
                )
            with col2:
                st.download_button(
                    "📄 Download as JSON",
                    data=_export_json(presentation, "presentation.json"),
                    file_name=f"{company_name}_presentation.json",
                    mime="application/json",
                    use_container_width=True,
                )


# ─── Concept Mode ───────────────────────────────────────────────────────────

def render_concept_mode():
    st.title("💡 Concept Mode")
    st.markdown(
        "Enter a business concept to get a structured explanation and mind map."
    )

    col1, col2 = st.columns([1, 2])

    with col1:
        concept = st.text_input(
            "Enter a concept",
            placeholder="e.g. Sales funnel, Value chain, Lean startup...",
        )
        run_btn = st.button("🧠 Analyze Concept", type="primary", use_container_width=True)

    with col2:
        if run_btn:
            if not concept.strip():
                st.warning("Please enter a concept.")
                return
            if not os.getenv("OPENAI_API_KEY"):
                st.error("OpenAI API key is required.")
                return

            orch = orchestrator.Orchestrator()
            with st.spinner(f"Analyzing concept: {concept}..."):
                try:
                    mindmap, concept_data = orch.run_concept(concept)
                    st.session_state["concept_mindmap"] = mindmap
                    st.session_state["concept_data"] = concept_data
                    st.session_state["concept_name"] = concept
                except Exception as e:
                    st.error(f"Error: {e}")
                    return

        if "concept_data" in st.session_state:
            concept_data = st.session_state["concept_data"]
            concept_mindmap = st.session_state["concept_mindmap"]

            tab1, tab2, tab3 = st.tabs(["📖 Explanation", "🗺️ Mind Map", "📥 Export"])

            with tab1:
                st.subheader(concept_data.get("concept", ""))

                st.markdown("### Definition")
                st.info(concept_data.get("definition", ""))

                components = concept_data.get("components", [])
                if components:
                    st.markdown("### Components")
                    for comp in components:
                        with st.expander(comp.get("name", "")):
                            st.write(comp.get("description", ""))
                            examples = comp.get("examples", [])
                            if examples:
                                st.markdown("**Examples:** " + ", ".join(examples))

                applications = concept_data.get("applications", [])
                if applications:
                    st.markdown("### Applications")
                    for app in applications:
                        st.markdown(
                            f"**{app.get('context', '')}**: {app.get('use_case', '')} "
                            f"*(Benefit: {app.get('benefit', '')})*"
                        )

                actions = concept_data.get("actions", [])
                if actions:
                    st.markdown("### Actions")
                    for action in actions:
                        st.markdown(f"✅ {action}")

                related = concept_data.get("related_concepts", [])
                if related:
                    st.markdown("### Related Concepts")
                    st.markdown(" · ".join(f"`{r}`" for r in related))

                metrics = concept_data.get("metrics", [])
                if metrics:
                    st.markdown("### Key Metrics")
                    for metric in metrics:
                        st.markdown(f"📊 {metric}")

            with tab2:
                st.subheader(f"Mind Map: {concept_mindmap.get('title', '')}")
                html = _render_mindmap_html(concept_mindmap)
                st.components.v1.html(html, height=600, scrolling=False)

            with tab3:
                st.download_button(
                    "📄 Download JSON",
                    data=_export_json(concept_data, "concept.json"),
                    file_name=f"{st.session_state.get('concept_name', 'concept')}.json",
                    mime="application/json",
                )


# ─── CRM Memory ─────────────────────────────────────────────────────────────

def render_crm_memory():
    st.title("📁 CRM Memory")
    st.markdown("View, load, and manage saved company analyses.")

    companies = memory_store.list_companies()

    if not companies:
        st.info("No analyses saved yet. Run an analysis to populate the CRM.")
        return

    st.markdown(f"**{len(companies)} company analyses stored**")

    for company in companies:
        with st.expander(
            f"🏢 {company['company_name']} · {company['company_id']} · {company['date'][:10]}"
        ):
            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button(
                    "📂 Load Analysis",
                    key=f"load_{company['company_id']}",
                    use_container_width=True,
                ):
                    record = memory_store.load_analysis(company["company_id"])
                    if record:
                        st.session_state["structured"] = record["structured_data"]
                        st.session_state["insights"] = record["insights"]
                        st.session_state["mindmap"] = record["mindmap"]
                        st.session_state["company_name"] = record["company_name"]
                        st.session_state["company_id"] = record["company_id"]
                        st.session_state["input_text"] = record.get("input", "")
                        st.success(f"Loaded '{record['company_name']}' — switch to Analysis Mode to view.")

            with col2:
                record = memory_store.load_analysis(company["company_id"])
                if record:
                    st.download_button(
                        "📄 Export JSON",
                        data=_export_json(record, "record.json"),
                        file_name=f"{company['company_id']}.json",
                        mime="application/json",
                        key=f"export_{company['company_id']}",
                        use_container_width=True,
                    )

            with col3:
                if st.button(
                    "🗑️ Delete",
                    key=f"delete_{company['company_id']}",
                    use_container_width=True,
                ):
                    memory_store.delete_analysis(company["company_id"])
                    st.success("Deleted.")
                    st.rerun()


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    mode = render_sidebar()

    if mode == "📊 Analysis Mode":
        render_analysis_mode()
    elif mode == "🎯 Presentation Mode":
        render_presentation_mode()
    elif mode == "💡 Concept Mode":
        render_concept_mode()
    elif mode == "📁 CRM Memory":
        render_crm_memory()


if __name__ == "__main__":
    main()
