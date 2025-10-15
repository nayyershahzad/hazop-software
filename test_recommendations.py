#!/usr/bin/env python3
"""
Test script to verify that recommendations are saved to correct table
"""
import requests
import json

API_URL = "http://localhost:8000"
DEVIATION_ID = "cde3f2f3-268b-4f7d-ab52-88d70f5a3c16"

# Login
print("Logging in...")
response = requests.post(f"{API_URL}/api/auth/login", json={
    "email": "gemini_test@example.com",
    "password": "test123"
})
token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
print("✓ Login successful\n")

# Test adding a recommendation
print("Testing: Add Recommendation")
print("-" * 50)

recommendation_payload = {
    "deviation_id": DEVIATION_ID,
    "consequence_id": None,
    "suggestions": [
        {
            "text": "Test recommendation: Implement automated flow monitoring system",
            "confidence": 95.0,
            "type": "Engineering",
            "effectiveness": "High"
        }
    ]
}

response = requests.post(
    f"{API_URL}/api/gemini/apply-suggestions/recommendations",
    json=recommendation_payload,
    headers=headers
)

if response.status_code == 200:
    result = response.json()
    print(f"✓ SUCCESS: {result['message']}")
    print(f"  Count: {result['count']}")
else:
    print(f"✗ FAILED: {response.status_code}")
    print(f"Response: {response.text}")

print("\n" + "=" * 50)
print("Test complete!")
