__author__ = 'basil.beirouti'

from BM25.BM25Okapi import Bm25Query
from BM25.Plugins import csv_to_tups, tuples_tse_psums_concat
from BM25.TextCleaning import wordslist2string, cleanStringAndLemmatize
import time
start1 = time.time()
alldata = csv_to_tups("RawData/sampleNoDialHome.csv")
print(time.time() - start1)
start2 = time.time()
out = tuples_tse_psums_concat(alldata)
print(time.time() - start2)
temp = Bm25Query(out, ngrams_range = (1,1))
# test query to make sure everything is working properly
cleanedquery = wordslist2string(cleanStringAndLemmatize("disk drive failure"))
tt = temp.queryalgorithm(cleanedquery, 5)
print(tt)

while True:
    out = input("Enter a query to match to a TSE: ")
    out = wordslist2string(cleanStringAndLemmatize(out))
    temp.queryalgorithm(out, 5)
