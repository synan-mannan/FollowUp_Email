from langchain_groq import ChatGroq
import os
from pydantic import SecretStr

api_key = os.getenv("GROQ_API_KEY")

def getllm():
    return ChatGroq(
        model="llama-3.1-8b-instant",
        api_key= SecretStr(api_key) if api_key else None,
        temperature=0
    )