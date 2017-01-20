#import sys
#reload(sys)
#sys.setdefaultencoding('ascii')
from flask import Flask, json, jsonify, Response, g, request
from flaskext.mysql import MySQL
import ast
#from flask.ext.restful.representations.json import output_json
#output_json.func_globals['settings'] = {'ensure_ascii': True, 'encoding': 'acsii'}

app = Flask(__name__)

mysql = MySQL()
app.config.from_pyfile('config.py')
mysql.init_app(app)

@app.before_request
def db_connect():
    g.conn = mysql.connect()
    g.cursor = g.conn.cursor()

@app.after_request
def db_disconnect(response):
    g.cursor.close()
    g.conn.close()
    return response

def queryToJson(query, args=(), one=False):
    g.cursor.execute(query, args)
    resValue = [dict((g.cursor.description[idx][0], value)
    for idx, value in enumerate(row)) for row in g.cursor.fetchall()]
    return (resValue[0] if resValue else None) if one else resValue

def jsonToQuery(jsonObj,table,operation):
    if operation == 'INSERT':
        #columns, values = zip(*jsonObj.items())    
        query = "INSERT INTO %s (%s) VALUES %s" %(table,','.join(jsonObj.keys()),tuple(jsonObj.values()))
        print "query:" + query
        #g.cursor.execute("INSERT INTO %s %s VALUES %s", (table,columns,values))
        g.cursor.execute(query)
        g.conn.commit()
        return "DONE"

    if operation == 'UPDATE':    
        #print "updating..."
        uList=list(map(lambda (k,v): str(k)+'="'+str(v)+'"' if (str(k)<>'id') else None, jsonObj.iteritems()))
        #print "uList: " + str(','.join(filter(None, uList)))
        query = "UPDATE %s SET %s WHERE id=%s" %(table,','.join(filter(None, uList)),int(jsonObj['id'])) 
        #print "query:" + str(query)
        g.cursor.execute(query)
        g.conn.commit()
        return "DONE"

@app.route("/")
def main():
    print "hello there"
    return "Index page loaded"

@app.route("/jobs", methods=["GET"], strict_slashes=False)
def jobList():
    result = queryToJson("SELECT * FROM developer")
    return jsonify(result)

@app.route("/jobs/<int:id>", methods=["GET","PUT"], strict_slashes=False)
def jobsById(id):
    if request.method == 'PUT':
        postJson = ast.literal_eval(json.dumps(request.json))
        #print "postJson:" + postJson['name']
        #g.cursor.execute("UPDATE developer SET name=%s, hireDate=%s, focus=%s WHERE id=%s", (postJson['name'],postJson['hireDate'], postJson['focus'],int(postJson['id'])))
        #g.conn.commit()
        jsonToQuery(postJson,'developer','UPDATE')
        resultData = Response("Updated", status=202, mimetype='application/json')
        return resultData

    jobData = queryToJson("SELECT * FROM developer WHERE id = %s", (int(id)))
    if jobData is None:
        return "No Job with id: %d" % id
    else:
        return jsonify(jobData)

@app.route("/addJob", methods=["POST"], strict_slashes=False)
def addNewJob():
    if request.method == 'POST':
        #postJson = json.dumps(request.json, ensure_ascii=True)
        postJson = ast.literal_eval(json.dumps(request.json))
        print "type of postjson:" + str(type(postJson))
        #print "postJson:" + str(postJson)
        #g.cursor.execute("INSERT INTO developer (name, hireDate, focus) VALUES (%s,%s,%s)", (postJson['name'],postJson['hireDate'], postJson['focus']))
        #g.conn.commit()
        jsonToQuery(postJson,'developer','INSERT')
        resultData = Response("Added", status=201, mimetype='application/json')
        return resultData


if __name__ == "__main__":
    app.run(debug=True)
