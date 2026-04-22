import pandas as pd
import sqlite3
from langchain_core.prompts import PromptTemplate
# from llm import getllm

# df = pd.read_json("C:/Users/syedm/Synelime/coirei/FollowUp_Email/LeadResponse/leadsData.json")

# dataList = df.get("data")
sqlL = sqlite3.connect("C:/Users/syedm/Synelime/coirei/FollowUp_Email/Company.db")
# cursor = sqlL.cursor()