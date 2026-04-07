from datetime import datetime
from database import db

# Association table for Contact <-> Tag many-to-many
contact_tags = db.Table(
    "contact_tags",
    db.Column("contact_id", db.Integer, db.ForeignKey("contact.id"), primary_key=True),
    db.Column("tag_id", db.Integer, db.ForeignKey("tag.id"), primary_key=True),
)

# Association table for Deal <-> Contact many-to-many
deal_contacts = db.Table(
    "deal_contacts",
    db.Column("deal_id", db.Integer, db.ForeignKey("deal.id"), primary_key=True),
    db.Column("contact_id", db.Integer, db.ForeignKey("contact.id"), primary_key=True),
)


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    color = db.Column(db.String(7), default="#6366f1")

    def to_dict(self):
        return {"id": self.id, "name": self.name, "color": self.color}


class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    company = db.Column(db.String(120))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(30))
    status = db.Column(db.String(20), default="lead")  # lead | prospect | customer | churned
    ai_score = db.Column(db.Float, default=0.0)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    tags = db.relationship("Tag", secondary=contact_tags, backref="contacts", lazy="subquery")
    activities = db.relationship("Activity", backref="contact", lazy="dynamic", cascade="all, delete-orphan")
    deals = db.relationship("Deal", secondary=deal_contacts, back_populates="contacts")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "company": self.company,
            "email": self.email,
            "phone": self.phone,
            "status": self.status,
            "ai_score": round(self.ai_score, 1),
            "notes": self.notes,
            "tags": [t.to_dict() for t in self.tags],
            "created_at": self.created_at.strftime("%Y-%m-%d"),
        }


class Deal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    value = db.Column(db.Float, default=0.0)
    stage = db.Column(db.String(30), default="discovery")  # discovery | proposal | negotiation | closed_won | closed_lost
    probability = db.Column(db.Integer, default=20)  # 0-100 %
    close_date = db.Column(db.Date)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    contacts = db.relationship("Contact", secondary=deal_contacts, back_populates="deals")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "value": self.value,
            "stage": self.stage,
            "probability": self.probability,
            "close_date": self.close_date.strftime("%Y-%m-%d") if self.close_date else None,
            "notes": self.notes,
            "contacts": [{"id": c.id, "name": c.name} for c in self.contacts],
            "created_at": self.created_at.strftime("%Y-%m-%d"),
        }


class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contact_id = db.Column(db.Integer, db.ForeignKey("contact.id"), nullable=False)
    kind = db.Column(db.String(30), default="note")  # note | call | email | meeting
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "contact_id": self.contact_id,
            "kind": self.kind,
            "description": self.description,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M"),
        }
