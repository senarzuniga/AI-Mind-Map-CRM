from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_db(app):
    """Initialise DB and create tables."""
    db.init_app(app)
    with app.app_context():
        db.create_all()
        _seed_if_empty()


def _seed_if_empty():
    """Populate the database with demo data on first run."""
    from models import Tag, Contact, Deal, Activity
    from datetime import date, datetime

    if Tag.query.count() > 0:
        return  # already seeded

    # --- Tags ---
    tags = {
        "VIP": Tag(name="VIP", color="#f59e0b"),
        "Tech": Tag(name="Tech", color="#6366f1"),
        "Retail": Tag(name="Retail", color="#10b981"),
        "Finance": Tag(name="Finance", color="#3b82f6"),
        "Startup": Tag(name="Startup", color="#ec4899"),
    }
    for t in tags.values():
        db.session.add(t)

    # --- Contacts ---
    contacts = [
        Contact(
            name="Alice Chen",
            company="NovaTech",
            email="alice@novatech.io",
            phone="+1 555-0101",
            status="customer",
            ai_score=87.5,
            notes="Key decision maker for AI projects.",
            tags=[tags["VIP"], tags["Tech"]],
        ),
        Contact(
            name="Bob Martinez",
            company="RetailPro",
            email="bob@retailpro.com",
            phone="+1 555-0202",
            status="prospect",
            ai_score=64.0,
            notes="Interested in automation tools.",
            tags=[tags["Retail"]],
        ),
        Contact(
            name="Carol White",
            company="FinanceFirst",
            email="carol@financefirst.com",
            phone="+1 555-0303",
            status="lead",
            ai_score=42.0,
            notes="Met at FinTech Summit 2024.",
            tags=[tags["Finance"]],
        ),
        Contact(
            name="David Kim",
            company="LoopStart",
            email="david@loopstart.io",
            phone="+1 555-0404",
            status="customer",
            ai_score=91.0,
            notes="Champion user – drives referrals.",
            tags=[tags["Startup"], tags["Tech"], tags["VIP"]],
        ),
        Contact(
            name="Eva Rossi",
            company="MegaMart",
            email="eva@megamart.com",
            phone="+1 555-0505",
            status="prospect",
            ai_score=55.5,
            notes="Evaluating solution alongside two competitors.",
            tags=[tags["Retail"]],
        ),
        Contact(
            name="Frank Osei",
            company="BankCore",
            email="frank@bankcore.com",
            phone="+1 555-0606",
            status="lead",
            ai_score=38.0,
            notes="Warm intro from David Kim.",
            tags=[tags["Finance"]],
        ),
    ]
    for c in contacts:
        db.session.add(c)

    db.session.flush()  # get IDs

    # --- Deals ---
    deals = [
        Deal(
            title="NovaTech Enterprise License",
            value=120000.0,
            stage="negotiation",
            probability=75,
            close_date=date(2026, 6, 30),
            notes="Awaiting procurement sign-off.",
            contacts=[contacts[0]],
        ),
        Deal(
            title="RetailPro Automation Suite",
            value=45000.0,
            stage="proposal",
            probability=50,
            close_date=date(2026, 7, 15),
            notes="Demo scheduled next week.",
            contacts=[contacts[1], contacts[4]],
        ),
        Deal(
            title="LoopStart Seed Package",
            value=18000.0,
            stage="closed_won",
            probability=100,
            close_date=date(2026, 3, 1),
            notes="Signed and onboarded.",
            contacts=[contacts[3]],
        ),
        Deal(
            title="BankCore Pilot",
            value=25000.0,
            stage="discovery",
            probability=20,
            close_date=date(2026, 9, 1),
            notes="Initial discovery call done.",
            contacts=[contacts[5], contacts[2]],
        ),
    ]
    for d in deals:
        db.session.add(d)

    db.session.flush()

    # --- Activities ---
    activities = [
        Activity(contact_id=contacts[0].id, kind="meeting", description="Signed enterprise agreement.", created_at=datetime(2026, 3, 10, 10, 0)),
        Activity(contact_id=contacts[0].id, kind="email", description="Sent onboarding materials.", created_at=datetime(2026, 3, 12, 9, 30)),
        Activity(contact_id=contacts[1].id, kind="call", description="Intro call – showed high interest.", created_at=datetime(2026, 3, 20, 14, 0)),
        Activity(contact_id=contacts[1].id, kind="email", description="Sent proposal PDF.", created_at=datetime(2026, 3, 25, 11, 0)),
        Activity(contact_id=contacts[2].id, kind="note", description="Collected business card at FinTech Summit.", created_at=datetime(2026, 2, 15, 17, 0)),
        Activity(contact_id=contacts[3].id, kind="meeting", description="Quarterly review – very satisfied.", created_at=datetime(2026, 4, 1, 10, 0)),
        Activity(contact_id=contacts[4].id, kind="call", description="Discussed pricing options.", created_at=datetime(2026, 3, 28, 15, 30)),
        Activity(contact_id=contacts[5].id, kind="email", description="Follow-up after intro call.", created_at=datetime(2026, 4, 2, 9, 0)),
    ]
    for a in activities:
        db.session.add(a)

    db.session.commit()
