#!/usr/bin/env python3
"""
End-to-end API test for the Jira Autofix Flask app.

This script tests the API endpoints directly without a browser.
Run with: python adk/tests/test_api_e2e.py
"""
import requests
import json
import time
import sys

BASE_URL = "http://localhost:5000"

def test_index():
    """Test that the index page loads."""
    print("1. Testing index page...")
    response = requests.get(f"{BASE_URL}/")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    assert "Jira Autofix Agent" in response.text
    print("   ✓ Index page loads correctly\n")

def test_workflow():
    """Test the complete workflow API."""
    # Use a session to maintain cookies
    session = requests.Session()
    
    # Step 1: Start workflow
    print("2. Testing /api/start...")
    response = session.post(
        f"{BASE_URL}/api/start",
        json={"issue_key": "SCRUM-1"},
        headers={"Content-Type": "application/json"}
    )
    print(f"   Status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"   ✗ Failed: {response.text}")
        return False
    
    data = response.json()
    print(f"   Response: {json.dumps(data, indent=2)}")
    
    assert data.get("status") == "started"
    assert data.get("issue_key") == "SCRUM-1"
    assert "state" in data
    print("   ✓ Workflow started successfully\n")
    
    # Step 2: Get status
    print("3. Testing /api/status...")
    response = session.get(f"{BASE_URL}/api/status")
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Response: {json.dumps(data, indent=2)}")
    print("   ✓ Status endpoint works\n")
    
    # Step 3: Run first phase
    print("4. Testing /api/run (Phase 1: Gather Jira Context)...")
    print("   This may take up to 60 seconds while the ADK agent runs...")
    start_time = time.time()
    
    response = session.post(
        f"{BASE_URL}/api/run",
        headers={"Content-Type": "application/json"}
    )
    
    elapsed = time.time() - start_time
    print(f"   Status: {response.status_code} (took {elapsed:.2f}s)")
    
    try:
        data = response.json()
        print(f"   Response: {json.dumps(data, indent=2)[:1000]}...")  # Truncate long responses
    except:
        print(f"   Raw response: {response.text[:500]}")
    
    if response.status_code == 200:
        if data.get("status") == "success":
            print("   ✓ Phase 1 completed successfully!")
            return True
        else:
            print(f"   ✗ Phase status: {data.get('status')}")
            return False
    else:
        print(f"   ✗ API returned error: {response.status_code}")
        if "error" in data:
            print(f"   Error details: {data['error']}")
        return False

def main():
    print("=" * 60)
    print("ADK Jira Autofix - API End-to-End Test")
    print("=" * 60)
    print(f"\nTargeting: {BASE_URL}\n")
    
    # Check server is running
    try:
        requests.get(BASE_URL, timeout=2)
    except requests.exceptions.ConnectionError:
        print("ERROR: Flask server is not running!")
        print("Start it with: ./adk/start.sh")
        sys.exit(1)
    
    try:
        test_index()
        success = test_workflow()
        
        print("\n" + "=" * 60)
        if success:
            print("✓ ALL TESTS PASSED")
        else:
            print("✗ SOME TESTS FAILED")
        print("=" * 60)
        
        sys.exit(0 if success else 1)
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
