import os


def on_delete_confirmation_window_delete_event(self, widget, event=None):
    widget.hide()
    return True


def on_delete_confirmation_yes_clicked(self, widget):
    self.delete_animation_files()
    widget.hide()
    #self._widget['delete_confirmation_window'].hide()
