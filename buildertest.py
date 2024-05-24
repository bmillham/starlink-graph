import gi

gi.require_version('Gtk', '4.0')
from gi.repository import Gtk

import os

def on_obstructions_clicked():
    pass

resource_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), "resources") # Where the UI files are
builder = Gtk.Builder()
#builder.add_from_file("starlink-graph.glade")
ui_files = []
ui_files += [each for each in os.listdir(resource_directory) if each.endswith('.ui')]
if len(ui_files) == 0:
    print(f"No UI files found in {resource_directory}")
    exit()

for ui in ui_files:
    try:
        builder.add_from_file(os.path.join(resource_directory, ui))
    except Exception as e:
        print(f"Unable to open UI file: {ui} ({e})")
        exit()

#print(dir(builder))
for o in builder.get_objects():
    #print(dir(o))
    try:
        n = Gtk.Buildable.get_buildable_id(o)
        print(n)
    except:
        pass
    #try:
    #    print(o.get_value())
    #except:
    #    pass
    #print(o.get_properties())
