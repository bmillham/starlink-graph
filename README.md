# starlink-graph
Show Starlink stats in a nice graph in an app instead of using a web browser. It has been tested on linux and MacOS. 
# Prerequisites
You will need starlink-grps-tools from https://github.com/sparky8512/starlink-grpc-tools
Some distributions (Manjaro) do not have matplotlib installed by default. Install it with pip install matplotlib
# Optional
The humanize module is used if installed. Install it with pip3 install humanize
# Running
Just clone the git and run the script: python starlink-graph.py
If you have the environment variable PYTHONPATH set to include the location of starlink-grpc-tools then
the script should run. If you don't have it set you will prompted to select the location of starlink-grpc-tools
# Release Notes
V 0.2: Removed command line options in favor of having a GUI setting window.
V 0.3: Added basic obstruction map



