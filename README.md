# 🧠 AI Mind Map CRM

A Python (Streamlit) application that converts documents and concepts into structured mind maps, generates AI-driven multi-agent insights, supports consulting presentations, and stores analyses as a CRM memory system.

## Features

- **📊 Analysis Mode** — Upload PDF/TXT/Markdown or paste text to generate structured mind maps with role-based AI insights
- **🎯 Presentation Mode** — Generate slide-ready consulting presentations from any analysis
- **💡 Concept Mode** — Enter any business concept (e.g. "Sales funnel") for a structured explanation and mind map
- **📁 CRM Memory** — Save, load, and manage all company analyses with export support

## Architecture

```
app/
  main.py              # Streamlit entry point (all modes)
  ui/                  # UI components

core/
  parser.py            # Input normalization
  ai_engine.py         # OpenAI-powered structuring
  mindmap_builder.py   # JSON → graph nodes/edges
  orchestrator.py      # Pipeline coordinator
  presentation_builder.py  # Slide generation helpers

agents/
  sales_agent.py       # Sales insights
  finance_agent.py     # Finance insights
  ops_agent.py         # Operations insights
  manager_agent.py     # Management insights

models/prompts/        # Prompt templates
data/memory/           # CRM storage (JSON files)
utils/
  file_loader.py       # PDF/TXT/MD parsing
  text_cleaner.py      # Text normalization
  memory_store.py      # CRM read/write
outputs/
  mindmaps/            # Exported HTML mind maps
  reports/             # Exported PDF reports
```

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API key

```bash
cp .env.example .env
# Edit .env and set your OPENAI_API_KEY
```

### 3. Run the app

```bash
streamlit run app/main.py
```

The app will open at `http://localhost:8501`.

## Usage

### Analysis Mode
1. Select "📊 Analysis Mode" in the sidebar
2. Enter a Company Name and Company ID
3. Paste text or upload a PDF/TXT/Markdown file
4. Click **Run Analysis** to generate:
   - Interactive mind map visualization
   - Sales, Finance, Operations, and Management insights
   - Structured JSON data
5. Export results as JSON, HTML mind map, or PDF report

### Presentation Mode
1. Run an analysis first (or load one from CRM Memory)
2. Switch to "🎯 Presentation Mode"
3. Click **Generate Presentation** to create consulting slides
4. Navigate slides and export as Markdown or JSON

### Concept Mode
1. Select "💡 Concept Mode"
2. Enter any business concept (e.g. "Value chain", "Lean startup")
3. Click **Analyze Concept** to get:
   - Structured definition, components, applications
   - Interactive mind map
   - Export as JSON

### CRM Memory
- All analyses are auto-saved when a Company ID is provided
- Load past analyses from the "📁 CRM Memory" tab
- Export or delete individual company records

## CRM Data Format

Analyses are stored as JSON files in `data/memory/`:

```json
{
  "company_id": "acme_corp",
  "company_name": "Acme Corp",
  "date": "2024-01-15T10:30:00",
  "input": "...",
  "structured_data": {},
  "mindmap": {},
  "insights": {}
}
```

## Requirements

- Python 3.9+
- OpenAI API key (GPT-4o-mini or better)
- See `requirements.txt` for all dependencies
