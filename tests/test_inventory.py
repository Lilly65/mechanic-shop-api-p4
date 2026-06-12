import unittest
from mechanic_shop import create_app, db


class TestInventory(unittest.TestCase):

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

    def test_create_part(self):
        # Positive test: creating a part with valid data should return 201.
        response = self.client.post('/inventory/', json={
            "name":  "Oil Filter",
            "price": 12.99
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn('Oil Filter', response.get_data(as_text=True))

    def test_create_part_missing_field(self):
        # Negative test: missing the price field should return 400.
        response = self.client.post('/inventory/', json={
            "name": "Oil Filter"
        })
        self.assertEqual(response.status_code, 400)

    def test_get_parts(self):
        # Positive test: retrieving all parts should return 200.
        response = self.client.get('/inventory/')
        self.assertEqual(response.status_code, 200)

    def test_update_part(self):
        # Positive test: updating an existing part should return 200.
        self.client.post('/inventory/', json={
            "name":  "Oil Filter",
            "price": 12.99
        })
        response = self.client.put('/inventory/1', json={
            "name":  "Air Filter",
            "price": 18.99
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('Air Filter', response.get_data(as_text=True))

    def test_update_part_not_found(self):
        # Negative test: updating a part that does not exist should return 404.
        response = self.client.put('/inventory/999', json={
            "name":  "Ghost Part",
            "price": 0.00
        })
        self.assertEqual(response.status_code, 404)

    def test_delete_part(self):
        # Positive test: deleting an existing part should return 200.
        self.client.post('/inventory/', json={
            "name":  "Oil Filter",
            "price": 12.99
        })
        response = self.client.delete('/inventory/1')
        self.assertEqual(response.status_code, 200)

    def test_delete_part_not_found(self):
        # Negative test: deleting a part that does not exist should return 404.
        response = self.client.delete('/inventory/999')
        self.assertEqual(response.status_code, 404)


if __name__ == '__main__':
    unittest.main()