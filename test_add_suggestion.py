#!/usr/bin/env python3
"""
Test script to verify that adding AI suggestions to HAZOP analysis works
"""
import requests
import json

API_URL = "http://localhost:8000"
DEVIATION_ID = "cde3f2f3-268b-4f7d-ab52-88d70f5a3c16"  # "No flow from pump P-101"

# Login
print("Logging in...")
response = requests.post(f"{API_URL}/api/auth/login", json={
    "email": "gemini_test@example.com",
    "password": "test123"
})
token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

print("✓ Login successful\n")

# Test adding a cause suggestion
print("Testing: Add Cause Suggestion")
print("-" * 50)

cause_payload = {
    "deviation_id": DEVIATION_ID,
    "suggestions": [
        {
            "text": "Test cause: Suction valve inadvertently closed",
            "confidence": 95.0,
            "reasoning": "Common operational error"
        }
    ]
}

response = requests.post(
    f"{API_URL}/api/gemini/apply-suggestions/causes",
    json=cause_payload,
    headers=headers
)

if response.status_code == 200:
    result = response.json()
    print(f"✓ SUCCESS: {result['message']}")
else:
    print(f"✗ FAILED: {response.status_code}")
    print(f"Response: {response.text}")

print()

# Test adding a consequence suggestion
print("Testing: Add Consequence Suggestion")
print("-" * 50)

consequence_payload = {
    "deviation_id": DEVIATION_ID,
    "cause_id": None,
    "suggestions": [
        {
            "text": "Test consequence: Production loss and potential shutdown",
            "confidence": 90.0,
            "severity": "High",
            "category": "Operational"
        }
    ]
}

response = requests.post(
    f"{API_URL}/api/gemini/apply-suggestions/consequences",
    json=consequence_payload,
    headers=headers
)

if response.status_code == 200:
    result = response.json()
    print(f"✓ SUCCESS: {result['message']}")
else:
    print(f"✗ FAILED: {response.status_code}")
    print(f"Response: {response.text}")

print()

# Test adding a safeguard suggestion
print("Testing: Add Safeguard Suggestion")
print("-" * 50)

safeguard_payload = {
    "deviation_id": DEVIATION_ID,
    "consequence_id": None,
    "suggestions": [
        {
            "text": "Test safeguard: Install low flow alarm with automatic trip",
            "confidence": 95.0,
            "type": "Detection",
            "effectiveness": "High"
        }
    ]
}

response = requests.post(
    f"{API_URL}/api/gemini/apply-suggestions/safeguards",
    json=safeguard_payload,
    headers=headers
)

if response.status_code == 200:
    result = response.json()
    print(f"✓ SUCCESS: {result['message']}")
else:
    print(f"✗ FAILED: {response.status_code}")
    print(f"Response: {response.text}")

print()
print("=" * 50)
print("All tests complete!")
print("=" * 50)
