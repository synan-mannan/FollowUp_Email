from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from email.mime.text import MIMEText
import base64
import json
from google.auth.transport.requests import Request

# creds = Credentials("C:/Users/syedm/Synelime/coirei/FollowUp_Email/Gmail_API_Setup/token.json")

with open("C:/Users/syedm/Synelime/coirei/FollowUp_Email/Gmail_API_Setup/token.json", "r") as f:
    data = json.load(f)

creds = Credentials(
    token=data.get("token"),
    refresh_token=data.get("refresh_token"),
    token_uri=data.get("token_uri"),
    client_id=data.get("client_id"),
    client_secret=data.get("client_secret"),
    scopes=data.get("scopes")
)

# force refresh check
if creds.expired and creds.refresh_token:
    creds.refresh(Request())

# import json

# with open("C:/Users/syedm/Synelime/coirei/FollowUp_Email/Gmail_API_Setup/token.json") as f:
#     data = json.load(f)
#     print(data)

service = build("gmail", "v1", credentials=creds)

print("creds is working")

def send_email(to, name, services, requirement):
    body = f"""
    Hello {name}, we help businesses with {services}. You mentioned {requirement}. Can you share more details about your requirement?

    Thanks & Regards
    Syed Mohammed Mannan
"""
    subject = "Company Services Offered"

    message = MIMEText(body)
    message["to"] = to
    message["subject"] = subject

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

    result = service.users().messages().send(
        userId="me",
        body={"raw": raw}
    ).execute()

    return result


# “Hi [Name], we help businesses with [services]. You mentioned [requirement]. Can you share more details about your requirement?”