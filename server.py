from flask import Flask, request, make_response, jsonify, json
from flask_restful import Resource, Api
from pymongo import MongoClient
from bson.objectid import ObjectId
from bson.json_util import dumps
from utils.mongo_json_encoder import JSONEncoder
from auth import requires_auth
import bcrypt
import base64

# Basic Setup
app = Flask(__name__)
mongo = MongoClient('localhost', 27017)
app.db = mongo.develop_database
api = Api(app)


# Implement Trip resource
class Trip(Resource):

    # post new trip to database
    @requires_auth
    def post(self):
        # authentication
        auth = request.authorization
        owner = auth.username

        # access the JSON provided by client
        new_trip_object = request.json
        new_trip_object['owner'] = owner

        # access colleciton in database to store the new object
        trip_object_collection = app.db.trips
        result = trip_object_collection.insert_one(new_trip_object)
        trip_object = trip_object_collection.find_one({"_id": ObjectId(result.inserted_id)})
        return trip_object

    # get trip with id or username
    @requires_auth
    def get(self, trip_object_id=None):
        # authorization
        auth = request.authorization
        owner = auth.username

        # access trip object collection
        trip_object_collection = app.db.trips
        returned_object = None
        if trip_object_id is not None:
            # get trip by id
            returned_object = trip_object_collection.find_one({"_id": ObjectId(trip_object_id), "owner": owner})
        else:
            cursor_object = trip_object_collection.find({"owner": owner})
            # convert cursor object
            # [Ben-G] You can convert the cursor into a list using the list() function
            # trips = list(cursor_object) 
            # Above line will do the same as encoding/decoding but code is cleaner
            json_object = dumps(cursor_object)
            returned_object = json.loads(json_object)
        # check if trip_object is found or not
        if returned_object is None:
            response = jsonify(data=[])
            response.status_code = 404
            return response
        else:
            return returned_object

    # update trip with id
    @requires_auth
    def put(self, trip_object_id):
        # access new_trip_id
        new_trip_object = request.json
        # access trip object collection
        trip_object_collection = app.db.trips
        # [Ben-G] Might still be in the works, but you should verify that the trip that's being
        # updated belongs to the authenticated user
        result = trip_object_collection.update_one({"_id": ObjectId(trip_object_id)}, {"$set": new_trip_object})
        updated_trip_object = trip_object_collection.find_one({"_id": ObjectId(trip_object_id)})
        # check if trip_object is found or not
        if updated_trip_object is None:
            response = jsonify(data=[])
            response.status_code = 404
            return response
        else:
            # trip found and updated
            return updated_trip_object

    # delete trip with id
    @requires_auth
    def delete(self, trip_object_id):
        # access trip object collection
        trip_object_collection = app.db.trips
        # perform deletion
        # [Ben-G] Might still be in the works, but you should verify that the trip that's being
        # deleted belongs to the authenticated user
        result = trip_object_collection.delete_one({"_id": ObjectId(trip_object_id)})
        if result.deleted_count == 0:
            # nothing deleted
            response = jsonify(data=[])
            response.status_code = 404
            return response
        else:
            response = jsonify(data=[])
            response.status_code = 200
            return response


class User(Resource):

    # post new User to database
    def post(self):
        # access the JSON provided by client
        new_user_object = request.json
        # check
        try:
            password = new_user_object["password"]
            password_encoded = password.encode('utf-8')
            hashed_password = bcrypt.hashpw(password_encoded, bcrypt.gensalt(12))
            new_user_object["password"] = hashed_password.decode('utf-8')
        # [Ben-G] Which type of exception are you trying to catch here? You should state the specific one.
        # If you don't specify, you catch all. Catching all exceptions is considered bad practice since you
        # might swallow errors that you would like to know about.
        except:
            # no password
            print("No password")
            return
        # access colleciton in database to store the new object
        user_object_collection = app.db.users

        # check if user already exists (and passwords using regex someday)
        check_result = user_object_collection.find_one({"username": new_user_object["username"]})
        if check_result is not None:
            # username already exists
            response = jsonify(data=[])
            # [Ben-G] Nice use of status codes :)
            response.status_code = 409
            return response

        result = user_object_collection.insert_one(new_user_object)
        user_object = user_object_collection.find_one({"_id": ObjectId(result.inserted_id)})
        return user_object

    # get user with id
    # [Ben-G] Might in the works: this endpoint should also require authentication since it will be used
    # by the client to verify a user's credentials
    def get(self, user_object_id):
        # access user object collection
        user_object_collection = app.db.users
        user_object = user_object_collection.find_one({"_id": ObjectId(user_object_id)})
        # check if user_object is found or not
        if user_object is None:
            response = jsonify(data=[])
            response.status_code = 404
            return response
        else:
            return user_object

# Add REST User resource to API
api.add_resource(User, '/users/', '/users/<string:user_object_id>')
api.add_resource(Trip, '/trips/', '/trips/<string:trip_object_id>')

# provide a custom JSON serializer for flaks_restful
@api.representation('application/json')
def output_json(data, code, headers=None):
    resp = make_response(JSONEncoder().encode(data), code)
    resp.headers.extend(headers or {})
    return resp

if __name__ == '__main__':
    # Turn this on in debug mode to get detailled information about request related exceptions: http://flask.pocoo.org/docs/0.10/config/
    app.config['TRAP_BAD_REQUEST_ERRORS'] = True
    app.run(debug=True)
