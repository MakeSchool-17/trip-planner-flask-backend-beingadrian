from functools import wraps
from flask import request, Response, jsonify
import server
import bcrypt

def check_auth(username, password):
    users = server.app.db.users
    user = users.find_one({'username': username})
    user_password_encoded = user['password'].encode('utf-8')
    password_matches = bcrypt.hashpw(password.encode('utf-8'), user_password_encoded) == user_password_encoded

    return username == 'beingadrian' and password_matches

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        
        if not auth or not check_auth(auth.username, auth.password):
            message = {'error': 'Basic auth Required.'}
            resp = jsonify(message)
            resp.status_code = 401
            return resp

        return f(*args, **kwargs)
    return decorated
