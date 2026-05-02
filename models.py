from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255))
    phone = Column(String(20))
    email = Column(String(255), unique=True, index=True)
    requirement = Column(Text)
    status = Column(String(50), default="not_contacted")
    score = Column(Integer, default=0)
    lead_type = Column(String(50))
    last_contacted = Column(DateTime, default=func.now())
    last_replied = Column(DateTime, nullable=True)
    followup_count = Column(Integer, default=0)
    thread_id = Column(String(255), nullable=True)
    ai_score = Column(JSON, nullable=True)
    classification = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=func.now())
    company_id = Column(Integer, ForeignKey("companies.id"), index = True)

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), index=True)
    message = Column(Text)
    direction = Column(String(20), default="sent")  # sent / received
    timestamp = Column(DateTime, default=func.now())

class companies(Base):
     __tablename__ = "companies"

     id = Column(Integer, primary_key=True, autoincrement=True)
     company_name = Column(Text)
     industry = Column(Text)
     services = Column(Text)
     intro_message = Column(Text)
     qualification_questions = Column(Text)
     pricing_notes = Column(Text)
     preferred_channel = Column(Text)
     created_at = Column(DateTime, default=func.now())

