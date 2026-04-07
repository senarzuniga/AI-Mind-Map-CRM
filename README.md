# 🧠 AI Mind Map CRM

A lightweight, AI-assisted Customer Relationship Management app with an interactive D3.js mind-map visualization of contacts, deals, and tags.

## Features

| Area | Details |
|---|---|
| **Dashboard** | KPI cards, deal-pipeline funnel, top-contact AI scores, activity feed, AI insights |
| **Contacts** | Full CRUD, search/filter, tag management, activity log, AI score |
| **Deals** | Kanban pipeline across 5 stages, linked contacts, value & probability tracking |
| **Mind Map** | Interactive D3 force-directed graph of contacts ↔ deals ↔ tags |
| **AI Insights** | Rule-based scoring engine + actionable recommendations via REST API |

## Tech Stack

- **Backend** – Python 3.9+ / Flask 3 / SQLAlchemy / SQLite
- **Frontend** – Vanilla HTML/CSS/JS + D3.js v7 (no build tools required)

## Quick Start

```bash
# 1. Clone & enter the directory
git clone https://github.com/senarzuniga/AI-Mind-Map-CRM.git
cd AI-Mind-Map-CRM

# 2. Create and activate a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app (demo data is seeded automatically on first start)
python app.py
```

Open **http://localhost:5000** in your browser.

## Project Structure

```
AI-Mind-Map-CRM/
├── app.py                  # Flask routes & AI scoring logic
├── models.py               # SQLAlchemy models (Contact, Deal, Activity, Tag)
├── database.py             # DB init & demo seed data
├── requirements.txt
├── instance/
│   └── crm.db              # SQLite database (auto-created)
├── templates/
│   ├── base.html
│   ├── index.html          # Dashboard
│   ├── contacts.html
│   ├── contact_detail.html
│   ├── contact_form.html
│   ├── deals.html
│   ├── deal_form.html
│   └── mindmap.html        # D3 mind map
└── static/
    ├── css/style.css
    └── js/
        ├── app.js
        └── mindmap.js      # D3 force-directed graph
```

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` | `dev-secret-key-change-in-production` | Flask session secret |
| `PORT` | `5000` | Port to listen on |
