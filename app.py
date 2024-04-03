"""
importeer data via api
verwerk data
exporteer data naar calender
geef data weer
"""
from datetime import datetime
from flask import Flask, g, jsonify, render_template, request, Response
from icalendar import Calendar, Event, vCalAddress, vText
from pathlib import Path
import pytz
import os
import requests


app = Flask(__name__, '/static')


# index route met weergave vooruitzicht
@app.route('/')
def get_weer():

    data = requests.get("http://api.weatherapi.com/v1/forecast.json?key=007ca694539c40549f8105112242603&q=Purmerend&days=7&aqi=no&alerts=no").json()
    # print(data['location']['name'])
    print(data['current']['condition'])
    print(type(data['current']['condition']))
    print(data['forecast']['forecastday'][1]['date'])
    if data:
        datum = datetime.datetime.now()
        locatie = data['location']['name']

        return render_template("index.html", data=data, datum=datum, 
                               locatie=locatie)
    else:
        return "big sad, no data"

@app.route('/ical')
def geef_agenda_feed():
    ical = '''BEGIN:VCALENDAR
PRODID:-//Google Inc//Google Calendar 70.9054//EN
VERSION:2.0
CALSCALE:GREGORIAN
METHOD:PUBLISH
X-WR-CALNAME:test
X-WR-TIMEZONE:Europe/Amsterdam
BEGIN:VEVENT
DTSTART:20240403T080000Z
DTEND:20240403T100000Z
DTSTAMP:20240403T080705Z
UID:2c925eh6840mpla95ioc1gkrm4@google.com
CREATED:20240403T080016Z
LAST-MODIFIED:20240403T080034Z
SEQUENCE:0
STATUS:CONFIRMED
SUMMARY:Zonnig 20graden
TRANSP:OPAQUE
END:VEVENT
BEGIN:VEVENT
DTSTART:20240403T100000Z
DTEND:20240403T110000Z
DTSTAMP:20240403T080705Z
UID:30c52im316ahn415bd507uievp@google.com
CREATED:20240403T080051Z
LAST-MODIFIED:20240403T080051Z
SEQUENCE:0
STATUS:CONFIRMED
SUMMARY:Kankerheet 36graden
TRANSP:OPAQUE
END:VEVENT
BEGIN:VEVENT
DTSTART:20240403T110000Z
DTEND:20240403T130000Z
DTSTAMP:20240403T080705Z
UID:500ed7m8kebgu0544j5lu6i4rj@google.com
CREATED:20240403T080112Z
LAST-MODIFIED:20240403T080112Z
SEQUENCE:0
STATUS:CONFIRMED
SUMMARY:Helemaal kutweer 5 graden
TRANSP:OPAQUE
END:VEVENT
END:VCALENDAR

'''

    return Response(ical, mimetype='text/calendar')


if __name__ == '__main__':
    app.run(debug=True)
