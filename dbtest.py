__author__ = 'basilbeirouti'

from DBConnect.Queries import srdata, lookupdict, build_lookup_dict, whoson


histsr = srdata()
print(len(histsr))
alltses = build_lookup_dict()
print(len(alltses))
onnow = whoson()
print(len(onnow))
