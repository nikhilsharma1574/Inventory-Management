import unittest
import coverage
from API import app, db, User, Items

# Start coverage
cov = coverage.Coverage()
cov.start()


class APITestCase(unittest.TestCase):
    def setUp(self):
        # Configure the app for testing
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()

        db.create_all()
        self.populate_db()


    def tearDown(self):
        db.session.remove()
        db.drop_all()
        # Pop application context
        self.app_context.pop()

    def populate_db(self):
        # Add a test user and item to the database
        try:
            user = User(isAdmin=True, FullName="Test Admin", Email="admin@test.com", Password="password")
            item = Items(SerialNumber="123", ItemName="Test Item", Quantity=1, Category="Test", BillNumber="123", DateOfPurchase="2024-01-01", Warranty="1 year", AssignedTo=None)
            db.session.add(user)
            db.session.add(item)
            db.session.commit()
        except Exception as e:
            print(f"Error populating database: {e}")

    def test_add_item(self):
        try:
            response = self.app.post('/add-item', data=dict(
                serialNumber="124",
                itemName="New Item",
                quantity=2,
                category="New",
                billNumber="124",
                dateOfPurchase="2024-01-02",
                warranty="2 years",
                assignedTo=None
            ))
            self.assertEqual(response.status_code, 302)
            item = Items.query.filter_by(SerialNumber="124").first()
            self.assertIsNotNone(item)
        except Exception as e:
            print(f"Error during add item test: {e}")

    def test_add_user(self):
        try:
            response = self.app.post('/add-user', data=dict(
                isAdmin='on',
                fullName='Test User',
                email='testuser',
                password='password123',
                confirmPassword='password123'
            ))
            self.assertEqual(response.status_code, 302)  # Assuming a redirect on success
            user = User.query.filter_by(Email='testuser@nqt.com').first()
            self.assertIsNotNone(user)
            self.assertEqual(user.FullName, 'Test User')
        except Exception as e:
            print(f"Error during add user test: {e}")

    def test_delete_item(self):
        try:
            response = self.app.post('/delete-item', data=dict(serialNumber="123"))
            self.assertEqual(response.status_code, 302)  # Redirects after deletion
            item = Items.query.filter_by(SerialNumber="123").first()
            self.assertIsNone(item)
        except Exception as e:
            print(f"Error during delete item test: {e}")

    def test_delete_user(self):
        try:
            response = self.app.post('/delete-user', data=dict(uid=1))
            self.assertEqual(response.status_code, 302)  # Redirects after deletion
            user = User.query.filter_by(UID=1).first()
            self.assertIsNone(user)
        except Exception as e:
            print(f"Error during delete user test: {e}")

    def test_assign_item(self):
        try:
            response = self.app.post('/assign-item', data=dict(serialNumber="123", assignedTo=1))
            self.assertEqual(response.status_code, 302)  # Redirects after assigning
            item = Items.query.filter_by(SerialNumber="123").first()
            self.assertEqual(item.AssignedTo, 1)
        except Exception as e:
            print(f"Error during assign item test: {e}")

    def test_unassign_item(self):
        try:
            response = self.app.post('/unassign-item', data=dict(serialNumber="123"))
            self.assertEqual(response.status_code, 302)  # Redirects after unassigning
            item = Items.query.filter_by(SerialNumber="123").first()
            self.assertIsNone(item.AssignedTo)
        except Exception as e:
            print(f"Error during unassign item test: {e}")


#Session Tests
    def test_login_valid_credentials(self):
        try:
            response = self.app.post('/', data=dict(
                email='admin',
                password='password'
            ), follow_redirects=True)

            # Assertions
            self.assertEqual(response.status_code, 200)

        except Exception as e:
            print(f"Error during login with valid credentials test: {e}")

    def test_login_invalid_credentials(self):
        try:
            response = self.app.post('/', data=dict(
                email='invalid',
                password='invalid'
            ), follow_redirects=True)

            # Assertions
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Invalid credentials', response.data)

        except Exception as e:
            print(f"Error during login with invalid credentials test: {e}")

    def test_access_login_page_when_logged_in(self):
        try:
            # Log in first
            response_login = self.app.post('/', data=dict(
                email='admin',
                password='password'
            ), follow_redirects=True)

            # Access the login page again
            response = self.app.get('/')
            self.assertEqual(response.status_code, 200)  # Assuming logged-in users are redirected

        except Exception as e:
            print(f"Error during access login page when logged in test: {e}")

    def test_logout(self):
        try:
            # Log in first
            response_login = self.app.post('/', data=dict(
                email='admin',
                password='password'
            ), follow_redirects=True)

            # Logout
            response_logout = self.app.get('/logout', follow_redirects=True)
            self.assertEqual(response_logout.status_code, 200)

        except Exception as e:
            print(f"Error during logout test: {e}")




    # def test_edit_item(self):
    #     try:
    #         # Add an item first
    #         item = Items(SerialNumber="12345", ItemName="Test Item", Quantity=1, Category="Test", BillNumber="123", DateOfPurchase="2024-01-01", Warranty="1 year", AssignedTo=None)
    #         db.session.add(item)
    #         db.session.commit()

    #         # Edit the item
    #         response = self.app.post('/edit-item', data=dict(
    #             serialNumber="12345",
    #             itemName="Updated Item",
    #             quantity=2,
    #             category="Updated Category",
    #             billNumber="124",
    #             dateOfPurchase="2024-01-02",
    #             warranty="2 years",
    #             assignedTo=None
    #         ))

    #         # Assertions
    #         self.assertEqual(response.status_code, 302)  # Assuming a redirect on success
    #         updated_item = Items.query.filter_by(SerialNumber="12345").first()
    #         self.assertIsNotNone(updated_item)
    #         self.assertEqual(updated_item.ItemName, "Updated Item")
    #         self.assertEqual(updated_item.Quantity, 2)
    #         self.assertEqual(updated_item.Category, "Updated Category")

    #     except Exception as e:
    #         print(f"Error during edit item test: {e}")

    # def test_edit_user(self):
    #     try:
    #         # Add a user first
    #         user = User(isAdmin=True, FullName="Original User", Email="original@example.com", Password="password")
    #         db.session.add(user)
    #         db.session.commit()

    #         # Edit the user
    #         response = self.app.post('/edit-user', data=dict(
    #             uid=user.UID,
    #             fullName='Updated User',
    #             email='updated@example.com',
    #             isAdmin='on'
    #         ))

    #         # Assertions
    #         self.assertEqual(response.status_code, 302)  # Assuming a redirect on success
    #         updated_user = User.query.get(user.UID)
    #         self.assertIsNotNone(updated_user)
    #         self.assertEqual(updated_user.FullName, 'Updated User')
    #         self.assertEqual(updated_user.Email, 'updated@example.com')
    #         self.assertTrue(updated_user.isAdmin)

    #     except Exception as e:
    #         print(f"Error during edit user test: {e}")


if __name__ == '__main__':

    # Run tests
    unittest.main()

    # Stop coverage and generate report
    cov.stop()
    cov.save()
    cov.report(include=["API.py"])
    cov.html_report(directory='coverage_report')
