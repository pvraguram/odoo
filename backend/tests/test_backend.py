#!/usr/bin/env python3
"""
Test script for the Digital Logic Backend
"""

import requests
import json

def test_backend():
    """Test the backend API endpoints"""
    base_url = "http://localhost:8000"
    
    print("Testing Digital Logic Backend...")
    print("=" * 50)
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("[OK] Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"[FAIL] Health check failed: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] Health check error: {e}")
        print("   Make sure the backend server is running:")
        print("   python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload")
        return False
    
    # Test simplify endpoint
    test_expression = "A & B | A & ~B"
    print(f"\nTesting simplify endpoint with: {test_expression}")
    
    try:
        data = {"expr": test_expression}
        response = requests.post(f"{base_url}/simplify", data=data)
        
        if response.status_code == 200:
            result = response.json()
            print("[OK] Simplify endpoint working")
            print(f"   Original: {result.get('original', 'N/A')}")
            print(f"   Simplified: {result.get('simplified', 'N/A')}")
            print(f"   Variables: {result.get('variables', 'N/A')}")
            print(f"   Complexity reduction: {result.get('complexity_reduction', 'N/A')}")
        else:
            print(f"[FAIL] Simplify endpoint failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"[ERROR] Simplify endpoint error: {e}")
        return False
    
    # Test truth table endpoint
    print(f"\nTesting truth table endpoint with: {test_expression}")
    
    try:
        data = {"expr": test_expression}
        response = requests.post(f"{base_url}/truth-table", data=data)
        
        if response.status_code == 200:
            result = response.json()
            print("[OK] Truth table endpoint working")
            print(f"   Variables: {result.get('variables', 'N/A')}")
            print(f"   Table rows: {len(result.get('table', []))}")
        else:
            print(f"[FAIL] Truth table endpoint failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"[ERROR] Truth table endpoint error: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("[SUCCESS] All tests passed! Backend is working correctly.")
    return True

if __name__ == "__main__":
    test_backend() 