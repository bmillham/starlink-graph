import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gdk

import configparser

class Config(object):
    from .set_widget_values import set_widget_values

    def __init__(self, configfile=None, defaultconfigfile=None):
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
        return self._opts['obstructionhistorylocation']

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
    def animation_directory(self):
        return self._opts.get('animation_directory')

