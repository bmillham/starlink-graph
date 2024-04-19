from sqlalchemy import create_engine, select, MetaData, Boolean, text
from sqlalchemy import Table, Column, Integer, DateTime, String, Text, Float, insert, func, and_, or_
from sqlalchemy.orm import Mapped, DeclarativeBase
from sqlalchemy.orm import mapped_column
from sqlalchemy import exc
from datetime import datetime, timedelta, timezone
import dateutil.relativedelta
from . import Base

class OutagesTable(Base):
    __tablename__ = "outages"

    id: Mapped[int] = mapped_column(primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, unique=True)
    cause: Mapped[str] = mapped_column(Text)
    duration: Mapped[float] = mapped_column(Float)

    def __init__(self, config=None):
        self._engine = None
        self._conn = None

    def _create_database(self):
        try:
            self.metadata.create_all(self.engine)
        except exc.OperationalError:
            print('Unable to create outages table')

    def insert_data(self, timestamp=None, cause=None, duration=None):
        ts = self._remove_ms(data._xaxis[cnt])
        stmt = insert(OutagesTable).values(timestamp=ts,
                                           cause=cause,
                                           duration=duration)
