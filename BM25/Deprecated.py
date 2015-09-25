from BM25 import TF2BM25
import numpy
import operator
from sklearn.feature_extraction.text import CountVectorizer

__author__ = 'basilbeirouti'


class Bm25Eval:

    def __init__(self, *args, **kwargs):
        self.traindata = args[0]
        self.testdata = args[1]
        self.trainnames, self.traincontent = zip(*self.traindata)
        self.trainnames, self.traincontent = list(self.trainnames), list(self.traincontent)
        testnames, testcontent = zip(*self.testdata)
        self.actualnames, self.qcontents = list(testnames), list(testcontent)
        self.results = []

        if "min_df" in kwargs:
            self.min_df = kwargs["min_df"]
        else:
            self.min_df = 2

        if "ngrams_range" in kwargs:
            self.ngrams_range = kwargs["ngrams_range"]
        else:
            self.ngrams_range = (1,1)

    def make_bm25(self):
        self.bm_vectorizer = CountVectorizer(self.traincontent, min_df = self.min_df, ngram_range= self.ngrams_range)
        self.bm_vectobj = self.bm_vectorizer.fit(self.traincontent)
        self.bm_vectout = self.bm_vectobj.transform(self.traincontent)
        out = numpy.asarray(self.bm_vectout.toarray())
        print("converting to BM25 representation")
        self.bm25obj = TF2BM25.OkapiWeights(out, 2, 1000, 0.75)
        self.bm25 = self.bm25obj.make_bm25()
        self.vectout = self.bm25
        print("returned from BM25 conversion")

    def transform(self):
        self.qvectsout = self.bm_vectobj.transform(list(self.qcontents))
        print(self.qvectsout.shape)

    def similarity(self):
        matrixvectout = numpy.asmatrix(self.vectout)
        print("matrixvectout shape is ", matrixvectout.shape)
        matrixqvectsout = numpy.asmatrix(self.qvectsout.toarray())
        print("matrix qvectsout shape is ", matrixqvectsout.shape)
        self.similaritymatrix = numpy.asarray(matrixvectout*matrixqvectsout.T)
        print(self.similaritymatrix.shape)

    def toppredictions(self, n = 1):
        if n == 1:
            out = numpy.argmax(self.similaritymatrix, axis = 0)
            print(out.shape)
            self.predictednames = [self.trainnames[ind] for ind in out]
            bools1 = [self.predictednames[ii] == self.actualnames[ii] for ii in range(len(self.actualnames))]
            accuracy = sum(bools1)/len(bools1)
            randaccuracy = 1/len(self.trainnames)
            print("algorithm achieved ", accuracy, " accuracy")
            print("random achieved ", randaccuracy, " accuracy")
            print((accuracy)/(randaccuracy), " times better than random!")
        else:
            topnindices = numpy.argpartition(self.similaritymatrix, -n, axis = 0)[-n:]
            topnbools = [self.actualnames[ii] in set([self.trainnames[ind] for ind in topnindices[:, ii]]) for ii in range(topnindices.shape[1])]
            accuracy = sum(topnbools)/len(topnbools)
            randaccuracy = n/len(self.trainnames)
            print("in top ", str(n), " algorithm achieved ", accuracy , " accuracy")
            print("random achieved ", randaccuracy, " accuracy")
            print(accuracy/randaccuracy, " times better than random!")

        self.results.append((n, accuracy, randaccuracy, accuracy/randaccuracy))

    def evaluatealgorithm(self):
        self.make_bm25()
        self.transform()
        self.similarity()
        self.toppredictions()
        self.toppredictions(10)


class Bm25Query:

    def __init__(self, tup_tse_psums, **kwargs):
        # self.corpusdirectory = corpusdirectory
        # self._itertrain = IterDocs(self.corpusdirectory)
        # self.trainnames, self.traincontent = zip(*list(self._itertrain))
        self.trainnames, self.traincontent = zip(*tup_tse_psums)
        self.trainnames, self.traincontent = list(self.trainnames), list(self.traincontent)

        if "min_df" in kwargs:
            self.min_df = kwargs["min_df"]
        else:
            self.min_df = 2

        if "ngrams_range" in kwargs:
            self.ngrams_range = kwargs["ngrams_range"]
        else:
            self.ngrams_range = (1,1)

        self.make_bm25()

    def make_bm25(self):
        self.bm_vectorizer = CountVectorizer(self.traincontent, min_df = self.min_df, ngram_range= self.ngrams_range)
        self.bm_vectobj = self.bm_vectorizer.fit(self.traincontent)
        self.bm_vectout = self.bm_vectobj.transform(self.traincontent)
        out = numpy.asarray(self.bm_vectout.toarray())
        self.bm25obj = TF2BM25.OkapiWeights(out, 2, 1000, 0.75)
        self.bm25 = self.bm25obj.make_bm25()
        self.vectout = self.bm25

    def transform(self, querytext):
        self.qvectsout = self.bm_vectobj.transform([querytext]) #put brackets because it's a list of 1 query
        # print(self.qvectsout.shape)

    def similarity(self):
        matrixvectout = numpy.asmatrix(self.vectout)
        # print("matrixvectout shape is ", matrixvectout.shape)
        matrixqvectsout = numpy.asmatrix(self.qvectsout.toarray())
        # print("matrix qvectsout shape is ", matrixqvectsout.shape)
        out = self.bm_vectobj.get_feature_names()
        self.similaritymatrix = numpy.asarray(matrixvectout*matrixqvectsout.T)
        # print(self.similaritymatrix.shape)

    @staticmethod
    def maxpoints(matrix, n):
        if n == 1:
            topindex = numpy.argmax(matrix)
            return [topindex]

        elif n > 1:
            topnindices = numpy.argpartition(matrix, -n, axis = 0)[-n:]
            topnindices = [ind[0] for ind in topnindices]
            return topnindices

    def toppredictions(self, n = 1):
        topnindices = self.maxpoints(self.similaritymatrix, n)
        self.name_score = [(self.trainnames[ind], float("{0:.3f}".format(self.similaritymatrix[ind][0]))) for ind in topnindices]
        self.name_score.sort(key = operator.itemgetter(1), reverse = True)
        # print("algorithm predicts ", self.name_score)
        return self.name_score

    def queryalgorithm(self, querytext, num):
        self.transform(querytext)
        self.similarity()
        return self.toppredictions(num)