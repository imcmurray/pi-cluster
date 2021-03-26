#!/usr/bin/env python3
import redis
import subprocess
import os
import time


try:
    conn = redis.StrictRedis(
        host='pistats.lan',
        port=6379,
        password='****')
    # Get hostname
    hostname = os.uname().nodename
    # Get CPU Temp
    t = subprocess.getoutput('cat /sys/class/thermal/thermal_zone0/temp')
    # Get CPU Speed
    s = subprocess.getoutput('sudo cat /sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_cur_freq')
    # Pretty the data
    temp = '{0:.1f}'.format(int(t)/1000)
    speed = '{0:.2f}'.format(int(s)/1000000)
    # Get file hit status
    hit = "no"
    if os.path.isfile('/home/ubuntu/results.txt'):
        hit = "yes"
    # Get timestamp
    time = int(time.time())
    check_status = subprocess.getoutput('sudo systemctl status memory-dormant.service | grep running')
    if check_status:
        conn.hset(hostname, "last", time)
    # Send to Redis
    conn.hset(hostname, "temp", temp)
    conn.hset(hostname, "speed", speed)
    conn.hset(hostname, "hit", hit)
except Exception as ex:
    print('Error:', ex)
    exit('Failed to connect, terminating.')


