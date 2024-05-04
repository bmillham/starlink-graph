from sqlalchemy import create_engine, select, MetaData, Boolean, text
from sqlalchemy import Table, Column, Integer, DateTime, String, Text, Float, insert, func, and_, or_
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import exc
from datetime import datetime
from history import Base

'''
sqlite> pragma table_info(usage);
0|time|INTEGER|1||1
1|id|TEXT|1||2
2|download_usage|INTEGER|0||0
3|upload_usage|INTEGER|0||0
sqlite> .schema usage
CREATE TABLE IF NOT EXISTS "usage" ("time" INTEGER NOT NULL, "id" TEXT NOT NULL, "download_usage" INTEGER, "upload_usage" INTEGER, PRIMARY KEY("time","id"));

'''

class UsageTable(Base):
    __tablename__ = "usage"

    time: Mapped[int] = mapped_column(primary_key=True)
    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    download_usage: Mapped[int] = mapped_column()
    upload_usage: Mapped[int] = mapped_column()

    def __repr__(self) -> str:
        return f'UsageTable(timestamp={self.time!r}, latency={self.id}'

    def __init__(self, config=None, engine=None, conn=None):
        self._engine = engine
        self._conn = conn

    def _create_table(self):
        try:
            self.metadata.create_all(self._engine)
        except exc.OperationalError:
            print('Error creating usage table')

    def insert_data(self, timestamp, dish_id, data, commit=True):
        stmt = insert(UsageTable).values(time=timestamp,
                                         id=dish_id,
                                         download_usage=data['download_usage'],
                                         upload_usage=data['upload_usage'])
        try:
            self._conn.execute(stmt)
        except exc.IntegrityError as e:
            print(f'Error {e} inserting {data} in UsageTable')
            return False
        if commit:
            self._conn.commit()
        return True


