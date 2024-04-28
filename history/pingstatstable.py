from sqlalchemy import create_engine, select, MetaData, Boolean, text
from sqlalchemy import Table, Column, Integer, DateTime, String, Text, Float, insert, func, and_, or_
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import exc
from datetime import datetime
from history import Base

'''
sqlite3 table schema
CREATE TABLE IF NOT EXISTS "history" ("time" INTEGER NOT NULL, "id" TEXT NOT NULL, "pop_ping_drop_rate" REAL, "pop_ping_latency_ms" REAL, "downlink_throughput_bps" REAL, "uplink_throughput_bps" REAL, "snr" REAL, "scheduled" BOOLEAN, "obstructed" BOOLEAN, "counter" INTEGER, PRIMARY KEY("time","id"));

0|time|INTEGER|1||1
1|id|TEXT|1||2
2|pop_ping_drop_rate|REAL|0||0
3|pop_ping_latency_ms|REAL|0||0
4|downlink_throughput_bps|REAL|0||0
5|uplink_throughput_bps|REAL|0||0
6|snr|REAL|0||0
7|scheduled|BOOLEAN|0||0
8|obstructed|BOOLEAN|0||0
9|counter|INTEGER|0||0
'''

class HistoryTable(Base):
    __tablename__ = "history"

    id: Mapped[int] = mapped_column(primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, unique=True)
    latency: Mapped[float] = mapped_column(Float)
    uptime: Mapped[float] = mapped_column(Float)
    rx: Mapped[int] = mapped_column(Integer)
    tx: Mapped[int] = mapped_column(Integer)
    state: Mapped[str] = mapped_column(Text)

    def __repr__(self) -> str:
        return f'HistoryTable(timestamp={self.timestamp!r}, latency={id.latency!r}'

    def __init__(self, config=None, engine=None, conn=None):
        self._engine = engine
        self._conn = conn

        if config is None:
            self._cycle_start_day = 27
        else:
            self._cycle_start_day = config.billing_date

    def _create_database(self):
        try:
            self.metadata.create_all(self._engine)
        except exc.OperationalError:
            db_type = self._db.split(':')[0]; # Find the database type
            db_name = self._db.split('/')[-1] # Find the database name
            db_server = self._db.split('/')[-2] # Find the server
            print('Database error, attempting to create')
            engine = create_engine(f'{db_type}://{db_server}')
            conn = engine.connect()
            conn.execute(text(f'CREATE DATABASE `{db_name}`;'))
            conn.close()
            #self.connect()
            self.metadata.create_all(self._engine)

    def _remove_ms(self, timestamp) -> datetime:
        return timestamp.replace(microsecond=0)

    def insert_data(self, data, cnt=-1, commit=True):
        ts = self._remove_ms(data._xaxis[cnt])
        try:
            state = data._last_data['state']
        except TypeError:
            state = 'NO STATE AVAILABLE'
        stmt = insert(HistoryTable).values(timestamp=ts,
                                           latency=data._latency[cnt],
                                           uptime=data._avail[cnt],
                                           rx=data._download[cnt],
                                           tx=data._upload[cnt],
                                           state=state)

        try:
            self._conn.execute(stmt)
        except exc.IntegrityError as e:
            print(f'Duplicate entry for {data._xaxis[cnt]}')
            return False
        if commit:
            self._conn.commit()
        return True


#    @property
#    def engine(self):
#        return self._engine

#    @engine.setter
#    def engine(self, engine):
#        self._engine = engine

#    @property
#    def conn(self):
#        return self._conn

#    @conn.setter
#    def conn(self, conn):
#        self._conn = conn
