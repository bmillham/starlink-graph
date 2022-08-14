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
import sys
from Config import Config
import os
import time
from Signals import Signals

from SimpleHuman import naturalsize

configfile = 'starlink-graph.ini'
defaultconfigfile = 'starlink-graph-default.ini'
config = Config(configfile=configfile, defaultconfigfile=defaultconfigfile)

#opts = config.opts

if config.grpctools is not None:
    sys.path.insert(0, config.grpctools)

fig = Figure()
availchart = fig.add_subplot(4, 1, 1)
latencychart = fig.add_subplot(4, 1, 2)
downchart = fig.add_subplot(4, 1, 3)
upchart = fig.add_subplot(4, 1, 4)
builder = Gtk.Builder()
builder.add_from_file("starlink-graph.glade")

# Build dict of all widgets with an ID
widgets = {}
for o in builder.get_objects():
    try:
        widgets[Gtk.Buildable.get_name(o)] = o
    except TypeError:
        pass

my_signals = Signals(widgets=widgets, exe_file=__file__, configfile=configfile, config=config)
builder.connect_signals(my_signals)

# Get the options from the ini file
config.set_widget_values(widgets=widgets)


def animate(i):
    sd.current_data()
    if sd._last_data['state'] != 'CONNECTED':
        print(f'Not connected: {sd._last_data["state"]}@{sd._last_data["datetimestamp_utc"]}')
        sd.outages()
    else:
        # Things are working normally, so only check outages every 5 seconds
        if sd._xaxis[-1].second % 5 == 0:
            sd.outages(min_duration=config.duration)

    hdl = sd._download[-1]
    hul = sd._upload[-1]
    hmdl = max(sd._download)
    hmul = max(sd._upload)
    # Get averages, excluding an 0 values
    try:
        dlave = mean([z for z in sd._download if z > 0])
        upave = mean([z for z in sd._upload if z > 0])
        latave = mean([z for z in sd._latency if z > 0])
        availave = mean([z for z in sd._avail])
    except StatisticsError:
        dlave = 0
        upave = 0
        latave = 0
        availave = 0
        print('No data received')

    daveline = [dlave] * len(sd._xaxis)
    uaveline = [upave] * len(sd._xaxis)
    lataveline = [latave] * len(sd._xaxis)
    availave = [availave] * len(sd._xaxis)
    savedlave = dlave
    saveupave = upave
    hdl = naturalsize(hdl)
    hmdl = naturalsize(max(sd._download))
    hul = naturalsize(hul)
    umin = naturalsize(min(sd._upload))
    hmul = naturalsize(max(sd._upload))
    dlave = naturalsize(dlave)
    upave = naturalsize(upave)

    availchart.clear()
    availchart.plot(sd._xaxis, sd._avail, linewidth=1, color='green')
    availchart.plot(sd._xaxis, availave, linewidth=1, linestyle='dotted', color='black')
    downchart.clear()
    downchart.plot(sd._xaxis, sd._download, linewidth=1)
    downchart.plot(sd._xaxis, daveline, linewidth=1, linestyle='dashed', color='black')
    downchart.legend([f'Last: {hdl}'], loc='upper left')
    upchart.clear()
    upchart.plot(sd._xaxis, sd._upload, linewidth=1, color='red')
    upchart.plot(sd._xaxis, uaveline, linewidth=1, color='black', linestyle='dashed')
    upchart.legend([f'Last: {hul}'], loc='upper left')
    latencychart.clear()
    latencychart.plot(sd._xaxis, sd._latency, linewidth=1, color='green')
    latencychart.plot(sd._xaxis, lataveline, linewidth=1, color='black', linestyle='dashed')

    latencychart.legend([f'Last: {sd._latency[-1]:.0f} ms'], loc='upper left')

    # Turn off the ticks for up/down charts
    downchart.xaxis.set_ticks([])
    latencychart.xaxis.set_ticks([])
    # Set the tick interval
    tick_count = int(len(sd._xaxis) / (config.ticks - 1))
    tick_vals = sd._xaxis[::tick_count]
    if len(tick_vals) < config.ticks:
        tick_vals.append(sd._xaxis[-1])
    tick_labels = [f'{v.astimezone().strftime("%I:%M%p")}' for v in tick_vals]
    upchart.xaxis.set_ticks(tick_vals, labels=tick_labels)
    # Rotate the tick text
    # upchart.xaxis.set_tick_params(rotation=30)
    latencychart.yaxis.set_label_text('Latency\n(ms)')
    latencychart.yaxis.set_label_position('right')
    upchart.yaxis.set_label_text('Upload')
    upchart.yaxis.set_label_position('right')
    downchart.yaxis.set_label_text('Download')
    downchart.yaxis.set_label_position('right')
    availchart.yaxis.set_label_text('Uptime')
    availchart.yaxis.set_label_position('right')
    availchart.xaxis.set_ticks([])
    availchart.set_yticks([100, availave[0], 0], labels=[f'{"" if availave[0] > 85.0 else "100%"}',
                                                         f'Ave: {availave[0] / 100:.2%}', '0%'])
    if len(sd._outages_by_cause) == 0:
        availchart.text(sd._xaxis[0], 10, "No outages in the last 12 hours",
                        bbox={'facecolor': 'green',
                              'alpha': 0.5,
                              'pad': 1})
    else:
        availchart.text(sd._xaxis[0], 10, "\n".join([f'{k}: {v:.0f}s' for k, v in sd._outages_by_cause.items()]), bbox={
            'facecolor': 'green', 'alpha': 0.5, 'pad': 1})
    upmin = min(sd._upload)
    upmax = max(sd._upload)
    dmin = min(sd._download)
    dmax = max(sd._download)
    upchart.set_yticks([upmin, saveupave, upmax], labels=['', f'Ave:\n{upave}', hmul])
    downchart.set_yticks([dmin, savedlave, dmax], labels=['', f'Ave:\n{dlave}', hmdl])

    try:
        latmin = min([x for x in sd._latency if x != 0.0])
    except:
        latmin = 0

    latencychart.set_yticks([latmin, latave, max(sd._latency)],
                            labels=[f'Min: {latmin:.0f}',
                                    f'Ave: {latave:.0f}',
                                    f'Max: {max(sd._latency):.0f}'])
    clear_history_images()
    return True


def clear_history_images():
    obs_dir = config.obstructionhistorylocation
    if obs_dir == '':
        return
    dir_list = os.listdir(obs_dir)
    try:
        histtime = widgets['keep_history_images'].get_model()[config.keep_history_images][1]
    except TypeError:
        histtime = -1
    if histtime == -1:
        return
    target_time = time.time() - (histtime * 60 * 60)
    to_delete = 0
    to_keep = 0
    to_ignore = 0
    bad_file = 0
    for f in dir_list:
        if not f.startswith("obstruction_"):
            to_ignore += 1
            continue
        if not f.endswith('.png'):
            to_ignore += 1
            continue
        # Get the creation name from the file instead of using ctime because ctime could have been changed
        try:
            fctime = datetime.datetime.fromisoformat(f.split('_')[1].split('.')[0]).timestamp()
        except:
            print(f'Unable to find ctime of: {f}')
            bad_file += 1
            continue
        if fctime < target_time:
            to_delete += 1
            os.unlink(os.path.join(obs_dir, f))
        else:
            to_keep += 1


def startup():
    # On startup, grab the data right away so the graph can be populated.
    canvas = FigureCanvas(fig)
    widgets['scrolledwindow1'].add(canvas)
    sd.history()
    sd.outages()
    # Force an update right away.
    animate(1)
    return animation.FuncAnimation(fig, animate, interval=config.updateinterval)


try:
    from starlinkdata import StarlinkData
except:
    StarlinkData = None

if StarlinkData is None:
    widgets['window1'].show_all()
    widgets['nogrpcwindow'].show_all()
else:
    sd = StarlinkData(config=config)
    my_signals.sd = sd
    ani = startup()

widgets['window1'].show_all()

Gtk.main()
