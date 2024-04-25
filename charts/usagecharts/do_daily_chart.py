from datetime import datetime, timedelta
import numpy as np
from simplehuman import naturalsize

def do_daily_chart(self):
    now = datetime.now()
    date = self._widgets['today_label1'].get_text()
    if now.minute == self.day_last_update and date == self.last_date:
        return

    sday, eday, cycle_rx, cycle_tx, cycle_latency, cycle_uptime  = self._db.get_cycle_usage()
    labels = []
    day_rx = []
    day_tx = []
    day_total = []
    self.day_ax.clear()
    day = sday

    while day < eday:
        r, t, l, u = self._db.get_usage(day.year, day.month, day.day)
        labels.append(f'{day.year}-{day.month:02}-{day.day:02}')
        day_rx.append(int(r))
        day_tx.append(int(t))
        day_total.append(int(r+t))
        day += timedelta(days=1)

    #width=0.35
    width=1
    x = np.arange(len(labels))
    rect1 = self.day_ax.bar(x - width, day_rx, width, label='RX')
    self.day_ax.bar(x - width, day_tx, width, bottom=day_rx, label='TX')

    self.day_ax.yaxis.set_ticks([0, min(day_total), max(day_total), ], labels=['', naturalsize(min(day_total)), naturalsize(max(day_total))])
    self.day_ax.xaxis.set_ticks([z for z in x if z % 2 != 0], labels=[labels[z] for z in x if z % 2 != 0])
    self.day_ax.legend()
    self.day_fig.autofmt_xdate()
    self.day_ax.set_xlabel('Day')
    #self.day_fig.tight_layout()
    self.day_ax.set_title(f'Updated: {now.hour:02}:{now.minute:02}')
    self.day_canvas.draw()
    self.day_last_update = now.minute
    self.last_date = date
    self._widgets['cycle_usage_label'].set_text(f'{labels[0]} - {labels[-1]}')
