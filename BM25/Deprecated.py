import csv
from BM25 import TF2BM25, BorgConnect
import numpy
import numpy as np
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


borg = BorgConnect()


@borg.with_connection
def lookupdict(cur, *args, **kwargs):
    query_lookup = """
SELECT
  DISTINCT person.row_wid, person.first_name, person.last_name, person.person_id
FROM
  emcas_engr_s360.profiles_person_it as person
  WHERE type like '%E%'
  ;
        """
    cur.execute(query_lookup)
    rows = cur.fetchall()
    return rows


def build_lookup_dict():
    rows = lookupdict()
    out = dict()
    out.update((tup[0],(tup[1], tup[2])) for tup in rows)
    return out


@borg.with_connection
def whoson(cur, *args, **kwargs):
    #in the query below, remember to remove the - and + CAST('50 hours' as interval) from the last line
    #it is only to get more data. Once all the data is in that table there's no need to artificially expand the query.
    query_whos_on =         """
    SELECT
        shift.person_id, shift.shift_start_date, shift.shift_duration
    FROM
        emcas_engr_s360.profiles_person_shift as shift
    WHERE
        (shift.shift_start_date, shift.shift_start_date + CAST(shift.shift_duration/60-1 || 'HOURS' as INTERVAL))
    OVERLAPS
        (now()::timestamp, now()::timestamp);
                            """
    print("in whoson")
    cur.execute(query_whos_on)
    print("executed with cursor")
    rows = cur.fetchall()
    print("returned results")
    return rows


def writetodisk(personids, filehandle):
    arr = np.asarray(personids, dtype = np.int32)
    np.save(filehandle, arr)


def updatelist(filehandle):
    rows = whoson()
    #get the personids out of the list of tuples
    personids = list(set(int(tup[0]) for tup in rows))
    writetodisk(personids, filehandle)
    return personids


@borg.with_connection
def srdata(cur, *args, **kwargs):
    query_srdata = "SELECT DISTINCT work.sr_num, work.sr_owner_person_id, work.sr_owner, work.problem_description FROM emcas_engr_s360.profiles_work_it as work;"
    cur.execute(query_srdata)
    rows = cur.fetchall()
    return rows


@borg.with_connection
def getwork(cur, *args, **kwargs):
    query_getwork = """
    SELECT
    DISTINCT SR.SRVC_REQ_NUM AS SR_NUM,
    WPD.EMPL_BDGE_NUM AS SR_OWNER_PERSON_ID,
    RSR.PERS_FULL_NM AS SR_OWNER,
    SR.SRVC_REQ_PROB_TEXT AS PROBLEM_DESCRIPTION
    FROM
    EMCAS_ENGR_S360.W_SERVICE_REQUEST_D SR,
    EMCAS_ENGR_S360.W_RESOURCE_ROLE_REF RSR,
    EMCAS_ENGR_S360.W_PERSON_D WPD
    WHERE
    SR.SRVC_REQ_OWNR_RSRC_ID = RSR.RSRC_ID
    AND
    RSR.PERS_11I_ID = WPD.PERS_11I_ID
    AND
    SR.SRVC_REQ_CRTE_DT;
        """
    cur.execute(query_getwork)
    with open("RawData/getwork.csv", 'wt') as csvfile:
        spamwriter = csv.writer(csvfile)
        for row in cur:
            spamwriter.writerow(row)
    cur.close()


@borg.with_connection
def getalltses(cur, *args, **kwargs):
    query_getalltses = """
    SELECT
    DISTINCT PERSON.EMPL_BDGE_NUM AS PERSON_ID,
    PERSON.PERS_FIRST_NM AS FIRST_NAME,
    PERSON.PERS_LAST_NM AS LAST_NAME
    FROM
    EMCAS_ENGR_S360.W_PERSON_D AS PERSON
    WHERE EMC_EMP_TYPE LIKE 'Employee'
    AND PERSON.EMPL_BDGE_NUM is not NULL;
"""
    cur.execute(query_getalltses)
    with open("RawData/getalltses.csv", 'wt') as csvfile:
        spamwriter = csv.writer(csvfile)
        for row in cur:
            spamwriter.writerow(row)
    cur.close()