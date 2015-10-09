from flask import Flask, render_template, request
from werkzeug.exceptions import BadRequestKeyError
from tfl_api import TflApi
from geo import Geo
from utilities import Utilities as U

app = Flask(__name__)


@app.route('/stops', methods=['POST'])
def stops():
    """Retrieve list of bus stops (type: STBC) around the user's location"""
    tfl_api = TflApi()

    try:
        lat = request.form['lat']
        lon = request.form['lon']
    except BadRequestKeyError:
        try:
            postcode = request.form['postcode']
        except BadRequestKeyError:
            return render_template('main.html')  # bail out

        # Convert postcode to coordinates
        geo = Geo(postcode)
        lat, lon = geo.getLatitudeAndLongitude()

    stops = tfl_api.getStopList(lat, lon)

    stopcodes = [s['StopCode1'] for s in stops]
    busses = tfl_api.getBusList(stopcodes)

    results = []
    for stop in stops:
        result = {
            'name': '{name} ({letter})'.format(name=stop['StopPointName'], letter=stop['StopPointIndicator']),
            'busses': []
        }
        busses_for_stopcode = [b for b in busses if b['StopCode1'] == stop['StopCode1']]
        for bus in sorted(busses_for_stopcode, key=lambda i: i['EstimatedTime']):
            result['busses'].append({
                'number': bus['LineName'],
                'direction': bus['DestinationText'],
                'eta': U.format_time(bus['EstimatedTime'])
            })

        results.append(result)

    return render_template('results.html', results=results)


@app.route("/about")
def about():
    return render_template('about.html')


@app.route("/")
def home():
    return render_template('main.html')

if __name__ == "__main__":
    app.run('0.0.0.0', debug=True)
