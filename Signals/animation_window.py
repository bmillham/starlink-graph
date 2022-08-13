import subprocess

def _on_create_animation_clicked(self):
    ani_button.set_label('Creating')
    ani_button.set_sensitive(False)
    ani_window.show()
    yield True
    ani_progress.pulse()
    obs_dir = opts.get('obstructionhistorylocation')
    if obs_dir == '':
        return

    video_format = video_format_cb.get_model()[opts.getint('video_format')][1]
    video_codec = video_codec_cb.get_model()[opts.getint('video_codec')][1]
    out_size = video_size_cb.get_model()[opts.getint('video_size')][0]
    out_dir = animation_output_directory.get_filename()
    duration = video_duration_spin_button.get_value()
    dir_list = os.listdir(obs_dir)
    animation_directory_label.set_text(obs_dir)

    if len(dir_list) < duration:  # Make sure that there is at least enough images for a 1FPS video
        ani_progress.set_text('Not enough files to create animation')
        ani_progress.set_fraction(1.0)
        ani_button.set_sensitive(True)
        ani_button.set_label('Done')
        yield False
        return

    frame_rate = len(dir_list) / duration
    name_template = f'obstruction_animation_{datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")}.{video_format}'
    animation_file_label.set_text(name_template)
    cat_pipe = subprocess.Popen(f"cat {obs_dir}/*.png", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

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
              f"{out_dir}/{name_template}"]

    output = subprocess.Popen(ff_cmd, bufsize=1, universal_newlines=True, stdin=cat_pipe.stdout, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)
    ani_progress.pulse()
    yield True
    while True:
        line = output.stderr.readline()
        if not line:
            break
        ani_progress.set_text(line.rstrip())
        ani_progress.pulse()
        yield True
    cat_pipe.stdout.close()
    cat_pipe.wait()
    ani_progress.set_text('Created')
    ani_progress.set_fraction(1.0)
    ani_button.set_label('Done')
    ani_button.set_sensitive(True)
    yield False


def on_ani_window_delete(self, widget, event=None):
    widget.hide()
    return True