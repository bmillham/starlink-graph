def delete_obstruction_images(self, widget):
    obs_dir, dir_list = self._get_png_files()
    if len(dir_list) == 0:
        self._widgets['really_delete_label'].set_text('No files found to remove')
    else:
        self._widgets['really_delete_label'].set_text(f'Really delete {len(dir_list)} files from {obs_dir}?')
    widget.show()


def on_obstructions_clicked(self, widget):
    self.auto_obstruction_toggle()

    self.show_obstruction_map()
    widget.show()


def auto_obstruction_toggle(self, widget=None):
    if self._widgets['obstruction_update_check'].get_active() or self._widgets['save_map_when_window_closed_cb'].get_active():
        if self._obstructionstimer is None:
            self._obstructionstimer = self.add_timer(self._config.obstructioninterval, self.show_obstruction_map)
    else:
        if self._obstructionstimer is not None:
            self.remove_timer(self._obstructionstimer)
            self._obstructionstimer = None


def on_obstructionwindow_delete_event(self, widget, event=None):
    widget.hide()
    if self._obstructionstimer is not None:
        self.remove_timer(self._obstructionstimer)
        self._obstructionstimer = None
    return True
