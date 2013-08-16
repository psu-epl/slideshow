from flask import Flask, render_template
import httplib
import xml.etree.ElementTree as ET

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/cal")
def cal():
    c = httplib.HTTPSConnection("www.google.com")
    c.request("GET", "/calendar/feeds/epl.pdx%40gmail.com/public/basic")
    response = c.getresponse()

    root = ""
    if response.status == 200:
        data = response.read()
        root = ET.fromstring(data)

    for child in root:
        print child.tag, child.attrib

    return root.tag

if __name__ == "__main__":
    app.debug = True
    app.run()
