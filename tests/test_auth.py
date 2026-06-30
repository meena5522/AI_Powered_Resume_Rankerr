import os
import unittest
import tempfile
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config

# Point database to temporary configuration before importing models
db_fd, temp_db_path = tempfile.mkstemp()
Config.DATABASE = temp_db_path

from models import database as db

class TestAuthAndDatabase(unittest.TestCase):

    def setUp(self):
        db.init_db()

    def tearDown(self):
        # Close database connection and clean up temp db file
        try:
            os.close(db_fd)
            os.unlink(temp_db_path)
        except OSError:
            pass

    def test_create_user_and_authenticate(self):
        username = "recruiter1"
        email = "recruiter1@company.com"
        password = "securepassword123"
        hashed = generate_password_hash(password)
        
        # Test creation
        user_id = db.create_user(username, email, hashed)
        self.assertIsNotNone(user_id)
        
        # Test fetching details
        user = db.get_user_by_username(username)
        self.assertIsNotNone(user)
        self.assertEqual(user['email'], email)
        
        # Test credentials verification
        self.assertTrue(check_password_hash(user['password_hash'], password))
        self.assertFalse(check_password_hash(user['password_hash'], "wrongpassword"))

    def test_duplicate_user_integrity(self):
        username = "recruiter2"
        email = "recruiter2@company.com"
        hashed = generate_password_hash("password123")
        
        db.create_user(username, email, hashed)
        # Try creating identical username
        duplicate_id = db.create_user(username, "diff@email.com", hashed)
        self.assertIsNone(duplicate_id)

    def test_update_profile(self):
        username = "recruiter3"
        email = "recruiter3@company.com"
        hashed = generate_password_hash("password123")
        
        user_id = db.create_user(username, email, hashed)
        self.assertIsNotNone(user_id)
        
        # Update details
        db.update_user_profile(user_id, "new_username", "new_email@company.com")
        
        updated_user = db.get_user_by_id(user_id)
        self.assertEqual(updated_user['username'], "new_username")
        self.assertEqual(updated_user['email'], "new_email@company.com")

if __name__ == '__main__':
    unittest.main()
