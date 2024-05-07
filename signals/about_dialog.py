#rom humanize.time import naturaldelta
#from simplehuman import naturaldelta
from datetime import timedelta


def on_about_close_button(self, widget):
    widget.hide()
    return True


def on_about_dialog_click(self, widget):
    widget.show()
