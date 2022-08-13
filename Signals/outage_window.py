def outage_close(self, widget, event=None):
    widget.hide()
    return True


def outage_toggled(self, widget):
    self.show_outages(all=widget.get_active())

def on_outage_clicked(self, widget):
    self.show_outages()