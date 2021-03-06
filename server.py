from flask import Flask, render_template, jsonify
import urllib2
from dateutil import parser
from calendar import timegm
import datetime
from datetime import tzinfo
import xml.etree.ElementTree as ET
import config

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

@app.route("/draw")
def draw():
    return render_template('events.html')


@app.route("/drawdom")
def drawdom():
    return render_template('events_dom.html')


@app.route("/calendar.json")
def calendar():

    # times
    now = datetime.datetime.utcnow()
    today = datetime.datetime(now.year, now.month, now.day, 10, 0, 0, 0, UTC())  
    tonight = datetime.datetime(now.year, now.month, now.day, 10, 0, 0, 0, UTC()) + datetime.timedelta(days=1)

    # Get current public calendar
    url = config.CALENDAR_URL % (today.isoformat(), (today+datetime.timedelta(days=8)).isoformat())
    # TODO: this is a bad hack
    url = url.replace('+','-')
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
            calendar['events'].append({
                'title': title,
                'begin': begin,
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
            begin_hour = event['begin'].hour + (event['begin'].minute/60.0)
            end_hour = event['end'].hour + (event['end'].minute/60.0)
            todays['events'].append({
                'title': event['title'],
                'begin': begin_hour,
                'begin-label': event['begin'].strftime('%I:%M %p'),
                'end': end_hour,
                'end-label': event['end'].strftime('%I:%M %p'),
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
