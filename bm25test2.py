__author__ = 'basil.beirouti'

from BM25.Plugins import process_docmatrix_data, clean_docmatrix_data, docmatrix_data, tuples_tse_psums_concat
from BM25.BM25Okapi import QueryMaster, DocMatrix
from BM25.Plugins import csv_to_tups, tuples_tse_psums_concat, tse_psums_concat
import time, sys, random
from BM25.TextCleaning import wordslist2string, cleanStringAndLemmatize
from itertools import groupby
import cProfile

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

# evaluator = Bm25Eval(tups_train, test)
# print("running evaluation")
# evaluator.evaluatealgorithm()

def testfunction(tups_train, tups_test):
    okapi_docmatrix = DocMatrix(tups_train, bm25 = True, ngrams_range = (1,1))
    query_master = QueryMaster(okapi_docmatrix)
    start = time.time()
    query_master.evaluatealgorithm(tups_test, 1)
    query_master.evaluatealgorithm(tups_test, 10)
    stop = time.time()
    tot = stop - start
    print(tot)

# cProfile.runctx("testfunction()", globals(), locals())

rawdata = docmatrix_data()
processed = process_docmatrix_data(rawdata)
cleaned = clean_docmatrix_data(rawdata)
names, cleanedpsums = zip(*cleaned)
names, processedpsums = zip(*processed)

# train, test = rand_divide(processed, 0.75)
# traindata = tuples_tse_psums_concat(train)
# testfunction(traindata, test)




