from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.send"
]

flow = InstalledAppFlow.from_client_secrets_file(
    "C:/Users/syedm/Synelime/coirei/FollowUp_Email/Gmail_API_Setup/credentials.json",
    SCOPES
)

creds = flow.run_local_server(port=0)

with open("token.json", "w") as f:
    f.write(creds.to_json())