# starlink-graph
Show Starlink stats in a nice graph in an app instead of using a web browser. It has been tested on linux and MacOS. 
# Important Information!
The database has changed in this version!
<p>
If you don't care about the history then you can just remove starlink-history.db.
<p>
If you want your history then:
<ul>
<li>Stop any currently running version</li>
<li>Run <b>python convert_database.py</b> to convert the database</li>
<li>This can take serveral minutes to run depending on the size of your current database</li>
<li>The original database will be saved</li>
<li>Once converted start the starlink-graph.py again</li>
</ul>
# Prerequisites
You will need starlink-grps-tools from https://github.com/sparky8512/starlink-grpc-tools
Some distributions (Manjaro) do not have matplotlib installed by default. Install it with pip3 install matplotlib
or apt install python3-matplotlib
<p>To create the new obstruction animation ffmpeg is required (called directly so no python modules are needed)
<p>NEW: Added experimental usage tracking. The data is saved in a sqlite3 database, so to use the feature sqlite3
must be installed on your system. 
<p>NEW: Changed to using SQLAlchemy 2.0 for database access to allow usage with MySQL and other database.
<ul>
<li>Currenly only tested with sqlite3</li>
<li>You probably should use a venv!</li>
<li>pip3 install 'sqlalchemy>=2.0'</li>
</ul>
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
<p>If you have the environment variable PYTHONPATH set to include the location of starlink-grpc-tools then
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
