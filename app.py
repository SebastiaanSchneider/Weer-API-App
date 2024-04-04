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
import re
import requests
import uuid

app = Flask(__name__, '/static')


# index route met test weergave
@app.route('/')
def get_weer():

    data = requests.get("http://api.weatherapi.com/v1/forecast.json?key=007ca694539c40549f8105112242603&q=Purmerend&days=7&aqi=no&alerts=no").json()

    if data:
        datum = datetime.now()
        locatie = data['location']['name']

        return render_template("index.html", data=data, datum=datum, 
                               locatie=locatie)
    else:
        return "big sad, no data"


# route om de ical te vormen en hosten
@app.route('/ical')
def geef_agenda_feed():
    # importeer api data
    data = requests.get(
        "http://api.weatherapi.com/v1/forecast.json?key=007ca694539c40549f8105112242603&q=Purmerend&days=7&aqi=no&alerts=no").json()

    # init the calendar
    cal = Calendar()

    # Some properties are required to be compliant
    cal.add('prodid', '-//My calendar product//example.com//')
    cal.add('version', '2.0')

    for day in data['forecast']['forecastday']:
        for hour in day['hour']:
            # opzet componenten
            event = Event()
            start = hour['time']
            
            delimiters = ["-", " ", ":"]
            for delimiter in delimiters:
                start = " ".join(start.split(delimiter))
            start = start.split()
            year = int(start[0])
            month = int(start[1])
            day = int(start[2])
            time_hour = int(start[3])
            time_minute = int(start[4])
 
            uid = str(uuid.uuid4())

            # combinatie weerbericht
            regen_kans = str(hour['chance_of_rain']) + "%"
            text = hour['condition']['text']
            dew_point = str(hour['dewpoint_c']) + "C"
            gevoelstemperatuur = str(hour['feelslike_c']) + "C"
            windvlagen = str(hour['gust_kph']) + "km/h"
            humidity = str(hour['humidity']) + "%"
            neerslag = str(hour['precip_mm']) + "mm"
            luchtdruk = str(hour['pressure_mb']) + "mB"
            temperature = str(hour['temp_c']) + "C"
            uv = str(hour['uv'])
            zicht = str(hour['vis_km']) + "km"
            windrichting = hour['wind_dir']
            wind_snelheid = str(hour['wind_kph']) + "km/h"
            wind_temp = str(hour['windchill_c']) + "C"
            weerbericht = ("Vooruitzicht: " + text + ", kans op regen: " + 
                           regen_kans + ", dew_point: " + dew_point + 
                           ", gevoelstemperatuur: " + gevoelstemperatuur + 
                           ", windvlagen: " + windvlagen + ", humidity: " + 
                           humidity + ", neerslag: " + neerslag + 
                           ", luchtdruk: " + luchtdruk + ", temperature: " + 
                           temperature + ", uv: " + uv + ", zicht: " + zicht + 
                           ", windrichting: " + windrichting + 
                           ", wind_snelheid: " + wind_snelheid + 
                           ", wind_temp: " + wind_temp)

            # aanmaak componenten
            event.add('dtstart', datetime(year, month, day, time_hour, 
                                          time_minute, 0, tzinfo=pytz.timezone('Europe/Amsterdam')))
            event.add('dtend', datetime(year, month, day,
                      (time_hour + 1) % 24, time_minute, 0, tzinfo=pytz.timezone('Europe/Amsterdam')))
            event['uid'] = uid
            event.add('summary', weerbericht)
            event.transparent = False

            # toevoegen componeneten aan cal
            cal.add_component(event)
    return Response(cal.to_ical(), mimetype='text/calendar')


if __name__ == '__main__':
    app.run(debug=True)
