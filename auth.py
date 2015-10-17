from functools import wraps
from flask import request, Response, jsonify

def check_auth(username, password):
    return username == 'beingadrian' and password == 'secret'

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or check_auth(auth.username, auth.password):
            message = {'error': 'Basic auth Required.'}
            resp = jsonify(message)
            resp.status_code = 401
            return resp

        return f(*args, **kwargs)
    return decorated
