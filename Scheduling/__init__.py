__author__ = 'basilbeirouti'

import csv, os, datetime
import numpy as np

schedule_path = os.path.join(os.getcwd(), "ApplicationData","WFM_Schedule_Sep2Dec_2015")
headers = ['id', 'person_id', 'utc_date', 'mins', 'active_utc_date', 'active_mins']
headers = dict(enumerate(headers))

def npy_from_csv(schedule_path):
    schedule = read_schedule_file(schedule_path)
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


def read_schedule_file(schedule_path):
    file_ext = schedule_path[-4:]
    if file_ext == ".npy":
        with open(schedule_path, "r") as schedule_file:
            schedule = np.load(schedule_file, mmap_mode = "r")
        return schedule

    elif file_ext == ".csv":
        with open(schedule_path, "r") as schedule_file:
            schedule = csv.reader(schedule_file)
            schedule = to_datetime(schedule)
        return schedule

def schedule_array2list(schedule_array):
    return [tuple(row) for row in schedule_array]

def to_datetime(schedule):
    for row in schedule:
        row[0], row[1], row[3], row[5] = int(row[0]), int(row[1]), int(row[3]), int(row[5])
        row[2] = datetime.datetime.strptime(row[2], "%Y-%m-%d %H:%M:%S")
        row[4] = datetime.datetime.strptime(row[4], "%Y-%m-%d %H:%M:%S")
    return schedule











