import json
import requests
import sqlite3 as sql

def update():
    """Update User Data"""
    conn = sql.connect("data.db")
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS data")
    cursor.execute("""CREATE TABLE IF NOT EXISTS data(
    steamID CHAR(17) PRIMARY KEY,
    place INTEGER,
    totalScore INTEGER,
    avgAccuracy FLOAT,
    avgMisses FLOAT,
    updated DATETIME
    );""")
    data = json.loads(requests.get("https://intralism.khb-soft.ru/?GetRanks",verify=False).text)
    temp = data["playersRanks"]
    for i in temp:
        cursor.execute("INSERT INTO data(steamID, place, totalScore, avgAccuracy, avgMisses, updated) VALUES (?,?,?,?,?,?)", (i["steamID"],i["place"],i["totalScore"],i["avgAccuracy"],i["avgMisses"],i["updated"]))
    conn.commit()
