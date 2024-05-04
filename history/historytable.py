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

    time: Mapped[int] = mapped_column(primary_key=True)
    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    pop_ping_drop_rate: Mapped[float] = mapped_column(Float)
    pop_ping_latency_ms: Mapped[float] = mapped_column(Float)
    downlink_throughput_bps: Mapped[float] = mapped_column(Float)
    uplink_throughput_bps: Mapped[float] = mapped_column(Float)
    snr: Mapped[float | None] = mapped_column(Float)
    scheduled: Mapped[bool | None] = mapped_column(Boolean)
    obstructed: Mapped[bool | None] = mapped_column(Boolean)
    counter: Mapped[int] = mapped_column()

    def __repr__(self) -> str:
        return f'HistoryTable(timestamp={self.timestamp!r}, latency={id.latency!r}'

    def __init__(self, config=None, engine=None, conn=None):
        self._engine = engine
        self._conn = conn

    def _create_table(self):
        try:
            self.metadata.create_all(self._engine)
        except exc.OperationalError:
            print('Error creating history table')

    def insert_data(self, data, commit=True):
        stmt = insert(HistoryTable).values(time=data[0],
                                           id=data[1],
                                           pop_ping_drop_rate=data[2],
                                           pop_ping_latency_ms=data[3],
                                           downlink_throughput_bps=data[4],
                                           uplink_throughput_bps=data[5],
                                           snr=data[6],
                                           scheduled=data[7],
                                           obstructed=data[8],
                                           counter=data[9])
        try:
            self._conn.execute(stmt)
        except exc.IntegrityError as e:
            print(f'Duplicate entry for {data}')
            return False
        if commit:
            self._conn.commit()
        return True

