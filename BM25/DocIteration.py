__author__ = 'BasilBeirouti'

import csv, os, random, glob, math, time
from BM25.TextCleaning import wordslist2string, cleanStringAndLemmatize

def changename(name):
    docname = name.replace("," , "_").replace(" " , "")
    return docname

class IterProbSums:

    def __init__(self, csvfilename):
        self.reader = csv.DictReader(open(csvfilename, encoding="utf-8"))

    def __iter__(self):
        for row in self.reader:
            name = row["sr_closer_name"]
            docname = name.replace("," , "_").replace(" " , "")
            newline = wordslist2string(cleanStringAndLemmatize(str(row["srvc_req_prob_text"])))
            yield docname, newline

class TestDocs:
    def __init__(self, directory):
        self.directory = directory
        self.tuples = []

    def __iter__(self):
        docnames = sorted([docname for docname in glob.glob(self.directory + "/*.txt")])
        for docname in docnames:
            with open(docname) as file:
                (filedir, filename) = os.path.split(docname)
                filename = filename.replace(".txt", "")
                for line in file:
                    # content = line.split()
                    if len(line) < 2:
                        continue
                    yield (filename, line)

class IterDocs:
    def __init__(self, directory):
        self.directory = directory
        self.tuples = []

    def __iter__(self):
        docnames = sorted([docname for docname in glob.glob(self.directory + "/*.txt")])
        for docname in docnames:
            with open(docname) as file:
                content = file.read()
                (filedir, filename) = os.path.split(docname)
                filename = filename.replace(".txt", "")
                content.replace("\n", " ")
                yield (filename, content)

def preparecwd(num):
    def emptyfolder(foldername):
        if os.path.exists(foldername):
            docs = [docname for docname in glob.glob(foldername + "/*.txt")]
            if len(docs) > 0:
                for doc in docs:
                    os.remove(doc)
    emptyfolder( str(num) + "/TrainCorpus")
    emptyfolder( str(num) + "/TestCorpus")

def twocorpora(csvfilename, num, percentintraining):
    preparecwd(num)
    if not os.path.exists(str(num) + "/TrainCorpus"):
        os.makedirs(str(num) + "/TrainCorpus")
    if not os.path.exists(str(num) + "/TestCorpus"):
        os.makedirs(str(num) + "/TestCorpus")
    reader = csv.DictReader(open(csvfilename, encoding = "utf-8"))
    for row in reader:
        name = row["sr_closer_name"]
        docname = name.replace("," , "_").replace(" " , "")
        if random.randrange(0,100)/100 < percentintraining:
            filepath = str(num) + "/TrainCorpus"+ "/" + docname + ".txt"
        else:
            filepath = str(num) + "/TestCorpus"+ "/" + docname + ".txt"
        with open(filepath, "a", encoding = "utf-8") as file:
            #write processed string, not raw string from csv
            newline = wordslist2string(cleanStringAndLemmatize(str(row["srvc_req_prob_text"])))
            if len(newline) > 2:
                newline = newline + " \n "
                file.write(newline)

def onecorpus(csvfilename, num):
    preparecwd(num)
    if not os.path.exists(str(num)):
        os.makedirs(str(num))
    reader = csv.DictReader(open(csvfilename, encoding = "utf-8"))
    for row in reader:
        name = row["sr_closer_name"]
        docname = name.replace("," , "_").replace(" " , "")
        filepath = str(num) + docname + ".txt"
        with open(filepath, "a", encoding = "utf-8") as file:
            #write processed string, not raw string from csv
            newline = wordslist2string(cleanStringAndLemmatize(str(row["srvc_req_prob_text"])))
            if len(newline) > 2:
                newline = newline + " \n "
                file.write(newline)

def prunecorpus(directory, min_prob_sum):
    docnames = [docname for docname in glob.glob(directory + "/*.txt")]
    for doc in docnames:
        with open(doc) as file:
            content = file.read()
        if len(content.split("\n")) < min_prob_sum:
            file.close()
            try:
                os.remove(doc)
            except PermissionError:
                time.sleep(0.1)
                os.remove(doc)

    oldlen = len(docnames)
    print(oldlen)

def removeuncommon(directory, common):
    docnames = [docname for docname in glob.glob(directory + "/*.txt")]
    for doc in docnames:
        (filedir, filename) = os.path.split(doc)
        if filename not in common:
            os.remove(doc)
    newlen = len([docname for docname in glob.glob(directory + "/*.txt")])
    print(newlen)

def preparecorpora(num, percentintraining, min_prob_sum):
    #first remove documents below minimum # of problem summaries
    prunecorpus(str(num) + "/TrainCorpus", round(percentintraining*min_prob_sum))
    prunecorpus(str(num) + "/TestCorpus", round((1-percentintraining)*min_prob_sum))
    train = [docname for docname in glob.glob(str(num) + "/" + "TrainCorpus" + "/*.txt")]
    trainnames = [filename for filedir, filename in (os.path.split(docname) for docname in train)]
    print(trainnames[0:10])
    test = [docname for docname in glob.glob(str(num) + "/" + "TestCorpus" + "/*.txt")]
    testnames = [filename for filedir, filename in (os.path.split(docname) for docname in test)]
    print(testnames[0:10])
    common = set(trainnames).intersection(set(testnames))
    #next remove all documents of all TSEs who do not exist in both corpora
    removeuncommon(str(num) + "/TrainCorpus", common)
    removeuncommon(str(num) + "/TestCorpus", common)
    return common

def randomcorpora(directory, percent_in_training, minprobsum):
    docnames = [docname for docname in glob.glob(directory + "/*.txt")]
    for docname in docnames:
        with open(docname) as file:
            (filedir, filename) = os.path.split(docname)
            filename = filename.replace(".txt", "")
            allprobsums = [line for line in file if len(line) > 1]
            numprobsums = len(allprobsums)
            newprobsums = random.sample(allprobsums, round(max(math.sqrt(numprobsums), min(numprobsums, percent_in_training*minprobsum))))
        with open(docname, "w") as file:
            file.writelines(newprobsums)

def eval_doall(csvfilename, num, percentintraining, minprobsum):
    preparecwd(num)
    twocorpora(csvfilename, num, percentintraining)
    preparecorpora(num, percentintraining, minprobsum)
    randomcorpora(str(num) + "/TrainCorpus", percentintraining, minprobsum)
    randomcorpora(str(num) + "/TestCorpus", 1-percentintraining, minprobsum)

def demo_doall(csvfilename, num, minprobsum):
    preparecwd(num)
    onecorpus(csvfilename, num)
    randomcorpora(num, 1, minprobsum)

def pre_post_cleansing(rownumber, csvfilename):
    reader = csv.DictReader(open(csvfilename, encoding = "utf-8"))
    rows = [row for row in reader]
    before = rows[rownumber]["srvc_req_prob_text"]
    after = wordslist2string(cleanStringAndLemmatize(before))
    print(before, " becomes ", after)
    return before, after

def allrows(csvfilename):
    reader = csv.DictReader(open(csvfilename, encoding = "utf-8"))
    rows = [row["srvc_req_prob_text"] for row in reader]
    return rows










