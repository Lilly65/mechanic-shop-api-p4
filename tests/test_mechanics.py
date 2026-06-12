import unittest
from mechanic_shop import create_app, db


class TestMechanics(unittest.TestCase):

    def setUp(self):
        # Create the app using the testing config, which points at an
        # in-memory SQLite database so the real database is never touched.
        self.app = create_app('config.TestingConfig')
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        # Drop all tables after each test to ensure a clean state for the next one.
        with self.app.app_context():
            db.drop_all()

    def test_create_mechanic(self):
        # Positive test: creating a mechanic with valid data should return 201.
        response = self.client.post('/mechanics/', json={
            "name":   "John Smith",
            "email":  "john@mechanicshop.com",
            "phone":  "555-6789",
            "salary": 55000.00
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn('John Smith', response.get_data(as_text=True))

    def test_create_mechanic_missing_field(self):
        # Negative test: missing the salary field should return 400.
        response = self.client.post('/mechanics/', json={
            "name":  "John Smith",
            "email": "john@mechanicshop.com",
            "phone": "555-6789"
        })
        self.assertEqual(response.status_code, 400)

    def test_get_mechanics(self):
        # Positive test: retrieving all mechanics should return 200.
        response = self.client.get('/mechanics/')
        self.assertEqual(response.status_code, 200)

    def test_update_mechanic(self):
        # Positive test: updating an existing mechanic should return 200.
        self.client.post('/mechanics/', json={
            "name":   "John Smith",
            "email":  "john@mechanicshop.com",
            "phone":  "555-6789",
            "salary": 55000.00
        })
        response = self.client.put('/mechanics/1', json={
            "name":   "John Updated",
            "email":  "updated@mechanicshop.com",
            "phone":  "555-9999",
            "salary": 60000.00
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('John Updated', response.get_data(as_text=True))

    def test_update_mechanic_not_found(self):
        # Negative test: updating a mechanic that does not exist should return 404.
        response = self.client.put('/mechanics/999', json={
            "name":   "Ghost",
            "email":  "ghost@example.com",
            "phone":  "000-0000",
            "salary": 0.00
        })
        self.assertEqual(response.status_code, 404)

    def test_delete_mechanic(self):
        # Positive test: deleting an existing mechanic should return 200.
        self.client.post('/mechanics/', json={
            "name":   "John Smith",
            "email":  "john@mechanicshop.com",
            "phone":  "555-6789",
            "salary": 55000.00
        })
        response = self.client.delete('/mechanics/1')
        self.assertEqual(response.status_code, 200)

    def test_delete_mechanic_not_found(self):
        # Negative test: deleting a mechanic that does not exist should return 404.
        response = self.client.delete('/mechanics/999')
        self.assertEqual(response.status_code, 404)

    def test_most_tickets(self):
        # Positive test: the leaderboard route should return 200.
        response = self.client.get('/mechanics/most-tickets')
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()