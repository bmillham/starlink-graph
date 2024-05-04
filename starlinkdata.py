from gi.repository import Gdk
import starlink_grpc
import leapseconds
import datetime
import png
import tempfile
import os

class StarlinkData:
    def __init__(self, config=None):
        self._xaxis = []
        self._latency = []
        self._upload = []
        self._download = []
        self._avail = []
        self._outages = []
        self._state = []
        self._outages_by_cause = {}
        self._last_data = None
        self._last_obstructions = None
        self._last_alerts = None
        self._config = config
        self.load_colors(config)

    @staticmethod
    def _color_conv(color):
        rgba_color = Gdk.RGBA()
        rgba_color.parse(color)
        return int(rgba_color.alpha * 255), int(rgba_color.red * 255), int(rgba_color.green * 255), int(rgba_color.blue*255)

    def load_colors(self, config=None):
        self._obstructed_color_a, self._obstructed_color_r, self._obstructed_color_g, self._obstructed_color_b = self._color_conv(
            config.obstructed_color)
        self._unobstructed_color_a, self._unobstructed_color_r, self._unobstructed_color_g, self._unobstructed_color_b = self._color_conv(
            config.unobstructed_color)
        self._no_data_color_a, self._no_data_color_r, self._no_data_color_g, self._no_data_color_b = self._color_conv(
            config.no_data_color)

    def current_data(self, db=None):
        if db is not None:
            row = db.current_data()
            print(f'{row=}')
            if row is None:
                self._last_data = None
                return
            self._last_data = {'datetimestamp_utc': datetime.datetime.fromtimestamp(row.time),
                               'downlink_throughput_bps': row.downlink_throughput_bps,
                               'pop_ping_latency_ms': row.pop_ping_latency_ms,
                               'pop_ping_drop_rate': row.pop_ping_drop_rate,
                               'uplink_throughput_bps': row.uplink_throughput_bps,
                               'state': row.state}
        else:
            try:
               self._last_data, self._last_obstructions, self._last_alerts = starlink_grpc.status_data()
            except:
                self._last_data = {'downlink_throughput_bps': 0,
                                   'pop_ping_latency_ms': 0,
                                   'pop_ping_drop_rate': 0,
                                   'uplink_throughput_bps': 0,
                                   'state': 'UNKNOWN'}
            self._last_data['datetimestamp_utc'] = datetime.datetime.now().astimezone()

        self._xaxis.append(self._last_data['datetimestamp_utc'])
        self._latency.append(self._last_data['pop_ping_latency_ms'])
        self._upload.append(self._last_data['uplink_throughput_bps'])
        self._download.append(self._last_data['downlink_throughput_bps'])
        if db:
            self._avail.append(100 - (self._last_data['pop_ping_drop_rate'] * 100))
        else:
            self._avail.append(100 - (self._last_data['pop_ping_drop_rate'] * 100))
        self.pop_history()

    def pop_history(self):
        last = self._xaxis[-1].replace(microsecond=0).replace(tzinfo=self._xaxis[0].tzinfo)
        while (last - self._xaxis[0]).seconds > self._config.history:
            self._xaxis.pop(0)
            self._latency.pop(0)
            self._upload.pop(0)
            self._download.pop(0)
            self._avail.pop(0)

    def _clear_stats(self):
        self._xaxis.clear()
        self._latency.clear()
        self._upload.clear()
        self._avail.clear()
        self._download.clear()

    def _gps_to_gmt(self, timestamp):
         # Convert GPS time to GMT.
        tzoff = datetime.datetime.now().astimezone().utcoffset().total_seconds()
        return leapseconds.gps_to_utc(datetime.datetime(1980,1,6) +
                                      datetime.timedelta(seconds=(timestamp/1000000000)+tzoff))

    def history(self, db=None):
        if db is not None:
            self._clear_stats()
            for row in  db.get_history_bulk_data():
                stamp = datetime.datetime.fromtimestamp(row.time)
                ts = stamp.replace(microsecond=0).replace(tzinfo=stamp.tzinfo)
                self._xaxis.append(ts.replace(tzinfo=stamp.tzinfo))
                self._latency.append(row.pop_ping_latency_ms)
                self._avail.append(100 - (row.pop_ping_drop_rate * 100))
                self._download.append(row.downlink_throughput_bps)
                self._upload.append(row.uplink_throughput_bps)
                self._state.append(row.state)
            return

        z = starlink_grpc.history_bulk_data(self._config.history)[1]
        seconds = self._config.history
        dtstart = datetime.datetime.now().astimezone() - datetime.timedelta(seconds=seconds)
        self._clear_stats()
        for i in range(0, seconds-1):
            try:
                l = {k: z[k][i] for k in z.keys()}
            except IndexError:
                l = 0
            self._xaxis.append(dtstart)
            try:
                if l['pop_ping_latency_ms'] is None:
                    self._latency.append(0)
                else:
                    self._latency.append(l['pop_ping_latency_ms'])
                self._download.append(l['downlink_throughput_bps'])
                self._upload.append(l['uplink_throughput_bps'])
                self._avail.append(100 - (l['pop_ping_drop_rate'] * 100))
            except:
                self._latency.append(0)
                self._download.append(0)
                self._upload.append(0)
                self._avail.append(0)
            dtstart += datetime.timedelta(seconds=1)

    def outages(self, min_duration=None):
        if min_duration is None:
            min_duration = self._config.duration
        # Clear old data
        self._outages.clear()
        self._outages_by_cause.clear()
        try:
            history = starlink_grpc.get_history()
        except:
            print('No history returned')
            return
        for o in history.outages:
            fix = self._gps_to_gmt(o.start_timestamp_ns)
            cause = o.Cause.Name(o.cause)
            duration =  o.duration_ns/1000000000
            # The starlink page ignores outages less than 2 seconds. So do the same.
            if duration < min_duration:
                continue
            self._outages.append({'time': fix,
                                  'cause': cause,
                                  'duration': duration})
            if cause not in self._outages_by_cause:
                self._outages_by_cause[cause] = duration
            else:
                self._outages_by_cause[cause] += duration

    def obstruction_map(self, config=None):
        try:
            snr_data = starlink_grpc.obstruction_map()
        except:
            print('Error getting obstructions')
            return False

        # Code lifted from starlink_grpc_tools/dish_obstruction_map.py
        def pixel_bytes(row):
            for point in row:
                if point > 1.0:
                    # shouldn't happen, but just in case...
                    point = 1.0

                if point >= 0.0:
                    yield round(point * self._unobstructed_color_r +
                            (1.0-point) * self._obstructed_color_r)
                    yield round(point * self._unobstructed_color_g +
                                (1.0-point) * self._obstructed_color_g)
                    yield round(point * self._unobstructed_color_b +
                                (1.0-point) * self._obstructed_color_b)
                    yield round(point * self._unobstructed_color_a +
                                (1.0-point) * self._obstructed_color_a)
                else:
                    yield self._no_data_color_r
                    yield self._no_data_color_g
                    yield self._no_data_color_b
                    yield self._no_data_color_a

        writer = png.Writer(len(snr_data[0]),
                            len(snr_data),
                            alpha=True,
                            greyscale=False)
        if config.obstructionhistorylocation != '':
            name_template = f'obstruction_{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}.png'
            tfname = os.path.join(config.obstructionhistorylocation, name_template)
            thandle = os.open(tfname, os.O_RDWR | os.O_CREAT)
        else:
            thandle, tfname = tempfile.mkstemp()
        with os.fdopen(thandle, "wb") as f:
            writer.write(f, (bytes(pixel_bytes(row)) for row in snr_data))
        return tfname
