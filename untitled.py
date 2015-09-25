import json

from flask import Flask, Response, request

from BM25.TextCleaning import cleanStringAndLemmatize, wordslist2string, changeback
from BM25.Deprecated import Bm25Query
from bm25test import temp

app = Flask(__name__)

def jsonVanilla(js,status):
    resp = Response( js ,status = status, mimetype='application/json')
    return resp

def errorResponseVanilla(description,status):
    return Response(json.dumps({"error":description}) ,status = status)

@app.route('/')
#right now just doing one product, vmax
def match():
    try:
        print(request)
        myjson = request.get_json(force=True)
        print("this is ",myjson)
    except Exception as inst:
        print(type(inst),inst.args,inst,"get getTSEs get json Fail!")
        return errorResponseVanilla("getTSEs "+str(type(inst)), status=500)
    try:
        print(myjson["problem_description"])
        probdesc = wordslist2string(cleanStringAndLemmatize(myjson["problem_description"]))
        predictions = temp.queryalgorithm(probdesc)
        predictions = [changeback(prediction) for prediction in predictions]

    except Exception as inst:
        return errorResponseVanilla("getTSEs "+str(type(inst)), status=500)
    data = {
        "error":"",
        "TSEs": predictions
    }
    print(data)
    js = json.dumps(data)
    return jsonVanilla(js,status=200)

if __name__ == '__main__':
    app.run(debug = True)
