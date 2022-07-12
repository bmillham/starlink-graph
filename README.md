# starlink-graph
Show Starlink stats in a nice graph in an app instead of using a web browser.
This is a very early crude version but it works. It really should not be calling the dish_grpc_text.py script but importing the modules and using them instead.
That's in my plans to impliment soon.
# Prerequisites
You will need starlink-grps-tools from https://github.com/sparky8512/starlink-grpc-tools
# Optional
The humanize module is used if installed. Install it with pip3 install humanize
# Running
Just clone the git and run the script: python starlink-graph.py
You must supply one option: -l which is the location of dish_grpc_text.py. So for example
starlink-graph.py -l ~/Develop/starlink/starlink-grpc-tools/dish_grpc_text.py

There are other options, -h/--help will show you all the fun things you can change.
