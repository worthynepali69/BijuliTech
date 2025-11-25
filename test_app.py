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
