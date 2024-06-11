import unittest
from flask_testing import TestCase
from API import app, db, User, Items
import coverage

# Start coverage measurement
cov = coverage.Coverage()
cov.start()

class APITestCase(TestCase):

    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    TESTING = True

    def create_app(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = self.SQLALCHEMY_DATABASE_URI
        app.config['TESTING'] = self.TESTING
        return app

    def setUp(self):
        db.create_all()
        user = User(isAdmin=True, FullName="Admin User", Email="admin@example.com", Password="password")
        db.session.add(user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_login_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data)

    def test_handle_users_get(self):
        response = self.client.get('/users')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Users', response.data)

    def test_handle_users_post(self):
        response = self.client.post('/users', data=dict(
            isAdmin='on',
            fullName='Test User',
            email='test@example.com',
            password='password'
        ))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test User', response.data)

    # def test_handle_items_get(self):
    #     response = self.client.get('/items')
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn(b'Items', response.data)

    # def test_handle_items_post(self):
    #     response = self.client.post('/items', data=dict(
    #         serialNumber=1,
    #         itemName='Test Item',
    #         quantity=10,
    #         category='Test Category',
    #         billNumber='123456',
    #         dateOfPurchase='2023-01-01',
    #         warranty='1 year',
    #         assignedTo=None
    #     ))
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn(b'Test Item', response.data)

    def test_edit_item_get(self):
        item = Items(ItemName='Test Item', Quantity=10, Category='Test Category', BillNumber='123456', 
                     DateOfPurchase='2023-01-01', Warranty='1 year', AssignedTo=None)
        db.session.add(item)
        db.session.commit()
        response = self.client.get(f'/edit-item')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Item', response.data)

    def test_edit_item_post(self):
        item = Items(ItemName='Test Item', Quantity=10, Category='Test Category', BillNumber='123456', 
                     DateOfPurchase='2023-01-01', Warranty='1 year', AssignedTo=None)
        db.session.add(item)
        db.session.commit()
        response = self.client.post(f'/edit-item', data=dict(
            itemName='Updated Item',
            quantity=20,
            category='Updated Category',
            billNumber='654321',
            dateOfPurchase='2024-01-01',
            warranty='2 years',
            assignedTo=None
        ))
        self.assertEqual(response.status_code, 302)  # Redirect status
        updated_item = Items.query.get(item.SerialNumber)
        self.assertEqual(updated_item.ItemName, 'Updated Item')

    def test_delete_item(self):
        item = Items(ItemName='Test Item', Quantity=10, Category='Test Category', BillNumber='123456', 
                     DateOfPurchase='2023-01-01', Warranty='1 year', AssignedTo=None)
        db.session.add(item)
        db.session.commit()
        response = self.client.post(f'/delete-item')
        self.assertEqual(response.status_code, 302)  # Redirect status
        deleted_item = Items.query.get(item.SerialNumber)
        self.assertIsNone(deleted_item)

        

if __name__ == '__main__':
    unittest.main()
    cov.stop()
    cov.save()
    cov.report()
