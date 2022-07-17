#!/usr/bin/env python3
from collections import defaultdict
from dateutil.parser import parse
import subprocess

# if period between commits > 8 hours, you weren't probably actively working

def read_log():
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
    return timestamps

def calc_time(timestamps, thresholds):
    # calculate total time spent for each user
    total_time = defaultdict(lambda: [0]*len(thresholds))
    for user in timestamps:
        dts = timestamps[user]
        for dts_i in range(len(dts)-1):
            gap = dts[dts_i] - dts[dts_i+1] # timedelta
            gap = gap.seconds/3600 # hours
            for thr_i, threshold in enumerate(thresholds):
                if gap < threshold:
                    total_time[user][thr_i] += gap
    return total_time

def print_time(total_time):
    # expects a list/tuple of calc_time results of length 1 or 2
    sorted_users = sorted(total_time.keys(), key=lambda x: sum(total_time[x])/len(total_time[x]))
    for user in sorted_users:
        times_str = ", ".join([f'{time:.2f}' for time in total_time[user]])
        print(f'{user}: {times_str} hours')

def main():
    thresholds = [6,8,12,24] # hours
    usr_thres = input(f'enter integer thresholds separated with commas (default: {thresholds}): ').strip()
    try:
        if usr_thres:
            thresholds = [int(i) for i in usr_thres.split(',')]
    except ValueError:
        print('illegal thresholds, using default values')
    timestamps = read_log()
    total_time = calc_time(timestamps, thresholds)
    print_time(total_time)

if __name__ == '__main__':
    main()
