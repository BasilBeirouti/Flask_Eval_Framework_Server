__author__ = 'BasilBeirouti'

from sklearn.feature_extraction.text import CountVectorizer
from BM25 import TF2BM25
import operator, os, numpy, time

class DocMatrix:

    def __init__(self, data_tuples, vectorizer = None, **kwargs):
        trainnames, traincontent = self.unpack_corpus(data_tuples)
        self.tse_dict = self.make_tse_dict(trainnames)
        self.tse_list = trainnames

        self.bm25 = False
        if "bm25" in kwargs:
            self.bm25 = kwargs["bm25"]
            kwargs.pop("bm25")
        #
        # self.mmap = True
        # if "mmap" in kwargs:
        #     self.mmap = kwargs["mmap"]
        #     kwargs.pop("mmap")

        self.vectorizer = vectorizer
        if vectorizer is None:
            self.vectorizer = self._make_vectorizer(traincontent, **kwargs)

        self.docmatrix = self.vectorize_content(traincontent)

        if self.bm25:
            self.docmatrix = self.okapi_weights(self.docmatrix)

        # if self.mmap:
        #     self.docmatrix = mem_map_save(self.docmatrix, "docmatrix")

    def _make_vectorizer(self, traincontent, min_df = 2, ngrams_range = (1,1)):
        self._bm_vectorizer = CountVectorizer(traincontent, min_df = min_df, ngram_range= ngrams_range)
        self._bm_vectobj = self._bm_vectorizer.fit(traincontent)
        return self._bm_vectobj

    def vectorize_content(self, content):
        print("building docmatrix (DocMatrix.vectorize_content method)")
        start = time.time()
        bm_vectout = self.vectorizer.transform(content)
        docmatrix = bm_vectout
        # docmatrix = numpy.asarray(bm_vectout.toarray())
        print("building docmatrix of size ", docmatrix.shape, " took ", time.time() - start, "\n")
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

    def toppredictions(self, similaritymatrix, recognized_tses, n = 1):
        topnindices = self.maxpoints(similaritymatrix, n)
        self.name_score = [(recognized_tses[ind], float("{0:.3f}".format(similaritymatrix[ind][0]))) for ind in topnindices]
        self.name_score.sort(key = operator.itemgetter(1), reverse = True)
        # print("algorithm predicts ", self.name_score)
        return self.name_score

    def evaluatealgorithm(self, testdata, n):
        testnames, testcontent = zip(*testdata)
        actualnames, qcontents = list(testnames), list(testcontent)
        qvect = self.docmatrix_obj.vectorize_content(qcontents)
        current_docmatrix, all_tses = self.docmatrix_obj.onshift_docmatrix(None)
        similaritymatrix = self.similarity(current_docmatrix, qvect)
        return self.evaluatepredictions(similaritymatrix, all_tses, testnames, n)

    def evaluatepredictions(self, similaritymatrix, trainnames, actualnames, n):
        if n == 1:
            out = numpy.argmax(similaritymatrix, axis = 0)
            self.predictednames = [trainnames[ind] for ind in out]
            bools1 = [self.predictednames[ii] == actualnames[ii] for ii in range(len(actualnames))]
            accuracy = sum(bools1)/len(bools1)
            randaccuracy = 1/len(trainnames)
            print("algorithm achieved ", accuracy, " accuracy")
            print("random achieved ", randaccuracy, " accuracy")
            print((accuracy)/(randaccuracy), " times better than random! \n")
        else:
            topnindices = numpy.argpartition(similaritymatrix, -n, axis = 0)[-n:]
            topnbools = [actualnames[ii] in set([trainnames[ind] for ind in topnindices[:, ii]]) for ii in range(topnindices.shape[1])]
            accuracy = sum(topnbools)/len(topnbools)
            randaccuracy = n/len(trainnames)
            print("in top ", str(n), " algorithm achieved ", accuracy , " accuracy")
            print("random achieved ", randaccuracy, " accuracy")
            print(accuracy/randaccuracy, " times better than random! \n")

    def similarity(self, current_docmatrix, qvect):
        print("calculating similarity (QueryMaster.similarity method)")
        start = time.time()
        matrixvectout = numpy.asmatrix(current_docmatrix)
        #NEED TO OPTIMIZE THIS LINE RIGHT BELOW!!!
        similaritymatrix = numpy.asarray(qvect.dot(matrixvectout.T).T)
        print("calculating similarity took ", time.time()-start, " seconds",  "\n")
        return similaritymatrix

    @staticmethod
    def maxpoints(matrix, n):
        if n == 1:
            topindex = numpy.argmax(matrix)
            return [topindex]

        elif n > 1:
            topnindices = numpy.argpartition(matrix, -n, axis = 0)[-n:]
            topnindices = [ind[0] for ind in topnindices]
            return topnindices

# def mem_map_save(matrix, name):
#     path = os.path.join(os.getcwd(), "ApplicationData")
#     if os.path.exists(path):
#         filepath = path + "/" + name
#         print(filepath)
#         numpy.save(filepath, matrix)
#         matrix = numpy.load(filepath + ".npy", mmap_mode = "r")
#     return matrix