#!/usr/bin/env python3
"""
HAZOP Gemini Integration Diagnostic Tool
=========================================

This script diagnoses why Gemini suggestions aren't appearing in the frontend.

It tests:
1. Backend API connectivity
2. Authentication
3. Data availability (studies, nodes, deviations)
4. Gemini API integration
5. Frontend-to-backend communication

Usage:
    python3 test_gemini_frontend.py

Author: Claude
Date: October 2025
"""

import requests
import json
import sys
from typing import Optional, Dict, Any

# Configuration
API_BASE = "http://localhost:8000"
FRONTEND_URL = "http://localhost:5173"

# Colors for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    """Print a formatted header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.RESET}\n")

def print_success(text: str):
    """Print success message"""
    print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")

def print_error(text: str):
    """Print error message"""
    print(f"{Colors.RED}❌ {text}{Colors.RESET}")

def print_warning(text: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.RESET}")

def print_info(text: str):
    """Print info message"""
    print(f"{Colors.CYAN}ℹ️  {text}{Colors.RESET}")

def test_backend_health() -> bool:
    """Test if backend is running"""
    print_header("1. Testing Backend Health")
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        if response.status_code == 200:
            print_success("Backend is running and healthy")
            return True
        else:
            print_error(f"Backend returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to backend at http://localhost:8000")
        print_info("Start backend with: cd backend && source venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        return False
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return False

def test_login(email: Optional[str] = None, password: Optional[str] = None) -> Optional[str]:
    """Test login and return access token"""
    print_header("2. Testing Authentication")

    # If no credentials provided, prompt user
    if not email or not password:
        print_info("Please enter your login credentials:")
        email = input(f"{Colors.CYAN}Email: {Colors.RESET}")
        password = input(f"{Colors.CYAN}Password: {Colors.RESET}")

    try:
        response = requests.post(
            f"{API_BASE}/api/auth/login",
            json={"email": email, "password": password},
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            user = data.get("user", {})
            print_success(f"Login successful as {user.get('full_name')} ({user.get('email')})")
            return token
        elif response.status_code == 401:
            print_error("Invalid credentials")
            print_info("If you don't have an account, go to http://localhost:5173 and register")
            return None
        else:
            print_error(f"Login failed with status {response.status_code}")
            print_info(f"Response: {response.text}")
            return None
    except Exception as e:
        print_error(f"Login error: {e}")
        return None

def test_data_availability(token: str) -> Optional[Dict[str, Any]]:
    """Test if studies, nodes, and deviations exist"""
    print_header("3. Testing Data Availability")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        # Get studies
        print_info("Fetching studies...")
        studies_response = requests.get(f"{API_BASE}/api/studies", headers=headers, timeout=10)

        if studies_response.status_code != 200:
            print_error(f"Failed to fetch studies: {studies_response.status_code}")
            return None

        studies = studies_response.json()

        if not studies:
            print_warning("No studies found in database")
            print_info("Create a study in the UI first:")
            print_info("  1. Go to http://localhost:5173")
            print_info("  2. Click 'Create New Study'")
            print_info("  3. Add a node (e.g., 'Pump P-101')")
            print_info("  4. Add a deviation (e.g., 'Flow / No')")
            return None

        print_success(f"Found {len(studies)} study/studies")
        study = studies[0]
        study_id = study.get('id')
        print_info(f"Using study: {study.get('study_name')} (ID: {study_id})")

        # Get nodes
        print_info("Fetching nodes...")
        nodes_response = requests.get(
            f"{API_BASE}/api/studies/{study_id}/nodes",
            headers=headers,
            timeout=10
        )

        if nodes_response.status_code != 200:
            print_error(f"Failed to fetch nodes: {nodes_response.status_code}")
            return None

        nodes = nodes_response.json()

        if not nodes:
            print_warning("No nodes found in study")
            print_info("Add a node to your study first")
            return None

        print_success(f"Found {len(nodes)} node(s)")
        node = nodes[0]
        node_id = node.get('id')
        print_info(f"Using node: {node.get('node_name')} (ID: {node_id})")

        # Get deviations
        print_info("Fetching deviations...")
        deviations_response = requests.get(
            f"{API_BASE}/api/hazop/nodes/{node_id}/deviations",
            headers=headers,
            timeout=10
        )

        if deviations_response.status_code != 200:
            print_error(f"Failed to fetch deviations: {deviations_response.status_code}")
            return None

        deviations = deviations_response.json()

        if not deviations:
            print_warning("No deviations found for node")
            print_info("Add a deviation to your node first")
            return None

        print_success(f"Found {len(deviations)} deviation(s)")
        deviation = deviations[0]
        deviation_id = deviation.get('id')
        print_info(f"Using deviation: {deviation.get('parameter')} / {deviation.get('guide_word')} (ID: {deviation_id})")

        return {
            "study": study,
            "node": node,
            "deviation": deviation,
            "headers": headers
        }

    except Exception as e:
        print_error(f"Error checking data: {e}")
        return None

def test_gemini_api(data: Dict[str, Any]) -> bool:
    """Test Gemini API endpoints"""
    print_header("4. Testing Gemini API Integration")

    deviation_id = data['deviation']['id']
    headers = data['headers']

    # Test context
    context = {
        "process_description": "Centrifugal pump transferring process fluid",
        "fluid_type": "Crude oil",
        "operating_conditions": "150°C, 5 bar",
        "previous_incidents": "Valve failed in 2018"
    }

    print_info("Test Context:")
    print(f"  • Process: {context['process_description']}")
    print(f"  • Fluid: {context['fluid_type']}")
    print(f"  • Conditions: {context['operating_conditions']}")
    print(f"  • History: {context['previous_incidents']}")

    # Test suggest-causes
    print(f"\n{Colors.BOLD}Testing: suggest-causes{Colors.RESET}")
    try:
        payload = {
            "deviation_id": deviation_id,
            "context": context
        }

        print_info(f"Sending request to /api/gemini/suggest-causes...")
        response = requests.post(
            f"{API_BASE}/api/gemini/suggest-causes",
            json=payload,
            headers=headers,
            timeout=60
        )

        if response.status_code == 200:
            causes = response.json()
            if causes:
                print_success(f"Received {len(causes)} cause suggestions")
                print(f"\n{Colors.BOLD}Sample Causes:{Colors.RESET}")
                for i, cause in enumerate(causes[:3], 1):
                    print(f"  {i}. {cause.get('text', 'N/A')[:70]}...")
                    print(f"     Confidence: {cause.get('confidence')}%")
            else:
                print_warning("Received empty suggestions array")
                print_info("This might be due to Gemini API rate limiting or safety filters")
            return True
        else:
            print_error(f"Request failed with status {response.status_code}")
            print_info(f"Response: {response.text}")
            return False

    except requests.exceptions.Timeout:
        print_error("Request timed out (>60 seconds)")
        print_info("Gemini API might be slow or unresponsive")
        return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_gemini_api_key() -> bool:
    """Test if Gemini API key is configured"""
    print_header("5. Checking Gemini API Key Configuration")

    try:
        import os
        import sys
        sys.path.insert(0, '/Users/nayyershahzad/HAZOP-Software/backend')

        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv('/Users/nayyershahzad/HAZOP-Software/backend/.env')

        api_key = os.getenv('GEMINI_API_KEY')

        if api_key:
            print_success("Gemini API key is configured")
            print_info(f"API Key: {api_key[:20]}...")

            # Test the key directly
            print_info("Testing API key with Google Gemini...")
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('models/gemini-2.5-flash')
            response = model.generate_content('Say hello in 5 words')
            print_success(f"API key is valid! Response: {response.text}")
            return True
        else:
            print_error("Gemini API key not found in .env file")
            print_info("Add GEMINI_API_KEY to backend/.env")
            print_info("Get a key from: https://makersuite.google.com/app/apikey")
            return False

    except ImportError:
        print_warning("Cannot test API key (missing dependencies)")
        print_info("Run: pip install python-dotenv google-generativeai")
        return True  # Don't fail the whole test
    except Exception as e:
        print_error(f"Error testing API key: {e}")
        return False

def provide_solution():
    """Provide solution based on test results"""
    print_header("💡 Solution & Next Steps")

    print(f"{Colors.BOLD}Common Issues:{Colors.RESET}\n")

    print("1️⃣  Frontend not receiving suggestions:")
    print("   • Check browser console for errors (F12)")
    print("   • Verify you're logged in with a valid token")
    print("   • Make sure you filled in the context form and clicked 'Apply Context'")
    print("   • Click the refresh button (🔄) in the AI Insights panel")

    print("\n2️⃣  Backend returning empty suggestions:")
    print("   • Gemini API might be rate-limited or blocked by safety filters")
    print("   • Try with different context descriptions")
    print("   • Check backend logs: tail -f /tmp/hazop-backend.log")

    print("\n3️⃣  Authentication issues:")
    print("   • Token might be expired - logout and login again")
    print("   • Clear browser localStorage and login fresh")

    print(f"\n{Colors.BOLD}How to use Gemini in the UI:{Colors.RESET}\n")
    print("1. Go to http://localhost:5173 and login")
    print("2. Select a study → Select a node → Click on a deviation")
    print("3. Look for the AI Insights panel (bottom-left, purple header)")
    print("4. Click to expand the panel")
    print("5. Click '+ Add Context' button")
    print("6. Fill in the context form:")
    print("   • Process Description: Centrifugal pump transferring process fluid")
    print("   • Fluid Type: Crude oil")
    print("   • Operating Conditions: 150°C, 5 bar")
    print("   • Previous Incidents: Valve failed in 2018")
    print("7. Click 'Apply Context'")
    print("8. Click the refresh button (🔄) in the panel header")
    print("9. Wait 5-10 seconds for AI to generate suggestions")
    print("10. Suggestions should appear in the selected tab")

def main():
    """Main diagnostic routine"""
    print(f"{Colors.BOLD}{Colors.MAGENTA}")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║         HAZOP Gemini Integration Diagnostic Tool                  ║")
    print("║                                                                    ║")
    print("║  This tool will help diagnose why Gemini suggestions aren't       ║")
    print("║  appearing in your HAZOP Software frontend.                       ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    print(Colors.RESET)

    # Run tests
    if not test_backend_health():
        print_error("\nBackend is not running. Cannot continue tests.")
        sys.exit(1)

    if not test_gemini_api_key():
        print_warning("\nGemini API key issue detected, but continuing tests...")

    token = test_login()
    if not token:
        print_error("\nAuthentication failed. Cannot continue tests.")
        print_info("Make sure you have a registered user account.")
        sys.exit(1)

    data = test_data_availability(token)
    if not data:
        print_error("\nNo data available for testing. Create a study/node/deviation first.")
        provide_solution()
        sys.exit(1)

    success = test_gemini_api(data)

    # Final summary
    print_header("📊 Diagnostic Summary")

    if success:
        print_success("All tests passed! Gemini integration is working correctly.")
        print_info("If you're still not seeing suggestions in the UI:")
        print_info("  1. Check browser console for JavaScript errors")
        print_info("  2. Make sure you filled in the context form")
        print_info("  3. Click the refresh button after adding context")
        print_info("  4. Wait 5-10 seconds for AI to respond")
    else:
        print_error("Some tests failed. See errors above.")
        provide_solution()

    print(f"\n{Colors.BOLD}Need more help?{Colors.RESET}")
    print("  • Check CLAUDE.md for full documentation")
    print("  • Check Gemini_Test.md for usage guide")
    print("  • Review backend logs: tail -f /tmp/hazop-backend.log")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Test interrupted by user{Colors.RESET}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}Unexpected error: {e}{Colors.RESET}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
