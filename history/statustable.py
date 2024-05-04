from sqlalchemy import create_engine, select, MetaData, Boolean, text
from sqlalchemy import Table, Column, Integer, DateTime, String, Text, Float, insert, func, and_, or_
from sqlalchemy.orm import Mapped, DeclarativeBase
from sqlalchemy.orm import mapped_column
from sqlalchemy import exc
from datetime import datetime, timedelta, timezone
import dateutil.relativedelta
from . import Base

'''
sqlite> .schema status
CREATE TABLE IF NOT EXISTS "status" ("time" INTEGER NOT NULL, "id" TEXT NOT NULL, "hardware_version" TEXT, "software_version" TEXT, "state" TEXT, "uptime" INTEGER, "snr" REAL, "seconds_to_first_nonempty_slot" REAL, "pop_ping_drop_rate" REAL, "downlink_throughput_bps" REAL, "uplink_throughput_bps" REAL, "pop_ping_latency_ms" REAL, "alerts" INTEGER, "fraction_obstructed" REAL, "currently_obstructed" BOOLEAN, "seconds_obstructed" REAL, "obstruction_duration" REAL, "obstruction_interval" REAL, "direction_azimuth" REAL, "direction_elevation" REAL, "is_snr_above_noise_floor" BOOLEAN, "wedges_fraction_obstructed" REAL, "raw_wedges_fraction_obstructed" REAL, "valid_s" REAL, "alert_motors_stuck" BOOLEAN, "alert_thermal_throttle" BOOLEAN, "alert_thermal_shutdown" BOOLEAN, "alert_mast_not_near_vertical" BOOLEAN, "alert_unexpected_location" BOOLEAN, "alert_slow_ethernet_speeds" BOOLEAN, "alert_roaming" BOOLEAN, "alert_install_pending" BOOLEAN, "alert_is_heating" BOOLEAN, "alert_power_supply_thermal_throttle" BOOLEAN, "alert_is_power_save_idle" BOOLEAN, "alert_moving_while_not_mobile" BOOLEAN, "alert_moving_too_fast_for_policy" BOOLEAN, "alert_dbf_telem_stale" BOOLEAN, "alert_low_motor_current" BOOLEAN, "alert_lower_signal_than_predicted" BOOLEAN, "latitude" REAL, "longitude" REAL, "altitude" REAL, PRIMARY KEY("time","id"));
sqlite> pragma table_info(status);
cid|name|type|notnull|dflt_value|pk
0|time|INTEGER|1||1
1|id|TEXT|1||2
2|hardware_version|TEXT|0||0
3|software_version|TEXT|0||0
4|state|TEXT|0||0
5|uptime|INTEGER|0||0
6|snr|REAL|0||0
7|seconds_to_first_nonempty_slot|REAL|0||0
8|pop_ping_drop_rate|REAL|0||0
9|downlink_throughput_bps|REAL|0||0
10|uplink_throughput_bps|REAL|0||0
11|pop_ping_latency_ms|REAL|0||0
12|alerts|INTEGER|0||0
13|fraction_obstructed|REAL|0||0
14|currently_obstructed|BOOLEAN|0||0
15|seconds_obstructed|REAL|0||0
16|obstruction_duration|REAL|0||0
17|obstruction_interval|REAL|0||0
18|direction_azimuth|REAL|0||0
19|direction_elevation|REAL|0||0
20|is_snr_above_noise_floor|BOOLEAN|0||0
21|wedges_fraction_obstructed|REAL|0||0
22|raw_wedges_fraction_obstructed|REAL|0||0
23|valid_s|REAL|0||0
24|alert_motors_stuck|BOOLEAN|0||0
25|alert_thermal_throttle|BOOLEAN|0||0
26|alert_thermal_shutdown|BOOLEAN|0||0
27|alert_mast_not_near_vertical|BOOLEAN|0||0
28|alert_unexpected_location|BOOLEAN|0||0
29|alert_slow_ethernet_speeds|BOOLEAN|0||0
30|alert_roaming|BOOLEAN|0||0
31|alert_install_pending|BOOLEAN|0||0
32|alert_is_heating|BOOLEAN|0||0
33|alert_power_supply_thermal_throttle|BOOLEAN|0||0
34|alert_is_power_save_idle|BOOLEAN|0||0
35|alert_moving_while_not_mobile|BOOLEAN|0||0
36|alert_moving_too_fast_for_policy|BOOLEAN|0||0
37|alert_dbf_telem_stale|BOOLEAN|0||0
38|alert_low_motor_current|BOOLEAN|0||0
39|alert_lower_signal_than_predicted|BOOLEAN|0||0
40|latitude|REAL|0||0
41|longitude|REAL|0||0
42|altitude|REAL|0||0
'''

class StatusTable(Base):
    __tablename__ = "status"

    time: Mapped[int] = mapped_column(primary_key=True)
    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    hardware_version: Mapped[str] = mapped_column(Text)
    software_version: Mapped[str] = mapped_column(Text)
    state: Mapped[str] = mapped_column(Text)
    uptime: Mapped[int] = mapped_column()
    snr: Mapped[float | None] = mapped_column(Float)
    seconds_to_first_nonempty_slot: Mapped[float] = mapped_column(Float)
    pop_ping_drop_rate: Mapped[float] = mapped_column(Float)
    downlink_throughput_bps: Mapped[float] = mapped_column(Float)
    uplink_throughput_bps: Mapped[float] = mapped_column(Float)
    pop_ping_latency_ms: Mapped[float] = mapped_column(Float)
    alerts: Mapped[int] = mapped_column()
    fraction_obstructed: Mapped[float] = mapped_column(Float)
    currently_obstructed: Mapped[bool] = mapped_column(Boolean)
    seconds_obstructed: Mapped[float | None] = mapped_column(Float)
    obstruction_duration: Mapped[float | None] = mapped_column(Float)
    obstruction_interval: Mapped[float | None] = mapped_column(Float)
    direction_azimuth: Mapped[float] = mapped_column(Float)
    direction_elevation: Mapped[float] = mapped_column(Float)
    is_snr_above_noise_floor: Mapped[bool] = mapped_column(Boolean)
    wedges_fraction_obstructed: Mapped[str] = mapped_column(Text)
    raw_wedges_fraction_obstructed: Mapped[str] = mapped_column(Text)
    valid_s: Mapped[float] = mapped_column(Float)
    alert_motors_stuck: Mapped[bool] = mapped_column(Boolean)
    alert_thermal_throttle: Mapped[bool] = mapped_column(Boolean)
    alert_thermal_shutdown: Mapped[bool] = mapped_column(Boolean)
    alert_mast_not_near_vertical: Mapped[bool] = mapped_column(Boolean)
    alert_unexpected_location: Mapped[bool] = mapped_column(Boolean)
    alert_slow_ethernet_speeds: Mapped[bool] = mapped_column(Boolean)
    alert_roaming: Mapped[bool] = mapped_column(Boolean)
    alert_install_pending: Mapped[bool] = mapped_column(Boolean)
    alert_is_heating: Mapped[bool] = mapped_column(Boolean)
    alert_power_supply_thermal_throttle: Mapped[bool] = mapped_column(Boolean)
    alert_is_power_save_idle: Mapped[bool] = mapped_column(Boolean)
    alert_moving_while_not_mobile: Mapped[bool] = mapped_column(Boolean)
    alert_moving_too_fast_for_policy: Mapped[bool] = mapped_column(Boolean)
    alert_dbf_telem_stale: Mapped[bool] = mapped_column(Boolean)
    alert_low_motor_current: Mapped[bool] = mapped_column(Boolean)
    alert_lower_signal_than_predicted: Mapped[bool] = mapped_column(Boolean)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    altitude: Mapped[float] = mapped_column(Float)

    def __init__(self, config=None, engine=None, conn=None):
        self._engine = engine
        self._conn = conn

    def _create_table(self):
        try:
            self.metadata.create_all(self._engine)
        except exc.OperationalError:
            print('Unable to create status table')

    def insert_data(self, timestamp, dish_id, data, commit=True):
        stmt = insert(StatusTable).values(time=timestamp,
                                          id=dish_id,
                                          hardware_version=data['hardware_version'],
                                          software_version=data['software_version'],
                                          state=data['state'],
                                          uptime=data['uptime'],
                                          snr=data['snr'],
                                          seconds_to_first_nonempty_slot=data['seconds_to_first_nonempty_slot'],
                                          pop_ping_drop_rate=data['pop_ping_drop_rate'],
                                          downlink_throughput_bps=data['downlink_throughput_bps'],
                                          uplink_throughput_bps=data['uplink_throughput_bps'],
                                          pop_ping_latency_ms=data['pop_ping_latency_ms'],
                                          alerts=data['alerts'],
                                          fraction_obstructed=data['fraction_obstructed'],
                                          currently_obstructed=data['currently_obstructed'],
                                          seconds_obstructed=data['seconds_obstructed'],
                                          obstruction_duration=data['obstruction_duration'],
                                          obstruction_interval=data['obstruction_interval'],
                                          direction_azimuth=data['direction_azimuth'],
                                          direction_elevation=data['direction_elevation'],
                                          is_snr_above_noise_floor=data['is_snr_above_noise_floor'],
                                          wedges_fraction_obstructed=data['wedges_fraction_obstructed'],
                                          raw_wedges_fraction_obstructed=data['raw_wedges_fraction_obstructed'],
                                          valid_s=data['valid_s'],
                                          alert_motors_stuck=data['alert_motors_stuck'],
                                          alert_thermal_throttle=data['alert_thermal_throttle'],
                                          alert_thermal_shutdown=data['alert_thermal_shutdown'],
                                          alert_mast_not_near_vertical=data['alert_mast_not_near_vertical'],
                                          alert_unexpected_location=data['alert_unexpected_location'],
                                          alert_slow_ethernet_speeds=data['alert_slow_ethernet_speeds'],
                                          alert_roaming=data['alert_roaming'],
                                          alert_install_pending=data['alert_install_pending'],
                                          alert_is_heating=data['alert_is_heating'],
                                          alert_power_supply_thermal_throttle=data['alert_power_supply_thermal_throttle'],
                                          alert_is_power_save_idle=data['alert_is_power_save_idle'],

                                          alert_moving_while_not_mobile=data['alert_moving_while_not_mobile'],
                                          alert_moving_too_fast_for_policy=data['alert_moving_too_fast_for_policy'],
                                          alert_dbf_telem_stale=data['alert_dbf_telem_stale'],
                                          alert_low_motor_current=data['alert_low_motor_current'],
                                          alert_lower_signal_than_predicted=data['alert_lower_signal_than_predicted'],
                                          latitude=data['latitude'],
                                          longitude=data['longitude'],
                                          altitude=data['altitude'])
        
        try:
            self._conn.execute(stmt)
        except exc.IntegrityError as e:
            print(f'Error {e}')
            return False
        except Exception as e:
            print(f'Other exception {e}')
        if commit:
            self._conn.commit()
        return True
