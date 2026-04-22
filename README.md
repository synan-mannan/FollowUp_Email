# AI-Powered Lead Management System V2

Complete end-to-end system: **FastAPI API** → Gmail send/read → **AI scoring (Groq)** → auto follow-ups → **Streamlit dashboard** + **APScheduler**.

## Architecture Diagram

```
POST /leads → DB Store + Initial Email (gmail.py)
      ↓ every 30min (scheduler.py)
Read Replies (gmail.py) → Score AI (scoring.py) → Decide (followup_engine.py) → Send Follow-up
      ↕ Live View/Test
Dashboard (Streamlit) + API (FastAPI)
```

## Features

- **API First**: Create leads, auto-send initial email, list/view
- **Gmail Full**: Send templates, read recent replies/threads
- **AI Strict JSON**: Groq LLM scores (clarity/budget/timeline/intent/score/classification)
- **Smart Follow-ups**: Time-based + score-driven (proposal/nurture/reminder)
- **Automation**: Background scheduler runs pipeline continuously
- **Dashboard**: Real-time leads table, manual controls, test scoring
- **No Manual Steps**: End-to-end connected pipeline

## Quick Start (Windows)

1. **Install & Configure**:

```
pip install -r requirements.txt
copy .env.example .env
```

**Edit `.env`**:

```
GROQ_API_KEY=your_key
GMAIL_TOKEN_PATH=./Gmail_API_Setup/token.json
GMAIL_CREDENTIALS_PATH=./Gmail_API_Setup/credentials.json
FROM_EMAIL=me
```

2. **Gmail Setup** (one-time):

```
python Gmail_API_Setup/first.py  # Browser OAuth → token.json
```

3. **Database**:

```
python migrate_db.py  # Adds new columns safely
```

4. **Run Full Stack** (3 terminals):

```
# Terminal 1: API Server
uvicorn fastapi_app:app --reload
# http://localhost:8000/docs

# Terminal 2: Dashboard
streamlit run dashboard.py
# http://localhost:8501

# Terminal 3: Automation
python scheduler.py  # Runs forever, checks every 30min
```

## API Usage

**Swagger**: `http://localhost:8000/docs`

```
# Create Lead + Auto Email
curl -X POST "http://localhost:8000/leads" \\
  -H "Content-Type: application/json" \\
  -d '{"name":"John Doe","phone":"1234567890","email":"john@test.com","requirement":"Web app"}'

# List Leads
curl http://localhost:8000/leads

# Lead + Replies
curl http://localhost:8000/leads/1
curl http://localhost:8000/leads/1/replies

# Manual Follow-up
curl -X POST http://localhost:8000/leads/1/followup
```

## AI Lead Scoring

**Input**: Gmail reply text  
**Output**: Strict Pydantic JSON

```json
{
  "requirement_clarity": "Clear",
  "budget_mentioned": "Yes",
  "timeline_mentioned": "No",
  "intent": "Serious",
  "score": 6,
  "classification": "Good"
}
```

**Logic**: +2 budget/timeline/clear/serious, -2/4 negatives → Good(≥6)/Maybe/Not Interested

## Follow-up Decision Engine

| Condition           | Action   |
| ------------------- | -------- |
| Just replied        | Wait     |
| Good + 48h no reply | Proposal |
| Maybe + 24h         | Nurture  |
| 72h no activity     | Reminder |
| Not Interested/5+   | Archive  |

## Dashboard (localhost:8501)

- Leads table: scores/status/time/metrics
- **Lead Detail**: JSON score, manual refresh/execute
- Global recent replies
- Test followup trigger

## Database (Company.db)

**Enhanced Schema**:

```
leads: id,name,email,requirement,status,score,type,last_contacted/replied,followup_count,thread_id,ai_score(JSON),classification
messages: lead_id,message,direction(sent/received),timestamp
```

## New Project Structure

```
├── fastapi_app.py     # API server
├── dashboard.py       # Streamlit UI
├── scheduler.py       # Automation
├── config.py          # .env loader
├── models.py          # SQLAlchemy
├── utils/             # gmail.py, scoring.py
├── core/              # followup_engine.py
├── Company.db
├── requirements.txt
├── .env.example
└── TODO.md            # Progress tracker
```

**Deprecated** (safe to delete): `app.py`, `excel_ops/`, `LeadResponse/`, `Gmail_API_Setup/sendMessage.py`

## End-to-End Test

```
1. curl POST /leads → Email sent, DB row created
2. Reply to Gmail email
3. Dashboard → See reply → Score updates to "Good"
4. scheduler.py runs → Auto sends Proposal template
5. Dashboard shows followup_count=1, new message
```

## Prerequisites / Troubleshooting

| Issue         | Fix                                         |
| ------------- | ------------------------------------------- |
| Import errors | `pip install -r requirements.txt`           |
| Gmail auth    | `python Gmail_API_Setup/first.py`           |
| No token.json | Enable Gmail API, download credentials.json |
| Groq fails    | Check key/quota at console.groq.com         |
| DB locked     | Kill Python processes                       |
| Windows paths | Use forward slashes in .env                 |
