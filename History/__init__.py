try:
    import sqlite3
except:
    print('sqlite3 module not found. History will not be saved')
    sqlite3 = None
else:
    from sqlite3 import Error
from datetime import datetime, timedelta

CREATE_TABLE = """CREATE TABLE IF NOT EXISTS history (
                   id INTEGER PRIMARY KEY,
                   timestamp TEXT UNIQUE,
                   latency REAL,
                   uptime REAL,
                   rx REAL,
                   tx REAL
                  );"""
INSERT_ROW = """ INSERT INTO history(timestamp,latency,uptime,rx,tx)
              VALUES(?,?,?,?,?) """

PRIME = """ SELECT sum(rx), sum(tx), avg(latency), avg(uptime) FROM history
            WHERE timestamp >= ? and timestamp < ?; """
NON_PRIME = """ SELECT sum(rx), sum(tx), avg(latency), avg(uptime) FROM history
            WHERE timestamp LIKE ? and (timestamp < ? OR timestamp >= ?); """
#NON_PRIME = """ SELECT sum(rx), sum(tx), avg(latency), avg(uptime) FROM history
#            WHERE timestamp < ? OR timestamp >= ?; """
CYCLE_USAGE = """ SELECT sum(rx), sum(tx), avg(latency), avg(uptime) FROM history
             WHERE datetime(timestamp, 'localtime') >= datetime(?, '-1 month') and datetime(timestamp, 'localtime') < datetime(?) """
CYCLE_USAGE_PRIME = """ SELECT sum(rx), sum(tx), avg(latency), avg(uptime) FROM history
                        WHERE time(timestamp, 'localtime') >= datetime(?, '-1 month') and datetime(timestamp, 'localtime') < datetime(?) """
CYCLE_DATES = """ SELECT datetime(?, '-1 month'), datetime(?) """
HOUR_USAGE = """select sum(rx), sum(tx), avg(latency), avg(uptime) from history where timestamp like ?; """

FIRST_DATE = "select timestamp from history order by timestamp asc limit 1"
END_DATE = "select timestamp from history order by timestamp DESC LIMIT 1"
ALL_DATES = "SELECT DATE(timestamp, 'localtime') FROM history GROUP BY DATE(timestamp, 'localtime');"

class History(object):
    def __init__(self, history_db="starlink-history.db", config=None):
        self._db = history_db
        self._config = config
        self.conn = None
        self._last_commit = 0
        self._commit_interval = 10 # Only commit every X seconds
        if config is None:
            self._prime_start = 7
            self._prime_end = 23
            self._cycle_start_day = 27
        else:
            self._prime_start = config.prime_start
            self._prime_end = config.prime_end
            self._cycle_start_day = config.billing_date


    def connect(self):
        if sqlite3 is None:
            return
        try:
            self.conn = sqlite3.connect(self._db)
        except Error as e:
            print(f'Connect to {self._db} failed: {e}')
            self.conn = None
        else:
            self.cursor = self.conn.cursor()
            self._create_table()

    def commit(self):
        now = datetime.now().timestamp()
        if now > self._last_commit + self._commit_interval:
            self.conn.commit()
            self._last_commit = now

    def _create_table(self):
        try:
            self.cursor.execute(CREATE_TABLE)
        except Error as e:
            print(f'Failed to create table: {e}')

    def insert_data(self, data, cnt=-1, commit=True):
        if self.conn is None:
            return
        try:
            self.cursor.execute(INSERT_ROW, (data._xaxis[cnt].replace(microsecond=0).isoformat(),
                                data._latency[cnt], data._avail[cnt], data._download[cnt], data._upload[cnt]))
        except sqlite3.IntegrityError:
            return -1
        if commit:
            self.commit()
        return self.cursor.lastrowid

    def query(self, sql):
        self.cursor.execute(sql)

    def populate(self, data):
        cnt = 0
        dups = 0
        inserted = 0
        self.cursor.execute('SELECT timestamp FROM history ORDER BY timestamp DESC LIMIT 1')
        last = self.cursor.fetchone()[0]
        print(f'Populating history to the database from {last}')
        for i in data._xaxis:
            x = i.replace(microsecond=0).isoformat()
            if x > last:
                if self.insert_data(data, cnt, commit=False) == -1:
                    dups += 1
                else:
                    inserted += 1
            cnt += 1
        self.commit()
        print(f'Done populating history. Inserted: {inserted} Dups: {dups}')

    def get_prime_usage(self, year, month, day):
        self.cursor.execute(PRIME, (f'{year}-{month}-{day:02}T{self.prime_start:02}:00:00', f'{year}-{month}-{day:02}T{self.prime_end:02}:00:00'))
        row = self.cursor.fetchone()
        return (row[0] if row[0] is not None else 0, row[1] if row[1] is not None else 0,
                0 if row[2] is None else row[2], 0 if row[3] is None else row[3])

    def get_non_prime_usage(self, year, month, day):
        self.cursor.execute(NON_PRIME, (f'{year}-{month}-{day:02}T%', f'{year}-{month}-{day:02}T{self.prime_start:02}:00:00', f'{year}-{month}-{day:02}T{self.prime_end:02}:00:00'))
        #self.cursor.execute(NON_PRIME, (f'{year}-{month}-{day:02}T{self.prime_start:02}:00:00', f'{year}-{month}-{day:02}T{self.prime_end:02}:00:00'))
        row = self.cursor.fetchone()
        return (0 if row[0] is None else row[0], 0 if row[1] is None else row[1],
                0 if row[2] is None else row[2], 0 if row[3] is None else row[3])

    def get_cycle_usage(self, month=None, year=None):
        now = datetime.now()
        #print(now.isoformat())
        y = now.year
        m = now.month
        d = now.day
        
        if d > self._cycle_start_day:
            m += 1
            if m >= 13:
                m = 1
                y += 1
       # m = 11
        if month is not None:
            month = month
        else:
            month = m
        if year is not None:
            year = year
        else:
            year = y
        day = f'{year}-{month:02}-{self._cycle_start_day:02}T00:00:00'
        #print(day)
        self.cursor.execute(CYCLE_DATES, (day, day))
        dates_row = self.cursor.fetchone()
        #print(f"Cycle Dates: {row[0]} - {row[1]}")
        ids = self._isodate(dates_row[0])
        ide = self._isodate(dates_row[1])
        #print(ids, ide)
        idm = ids - timedelta(days=30)
        idm1 = datetime(idm.year, idm.month, self._cycle_start_day)
        stday = idm1.day
        pruse = []
        ptuse = []
        pluse = []
        puuse = []
        nruse = []
        ntuse = []
        nluse = []
        nuuse = []
        tluse = []
        tuuse = []
        while True:
            #print(idm1)
            idm1 = idm1 + timedelta(days=1)
            use = self.get_prime_usage(idm1.year, idm1.month, idm1.day)
            #print(idm1, use[0])
            if use[0] > 0:
                pruse.append(use[0])
                ptuse.append(use[1])
                pluse.append(use[2])
                puuse.append(use[3])
                tluse.append(use[2])
                tuuse.append(use[3])
            nuse = self.get_non_prime_usage(idm1.year, idm1.month, idm1.day)
            if nuse[0] > 0:
                nruse.append(nuse[0])
                ntuse.append(nuse[1])
                nluse.append(nuse[2])
                nuuse.append(nuse[3])
                tluse.append(nuse[2])
                tuuse.append(nuse[3])
            if idm1.day > self._cycle_start_day and idm1.month == m:
                break

        self.cursor.execute(CYCLE_USAGE, (day, day))
        row = self.cursor.fetchone()
        #print(row)
        return (dates_row[0], dates_row[1], sum(pruse), sum(ptuse), self._average(pluse), self._average(puuse),
                sum(nruse), sum(ntuse), self._average(nluse), self._average(nuuse), self._average(tluse), self._average(tuuse))

    def _average(self, list):
        try:
            return sum(list) / len(list)
        except ZeroDivisionError:
            return 0

    def _isodate(self, date):
        csy, csm, csd = date.split(' ')[0].split('-')
        #return datetime(int(csy), int(csm), int(csd)).isoformat().split('T')[0]
        return datetime(int(csy), int(csm), int(csd))

    def get_hour_usage(self, year, month, day, hour):
        self.cursor.execute(HOUR_USAGE, (f'{year}-{month:02}-{day:02}T{hour:02}:%',))
        row = self.cursor.fetchone()
        #print(row)
        return (0 if row[0] is None else row[0], 0 if row[1] is None else row[1],
                0 if row[2] is None else row[2], 0 if row[3] is None else row[3])

    def get_start_end(self):
        self.cursor.execute(FIRST_DATE)
        row = self.cursor.fetchone()
        start_date = datetime.fromisoformat(row[0])
        self.cursor.execute(END_DATE)
        row = self.cursor.fetchone()
        end_date = datetime.fromisoformat(row[0])
        return start_date, end_date, start_date.day, end_date.day, start_date.year, start_date.month

    def get_all_dates(self):
        self.cursor.execute(ALL_DATES)
        dates = []
        for r in self.cursor.fetchall():
            dates.append(r[0])
        return dates
        
    @property
    def prime_start(self):
        return self._prime_start

    @prime_start.setter
    def prime_start(self, hour):
        self._prime_start = hour

    @property
    def prime_end(self):
        return self._prime_end

    @prime_end.setter
    def prime_end(self, hour):
        self._prime_end = hour

    @property
    def billing_date(self):
        return self._cycle_start_day

    @billing_date.setter
    def billing_date(self, day):
        self._cycle_start_day = day
