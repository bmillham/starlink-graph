#!/usr/bin/python3

# starlink-graph.py
# (C) 2022: Brian Millham

import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, Gdk, GLib, GLib
from matplotlib.figure import Figure
from matplotlib.backends.backend_gtk3agg import (FigureCanvasGTK3Agg as FigureCanvas)
import matplotlib.animation as animation
import datetime
from statistics import mean, StatisticsError
import sys
import configparser
import os
import importlib
import png
import time
import subprocess
from Signals import Signals

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
    def __init__(self):
        self._obstructionstimer = None

    def on_nogrpc_ok_button_clicked(self, widget):
        pass

 #   def enable_map_cb(self, widget):
 #       save_map_when_window_closed_cb.set_sensitive(True)

#    def clear_history_button_clicked(self, widget):
#        obstructionhistorylocation.unselect_all()
#        save_map_when_window_closed_cb.set_sensitive(False)

    def save_history_cb_toggled(self, widget):
        pass

    def save_map_when_window_closed_cb_toggled(self, widget):
        self.auto_obstruction_toggle()
        #if save_map_when_window_closed_cb.get_active():
    """ def on_create_animation_clicked(self, widget):
        #ani_window.show()
        #ani_out_buffer.set_text('Creating animation\n')
        #self._on_create_animation_clicked()
        pass

    def on_create_animation_clicked(self, widget):
        task = self._on_create_animation_clicked()
        GLib.idle_add(task.__next__)

    def _on_create_animation_clicked(self):
        ani_button.set_label('Creating')
        ani_button.set_sensitive(False)
        ani_window.show()
        yield True
        ani_progress.pulse()
        obs_dir = opts.get('obstructionhistorylocation')
        if obs_dir == '':
            return

        video_format = video_format_cb.get_model()[opts.getint('video_format')][1]
        video_codec = video_codec_cb.get_model()[opts.getint('video_codec')][1]
        out_size = video_size_cb.get_model()[opts.getint('video_size')][0]
        out_dir = animation_output_directory.get_filename()
        duration = video_duration_spin_button.get_value()
        dir_list = os.listdir(obs_dir)
        animation_directory_label.set_text(obs_dir)

        if len(dir_list) < duration: # Make sure that there is at least enough images for a 1FPS video
            ani_progress.set_text('Not enough files to create animation')
            ani_progress.set_fraction(1.0)
            ani_button.set_sensitive(True)
            ani_button.set_label('Done')
            yield False
            return

        frame_rate = len(dir_list) / duration
        name_template = f'obstruction_animation_{datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")}.{video_format}'
        animation_file_label.set_text(name_template)
        cat_pipe = subprocess.Popen(f"cat {obs_dir}/*.png", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

        ff_cmd = ["ffmpeg",
                  "-f",
                  "image2pipe",
                  "-r",
                  str(frame_rate),
                  "-i",
                  "-",
                  "-vcodec",
                  video_codec,
                  "-s",
                  out_size,
                  "-pix_fmt",
                  "yuv420p",
                  f"{out_dir}/{name_template}"]

        output = subprocess.Popen(ff_cmd, bufsize=1, universal_newlines=True, stdin=cat_pipe.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        ani_progress.pulse()
        yield True
#        while True:
#            line = output.stderr.readline()
#            if not line:
#                break
#            ani_progress.set_text(line.rstrip())
#            ani_progress.pulse()
#            yield True
#        cat_pipe.stdout.close()
#        cat_pipe.wait()
#        ani_progress.set_text('Created')
#        ani_progress.set_fraction(1.0)
#        ani_button.set_label('Done')
#        ani_button.set_sensitive(True)
#        yield False"""

#    def on_ani_window_delete(self, widget, event=None):
#        ani_window.hide()
#        return True

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

# Build dict of all widgets with an ID
widgets = {}
for o in builder.get_objects():
    try:
        widgets[Gtk.Buildable.get_name(o)] = o
    except TypeError:
        pass

my_signals = Signals(widgets=widgets, opts=opts, configfile=configfile, config=config)
builder.connect_signals(my_signals)

# Get the options from the ini file
widgets['toolslocation' ].set_filename(opts.get('grpctools'))
try:
    widgets['obstructionhistorylocation'].set_filename(opts.get('obstructionhistorylocation'))
except TypeError:
    widgets['obstructionhistorylocation'].set_filename('')

if opts.get('obstructionhistorylocation') == '':
    widgets['save_map_when_window_closed_cb'].set_sensitive(False)

widgets['updateentry'].set_value(opts.getint('updateinterval'))
widgets['durationentry'].set_value(opts.getint('duration'))
widgets['historyentry'].set_value(opts.getint('history'))
widgets['ticksentry'].set_value(opts.getint('ticks'))
widgets['obstruction_map_interval_entry'].set_value(opts.getint('obstructioninterval'))
ob_rgba_color = Gdk.RGBA()
ob_rgba_color.parse(opts.get('obstructed_color'))
un_rgba_color = Gdk.RGBA()
un_rgba_color.parse(opts.get('unobstructed_color'))
no_rgba_color = Gdk.RGBA()
no_rgba_color.parse(opts.get('no_data_color'))
widgets['obstructed_color_button'].set_rgba(ob_rgba_color)
widgets['unobstructed_color_button'].set_rgba(un_rgba_color)
widgets['no_data_color_button'].set_rgba(no_rgba_color)
widgets['keep_history_images'].set_active(opts.getint('keep_history_images'))
widgets['video_format_cb'].set_active(opts.getint('video_format'))
widgets['video_codec_cb'].set_active(opts.getint('video_codec'))
widgets['video_size_cb'].set_active(opts.getint('video_size'))
widgets['video_duration_spin_button'].set_value(opts.getint('video_duration'))
widgets['animation_output_directory'].set_filename(opts.get('animation_directory'))

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
    clear_history_images()
    return True

def clear_history_images():
    obs_dir = opts.get('obstructionhistorylocation')
    if obs_dir == '':
        return
    dir_list = os.listdir(obs_dir)
    histtime = widgets['keep_history_images'].get_model()[opts.getint('keep_history_images')][1]
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
    return animation.FuncAnimation(fig, animate, interval=opts.getint('updateinterval'))


try:
    from starlinkdata import StarlinkData
except:
    StarlinkData = None

if StarlinkData is None:
    widgets['window1'].show_All()
    widgets['nogrpswindow'].show_all()
else:
    sd = StarlinkData(opts=opts)
    my_signals.set_sd(sd)
    #my_signals.sd = sd
    ani = startup()

widgets['window1'].show_all()

Gtk.main()
