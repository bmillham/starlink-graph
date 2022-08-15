def outage_close(self, widget, event=None):
    widget.hide()
    return True


def outage_toggled(self, widget):
    self.show_outages()


def on_outage_clicked(self, widget):
    self.show_outages()


def show_outages(self):
    self._widgets['outagestore'].clear()
    if self._widgets['outagecheckbox'].get_active():
        duration = 0.0
    else:
        duration = self._config.duration
    self._sd.outages(duration)  # Re-read outage info
    if len(self._sd._outages) == 0:
        self._widgets['outagelabel'].set_text(
                f'There have been no outages in the last 12 hours over {self._config.duration} seconds!')
    else:
        self._widgets['outagelabel'].set_text(
                f'There have been {len(self._sd._outages)} outages {"over " + str(self._config.duration) + " seconds" if not all else ""} in the last 12 hours')

    for out in self._sd._outages:
        self._widgets['outagestore'].append([out['time'].strftime("%I:%M%p"), out['cause'], str(out['duration'])])
    self._widgets['outagewindow'].show()
