#!/usr/bin/python3

# starlink-graph.py
# (C) 2022: Brian Millham

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from matplotlib.figure import Figure
from matplotlib.backends.backend_gtk3agg import (FigureCanvasGTK3Agg as FigureCanvas)
import matplotlib.animation as animation
import datetime
from statistics import mean, StatisticsError
import argparse
import sys
import leapseconds

# Use humanize if it's available. Install with
# pip3 install humanize
try:
    from humanize import naturalsize
    from humanize.time import naturaldelta
except ModuleNotFoundError:
    print('Humazine module not installed. Install with pip3')
    # Use a tacky simple naturalsize
    def naturalsize(x): return f"{x:.1f} kB"
    def naturaldelta(x): return x

class Window1Signals:
    def on_window1_destroy(self, widget):
        Gtk.main_quit()
    def on_about_dialog_click(self, widget):
        # Show current dish info
        z = get_data()[0]
        aboutdialog.set_comments(f'Dishy: {z["software_version"]}\nUptime: {naturaldelta(z["uptime"])}')
        aboutdialog.show()
    def on_about_close_button(self, widget):
        aboutdialog.hide()
        return True
    def on_outage_clicked(self, widget):
        outagestore.clear()
        for out in outages:
                outagestore.append([out['time'].strftime("%I:%M%p"), out['cause'], str(out['duration'])])
        outagewindow.show()
    def outage_close(self, *args, **kwargs):
        outagewindow.hide()
        return True

parser = argparse.ArgumentParser(
        description="Watch various Starlink status"
        )
parser.add_argument('-H', '--host',
                    default='192.168.100.1',
                    help='IP of the Starlink dish')
parser.add_argument('-n', '--num-ticks',
                    default=3,
                    type=int,
                    help='Number of ticks to show on the graph')
parser.add_argument('-s', '--samples',
                    default=900,
                    type=int,
                    help='How many seconds of history to keep')
parser.add_argument('-l', '--tools-loc',
                    required=False,
                    help='Location of the grps-tools/dish_grpc_text.py script')
parser.add_argument('-u', '--update-interval',
                    default=1000,
                    type=int,
                    help='How often to poll the dish for stats, in milliseconds')
parser.add_argument('-o', '--minimum-outage',
                    default=2.0,
                    type=float,
                    help='Minimum outage time to report')
args = parser.parse_args()

if args.tools_loc:
        sys.path.insert(0, args.tools_loc)

try:
    import starlink_grpc
except:
    print("Unable to import starlink_grpc.!")
    print("Check your PYTHONPATH or use the -l/--tools-loc option")
    exit()

fig = Figure()
availchart = fig.add_subplot(4,1,1)
latencychart = fig.add_subplot(4,1,2)
downchart = fig.add_subplot(4,1,3)
upchart = fig.add_subplot(4,1,4)
builder = Gtk.Builder()
builder.add_from_file("starlink-graph.glade")

builder.connect_signals(Window1Signals())
window = builder.get_object("window1")
sw = builder.get_object("scrolledwindow1")
aboutdialog = builder.get_object('aboutdialog')
outagewindow = builder.get_object('outagewindow')
outagelist = builder.get_object('outagelist')
outagebox = builder.get_object('outagebox')
outagestore = builder.get_object('outagestore')

def ns_time_to_sec(stamp):
    # Convert GPS time to GMT.
    tzoff = datetime.datetime.now().astimezone().utcoffset().total_seconds()
    t = leapseconds.gps_to_utc(datetime.datetime(1980,1,6) +
                               datetime.timedelta(seconds=(stamp/1000000000)+tzoff))
    return t

def get_data(vals=0):
    try:
        z = starlink_grpc.status_data()
    except:
        print('No stats returned!')
        z = []
        z.append({'downlink_throughput_bps': 0,
                  'pop_ping_latency_ms': 0,
                  'pop_ping_drop_rate': 0,
                  'uplink_throughput_bps': 0,
                  'state': 'UNKNOWN'})
    z[0]['datetimestamp_utc'] = datetime.datetime.now().astimezone()
    return z

def get_outages(min_duration=2.0):
    # Clear old data
    outages.clear()
    outages_by_cause.clear()
    try:
        history = starlink_grpc.get_history()
    except:
        print('No history returned')
        return
    for o in history.outages:
        fix = ns_time_to_sec(o.start_timestamp_ns)
        cause = o.Cause.Name(o.cause)
        duration =  o.duration_ns/1000000000
        # The starlink page ignores outages less than 2 seconds. So do the same.
        if duration < min_duration:
            continue
        outages.append({'time': fix,
                        'cause': cause,
                        'duration': duration})
        if cause not in outages_by_cause:
            outages_by_cause[cause] = duration
        else:
            outages_by_cause[cause] += duration

def animate(i):
    data = get_data(vals=1) # Grab the latest data
    download.append(data[0]['downlink_throughput_bps']) # Convert the string to float
    latency.append(data[0]['pop_ping_latency_ms'])
    upload.append(data[0]['uplink_throughput_bps'])
    if data[0]['state'] != 'CONNECTED':
        print(f'Not connected: {data[0]["state"]}@{data[0]["datetimestamp_utc"]}')
        get_outages(args.minimum_outage)
    else:
        # Things are working normally, so only check outages every 5 seconds
        if xar[-1].second % 5 == 0:
            get_outages(args.minimum_outage) # Also get outage history as the current data is not always accurate                
        
    avail.append(100 - (data[0]['pop_ping_drop_rate'] * 100))
    xar.append(data[0]['datetimestamp_utc'])
    # Only keep maxvals (seconds) of samples
    while (xar[-1] - xar[0]).seconds > args.samples:
        xar.pop(0)
        download.pop(0)
        upload.pop(0)
        latency.pop(0)
        avail.pop(0)
    hdl = download[-1]
    hul = upload[-1]
    hmdl = max(download)
    hmul = max(upload)
    # Get averages, excluding an 0 values
    try:
        dlave = mean([z for z in download if z > 0])
        upave = mean([z for z in upload if z > 0])
        latave = mean([z for z in latency if z > 0])
    except StatisticsError:
        dlave = 0
        upave = 0
        latave = 0
        print('No data received')

    daveline = [dlave] * len(xar)
    uaveline = [upave] * len(xar)
    lataveline = [latave] * len(xar)
    savedlave = dlave
    saveupave = upave
    hdl = naturalsize(hdl)
    hmdl = naturalsize(max(download))
    hul = naturalsize(hul)
    umin = naturalsize(min(upload))
    hmul = naturalsize(max(upload))
    dlave = naturalsize(dlave)
    upave = naturalsize(upave)

    availchart.clear()
    availchart.plot(xar, avail, linewidth=1, color='green')
    downchart.clear()
    downchart.plot(xar, download, linewidth=1)
    downchart.plot(xar, daveline, linewidth=1, linestyle='dashed', color='black')
    downchart.legend([f'Last: {hdl}'], loc='upper left')
    upchart.clear()
    upchart.plot(xar, upload, linewidth=1, color='red')
    upchart.plot(xar, uaveline, linewidth=1, color='black', linestyle='dashed')
    upchart.legend([f'Last: {hul}'], loc='upper left')
    latencychart.clear()
    latencychart.plot(xar, latency, linewidth=1, color='green')
    latencychart.plot(xar, lataveline, linewidth=1, color='black', linestyle='dashed')

    latencychart.legend([f'Last: {latency[-1]:.0f} ms'], loc='upper left')

    # Turn off the ticks for up/down charts
    downchart.xaxis.set_ticks([]) 
    latencychart.xaxis.set_ticks([])
    # Set the tick interval
    tick_count = int(len(xar) / (args.num_ticks - 1))
    tick_vals = xar[::tick_count]
    if len(tick_vals) < args.num_ticks:
        tick_vals.append(xar[-1])
    tick_labels = [f'{v.astimezone().strftime("%I:%M%p")}' for v in tick_vals]
    upchart.xaxis.set_ticks(tick_vals, labels=tick_labels)
    # Rotate the tick text
    upchart.xaxis.set_tick_params(rotation=30)
    latencychart.yaxis.set_label_text('Latency\n(ms)')
    latencychart.yaxis.set_label_position('right')
    upchart.yaxis.set_label_text('Upload')
    upchart.yaxis.set_label_position('right')
    downchart.yaxis.set_label_text('Download')
    downchart.yaxis.set_label_position('right')
    availchart.yaxis.set_label_text('Uptime')
    availchart.yaxis.set_label_position('right')
    availchart.xaxis.set_ticks([])
    availchart.set_yticks([100, 0], labels=['100%', '0%'])
    if len(outages_by_cause) == 0:
        availchart.text(xar[0], 10, "No outages in the last 12 hours",
                        bbox={'facecolor': 'green',
                              'alpha': 0.5,
                              'pad': 1})
    else:
        availchart.text(xar[0], 10, "\n".join([f'{k}: {v:.0f}s' for k, v in outages_by_cause.items()]), bbox={
                'facecolor': 'green', 'alpha': 0.5, 'pad': 1})
    upmin = min(upload)
    upmax = max(upload)
    dmin = min(download)
    dmax = max(download)
    upchart.set_yticks([upmin, saveupave, upmax], labels=['', f'Ave:\n{upave}', hmul])
    downchart.set_yticks([dmin, savedlave, dmax], labels=['', f'Ave:\n{dlave}', hmdl])
    try:
        latmin = min([x for x in latency if x != 0.0])
    except:
        latmin = 0
        
    latencychart.set_yticks([latmin, latave, max(latency)],
                            labels=[f'Min: {latmin:.0f}',
                                    f'Ave: {latave:.0f}',
                                    f'Max: {max(latency):.0f}'])
    return True

# On startup, grab the data right away so the graph can be populated.
z1 = starlink_grpc.history_bulk_data(args.samples)
z = z1[1]

xar = []
download = []
upload = []
latency = []
avail = []
outages = []
outages_by_cause = {}

# Fill out the graph with the history
dtstart = datetime.datetime.now().astimezone() - datetime.timedelta(seconds=args.samples)

for i in range(0, args.samples-1):
    l = {k: z[k][i] for k in z.keys()}
    xar.append(dtstart)
    try:
        if l['pop_ping_latency_ms'] is None:
            latency.append(0)
        else:
            latency.append(l['pop_ping_latency_ms'])
        download.append(l['downlink_throughput_bps'])
        upload.append(l['uplink_throughput_bps'])
        avail.append(100 - (l['pop_ping_drop_rate'] * 100))
    except:
        print('something went wrong:', l, dtstart)
        latency.append(0)
        download.append(0)
        upload.append(0)
        avail.append(0)

    dtstart += datetime.timedelta(seconds=1)
# Try and get the outage history

get_outages(args.minimum_outage)

# Force an update right away.
animate(1)

# Create the canvas for matplotlib
canvas = FigureCanvas(fig)
sw.add(canvas)

window.show_all()

ani = animation.FuncAnimation(fig, animate, interval=args.update_interval)
Gtk.main()
