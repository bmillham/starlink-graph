#!/usr/bin/python
# (C) 2023 Brian Millham
# Convert the original sqlite database format to an imporoved formst
# Adds a new column prime to make searching for prime/non-prime easier
# Changed the format of the timestamp column to be compatible with SQLAlchemy
#
# SQLAlchemy >= 2.0 is required!
# pip install 'sqlalchemy>=2.0'

from history import History
from datetime import datetime
import sqlite3
import os

original = "starlink-history"
temp = "starlink-history.temp"

print('Converting database')
do_echo = False # Change to True to see what 

hist_db = History(history_db=f"sqlite+pysqlite:///{original}.temp.db", do_echo=do_echo)
hist_db.connect()

print('Converting database. This may take several minutes depending on the size of your data')
conn = sqlite3.connect(f'{original}.db')
cursor = conn.cursor()

# Get a total count to a little progress info can be shown
cursor.execute("select count(id) from history;")
count = cursor.fetchone()[0]

cursor.execute("select * from history;")
cnt = 0
for row in cursor.fetchall():
    if cnt % 1000 == 0:
        print(f'Convert {cnt}/{count}')
    try:
        ts = datetime.fromisoformat(row[1])
    except ValueError:
        ts = datetime.fromtimestamp(int(str(row[1])))
    prime = True if ts.hour >= 7 and ts.hour < 23 else False
    stmt = hist_db._insert(timestamp=datetime.fromisoformat(row[1]),
                                        latency=row[2],
                                        uptime=row[3],
                                        rx=row[4],
                                        tx=row[5])

    try:
        hist_db.conn.execute(stmt)
    except Error as e:
        print('Error inserting row:', e)
    cnt += 1

hist_db.conn.commit()
print('Database converted')

print(f'Saving backup of {original}.db to {original}.backup.db')
os.rename(f'{original}.db', f'{original}.backup.db')
print(f'Moving converts database {original}.temp.db to {original}.db')
os.rename(f'{original}.temp.db', f'{original}.db')


