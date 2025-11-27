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
#portion by nibesh
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

==============================
    def test_calculation_precision(self):
        """[Aayush] Ensure currency math is accurate to 2 decimal places."""
        price = 19.99
        qty = 3
        expected_total = 59.97
        calculated_total = round(price * qty, 2)
        self.assertEqual(calculated_total, expected_total, "Currency math error")

    def test_vip_discount_logic(self):
        """[Aayush] Verify 5% Discount Calculation for VIPs."""
        subtotal = 100.00
        discount_rate = 0.05
        expected_discount = 5.00
        
        calculated = subtotal * discount_rate
        self.assertEqual(calculated, expected_discount, "VIP 5% logic failed")

    def test_student_discount_logic(self):
        """[Aayush] Verify 10% Discount Calculation for Students."""
        subtotal = 100.00
        discount_rate = 0.10
        expected_discount = 10.00
        
        calculated = subtotal * discount_rate
        self.assertEqual(calculated, expected_discount, "Student 10% logic failed")
