from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from email.mime.text import MIMEText
import base64
import json
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from config import settings
from typing import Dict, List, Any

SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.send"
]

def get_gmail_service() -> Any:
    """Get authenticated Gmail service."""
    creds_data = json.load(open(settings.gmail_token_path, 'r'))
    creds = Credentials.from_authorized_user_info(
        creds_data, 
        scopes=SCOPES
    )
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(settings.gmail_token_path, 'w') as token_file:
            token_file.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

TEMPLATES = {
    "initial": """Hello {name},

We help businesses with {services}. You mentioned needing help with {requirement}.

Can you share more details about your requirements?

Thanks & Regards,
Syed Mohammed Mannan""",
    
    "proposal": """Dear {name},

Following up on your {requirement} inquiry. Here's our detailed proposal.

[Proposal details here]

Looking forward to your feedback.

Best,
Syed""",
    
    "nurture": """Hi {name},

Just checking in on your {requirement} project. 

Any updates or questions?

Best regards,
Syed""",
    
    "reminder": """Hello {name},

Haven't heard back regarding your {requirement}. Still interested?

Let me know your thoughts.

Regards,
Syed"""
}

def send_email(template_key: str, to_email: str, name: str, requirement: str, services: str = None, **kwargs) -> Dict[str, str]:
    """Send templated email, return thread_id/message_id."""
    service = get_gmail_service()
    body = TEMPLATES[template_key].format(name=name, requirement=requirement, services=services or settings.lead_services, **kwargs)
    
    message = MIMEText(body)
    message['to'] = to_email
    message['subject'] = f"Re: {requirement[:50]}" if 'Re:' not in requirement else requirement
    
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    
    result = service.users().messages().send(
        userId=settings.from_email,
        body={'raw': raw}
    ).execute()
    
    thread_id = result.get('threadId')
    return {'message_id': result['id'], 'thread_id': thread_id}

def get_recent_replies(lead_email: str, days_back: int = 2) -> List[Dict]:
    """Get recent messages matching lead email (replies/conversations)."""
    service = get_gmail_service()
    since = (datetime.now() - timedelta(days=days_back)).strftime('%Y/%m/%d')
    # Query: to/from lead, exclude pure outbound
    query = f"after:{since} ({lead_email}) -in:sent"
    
    res = service.users().messages().list(
        userId=settings.from_email,
        q=query,
        maxResults=20
    ).execute()
    
    replies = []
    for msg_id in res.get('messages', []):
        msg = service.users().messages().get(
            userId=settings.from_email, 
            id=msg_id['id'],
            format='full'
        ).execute()
        
        # print(msg)

        payload = msg['payload']
        headers = {h['name']: h['value'] for h in payload.get('headers', [])}
        
        # Get body
        if 'parts' in payload:
            body_data = payload['parts'][0]['body']['data']
        else:
            body_data = payload['body']['data']
        body = base64.urlsafe_b64decode(body_data).decode('utf-8', errors='ignore') if body_data else ''
        
        replies.append({
            'id': msg['id'],
            'thread_id': msg['threadId'],
            'timestamp': datetime.fromtimestamp(int(msg['internalDate']) / 1000),
            'from': headers.get('From', ''),
            'subject': headers.get('Subject', ''),
            'body_snippet': body[:500]  # Truncate for scoring
        })
    
    return sorted(replies, key=lambda x: x['timestamp'], reverse=True)

