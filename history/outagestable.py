from sqlalchemy import create_engine, MetaData, Boolean
from sqlalchemy import Text, REAL, insert
from sqlalchemy.orm import Mapped, DeclarativeBase
from sqlalchemy.orm import mapped_column
from sqlalchemy import exc
from datetime import datetime, timedelta, timezone
import dateutil.relativedelta
from . import Base

class OutagesTable(Base):
    __tablename__ = "outages"

    start_timestamp_ns: Mapped[float] = mapped_column(REAL, unique=True, primary_key=True)
    cause: Mapped[str] = mapped_column(Text)
    duration_ns: Mapped[float] = mapped_column(REAL)
    did_switch: Mapped[bool] = mapped_column(Boolean)

    def __init__(self, config=None, engine=None, conn=None):
        self._engine = engine
        self._conn = conn
        self.last_timestamp_ns = 0

    def _create_table(self):
        try:
            self.metadata.create_all(self._engine)
        except exc.OperationalError:
            print('Unable to create outages table')

    def insert_data(self, data):
        for d in data:
            if d.start_timestamp_ns > self.last_timestamp_ns:
                stmt = insert(OutagesTable).values(cause=d.Cause.Name(d.cause),
                                                   start_timestamp_ns=d.start_timestamp_ns,
                                                   duration_ns=d.duration_ns,
                                                   did_switch=d.did_switch
                                                   )
                try:
                    self._conn.execute(stmt)
                except Exception as e:
                    print(f'Exception outage')
                finally:
                    self._conn.commit()
                    self.last_timestamp_ns = d.start_timestamp_ns
        return True
