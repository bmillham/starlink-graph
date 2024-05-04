#rom humanize.time import naturaldelta
#from simplehuman import naturaldelta
from datetime import timedelta


def on_about_close_button(self, widget):
    widget.hide()
    return True


def on_about_dialog_click(self, widget):
    # Show current dish info
    info = self.sd.dish_info
    widget.set_comments(f'Dishy ID: {info.id}\nHardware: {info.hardware_version}\nSoftware: {info.software_version}\nUptime: {timedelta(seconds=info.uptime)}')
    widget.show()
