#!/usr/bin/env python3
from collections import defaultdict
from dateutil.parser import parse
import subprocess

# if period between commits > 8 hours, you weren't probably actively working
threshold = 6 # hours

# get git log output in a convenient format
process = subprocess.run(["git", "log", "--date=format:'%Y-%m-%d %H:%M:%S'"], capture_output=True)
lines = [line for line in process.stdout.decode().split('\n') if line]

# parse datetimes of commits for different users
timestamps = defaultdict(list)
for j, line in enumerate(lines):
    if "Date:" in line:
        # XXX this line is definitely going to break at some point
        timestamp = parse(line.split("'")[1])
        user = ' '.join(lines[j-1].split(' ')[1:])
        timestamps[user].append(timestamp)

# calculate total time spent for each user
total_time = defaultdict(int) 
for user in timestamps:
    dts = timestamps[user]
    for j in range(len(dts)-1):
        gap = dts[j] - dts[j+1] # timedelta
        gap = gap.seconds/3600 # hours
        if gap < threshold:
            total_time[user] += gap

sorted_users = sorted(total_time, key=total_time.get)
for user in sorted_users:
    print(f'{user}: {total_time[user]} hours')
