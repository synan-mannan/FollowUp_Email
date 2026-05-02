from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import sqlalchemy as sa
from models import Lead, Message, Base, companies
from utils.gmail import send_email
from core.followup_engine import execute_followup
from config import settings
from datetime import datetime
from LeadResponse.llm import getllm

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
    company_name: str

class LeadResponse(BaseModel):
    id: int
    name: str
    email: str
    status: str
    company_id: int
    classification: Optional[str] = None
    score: Optional[int] = None

class CompanyCreate(BaseModel):
    company_name: str
    industry : str
    services : str
    preferred_channel : str
    pricing_notes : str
    qualification_questions: str
    company_intro: str

class CompanyResponse(BaseModel):
    id: int
    company_name: str
    industry: str
    services: str
    intro_message: Optional[str] = None
    qualification_questions: Optional[list[str]] = None
    pricing_notes: Optional[str] = None
    preferred_channel: Optional[str] = None
    created_at: datetime


@app.post("/leads", response_model=LeadResponse)
def create_lead(lead: LeadCreate, db: Session = Depends(get_db)):
    # Check existing
    existing = db.query(Lead).filter(Lead.email == lead.email).first()
    if existing:
        raise HTTPException(409, "Lead email exists")
    
    try:
        company = db.query(companies).filter(companies.name == lead.company_name).first()
        company_id = company.company_id
    except Exception as e:
        raise HTTPException(500, f"Company id failed : {str(e)}")

    # Create lead
    db_lead = Lead(
        name=lead.name,
        phone=lead.phone,
        email=lead.email,
        requirement=lead.requirement,
        company_id = company_id,
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
            lead.requirement,
            company_id
        )
        db_lead.thread_id = email_result["thread_id"]
        db_lead.last_contacted = datetime.now()
        db.commit()
    except Exception as e:
        db_lead.status = "email_failed"
        db.commit()
        raise HTTPException(500, f"Email failed: {str(e)}")
    
    return db_lead

# @app.post("/leads", response_model=LeadResponse)
# def create_lead(lead: LeadCreate, db: Session = Depends(get_db)):
    
#     #  1. Ensure company exists (first-time setup)
#     company = db.query(Company).first()

#     if not company:
#         company = Company(
#             company_name="Oblytech",
#             industry="Software & Automation",
#             services="Custom software, AI automation, backend systems",
#             intro_message="We build scalable automation and custom software solutions.",
#             qualification_questions="",
#             pricing_notes="Flexible pricing based on scope",
#             preferred_channel="email",
#             created_at=datetime.now()
#         )
#         db.add(company)
#         db.commit()
#         db.refresh(company)

#     #  2. Check existing lead
#     existing = db.query(Lead).filter(Lead.email == lead.email).first()
#     if existing:
#         raise HTTPException(409, "Lead email exists")
    
#     #  3. Create lead
#     db_lead = Lead(
#         name=lead.name,
#         phone=lead.phone,
#         email=lead.email,
#         requirement=lead.requirement,
#         status="contacted",
#         lead_type="maybe",
#         score=2
#     )
#     db.add(db_lead)
#     db.commit()
#     db.refresh(db_lead)
    
#     #  4. Send initial email (with company context)
#     try:
#         email_result = send_email(
#             email_type="initial",
#             to_email=lead.email,
#             lead_name=lead.name,
#             lead_requirement=lead.requirement,
#             company_intro=company.intro_message,
#             company_services=company.services,
#             company_name=company.company_name
#         )

#         db_lead.thread_id = email_result["thread_id"]
#         db_lead.last_contacted = datetime.now()
#         db.commit()

#     except Exception as e:
#         db_lead.status = "email_failed"
#         db.commit()
#         raise HTTPException(500, f"Email failed: {str(e)}")
    
#     return db_lead



@app.post("/company", response_model=CompanyResponse)
def register_company(
    company: CompanyCreate,
    db: Session = Depends(get_db)
):
    
    
    existing = db.query(companies).filter(
        companies.company_name == company.company_name
    ).first()

    if existing:
        raise HTTPException(409, "Company already registered")

    
    db_company = companies(
        company_name=company.company_name,
        industry=company.industry,
        services=company.services,
        company_intro = company.company_intro,
        pricing_notes=company.pricing_notes,
        preferred_channel=company.preferred_channel,
        qualification_questions = company.qualification_questions,
        created_at=datetime.now()
    )

    db.add(db_company)
    db.commit()
    db.refresh(db_company)

    return db_company

@app.get("/company")
def list_companies(db: Session = Depends(get_db)):
    company_list = db.query(companies).all()
    return company_list

@app.get("/leads")
def list_leads(db: Session = Depends(get_db)):
    leads = db.query(Lead).all()
    return leads

@app.get("/company/{company_name}", response_model=CompanyResponse)
def get_company(company_name: str, db: Session = Depends(get_db)):
    company = db.query(companies).filter(companies.company_name == company_name).first()
    if not company:
        raise HTTPException(404, "company not found")
    return company

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

