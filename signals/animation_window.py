import subprocess
import os
import datetime
from gi.repository import GLib


def on_create_animation_clicked(self, widget):
    task = self.create_animation()
    GLib.idle_add(task.__next__)


def create_animation(self):
    self._widgets['ani_button'].set_label('Creating')
    self._widgets['ani_button'].set_sensitive(False)
    self._widgets['ani_window'].show()
    yield True
    self._widgets['ani_progress'].pulse()
    obs_dir = self._config.obstructionhistorylocation
    if obs_dir == '':
        return

    video_format = self._widgets['video_format_cb'].get_model()[self._config.video_format][1]
    video_codec = self._widgets['video_codec_cb'].get_model()[self._config.video_codec][1]
    out_size = self._widgets['video_size_cb'].get_model()[self._config.video_size][0]
    out_dir = self._widgets['animation_output_directory'].get_filename()
    duration = self._widgets['video_duration_spin_button'].get_value()
    dir_list = self._get_png_files()[1]
    self._widgets['animation_directory_label'].set_text(out_dir)

    if len(dir_list) < duration:  # Make sure that there is at least enough images for a 1FPS video
        self._widgets['ani_progress'].set_text('Not enough files to create animation')
        self._widgets['ani_progress'].set_fraction(1.0)
        self._widgets['ani_button'].set_sensitive(True)
        self._widgets['ani_button'].set_label('Done')
        yield False
        return

    frame_rate = len(dir_list) / duration
    name_template = f'obstruction_animation_{datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")}.{video_format}'
    self._widgets['animation_file_label'].set_text(name_template)
    cat_pipe = subprocess.Popen(f"cat {os.path.join(obs_dir, 'obstruction_*.png')}", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    frame_count = len(dir_list)

    ff_cmd = ["ffmpeg",
              "-f",
              "image2pipe",
              "-r",
              str(frame_rate),
              "-i",
              "-",
              "-vcodec",
              video_codec,
              "-s",
              out_size,
              "-pix_fmt",
              "yuv420p",
              os.path.join(out_dir, name_template)]

    output = subprocess.Popen(ff_cmd, bufsize=1, universal_newlines=True, stdin=cat_pipe.stdout, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)
    self._widgets['ani_progress'].pulse()
    yield True
    while True:
        # Get rid of extra spaces
        line = " ".join(output.stderr.readline().lstrip().split())
        if not line:
            break
        if line.startswith("frame="):
            current_frame = line.split("=")[1].strip().split()[0]
            self._widgets['ani_progress'].set_fraction(int(current_frame) / frame_count)
        else:
            self._widgets['ani_progress'].pulse()
        self._widgets['ani_progress'].set_text(line)
        yield True
    cat_pipe.stdout.close()
    cat_pipe.wait()
    self._widgets['ani_progress'].set_text('Created')
    self._widgets['ani_progress'].set_fraction(1.0)
    self._widgets['ani_button'].set_label('Done')
    self._widgets['ani_button'].set_sensitive(True)
    yield False


def on_ani_window_delete(self, widget, event=None):
    widget.hide()
    return True