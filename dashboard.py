import streamlit as st
import pandas as pd
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from models import Lead, Message
from config import settings
from utils.gmail import get_recent_replies
from utils.scoring import score_reply
from core.followup_engine import decide_followup

engine = sa.create_engine(f"sqlite:///{settings.db_path}")
SessionLocal = sessionmaker(bind=engine)

st.set_page_config(page_title="Lead Dashboard", layout="wide")

st.title("AI Lead Management Dashboard")

# Sidebar
st.sidebar.header("Controls")
refresh = st.sidebar.button("Refresh Data")
test_followup = st.sidebar.text_input("Test Followup Lead ID")
if st.sidebar.button("Trigger Followup"):
    if test_followup:
        from core.followup_engine import execute_followup
        execute_followup(int(test_followup))
        st.sidebar.success(f"Triggered followup for lead {test_followup}")

@st.cache_data(ttl=300)
def load_data():
    db = SessionLocal()
    leads = db.query(Lead).all()
    messages = db.query(Message).all()
    db.close()
    return leads, messages

leads, messages = load_data()

if not leads:
    st.info("No leads yet. Create via API: POST /leads")
else:
    df_leads = pd.DataFrame([l.__dict__ for l in leads])
    df_leads['hours_since_contact'] = (pd.Timestamp.now() - pd.to_datetime(df_leads['last_contacted'])).dt.total_seconds() / 3600
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Leads", len(leads))
    with col2:
        good = len([l for l in leads if l.classification == "Good"])
        st.metric("Good Leads", good)
    with col3:
        st.metric("Followups Needed", len([l for l in leads if l.followup_count < 3 and l.status != "closed"]))
    
    st.subheader("Leads Overview")
    st.dataframe(df_leads[['name', 'email', 'classification', 'score', 'followup_count', 'status', 'hours_since_contact']].sort_values('score', ascending=False))
    
    selected_lead = st.selectbox("View Details", leads, format_func=lambda l: f"{l.name} ({l.email}) - {l.classification}")
    
    if selected_lead:
        col1, col2 = st.columns(2)
        with col1:
            st.json(selected_lead.ai_score or {})
            if st.button(f"Manual Score Refresh - {selected_lead.name}"):
                from utils.gmail import get_recent_replies
                replies = get_recent_replies(selected_lead.email)
                if replies:
                    latest_reply = replies[0]['body_snippet']
                    score = score_reply(latest_reply)
                    st.json(score.model_dump())
        
        with col2:
            action = decide_followup(selected_lead.id)
            st.info(f"Recommended Action: {action or 'Wait'}")
            if st.button(f"Execute Followup - {selected_lead.name}"):
                from core.followup_engine import execute_followup
                execute_followup(selected_lead.id)
                st.rerun()
        
        st.subheader("Messages")
        lead_msgs = [m for m in messages if m.lead_id == selected_lead.id]
        for msg in lead_msgs[-10:]:  # Last 10
            st.write(f"**{msg.direction.upper()}** ({msg.timestamp}): {msg.message[:200]}...")
    
    st.subheader("Recent Gmail Replies (All Leads)")
    all_replies = {}
    for lead in leads[:5]:  # Top 5
        replies = get_recent_replies(lead.email)
        if replies:
            all_replies[lead.name] = replies[0]
    st.json(all_replies)

