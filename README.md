# FollowUp Email Automation

A Python-based CRM system for managing leads: capturing lead details, sending automated Gmail follow-up emails, appending data to Excel and SQLite database, and scoring leads using AI (Groq/Llama LLM) based on customer replies.

## Features

- **Lead Capture**: Interactive CLI input for name, phone, email, requirements; stores in SQLite (`Company.db`).
- **Automated Email**: Sends personalized follow-up emails via Gmail API.
- **Excel Integration**: Appends lead data to `excel_path.xlsx`.
- **AI Lead Scoring**: Analyzes customer reply messages (from `leadsData.json`) to classify leads as "Good", "Maybe", or "Not Interested" with scores based on clarity, budget, timeline, intent.
- **Database**: Tracks leads and messages in `Company.db`.

## Project Structure

```
FollowUp_Email/
├── app.py                  # Main CLI app for lead capture, email, Excel/DB ops
├── Company.db              # SQLite DB for leads &amp; messages
├── excel_path.xlsx         # Excel sheet for lead export
├── excel_ops/
│   └── appendData.py       # Appends data to Excel
├── Gmail_API_Setup/
│   ├── first.py            # OAuth setup (run once to generate token.json)
│   ├── sendMessage.py      # Gmail API email sender
│   ├── credentials.json    # Gmail API credentials (download from Google Console)
│   └── token.json          # Generated OAuth token
└── LeadResponse/
    ├── LeadExtraction.py   # AI lead scoring from replies using LLM
    ├── llm.py              # Groq LLM setup
    ├── LeadInfo.json       # Generated lead scores
    └── leadsData.json      # Sample reply data
```

## Prerequisites

- Python 3.8+
- Gmail API credentials: [Setup Guide](https://developers.google.com/gmail/api/quickstart/python)
  - Download `credentials.json`.
- `GROQ_API_KEY` env var for AI scoring.
- Libraries: `pip install pandas openpyxl sqlite3 langchain-groq google-api-python-client google-auth-oauthlib google-auth-httplib2`

## Quick Start

1. **Gmail Setup** (one-time):

   ```
   cd Gmail_API_Setup
   python first.py  # Opens browser for OAuth, generates token.json
   ```

2. **AI Setup**:

   ```
   set GROQ_API_KEY=your_key_here  # Windows
   # export GROQ_API_KEY=your_key_here  # Linux/Mac
   ```

3. **Run Main App**:

   ```
   python app.py
   ```

   - Enter lead details (name, phone, email, requirement).
   - Automatically: sends email, appends to Excel/DB.

4. **Score Leads** (from replies):
   ```
   cd LeadResponse
   python LeadExtraction.py  # Processes leadsData.json → LeadInfo.json
   ```

## Usage Example

```
Enter the name: John Doe
Enter phone number: 1234567890
Enter Email: john@example.com
Enter your requirements: Need web dev services
```

- Email sent, data appended to Excel/DB.

## Database Schema

```sql
-- leads
CREATE TABLE leads (
    id INTEGER PRIMARY KEY,
    name TEXT, phone TEXT, email TEXT, requirement TEXT,
    status TEXT DEFAULT &#39;not_contacted&#39;,
    score INTEGER, lead_type TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- messages
CREATE TABLE messages (
    id INTEGER PRIMARY KEY,
    lead_id INTEGER, message TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## AI Scoring Logic

- Analyzes replies for: requirement clarity, budget/timeline mentions, intent.
- Score: +2 per positive factor, -2 for low interest.
- Output: JSON with classification.

## Notes

- Hardcoded paths (e.g., Excel); update as needed.
- Run `python app.py` in loop for continuous input.
- For production: Add env vars, error handling, web UI.

## Troubleshooting

- Gmail errors: Refresh `token.json` with `first.py`.
- LLM: Check `GROQ_API_KEY`.
- Excel: Ensure `openpyxl` installed.
