__author__ = 'BasilBeirouti'

import numpy as numpy
import os

class Okapi:

    def __init__(self, docmatrix, k1, k3, b):
        self.docmatrix = docmatrix
        shape = self.docmatrix.shape
        self.numdocs = shape[0]
        self.numterms = shape[1]
        self.k1 = k1
        self.b = b

    def makeidfs(self):
        docmatrix_boolean = self.docmatrix != 0
        dfs = numpy.sum(docmatrix_boolean, axis = 0) #sum along the columns to get vect of len numterms, df for each term
        idfs = numpy.divide(((self.numdocs-dfs) + 0.5), (dfs + 0.5))
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
        tfnorms = self.make_tfnorms()
        idfs = self.makeidfs()
        self.bm25 = numpy.multiply(tfnorms, idfs)
        return self.bm25

    # #returns same array memory mapped on disk
    # def tempsave(self, array, namestring):
    #     filename = "temp" + namestring
    #     try:
    #         numpy.save(array, filename)
    #     except AttributeError:
    #         array = array.astype(numpy.float64, subok = False)
    #         numpy.save(array, filename)
    #     del array
    #     array = numpy.load(filename, mmap_mode = "r")
    #     return array


