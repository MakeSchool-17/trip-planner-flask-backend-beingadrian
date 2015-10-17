import server
import unittest
import json
from pymongo import MongoClient
import bcrypt


class FlaskrTestCase(unittest.TestCase):

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

    # Trip tests

    def test_posting_trip(self):
        response = self.app.post('/trips/',
            data=json.dumps(dict(
                name="A trip"
            )),
        content_type='application/json')

        responseJSON = json.loads(response.data.decode())

        self.assertEqual(response.status_code, 200)
        assert 'application/json' in response.content_type
        assert 'A trip' in responseJSON["name"]

    def test_getting_trip(self):
        # create trip response with user_object_id
        trip_response = self.app.post('/trips/',
            data=json.dumps(dict(
                name="A trip"
            )),
        content_type='application/json')

        tripPostResponseJSON = json.loads(trip_response.data.decode())
        tripPostedObjectID = tripPostResponseJSON["_id"]

        response = self.app.get('/trips/'+tripPostedObjectID)
        response_json = json.loads(response.data.decode())

        self.assertEqual(response.status_code, 200)
        assert 'A trip' in response_json["name"]

        def test_getting_non_existent_trip(self):
            response = self.app.get('/trips/anyeonghaseo')
            self.assertEqual(response.status_code, 404)

    def test_getting_user_trips(self):
        trip_response = self.app.post('/trips/',
            data=json.dumps(dict(
                name="A trip"
            )),
        content_type='application/json')

        trip_response = self.app.post('/trips/',
            data=json.dumps(dict(
                name="A second trip"
            )),
        content_type='application/json')

        response = self.app.get('/trips/')
        response_json = json.loads(response.data.decode())

        self.assertEqual(trip_response.status_code, 200)

        assert "A trip" in response_json[0]["name"]


    def test_putting_trip(self):
        response = self.app.post('/trips/',
            data=json.dumps(dict(
                name="Some trip"
            )),
            content_type='application/json')

        postResponseJSON = json.loads(response.data.decode())
        postedObjectID = postResponseJSON["_id"]

        response = self.app.put('/trips/'+postedObjectID,
            data=json.dumps(dict(
                name="Some trip",
                waypoint=[{"Disneyland": (10, 21)}]
            )),
            content_type='application/json')

        response_json = json.loads(response.data.decode())

        self.assertEqual(response.status_code, 200)
        assert 'application/json' in response.content_type
        assert 'Some trip' in response_json["name"]

    def test_deleting_trip(self):
        response = self.app.post('/trips/',
            data=json.dumps(dict(
                name="Delete trip"
            )),
            content_type='application/json')

        postResponseJSON = json.loads(response.data.decode())
        postedObjectID = postResponseJSON["_id"]

        response = self.app.delete('/trips/'+postedObjectID)

        self.assertEqual(response.status_code, 200)
        assert 'application/json' in response.content_type

    # User tests

    def test_posting_user(self):
        response = self.app.post('/users/',
            data=json.dumps(dict(
                username="beingadrian",
                password="abc123"
            )),
        content_type='application/json')

        response_json = json.loads(response.data.decode())

        self.assertEqual(response.status_code, 200)
        assert 'application/json' in response.content_type
        assert 'beingadrian' in response_json["username"]

        # test password
        pw_hash = response_json["password"].encode('utf-8')
        self.assertEqual(bcrypt.hashpw('abc123'.encode('utf-8'), pw_hash), pw_hash)

    def test_getting_user(self):
        response = self.app.post('/users/',
            data=json.dumps(dict(
                username="beingadrian",
                password="abc123"
            )),
        content_type='application/json')

        postResponseJSON = json.loads(response.data.decode())
        postedObjectID = postResponseJSON["_id"]

        response = self.app.get('/users/'+postedObjectID)
        response_json = json.loads(response.data.decode())

        self.assertEqual(response.status_code, 200)
        assert 'beingadrian' in response_json["username"]

        def test_getting_non_existent_trip(self):
            response = self.app.get('/users/asdf1415512')
            self.assertEqual(response.status_code, 404)


if __name__ == '__main__':
        unittest.main()
