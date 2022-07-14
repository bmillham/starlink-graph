#!/usr/bin/python3

# starlink-graph.py
# (C) 2022: Brian Millham

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import subprocess
import datetime
from statistics import mean, StatisticsError
import argparse
import sys

# Use humanize if it's available. Install with
# pip3 install humanize
try:
        from humanize import naturalsize
except ModuleNotFoundError:
        print('Humazine module not installed. Install with pip3')
        # Use a tacky simple naturalsize
        def naturalsize(x): return f"{x:.1f} kB"

parser = argparse.ArgumentParser(
        description="Watch various Starlink status"
        )
parser.add_argument('-H', '--host',
                    default='192.168.100.1',
                    help='IP of the Starlink dish')
parser.add_argument('-n', '--num-ticks',
                    default=3,
                    type=int,
                    help='Number of ticks to show on the graph')
parser.add_argument('-s', '--samples',
                    default=900,
                    type=int,
                    help='How many seconds of history to keep')
parser.add_argument('-l', '--tools-loc',
                    required=True,
                    help='Location of the grps-tools/dish_grpc_text.py script')
parser.add_argument('-u', '--update-interval',
                    default=1000,
                    type=int,
                    help='How often to poll the dish for stats, in milliseconds')
args = parser.parse_args()

sys.path.insert(0, args.tools_loc)
try:
        import starlink_grpc
except:
        print("Unable to import starlink_grpc.!")
        print(f"Is it really available in {args.tools_loc}?")
        #exit()

fig = plt.figure(label='Starlink')
availchart = fig.add_subplot(4,1,1)
downchart = fig.add_subplot(4,1,2)
upchart = fig.add_subplot(4,1,3)
latencychart = fig.add_subplot(4,1,4)

def get_data(vals=0):
        z = starlink_grpc.status_data()
        z[0]['datetimestamp_utc'] = datetime.datetime.now().astimezone()
        return z

def animate(i):
        data = get_data(vals=1) # Grab the latest data
        download.append(data[0]['downlink_throughput_bps']) # Convert the string to float
        latency.append(data[0]['pop_ping_latency_ms'])
        upload.append(data[0]['uplink_throughput_bps'])
        if data[0]['state'] != 'CONNECTED':
                print(f'Not connected: {data[0]["state"]}')
        #        new_avail = avail[-1] - 10
        #        if new_avail < 0:
        #                new_avail = 0
        #        avail.append(new_avail)
        #else:
        #        new_avail = avail[-1] + 10
        #        if new_avail > 100:
        #                new_avail = 100
        #        avail.append(new_avail)
        #if data[0]['pop_ping_drop_rate'] != 0:
        #        print(f'Ping rate {data[0]["pop_ping_drop_rate"]}')
        avail.append(100 - (data[0]['pop_ping_drop_rate'] * 100))
        xar.append(data[0]['datetimestamp_utc'])
        # Only keep maxvals (seconds) of samples
        while (xar[-1] - xar[0]).seconds > args.samples:
                #print(f'Popping sample {len(xar)} {(xar[-1] - xar[0]).seconds}')
                xar.pop(0)
                download.pop(0)
                upload.pop(0)
                latency.pop(0)
                avail.pop(0)
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

        availchart.clear()
        availchart.plot(xar, avail, linewidth=1, color='green')
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
        if data[0]['state'] != 'CONNECTED':
                latencychart.legend([data[0]['state']], loc='upper left')
                print('complete stats', data)
        else:
                latencychart.legend([f'Last: {latency[-1]:.0f} ms'], loc='upper left')

        # Turn off the ticks for up/down charts
        downchart.xaxis.set_ticks([]) 
        upchart.xaxis.set_ticks([])
        # Set the tick interval
        tick_count = int(len(xar) / (args.num_ticks - 1))
        tick_vals = xar[::tick_count]
        if len(tick_vals) < args.num_ticks:
                tick_vals.append(xar[-1])
        tick_labels = [f'{v.astimezone().strftime("%I:%M%p")}' for v in tick_vals]
        latencychart.xaxis.set_ticks(tick_vals, labels=tick_labels)
        # Rotate the tick text
        latencychart.xaxis.set_tick_params(rotation=30)
        latencychart.yaxis.set_label_text('Latency\n(ms)')
        latencychart.yaxis.set_label_position('right')
        upchart.yaxis.set_label_text('Upload')
        upchart.yaxis.set_label_position('right')
        downchart.yaxis.set_label_text('Download')
        downchart.yaxis.set_label_position('right')
        availchart.yaxis.set_label_text('Uptime')
        availchart.yaxis.set_label_position('right')
        availchart.xaxis.set_ticks([])
        availchart.set_yticks([100, 0], labels=['100%', '0%'])
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
#z = get_data(data_type='bulk_history', vals=args.samples)
z = starlink_grpc.history_bulk_data(args.samples)[1]

xar = []
download = []
upload = []
latency = []
avail = []

# Fill out the graph with the history
dtstart = datetime.datetime.now().astimezone() - datetime.timedelta(seconds=args.samples)

for i in range(0, args.samples-1):
        l = {k: z[k][i] for k in z.keys()}
        xar.append(dtstart)
        dtstart += datetime.timedelta(seconds=1)
        try:
                if l['pop_ping_latency_ms'] is None:
                        latency.append(0)
                else:
                        latency.append(l['pop_ping_latency_ms'])
                download.append(l['downlink_throughput_bps'])
                upload.append(l['uplink_throughput_bps'])
                #if l['pop_ping_latency_ms'] is None:
                #        avail.append(0)
                #else:
                #        avail.append(100)
                #if l['pop_ping_drop_rate'] != 0:
                #        print(f"ppdr {l['pop_ping_drop_rate'] * 100}")
                avail.append(100 - (l['pop_ping_drop_rate'] * 100))
        except:
                latency.append(0)
                download.append(0)
                upload.append(0)
                avail.append(0)

# Show the dish firmware release
z = get_data()[0]
fig.suptitle(f'Dishy: {z["software_version"]}')

# Force an update right away.
animate(1)

# Start filling out the graph every 900ms.
ani = animation.FuncAnimation(fig, animate, interval=args.update_interval)
plt.show()
