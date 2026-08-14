import sqlite3

c = sqlite3.connect("/opt/hunger-bot/data/bot.db")
cols = [r[1] for r in c.execute("pragma table_info(events)")]
print("events cols:", cols)
print("events total:", c.execute("select count(*) from events").fetchone()[0])
print("events user 79956169:", c.execute("select count(*) from events where user_id=79956169").fetchone()[0])
print("schema version:", c.execute("select version from schema_meta").fetchone()[0])
