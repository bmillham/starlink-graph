#!/usr/bin/python3

# starlink-graph.py
# (C) 2022: Brian Millham

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import subprocess
import datetime
from statistics import mean, StatisticsError

# Use humanize if it's available. Install with
# pip3 install humanize
try:
        from humanize import naturalsize
except ModuleNotFoundError:
        print('Humazine module not installed. Install with pip3')
        # Use a tacky simple naturalsize
        def naturalsize(x): return f"{x:.1f} kB"

# IMPORTANT: you must set tools_loc!!!
# Location of the grpc-tools script dish_grpc_text.py
tools_loc = '/home/brian/Develop/starlink/starlink-grpc-tools/dish_grpc_text.py'
maxvals = 900 # 15 minutes
# How many ticks to show on the x-axis
num_ticks = 3

fig = plt.figure(label='Starlink')
downchart = fig.add_subplot(3,1,1)
upchart = fig.add_subplot(3,1,2)
latencychart = fig.add_subplot(3,1,3)






def get_data(data_type='status', vals=1, headers_only=False):
        """
        This really should directly use the grpc-tools module instead of just running the script!
        Uses decode('utf-8') because subprocess returns a binary instead of a string
        """
        args = ['python', tools_loc]
        if headers_only:
                args += ['-H']
        else:
                args += ['-s', f'{vals}'] # Need to convert to strings as arg can't be an int
        args += [data_type]
        result = subprocess.check_output(args).decode('utf-8')
        lines = result.split('\n')
        vals = []
        fixed_result = []
        for line in lines:
                if line == '':
                        continue
                fields = line.split(',')
                if not headers_only:
                        fields[0] = f"{fields[0]}+00:00" # Convert to UTC
                if data_type == 'bulk_history':
                        newf = [None] * 20 # Create empty array
                        newf[0] = fields[0]
                        newf[8] = fields[1]
                        newf[9] = fields[3]
                        newf[10] = fields[4]
                        newf[11] = fields[2]
                        vals.append(newf)
                else:
                        vals.append(fields)
        if len(vals) > 1:
                return vals
        else:
                return vals[0]

def animate(i):
        '''Returned fields:
           datetimestamp_utc,0
	   id,1
           hardware_version,2
           software_version,3
           state,4
           uptime,5
           snr,6
           seconds_to_first_nonempty_slot,7
           pop_ping_drop_rate,8
           downlink_throughput_bps,9
           uplink_throughput_bps,10
           pop_ping_latency_ms,11
           alerts,12
           fraction_obstructed,13
           currently_obstructed,14
           seconds_obstructed,15
           obstruction_duration,16
           obstruction_interval,17
           direction_azimuth,18
           direction_elevation,19'''

        z = get_data(vals=1) # Grab the latest data

        if len(z) != 20:
                print(f'Got an unexpected result: {z}')
                # Convert to expected results.
                z = [z[0], '0', '0', '0', z[4], '0', '', '0', '0',
                     '0', '0', '0', '0', '0', '0', '0', '0', '0',
                     '0', '0']
        if z[6] != '':
                print('Got SNR:', z[6])
        try:
                download.append(float(z[9])) # Convert the string to float
                latency.append(float(z[11]))
                upload.append(float(z[10]))
                xar.append(datetime.datetime.fromisoformat(z[0]))
        except:
                print(f'Unable to convert {z[9]} to float')
                print(z)
                return

        # Only keep maxvals (seconds) of samples
        while (xar[-1] - xar[0]).seconds > maxvals:
                xar.pop(0)
                download.pop(0)
                upload.pop(0)
                latency.pop(0)
        hdl = download[-1]
        hul = upload[-1]
        hmdl = max(download)
        hmul = max(upload)
        # Get averages, excluding an 0 values
        try:
                dlave = mean([z for z in download if z > 0])
                upave = mean([z for z in upload if z > 0])
                latave = mean([z for z in latency if z > 0])
                
        except StatisticsError:
                dlave = 0
                upave = 0
                latave = 0
                print('No data received')

        daveline = [dlave] * len(xar)
        uaveline = [upave] * len(xar)
        lataveline = [latave] * len(xar)
        savedlave = dlave
        saveupave = upave
        hdl = naturalsize(hdl)
        hmdl = naturalsize(max(download))
        hul = naturalsize(hul)
        umin = naturalsize(min(upload))
        hmul = naturalsize(max(upload))
        dlave = naturalsize(dlave)
        upave = naturalsize(upave)

        downchart.clear()
        downchart.plot(xar, download, linewidth=1)
        downchart.plot(xar, daveline, linewidth=1, linestyle='dashed', color='black')
        downchart.legend([f'Last: {hdl}'], loc='upper left')
        upchart.clear()
        upchart.plot(xar, upload, linewidth=1, color='red')
        upchart.plot(xar, uaveline, linewidth=1, color='black', linestyle='dashed')
        upchart.legend([f'Last: {hul}'], loc='upper left')
        latencychart.clear()
        latencychart.plot(xar, latency, linewidth=1, color='green')
        latencychart.plot(xar, lataveline, linewidth=1, color='black', linestyle='dashed')
        if z[4] != 'CONNECTED':
                latencychart.legend([z[4]], loc='upper left')
        else:
                latencychart.legend([f'Last: {latency[-1]:.0f} ms'], loc='upper left')

        # Turn off the ticks for up/down charts
        downchart.xaxis.set_ticks([]) 
        upchart.xaxis.set_ticks([])
        # Set the tick interval
        tick_count = int(len(xar) / (num_ticks - 1))
        tick_vals = xar[::tick_count]
        if len(tick_vals) < num_ticks:
                tick_vals.append(xar[-1])
        tick_labels = [f'{v.astimezone().strftime("%I:%M%p")}' for v in tick_vals]
        latencychart.xaxis.set_ticks(tick_vals, labels=tick_labels)
        # Rotate the tick text
        latencychart.xaxis.set_tick_params(rotation=30)
        latencychart.yaxis.set_label_text('Latency (ms)')
        latencychart.yaxis.set_label_position('right')
        upchart.yaxis.set_label_text('Upload')
        upchart.yaxis.set_label_position('right')
        downchart.yaxis.set_label_text('Download')
        downchart.yaxis.set_label_position('right')
        upmin = min(upload)
        upmax = max(upload)
        dmin = min(download)
        dmax = max(download)
        upchart.set_yticks([upmin, saveupave, upmax], labels=['', f'Ave:\n{upave}', hmul])
        downchart.set_yticks([dmin, savedlave, dmax], labels=['', f'Ave:\n{dlave}', hmdl])
        try:
                latmin = min([x for x in latency if x != 0.0])
        except:
                latmin = 0
        
        latencychart.set_yticks([latmin, latave, max(latency)],
                                labels=[f'Min: {latmin:.0f}', f'Ave: {latave:.0f}', f'Max: {max(latency):.0f}'])

# On startup, grab the data right away so the graph can be populated.
z = get_data(data_type='bulk_history', vals=maxvals)

xar = []
download = []
upload = []
latency = []

headers = get_data('status', headers_only=True) # Nothing is done with this yet.

# Fill out the graph with the history
for i in z:
        xar.append(datetime.datetime.fromisoformat(i[0]))
        download.append(float(i[9]))
        upload.append(float(i[10]))
        try:
                latency.append(float(i[11]))
        except:
                latency.append(latency[-1])

# Show the dish firmware release
z = get_data()
fig.suptitle(f'Dishy: {z[3]}')

# Force an update right away.
animate(1)

# Start filling out the graph every 900ms.
ani = animation.FuncAnimation(fig, animate, interval=900)
plt.show()
