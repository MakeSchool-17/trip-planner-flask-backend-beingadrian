from flask import Flask, request, make_response, jsonify
from flask_restful import Resource, Api
from pymongo import MongoClient
from bson.objectid import ObjectId
from utils.mongo_json_encoder import JSONEncoder

# Basic Setup
app = Flask(__name__)
mongo = MongoClient('localhost', 27017)
app.db = mongo.develop_database
api = Api(app)


# Implement Trip resource
class Trip(Resource):

    # post new trip to database
    def post(self):
        # access the JSON provided by client
        new_trip_object = request.json
        # access colleciton in database to store the new object
        trip_object_collection = app.db.trips
        result = trip_object_collection.insert_one(new_trip_object)
        trip_object = trip_object_collection.find_one({"_id": ObjectId(result.inserted_id)})
        return trip_object

    # get trip with id or username
    def get(self, trip_object_id=None, user_object_id=None):
        # access trip object collection
        trip_object_collection = app.db.trips
        trip_object = trip_object_collection.find_one({"_id": ObjectId(trip_object_id)})
        # check if trip_object is found or not
        if trip_object is None:
            response = jsonify(data=[])
            response.status_code = 404
            return response
        else:
            return trip_object

    # update trip with id
    def put(self, trip_object_id):
        # access new_trip_id
        new_trip_object = request.json
        # access trip object collection
        trip_object_collection = app.db.trips
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
    def delete(self, trip_object_id):
        # access trip object collection
        trip_object_collection = app.db.trips
        # perform deletion
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

    def get_trips(self, user_object_id):
        # access user collection
        trip_object_collection = app.db.trips
        trip_objects = trip_object_collection.find({"user_object_id": ObjectId(user_object_id)})
        if trip_objects is None:
            response = jsonify(data=[])
            response.status_code = 404
            return response
        else:
            return trip_objects


# Add REST Trip resource to API
api.add_resource(Trip, '/trips/', '/trips/<string:trip_object_id>')


class User(Resource):

    # post new User to database
    def post(self):
        # access the JSON provided by client
        new_user_object = request.json
        # access colleciton in database to store the new object
        user_object_collection = app.db.users
        result = user_object_collection.insert_one(new_user_object)
        user_object = user_object_collection.find_one({"_id": ObjectId(result.inserted_id)})
        return user_object

    # get user with id
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
