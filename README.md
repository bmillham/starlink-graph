# starlink-graph
Show Starlink stats in a nice graph in an app instead of using a web browser.
This is a very early crude version but it works. It really should not be calling the dish_grpc_text.py script but importing the modules and using them instead.
That's in my plans to impliment soon.
# Prerequisites
You will need starlink-grps-tools from https://github.com/sparky8512/starlink-grpc-tools
Edit statlink-graph.py and change this line:
tools_loc = '/home/brian/Develop/starlink/starlink-grpc-tools/dish_grpc_text.py'
to point to where your version of dish_grpc_text.py is. All other options should be set to sane defaults.
# Optional
The humanize module is used if installed. Install it with pip3 install humanize
