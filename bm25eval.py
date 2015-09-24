__author__ = 'basilbeirouti'

from BM25.BM25Okapi import Bm25Eval, Bm25Query
from BM25.Plugins import csv_to_tups, tuples_tse_psums_concat, tse_psums_concat
import time, sys, random
from BM25.TextCleaning import wordslist2string, cleanStringAndLemmatize
from BM25.LatentSemanticAnalysis import LSA
from itertools import groupby


combined =[]
data_vmax = csv_to_tups("RawData/sampleNoDialHome.csv")
# data_vnx = csv_to_tups("RawData/vnx2.csv")

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

for ii in range(7):
    train1, test1 = rand_divide(data_vmax, 0.75)
    # train2, test2 = rand_divide(data_vnx, 0.75)
    train = train1
    test = test1

    print("divided data into training and testing sets")

    tups_train = tuples_tse_psums_concat(train)
    tups_train2 = tse_psums_concat(train)

    print("grouped problem summaries by TSE")

    evaluator = Bm25Eval(tups_train, test)
    print("running evaluation")
    evaluator.evaluatealgorithm()
    combined.append(evaluator.results)

