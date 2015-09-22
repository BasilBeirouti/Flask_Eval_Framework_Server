__author__ = 'BasilBeirouti'

from BM25.DocIteration import TestDocs, IterDocs, eval_doall
from BM25 import ResultsAnalysis, TF2BM25
import numpy
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.preprocessing import Normalizer
import time
import matplotlib.pyplot as plt
import scipy.sparse as ssp


start = time.time()
# doall("DataFolder/vnx2.csv", 2, 0.7, 20)

class LSA:

    def __init__(self, *args, **kwargs):
        self.traindirectory = args[0]
        self.testdirectory = args[1]
        self._itertrain = IterDocs(self.traindirectory)
        self._itertest = TestDocs(self.testdirectory)
        self.trainnames, self.traincontent = zip(*list(self._itertrain))
        self.actualnames, self.qcontents = zip(*list(iter(self._itertest)))
        self.results = []


        if "min_df" in kwargs:
            self.min_df = kwargs["min_df"]
        else:
            self.min_df = 2

        if "ngrams_range" in kwargs:
            self.ngrams_range = kwargs["ngrams_range"]
        else:
            self.ngrams_range = (1,1)

        if "num_features" in kwargs:
            self.num_features = kwargs["num_features"]
        else:
            self.num_features = 500

        if "usebm25" in kwargs:
            self.usebm25 = kwargs["usebm25"]
        else:
            self.usebm25 = False

    def vectorize(self):
        self.vectorizer = TfidfVectorizer(self.traincontent, min_df = self.min_df, ngram_range= self.ngrams_range)
        self.vectobj = self.vectorizer.fit(self.traincontent)
        self.vectout = self.vectobj.transform(self.traincontent)

    def make_bm25(self):
        self.bm_vectorizer = CountVectorizer(self.traincontent, min_df = self.min_df, ngram_range= self.ngrams_range)
        self.bm_vectobj = self.vectorizer.fit(self.traincontent)
        self.bm_vectout = self.vectobj.transform(self.traincontent)
        self.bm25obj = TF2BM25.Okapi(numpy.asarray(self.vectout.toarray()), 2, 1000, 0.75)
        self.bm25 = self.bm25obj.make_bm25()
        self.bm25 = ssp.csr_matrix(self.bm25)
        self.vectout = self.bm25
        print("doing bm25")

    def fit(self):
        print(self.vectout.shape)
        self.svder = TruncatedSVD(self.num_features, n_iter = 15)
        self.svdobj = self.svder.fit(self.vectout)
        self.svdout = self.svdobj.transform(self.vectout)
        self.normer = Normalizer()
        self.normobj = self.normer.fit(self.svdout)
        self.normout = self.normobj.transform(self.svdout)
        # self.normout = self.svdout
        print(self.vectout.shape)
        print(self.svdout.shape)
        print(self.normout.shape)

    def transform(self):
        self.qvectsout = self.vectobj.transform(self.qcontents)
        self.qsvdsout = self.svdobj.transform(self.qvectsout)
        self.qnormsout = self.normobj.transform(self.qsvdsout)
        # self.qnormsout = self.qsvdsout
        print(self.qnormsout.shape)

    def similarity(self):
        self.similaritymatrix = numpy.asarray(numpy.asmatrix(self.normout)*numpy.asmatrix(self.qnormsout).T)
        print(self.similaritymatrix.shape)

    def toppredictions(self, n = 1):
        if n == 1:
            out = numpy.argmax(self.similaritymatrix, axis = 0)
            print(out.shape)
            self.predictednames = [self.trainnames[ind] for ind in out]
            bools1 = [self.predictednames[ii] == self.actualnames[ii] for ii in range(len(self.actualnames))]
            accuracy = sum(bools1)/len(bools1)
            randaccuracy = 1/len(self.trainnames)
            print("algorithm achieved ", accuracy, "% accuracy")
            print("random achieved ", randaccuracy, "% accuracy")
            print((accuracy)/(randaccuracy), " times better than random!")
        else:
            topnindices = numpy.argpartition(self.similaritymatrix, -n, axis = 0)[-n:]
            topnbools = [self.actualnames[ii] in set([self.trainnames[ind] for ind in topnindices[:, ii]]) for ii in range(topnindices.shape[1])]
            accuracy = sum(topnbools)/len(topnbools)
            randaccuracy = n/len(self.trainnames)
            print("in top ", str(n), " algorithm achieved ", accuracy , "% accuracy")
            print("random achieved ", randaccuracy, "% accuracy")
            print(accuracy/randaccuracy, " times better than random!")

        self.results.append((n, accuracy, randaccuracy, accuracy/randaccuracy))

    def evaluatealgorithm(self):
        self.vectorize()
        if self.usebm25:
            self.make_bm25()
        self.compute()

    def compute(self):
        self.fit()
        self.transform()
        self.similarity()
        self.toppredictions()
        self.toppredictions(10)

    def tse_precision_recall(self):
        self.pandr = ResultsAnalysis.PrecisionAndRecall(self.actualnames, self.predictednames)
        self.allprecision = self.pandr.all_precision()
        self.allrecall = self.pandr.all_recall()
        self.sortednames, self.precisions = zip(*self.allprecision)
        names, self.recalls = zip(*self.allrecall)

    def scatter_precision_recall(self):
        plt.scatter(self.precisions, self.recalls)
        plt.show()

