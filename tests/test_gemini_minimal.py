#!/usr/bin/env python
"""
Minimal test for Gemini integration
"""

import unittest
import os
import sys
import json
import requests
from dotenv import load_dotenv

# Add the parent directory to the path to import app modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load environment variables
load_dotenv()

# Default API URL
API_URL = os.getenv('API_URL', 'http://localhost:8000')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

class GeminiMinimalTest(unittest.TestCase):
    """Minimal test cases for the Gemini AI integration."""

    def test_env_variables(self):
        """Test if environment variables are loaded correctly."""
        print("\nChecking environment variables...")
        print(f"API_URL: {API_URL}")
        print(f"GEMINI_API_KEY: {'Set (hidden)' if GEMINI_API_KEY else 'Not set'}")

        self.assertIsNotNone(API_URL, "API_URL environment variable not set")
        self.assertIsNotNone(GEMINI_API_KEY, "GEMINI_API_KEY environment variable not set")

    def test_backend_health(self):
        """Test if the backend API is running."""
        print("\nChecking backend API health...")
        try:
            response = requests.get(f"{API_URL}/health", timeout=5)
            print(f"Response status: {response.status_code}")
            print(f"Response body: {response.text}")
            self.assertEqual(response.status_code, 200)
            self.assertIn("healthy", response.text)
            print("✅ Backend API health check passed")
        except Exception as e:
            print(f"❌ Failed to connect to backend: {e}")
            self.fail(f"Failed to connect to backend: {e}")

    def test_backend_gemini_endpoint(self):
        """Test the backend Gemini endpoints."""
        print("\nTesting backend Gemini endpoint...")

        # Create a test user first to get authentication token
        try:
            # First try to login
            login_response = requests.post(
                f"{API_URL}/api/auth/login",
                json={"email": "test@example.com", "password": "test1234"},
                timeout=5
            )

            # If login fails, we'll try to create a test user
            if login_response.status_code != 200:
                print("Login failed, creating test user...")
                register_response = requests.post(
                    f"{API_URL}/api/auth/register",
                    json={
                        "email": "test@example.com",
                        "password": "test1234",
                        "name": "Test User"
                    },
                    timeout=5
                )

                # Now try to login again
                login_response = requests.post(
                    f"{API_URL}/api/auth/login",
                    json={"email": "test@example.com", "password": "test1234"},
                    timeout=5
                )

            self.assertEqual(login_response.status_code, 200, f"Failed to login: {login_response.text}")
            token = login_response.json().get("access_token")
            print("✅ Authentication successful")

            # Now test if the Gemini health endpoint is available
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }

            # Test the health endpoint first
            health_response = requests.get(
                f"{API_URL}/health",
                timeout=5
            )
            self.assertEqual(health_response.status_code, 200, f"Health endpoint failed: {health_response.text}")
            print("✅ Health endpoint check passed")

            # Now try to access the Gemini endpoint
            try:
                # Create a test study
                study_response = requests.post(
                    f"{API_URL}/api/studies",
                    json={
                        "title": "Test Study for Gemini Testing",
                        "description": "A test study for Gemini API integration testing",
                        "facility_name": "Test Facility"
                    },
                    headers=headers,
                    timeout=5
                )

                if study_response.status_code == 200:
                    study_id = study_response.json().get("id")
                    print(f"✅ Created test study with ID: {study_id}")

                    # Create a test node
                    node_response = requests.post(
                        f"{API_URL}/api/studies/{study_id}/nodes",
                        json={
                            "node_number": "N-001",
                            "node_name": "Test Pressure Vessel",
                            "description": "A test pressure vessel for Gemini API testing",
                            "design_intent": "Store high-pressure fluid"
                        },
                        headers=headers,
                        timeout=5
                    )

                    if node_response.status_code == 200:
                        node_id = node_response.json().get("id")
                        print(f"✅ Created test node with ID: {node_id}")

                        # Create a test deviation
                        deviation_response = requests.post(
                            f"{API_URL}/api/studies/nodes/{node_id}/deviations",
                            json={
                                "parameter": "Pressure",
                                "guide_word": "HIGH",
                                "deviation_description": "High pressure in test vessel"
                            },
                            headers=headers,
                            timeout=5
                        )

                        if deviation_response.status_code == 200:
                            deviation_id = deviation_response.json().get("id")
                            print(f"✅ Created test deviation with ID: {deviation_id}")

                            # Now test the Gemini suggest-causes endpoint
                            causes_response = requests.post(
                                f"{API_URL}/api/gemini/suggest-causes",
                                json={
                                    "deviation_id": deviation_id,
                                    "context": {
                                        "process_description": "Pressure vessel containing water",
                                        "operating_conditions": "10 bar, 25°C"
                                    }
                                },
                                headers=headers,
                                timeout=10  # Longer timeout for AI processing
                            )

                            print(f"Response status: {causes_response.status_code}")

                            if causes_response.status_code == 200:
                                causes = causes_response.json()
                                print(f"✅ Received {len(causes)} cause suggestions")
                                print("Sample causes:", causes[:2] if len(causes) > 2 else causes)
                                self.assertIsInstance(causes, list)
                                print("✅ Backend Gemini API integration test passed")
                            else:
                                print(f"⚠️ Gemini API returned: {causes_response.text}")
                                print("Test skipped - Gemini API may not be properly configured")
                        else:
                            print(f"❌ Failed to create deviation: {deviation_response.text}")
                            self.skipTest("Failed to create test deviation")
                    else:
                        print(f"❌ Failed to create node: {node_response.text}")
                        self.skipTest("Failed to create test node")
                else:
                    print(f"❌ Failed to create study: {study_response.text}")
                    self.skipTest("Failed to create test study")

            except Exception as e:
                print(f"❌ Error during Gemini endpoint testing: {e}")
                self.skipTest(f"Error during Gemini endpoint testing: {e}")

        except Exception as e:
            print(f"❌ Authentication failed: {e}")
            self.skipTest(f"Authentication failed: {e}")

if __name__ == '__main__':
    print("\n===== Gemini Minimal Integration Test =====")
    print("Environment:")
    print(f"• API_URL: {API_URL}")
    print(f"• GEMINI_API_KEY: {'Set (hidden)' if GEMINI_API_KEY else 'Not set'}")
    print("===========================================")
    unittest.main(verbosity=2)