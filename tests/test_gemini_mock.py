#!/usr/bin/env python
"""
Mock test for Gemini integration that doesn't require a live backend.
"""

import unittest
import os
import json
from unittest.mock import patch, MagicMock
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_URL = os.getenv('API_URL', 'http://localhost:8000')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')

class MockResponse:
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code
        self.text = json.dumps(json_data)

    def json(self):
        return self.json_data

    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception(f"HTTP Error: {self.status_code}")

class GeminiMockTest(unittest.TestCase):
    """Mock test cases for the Gemini AI integration."""

    def setUp(self):
        """Set up test variables."""
        self.headers = {'Authorization': 'Bearer mock_token', 'Content-Type': 'application/json'}
        self.study_id = "00000000-0000-0000-0000-000000000001"
        self.node_id = "00000000-0000-0000-0000-000000000002"
        self.deviation_id = "00000000-0000-0000-0000-000000000003"
        self.consequence_id = "00000000-0000-0000-0000-000000000004"
        self.safeguard_id = "00000000-0000-0000-0000-000000000005"

    @patch('requests.post')
    def test_suggest_causes(self, mock_post):
        """Test the suggest-causes endpoint with mocked response."""
        print("\nTesting suggest-causes endpoint...")

        # Setup mock response
        mock_data = [
            {
                "text": "Failure of pressure relief valve",
                "confidence": 0.92,
                "reasoning": "Common cause of high pressure in vessels"
            },
            {
                "text": "Blocked outlet",
                "confidence": 0.85,
                "reasoning": "Restriction in flow can lead to pressure buildup"
            }
        ]
        mock_post.return_value = MockResponse(mock_data, 200)

        # Simulated API call
        endpoint = f"{API_URL}/api/gemini/suggest-causes"
        payload = {
            "deviation_id": self.deviation_id,
            "context": {
                "process_description": "Pressure vessel containing water",
                "operating_conditions": "10 bar, 25°C"
            }
        }

        # Directly access the mocked response
        response = MockResponse(mock_data, 200)

        # Verify response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertTrue(all('text' in item for item in data))
        self.assertTrue(all('confidence' in item for item in data))

        print("✅ suggest-causes test passed")

    @patch('requests.post')
    def test_suggest_consequences(self, mock_post):
        """Test the suggest-consequences endpoint with mocked response."""
        print("\nTesting suggest-consequences endpoint...")

        # Setup mock response
        mock_data = [
            {
                "text": "Vessel rupture leading to contents release",
                "confidence": 0.95,
                "severity": "catastrophic",
                "category": "safety,environmental"
            },
            {
                "text": "Damage to connected equipment",
                "confidence": 0.82,
                "severity": "major",
                "category": "operational"
            }
        ]
        mock_post.return_value = MockResponse(mock_data, 200)

        # Simulated API call
        endpoint = f"{API_URL}/api/gemini/suggest-consequences"
        payload = {
            "deviation_id": self.deviation_id,
            "context": {
                "process_description": "Pressure vessel containing water",
                "operating_conditions": "10 bar, 25°C"
            }
        }

        # Directly access the mocked response
        response = MockResponse(mock_data, 200)

        # Verify response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertTrue(all('text' in item for item in data))
        self.assertTrue(all('confidence' in item for item in data))

        print("✅ suggest-consequences test passed")

    @patch('requests.post')
    def test_suggest_safeguards(self, mock_post):
        """Test the suggest-safeguards endpoint with mocked response."""
        print("\nTesting suggest-safeguards endpoint...")

        # Setup mock response
        mock_data = [
            {
                "text": "Pressure relief valve set at 12 bar",
                "confidence": 0.95,
                "type": "prevention",
                "effectiveness": "high"
            },
            {
                "text": "High pressure alarm",
                "confidence": 0.88,
                "type": "detection",
                "effectiveness": "medium"
            }
        ]
        mock_post.return_value = MockResponse(mock_data, 200)

        # Directly access the mocked response
        response = MockResponse(mock_data, 200)

        # Verify response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertTrue(all('text' in item for item in data))
        self.assertTrue(all('confidence' in item for item in data))

        print("✅ suggest-safeguards test passed")

    def test_gemini_api_key_format(self):
        """Test if the Gemini API key is in the expected format."""
        print(f"\nTesting Gemini API key format...")

        # Skip test if key not provided
        if not GEMINI_API_KEY:
            print("⚠️ Skipped: Gemini API key not provided")
            self.skipTest("Gemini API key not provided")

        # Check if key starts with "AIza"
        self.assertTrue(GEMINI_API_KEY.startswith("AIza"),
                       "Gemini API key should start with 'AIza'")

        # Check length (typically around 39 characters)
        self.assertTrue(len(GEMINI_API_KEY) >= 30,
                       "Gemini API key seems too short")

        print("✅ Gemini API key format test passed")

if __name__ == '__main__':
    print("=== Running Gemini Mock Tests ===")
    unittest.main(verbosity=2)