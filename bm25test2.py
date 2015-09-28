# __author__ = 'basil.beirouti'

import csv, datetime, random
from BM25 import last_thousand
from BM25.Scheduling import whos_on, read_filtered_csv_file, read_raw_schedule_csv, write_filtered_csv_file, this_year, docmatrix_data
from BM25.Plugins import tuples_tse_psums_concat
from BM25.TextCleaning import wordslist2string, cleanStringAndLemmatize
from BM25.BM25Okapi import QueryMaster, DocMatrix

def rand_divide(data, proportion):
    lendata = len(data)
    numgroup1 = round(proportion*lendata)
    numgroup2 = lendata-numgroup1
    random.shuffle(data)
    random.shuffle(data)
    group1 = data[0:numgroup1]
    group2 = data[numgroup1:]
    assert(numgroup1 == len(group1))
    assert(numgroup2 == len(group2))
    return group1, group2

rows = read_filtered_csv_file()
on_now = whos_on(rows)
personids = [el[1] for el in on_now]
out = docmatrix_data(personids, 500)
srnums, badgenums, personids, fns, lns, psums, dates = zip(*out)
tupsdata = [(el[3] + el[4], el[5]) for el in out]
cleaned_data= [(el[0], wordslist2string(cleanStringAndLemmatize(el[1]))) for el in tupsdata]
train, test = rand_divide(cleaned_data, 0.75)
processed_data = tuples_tse_psums_concat(train)
DocMatrix(processed_data, )