__author__ = 'basilbeirouti'

import csv, os, datetime
import numpy as np

headers = ['id', 'person_id', 'utc_date', 'mins', 'active_utc_date', 'active_mins']
headers = dict(enumerate(headers))

def npy_from_csv(schedule):
    wid, person_id, utc_date, mins, active_date, active_mins = zip(*schedule)
    wid, person_id, utc_date, mins, active_date, active_mins = list(wid), list(person_id), list(utc_date), list(mins), list(active_date), list(active_mins)

    schedule_array = np.zeros((len(schedule),),
                          dtype = [('row_id', 'uint32'),
                                   ('person_id', 'uint32'),
                                   ('utc_date', 'a19'),
                                   ('mins', 'uint16'),
                                   ('active_utc_date', 'a19'),
                                   ('active_mins', 'uint16')])
    schedule_array['row_id'] = wid
    schedule_array['person_id'] = person_id
    schedule_array['utc_date'] = utc_date
    schedule_array['mins'] = mins
    schedule_array['active_utc_date'] = active_date
    schedule_array['active_mins'] = active_mins
    return schedule_array
    #u32, u32, str(19), u16, str(19), u16

def schedule_array2list(schedule_array):
    return [list(row) for row in schedule_array]

def make_datetime(schedule):
    for row in schedule:
        row[0], row[1], row[3], row[5] = int(row[0]), int(row[1]), int(row[3]), int(row[5])
        row[2] = datetime.datetime.strptime(bytes.decode(row[2]), "%Y-%m-%d %H:%M:%S")
        row[4] = datetime.datetime.strptime(bytes.decode(row[4]), "%Y-%m-%d %H:%M:%S")
    return schedule

def get_schedule_list():
    schedule_array = np.load(open("/Users/basilbeirouti/PycharmProjects/Server/ApplicationData/Numpy_Schedule.npy", 'rb'))
    out = make_datetime(schedule_array2list(schedule_array))
    return out

schedule_list = get_schedule_list()

def on_now(shift):
    start = shift[2]
    end = shift[2] + datetime.timedelta(minutes = shift[3])
    if start < datetime.datetime.today() < end:
        return True
    return False

def whos_on(schedule_list):
    return [shift for shift in schedule_list if on_now(shift)]




