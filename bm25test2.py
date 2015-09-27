__author__ = 'basil.beirouti'

from BM25.BM25Okapi import DocMatrix, QueryMaster
from Scheduling import headers, schedule_list, whos_on
from DBConnect.Queries import last_thousand, lookupdict, build_lookup_dict
from BM25.TextCleaning import wordslist2string, cleanStringAndLemmatize
import sys, time
#
onshift_list = whos_on(schedule_list)
results = []
for el in onshift_list:
    results.append(last_thousand(str(el[1])))

acc = []
for el in results:
    acc = acc + el


