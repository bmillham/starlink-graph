from sqlalchemy import create_engine, MetaData, Boolean, select
from sqlalchemy import Text, REAL, insert, DateTime, Float
from sqlalchemy.orm import Mapped, DeclarativeBase
from sqlalchemy.orm import mapped_column
from sqlalchemy import exc
from datetime import datetime, timedelta, timezone
import dateutil.relativedelta
import leapseconds
from . import Base

class OutagesTable(Base):
    __tablename__ = "outages"

    start_timestamp: Mapped[datetime] = mapped_column(DateTime,
                                                      unique=True,
                                                      primary_key=True)
    cause: Mapped[str] = mapped_column(Text)
    duration: Mapped[float] = mapped_column(Float)
    did_switch: Mapped[bool] = mapped_column(Boolean)

    def __init__(self, config=None, engine=None, conn=None):
        self._engine = engine
        self._conn = conn
        self.last_timestamp_ns = 0
        self.last_timestamp = datetime(1980, 1, 1, 0, 0, 0)

    def _create_table(self):
        try:
            self.metadata.create_all(self._engine)
        except exc.OperationalError:
            print('Unable to create outages table')

    def insert_data(self, data):
        def _gps_to_gmt(timestamp):
            # Convert GPS time to GMT.
            tzoff = datetime.now().astimezone().utcoffset().total_seconds()
            return leapseconds.gps_to_utc(datetime(1980,1,6) +
                                      timedelta(seconds=(timestamp/1000000000)+tzoff))
        for d in data:
            ts = _gps_to_gmt(d.start_timestamp_ns)
            if ts > self.last_timestamp:
                stmt = insert(OutagesTable).values(cause=d.Cause.Name(d.cause),
                                                   did_switch=d.did_switch,
                                                   start_timestamp=ts,
                                                   duration=d.duration_ns/1000000000
                                                   )
                try:
                    self._conn.execute(stmt)
                except Exception as e:
                    print(f'Exception outage {e.params}')
                finally:
                    self._conn.commit()
                    self.last_timestamp = ts
        return True

    def get_all_outages(self):
        start_time = datetime.now() + timedelta(hours=-12)
        stmt = select(OutagesTable).where(start_time >= start_time)
        res = self._conn.execute(stmt)
        return res.fetchall() 
