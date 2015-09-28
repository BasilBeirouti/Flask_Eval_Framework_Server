__author__ = 'BasilBeirouti'

import functools
from nltk.corpus import wordnet as wn
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import stopwords

lmtzr = WordNetLemmatizer()
lemmas = {"has":"has","was":"be"}
lemmas["rpa"] = "rp"
lemmas["rpas"] = "rp"
lemmas["esrs"] = "esrs"
lemmas["nas"] = "nas"
lemmas["config"] = "configuration"
lemmas["luns"] = "lun"
lemmas["commond"] = "command"
lemmas["vplex"] = "vplex"


#lemmatization using NLTK
def myLemmatize(token):
    if not token in lemmas:
        lemma = wn.morphy(token)
        if lemma is None:
            lemma = token
        if lemma == token:
            lemma = lmtzr.lemmatize(token)
        if lemma == token:
            lemma = lmtzr.lemmatize(token,"v")
        lemmas[token] = lemma
    return lemmas[token]

def remove_stpwrds(function):
    sw = set(stopwords.words())
    @functools.wraps(function)
    def wrapped(*args, **kwargs):
        result = function(*args, **kwargs)
        removed = list(set(result) - sw)
        result = [word for word in result if word in removed]
        return result
    return wrapped

#some tokenization and cleansing
@remove_stpwrds
def cleanStringAndLemmatize(mytext):
    cleantext = mytext
    space_chars = """ "12345678910.,|:!()_-?'/\t\n """
    for char in space_chars:
        if char in cleantext:
            cleantext = cleantext.replace(char," ")
    #remove the list() function if you want to return a map object directly
    words = list(map(myLemmatize,cleantext.lower().split()))
    return words

def wordslist2string(wordslist):
    return str.strip(" ".join(wordslist))

def string2wordslist(string):
    return string.split()

def changename(name):
    docname = name.replace("," , "_").replace(" " , "")
    return docname

def changeback(name):
    out = name.split("_")
    return out[0] + ", " + out[1]

def text_scrub(func):
    def wrapped(*args, **kwargs):
        return cleanStringAndLemmatize(func(*args, **kwargs))
    return wrapped
