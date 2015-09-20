from flask import Flask, render_template
from tfl_api import TflApi

app = Flask(__name__)


@app.route('/stops/<lat>/<lon>/')
def stops(lat, lon): 
    """Retrieve list of bus stops (type: STBC) around the user's location"""
    tfl_api = TflApi()

    stops = tfl_api.getStopList(lat, lon)

    stopcode_list = [s['StopCode1'] for s in stops]
    busses = tfl_api.getBusList(stopcode_list)

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
