#rom humanize.time import naturaldelta
#from simplehuman import naturaldelta
from datetime import timedelta


def on_about_close_button(self, widget):
    widget.hide()
    return True


def on_about_dialog_click(self, widget):
    # Show current dish info
    info = self.sd.dish_info
    widget.set_comments(f'Dishy ID: {info.id}\n'
                        f'Hardware: {info.hardware_version}\n'
                        f'Software: {info.software_version}\n'
                        f'Uptime: {timedelta(seconds=info.uptime)}')
    widget.show()
