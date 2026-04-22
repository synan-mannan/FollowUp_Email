from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import sqlalchemy as sa
from models import Lead, Message, Base
from utils.gmail import send_email
from core.followup_engine import execute_followup
from config import settings
from datetime import datetime

# DB
engine = sa.create_engine(f"sqlite:///{settings.db_path}", echo=True)
Base.metadata.create_all(engine)  # Safe idempotent

SessionLocal = sa.orm.sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI(title="Lead Management API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LeadCreate(BaseModel):
    name: str
    phone: str
    email: str
    requirement: str

class LeadResponse(BaseModel):
    id: int
    name: str
    email: str
    status: str
    classification: Optional[str] = None
    score: Optional[int] = None

@app.post("/leads", response_model=LeadResponse)
def create_lead(lead: LeadCreate, db: Session = Depends(get_db)):
    # Check existing
    existing = db.query(Lead).filter(Lead.email == lead.email).first()
    if existing:
        raise HTTPException(409, "Lead email exists")
    
    # Create lead
    db_lead = Lead(
        name=lead.name,
        phone=lead.phone,
        email=lead.email,
        requirement=lead.requirement,
        status="contacted",
        lead_type="maybe",
        score=2
    )
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    
    # Send initial email
    try:
        email_result = send_email(
            "initial",
            lead.email,
            lead.name,
            lead.requirement
        )
        db_lead.thread_id = email_result["thread_id"]
        db_lead.last_contacted = datetime.now()
        db.commit()
    except Exception as e:
        db_lead.status = "email_failed"
        db.commit()
        raise HTTPException(500, f"Email failed: {str(e)}")
    
    return db_lead

@app.get("/leads")
def list_leads(db: Session = Depends(get_db)):
    leads = db.query(Lead).all()
    return leads

@app.get("/leads/{lead_id}", response_model=LeadResponse)
def get_lead(lead_id: int, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(404, "Lead not found")
    return lead

@app.get("/leads/{lead_id}/replies")
def get_replies(lead_id: int, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(404, "Lead not found")
    from utils.gmail import get_recent_replies
    replies = get_recent_replies(lead.email)
    messages = db.query(Message).filter(Message.lead_id == lead_id).all()
    return {"gmail_replies": replies, "db_messages": messages}

@app.post("/leads/{lead_id}/followup")
def trigger_followup(lead_id: int, db: Session = Depends(get_db)):
    execute_followup(lead_id)
    return {"status": "followup_triggered"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

