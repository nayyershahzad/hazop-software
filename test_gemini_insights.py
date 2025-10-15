#!/usr/bin/env python3
"""
Test script to demonstrate Gemini AI insights for HAZOP analysis
"""
import requests
import json
import sys

# Configuration
API_URL = "http://localhost:8000"
DEVIATION_ID = "cde3f2f3-268b-4f7d-ab52-88d70f5a3c16"  # "No flow from pump P-101"

# First, login to get a token
print("=" * 80)
print("STEP 1: Logging in to get authentication token...")
print("=" * 80)

login_data = {
    "email": "gemini_test@example.com",
    "password": "test123"
}

try:
    response = requests.post(f"{API_URL}/api/auth/login", json=login_data)
    if response.status_code == 200:
        token = response.json()["access_token"]
        print(f"✓ Login successful! Token obtained.\n")
    else:
        print(f"✗ Login failed: {response.status_code}")
        print(f"Response: {response.text}")
        print("\nPlease update the username/password in the script or register a new user.")
        sys.exit(1)
except Exception as e:
    print(f"✗ Error during login: {e}")
    sys.exit(1)

# Prepare headers with auth token
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# Test context data (similar to what you entered)
context_data = {
    "process_description": "Centrifugal pump transferring process fluid",
    "fluid_type": "Crude oil",
    "operating_conditions": "150°C, 5 bar",
    "previous_incidents": "Valve failed in 2018"
}

print("=" * 80)
print("STEP 2: Requesting AI-generated CAUSE suggestions...")
print("=" * 80)
print(f"Deviation: No flow from pump P-101")
print(f"Context provided:")
for key, value in context_data.items():
    print(f"  - {key}: {value}")
print()

# Request causes
payload = {
    "deviation_id": DEVIATION_ID,
    "context": context_data
}

try:
    response = requests.post(
        f"{API_URL}/api/gemini/suggest-causes",
        json=payload,
        headers=headers
    )

    if response.status_code == 200:
        causes = response.json()
        print(f"✓ Received {len(causes)} cause suggestions:\n")

        for i, cause in enumerate(causes, 1):
            print(f"  {i}. {cause['text']}")
            print(f"     Confidence: {cause['confidence']}%")
            if 'reasoning' in cause:
                print(f"     Reasoning: {cause['reasoning']}")
            print()
    else:
        print(f"✗ Failed to get causes: {response.status_code}")
        print(f"Response: {response.text}\n")

except Exception as e:
    print(f"✗ Error getting causes: {e}\n")

print("=" * 80)
print("STEP 3: Requesting AI-generated CONSEQUENCE suggestions...")
print("=" * 80)

try:
    response = requests.post(
        f"{API_URL}/api/gemini/suggest-consequences",
        json=payload,
        headers=headers
    )

    if response.status_code == 200:
        consequences = response.json()
        print(f"✓ Received {len(consequences)} consequence suggestions:\n")

        for i, cons in enumerate(consequences, 1):
            print(f"  {i}. {cons['text']}")
            print(f"     Confidence: {cons['confidence']}%")
            if 'severity' in cons:
                print(f"     Severity: {cons['severity']}")
            if 'category' in cons:
                print(f"     Category: {cons['category']}")
            print()
    else:
        print(f"✗ Failed to get consequences: {response.status_code}")
        print(f"Response: {response.text}\n")

except Exception as e:
    print(f"✗ Error getting consequences: {e}\n")

print("=" * 80)
print("STEP 4: Requesting AI-generated SAFEGUARD suggestions...")
print("=" * 80)

try:
    response = requests.post(
        f"{API_URL}/api/gemini/suggest-safeguards",
        json=payload,
        headers=headers
    )

    if response.status_code == 200:
        safeguards = response.json()
        print(f"✓ Received {len(safeguards)} safeguard suggestions:\n")

        for i, safe in enumerate(safeguards, 1):
            print(f"  {i}. {safe['text']}")
            print(f"     Confidence: {safe['confidence']}%")
            if 'type' in safe:
                print(f"     Type: {safe['type']}")
            if 'effectiveness' in safe:
                print(f"     Effectiveness: {safe['effectiveness']}")
            print()
    else:
        print(f"✗ Failed to get safeguards: {response.status_code}")
        print(f"Response: {response.text}\n")

except Exception as e:
    print(f"✗ Error getting safeguards: {e}\n")

print("=" * 80)
print("STEP 5: Requesting Contextual Knowledge...")
print("=" * 80)

# Get node ID for contextual knowledge
node_id = "41849b5b-f501-438f-ba56-9dc90cbcff05"  # Centrifugal Pump

knowledge_payload = {
    "node_id": node_id,
    "deviation_id": DEVIATION_ID,
    "context": context_data
}

try:
    response = requests.post(
        f"{API_URL}/api/gemini/contextual-knowledge",
        json=knowledge_payload,
        headers=headers
    )

    if response.status_code == 200:
        knowledge = response.json()

        print(f"✓ Contextual Knowledge Retrieved:\n")

        print(f"  Regulations ({len(knowledge['regulations'])} found):")
        for reg in knowledge['regulations']:
            print(f"    - {reg['title']}")
            print(f"      {reg['description']}")
            print()

        print(f"  Incident Reports ({len(knowledge['incident_reports'])} found):")
        for inc in knowledge['incident_reports']:
            print(f"    - {inc['title']} ({inc['date']})")
            print(f"      {inc['description']}")
            print()

        print(f"  Technical References ({len(knowledge['technical_references'])} found):")
        for tech in knowledge['technical_references']:
            print(f"    - {tech['title']}")
            print(f"      {tech['description']}")
            print()

    else:
        print(f"✗ Failed to get contextual knowledge: {response.status_code}")
        print(f"Response: {response.text}\n")

except Exception as e:
    print(f"✗ Error getting contextual knowledge: {e}\n")

print("=" * 80)
print("TEST COMPLETE!")
print("=" * 80)
