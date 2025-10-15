#!/usr/bin/env python
"""
Simple test to check if testing infrastructure is working
"""

import unittest

class SimpleTest(unittest.TestCase):
    def test_simple(self):
        """Simple test to check if unittest is working."""
        print("Simple test running...")
        self.assertEqual(1, 1)
        print("Simple test passed!")

if __name__ == '__main__':
    unittest.main(verbosity=2)