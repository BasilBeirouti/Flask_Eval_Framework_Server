__author__ = 'BasilBeirouti'

from sklearn.feature_extraction.text import CountVectorizer
from BM25.DocIteration import IterDocs, TestDocs
from BM25 import TF2BM25
import operator, os, numpy

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

class DocMatrix:

    def __init__(self, data_tuples, vectorizer = None, **kwargs):
        trainnames, traincontent = self.unpack_corpus(data_tuples)
        self.tse_dict = self.make_tse_dict(trainnames)
        self.tse_list = trainnames

        self.bm25 = False
        if "bm25" in kwargs:
            self.bm25 = kwargs["bm25"]
            kwargs.pop("bm25")

        self.mmap = True
        if "mmap" in kwargs:
            self.mmap = kwargs["mmap"]
            kwargs.pop("mmap")

        self.vectorizer = vectorizer
        if vectorizer is None:
            self.vectorizer = self._make_vectorizer(traincontent, **kwargs)

        self.docmatrix = self.vectorize_content(traincontent)

        if self.bm25:
            self.docmatrix = self.okapi_weights(self.docmatrix)

        if self.mmap:
            self.docmatrix = mem_map_save(self.docmatrix, "docmatrix")

    def _make_vectorizer(self, traincontent, min_df = 2, ngrams_range = (1,1)):
        self._bm_vectorizer = CountVectorizer(traincontent, min_df = min_df, ngram_range= ngrams_range)
        self._bm_vectobj = self._bm_vectorizer.fit(traincontent)
        return self._bm_vectobj

    def vectorize_content(self, content):
        bm_vectout = self.vectorizer.transform(content)
        docmatrix = numpy.asarray(bm_vectout.toarray())
        return docmatrix

    def onshift_docmatrix(self, tsesonshift = None):
        if tsesonshift is None:
            return self.docmatrix, self.tse_list
        recognized_tses = [tse for tse in tsesonshift if tse in self.tse_dict]
        rownums = [self.tse_dict[tse] for tse in recognized_tses]
        return self.docmatrix[rownums,:], recognized_tses

    @staticmethod
    def unpack_corpus(data):
        data.sort(key = operator.itemgetter(0))
        names, content = zip(*data)
        names, content = list(names), list(content)
        return names, content

    @staticmethod
    def make_tse_dict(trainnames):
        nums, names = zip(*enumerate(trainnames))
        return dict(list(zip(names, nums)))

    @staticmethod
    def okapi_weights(docmatrix):
        print("converting to BM25 representation")
        bm25obj = TF2BM25.OkapiWeights(docmatrix, 2, 1000, 0.75)
        bm25_docmatrix = bm25obj.make_bm25()
        return bm25_docmatrix

class QueryMaster:

    def __init__(self, docmatrix_obj):
        """
        :param docmatrix_obj: numpy matrix representing corpus. shape: (numtses, numwords)
        :type docmatrix_obj: numpy.ndarray
        """
        self.docmatrix_obj = docmatrix_obj

    def queryalgorithm(self, newquery, tsesonshift = None):
        current_docmatrix, recognized_tses = self.docmatrix_obj.onshift_docmatrix(tsesonshift)
        qvect = self.docmatrix_obj.vectorize_content([newquery])
        similaritymatrix = self.similarity(current_docmatrix, qvect)
        return self.toppredictions(similaritymatrix, recognized_tses, similaritymatrix.shape[0])

    def similarity(self, current_docmatrix, qvect):
        matrixvectout = numpy.asmatrix(current_docmatrix)
        matrixqvectsout = numpy.asmatrix(qvect)
        similaritymatrix = numpy.asarray(matrixvectout*matrixqvectsout.T)
        return similaritymatrix

    def toppredictions(self, similaritymatrix, recognized_tses, n = 1):
        topnindices = self.maxpoints(similaritymatrix, n)
        self.name_score = [(recognized_tses[ind], float("{0:.3f}".format(similaritymatrix[ind][0]))) for ind in topnindices]
        self.name_score.sort(key = operator.itemgetter(1), reverse = True)
        # print("algorithm predicts ", self.name_score)
        return self.name_score

    @staticmethod
    def maxpoints(matrix, n):
        if n == 1:
            topindex = numpy.argmax(matrix)
            return [topindex]

        elif n > 1:
            topnindices = numpy.argpartition(matrix, -n, axis = 0)[-n:]
            topnindices = [ind[0] for ind in topnindices]
            return topnindices

def mem_map_save(matrix, name):
    path = os.path.join(os.getcwd(), "ApplicationData")
    if os.path.exists(path):
        filepath = path + "/" + name
        print(filepath)
        numpy.save(filepath, matrix)
        matrix = numpy.load(filepath + ".npy", mmap_mode = "r")
    return matrix