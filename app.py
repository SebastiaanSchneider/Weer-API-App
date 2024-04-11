"""
importeer data via api
verwerk data
exporteer data naar calender
geef data weer
"""
import uuid
from datetime import datetime
import pytz
import requests
from flask import Flask, render_template, Response
from icalendar import Calendar, Event


app = Flask(__name__, '/static')


# index route met test weergave
@app.route('/')
def get_weer():
    # importeer api data
    data = requests.get("http://api.weatherapi.com/v1/forecast.json?key=007ca694539c40549f8105112242603&q=Purmerend&days=7&aqi=no&alerts=no",  # pylint: disable=line-too-long
                        timeout=10).json()

    # haal data op en geef ze door aan index template om in tabel te zetten
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
    data = requests.get("http://api.weatherapi.com/v1/forecast.json?key=695b6ac170744c18bc780518241004&q=Purmerend&days=7&aqi=no&alerts=no",  # pylint: disable=line-too-long
                        timeout=10).json()

    # setup kalender variabele
    cal = Calendar()

    # basiscomponenten ical-format
    cal.add('prodid', '-//API Weer Kalender//weatherapi.com//')
    cal.add('version', '2.0')

    # itereer over elke dag en elk uur
    for day in data['forecast']['forecastday']:
        for hour in day['hour']:
            # opzet componenten
            event = Event()
            uid = str(uuid.uuid4())  # willekeurige uid voor elk uur aan
            start = hour['time']

            # split de componenten van de data en tijden
            delimiters = ["-", " ", ":"]
            for delimiter in delimiters:
                start = " ".join(start.split(delimiter))
            start = start.split()
            year = int(start[0])
            month = int(start[1])
            day = int(start[2])
            time_hour = int(start[3])
            time_minute = int(start[4])

            # opzet en verwerking van de individuele informatiepunten
            dauwpunt = str(hour['dewpoint_c']) + " C"
            gevoelstemperatuur = str(hour['feelslike_c']) + " C"
            luchtdruk = str(hour['pressure_mb']) + " mB"
            luchtvochtigheid = str(hour['humidity']) + "%"
            neerslag = str(hour['precip_mm']) + " mm"
            regen_kans = str(hour['chance_of_rain']) + "%"
            temperatuur = str(hour['temp_c']) + " C"
            text = hour['condition']['text']
            uv = str(hour['uv'])
            wind_snelheid = str(hour['wind_kph']) + " km/h"
            wind_temp = str(hour['windchill_c']) + " C"
            windrichting = hour['wind_dir']
            windstoten = str(hour['gust_kph']) + " km/h"
            zicht = str(hour['vis_km']) + " km"

            # header van elk agenda punt met hoofd informatie
            weer_kop = ("Vooruitzicht: " + text + " bij " + temperatuur +
                        " met " + regen_kans + " kans op regen en gemiddeld " +
                        neerslag + " neerslag.")
            # omschrijving van elk agenda punt met verdere details
            weerbericht = ("Gevoelstemperatuur: " + gevoelstemperatuur +
                           "\nDauwpunt: " + dauwpunt +
                           "\nLuchtvochtigheid: " + luchtvochtigheid +
                           "\nLuchtdruk: " + luchtdruk +
                           "\nUV Straling: " + uv +
                           "\nZicht: " + zicht +
                           "\nWindrichting: " + windrichting +
                           "\nWind Snelheid: " + wind_snelheid +
                           "\nWindstoten: " + windstoten +
                           "\nWind Temperatuur: " + wind_temp)

            # aanmaak componenten
            event.add('dtstart', datetime(year, month, day, time_hour,
                                          time_minute, 0, tzinfo=pytz.timezone('Europe/Amsterdam')))
            event.add('dtend', datetime(year, month, day, (time_hour + 1) % 24,
                                        time_minute, 0, tzinfo=pytz.timezone('Europe/Amsterdam')))
            event['uid'] = uid
            event.add('summary', weer_kop)
            event.add('description', weerbericht)
            event.transparent = False

            # voeg uur toe aan kalender
            cal.add_component(event)

    # geef .ics bestand terug
    return Response(cal.to_ical(), mimetype='text/calendar')


# route om de ical te vormen en hosten met een filter
@app.route('/ical/filter/<filters>')
def agenda_feed_filter(filters):
    # importeer api data en categoriseer filter
    if "locatie" in filters:
        # opzet filter voor locatie
        locatie = filters.split("=")[1]
        data = requests.get("http://api.weatherapi.com/v1/forecast.json?key=695b6ac170744c18bc780518241004&q="  # pylint: disable=line-too-long
                            + locatie + "&days=7&aqi=no&alerts=no",
                            timeout=10).json()
        verhouding = False
        variabele = False
        waarde = False
    else:
        data = requests.get("http://api.weatherapi.com/v1/forecast.json?key=695b6ac170744c18bc780518241004&q=Purmerend&days=7&aqi=no&alerts=no",  # pylint: disable=line-too-long
                            timeout=10).json()

        # opzet filter voor variabele
        if "=" in filters:
            filters = filters.split("=")
            verhouding = "="
        elif "<" in filters:
            filters = filters.split("<")
            verhouding = "<"
        elif ">" in filters:
            filters = filters.split(">")
            verhouding = ">"
        else:
            print("Error: operator niet herkend")
        variabele = filters[0].lower()
        waarde = int(filters[1])

    # setup kalender variabele
    cal = Calendar()

    # basiscomponenten ical-format
    cal.add('prodid', '-//API Weer Kalender//weatherapi.com//')
    cal.add('version', '2.0')

    # itereer over elke dag en elk uur
    for day in data['forecast']['forecastday']:
        for hour in day['hour']:
            # opzet componenten
            event = Event()
            uid = str(uuid.uuid4())  # maak willekeurige uid voor elk uur aan
            start = hour['time']

            # split de componenten van de data en tijden
            delimiters = ["-", " ", ":"]
            for delimiter in delimiters:
                start = " ".join(start.split(delimiter))
            start = start.split()
            year = int(start[0])
            month = int(start[1])
            day = int(start[2])
            time_hour = int(start[3])
            time_minute = int(start[4])

            # opzet en verwerking van de individuele informatiepunten
            dauwpunt = hour['dewpoint_c']
            gevoelstemperatuur = hour['feelslike_c']
            luchtdruk = hour['pressure_mb']
            luchtvochtigheid = hour['humidity']
            neerslag = hour['precip_mm']
            regen_kans = hour['chance_of_rain']
            temperatuur = hour['temp_c']
            text = hour['condition']['text']
            uv = hour['uv']
            wind_snelheid = hour['wind_kph']
            wind_temp = hour['windchill_c']
            windrichting = hour['wind_dir']
            windstoten = hour['gust_kph']
            zicht = hour['vis_km']

            # header van elk agenda punt met hoofd informatie
            weer_kop = ("Vooruitzicht: " + text + " bij " + str(temperatuur) +
                        " C met " + str(regen_kans) +
                        "% kans op regen en gemiddeld " + str(neerslag) +
                        " mm neerslag.")

            # omschrijving van elk agenda punt met verdere details
            weerbericht = ("Gevoelstemperatuur: " + str(gevoelstemperatuur) +
                           " C" + "\nDauwpunt: " + str(dauwpunt) + " C" +
                           "\nLuchtvochtigheid: " + str(luchtvochtigheid) +
                           "%" + "\nLuchtdruk: " + str(luchtdruk) + " mB" +
                           "\nUV Straling: " + str(uv) +
                           "\nZicht: " + str(zicht) + " km" +
                           "\nWindrichting: " + windrichting +
                           "\nWind Snelheid: " + str(wind_snelheid) + " km/h" +
                           "\nWindstoten: " + str(windstoten) + " km/h" +
                           "\nWind Temperatuur: " + str(wind_temp) + " C")

            # aanmaak componenten
            event.add('dtstart', datetime(year, month, day, time_hour,
                                          time_minute, 0, tzinfo=pytz.timezone('Europe/Amsterdam')))
            event.add('dtend', datetime(year, month, day, (time_hour + 1) % 24,
                                        time_minute, 0, tzinfo=pytz.timezone('Europe/Amsterdam')))
            event['uid'] = uid
            event.add('summary', weer_kop)
            event.add('description', weerbericht)
            event.transparent = False


            # opties = ['temperatuur', 'regenkans']

            # for optie in opties:
            #     if variabele == optie:
            #         var = {variabele : {verhouding: waarde}}
                    
            # uitvoering filter, voeg event alleen to als filter het toelaat
            if variabele is False:
                cal.add_component(event)
            elif variabele == "temperatuur":
                if verhouding == "=":
                    if temperatuur == waarde:
                        cal.add_component(event)
                elif verhouding == "<":
                    if temperatuur < waarde:
                        cal.add_component(event)
                elif verhouding == ">":
                    if temperatuur > waarde:
                        cal.add_component(event)
            elif variabele == "regenkans":
                if verhouding == "=":
                    if regen_kans == waarde:
                        cal.add_component(event)
                elif verhouding == "<":
                    if regen_kans < waarde:
                        cal.add_component(event)
                elif verhouding == ">":
                    if regen_kans > waarde:
                        cal.add_component(event)
            elif variabele == "neerslag":
                if verhouding == "=":
                    if neerslag == waarde:
                        cal.add_component(event)
                elif verhouding == "<":
                    if neerslag < waarde:
                        cal.add_component(event)
                elif verhouding == ">":
                    if neerslag > waarde:
                        cal.add_component(event)
            elif variabele == "gevoelstemperatuur":
                if verhouding == "=":
                    if gevoelstemperatuur == waarde:
                        cal.add_component(event)
                elif verhouding == "<":
                    if gevoelstemperatuur < waarde:
                        cal.add_component(event)
                elif verhouding == ">":
                    if gevoelstemperatuur > waarde:
                        cal.add_component(event)
            elif variabele == "dauwpunt":
                if verhouding == "=":
                    if dauwpunt == waarde:
                        cal.add_component(event)
                elif verhouding == "<":
                    if dauwpunt < waarde:
                        cal.add_component(event)
                elif verhouding == ">":
                    if dauwpunt > waarde:
                        cal.add_component(event)
            elif variabele == "luchtvochtigheid":
                if verhouding == "=":
                    if luchtvochtigheid == waarde:
                        cal.add_component(event)
                elif verhouding == "<":
                    if luchtvochtigheid < waarde:
                        cal.add_component(event)
                elif verhouding == ">":
                    if luchtvochtigheid > waarde:
                        cal.add_component(event)
            elif variabele == "luchtdruk":
                if verhouding == "=":
                    if luchtdruk == waarde:
                        cal.add_component(event)
                elif verhouding == "<":
                    if luchtdruk < waarde:
                        cal.add_component(event)
                elif verhouding == ">":
                    if luchtdruk > waarde:
                        cal.add_component(event)
            elif variabele == "uv straling":
                if verhouding == "=":
                    if uv == waarde:
                        cal.add_component(event)
                elif verhouding == "<":
                    if uv < waarde:
                        cal.add_component(event)
                elif verhouding == ">":
                    if uv > waarde:
                        cal.add_component(event)
            elif variabele == "zicht":
                if verhouding == "=":
                    if zicht == waarde:
                        cal.add_component(event)
                elif verhouding == "<":
                    if zicht < waarde:
                        cal.add_component(event)
                elif verhouding == ">":
                    if zicht > waarde:
                        cal.add_component(event)
            elif variabele == "windrichting":
                if verhouding == "=":
                    if windrichting == waarde:
                        cal.add_component(event)
                elif verhouding == "<":
                    if windrichting < waarde:
                        cal.add_component(event)
                elif verhouding == ">":
                    if windrichting > waarde:
                        cal.add_component(event)
            elif variabele == "wind snelheid":
                if verhouding == "=":
                    if wind_snelheid == waarde:
                        cal.add_component(event)
                elif verhouding == "<":
                    if wind_snelheid < waarde:
                        cal.add_component(event)
                elif verhouding == ">":
                    if wind_snelheid > waarde:
                        cal.add_component(event)
            elif variabele == "windstoten":
                if verhouding == "=":
                    if windstoten == waarde:
                        cal.add_component(event)
                elif verhouding == "<":
                    if windstoten < waarde:
                        cal.add_component(event)
                elif verhouding == ">":
                    if windstoten > waarde:
                        cal.add_component(event)
            elif variabele == "wind temperatuur":
                if verhouding == "=":
                    if wind_temp == waarde:
                        cal.add_component(event)
                elif verhouding == "<":
                    if wind_temp < waarde:
                        cal.add_component(event)
                elif verhouding == ">":
                    if wind_temp > waarde:
                        cal.add_component(event)

    # geef .ics bestand terug
    return Response(cal.to_ical(), mimetype='text/calendar')


if __name__ == '__main__':
    app.run(debug=True)
