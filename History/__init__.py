try:
    import sqlite3
except:
    print('sqlite3 module not found. History will not be saved')
    sqlite3 = None
else:
    from sqlite3 import Error

CREATE_TABLE = """CREATE TABLE IF NOT EXISTS history (
                   id INTEGER PRIMARY KEY,
                   timestamp REAL UNIQUE,
                   latency REAL,
                   uptime REAL,
                   rx REAL,
                   tx REAL
                  );"""
INSERT_ROW = """ INSERT INTO history(timestamp,latency,uptime,rx,tx)
              VALUES(?,?,?,?,?) """

class History(object):
    def __init__(self, history_db="starlink-history.db"):
        self._db = history_db
        self.conn = None

    def connect(self):
        print("Connecting to the database")
        if sqlite3 is None:
            return
        try:
            self.conn = sqlite3.connect(self._db)
            print(f'Connected to {self._db} version {sqlite3.version}')
        except Error as e:
            print(f'Connect to {self._db} failed: {e}')
            self.conn = None
        else:
            self.cursor = self.conn.cursor()
            self._create_table()

    def _create_table(self):
        print("Creating the table")
        try:
            self.cursor.execute(CREATE_TABLE)
        except Error as e:
            print(f'Failed to create table: {e}')

    def insert_data(self, data, cnt=-1, commit=True):
        if self.conn is None:
            return
        try:
            self.cursor.execute(INSERT_ROW, (int(data._xaxis[cnt].timestamp()), data._latency[cnt], data._avail[cnt], data._download[cnt], data._upload[cnt]))
        except sqlite3.IntegrityError:
            pass # Ignore error in unique row
        if commit:
            self.conn.commit()
        return self.cursor.lastrowid

    def populate(self, data):
        cnt = 0
        print('Populating history to the database')
        for i in data._xaxis:
            self.insert_data(data, cnt, commit=False)
            cnt += 1
        self.conn.commit()
        print('Done populating history')
