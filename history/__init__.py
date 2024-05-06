from sqlalchemy import create_engine, select, MetaData, Boolean, text
from sqlalchemy import Table, Column, Integer, DateTime, String, Text, Float, insert, func, and_, or_, desc
from sqlalchemy.orm import Mapped, DeclarativeBase
from sqlalchemy.orm import mapped_column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import exc
from datetime import datetime, timedelta, timezone
import leapseconds
import time
import dateutil.relativedelta
#class Base(DeclarativeBase):
#    pass
Base = declarative_base()
from .historytable import HistoryTable
from .outagestable import OutagesTable
from .statustable import StatusTable
from .pingstatstable import PingStatsTable
from .usagetable import UsageTable

class History():


    def __init__(self, history_db="sqlite+pysqlite:///starlink-history.db", do_echo=False, config=None):

        self._db = history_db
        self._config = config
        self.conn = None
        self.engine = None
        self._do_echo = do_echo
        self._last_commit = 0
        self._commit_interval = 1 # Only commit every X seconds
        self._saved_history = {}
        #self.history_table = HistoryTable(config)
        if config is None:
            self._cycle_start_day = 27
        else:
            self._cycle_start_day = config.billing_date
            self._db = config.database_url
        

    def close(self):
        self.conn.close()

    def connect(self):
        print('Connecting to database')
        try:
            self.engine = create_engine(self._db,
                                        echo=self._do_echo,
                                        future=True)
        except:
            print(f'Failed to create engine to {self._db}')
            self.conn = None
            return

        #self._create_database() # Create the database. Does nothing if the database exists
        #self.history_table.engine = self.engine
        #self.history_table._create_database()
        try:
            self.conn = self.engine.connect()
        except:
            print(f'Failed to connect to {self._db}')
            self.conn = None
        self.history_table = HistoryTable(self._config, engine=self.engine, conn=self.conn)
        #self.history_table.conn = self.conn
        self.history_table._create_table()
        self.status_table = StatusTable(self._config, engine=self.engine, conn=self.conn)
        self.status_table._create_table()
        self.ping_stats_table = PingStatsTable(self._config, engine=self.engine, conn=self.conn)
        self.ping_stats_table._create_table()
        self.usage_table = UsageTable(self._config, engine=self.engine, conn=self.conn)
        self.usage_table._create_table()
        self.outages_table = OutagesTable(self._config, engine=self.engine, conn=self.conn)
        self.outages_table._create_table()
        return

    def commit(self):
        if self.conn is None:
            return
        now = datetime.now().timestamp()
        if now > self._last_commit + self._commit_interval:
            self.conn.commit()
            
            self._last_commit = now


    def insert_data(self, data, cnt=-1, commit=True):
        if self.conn is None:
            return
        self.history_table.insert_data(data, cnt=-1, commit=True)
        #self.ping_stats_table.insert_data(data, cnt=-1, commit=True)

    def populate(self, data):
        if self.conn is None:
            print('No database to populate from')
            return
        cnt = 0
        dups = 0
        inserted = 0
        stmt = select(HistoryTable.timestamp).order_by(HistoryTable.timestamp.desc()).limit(1)
        last = self.conn.execute(stmt).fetchone()

        if last is not None:
            print(f'Populating history to the database from {last.timestamp}')
            lasttime = last.timestamp
        else:
            lasttime = datetime.now() + timedelta(days=-1)
        for i in data._xaxis:
            x = i.replace(microsecond=0)
            if x > lasttime.replace(tzinfo=x.tzinfo):
                try:
                    self.history_table.insert_data(data=data, cnt=cnt)
                except exc.IntegrityError:
                    dups += 1
                else:
                    inserted += 1
            cnt += 1
        self.commit()
    
        print(f'Done populating history. Inserted: {inserted} Dups: {dups}')

    def get_usage(self, syear=None, smonth=None, sday=None, eyear=None, emonth=None, eday=None):
        if self.conn is None:
            return None
        start_date = datetime(syear, smonth, sday)
        if eyear is None:
            end_date = start_date + timedelta(days=1)
        else:
            end_date = datetime(eyear, emonth, eday)
        stmt = select(func.sum(StatusTable.downlink_throughput_bps),
                      func.sum(StatusTable.uplink_throughput_bps),
                      func.avg(StatusTable.pop_ping_latency_ms),
                      func.avg(StatusTable.pop_ping_drop_rate)).where(
                          and_(
                              StatusTable.time >= datetime.timestamp(start_date),
                              StatusTable.time < datetime.timestamp(end_date))
                      )
                     

        row = self.conn.execute(stmt).fetchone()
        return (row[0] / 8.0 if row[0] is not None else 0, row[1] / 8.0 if row[1] is not None else 0,
                0 if row[2] is None else row[2], 0 if row[3] is None else row[3])


    def get_cycle_usage(self, month=None, year=None):
        if self.conn is None:
            return None
        now = datetime.now()
        if month is not None or year is not None:
            now = datetime(year=year, month=month, day=1)

        # Last day of the billing cycle
        last_date = now.replace(day=self.billing_date)
        # Move to next month if after the billing date
        if now.day >= self.billing_date:
            last_date += dateutil.relativedelta.relativedelta(months=1)

        # First day of the billing cycle
        first_date = last_date + dateutil.relativedelta.relativedelta(months=-1)

        total = self.get_usage(syear=first_date.year, smonth=first_date.month, sday=first_date.day,
                               eyear=last_date.year, emonth=last_date.month, eday=last_date.day)
        return (first_date, last_date,
                total[0], total[1], total[2], total[3])

    def query_counter(self, opts, gstate, column, table):
        now = time.time()
        stmt = select(HistoryTable.time, HistoryTable.counter).where(and_(
            HistoryTable.time < now,
            HistoryTable.id == gstate.dish_id)).order_by(HistoryTable.time.desc()).limit(1)
        row = self.conn.execute(stmt).fetchone()
        if row is None:
            return 0, None
        else:
            return row
                      
    def get_hour_usage(self, year, month, day, hour):
        if self.conn is None:
            return None
        start = datetime(year, month, day, hour)
        end = start + timedelta(hours=1)
        stmt = select(func.sum(StatusTable.downlink_throughput_bps),
                      func.sum(StatusTable.uplink_throughput_bps),
                      func.avg(StatusTable.pop_ping_latency_ms),
                      func.avg(StatusTable.pop_ping_drop_rate)).where(and_(
                          StatusTable.time >= datetime.timestamp(start),
                          StatusTable.time < datetime.timestamp(end)))

        row = self.conn.execute(stmt).fetchone()
        return row

    def current_data(self):
        if self.conn is None:
            return None

        self.conn.commit()
        stmt = select(StatusTable).order_by(StatusTable.time.desc()).limit(1)
        row = self.conn.execute(stmt).fetchone()
        return row

    def get_history_bulk_data(self):
        if self.conn is None:
            return None
        end = datetime.now()
        start = end - timedelta(seconds=self._config.history)
        print(f'Reading bulk data from {start} to {end} from the database')

        stmt = select(StatusTable.time,
                      StatusTable.uplink_throughput_bps,
                      StatusTable.downlink_throughput_bps,
                      StatusTable.pop_ping_latency_ms,
                      StatusTable.pop_ping_drop_rate,
                      StatusTable.state).where(and_(
                          StatusTable.time >= datetime.timestamp(start),
                          StatusTable.time <= datetime.timestamp(end)))
        return self.conn.execute(stmt).fetchall()

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

    @property
    def software_version(self):
        stmt = select(StatusTable.software_version).order_by(StatusTable.time.desc()).limit(1)
        version = self.conn.execute(stmt).fetchone()
        return version.software_version

    @property
    def dish_info(self):
        stmt = select(StatusTable.id,
                      StatusTable.hardware_version,
                      StatusTable.software_version,
                      StatusTable.uptime).order_by(StatusTable.time.desc()).limit(1)
        info = self.conn.execute(stmt).fetchone()
        return info
