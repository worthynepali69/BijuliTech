#gotta add some test cases mate (it has to be 5)
import unittest
from database import Database

# ==============================================================================
# BIJULI TECH POS - AUTOMATED TEST SUITE
# ==============================================================================

class TestBijuliSystem(unittest.TestCase):

    def setUp(self):
        """Run before every test: Setup DB connection"""
        self.db = Database()
    # instructions: Nibesh, copy/paste this section first.
    # ==========================================================================
    def test_database_connection(self):
        """[Nibesh] Verify that the application connects to MySQL successfully."""
        conn = self.db.get_connection()
        self.assertIsNotNone(conn, "Database connection failed")
        if conn:
            conn.close()

    def test_admin_authentication(self):
        """[Nibesh] Test that Admin login works and returns correct Role."""
        user = self.db.login("aayush", "aayush123")
        self.assertIsNotNone(user, "Admin login failed with correct credentials")
        self.assertEqual(user['role'], 'admin', "User role is not Admin")

    def test_staff_authentication(self):
        """[Nibesh] Test that Staff login works and prevents Admin access."""
        user = self.db.login("zimone", "zimone123")
        self.assertIsNotNone(user, "Staff login failed")
        self.assertEqual(user['role'], 'staff', "User role is not Staff")
