import os
import unittest
import tempfile
from config import Config

# Force a temp database path for isolated route testing
db_fd, temp_db_path = tempfile.mkstemp()
Config.DATABASE = temp_db_path

from app import app
from models import database as db

class TestAppRoutes(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test_session_secret'
        self.client = app.test_client()
        db.init_db()
        
        # Insert a default user for route testing
        from werkzeug.security import generate_password_hash
        db.create_user("testuser", "testuser@company.com", generate_password_hash("password123"))

    def tearDown(self):
        try:
            os.close(db_fd)
            os.unlink(temp_db_path)
        except OSError:
            pass

    def test_anonymous_redirect_to_login(self):
        # Protected pages should redirect anonymous users to login
        routes = ['/dashboard', '/job-descriptions', '/resumes', '/rankings', '/reports', '/profile']
        for route in routes:
            response = self.client.get(route)
            self.assertEqual(response.status_code, 302)
            self.assertIn('/login', response.headers['Location'])

    def test_login_and_logout_flow(self):
        # Test login page loading
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'HR Portal', response.data)
        
        # Test authenticating
        login_response = self.client.post('/login', data={
            'username': 'testuser',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertEqual(login_response.status_code, 200)
        self.assertIn(b'HR Administration Panel', login_response.data)
        
        # Test logout
        logout_response = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(logout_response.status_code, 200)
        self.assertIn(b'HR Portal', logout_response.data)

    def test_register_page(self):
        response = self.client.get('/register')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Create Account', response.data)

if __name__ == '__main__':
    unittest.main()
