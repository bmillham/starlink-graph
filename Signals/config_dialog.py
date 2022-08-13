import os


def on_settings_clicked(self, widget):
    widget.show()


def no_grpc_hide(self, widget):
    widget.hide()


def on_configcancelbutton_clicked(self, widget, event=None):
    widget.hide()
    return True


def on_configsavebutton_clicked(self, widget):
    savetools = self._opts.get('grpctools')
    saveinterval = self._opts.getint('updateinterval')
    saveobstructions = self._opts.getint('obstructioninterval')
    self._config['options'] = {'updateinterval': f'{self._widgets["updateentry"].get_value():.0f}',
                         'duration': str(int(self._widgets["durationentry"].get_value())),
                         'history': str(int(self._widgets['historyentry'].get_value())),
                         'ticks': str(int(self._widgets['ticksentry'].get_value())),
                         'obstructed_color': self._widgets['obstructed_color_button'].get_rgba().to_string(),
                         'unobstructed_color': self._widgets['unobstructed_color_button'].get_rgba().to_string(),
                         'no_data_color': self._widgets['no_data_color_button'].get_rgba().to_string(),
                         'obstructioninterval': str(int(self._widgets['obstruction_map_interval_entry'].get_value())),
                         'obstructionhistorylocation': '' if self._widgets['obstructionhistorylocation'].get_filename() is None else self._widgets['obstructionhistorylocation'].get_filename(),
                         'grpctools': '' if self._widgets['toolslocation'].get_filename() is None else self._widgets['toolslocation'].get_filename(),
                         'keep_history_images': self._widgets['keep_history_images'].get_active(),
                         'video_format': self._widgets['video_format_cb'].get_active(),
                         'video_codec': self._widgets['video_codec_cb'].get_active(),
                         'video_size': self._widgets['video_size_cb'].get_active(),
                         'video_duration': str(int(self._widgets['video_duration_spin_button'].get_value())),
                         'animation_directory': '' if self._widgets['animation_output_directory'].get_filename() is None else self._widgets['animation_output_directory'].get_filename(),
                         }

    with open(self._configfile, 'w') as f:
        self._config.write(f)
    widget.hide()
    if savetools != self._opts.get('grpctools') or saveinterval != self._opts.getint('updateinterval'):
        os.execv(__file__, sys.argv)  # Restart the script
    if saveobstructions != self._opts.getint('obstructioninterval'):
        if self._obstructionstimer is not None: # If updates are currently running, stop/start the timer
            GLib.source_remove(self._obstructionstimer)
            self._obstructionstimer = GLib.timeout_add_seconds(self._opts.getint('obstructioninterval'),
            self._show_obstruction_map)
    self._sd.load_colors(self._opts) # Load the new colors
    self._sd.outages(min_duration=self._opts.getfloat('duration'))
    self._sd.history()
    #animate(1)  # Force an update.


def enable_map_cb(self, widget):
    widget.set_sensitive(True)


def clear_history_button_clicked(self, widget):
    self._widgets['obstructionhistorylocation'].unselect_all()
    self._widgets['save_map_when_window_closed_cb'].set_sensitive(False)


def save_map_when_window_closed_cb_toggled(self, widget):
    self.auto_obstruction_toggle()
