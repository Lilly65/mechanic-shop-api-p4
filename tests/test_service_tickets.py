import unittest
from mechanic_shop import create_app, db


class TestServiceTickets(unittest.TestCase):

    def setUp(self):
        # Create the app using the testing config, which points at an
        # in-memory SQLite database so the real database is never touched.
        self.app = create_app('config.TestingConfig')
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

        # Create a customer and mechanic to use across service ticket tests.
        self.client.post('/customers/', json={
            "name":     "Jane Doe",
            "email":    "jane@example.com",
            "phone":    "555-1234",
            "password": "securepassword123"
        })
        self.client.post('/mechanics/', json={
            "name":   "John Smith",
            "email":  "john@mechanicshop.com",
            "phone":  "555-6789",
            "salary": 55000.00
        })

    def tearDown(self):
        # Drop all tables after each test to ensure a clean state for the next one.
        with self.app.app_context():
            db.drop_all()

    def test_create_service_ticket(self):
        # Positive test: creating a ticket with valid data should return 201.
        response = self.client.post('/service-tickets/', json={
            "VIN":          "1HGBH41JXMN109186",
            "service_date": "2026-05-22",
            "service_desc": "Oil change",
            "customer_id":  1
        })
        self.assertEqual(response.status_code, 201)

    def test_create_service_ticket_missing_field(self):
        # Negative test: missing the VIN field should return 400.
        response = self.client.post('/service-tickets/', json={
            "service_date": "2026-05-22",
            "service_desc": "Oil change",
            "customer_id":  1
        })
        self.assertEqual(response.status_code, 400)

    def test_get_service_tickets(self):
        # Positive test: retrieving all tickets should return 200.
        response = self.client.get('/service-tickets/')
        self.assertEqual(response.status_code, 200)

    def test_assign_mechanic(self):
        # Positive test: assigning a mechanic to a ticket should return 200.
        self.client.post('/service-tickets/', json={
            "VIN":          "1HGBH41JXMN109186",
            "service_date": "2026-05-22",
            "service_desc": "Oil change",
            "customer_id":  1
        })
        response = self.client.put('/service-tickets/1/assign-mechanic/1')
        self.assertEqual(response.status_code, 200)

    def test_assign_mechanic_duplicate(self):
        # Negative test: assigning the same mechanic twice should return 400.
        self.client.post('/service-tickets/', json={
            "VIN":          "1HGBH41JXMN109186",
            "service_date": "2026-05-22",
            "service_desc": "Oil change",
            "customer_id":  1
        })
        self.client.put('/service-tickets/1/assign-mechanic/1')
        response = self.client.put('/service-tickets/1/assign-mechanic/1')
        self.assertEqual(response.status_code, 400)

    def test_remove_mechanic(self):
        # Positive test: removing an assigned mechanic should return 200.
        self.client.post('/service-tickets/', json={
            "VIN":          "1HGBH41JXMN109186",
            "service_date": "2026-05-22",
            "service_desc": "Oil change",
            "customer_id":  1
        })
        self.client.put('/service-tickets/1/assign-mechanic/1')
        response = self.client.put('/service-tickets/1/remove-mechanic/1')
        self.assertEqual(response.status_code, 200)

    def test_remove_mechanic_not_assigned(self):
        # Negative test: removing a mechanic not assigned to the ticket should return 400.
        self.client.post('/service-tickets/', json={
            "VIN":          "1HGBH41JXMN109186",
            "service_date": "2026-05-22",
            "service_desc": "Oil change",
            "customer_id":  1
        })
        response = self.client.put('/service-tickets/1/remove-mechanic/1')
        self.assertEqual(response.status_code, 400)

    def test_edit_service_ticket(self):
        # Positive test: bulk editing mechanics on a ticket should return 200.
        self.client.post('/service-tickets/', json={
            "VIN":          "1HGBH41JXMN109186",
            "service_date": "2026-05-22",
            "service_desc": "Oil change",
            "customer_id":  1
        })
        response = self.client.put('/service-tickets/1/edit', json={
            "add_ids":    [1],
            "remove_ids": []
        })
        self.assertEqual(response.status_code, 200)

    def test_edit_service_ticket_not_found(self):
        # Negative test: editing a ticket that does not exist should return 404.
        response = self.client.put('/service-tickets/999/edit', json={
            "add_ids":    [1],
            "remove_ids": []
        })
        self.assertEqual(response.status_code, 404)

    def test_add_part_to_ticket(self):
        # Positive test: adding a part to a ticket should return 200.
        self.client.post('/service-tickets/', json={
            "VIN":          "1HGBH41JXMN109186",
            "service_date": "2026-05-22",
            "service_desc": "Oil change",
            "customer_id":  1
        })
        self.client.post('/inventory/', json={
            "name":  "Oil Filter",
            "price": 12.99
        })
        response = self.client.put('/service-tickets/1/add-part/1')
        self.assertEqual(response.status_code, 200)

    def test_add_part_to_ticket_duplicate(self):
        # Negative test: adding the same part to a ticket twice should return 400.
        self.client.post('/service-tickets/', json={
            "VIN":          "1HGBH41JXMN109186",
            "service_date": "2026-05-22",
            "service_desc": "Oil change",
            "customer_id":  1
        })
        self.client.post('/inventory/', json={
            "name":  "Oil Filter",
            "price": 12.99
        })
        self.client.put('/service-tickets/1/add-part/1')
        response = self.client.put('/service-tickets/1/add-part/1')
        self.assertEqual(response.status_code, 400)


if __name__ == '__main__':
    unittest.main()