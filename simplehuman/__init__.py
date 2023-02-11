#
# A simple module that uses humanize if available. If not then uses crude methods to mimic humanize
#

try:
    import humanize
except ModuleNotFoundError:
    print('Humanize module not installed. Install with pip3')
    humanize = None


def naturalsize(size):
    if humanize is None:
        return f"{size/1000:.1f} kB"
    else:
        return humanize.naturalsize(size)


def naturaldelta(time):
    if humanize is None:
        return f"{time/60:.0f} minutes"
    else:
        return humanize.time.naturaldelta(time)
