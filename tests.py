import server
import unittest
import json
from pymongo import MongoClient
import bcrypt
import base64
from requests.auth import HTTPBasicAuth
from flask import request

class FlaskrTestCase(unittest.TestCase):

    # authorization
    base64_obj = "beingadrian:abc123"
    base64_str = base64.encodebytes(base64_obj.encode('utf-8'))
    basic_str = "Basic " + base64_str.decode('utf-8').strip('\n')
    headers = {"Authorization": basic_str}


    def setUp(self):
        self.app = server.app.test_client()
        # Run app in testing mode to retrieve exceptions and stack traces
        server.app.config['TESTING'] = True

        # Inject test database into application
        mongo = MongoClient('localhost', 27017)
        db = mongo.test_database
        server.app.db = db

        # Drop collection (significantly faster than dropping entire db)
        db.drop_collection('trips')
        db.drop_collection('users')

        # create user to start with
        user_response = self.app.post('/users/',
            data=json.dumps(dict(
                username="beingadrian",
                password="abc123"
            )),
            content_type='application/json')

    # ===================
    #   TRIP TESTS
    # ===================

    def test_posting_trip(self):
        # post trip
        response = self.app.post('/trips/',
            data=json.dumps(dict(
                name="A trip"
            )),
            content_type='application/json',
            headers=self.headers)

        response_json = json.loads(response.data.decode())

        self.assertEqual(response.status_code, 200)
        assert 'application/json' in response.content_type
        assert 'A trip' in response_json["name"]

    def test_getting_trip(self):
        # ======== FIXED ========
        # [Ben-G] here, and in other cases, username and pw should be passed as
        # part of authorization header instead of as part of the body
        # Additionally, instead of duplicating the code to create a user in each test
        # case that requires authentication, you can move this code into the setup function

        # create trip response
        trip_response = self.app.post('/trips/',
            data=json.dumps(dict(
                name="A trip"
            )),
            content_type='application/json',
            headers=self.headers)

        trippost_response_json = json.loads(trip_response.data.decode())
        tripposted_object_id = trippost_response_json["_id"]

        response = self.app.get('/trips/'+tripposted_object_id, headers=self.headers)
        response_json = json.loads(response.data.decode())

        self.assertEqual(response.status_code, 200)
        assert 'A trip' in response_json["name"]

    # ======== FIXED =========
    # [Ben-G] This test is indented incorrectly, so it won't run
    def test_getting_non_existent_trip(self):
        response = self.app.get('/trips/123456789012345678901234', headers=self.headers)
        self.assertEqual(response.status_code, 404)

    def test_getting_user_trips(self):
        # post trips
        trip_response = self.app.post('/trips/',
            data=json.dumps(dict(
                name="A trip"
            )),
            content_type='application/json',
            headers=self.headers)

        trip_response = self.app.post('/trips/',
            data=json.dumps(dict(
                name="A second trip"
            )),
            content_type='application/json',
            headers=self.headers)

        response = self.app.get('/trips/', headers=self.headers)
        response_json = json.loads(response.data.decode())

        self.assertEqual(response.status_code, 200)

        assert "A trip" in response_json[0]["name"]
        assert "beingadrian" in response_json[0]["owner"]


    def test_putting_trip(self):
        # post trip
        response = self.app.post('/trips/',
            data=json.dumps(dict(
                name="Some trip"
            )),
            content_type='application/json',
            headers=self.headers)

        post_response_json = json.loads(response.data.decode())
        posted_object_id = post_response_json["_id"]

        # put trip (update trip)
        response = self.app.put('/trips/'+posted_object_id,
            data=json.dumps(dict(
                name="Some trip",
                waypoint=[{"Disneyland": (10, 21)}]
            )),
            content_type='application/json',
            headers=self.headers)

        response_json = json.loads(response.data.decode())

        self.assertEqual(response.status_code, 200)
        assert 'application/json' in response.content_type
        assert 'Some trip' in response_json["name"]

    def test_deleting_trip(self):
        # post trip initially
        response = self.app.post('/trips/',
            data=json.dumps(dict(
                name="Delete trip"
            )),
            content_type='application/json',
            headers=self.headers)

        post_response_json = json.loads(response.data.decode())
        posted_object_id = post_response_json["_id"]

        response = self.app.delete('/trips/'+posted_object_id, headers=self.headers)

        self.assertEqual(response.status_code, 200)
        assert 'application/json' in response.content_type

    # ===================
    #   USER TESTS
    # ===================

    def test_posting_extra_user(self):
        # create extra user with same username
        response = self.app.post('/users/',
            data=json.dumps(dict(
                username="beingadrian",
                password="abc12d"
            )),
            content_type='application/json')

        response_json = json.loads(response.data.decode())

        # assert that username already exists
        self.assertEqual(response.status_code, 409)
        assert 'application/json' in response.content_type

    def test_posting_user_without_password(self):
        # create new user
        response = self.app.post('/users/',
            data=json.dumps(dict(
                username="beingbob"
                # no password
            )),
            content_type='application/json')

        response_json = json.loads(response.data.decode())

        # assert that password is missing using status_code 409
        self.assertEqual(response.status_code, 400)

    def test_getting_user(self):
        # get user
        response = self.app.get('/users/', headers=self.headers)
        response_json = json.loads(response.data.decode())

        self.assertEqual(response.status_code, 200)
        assert 'beingadrian' in response_json["username"]


if __name__ == '__main__':
        unittest.main()
