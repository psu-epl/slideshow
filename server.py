from flask import Flask, render_template, jsonify
import urllib2
from dateutil import parser
from calendar import timegm
import datetime
from datetime import tzinfo
import xml.etree.ElementTree as ET

app = Flask(__name__)

class UTC(tzinfo):
    """UTC"""
    def utcoffset(self, dt):
        return datetime.timedelta(0)
    def tzname(self, dt):
        return "UTC"
    def dst(self, dt):
        return datetime.timedelta(0)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/calendar.json")
def calendar():

    # times
    now = datetime.datetime.utcnow()
    today = datetime.datetime(now.year, now.month, now.day, 10, 0, 0, 0, UTC())  
    tonight = datetime.datetime(now.year, now.month, now.day, 10, 0, 0, 0, UTC()) + datetime.timedelta(days=1)

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
                'begin': begin,
                #'begin-label': begin.strftime('%A %b %d, %I:%M %p'),
                'end': end,
              })

        # sort by date
        calendar['events'] = sorted(calendar['events'], key=lambda event: event['begin'])
    except:
        return jsonify({'message': "Google Lookup Failure"}), 500

    todays = {'events': []}
    upcoming = {'events': []}

    # Divide up today vs this week
    for event in calendar['events']:
        if event['begin'] < tonight:
            todays['events'].append({
                'title': event['title'],
                'begin': timegm(event['begin'].utctimetuple()),
                'begin-label': event['begin'].strftime('%A %b %d, %I:%M %p'),
                'end': timegm(event['end'].utctimetuple()),
                'end-label': event['end'].strftime('%A %b %d, %I:%M %p'),
            })
        else:
            upcoming['events'].append({
                'title': event['title'],
                'begin': timegm(event['begin'].utctimetuple()),
                'begin-label': event['begin'].strftime('%A %b %d, %I:%M %p'),
                'end': timegm(event['end'].utctimetuple()),
                'end-label': event['end'].strftime('%A %b %d, %I:%M %p'),
            })

    # Push to frontend
    union = {'today': todays, 'upcoming': upcoming}
    return jsonify(dict({'message': "success"}, **union))

if __name__ == "__main__":
    app.debug = True
    app.run()
