from datetime import datetime, timedelta
from classes import Asterix, LDAP, OsTicket
from functions import data_process
from time import sleep
import schedule


def ten_minutes():
    times = [(datetime.today()-timedelta(hours=0, minutes=10)).strftime("%Y-%m-%d %H:%M:%S"),
    datetime.today().strftime("%Y-%m-%d %H:%M:%S")]
    check(times)

def daily():
    times = [(datetime.today()-timedelta(hours=60, minutes=59)).strftime("%Y-%m-%d %H:%M:%S"),
    datetime.today().strftime("%Y-%m-%d %H:%M:%S")]
    check(times)

def check(times):
    asterix = Asterix()
    ldap = LDAP()
    osticket = OsTicket()

    data = asterix.get_string(times)

    if(data):
        for i in data.split("\n")[1:]:
            if(len(i) > 25):
                data_process(i, (ldap, osticket, asterix))
    else:
        print("No data")



schedule.every(10).minutes.do(ten_minutes)
schedule.every().day.at("23:59").do(daily)


while True:
    schedule.run_pending()
    sleep(1)
