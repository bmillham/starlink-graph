import datetime
import numpy as np
from SimpleHuman import naturalsize

def do_daily_chart(self):
    now = datetime.datetime.now()
    date = self._widgets['today_label1'].get_text()
    if now.minute == self.day_last_update and date == self.last_date:
        return

    sday, eday, prx, ptx, pavg, puptime, nrx, ntx, nave, nuptime, tave, tuptime = self._db.get_cycle_usage()
    y, m, d = sday.split(' ')[0].split('-')
    cycle_dates = self._db.get_cycle_dates(int(y), int(m), int(d))
    labels = []
    prime_rx = []
    prime_tx = []
    prime_total = []
    nonprime_rx = []
    nonprime_tx = []
    nonprime_total = []
    self.day_ax.clear()
    for day in cycle_dates:
        r, t, l, u = self._db.get_prime_usage(day.year, day.month, day.day)
        labels.append(f'{day.year}-{day.month:02}-{day.day:02}')
        prime_rx.append(r)
        prime_tx.append(t)
        prime_total.append(r+t)
        r, t, l, u = self._db.get_non_prime_usage(day.year, day.month, day.day)
        nonprime_rx.append(r)
        nonprime_tx.append(t)
        nonprime_total.append(r+t)

    width=0.35
    x = np.arange(len(labels))
    rect1 = self.day_ax.bar(x - width/2, prime_rx, width, label='Prime RX')
    self.day_ax.bar(x - width/2, prime_tx, width, bottom=prime_rx, label='Prime TX')
    rect2 = self.day_ax.bar(x + width/2, nonprime_rx, width, label='Non-Prime RX')
    self.day_ax.bar(x + width/2, nonprime_tx, width, bottom=nonprime_rx, label='Non-Prime TX')

    self.day_ax.yaxis.set_ticks([0, min(prime_total), max(prime_total), max(nonprime_total)], labels=['', naturalsize(min(prime_total)), naturalsize(max(prime_total)), naturalsize(max(nonprime_total))])
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
