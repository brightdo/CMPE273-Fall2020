import os
import io
import qrcode.image.svg
from PIL import Image
from flask import Flask, render_template, request, Response 
from sqlitedict import SqliteDict
import json

app = Flask(__name__)
mydict = SqliteDict('./my_db.sqlite', autocommit=True, encode=json.dumps, decode=json.loads)
qr=qrcode.QRCode(
    version=1,
    box_size=15,
    border=5
)


@app.route('/api/bookmarks', methods=['GET','POST'])
def put():
    if request.method == "POST":
        try:
            name = request.form["name"]
            url = request.form["url"]
            description = request.form["description"]
            json1 = {
                "name":name,
                "url": url,
                "description":description,
                "id": name,
                "count":0 
            }
            if  mydict.get(name) != None:
                return '"reason": "The given name already existed in the system', 400
            mydict[name] = json1
            returned = '"id": "{}"'.format(name)
            return returned,201
        except Exception as e:
             return str(e)
    else:
        return render_template("put.html")

@app.route('/api/bookmarks/<id>', methods=['GET'])
def url(id):

    if  mydict.get(id) == None:
        return "404 Not Found", 404
    import json
    y = json.loads(json.dumps(mydict[id]))
    y["count"] = y["count"] +1
    mydict[id] = y
    returned = '"id": "{}", \n "name": "{}", \n "url": "{}", \n "description": "{}"'.format(y["id"],y["name"], y["url"], y["description"])
    return returned

@app.route('/api/bookmarks/<id>/qrcode', methods=['GET'])
def qrcode(id):
    y = json.loads(json.dumps(mydict[id]))
    url =y["url"]
    import qrcode
    img = qrcode.make(url)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return Response(buffer.getvalue(), mimetype='image/png')


@app.route('/api/bookmarks/<id>', methods=["DELETE"])
def delete_member(id):
    del mydict[id]
    return ('', 204)
    
@app.route("/api/bookmarks/<id>/stats", methods=['GET'])
def geturl(id):

    if  mydict.get(id) == None:
        return "404 Not Found", 404
    old_etag = request.headers.get("If-None-Match", '')
    y= json.loads(json.dumps(mydict[id]))
    count = y["count"]
    new_etag = str(count)
    if (new_etag) == (old_etag):
        return ('',304)
    else:
        return str(count), 200, {'Etag': new_etag}



if __name__ == '__main__':
    app.run()