# __author__ = 'basil.beirouti'
#
# from BM25 import whos_on, whos_on_today, schedule_list
# from BM25.Plugins import process_docmatrix_data, clean_docmatrix_data, docmatrix_data, tuples_tse_psums_concat
# from BM25.BM25Okapi import QueryMaster, DocMatrix
# from BM25.Plugins import csv_to_tups, tuples_tse_psums_concat, tse_psums_concat
# import time, sys, random
# from BM25.TextCleaning import wordslist2string, cleanStringAndLemmatize
# from itertools import groupby
# import cProfile
#
# def rand_divide(data, proportion):
#     lendata = len(data)
#     numgroup1 = round(proportion*lendata)
#     numgroup2 = lendata-numgroup1
#     random.shuffle(data)
#     random.shuffle(data)
#     group1 = data[0:numgroup1]
#     group2 = data[numgroup1:]
#     assert(numgroup1 == len(group1))
#     assert(numgroup2 == len(group2))
#     return group1, group2
#
# # evaluator = Bm25Eval(tups_train, test)
# # print("running evaluation")
# # evaluator.evaluatealgorithm()
#
# def testfunction(tups_train, tups_test):
#     okapi_docmatrix = DocMatrix(tups_train, bm25 = True, ngrams_range = (1,2))
#     query_master = QueryMaster(okapi_docmatrix)
#     start = time.time()
#     query_master.evaluatealgorithm(tups_test, 1)
#     query_master.evaluatealgorithm(tups_test, 10)
#     stop = time.time()
#     tot = stop - start
#     print(tot)
#
# # cProfile.runctx("testfunction()", globals(), locals())
# out = whos_on_today(schedule_list)
# print(len(out))
# rawdata = docmatrix_data()
# cleaned = clean_docmatrix_data(rawdata)
# names, psums = zip(*cleaned)
# print(len(set(names)))
# train, test = rand_divide(cleaned, 0.75)
# traindata = tuples_tse_psums_concat(train)
# testfunction(traindata, test)
#
#
#
#

import csv, datetime
from BM25 import last_thousand
reader = csv.reader(open("/Users/basilbeirouti/PycharmProjects/Server/RawData/WFM_Schedule.csv", "r"), delimiter = "\t")
out = [el[0:6] for el in reader]
headers = out[0]
out = out[1:]

acc0 = []
for el in out:
    start = datetime.datetime.strptime(el[2],"%Y-%m-%d %H:%M:%S")
    if start.year == 2015:
        if start.month > 8:
            delta = datetime.timedelta(minutes = int(el[3]))
            end = start + delta
            acc0.append([el[0], el[1], start, end])

writer = csv.writer(open("/Users/basilbeirouti/PycharmProjects/Server/ApplicationData/Schedule.csv", 'w'))
writer.writerows(acc0)
acc = []
for el in acc0:
    if el[2] <= datetime.datetime.today() <= el[3]:
        acc.append((el[0], el[1]))

l= []
r= []
for el in acc:
    l.append(len(last_thousand(el[0], 1)) >= 1)
    r.append(len(last_thousand(el[1], 1)) >= 1)

