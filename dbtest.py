__author__ = 'basilbeirouti'

from DBConnect.Queries import getwork, getalltses
import csv


# histsr = srdata()
# print(len(histsr))
# alltses = build_lookup_dict()
# print(len(alltses))
# onnow = whoson()
# print(len(onnow))

getalltses()
getwork()

spamwriter = csv.writer(open("RawData/Bob.csv"))