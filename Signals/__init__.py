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
    from .animation_window import on_ani_window_delete, create_animation, on_create_animation_clicked

    def __init__(self, widgets=None, exe_file=None, opts=None, configfile=None, config=None):
        self._obstructionstimer = None
        self._sd = None
        self._widgets = widgets
        self._opts = opts
        self._configfile = configfile
        self._config = config
        self._exe_file = exe_file

    @property
    def sd(self):
        return self._sd

    @sd.setter
    def sd(self, sd):
        self._sd = sd


    @staticmethod
    def on_window1_destroy(widget, event=None):
        Gtk.main_quit()

    def _get_png_files(self):
        obs_dir = self._config.obstructionhistorylocation
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
        map = self._sd.obstruction_map(config=self._config)  # Get the latest obstruction map in a temp file
        try:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(map,
                                                            width=400,
                                                            height=400)
        except:
            print('Bad map!')
            return True
        self._widgets['obstructionimage'].set_from_pixbuf(pixbuf)
        if self._config.obstructionhistorylocation == '':
            os.unlink(map)  # Remove the temp file
        self._widgets['obstruction_timer_label'].set_text(
            'Last Update: ' + str(datetime.datetime.now().strftime("%I:%M:%S %p")))
        return True

    def show_outages(self, all=False):
        self._widgets['outagestore'].clear()
        if all:
            self._sd.outages(min_duration=0.0)
        else:
            self._sd.outages(min_duration=self._config.duration)  # Re-read outage info
        if len(self._sd._outages) == 0:
            self._widgets['outagelabel'].set_text(
                f'There have been no outages in the last 12 hours over {self._config.duration} seconds!')
        else:
            self._widgets['outagelabel'].set_text(
                f'There have been {len(self._sd._outages)} outages {"over " + str(self._config.duration) + " seconds" if not all else ""} in the last 12 hours')

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
