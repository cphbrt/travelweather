import flask

def get_forecast(request):
    payload = { 'lat': request.args.get('lat'), 'long': request.args.get('long')}
    return flask.jsonify(payload)