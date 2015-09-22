
from flask import Flask, Response
import sys
import os
from datetime import date
from datetime import datetime
from flask import after_this_request, request
import gzip
import functools
from io import StringIO

app = Flask(__name__)
Compress(app)

from collections import defaultdict,Counter


cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

import json
from time import time

def toTimeStamp(dt):
    return (dt - datetime(1970,1,1)).total_seconds()

from flask import request, current_app

def jsonVanilla(js,status):
    resp = Response( js ,status = status, mimetype='application/json')
    return resp

def errorResponseVanilla(description,status):
    return Response(json.dumps({"error":description}) ,status = status)

"""
/intellimatch/<product>
request:
{
�problem_description�:�the text�'
}

return:
{
error:""
,�model�:�name of model�,
�tses�:[(�name�,score)�]
}
"""
@app.route('/intellimatch/<product>',methods=['GET','POST'])
@cross_origin()
def getTSEs(product):
    print("getTSEs",product)

    try:
        print(request)
        myjson = request.get_json(force=True)
        print("this is ",myjson)
    except Exception as inst:
        print(type(inst),inst.args,inst,"get getTSEs get json Fail!")
        return errorResponseVanilla("getTSEs "+type(inst), status=500)
    try:
        print(myjson["problem_description"])
        """
        put rest of the code here
        """
    except Exception as inst:
        return errorResponseVanilla("getTSEs "+type(inst), status=500)
    data = {
        "error":"",
        #add the list of TSEs here
    }
    print(data)
    js = json.dumps(data)
    return jsonVanilla(js,status=200)



if __name__ == "__main__":
    try:
        app.run(host='0.0.0.0',port=int(sys.argv[1]))
    except:
        app.run(host='0.0.0.0')
    #"""
