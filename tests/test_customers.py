import unittest
from mechanic_shop import create_app, db
from werkzeug.security import generate_password_hash


class TestCustomers(unittest.TestCase):

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

    def test_create_customer(self):
        # Positive test: creating a customer with valid data should return 201.
        response = self.client.post('/customers/', json={
            "name":     "Jane Doe",
            "email":    "jane@example.com",
            "phone":    "555-1234",
            "password": "securepassword123"
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn('Jane Doe', response.get_data(as_text=True))

    def test_create_customer_missing_field(self):
        # Negative test: missing the password field should return 400.
        response = self.client.post('/customers/', json={
            "name":  "Jane Doe",
            "email": "jane@example.com",
            "phone": "555-1234"
        })
        self.assertEqual(response.status_code, 400)

    def test_get_customers(self):
        # Positive test: retrieving all customers should return 200.
        response = self.client.get('/customers/')
        self.assertEqual(response.status_code, 200)

    def test_get_customer_by_id(self):
        # Positive test: creating then retrieving a customer by id should return 200.
        self.client.post('/customers/', json={
            "name":     "Jane Doe",
            "email":    "jane@example.com",
            "phone":    "555-1234",
            "password": "securepassword123"
        })
        response = self.client.get('/customers/1')
        self.assertEqual(response.status_code, 200)

    def test_get_customer_not_found(self):
        # Negative test: requesting a customer id that does not exist should return 404.
        response = self.client.get('/customers/999')
        self.assertEqual(response.status_code, 404)

    def test_login_success(self):
        # Positive test: logging in with correct credentials should return 200 and a token.
        self.client.post('/customers/', json={
            "name":     "Jane Doe",
            "email":    "jane@example.com",
            "phone":    "555-1234",
            "password": "securepassword123"
        })
        response = self.client.post('/customers/login', json={
            "email":    "jane@example.com",
            "password": "securepassword123"
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.get_json())

    def test_login_wrong_password(self):
        # Negative test: logging in with the wrong password should return 401.
        self.client.post('/customers/', json={
            "name":     "Jane Doe",
            "email":    "jane@example.com",
            "phone":    "555-1234",
            "password": "securepassword123"
        })
        response = self.client.post('/customers/login', json={
            "email":    "jane@example.com",
            "password": "wrongpassword"
        })
        self.assertEqual(response.status_code, 401)

    def test_get_my_tickets_no_token(self):
        # Negative test: accessing the protected my-tickets route without a token
        # should return 401.
        response = self.client.get('/customers/my-tickets')
        self.assertEqual(response.status_code, 401)

    def test_get_my_tickets_with_token(self):
        # Positive test: accessing my-tickets with a valid token should return 200.
        self.client.post('/customers/', json={
            "name":     "Jane Doe",
            "email":    "jane@example.com",
            "phone":    "555-1234",
            "password": "securepassword123"
        })
        login = self.client.post('/customers/login', json={
            "email":    "jane@example.com",
            "password": "securepassword123"
        })
        token = login.get_json()['token']
        response = self.client.get('/customers/my-tickets', headers={
            "Authorization": f"Bearer {token}"
        })
        self.assertEqual(response.status_code, 200)

    def test_update_customer_no_token(self):
        # Negative test: updating a customer without a token should return 401.
        response = self.client.put('/customers/1', json={
            "name":     "Updated Name",
            "email":    "updated@example.com",
            "phone":    "555-9999",
            "password": "newpassword123"
        })
        self.assertEqual(response.status_code, 401)

    def test_delete_customer_no_token(self):
        # Negative test: deleting a customer without a token should return 401.
        response = self.client.delete('/customers/1')
        self.assertEqual(response.status_code, 401)


if __name__ == '__main__':
    unittest.main()