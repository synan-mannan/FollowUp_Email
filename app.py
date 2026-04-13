import pandas as pd
import os
import time
import sqlite3
from Gmail_API_Setup.sendMessage import send_email
from excel_ops.appendData import append

file_path = "C:/Users/syedm/OneDrive/Documents/excel_path.xlsx"

sqlL = sqlite3.connect("./Company.db")

cursor = sqlL.cursor()

# cursor.execute(
#     """
#     CREATE TABLE leads (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     name TEXT,
#     phone TEXT,
#     email TEXT,
#     requirement TEXT,
#     status TEXT CHECK(status IN ('contacted', 'not_contacted')) DEFAULT 'not_contacted',
#     score INTEGER,
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     lead_type TEXT CHECK(lead_type IN ('good', 'maybe', 'not_interested'))
# );
# """
# )

# print("leads")

# cursor.execute(
#     """
#     CREATE TABLE messages (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     lead_id INTEGER,
#     message TEXT,
#     timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     FOREIGN KEY (lead_id) REFERENCES leads(id)
# );
# """
# )

# print("messages")



while True:
    name = input("Enter the name")
    ph_num = int(input("Enter phone number"))
    email = input("Enter Email")
    requirement = input("Enter your requirements")

    if name and ph_num and email and requirement:
        try:
            cursor.execute(
                f"""
                insert into leads(name, phone, email, requirement, status, score, lead_type) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (name, ph_num, email, requirement, "contacted", 2, "maybe")
            )
            print("added lead to db")
            # print(result)

            message_result = send_email(email, name, "xyz, abc, lmnop", requirement)
            # print("message sent", message_result)
            result = append(file_path, name, ph_num, email, requirement, "contacted")

        except Exception as e:
            print("Error", e)

    


