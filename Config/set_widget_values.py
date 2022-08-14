def set_widget_values(self, widgets):
    widgets['updateentry'].set_value(self.updateinterval)
    widgets['durationentry'].set_value(self.duration)
    widgets['historyentry'].set_value(self.history)
    widgets['ticksentry'].set_value(self.ticks)
    widgets['obstruction_map_interval_entry'].set_value(self.obstructioninterval)
    widgets['obstructed_color_button'].set_rgba(self.ob_rgba_color)
    widgets['unobstructed_color_button'].set_rgba(self.un_rgba_color)
    widgets['no_data_color_button'].set_rgba(self.no_rgba_color)
    widgets['keep_history_images'].set_active(self.keep_history_images)
    widgets['video_format_cb'].set_active(self.video_format)
    widgets['video_codec_cb'].set_active(self.video_codec)
    widgets['video_size_cb'].set_active(self.video_size)
    widgets['video_duration_spin_button'].set_value(self.video_duration)
    widgets['animation_output_directory'].set_filename(self.animation_directory)
    widgets['toolslocation'].set_filename(self.grpctools)
    try:
        widgets['obstructionhistorylocation'].set_filename(self.obstructionhistorylocation)
    except TypeError:
        widgets['obstructionhistorylocation'].set_filename('')

    if self.obstructionhistorylocation == '':
        widgets['save_map_when_window_closed_cb'].set_sensitive(False)
    self._widgets = widgets
