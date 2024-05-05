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
sqlite> pragma table_info(ping_stats);
0|time|INTEGER|1||1
1|id|TEXT|1||2
2|samples|INTEGER|0||0
3|end_counter|INTEGER|0||0
4|total_ping_drop|REAL|0||0
5|count_full_ping_drop|INTEGER|0||0
6|count_obstructed|INTEGER|0||0
7|total_obstructed_ping_drop|REAL|0||0
8|count_full_obstructed_ping_drop|INTEGER|0||0
9|count_unscheduled|INTEGER|0||0
10|total_unscheduled_ping_drop|REAL|0||0
11|count_full_unscheduled_ping_drop|INTEGER|0||0
12|init_run_fragment|INTEGER|0||0
13|final_run_fragment|INTEGER|0||0
14|run_seconds|INTEGER|0||0
15|run_minutes|INTEGER|0||0
16|mean_all_ping_latency|REAL|0||0
17|deciles_all_ping_latency|REAL|0||0
18|mean_full_ping_latency|REAL|0||0
19|deciles_full_ping_latency|REAL|0||0
20|stdev_full_ping_latency|REAL|0||0
21|load_bucket_samples|INTEGER|0||0
22|load_bucket_min_latency|REAL|0||0
23|load_bucket_median_latency|REAL|0||0
24|load_bucket_max_latency|REAL|0||0

sqlite> .schema ping_stats
CREATE TABLE IF NOT EXISTS "ping_stats" ("time" INTEGER NOT NULL, "id" TEXT NOT NULL, "samples" INTEGER, "end_counter" INTEGER, "total_ping_drop" REAL, "count_full_ping_drop" INTEGER, "count_obstructed" INTEGER, "total_obstructed_ping_drop" REAL, "count_full_obstructed_ping_drop" INTEGER, "count_unscheduled" INTEGER, "total_unscheduled_ping_drop" REAL, "count_full_unscheduled_ping_drop" INTEGER, "init_run_fragment" INTEGER, "final_run_fragment" INTEGER, "run_seconds" INTEGER, "run_minutes" INTEGER, "mean_all_ping_latency" REAL, "deciles_all_ping_latency" REAL, "mean_full_ping_latency" REAL, "deciles_full_ping_latency" REAL, "stdev_full_ping_latency" REAL, "load_bucket_samples" INTEGER, "load_bucket_min_latency" REAL, "load_bucket_median_latency" REAL, "load_bucket_max_latency" REAL, PRIMARY KEY("time","id"));
'''

class PingStatsTable(Base):
    __tablename__ = "ping_stats"

    time: Mapped[int] = mapped_column(primary_key=True)
    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    samples: Mapped[int] = mapped_column()
    end_counter: Mapped[int] = mapped_column()
    total_ping_drop: Mapped[float] = mapped_column(Float)
    count_full_ping_drop: Mapped[int] = mapped_column()
    count_obstructed: Mapped[int] = mapped_column()
    total_obstructed_ping_drop: Mapped[float] = mapped_column(Float)
    count_full_obstructed_ping_drop: Mapped[int] = mapped_column()
    count_unscheduled: Mapped[int] = mapped_column()
    total_unscheduled_ping_drop: Mapped[float] = mapped_column(Float)
    count_full_unscheduled_ping_drop: Mapped[int] = mapped_column()
    init_run_fragment: Mapped[int] = mapped_column()
    final_run_fragment: Mapped[int] = mapped_column()
    run_seconds: Mapped[str] = mapped_column(Text)
    run_minutes: Mapped[str] = mapped_column(Text)
    mean_all_ping_latency: Mapped[float | None] = mapped_column(Float)
    deciles_all_ping_latency: Mapped[str] = mapped_column(Text)
    mean_full_ping_latency: Mapped[str | None] = mapped_column(Text)
    deciles_full_ping_latency: Mapped[str] = mapped_column(Text)
    stdev_full_ping_latency: Mapped[float | None] = mapped_column(Float)
    load_bucket_samples: Mapped[str] = mapped_column(Text)
    load_bucket_min_latency: Mapped[str] = mapped_column(Text)
    load_bucket_median_latency: Mapped[str] = mapped_column(Text)
    load_bucket_max_latency: Mapped[str] = mapped_column(Text)
    
    def __repr__(self) -> str:
        return f'PingStats(timestamp={time!r}, latency={id!r}'

    def __init__(self, config=None, engine=None, conn=None):
        self._engine = engine
        self._conn = conn

    def _create_table(self):
        try:
            self.metadata.create_all(self._engine)
        except exc.OperationalError:
            print('Unable to create ping_status table')

    def insert_data(self, timestamp, dish_id, data, commit=True):
        stmt = insert(PingStatsTable).values(time=timestamp,
                                             id=dish_id,
                                             samples=data['samples'],
                                             end_counter=data['end_counter'],
                                             total_ping_drop=data['total_ping_drop'],
                                             count_full_ping_drop=data['count_full_ping_drop'],
                                             count_obstructed=data['count_obstructed'],
                                             total_obstructed_ping_drop=data['total_obstructed_ping_drop'],
                                             count_full_obstructed_ping_drop=data['count_full_obstructed_ping_drop'],
                                             count_unscheduled=data['count_unscheduled'],
                                             total_unscheduled_ping_drop=data['total_unscheduled_ping_drop'],
                                             count_full_unscheduled_ping_drop=data['count_full_unscheduled_ping_drop'],
                                             init_run_fragment=data['init_run_fragment'],
                                             final_run_fragment=data['final_run_fragment'],
                                             run_seconds=data['run_seconds'],
                                             run_minutes=data['run_minutes'],
                                             mean_all_ping_latency=data['mean_all_ping_latency'],
                                             deciles_all_ping_latency=data['deciles_all_ping_latency'],
                                             mean_full_ping_latency=data['mean_full_ping_latency'],
                                             deciles_full_ping_latency=data['deciles_full_ping_latency'],
                                             stdev_full_ping_latency=data['stdev_full_ping_latency'],
                                             load_bucket_samples=data['load_bucket_samples'],
                                             load_bucket_min_latency=data['load_bucket_min_latency'],
                                             load_bucket_median_latency=data['load_bucket_median_latency'],
                                             load_bucket_max_latency=data['load_bucket_max_latency']
                                             )

        try:
            self._conn.execute(stmt)
        except exc.IntegrityError as e:
            print(f'Error {e} inserting {data=}')
            return False
        if commit:
            self._conn.commit()
        return True

