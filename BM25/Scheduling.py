__author__ = 'basilbeirouti'

import datetime, csv
from BM25 import last_thousand, rawcsvfile, filteredcsvfile


def read_raw_schedule_csv(path = rawcsvfile):
    reader = csv.reader(open(path, 'r'), delimiter = "\t")
    rows = [el[0:6] for el in reader][1:]
    return rows

def this_year(rows):
    newrows = []
    for el in rows:
        start = datetime.datetime.strptime(el[2], "%Y-%m-%d %H:%M:%S")
        if start.month > 8:
            if start.year == 2015:
                newrows.append(el)
    return newrows

def write_filtered_csv_file(newrows, path = filteredcsvfile):
    writer = csv.writer(open(path, 'w'), delimiter = ",")
    writer.writerows(newrows)
    return

def read_filtered_csv_file(path = filteredcsvfile):
    with open(path, 'r') as file:
        reader = csv.reader(file)
        rows = [el for el in reader]
    return rows

def on_now(shift):
    start = datetime.datetime.strptime(shift[4], "%Y-%m-%d %H:%M:%S")
    end = start + datetime.timedelta(minutes = int(shift[5]) - 60)
    if start <= datetime.datetime.today() <= end:
        return True
    return False

def whos_on(schedule_list):
    return [shift for shift in schedule_list if on_now(shift)]

def docmatrix_data(personids, n):
    results = []
    for el in personids:
        results.append(last_thousand(el, n))
    acc = []
    for el in results:
        acc = acc + el
    return acc
