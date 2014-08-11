import hashlib
from datetime import date, timedelta, datetime


def callMethod(o, name):
    getattr(o, name)()

def strmd5sum(string):
    m = hashlib.md5()
    m.update(str(string))
    return m.hexdigest()

def _last_hour(n=24):
    today = date.today()
    startdate = today - timedelta(hours=n)
    enddate = today
    return startdate, enddate


