from functools import wraps
from flask import request, Response, jsonify
import server
import bcrypt

def check_auth(username, password):
    users = server.app.db.users
    user = users.find_one({'username': username})
    user_password_encoded = user['password'].encode('utf-8')
    # [Ben-G] Careful! Here you are comparing the stored password to the stored password! You are not actually
    # checking the password that the user entered! You should add a test that catches this scenario. The test
    # should use an incorrect password and expect a 401 status code when hitting an endpoint that requires authentication
    password_matches = bcrypt.hashpw(password.encode('utf-8'), user_password_encoded) == user_password_encoded

    # [Ben-G] once your implementation is complete you can remove the hardcoded username 'beingadrian'
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
