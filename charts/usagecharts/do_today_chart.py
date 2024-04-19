import datetime
import numpy as np
from simplehuman import naturalsize
from statistics import mean, StatisticsError

def do_today_chart(self):
    now = datetime.datetime.now()
    minute = now.minute
    hour = now.hour
    date = self._widgets['today_label1'].get_text()
    year, month, day = date.split('-')
    year = int(year)
    month = int(month)
    day = int(day)
    if minute == self.today_last_update and date == self.last_date:
        return

    if self.last_date == date and day != now.day:
        self.today_ax.set_title('Will not auto update')
        self.today_canvas.draw()
        self.today_last_update = minute
        return

    #prime_rx, prime_tx, l, u = self._db.get_usage(syear=year, smonth=month, sday=day, prime=True)
    #nonprime_rx, nonprime_tx, l, u = self._db.get_usage(syear=year, smonth=month, sday=day)
    total_rx, total_tx, l, u = self._db.get_usage(syear=year, smonth=month, sday=day)

    self.today_ax.clear()

    if total_rx == 0 and total_tx == 0:
        self.today_ax.set_title('No data for this date')
        #self.today_fig.tight_layout()
        self.today_canvas.draw()
        self.today_last_update = minute
        self.last_date = date
        return

    self.update_usage_chart(self.today_usage_ax, total_rx, total_tx, '')

    for i in range(1, 4):
        self._widgets[f'today_label{i}'].set_text(f'{now.year}-{now.month:02}-{now.day:02}')
        self._widgets[f'updated_label{i}'].set_text(f'{now.hour:02}:{now.minute:02}')
    width = 0.35
    rx = []
    tx = []
    latency = []
    uptime = []
    for h in range(24):
        if day == now.day and h > now.hour:
            break
        r, t, a, u = self._db.get_hour_usage(year, month, day, h)
        rx.append(r)
        tx.append(t)
        if a > 0:
            latency.append(a)
        uptime.append(u)

    max_hour = h
    self._widgets['average_latency_label'].set_text(f'{mean(latency):.0f}ms')
    self._widgets['min_latency_label'].set_text(f'{min(latency):.0f}ms')
    self._widgets['max_latency_label'].set_text(f'{max(latency):.0f}ms')
    self._widgets['uptime_label'].set_text(f'{mean(uptime):.1f}%')
    x = np.arange(len(rx))
    rects1 = self.today_ax.bar(x - width/2, rx, width, label='RX')
    rects2 = self.today_ax.bar(x + width/2, tx, width, label='TX')
    self.today_ax.legend()
    m = [max(rx), max(tx)]
    self.today_ax.yaxis.set_ticks([0, min(m), max(m)], labels=['', naturalsize(min(m)), naturalsize(max(m))])
    if len(rx) > 7:
        self.today_ax.xaxis.set_ticks([x for x in range(max_hour + 1) if x % 2 != 0], labels=[f'{x:02}' for x in range(max_hour +1) if x % 2 != 0])
    else:

        self.today_ax.xaxis.set_ticks([x for x in range(len(rx))], labels=[f'{x:02}' for x in range(len(rx))])
    self.today_ax.bar_label(rects1, padding=3, labels=[naturalsize(x) if x > 0 else "" for x in rects1.datavalues], rotation=90, fontsize=5)
    self.today_ax.bar_label(rects2, padding=3, labels=[naturalsize(x) if x > 0 else "" for x in rects2.datavalues], rotation=90, fontsize=5)
    self.today_ax.set_xlabel('Hour')
    #self.today_fig.tight_layout()
    self.today_canvas.draw()
    self.today_usage_canvas.draw()
    self.today_last_update = minute
    self.last_date = date


