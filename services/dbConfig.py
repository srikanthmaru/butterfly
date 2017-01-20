from flask import Flask, json, jsonify, Response, g, request
from flaskext.mysql import MySQL

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

def query_db(query, args=(), one=False):
    #print "query: " + query + ' ' + "args:" + args
    g.cursor.execute(query, args)
    resValue = [dict((g.cursor.description[idx][0], value)
    for idx, value in enumerate(row)) for row in g.cursor.fetchall()]
    return (resValue[0] if resValue else None) if one else resValue

@app.route("/", strict_slashes=False)
def main():
    print "hello there"
    return "Index page loaded"

@app.route("/sourcedbs", methods=["GET"], strict_slashes=False)
def dbList():
    if request.args.get('search') is None: 
        result = query_db("SELECT * FROM developer")
        return jsonify(result)
    else:
        searchValue = "{}{}{}".format('%%',request.args.get('search'),'%%')
        #searchValue = request.args.get('search')
        #print "searchValue:" + searchValue
        query = "SELECT * FROM developer WHERE CONCAT_WS('',id,name,hireDate,focus) LIKE '" + (str(searchValue)) + "'"
        #print "query:" + query
        result = query_db(query)
        return jsonify(result)
#@app.route("/sourcedbs/<string:searchValue>", methods=["GET"])
#def dbSearch():
#    result = query_db("SELECT * FROM developer WHERE id like '{searchParam}' or name like '{searchParam}' or hireDate like '{searchParam}' or focus like '{searchParam}'".format(searchParam=searchValue))
#    return jsonify(result)


@app.route("/sourcedbs/<int:id>", methods=["GET","PUT"], strict_slashes=False)
def dbById(id):
    if request.method == 'PUT':
        postJson = request.json
        print "postJson:" + postJson['name']
        g.cursor.execute("UPDATE developer SET name=%s, hireDate=%s, focus=%s WHERE id=%s", (postJson['name'],postJson['hireDate'], postJson['focus'],int(postJson['id'])))
        g.conn.commit()
        resultData = Response("Updated", status=202, mimetype='application/json')
        return resultData

    jobData = query_db("SELECT * FROM developer WHERE id = %s", (int(id)))
    if jobData is None:
        return "No Job with id: %d" % id
    else:
        return jsonify(jobData)

@app.route("/addsourcedb", methods=["POST"], strict_slashes=False)
def addNewDb():
    if request.method == 'POST':
        postJson = request.json
        #print "postJson:" + str(postJson)
        g.cursor.execute("INSERT INTO developer (name, hireDate, focus) VALUES (%s,%s,%s)", (postJson['name'],postJson['hireDate'], postJson['focus']))
        g.conn.commit()
        resultData = Response("Added", status=201, mimetype='application/json')
        return resultData


if __name__ == "__main__":
    app.run(port=5001, debug=True)
