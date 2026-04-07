"""AI Mind Map CRM – Flask application."""

import math
import os
from datetime import datetime, date

from flask import Flask, render_template, request, redirect, url_for, jsonify, flash

from database import db, init_db
from models import Contact, Deal, Activity, Tag, deal_contacts

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///crm.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
_secret_key = os.environ.get("SECRET_KEY")
if not _secret_key:
    if os.environ.get("FLASK_ENV") == "production":
        raise RuntimeError("SECRET_KEY environment variable must be set in production.")
    _secret_key = "dev-secret-key-change-in-production"
app.secret_key = _secret_key

init_db(app)

# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

STAGE_ORDER = ["discovery", "proposal", "negotiation", "closed_won", "closed_lost"]
STATUS_COLORS = {
    "lead": "#94a3b8",
    "prospect": "#f59e0b",
    "customer": "#10b981",
    "churned": "#ef4444",
}


def _ai_score(contact):
    """
    Simple rule-based AI scoring:
      - Activity count drives 50 % of score
      - Deal involvement drives 30 %
      - Status drives 20 %
    """
    activity_count = contact.activities.count()
    deal_count = len(contact.deals)
    status_base = {"customer": 100, "prospect": 60, "lead": 30, "churned": 10}.get(contact.status, 0)

    raw = (min(activity_count, 10) / 10) * 50 + (min(deal_count, 3) / 3) * 30 + (status_base / 100) * 20
    return round(raw, 1)


def _recalculate_scores():
    for contact in Contact.query.all():
        contact.ai_score = _ai_score(contact)
    db.session.commit()


# ──────────────────────────────────────────────────────────────────────────────
# Dashboard
# ──────────────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    _recalculate_scores()
    total_contacts = Contact.query.count()
    total_deals = Deal.query.count()
    pipeline_value = sum(
        d.value * d.probability / 100
        for d in Deal.query.filter(Deal.stage.notin_(["closed_won", "closed_lost"])).all()
    )
    won_value = sum(d.value for d in Deal.query.filter_by(stage="closed_won").all())
    recent_activities = Activity.query.order_by(Activity.created_at.desc()).limit(8).all()
    top_contacts = Contact.query.order_by(Contact.ai_score.desc()).limit(5).all()

    stage_counts = {}
    for s in STAGE_ORDER:
        stage_counts[s] = Deal.query.filter_by(stage=s).count()

    return render_template(
        "index.html",
        total_contacts=total_contacts,
        total_deals=total_deals,
        pipeline_value=pipeline_value,
        won_value=won_value,
        recent_activities=recent_activities,
        top_contacts=top_contacts,
        stage_counts=stage_counts,
        STATUS_COLORS=STATUS_COLORS,
    )


# ──────────────────────────────────────────────────────────────────────────────
# Contacts
# ──────────────────────────────────────────────────────────────────────────────

@app.route("/contacts")
def contacts():
    q = request.args.get("q", "").strip()
    status_filter = request.args.get("status", "")
    query = Contact.query
    if q:
        query = query.filter(
            db.or_(Contact.name.ilike(f"%{q}%"), Contact.company.ilike(f"%{q}%"), Contact.email.ilike(f"%{q}%"))
        )
    if status_filter:
        query = query.filter_by(status=status_filter)
    all_contacts = query.order_by(Contact.ai_score.desc()).all()
    return render_template("contacts.html", contacts=all_contacts, q=q, status_filter=status_filter, STATUS_COLORS=STATUS_COLORS)


@app.route("/contacts/new", methods=["GET", "POST"])
def new_contact():
    all_tags = Tag.query.order_by(Tag.name).all()
    if request.method == "POST":
        tag_ids = request.form.getlist("tags")
        c = Contact(
            name=request.form["name"],
            company=request.form.get("company"),
            email=request.form.get("email"),
            phone=request.form.get("phone"),
            status=request.form.get("status", "lead"),
            notes=request.form.get("notes"),
        )
        c.tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()
        c.ai_score = _ai_score(c)
        db.session.add(c)
        db.session.commit()
        flash(f"Contact '{c.name}' created.", "success")
        return redirect(url_for("contact_detail", contact_id=c.id))
    return render_template("contact_form.html", contact=None, all_tags=all_tags, title="New Contact")


@app.route("/contacts/<int:contact_id>")
def contact_detail(contact_id):
    contact = Contact.query.get_or_404(contact_id)
    activities = contact.activities.order_by(Activity.created_at.desc()).all()
    return render_template("contact_detail.html", contact=contact, activities=activities, STATUS_COLORS=STATUS_COLORS)


@app.route("/contacts/<int:contact_id>/edit", methods=["GET", "POST"])
def edit_contact(contact_id):
    contact = Contact.query.get_or_404(contact_id)
    all_tags = Tag.query.order_by(Tag.name).all()
    if request.method == "POST":
        contact.name = request.form["name"]
        contact.company = request.form.get("company")
        contact.email = request.form.get("email")
        contact.phone = request.form.get("phone")
        contact.status = request.form.get("status", "lead")
        contact.notes = request.form.get("notes")
        tag_ids = request.form.getlist("tags")
        contact.tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()
        contact.ai_score = _ai_score(contact)
        db.session.commit()
        flash(f"Contact '{contact.name}' updated.", "success")
        return redirect(url_for("contact_detail", contact_id=contact.id))
    return render_template("contact_form.html", contact=contact, all_tags=all_tags, title="Edit Contact")


@app.route("/contacts/<int:contact_id>/delete", methods=["POST"])
def delete_contact(contact_id):
    contact = Contact.query.get_or_404(contact_id)
    name = contact.name
    db.session.delete(contact)
    db.session.commit()
    flash(f"Contact '{name}' deleted.", "info")
    return redirect(url_for("contacts"))


@app.route("/contacts/<int:contact_id>/activity", methods=["POST"])
def add_activity(contact_id):
    contact = Contact.query.get_or_404(contact_id)
    a = Activity(
        contact_id=contact_id,
        kind=request.form.get("kind", "note"),
        description=request.form["description"],
    )
    db.session.add(a)
    contact.ai_score = _ai_score(contact)
    db.session.commit()
    flash("Activity logged.", "success")
    return redirect(url_for("contact_detail", contact_id=contact_id))


# ──────────────────────────────────────────────────────────────────────────────
# Deals
# ──────────────────────────────────────────────────────────────────────────────

@app.route("/deals")
def deals():
    all_deals = Deal.query.order_by(Deal.stage, Deal.value.desc()).all()
    pipeline = {s: [] for s in STAGE_ORDER}
    for d in all_deals:
        pipeline[d.stage].append(d)
    return render_template("deals.html", pipeline=pipeline, STAGE_ORDER=STAGE_ORDER)


@app.route("/deals/new", methods=["GET", "POST"])
def new_deal():
    all_contacts = Contact.query.order_by(Contact.name).all()
    if request.method == "POST":
        close_date_str = request.form.get("close_date")
        close_date = datetime.strptime(close_date_str, "%Y-%m-%d").date() if close_date_str else None
        contact_ids = request.form.getlist("contacts")
        d = Deal(
            title=request.form["title"],
            value=float(request.form.get("value", 0)),
            stage=request.form.get("stage", "discovery"),
            probability=int(request.form.get("probability", 20)),
            close_date=close_date,
            notes=request.form.get("notes"),
        )
        d.contacts = Contact.query.filter(Contact.id.in_(contact_ids)).all()
        db.session.add(d)
        db.session.commit()
        flash(f"Deal '{d.title}' created.", "success")
        return redirect(url_for("deals"))
    return render_template("deal_form.html", deal=None, all_contacts=all_contacts, STAGE_ORDER=STAGE_ORDER, title="New Deal")


@app.route("/deals/<int:deal_id>/edit", methods=["GET", "POST"])
def edit_deal(deal_id):
    deal = Deal.query.get_or_404(deal_id)
    all_contacts = Contact.query.order_by(Contact.name).all()
    if request.method == "POST":
        close_date_str = request.form.get("close_date")
        deal.title = request.form["title"]
        deal.value = float(request.form.get("value", 0))
        deal.stage = request.form.get("stage", "discovery")
        deal.probability = int(request.form.get("probability", 20))
        deal.close_date = datetime.strptime(close_date_str, "%Y-%m-%d").date() if close_date_str else None
        deal.notes = request.form.get("notes")
        contact_ids = request.form.getlist("contacts")
        deal.contacts = Contact.query.filter(Contact.id.in_(contact_ids)).all()
        db.session.commit()
        flash(f"Deal '{deal.title}' updated.", "success")
        return redirect(url_for("deals"))
    return render_template("deal_form.html", deal=deal, all_contacts=all_contacts, STAGE_ORDER=STAGE_ORDER, title="Edit Deal")


@app.route("/deals/<int:deal_id>/delete", methods=["POST"])
def delete_deal(deal_id):
    deal = Deal.query.get_or_404(deal_id)
    title = deal.title
    db.session.delete(deal)
    db.session.commit()
    flash(f"Deal '{title}' deleted.", "info")
    return redirect(url_for("deals"))


# ──────────────────────────────────────────────────────────────────────────────
# Mind Map
# ──────────────────────────────────────────────────────────────────────────────

@app.route("/mindmap")
def mindmap():
    return render_template("mindmap.html")


@app.route("/api/mindmap-data")
def mindmap_data():
    """Return graph data (nodes + links) for D3 force simulation."""
    nodes = []
    links = []

    # Central hub node
    nodes.append({"id": "hub", "label": "CRM Hub", "type": "hub", "group": 0})

    # Contact nodes
    for c in Contact.query.all():
        nodes.append({
            "id": f"c{c.id}",
            "label": c.name,
            "sub": c.company or "",
            "type": "contact",
            "status": c.status,
            "score": c.ai_score,
            "group": 1,
        })
        links.append({"source": "hub", "target": f"c{c.id}", "value": 1})

    # Deal nodes + edges to contacts
    for d in Deal.query.all():
        nodes.append({
            "id": f"d{d.id}",
            "label": d.title,
            "sub": f"${d.value:,.0f}",
            "type": "deal",
            "stage": d.stage,
            "group": 2,
        })
        for c in d.contacts:
            links.append({"source": f"c{c.id}", "target": f"d{d.id}", "value": 2})

    # Tag nodes + edges to contacts
    for tag in Tag.query.all():
        if tag.contacts:
            nodes.append({
                "id": f"t{tag.id}",
                "label": f"#{tag.name}",
                "type": "tag",
                "color": tag.color,
                "group": 3,
            })
            for c in tag.contacts:
                links.append({"source": f"c{c.id}", "target": f"t{tag.id}", "value": 1})

    return jsonify({"nodes": nodes, "links": links})


# ──────────────────────────────────────────────────────────────────────────────
# AI Insights API
# ──────────────────────────────────────────────────────────────────────────────

@app.route("/api/ai-insights")
def ai_insights():
    """Return AI-generated insights for the dashboard."""
    _recalculate_scores()

    contacts = Contact.query.order_by(Contact.ai_score.desc()).all()
    deals = Deal.query.all()

    insights = []

    # Top contact suggestion
    if contacts:
        top = contacts[0]
        insights.append({
            "icon": "⭐",
            "text": f"<strong>{top.name}</strong> has the highest AI score ({top.ai_score}). Prioritise follow-up.",
        })

    # Stale prospects
    stale = [
        c for c in contacts
        if c.status == "prospect" and c.activities.count() == 0
    ]
    if stale:
        names = ", ".join(c.name for c in stale[:3])
        insights.append({
            "icon": "⚠️",
            "text": f"Prospects with no activity: <strong>{names}</strong>. Schedule a touch-point.",
        })

    # High-value deals near closing
    near_close = [
        d for d in deals
        if d.stage == "negotiation" and d.probability >= 70
    ]
    if near_close:
        d = near_close[0]
        insights.append({
            "icon": "💰",
            "text": f"Deal <strong>{d.title}</strong> (${d.value:,.0f}) is {d.probability}% likely to close. Push to finish.",
        })

    # Referral opportunity
    customers = [c for c in contacts if c.status == "customer"]
    leads = [c for c in contacts if c.status == "lead"]
    if customers and leads:
        insights.append({
            "icon": "🔗",
            "text": f"You have {len(customers)} customers who could refer {len(leads)} open leads. Consider a referral campaign.",
        })

    return jsonify({"insights": insights})


# ──────────────────────────────────────────────────────────────────────────────
# Run
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "127.0.0.1")
    app.run(host=host, port=port, debug=False)
