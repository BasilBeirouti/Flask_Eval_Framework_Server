__author__ = 'BasilBeirouti'

import time

class PrecisionAndRecall:
    #length of actualnames and predictednames should be equal, and should be equal to number of queries in test data
    def __init__(self, actualnames, predictednames):
        self.actualnames = actualnames
        self.predictednames = predictednames
        self.sortednames = sorted(list(set(actualnames)))

        self.tps = dict()
        self.fps = dict()
        # self.tns = dict()
        self.fns = dict()
        self.weight = dict()
        self.countact = dict()
        self.countpred = dict()
        start = time.time()
        for name in set(actualnames):
            self.countact[name] = countofname(name, actualnames)
            self.countpred[name] = countofname(name, predictednames)
            self.weight[name] = self.countpred[name]/self.countact[name]
            self.tps[name] = truepositives(name, actualnames, predictednames)
            # self.fps[name] = falsepositives(name, actualnames, predictednames)
            self.fps[name] = self.countpred[name] - self.tps[name]
            # self.tns[name] = truenegatives(name, actualnames, predictednames)
            self.fns[name] = falsenegatives(name, actualnames, predictednames)
        print(time.time() - start)

    def precision(self, name):
        tp = self.tps[name]
        fp = self.fps[name] #think about optimizing this by using count instead
        if tp + fp == 0:
            return None #the algorithm never predicted this name, to avoid dividing by zero, return None
        return tp/(tp + fp)

    def recall(self, name):
        tp = self.tps[name]
        fn = self.fns[name]
        return tp/(fn+tp)

    def all_precision(self):
        return [(name, self.precision(name)) for name in self.sortednames]

    def all_recall(self):
        return [(name, self.recall(name)) for name in self.sortednames]



def countofname(name, iterable):
    return len([i for i in iterable if i == name])

def truepositives(name, actualnames, predictednames):
    return sum([((actualnames[ii] == predictednames[ii]) and (actualnames[ii] == name)) for ii in range(len(actualnames))])

def falsepositives(name, actualnames, predictednames):
    return sum([((actualnames[ii] != predictednames[ii]) and (predictednames[ii] == name)) for ii in range(len(actualnames))])

def truenegatives(name, actualnames, predictednames):
    return sum([((predictednames[ii] != name) and (actualnames[ii] != name)) for ii in range(len(actualnames))])

def falsenegatives(name, actualnames, predictednames):
    return sum([((predictednames[ii] != name) and (actualnames[ii] == name)) for ii in range(len(actualnames))])

def precision(name, actualnames, predictednames):
    tp = truepositives(name, actualnames, predictednames)
    fp = falsepositives(name, actualnames, predictednames)
    if tp + fp == 0:
        return None #the algorithm never predicted this name, to avoid dividing by zero, return None
    return tp/(tp + fp)

def recall(name, actualnames, predictednames):
    tp = truepositives(name, actualnames, predictednames)
    fn = falsenegatives(name, actualnames, predictednames)
    return tp/(fn+tp)

#how many selected items are relevant?
def all_precision(setofnames, actualnames, predictednames):
    return [(name, precision(name, actualnames, predictednames)) for name in setofnames]

#how many relevant items are selected?
def all_recall(setofnames, actualnames, predictednames):
    return [(name, precision(name, actualnames, predictednames)) for name in setofnames]

