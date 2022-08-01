#!/usr/bin/python3

# starlink-graph.py
# (C) 2022: Brian Millham

import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, Gdk
from matplotlib.figure import Figure
from matplotlib.backends.backend_gtk3agg import (FigureCanvasGTK3Agg as FigureCanvas)
import matplotlib.animation as animation
import datetime
from statistics import mean, StatisticsError
import sys
import configparser
import os
import importlib

# Use humanize if it's available. Install with
# pip3 install humanize
try:
    from humanize import naturalsize
    from humanize.time import naturaldelta
except ModuleNotFoundError:
    print('Humazine module not installed. Install with pip3')


    # Use a tacky simple naturalsize
    def naturalsize(x):
        return f"{x:.1f} kB"


    def naturaldelta(x):
        return x


class Window1Signals:
    def on_nogrpc_ok_button_clicked(self, widget):
        pass

    def on_window1_destroy(self, widget):
        Gtk.main_quit()

    def on_about_dialog_click(self, widget):
        # Show current dish info
        sd.current_data()
        aboutdialog.set_comments(
            f'Dishy: {sd._last_data["software_version"]}\nUptime: {naturaldelta(sd._last_data["uptime"])}')
        aboutdialog.show()

    def on_about_close_button(self, widget):
        aboutdialog.hide()
        return True

    def on_outage_clicked(self, widget):
        self._show_outages()

    def on_obstructions_clicked(self, widget):
        map = sd.obstruction_map()  # Get the latest obstruction map in a temp file
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(map,
                                                        width=400,
                                                        height=400)

        obstructionimage.set_from_pixbuf(pixbuf)
        obstructionwindow.show()
        os.unlink(map)  # Remove the temp file

    def on_obstructionwindow_delete_event(self, *args):
        obstructionwindow.hide()
        return True

    def on_configcancelbutton_clicked(self, *args):
        configwindow.hide()
        return True

    def on_configsavebutton_clicked(self, widget):
        savetools = opts.get('grpctools')
        saveinterval = opts.getint('updateinterval')
        config['options'] = {'updateinterval': f'{updateentry.get_value():.0f}',
                             'duration': str(int(durationentry.get_value())),
                             'history': str(int(historyentry.get_value())),
                             'ticks': str(int(ticksentry.get_value())),
                             'obstructed_color': obstructed_color_button.get_rgba().to_string(),
                             'unobstructed_color': unobstructed_color_button.get_rgba().to_string(),
                             'no_data_color': no_data_color_button.get_rgba().to_string(),
                             'grpctools': '' if toolslocation.get_filename() is None else toolslocation.get_filename()}
        with open(configfile, 'w') as f:
            config.write(f)
        configwindow.hide()
        if savetools != opts.get('grpctools') or saveinterval != opts.getint('updateinterval'):
            os.execv(__file__, sys.argv)  # Restart the script
        sd.load_colors(opts) # Load the new colors
        sd.outages(min_duration=opts.getfloat('duration'))
        sd.history()
        animate(1)  # Force an update.

    def on_settings_clicked(self, widget):
        nogrpcwindow.hide()
        configwindow.show()

    def _show_outages(self, all=False):
        outagestore.clear()
        if all:
            sd.outages(min_duration=0.0)
        else:
            sd.outages(min_duration=opts.getfloat('duration'))  # Re-read outage info
        if len(sd._outages) == 0:
            outagelabel.set_text(
                f'There have been no outages in the last 12 hours over {opts.getint("duration")} seconds!')
        else:
            outagelabel.set_text(
                f'There have been {len(sd._outages)} outages {"over " + opts.get("duration") + " seconds" if not all else ""} in the last 12 hours')

        for out in sd._outages:
            outagestore.append([out['time'].strftime("%I:%M%p"), out['cause'], str(out['duration'])])
        outagewindow.show()

    def outage_close(self, *args, **kwargs):
        outagewindow.hide()
        return True

    def outage_toggled(self, widget):
        self._show_outages(all=widget.get_active())


config = configparser.ConfigParser()
configfile = 'starlink-graph.ini'
defaultconfigfile = 'starlink-graph-default.ini'

try:
    config.read([defaultconfigfile, configfile])
except:
    print('No config files found!')
    exit()

opts = config['options']

if config.get('options', 'grpctools') != '':
    sys.path.insert(0, opts.get('grpctools'))

fig = Figure()
availchart = fig.add_subplot(4, 1, 1)
latencychart = fig.add_subplot(4, 1, 2)
downchart = fig.add_subplot(4, 1, 3)
upchart = fig.add_subplot(4, 1, 4)
builder = Gtk.Builder()
builder.add_from_file("starlink-graph.glade")

window = builder.get_object("window1")
sw = builder.get_object("scrolledwindow1")
aboutdialog = builder.get_object('aboutdialog')
outagewindow = builder.get_object('outagewindow')
outagelist = builder.get_object('outagelist')
outagebox = builder.get_object('outagebox')
outagestore = builder.get_object('outagestore')
outagelabel = builder.get_object('outagelabel')
configwindow = builder.get_object('configwindow')
configsavebutton = builder.get_object('configsavebutton')
configcancelbutton = builder.get_object('configcancelbutton')
toolslocation = builder.get_object('toolslocation')
updateentry = builder.get_object('updateentry')
intervaladjustment = builder.get_object('intervaladjustment')
durationentry = builder.get_object('durationentry')
outagedurationadjustment = builder.get_object('outagedurationadjustment')
durationentry.configure(outagedurationadjustment, 1, 0)
updateentry.configure(intervaladjustment, 1, 0)
historyentry = builder.get_object('historyentry')
historyentry.configure(builder.get_object('historyadjustment'), 1, 0)
ticksentry = builder.get_object('ticksentry')
ticksentry.configure(builder.get_object('ticksadjustment'), 1, 0)
nogrpcwindow = builder.get_object('nogrpcwindow')
obstructionwindow = builder.get_object('obstructionwindow')
obstructionimage = builder.get_object('obstructionimage')
obstructed_color_button = builder.get_object('obstructed_color_button')
unobstructed_color_button = builder.get_object('unobstructed_color_button')
no_data_color_button = builder.get_object('no_data_color_button')
builder.connect_signals(Window1Signals())

# Get the options from the ini file
toolslocation.set_filename(opts.get('grpctools'))
updateentry.set_value(opts.getint('updateinterval'))
durationentry.set_value(opts.getint('duration'))
historyentry.set_value(opts.getint('history'))
ticksentry.set_value(opts.getint('ticks'))
ob_rgba_color = Gdk.RGBA()
ob_rgba_color.parse(opts.get('obstructed_color'))
un_rgba_color = Gdk.RGBA()
un_rgba_color.parse(opts.get('unobstructed_color'))
no_rgba_color = Gdk.RGBA()
no_rgba_color.parse(opts.get('no_data_color'))
obstructed_color_button.set_rgba(ob_rgba_color)
unobstructed_color_button.set_rgba(un_rgba_color)
no_data_color_button.set_rgba(no_rgba_color)

def animate(i):
    sd.current_data()
    if sd._last_data['state'] != 'CONNECTED':
        print(f'Not connected: {sd._last_data["state"]}@{sd._last_data["datetimestamp_utc"]}')
        sd.outages()
    else:
        # Things are working normally, so only check outages every 5 seconds
        if sd._xaxis[-1].second % 5 == 0:
            sd.outages(min_duration=opts.getfloat('duration'))

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
    tick_count = int(len(sd._xaxis) / (opts.getint('ticks') - 1))
    tick_vals = sd._xaxis[::tick_count]
    if len(tick_vals) < opts.getint('ticks'):
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
    return True


def startup():
    # On startup, grab the data right away so the graph can be populated.
    canvas = FigureCanvas(fig)
    sw.add(canvas)
    sd.history()
    sd.outages()
    # Force an update right away.
    animate(1)
    return animation.FuncAnimation(fig, animate, interval=opts.getint('updateinterval'))


try:
    from starlinkdata import StarlinkData
except:
    StarlinkData = None

if StarlinkData is None:
    window.show_all()
    nogrpcwindow.show()
else:
    sd = StarlinkData(opts=opts)
    ani = startup()

window.show_all()

Gtk.main()
