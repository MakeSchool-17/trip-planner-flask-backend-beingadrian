import server
import unittest
import json
from pymongo import MongoClient


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
        db.drop_collection('myobject')

    # MyObject tests

    def test_posting_myobject(self):
        response = self.app.post('/myobject/',
        data=json.dumps(dict(
            name="A object"
        )),
        content_type='application/json')

        responseJSON = json.loads(response.data.decode())

        self.assertEqual(response.status_code, 200)
        assert 'application/json' in response.content_type
        assert 'A object' in responseJSON["name"]

    def test_getting_myobject(self):
        response = self.app.post('/myobject/',
        data=json.dumps(dict(
            name="Another object"
        )),
        content_type='application/json')

        postResponseJSON = json.loads(response.data.decode())
        postedObjectID = postResponseJSON["_id"]

        response = self.app.get('/myobject/'+postedObjectID)
        responseJSON = json.loads(response.data.decode())

        self.assertEqual(response.status_code, 200)
        assert 'Another object' in responseJSON["name"]

        def test_getting_non_existent_trip(self):
            response = self.app.get('/myobject/55f0cbb4236f44b7f0e3cb23')
            self.assertEqual(response.status_code, 404)

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
        response = self.app.post('/trips/',
        data=json.dumps(dict(
            name="Another trip"
        )),
        content_type='application/json')

        post_response_json = json.loads(response.data.decode())
        posted_object_id = post_response_json["_id"]

        response = self.app.get('/trips/'+posted_object_id)
        response_json = json.loads(response.data.decode())

        self.assertEqual(response.status_code, 200)
        assert 'Another trip' in response_json["name"]

        def test_getting_non_existent_trip(self):
            response = self.app.get('/trips/asdf1415512')
            self.assertEqual(response.status_code, 404)

    def test_putting_trip(self):
        response = self.app.post('/trips/')

if __name__ == '__main__':
        unittest.main()
