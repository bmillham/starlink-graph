# starlink-graph
Show Starlink stats in a nice graph in an app instead of using a web browser. It has been tested on linux and MacOS. 
# Prerequisites
You will need starlink-grps-tools from https://github.com/sparky8512/starlink-grpc-tools
Some distributions (Manjaro) do not have matplotlib installed by default. Install it with pip install matplotlib
To create the new obstruction animation ffmpeg is required (called directly so no python modules are needed)
NEW: Added experimental usage tracking. The data is saved in a sqlite3 database, so to use the feature sqlite3
must be installed on your system. 
# MacOS Notes
Thank you to reddit user u/virtuallynathan for the following information<br/>
Use <b>brew</b> to install these packages: cairo, gtk+3, gtksourceview3 gobject-introspection<br/>
Use <b>pip3</b> to install: pyGObject, pychairo, humanize, matplotlib
# Optional
The humanize module is used if installed. Install it with pip3 install humanize
# Preperation
Copy the exemple starlink-graph-default.ini to starlink-graph.ini and edit it to change billing_date to the start day of your billing cycle.
# Running
Just clone the git and run the script: python starlink-graph.py
If you have the environment variable PYTHONPATH set to include the location of starlink-grpc-tools then
the script should run. If you don't have it set you will prompted to select the location of starlink-grpc-tools
# Release Notes
<ul>
<li>V 0.2: Removed command line options in favor of having a GUI setting window.</li>
<li>V 0.3: Added basic obstruction map</li>
<li>V 0.4: Added controls to the obstruction map</li>
<li>V 0.5: Added ability to save obstructions history and create an animation from the history</li>
<li>V 0.6: No real functional changes, but major code re-factoring and cleanup</li>
<li>This branch is experimental!</li>
</ul>
