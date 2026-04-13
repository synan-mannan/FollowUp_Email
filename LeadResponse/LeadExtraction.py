import pandas as pd
import sqlite3
from langchain_core.prompts import PromptTemplate
from llm import getllm

df = pd.read_json("C:/Users/syedm/Synelime/coirei/FollowUp_Email/LeadResponse/leadsData.json")

dataList = df.get("data")
# sqlL = sqlite3.connect("C:/Users/syedm/Synelime/coirei/FollowUp_Email/Company.db")
# cursor = sqlL.cursor()


# for data in dataList:
#     cursor.execute(
#         f"""
#             insert into messages(lead_id, message) 
#                     VALUES (?, ?)
#                     """,
#         (data.get("id"), data.get("message"))
#     )

# print("added data to leads db")

llm = getllm()


lead_scoring_prompt = PromptTemplate(
    input_variables=["message"],
    template="""
You are an AI assistant that analyzes customer replies and extracts lead qualification details.

Step 1: Analyze the message and extract the following:

- Requirement Clarity: (Clear / Partial / Unclear)
- Budget Mentioned: (Yes / No)
- Timeline Mentioned: (Yes / No)
- Intent: (Serious / Exploring / Not Interested)

Step 2: Apply scoring rules:

- Budget mentioned → +2
- Timeline mentioned → +2
- Clear requirement → +2
- Exploring / Not Interested → -2

Step 3: Calculate total score.

Step 4: Classify the lead:

- Score ≥ 4 → Good Lead
- Score 1–3 → Maybe
- Score ≤ 0 → Not Interested

Return ONLY a valid JSON object string in the following format:

{{
  "requirement_clarity": "",
  "budget_mentioned": "",
  "timeline_mentioned": "",
  "intent": "",
  "score": 0,
  "classification": ""
}}

Customer Message:
\"\"\"{message}\"\"\"
"""
)

import json
import re

leadInfo = {}

for data in dataList:
    prompt = lead_scoring_prompt.format(
        message=data.get("message")
    )

    output = llm.invoke(prompt)

    #  Extract JSON safely
    match = re.search(r'\{.*?\}', output.content, re.DOTALL)

    if match:
        try:
            parsed = json.loads(match.group())
        except json.JSONDecodeError:
            parsed = {"error": "Invalid JSON", "raw": output.content}
    else:
        parsed = {"error": "No JSON found", "raw": output.content}

    leadInfo[data.get("id")] = parsed

#  Write proper JSON file
with open("C:/Users/syedm/Synelime/coirei/FollowUp_Email/LeadResponse/LeadInfo.json", "w") as li:
    json.dump(leadInfo, li, indent=4)

print("Saved successfully ")