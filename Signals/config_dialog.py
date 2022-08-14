from gi.repository import GLib
import os
import sys


def on_settings_clicked(self, widget):
    widget.show()
    self._widgets['nogrpcwindow'].hide()


def no_grpc_hide(self, widget):
    widget.hide()


def on_configcancelbutton_clicked(self, widget, event=None):
    widget.hide()
    return True


def on_configsavebutton_clicked(self, widget):
    savetools = self._config.grpctools
    saveinterval = self._config.updateinterval
    saveobstructions = self._config.obstructioninterval
    self._config.save(self._configfile)

    widget.hide()
    if savetools != self._config.grpctools or saveinterval != self._config.updateinterval:
        os.execv(self._exe_file, sys.argv)  # Restart the script
    if saveobstructions != self._config.obstructioninterval:
        if self._obstructionstimer is not None: # If updates are currently running, stop/start the timer
            GLib.source_remove(self._obstructionstimer)
            self._obstructionstimer = GLib.timeout_add_seconds(self._config.obstructioninterval,
            self.show_obstruction_map)
    self._sd.load_colors(self._config) # Load the new colors
    self._sd.outages(min_duration=self._config.duration)
    self._sd.history()
    #animate(1)  # Force an update.


def enable_map_cb(self, widget):
    widget.set_sensitive(True)


def clear_history_button_clicked(self, widget):
    self._widgets['obstructionhistorylocation'].unselect_all()
    self._widgets['save_map_when_window_closed_cb'].set_sensitive(False)


def save_map_when_window_closed_cb_toggled(self, widget):
    self.auto_obstruction_toggle()
