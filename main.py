from flask import Flask, render_template
from tfl_api import TflApi
from utilities import Utilities as U

app = Flask(__name__)


@app.route('/stops/<lat>/<lon>/')
def stops(lat, lon): 
    """Retrieve list of bus stops (type: STBC) around the user's location"""
    tfl_api = TflApi()

    stops = tfl_api.getStopList(lat, lon)

    stopcodes = [s['StopCode1'] for s in stops]
    busses = tfl_api.getBusList(stopcodes)

    text = []
    for stop in stops:
        text.append('Stop {name} ({letter}):'\
            .format(name=stop['StopPointName'], letter=stop['StopPointIndicator']))

        busses_for_stopcode = [b for b in busses if b['StopCode1'] == stop['StopCode1']]
        for bus in sorted(busses_for_stopcode, key=lambda i: i['EstimatedTime']):
            text.append('{line} towards {destination} should arrive at {time}'\
                .format(line=bus['LineName'], destination=bus['DestinationText'],
                        time=U.format_time(bus['EstimatedTime'])))

    return '<br/>'.join(text)



@app.route("/")
def main():
    return render_template('main.html')

if __name__ == "__main__":
    app.run(debug=True)
