#!/usr/bin/env python
"""
Test script for validating the Gemini integration in the HAZOP software.
This script tests the backend API endpoints related to Gemini AI functionality.
"""

import unittest
import os
import sys
import uuid
import json
import requests
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# Add the parent directory to the path to import app modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load environment variables
load_dotenv()

API_URL = os.getenv('API_URL', 'http://localhost:8000')
TEST_USER_EMAIL = os.getenv('TEST_USER_EMAIL', 'test@example.com')
TEST_USER_PASSWORD = os.getenv('TEST_USER_PASSWORD', 'password123')
TEST_STUDY_ID = os.getenv('TEST_STUDY_ID', '')
TEST_NODE_ID = os.getenv('TEST_NODE_ID', '')
TEST_DEVIATION_ID = os.getenv('TEST_DEVIATION_ID', '')

class GeminiIntegrationTest(unittest.TestCase):
    """Test cases for the Gemini AI integration."""

    @classmethod
    def setUpClass(cls):
        """Set up authentication and test data once for all tests."""
        print("\nSetting up test class...")

        try:
            print("Attempting authentication...")
            cls.token = cls.get_auth_token()
            cls.headers = {
                'Authorization': f'Bearer {cls.token}',
                'Content-Type': 'application/json'
            }
            print("✅ Authentication successful")

            # Create test data if needed
            if not TEST_STUDY_ID or not TEST_NODE_ID or not TEST_DEVIATION_ID:
                print("Creating test data...")
                cls.create_test_data()
                print("✅ Test data created successfully")
            else:
                print("Using existing test data")
                cls.study_id = TEST_STUDY_ID
                cls.node_id = TEST_NODE_ID
                cls.deviation_id = TEST_DEVIATION_ID
        except Exception as e:
            print(f"❌ Setup failed: {e}")
            raise

    @classmethod
    def get_auth_token(cls) -> str:
        """Authenticate and get a valid token."""
        auth_response = requests.post(
            f'{API_URL}/api/auth/login',
            json={
                'email': TEST_USER_EMAIL,
                'password': TEST_USER_PASSWORD
            }
        )
        auth_response.raise_for_status()
        return auth_response.json()['access_token']

    @classmethod
    def create_test_data(cls):
        """Create test data for the tests."""
        # Create a study if needed
        if not TEST_STUDY_ID:
            study_response = requests.post(
                f'{API_URL}/api/studies',
                json={
                    'title': f'Test Study for Gemini Integration {uuid.uuid4()}',
                    'description': 'Automated test study for Gemini integration testing',
                    'facility_name': 'Test Facility'
                },
                headers=cls.headers
            )
            study_response.raise_for_status()
            cls.study_id = study_response.json()['id']
        else:
            cls.study_id = TEST_STUDY_ID

        # Create a node if needed
        if not TEST_NODE_ID:
            node_response = requests.post(
                f'{API_URL}/api/studies/{cls.study_id}/nodes',
                json={
                    'node_number': f'N-{uuid.uuid4().hex[:5]}',
                    'node_name': 'Test Pressure Vessel',
                    'description': 'Vessel containing high-pressure fluid for testing Gemini AI',
                    'design_intent': 'Store high-pressure fluid for testing purposes'
                },
                headers=cls.headers
            )
            node_response.raise_for_status()
            cls.node_id = node_response.json()['id']
        else:
            cls.node_id = TEST_NODE_ID

        # Create a deviation if needed
        if not TEST_DEVIATION_ID:
            deviation_response = requests.post(
                f'{API_URL}/api/studies/nodes/{cls.node_id}/deviations',
                json={
                    'parameter': 'Pressure',
                    'guide_word': 'HIGH',
                    'deviation_description': 'High pressure in test vessel',
                },
                headers=cls.headers
            )
            deviation_response.raise_for_status()
            cls.deviation_id = deviation_response.json()['id']
        else:
            cls.deviation_id = TEST_DEVIATION_ID

    def test_suggest_causes(self):
        """Test the suggest-causes endpoint."""
        response = requests.post(
            f'{API_URL}/api/gemini/suggest-causes',
            json={
                'deviation_id': self.deviation_id if hasattr(self, 'deviation_id') else TEST_DEVIATION_ID,
                'context': {
                    'process_description': 'Pressure vessel containing water',
                    'operating_conditions': '10 bar, 25°C'
                }
            },
            headers=self.headers
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)

        if data:  # If AI returned suggestions
            self.assertTrue(all('text' in item for item in data))
            self.assertTrue(all('confidence' in item for item in data))

    def test_suggest_consequences(self):
        """Test the suggest-consequences endpoint."""
        response = requests.post(
            f'{API_URL}/api/gemini/suggest-consequences',
            json={
                'deviation_id': self.deviation_id if hasattr(self, 'deviation_id') else TEST_DEVIATION_ID,
                'context': {
                    'process_description': 'Pressure vessel containing water',
                    'operating_conditions': '10 bar, 25°C'
                }
            },
            headers=self.headers
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)

        if data:  # If AI returned suggestions
            self.assertTrue(all('text' in item for item in data))
            self.assertTrue(all('confidence' in item for item in data))

    def test_suggest_safeguards(self):
        """Test the suggest-safeguards endpoint."""
        response = requests.post(
            f'{API_URL}/api/gemini/suggest-safeguards',
            json={
                'deviation_id': self.deviation_id if hasattr(self, 'deviation_id') else TEST_DEVIATION_ID,
                'context': {
                    'process_description': 'Pressure vessel containing water',
                    'operating_conditions': '10 bar, 25°C'
                }
            },
            headers=self.headers
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)

        if data:  # If AI returned suggestions
            self.assertTrue(all('text' in item for item in data))
            self.assertTrue(all('confidence' in item for item in data))

    def test_complete_analysis(self):
        """Test the complete-analysis endpoint."""
        response = requests.post(
            f'{API_URL}/api/gemini/complete-analysis',
            json={
                'deviation_id': self.deviation_id if hasattr(self, 'deviation_id') else TEST_DEVIATION_ID,
                'context': {
                    'process_description': 'Pressure vessel containing water',
                    'operating_conditions': '10 bar, 25°C'
                }
            },
            headers=self.headers
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('causes', data)
        self.assertIn('consequences', data)
        self.assertIn('safeguards', data)

    def test_suggest_risk_assessment(self):
        """Test the suggest-risk-assessment endpoint."""
        # First create a consequence to test with
        consequence_response = requests.post(
            f'{API_URL}/api/hazop/consequences',
            json={
                'deviation_id': self.deviation_id if hasattr(self, 'deviation_id') else TEST_DEVIATION_ID,
                'consequence_description': 'Vessel rupture leading to release of contents',
                'severity': 'catastrophic'
            },
            headers=self.headers
        )

        self.assertEqual(consequence_response.status_code, 200)
        consequence_id = consequence_response.json()['id']

        # Now test the risk assessment endpoint
        response = requests.post(
            f'{API_URL}/api/gemini/suggest-risk-assessment',
            json={
                'consequence_id': consequence_id
            },
            headers=self.headers
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('current_likelihood', data)
        self.assertIn('suggested_likelihood', data)
        self.assertIn('current_severity', data)
        self.assertIn('suggested_severity', data)
        self.assertIn('reasoning', data)

    def test_evaluate_safeguard_effectiveness(self):
        """Test the evaluate-safeguard-effectiveness endpoint."""
        # First create a safeguard to test with
        safeguard_response = requests.post(
            f'{API_URL}/api/hazop/safeguards',
            json={
                'deviation_id': self.deviation_id if hasattr(self, 'deviation_id') else TEST_DEVIATION_ID,
                'safeguard_description': 'Pressure relief valve set at 12 bar',
                'safeguard_type': 'prevention',
                'effectiveness': 'medium'
            },
            headers=self.headers
        )

        self.assertEqual(safeguard_response.status_code, 200)
        safeguard_id = safeguard_response.json()['id']

        # Now test the safeguard effectiveness endpoint
        response = requests.post(
            f'{API_URL}/api/gemini/evaluate-safeguard-effectiveness',
            json={
                'safeguard_id': safeguard_id
            },
            headers=self.headers
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('effectiveness_score', data)
        self.assertIn('confidence_score', data)
        self.assertIn('reasoning', data)

    def test_contextual_knowledge(self):
        """Test the contextual-knowledge endpoint."""
        response = requests.post(
            f'{API_URL}/api/gemini/contextual-knowledge',
            json={
                'node_id': self.node_id if hasattr(self, 'node_id') else TEST_NODE_ID,
                'deviation_id': self.deviation_id if hasattr(self, 'deviation_id') else TEST_DEVIATION_ID
            },
            headers=self.headers
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('regulations', data)
        self.assertIn('incident_reports', data)
        self.assertIn('technical_references', data)
        self.assertIn('industry_benchmarks', data)

    def test_workshop_preparation(self):
        """Test the workshop-preparation endpoint."""
        response = requests.post(
            f'{API_URL}/api/gemini/workshop-preparation',
            json={
                'study_id': self.study_id if hasattr(self, 'study_id') else TEST_STUDY_ID
            },
            headers=self.headers
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('high_risk_areas', data)
        self.assertIn('suggested_questions', data)
        self.assertIn('similar_nodes', data)
        self.assertIn('reference_materials', data)

if __name__ == '__main__':
    print("\n=== Gemini Integration Test ===")
    print("Environment variables:")
    print(f"  API_URL: {os.getenv('API_URL', 'Not set')}")
    print(f"  GEMINI_API_KEY: {'Set (hidden)' if os.getenv('GEMINI_API_KEY') else 'Not set'}")
    print(f"  TEST_USER_EMAIL: {os.getenv('TEST_USER_EMAIL', 'Not set')}")

    # Check if required modules are present
    print("\nChecking required modules:")
    modules = ['requests', 'dotenv', 'uuid', 'json']
    missing_modules = []

    for module in modules:
        try:
            __import__(module)
            print(f"  ✅ {module}: Available")
        except ImportError:
            print(f"  ❌ {module}: Missing")
            missing_modules.append(module)

    if missing_modules:
        print(f"\nMissing modules: {', '.join(missing_modules)}")
        print("Please install them with:")
        print(f"pip install {' '.join(missing_modules)}")
        sys.exit(1)

    print("\nRunning tests...")
    unittest.main(verbosity=2)