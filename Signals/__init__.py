import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, Gdk, GLib, GLib

import os
import datetime
from humanize import naturalsize
#from humanize.time import naturaldelta
import subprocess


class Signals(object):
    from .about_dialog import on_about_close_button, on_about_dialog_click
    from .config_dialog import on_settings_clicked, no_grpc_hide, on_configcancelbutton_clicked, on_configsavebutton_clicked, enable_map_cb, clear_history_button_clicked, save_map_when_window_closed_cb_toggled
    from .obstruction_window import delete_obstruction_images, on_obstructions_clicked, auto_obstruction_toggle, on_obstructionwindow_delete_event
    from .outage_window import outage_close, outage_toggled, on_outage_clicked
    from .delete_dialog import on_delete_confirmation_window_delete_event, on_delete_confirmation_yes_clicked
    from .animation_window import on_ani_window_delete

    def __init__(self, widgets=None, opts=None, configfile=None, config=None):
        self._obstructionstimer = None
        self._sd = None
        self._widgets = widgets
        self._opts = opts
        self._configfile = configfile
        self._config = config

    @property
    def sd(self):
        return self._sd

    @sd.setter
    def sd(self, sd):
        self._sd = sd


    @staticmethod
    def on_window1_destroy(widget):
        Gtk.main_quit()

    def _get_png_files(self):
        obs_dir = self._opts.get('obstructionhistorylocation')
        if obs_dir == '':
            return obs_dir, []
        dir_list = os.listdir(obs_dir)
        # Return list of all obstruction_*.png files in obs_dir
        return obs_dir, list(filter(lambda f: f.startswith('obstruction_') and f.endswith('.png'), dir_list))

    def remove_timer(self, timer):
        GLib.source_remove(timer)

    def add_timer(self, interval, func):
        return GLib.timeout_add_seconds(interval, func)

    def show_obstruction_map(self):
        map = self._sd.obstruction_map(opts=self._opts)  # Get the latest obstruction map in a temp file
        try:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(map,
                                                            width=400,
                                                            height=400)
        except:
            print('Bad map!')
            return True
        self._widgets['obstructionimage'].set_from_pixbuf(pixbuf)
        if self._opts.get('obstructionhistorylocation') == '':
            os.unlink(map)  # Remove the temp file
        self._widgets['obstruction_timer_label'].set_text(
            'Last Update: ' + str(datetime.datetime.now().strftime("%I:%M:%S %p")))
        return True

    def show_outages(self, all=False):
        self._widgets['outagestore'].clear()
        if all:
            self._sd.outages(min_duration=0.0)
        else:
            self._sd.outages(min_duration=self._opts.getfloat('duration'))  # Re-read outage info
        if len(self._sd._outages) == 0:
            self._widgets['outagelabel'].set_text(
                f'There have been no outages in the last 12 hours over {self._opts.getint("duration")} seconds!')
        else:
            self._widgets['outagelabel'].set_text(
                f'There have been {len(self._sd._outages)} outages {"over " + self._opts.get("duration") + " seconds" if not all else ""} in the last 12 hours')

        for out in self._sd._outages:
            self._widgets['outagestore'].append([out['time'].strftime("%I:%M%p"), out['cause'], str(out['duration'])])
        self._widgets['outagewindow'].show()

    def delete_animation_files(self):
        print('deleting!')
        obs_dir, files = self._get_png_files()
        for f in files:
            fn = os.path.join(obs_dir, f)
            print(f'Deleting: {fn}')
            os.unlink(fn)
        print('done deleting')

    def on_create_animation_clicked(self, widget):
        task = self._on_create_animation_clicked()
        GLib.idle_add(task.__next__)

    def _on_create_animation_clicked(self):
        self._widgets['ani_button'].set_label('Creating')
        self._widgets['ani_button'].set_sensitive(False)
        self._widgets['ani_window'].show()
        yield True
        self._widgets['ani_progress'].pulse()
        obs_dir = self._opts.get('obstructionhistorylocation')
        if obs_dir == '':
            return

        video_format = self._widgets['video_format_cb'].get_model()[self._opts.getint('video_format')][1]
        video_codec = self._widgets['video_codec_cb'].get_model()[self._opts.getint('video_codec')][1]
        out_size = self._widgets['video_size_cb'].get_model()[self._opts.getint('video_size')][0]
        out_dir = self._widgets['animation_output_directory'].get_filename()
        duration = self._widgets['video_duration_spin_button'].get_value()
        dir_list = os.listdir(obs_dir)
        self._widgets['animation_directory_label'].set_text(obs_dir)

        if len(dir_list) < duration:  # Make sure that there is at least enough images for a 1FPS video
            self._widgets['ani_progress'].set_text('Not enough files to create animation')
            self._widgets['ani_progress'].set_fraction(1.0)
            self._widgets['ani_button'].set_sensitive(True)
            self._widgets['ani_button'].set_label('Done')
            yield False
            return

        frame_rate = len(dir_list) / duration
        name_template = f'obstruction_animation_{datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")}.{video_format}'
        self._widgets['animation_file_label'].set_text(name_template)
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

        output = subprocess.Popen(ff_cmd, bufsize=1, universal_newlines=True, stdin=cat_pipe.stdout,
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE)
        self._widgets['ani_progress'].pulse()
        yield True
        while True:
            line = output.stderr.readline()
            if not line:
                break
            self._widgets['ani_progress'].set_text(line.rstrip())
            self._widgets['ani_progress'].pulse()
            yield True
        cat_pipe.stdout.close()
        cat_pipe.wait()
        self._widgets['ani_progress'].set_text('Created')
        self._widgets['ani_progress'].set_fraction(1.0)
        self._widgets['ani_button'].set_label('Done')
        self._widgets['ani_button'].set_sensitive(True)
        yield False
