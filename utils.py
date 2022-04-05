import datetime
import time


def parse_time(time_int):
    '''
    Parse the time from integer format into readable string format:
    Year, Month, Day, Hour, Minute, Second

    time-int: time represented in integer format, like 1649185477
    '''
    if time_int is None:
        return 'Not Available'
    value = datetime.datetime.fromtimestamp(time_int)
    return value.strftime('%Y-%m-%d %H:%M:%S')


def parse_time_hms(time_int):
    '''
    Parse the time from integer format into hours, mimutes and seconds
    '''
    if time_int is None:
        return 'Not Available'
    time_str = str(datetime.timedelta(seconds=time_int))
    if time_int > 0:
        time_str = '+' + time_str
    else:
        time_str = '-' + time_str
    return time_str