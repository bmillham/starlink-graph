from history import History
from datetime import datetime
import sqlite3
# pip install 'sqlalchemy>=2.0'

print('Converting database')

print('Creating new database')
do_echo = True
#engine = create_engine("sqlite+pysqlite:///starlink-history3.db", echo=do_echo, future=True)

hist_db = History(history_db="sqlite+pysqlite:///starlink-history3.db", do_echo=True)
#hist_db._create_database()

print('Database created')
print('Converting timestamp')
conn = sqlite3.connect('starlink-history.db')
cursor = conn.cursor()
cursor.execute("select * from history;")

with hist_db.engine.connect() as aconn:
    for row in cursor.fetchall():
        ts = datetime.fromisoformat(row[1])
        prime = True if ts.hour >= 7 and ts.hour < 23 else False
        stmt = hist_db._insert(timestamp=datetime.fromisoformat(row[1]),
                                            latency=row[2],
                                            uptime=row[3],
                                            rx=row[4],
                                            tx=row[5])
        try:
            aconn.execute(stmt)
        except:
            print('error')
    aconn.commit()
