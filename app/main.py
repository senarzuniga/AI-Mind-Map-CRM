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
from utils.text_cleaner import truncate_text

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
    """Render the mind map as a consulting-grade interactive HTML using vis.js."""
    import json as _json

    # ── Node visual config ─────────────────────────────────────────────────
    NODE_CFG = {
        "root":        {"emoji": "🧠", "bg": "#6D28D9", "border": "#4C1D95", "size": 38, "fs": 16, "shape": "box"},
        "topic":       {"emoji": "🧭", "bg": "#1D4ED8", "border": "#1E3A8A", "size": 28, "fs": 13, "shape": "ellipse"},
        "component":   {"emoji": "📊", "bg": "#0E7490", "border": "#164E63", "size": 20, "fs": 11, "shape": "ellipse"},
        "action":      {"emoji": "🎯", "bg": "#15803D", "border": "#14532D", "size": 16, "fs": 10, "shape": "ellipse"},
        "risk":        {"emoji": "⚠️",  "bg": "#B91C1C", "border": "#7F1D1D", "size": 16, "fs": 10, "shape": "ellipse"},
        "metric":      {"emoji": "📈", "bg": "#7C3AED", "border": "#4C1D95", "size": 16, "fs": 10, "shape": "ellipse"},
        "insight":     {"emoji": "💡", "bg": "#B45309", "border": "#78350F", "size": 16, "fs": 10, "shape": "ellipse"},
        "opportunity": {"emoji": "🚀", "bg": "#047857", "border": "#064E3B", "size": 16, "fs": 10, "shape": "ellipse"},
        "definition":  {"emoji": "📖", "bg": "#1D4ED8", "border": "#1E3A8A", "size": 26, "fs": 12, "shape": "ellipse"},
        "applications":{"emoji": "🔧", "bg": "#0E7490", "border": "#164E63", "size": 26, "fs": 12, "shape": "ellipse"},
        "components":  {"emoji": "📦", "bg": "#1D4ED8", "border": "#1E3A8A", "size": 26, "fs": 12, "shape": "ellipse"},
        "actions":     {"emoji": "✅", "bg": "#15803D", "border": "#14532D", "size": 26, "fs": 12, "shape": "ellipse"},
    }
    DEFAULT_CFG = {"emoji": "🔹", "bg": "#334155", "border": "#1E293B", "size": 14, "fs": 10, "shape": "ellipse"}

    # ── Edge visual config by (src_level, tgt_level) ───────────────────────
    EDGE_CFG = {
        (0, 1): {"color": "#818CF8", "width": 3, "dashes": False},
        (1, 2): {"color": "#FCD34D", "width": 2, "dashes": False},
        (2, 3): {"color": "#6EE7B7", "width": 1.5, "dashes": False},
        (3, 4): {"color": "#94A3B8", "width": 1.5, "dashes": False},
    }
    DEFAULT_EDGE_CFG = {"color": "#475569", "width": 1, "dashes": False}

    # Target node type → edge colour/dashes override
    TTYPE_EDGE_OVERRIDE = {
        "risk":        {"color": "#FCA5A5", "dashes": True},
        "metric":      {"color": "#C4B5FD", "dashes": False},
        "insight":     {"color": "#FDE68A", "dashes": False},
        "opportunity": {"color": "#6EE7B7", "dashes": False},
    }

    node_level_map = {n["id"]: n.get("level", 0) for n in mindmap.get("nodes", [])}
    node_type_map  = {n["id"]: n.get("type", "action") for n in mindmap.get("nodes", [])}

    nodes_data = []
    for node in mindmap.get("nodes", []):
        ntype = node.get("type", "action")
        cfg = NODE_CFG.get(ntype, DEFAULT_CFG)
        emoji = node.get("emoji") or cfg["emoji"]
        bg    = node.get("color") or cfg["bg"]
        label = node.get("label", "")
        display = (label[:24] + "\u2026") if len(label) > 24 else label
        tooltip = (
            "<b>" + emoji + " " + label + "</b>"
            + "<br><span style='color:#94A3B8'>Type: " + ntype
            + " | Level: " + str(node.get("level", 0)) + "</span>"
        )
        nodes_data.append({
            "id": node["id"],
            "label": emoji + "\n" + display,
            "title": tooltip,
            "color": {
                "background": bg,
                "border": cfg["border"],
                "highlight": {"background": "#FCD34D", "border": "#F59E0B"},
                "hover":     {"background": "#E2E8F0", "border": "#94A3B8"},
            },
            "font": {
                "size": cfg["fs"], "color": "#F1F5F9",
                "face": "Segoe UI, Arial, sans-serif",
                "multi": True,
            },
            "size": cfg["size"],
            "shape": cfg["shape"],
            "borderWidth": 2,
            "borderWidthSelected": 3,
            "shadow": {"enabled": True, "color": "rgba(0,0,0,0.4)", "size": 8, "x": 2, "y": 2},
            "margin": 8,
        })

    edges_data = []
    for edge in mindmap.get("edges", []):
        src_id = edge["source"]
        tgt_id = edge["target"]
        src_level = node_level_map.get(src_id, 0)
        tgt_level = node_level_map.get(tgt_id, src_level + 1)
        tgt_type  = node_type_map.get(tgt_id, "action")

        ecfg = EDGE_CFG.get((src_level, tgt_level), DEFAULT_EDGE_CFG)
        e_color  = ecfg["color"]
        e_width  = ecfg["width"]
        e_dashes = ecfg["dashes"]

        # Apply per-target-type colour/dash overrides
        if tgt_type in TTYPE_EDGE_OVERRIDE:
            override = TTYPE_EDGE_OVERRIDE[tgt_type]
            e_color  = override["color"]
            e_dashes = override["dashes"]

        # Use edge emoji/label if already enriched, else fall back to type emoji
        e_emoji = edge.get("emoji", "")
        e_label_text = edge.get("label", "")
        e_display = (e_emoji + " " + e_label_text).strip() if e_emoji else e_label_text

        edges_data.append({
            "from": src_id,
            "to":   tgt_id,
            "label": e_display,
            "title": e_label_text or e_emoji or "",
            "color": {
                "color": e_color,
                "highlight": "#FCD34D",
                "hover": "#FCD34D",
                "opacity": 0.9,
            },
            "width": e_width,
            "dashes": e_dashes,
            "arrows": {"to": {"enabled": True, "scaleFactor": 0.8, "type": "arrow"}},
            "font": {"size": 9, "color": "#94A3B8", "strokeWidth": 0, "align": "middle"},
            "smooth": {"enabled": True, "type": "curvedCW", "roundness": 0.1},
        })

    nodes_json = _json.dumps(nodes_data, ensure_ascii=False)
    edges_json = _json.dumps(edges_data, ensure_ascii=False)
    title      = mindmap.get("title", "Mind Map")
    title_safe = title.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

    legend_items = [
        ("#6D28D9", "🧠", "Root"),
        ("#1D4ED8", "🧭", "Topic"),
        ("#0E7490", "📊", "Component"),
        ("#15803D", "🎯", "Action"),
        ("#B91C1C", "⚠️",  "Risk"),
        ("#7C3AED", "📈", "Metric"),
        ("#B45309", "💡", "Insight"),
        ("#047857", "🚀", "Opportunity"),
    ]
    legend_html = "".join(
        "<div class='li'>"
        "<span class='dot' style='background:" + c + "'></span>"
        + em + " " + lbl + "</div>"
        for c, em, lbl in legend_items
    )

    # Build the full HTML (uses string replacement to avoid f-string brace conflicts)
    html = (
        "<!DOCTYPE html>\n"
        "<html lang='en'>\n"
        "<head><meta charset='utf-8'>\n"
        "<script src='https://cdn.jsdelivr.net/npm/vis-network@9.1.6/dist/vis-network.min.js'></script>\n"
        "<link  href='https://cdn.jsdelivr.net/npm/vis-network@9.1.6/dist/vis-network.min.css' rel='stylesheet'>\n"
        "<style>\n"
        "  *{box-sizing:border-box;margin:0;padding:0}\n"
        "  body{background:#0F172A;font-family:'Segoe UI',Arial,sans-serif;overflow:hidden}\n"
        "  #net{width:100%;height:740px}\n"
        "  #ctrl{position:absolute;top:10px;right:10px;z-index:100;display:flex;gap:6px;flex-wrap:wrap;justify-content:flex-end}\n"
        "  #titlebar{position:absolute;top:10px;left:10px;z-index:100;color:#E2E8F0;font-size:13px;"
        "font-weight:600;background:rgba(30,41,59,0.92);padding:6px 14px;border-radius:8px;"
        "border:1px solid #334155;max-width:55%}\n"
        "  .btn{background:rgba(30,41,59,0.92);color:#E2E8F0;border:1px solid #334155;"
        "border-radius:8px;padding:6px 13px;font-size:12px;cursor:pointer;transition:all .2s}\n"
        "  .btn:hover{background:#1E293B;border-color:#6366F1;color:#A5B4FC}\n"
        "  #legend{position:absolute;bottom:10px;left:10px;z-index:100;"
        "background:rgba(15,23,42,0.95);border:1px solid #334155;border-radius:10px;"
        "padding:10px 14px;font-size:11px;color:#CBD5E1;min-width:140px}\n"
        "  #legend h4{color:#94A3B8;margin-bottom:6px;font-size:10px;text-transform:uppercase;letter-spacing:1px}\n"
        "  .li{display:flex;align-items:center;gap:6px;margin-bottom:3px}\n"
        "  .dot{width:9px;height:9px;border-radius:50%;display:inline-block;flex-shrink:0}\n"
        "  body.pres #legend,body.pres #ctrl,body.pres #titlebar{display:none}\n"
        "  body.pres #net{background:#000;height:100vh}\n"
        "  body.pres{overflow:hidden}\n"
        "</style></head>\n"
        "<body>\n"
        "<div id='titlebar'>🧠 __TITLE__</div>\n"
        "<div id='ctrl'>\n"
        "  <button class='btn' onclick='network.fit()'>⊡ Fit</button>\n"
        "  <button class='btn' onclick='toggleDir()'>⇄ Direction</button>\n"
        "  <button class='btn' id='pb' onclick='togglePres()'>🎬 Present</button>\n"
        "  <button class='btn' onclick='toggleFS()'>⛶ Fullscreen</button>\n"
        "</div>\n"
        "<div id='legend'><h4>Legend</h4>__LEGEND__</div>\n"
        "<div id='net'></div>\n"
        "<script>\n"
        "var nodesData=__NODES__;\n"
        "var edgesData=__EDGES__;\n"
        "var nodes=new vis.DataSet(nodesData);\n"
        "var edges=new vis.DataSet(edgesData);\n"
        "var container=document.getElementById('net');\n"
        "var dir='LR';\n"
        "var options={\n"
        "  layout:{hierarchical:{\n"
        "    enabled:true,direction:dir,sortMethod:'directed',\n"
        "    nodeSpacing:160,levelSeparation:220,treeSpacing:200,\n"
        "    blockShifting:true,edgeMinimization:true,parentCentralization:true\n"
        "  }},\n"
        "  physics:{enabled:false},\n"
        "  interaction:{hover:true,tooltipDelay:80,zoomView:true,dragView:true,\n"
        "               navigationButtons:false,keyboard:{enabled:true}},\n"
        "  nodes:{borderWidth:2,borderWidthSelected:3},\n"
        "  edges:{smooth:{type:'curvedCW',roundness:0.12},selectionWidth:3}\n"
        "};\n"
        "var network=new vis.Network(container,{nodes:nodes,edges:edges},options);\n"
        "network.once('stabilized',function(){network.fit();});\n"
        "function toggleDir(){\n"
        "  dir=dir==='LR'?'UD':'LR';\n"
        "  network.setOptions({layout:{hierarchical:{direction:dir}}});\n"
        "  setTimeout(function(){network.fit();},400);\n"
        "}\n"
        "function togglePres(){\n"
        "  document.body.classList.toggle('pres');\n"
        "  var btn=document.getElementById('pb');\n"
        "  btn.textContent=document.body.classList.contains('pres')?'✕ Exit':'🎬 Present';\n"
        "  if(document.body.classList.contains('pres'))network.fit();\n"
        "}\n"
        "function toggleFS(){\n"
        "  var el=document.documentElement;\n"
        "  if(!document.fullscreenElement){\n"
        "    el.requestFullscreen&&el.requestFullscreen();\n"
        "  }else{\n"
        "    document.exitFullscreen&&document.exitFullscreen();\n"
        "  }\n"
        "}\n"
        "</script></body></html>"
    )

    html = html.replace("__TITLE__",  title_safe)
    html = html.replace("__LEGEND__", legend_html)
    html = html.replace("__NODES__",  nodes_json)
    html = html.replace("__EDGES__",  edges_json)
    return html


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
                        st.text(truncate_text(input_text, TEXT_PREVIEW_LENGTH))
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
        st.components.v1.html(html, height=750, scrolling=False)

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
                st.components.v1.html(html, height=750, scrolling=False)

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
