#!/usr/bin/python
# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from functions import login, logout, download, get_string, data_process
import schedule
import time

"""First schedule - Firing every 10 minutes
"""
def ten_minutes():
    times = [(datetime.today() - timedelta(hours=0,
             minutes=10)).strftime('%Y-%m-%d %H:%M:%S'),
             datetime.today().strftime('%Y-%m-%d %H:%M:%S')]
    check(times)

"""Daily schedule - Firing every day at 23:59
"""
def daily():
    times = [(datetime.today() - timedelta(hours=23,
             minutes=59)).strftime('%Y-%m-%d %H:%M:%S'),
             datetime.today().strftime('%Y-%m-%d %H:%M:%S')]
    check(times)

"""Main processing function, logging and downloading of data from 
Asterix API""" 
def check(times):
    try:
        token = login()
        data = download(get_string(token, times), times)
    except:
        print 'Connection error'

    if data:
        for i in data.split('\n')[1:]:
            if len(i) > 25:
                data_process(i, token)
        logout(token)
    else:
        print 'No data'

if __name__ == "__main__":
    schedule.every(10).minutes.do(ten_minutes)
    schedule.every().day.at('23:59').do(daily)

    while True:
        schedule.run_pending()
        time.sleep(1)
