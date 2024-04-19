from gi.repository import Gdk
import configparser


class Config(object):
    from .set_widget_values import set_widget_values

    def __init__(self, exe_file=None, configfile=None, defaultconfigfile=None):
        self._config = configparser.ConfigParser()
        try:
            self._config.read([defaultconfigfile, configfile])
        except:
            print('No config files found!')
            self._config = None
        finally:
            self._opts = self._config['options']
        self._ob_rgba_color = Gdk.RGBA()
        self._un_rgba_color = Gdk.RGBA()
        self._no_rgba_color = Gdk.RGBA()
        self._widgets = dict()
        self._exe_file = exe_file
        self._config_changed = False

    def save(self, filename=None):
        self._config['options'] = {'updateinterval': f'{self._widgets["updateentry"].get_value():.0f}',
                                   'duration': str(int(self._widgets["durationentry"].get_value())),
                                   'history': str(int(self._widgets['historyentry'].get_value())),
                                   'ticks': str(int(self._widgets['ticksentry'].get_value())),
                                   'obstructed_color': self._widgets['obstructed_color_button'].get_rgba().to_string(),
                                   'unobstructed_color': self._widgets[
                                       'unobstructed_color_button'].get_rgba().to_string(),
                                   'no_data_color': self._widgets['no_data_color_button'].get_rgba().to_string(),
                                   'obstructioninterval': str(
                                       int(self._widgets['obstruction_map_interval_entry'].get_value())),
                                   'obstructionhistorylocation': '' if self._widgets[
                                                                           'obstructionhistorylocation'].get_filename() is None else
                                   self._widgets['obstructionhistorylocation'].get_filename(),
                                   'grpctools': '' if self._widgets['toolslocation'].get_filename() is None else
                                   self._widgets['toolslocation'].get_filename(),
                                   'keep_history_images': self._widgets['keep_history_images'].get_active(),
                                   'video_format': self._widgets['video_format_cb'].get_active(),
                                   'video_codec': self._widgets['video_codec_cb'].get_active(),
                                   'video_size': self._widgets['video_size_cb'].get_active(),
                                   'video_duration': str(int(self._widgets['video_duration_spin_button'].get_value())),
                                   'billing_date': int(self._widgets['billingdayspin'].get_value()),
                                   'animation_directory': '' if self._widgets[
                                                                    'animation_output_directory'].get_filename() is None else
                                   self._widgets['animation_output_directory'].get_filename(),
                                   }
        with open(filename, 'w') as f:
            self._config.write(f)
        self.config_changed = True
        
    @property
    def config(self):
        return self._config

    @property
    def opts(self):
        return self._opts

    @property
    def grpctools(self):
        try:
            return self._opts['grpctools']
        except:
            return None

    @property
    def obstructionhistorylocation(self):
        try:
            return self._opts['obstructionhistorylocation']
        except KeyError:
            return ''

    @property
    def updateinterval(self):
        return self._opts.getint('updateinterval')

    @property
    def duration(self):
        return self._opts.getint('duration')

    @property
    def history(self):
        return self._opts.getint('history')

    @property
    def ticks(self):
        return self._opts.getint('ticks')

    @property
    def obstructioninterval(self):
        return self._opts.getint('obstructioninterval')

    @property
    def obstructed_color(self):
        return self._opts.get('obstructed_color')

    @property
    def unobstructed_color(self):
        return self._opts.get('unobstructed_color')

    @property
    def no_data_color(self):
        return self._opts.get('no_data_color')

    @property
    def ob_rgba_color(self):
        self._ob_rgba_color.parse(self.obstructed_color)
        return self._ob_rgba_color

    @property
    def un_rgba_color(self):
        self._un_rgba_color.parse(self.unobstructed_color)
        return self._un_rgba_color

    @property
    def no_rgba_color(self):
        self._no_rgba_color.parse(self.no_data_color)
        return self._no_rgba_color

    @property
    def keep_history_images(self):
        return self._opts.getint('keep_history_images')

    @property
    def video_format(self):
        return self._opts.getint('video_format')

    @property
    def video_codec(self):
        return self._opts.getint('video_codec')

    @property
    def video_size(self):
        return self._opts.getint('video_size')

    @property
    def video_duration(self):
        return self._opts.getint('video_duration')

    @property
    def billing_date(self):
        return self._opts.getint('billing_date')

    @property
    def animation_directory(self):
        return self._opts.get('animation_directory')

    @property
    def config_changed(self):
        return self._config_changed

    @config_changed.setter
    def config_changed(self, value):
        self._config_changed = value

    @property
    def database_url(self):
        return self._opts.get('database_url')

    @property
    def access_mode(self):
        return self._opts.get('access_mode')

