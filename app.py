"""
importeer data via api
verwerk data
exporteer data naar calender
geef data weer
"""
from pickle import TRUE
from flask import Flask, g, jsonify, render_template, request
import datetime
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


if __name__ == '__main__':
    app.run(debug=True)
