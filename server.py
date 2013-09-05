from flask import Flask, render_template, jsonify
import urllib2
from dateutil import parser
from calendar import timegm
import xml.etree.ElementTree as ET

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/calendar.json")
def calendar():

    # Get current public calendar
    url = "https://www.google.com/calendar/feeds/epl.pdx%40gmail.com/public/full?start-min=2013-09-04T00:00:00-00:00&start-max=2013-09-11T00:00:00-00:00&singleevents=true"
    response = urllib2.urlopen(url)

    # Init return object
    calendar = {}
    calendar['events'] = []

    try:
        root = ET.fromstring(response.read())
        entries = root.findall('{http://www.w3.org/2005/Atom}entry')

        # Loop through events
        for entry in entries:

            # Event title and times
            title = entry.find('{http://www.w3.org/2005/Atom}title').text
            times =  entry.find('{http://schemas.google.com/g/2005}when').attrib

            # Parse times
            begin = parser.parse(times.get('startTime', None))
            end = parser.parse(times.get('endTime', None))

            # Pack
            calendar['events'].append(
                {
                    'title': title,
                    'begin': timegm(begin.utctimetuple()),
                    'begin-label': begin.strftime('%A %b %d, %I:%M %p'),
                    'end': timegm(end.utctimetuple()),
                    'end-label': end.strftime('%A %b %d, %I:%M %p'),
                })

    except:
        return jsonify({'message': "Google Lookup Failure"}), 500

    # Success
    return jsonify(dict({'message': "success"}, **calendar))

if __name__ == "__main__":
    app.debug = True
    app.run()
