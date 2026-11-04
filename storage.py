import sqlite3, json
from pathlib import Path
import pandas as pd

DB=Path(__file__).parent/"agripilot.db"
def save_assessment(farm,result):
    with sqlite3.connect(DB) as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS assessments
        (id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TEXT DEFAULT CURRENT_TIMESTAMP,
         farm_name TEXT, crop TEXT, stage TEXT, result_json TEXT)""")
        conn.execute("INSERT INTO assessments(farm_name,crop,stage,result_json) VALUES(?,?,?,?)",
                     (farm.get("farm_name",""),farm.get("crop",""),farm.get("stage",""),json.dumps(result)))
def recent_assessments(limit=10):
    with sqlite3.connect(DB) as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS assessments
        (id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TEXT DEFAULT CURRENT_TIMESTAMP,
         farm_name TEXT, crop TEXT, stage TEXT, result_json TEXT)""")
        rows=conn.execute("SELECT created_at,farm_name,crop,stage FROM assessments ORDER BY id DESC LIMIT ?",(limit,)).fetchall()
    return pd.DataFrame(rows,columns=["Date/time","Farm","Crop","Growth stage"])
