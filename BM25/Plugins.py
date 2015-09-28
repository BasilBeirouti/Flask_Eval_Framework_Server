__author__ = 'basilbeirouti'

import csv, operator
from itertools import groupby
from BM25.DocIteration import changename
from BM25.TextCleaning import wordslist2string, cleanStringAndLemmatize
import csv, os, datetime
import numpy as np


def csv_to_tups(csvfilename):
    reader = csv.DictReader(open(csvfilename, encoding = "utf-8"))
    alldata = list((changename(row["sr_closer_name"]), wordslist2string(cleanStringAndLemmatize(row["srvc_req_prob_text"])))for row in reader)
    alldata = sorted(alldata, key = operator.itemgetter(0))
    return alldata

def checknames(alldata, namelookuptable):
    alldata.sort(key = operator.itemgetter(0))
    names, probsums = zip(*alldata)
    if all(name in namelookuptable for name in names):
        return True
    return False

def dict_tse_psums(alldata):
    dict_out = dict()
    for key, group in groupby(alldata, operator.itemgetter(0)):
        name, psums = zip(*list(group))
        dict_out[key] = list(psums)
    return dict_out

def tse_psums_concat(alldata):
    tups = []
    alldata.sort(key = operator.itemgetter(0))
    for key, group in groupby(alldata, operator.itemgetter(0)):
        name, psums = zip(*list(group))
        tups.append((key, " ".join(list(psums))))
    return tups

def tuples_tse_psums_concat(alldata):
    alldata.sort(key = operator.itemgetter(0))
    out = [(name[0], " ".join(list(psums))) for name, psums in [zip(*list(group)) for key, group in groupby(alldata, operator.itemgetter(0))]]
    return out

def clean_docmatrix_data(raw_data):
    #lastname_firstname, cleanedproblemsummary
    temp = [(el[3].replace(" ", "") + "_" + el[2].replace(" ", ""), wordslist2string(cleanStringAndLemmatize(el[4]))) for el in raw_data]
    temp.sort(key = operator.itemgetter(0))
    return temp


