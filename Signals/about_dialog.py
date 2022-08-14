#rom humanize.time import naturaldelta
from SimpleHuman import naturaldelta


def on_about_close_button(self, widget):
    widget.hide()
    return True


def on_about_dialog_click(self, widget):
    # Show current dish info
    self._sd.current_data()
    widget.set_comments(
      f'Dishy: {self._sd._last_data["software_version"]}\nUptime: {naturaldelta(self._sd._last_data["uptime"])}')
    widget.show()