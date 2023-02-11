from sqlalchemy import create_engine, select, MetaData, Boolean
from sqlalchemy import Table, Column, Integer, DateTime, String, Float, insert, func, and_, or_
from sqlalchemy.orm import Mapped, DeclarativeBase
from sqlalchemy.orm import mapped_column
from sqlalchemy import exc
from datetime import datetime, timedelta, timezone
import dateutil.relativedelta

class Base(DeclarativeBase):
    pass

class History(Base):
    __tablename__ = "history"

    id: Mapped[int] = mapped_column(primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, unique=True)
    latency: Mapped[float] = mapped_column(Float)
    uptime: Mapped[float] = mapped_column(Float)
    rx: Mapped[int] = mapped_column(Integer)
    tx: Mapped[int] = mapped_column(Integer)
    prime: Mapped[bool] = mapped_column(Boolean)

    def __repr__(self) -> str:
        return f'History(timestamp={self.timestamp!r}, letency={id.latency!r}'

    def __init__(self, history_db="starlink-history.db", do_echo=False, config=None):
        self._db = history_db
        self._config = config
        self.conn = None
        self.engine = create_engine("sqlite+pysqlite:///starlink-history3.db",
                                    echo=do_echo,
                                    future=True)
        self._last_commit = 0
        self._commit_interval = 60 # Only commit every X seconds
        self._saved_history_non_prime = {}
        self._saved_history_prime = {}
        if config is None:
            self._prime_start = 7
            self._prime_end = 23
            self._cycle_start_day = 27
        else:
            self._prime_start = config.prime_start
            self._prime_end = config.prime_end
            self._cycle_start_day = config.billing_date
        self._create_database()

    def _create_database(self):
        self.metadata.create_all(self.engine)

    def _insert(self, timestamp, latency, uptime, rx, tx):
        prime = True if timestamp.hour >= self._prime_start and timestamp.hour < self._prime_end else False
        stmt = insert(History).values(timestamp=timestamp.replace(microsecond=0),
                                      latency=latency,
                                      uptime=uptime,
                                      rx=rx,
                                      tx=tx,
                                      prime=prime)
        return stmt

    def connect(self):
        self.conn = self.engine.connect()
        return

        # Old code
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
        if self.conn is not None:
            try:
                self.cursor.execute(INDEX)
            except Error as e:
                print(f'Failed to create index: {e}')

    def commit(self):
        now = datetime.now().timestamp()
        if now > self._last_commit + self._commit_interval:
            self.conn.commit()
            
            self._last_commit = now


    def insert_data(self, data, cnt=-1, commit=True):
        stmt = self._insert(timestamp=data._xaxis[cnt],
                            latency=data._latency[cnt],
                            uptime=data._avail[cnt],
                            rx=data._download[cnt],
                            tx=data._upload[cnt])
        try:
            self.conn.execute(stmt)
        except exc.IntegrityError as e:
            print(f'{e} trying to execute {stmt}')
            return False
        self.commit()
        return True
        

    def populate(self, data):
        cnt = 0
        dups = 0
        inserted = 0
        stmt = select(History.timestamp).order_by(History.timestamp.desc()).limit(1)
        last = self.conn.execute(stmt).fetchone()
        print(f'Populating history to the database from {last.timestamp}')
        for i in data._xaxis:
            x = i.replace(microsecond=0)
            if x > last.timestamp.replace(tzinfo=x.tzinfo):
                stmt = self._insert(timestamp=x.replace(tzinfo=x.tzinfo),
                                   latency=data._latency[cnt],
                                   uptime=data._avail[cnt],
                                   rx=data._download[cnt],
                                   tx=data._upload[cnt])
                try:
                    self.conn.execute(stmt)
                except exc.IntegrityError:
                    dups += 1
                else:
                    inserted += 1
            cnt += 1
        self.commit()
    
        print(f'Done populating history. Inserted: {inserted} Dups: {dups}')

    def get_usage(self, syear=None, smonth=None, sday=None, eyear=None, emonth=None, eday=None, prime=False):
        start_date = datetime(syear, smonth, sday)
        if eyear is None:
            end_date = start_date + timedelta(days=1)
        else:
            end_date = datetime(eyear, emonth, eday)
        if prime is not None:
            stmt = select(func.sum(History.rx),
                          func.sum(History.tx),
                          func.avg(History.latency),
                          func.avg(History.uptime)).where(and_(
                              and_(
                                  History.timestamp >= start_date,
                                  History.timestamp < end_date),
                              History.prime == prime))
        else:
            stmt = select(func.sum(History.rx),
                          func.sum(History.tx),
                          func.avg(History.latency),
                          func.avg(History.uptime)).where(and_(
                              History.timestamp >= start_date,
                              History.timestamp < end_date))

        row = self.conn.execute(stmt).fetchone()
        return (row[0] if row[0] is not None else 0, row[1] if row[1] is not None else 0,
                0 if row[2] is None else row[2], 0 if row[3] is None else row[3])


    def get_cycle_usage(self, month=None, year=None):
        now = datetime.now()
        if month is not None or year is not None:
            now = datetime(year=year, month=month, day=1)
        # Last day of the billing cycle
        last_date = now.replace(day=self.billing_date)
        # First day of the billine cycle
        first_date = last_date + dateutil.relativedelta.relativedelta(months=-1)

        prime = self.get_usage(syear=first_date.year, smonth=first_date.month, sday=first_date.day,
                               eyear=last_date.year, emonth=last_date.month, eday=last_date.day, prime=True)
        nonprime = self.get_usage(syear=first_date.year, smonth=first_date.month, sday=first_date.day,
                                  eyear=last_date.year, emonth=last_date.month, eday=last_date.day, prime=False)
        total = self.get_usage(syear=first_date.year, smonth=first_date.month, sday=first_date.day,
                               eyear=last_date.year, emonth=last_date.month, eday=last_date.day, prime=None)

        return (first_date, last_date,
                prime[0], prime[1], prime[2], prime[3],
                nonprime[0], nonprime[1], nonprime[2], nonprime[3],
                total[2], total[3])

    def get_hour_usage(self, year, month, day, hour):
        start = datetime(year, month, day, hour)
        end = start + timedelta(hours=1)
        stmt = select(func.sum(History.rx),
                      func.sum(History.tx),
                      func.avg(History.latency),
                      func.avg(History.uptime)).where(and_(
                          History.timestamp >= start,
                          History.timestamp < end))

        row = self.conn.execute(stmt).fetchone()
        return (0 if row[0] is None else row[0], 0 if row[1] is None else row[1],
                0 if row[2] is None else row[2], 0 if row[3] is None else row[3])
        
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
