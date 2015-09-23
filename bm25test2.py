__author__ = 'basil.beirouti'

from BM25.BM25Okapi import OkapiDocMatrix, QueryMaster, Bm25Query
from BM25.Plugins import csv_to_tups, tuples_tse_psums_concat
from BM25.TextCleaning import wordslist2string, cleanStringAndLemmatize
import sys, time

start1 = time.time()
alldata = csv_to_tups("RawData/sampleNoDialHome.csv")
print(time.time() - start1)
start2 = time.time()
out = tuples_tse_psums_concat(alldata)
print(time.time() - start2)
okapi_docmatrix = OkapiDocMatrix(out, ngrams_range = (1,1))
tse_dict = okapi_docmatrix.tse_dict
whoson = list(tse_dict.keys())[0:70]
query_master = QueryMaster(okapi_docmatrix)
toppredictions = query_master.queryalgorithm("disk drive failure", whoson)
predictednames, predictedscores = zip(*toppredictions)
predictednames = set(list(predictednames))

temp = Bm25Query(out, ngrams_range = (1,1))
# test query to make sure everything is working properly
cleanedquery = wordslist2string(cleanStringAndLemmatize("disk drive failure"))
tt = temp.queryalgorithm(cleanedquery, 2000)

newels = []
for el in tt:
    if el[0] in predictednames:
        newels.append(el)
