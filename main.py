from flask import Flask, render_template
from utilities import Utilities as U

app = Flask(__name__)

base_url = 'http://countdown.api.tfl.gov.uk/interfaces/ura/instant_V1?'


@app.route('/stops/<lat>/<lon>/')
def stops(lat, lon): 
    """Retrieve list of bus stops (type: STBC) around the user's location"""

    radius = str(300)
    return_list = [
        'StopPointName',
        'StopCode1',
        'Bearing',
        'StopPointIndicator',
        'Latitude',
        'Longitude'
    ]

    query = 'Circle={lat},{lon}'.format(lat=lat, lon=lon) + ',' + \
            radius + ',' + \
            '&StopPointState=0&StopPointType=STBC' + \
            '&ReturnList=' + ','.join(return_list)
    url = base_url + query
    response = U.url_open(url, 'Error retrieving list of stops')

    timestamp = response.readline()
    result = response.readlines()

    stops = []
    for r in result:
        # Clean entry and split into a list
        r = r.rstrip().strip('[]').split(',')
        # Discard first element (always 0) and replace any leading/trailing double quotes
        r = [i.strip('"') for i in r[1:]]
        stops.append(dict(zip(return_list, r)))

    stopcode_list = [s['StopCode1'] for s in stops]
    return getBus(stopcode_list)


@app.route('/bus/<stop_list>')
def getBus(stop_list):
    """"""
    return_list = [
        'StopPointName',
        'StopCode1',
        'LineName',
        'DestinationText',
        'EstimatedTime',
    ]

    stops = ','.join(stop_list)
    query = 'StopCode1={},75422'.format(stops) + \
            '&DirectionID=1&VisitNumber=1' + \
            '&ReturnList=' + ','.join(return_list)

    url = base_url + query
    response = U.url_open(url, 'Error retrieving list of busses')

    timestamp = response.readline()
    result = response.readlines()

    busses = []
    for r in result:
        # Clean entry and split into a list
        r = r.rstrip().strip('[]').split(',')
        # Discard first element (always 1) and replace any leading/trailing double quotes
        r = [i.strip('"') for i in r[1:]]
        # Convert epoch time to readable format
        r = r[:-1] + [U.epoch_to_localtime(r[-1])]
        busses.append(dict(zip(return_list, r)))

    a = []
    for b in busses:
        x = ', '.join(['{}: {}'.format(k, v) for (k, v) in b.items()])
        a.append(x)
    return '<br/>'.join(sorted(a, key=lambda x: x[0]))


@app.route("/")
def main():
    return render_template('main.html')

if __name__ == "__main__":
    app.run(debug=True)
