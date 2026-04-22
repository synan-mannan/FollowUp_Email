import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from models import Lead, Message
from utils.gmail import get_recent_replies, send_email
from utils.scoring import score_reply, LeadScore
from config import settings
from datetime import datetime, timedelta
import json

engine = sa.create_engine(f"sqlite:///{settings.db_path}")
SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def process_lead_replies(lead_id: int) -> bool:
    """Check replies, score, update lead. Return True if new replies processed."""
    db = next(get_db())
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        return False
    
    replies = get_recent_replies(lead.email)
    new_replies = [r for r in replies if (not lead.last_replied or r['timestamp'] > lead.last_replied)]
    
    if not new_replies:
        return False
    
    # Score new replies
    scores = [score_reply(r['body_snippet']) for r in new_replies]
    latest_score = scores[0]  # Use latest
    
    # Save messages
    for reply in new_replies:
        msg = Message(
            lead_id=lead_id,
            message=reply['body_snippet'],
            direction="received"
        )
        db.add(msg)
    
    # Update lead
    lead.ai_score = latest_score.model_dump()
    lead.classification = latest_score.classification
    lead.score = latest_score.score
    lead.last_replied = max(r['timestamp'] for r in new_replies)
    
    db.commit()
    return True

def decide_followup(lead_id: int) -> str | None:
    """Decide next action for lead. Returns template_key or None."""
    db = next(get_db())
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        return None
    
    if lead.classification == "Not Interested" or lead.followup_count >= 5:
        lead.status = "closed"
        db.commit()
        return None
    
    now = datetime.now()
    hours_since_contact = (now - lead.last_contacted).total_seconds() / 3600 if lead.last_contacted else 0
    hours_since_reply = (now - (lead.last_replied or lead.last_contacted)).total_seconds() / 3600
    
    updated = process_lead_replies(lead_id)
    
    if updated:
        lead.last_contacted = now
        db.commit()
        return None  # Just replied
    
    if hours_since_reply > 48 and lead.classification == "Good":
        lead.followup_count += 1
        lead.last_contacted = now
        db.commit()
        return "proposal"
    elif hours_since_contact > 24 and lead.classification == "Maybe":
        lead.followup_count += 1
        lead.last_contacted = now
        db.commit()
        return "nurture"
    elif hours_since_contact > 72:
        lead.followup_count += 1
        lead.last_contacted = now
        db.commit()
        return "reminder"
    
    return None

def execute_followup(lead_id: int):
    """Execute decided followup for lead."""
    action = decide_followup(lead_id)
    if not action:
        return
    
    db = next(get_db())
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    
    result = send_email(
        template_key=action,
        to_email=lead.email,
        name=lead.name,
        requirement=lead.requirement
    )
    
    # Save sent message
    msg = Message(
        lead_id=lead_id,
        message=f"Sent: {action} template via thread {result['thread_id']}",
        direction="sent"
    )
    db.add(msg)
    lead.thread_id = result.get('thread_id') or lead.thread_id
    
    db.commit()
    print(f"Executed {action} for lead {lead_id}")

