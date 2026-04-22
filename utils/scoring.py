from pydantic import BaseModel, Field
from typing import Dict, Any
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from config import settings
import json
import re
from datetime import datetime

class LeadScore(BaseModel):
    requirement_clarity: str = Field(..., description="Clear/Partial/Unclear")
    budget_mentioned: str = Field(..., description="Yes/No")
    timeline_mentioned: str = Field(..., description="Yes/No")
    intent: str = Field(..., description="Serious/Exploring/Not Interested")
    score: int = Field(..., ge=0, le=10)
    classification: str = Field(..., pattern="^(Good|Maybe|Not Interested)$")

SCORING_PROMPT = PromptTemplate(
    input_variables=["message"],
    template="""Analyze this customer reply for lead qualification. Return ONLY valid JSON.

Extract:
- requirement_clarity: "Clear" | "Partial" | "Unclear"
- budget_mentioned: "Yes" | "No"  
- timeline_mentioned: "Yes" | "No"
- intent: "Serious" | "Exploring" | "Not Interested"

Scoring (+2 each positive, -2 negative):
- Clear req +2, Budget Yes +2, Timeline Yes +2, Serious +2
- Not Interested -4

Classification:
- score >=6: "Good"
- score 2-5: "Maybe" 
- score <2: "Not Interested"

Customer message:
{message}

JSON:
""" 
)

def get_scoring_llm():
    return ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=settings.groq_api_key,
        temperature=0.1
    )

def score_reply(message: str) -> LeadScore:
    """Score a single reply message."""
    llm = get_scoring_llm()
    prompt = SCORING_PROMPT.format(message=message)
    response = llm.invoke(prompt)
    
    # Extract JSON from response
    json_match = re.search(r'\{[\s\S]*\}', response.content)    
    # print(response.content)
    # print(json_match)
    if json_match:
        try:
            score_data = json.loads(json_match.group())
            return LeadScore(**score_data)
        except Exception:
            pass
    
    # Fallback low score
    return LeadScore(
        requirement_clarity="Unclear",
        budget_mentioned="No",
        timeline_mentioned="No",
        intent="Not Interested",
        score=0,
        classification="Not Interested"
    )

def aggregate_scores(scores: list[LeadScore]) -> LeadScore:
    """Aggregate multiple scores for a lead."""
    if not scores:
        return LeadScore(score=0, classification="Maybe", requirement_clarity="Unclear", 
                        budget_mentioned="No", timeline_mentioned="No", intent="Exploring")
    
    latest = scores[0]  # Most recent
    return latest  # For simplicity, use latest score

