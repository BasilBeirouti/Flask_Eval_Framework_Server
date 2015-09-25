__author__ = 'BasilBeirouti'

import numpy, os, time, scipy

class OkapiWeights:

    def __init__(self, docmatrix, k1, k3, b):
        self.docmatrix = docmatrix
        shape = self.docmatrix.shape
        self.numdocs = shape[0]
        self.numterms = shape[1]
        self.k1 = k1
        self.b = b

    def makeidfs(self):
        docmatrix_boolean = self.docmatrix != 0
        dfs = numpy.sum(docmatrix_boolean, axis = 0) #sum along each column to get vect of len numterms, df for each term
        idfs = numpy.log(numpy.divide(((self.numdocs-dfs) + 0.5), (dfs + 0.5)))
        idfs.reshape((1,self.numterms))
        self.idfs = idfs
        return self.idfs

    def make_primes(self):
        docmatrix = self.docmatrix
        self.doclengths = numpy.sum(docmatrix, axis = 1) #sum along columns to get 1d array of length of each document
        self.avglen = sum(self.doclengths)/len(self.doclengths)
        factors = numpy.asarray([1/(1-self.b + self.b * doclength/self.avglen) for doclength in self.doclengths]) #numdocs 1d array
        factors = numpy.reshape(factors, (factors.shape[0], 1))
        docmatrix = self.docmatrix
        primes = docmatrix*factors
        self.primes = primes
        return self.primes

    def make_tfnorms(self):
        primes = self.make_primes()
        numerator = (self.k1+1)*primes
        denominator = numpy.reciprocal(self.k1 + primes)
        self.normtfs = numpy.multiply(numerator, denominator)
        return self.normtfs

    def make_bm25(self):
        start = time.time()
        print("applying bm25 weights (OkapiWeights Class)")
        tfnorms = self.make_tfnorms()
        idfs = self.makeidfs()
        self.bm25 = numpy.multiply(tfnorms, idfs)
        print("applying weights took ", time.time()-start, " seconds")
        return self.bm25
