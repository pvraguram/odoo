#!/usr/bin/env python3
"""
Test script to verify backend-frontend connection
"""
import requests
import json
import sys

def test_backend_connection():
    """Test if the backend is running and responding"""
    base_url = "http://localhost:8000"
    
    print("Testing backend connection...")
    print(f"Base URL: {base_url}")
    print("-" * 50)
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Health check: PASSED")
            print(f"   Status: {data.get('status', 'unknown')}")
            print(f"   Endpoints: {len(data.get('endpoints', []))}")
        else:
            print(f"❌ Health check: FAILED (Status: {response.status_code})")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Health check: FAILED (Connection error: {e})")
        return False
    
    # Test truth table endpoint
    try:
        form_data = {'expr': 'A & B'}
        response = requests.post(f"{base_url}/truth-table", data=form_data, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Truth table endpoint: PASSED")
            print(f"   Variables: {data.get('variables', [])}")
            print(f"   Table rows: {len(data.get('table', []))}")
        else:
            print(f"❌ Truth table endpoint: FAILED (Status: {response.status_code})")
    except requests.exceptions.RequestException as e:
        print(f"❌ Truth table endpoint: FAILED (Error: {e})")
    
    # Test K-map endpoint
    try:
        form_data = {'expr': 'A & B | C'}
        response = requests.post(f"{base_url}/kmap", data=form_data, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ K-map endpoint: PASSED")
            print(f"   Simplified: {data.get('simplified', 'N/A')}")
            print(f"   Image URL: {data.get('image_url', 'N/A')}")
        else:
            print(f"❌ K-map endpoint: FAILED (Status: {response.status_code})")
    except requests.exceptions.RequestException as e:
        print(f"❌ K-map endpoint: FAILED (Error: {e})")
    
    # Test circuit endpoint
    try:
        form_data = {'expr': 'A & B | C'}
        response = requests.post(f"{base_url}/circuit", data=form_data, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Circuit endpoint: PASSED")
            print(f"   Variables: {data.get('variables', [])}")
            print(f"   Gate count: {data.get('gate_count', 0)}")
        else:
            print(f"❌ Circuit endpoint: FAILED (Status: {response.status_code})")
    except requests.exceptions.RequestException as e:
        print(f"❌ Circuit endpoint: FAILED (Error: {e})")
    
    # Test sequence detector endpoint
    try:
        form_data = {
            'sequence_str': '1010',
            'detector_type': 'mealy',
            'test_sequence': '110101010'
        }
        response = requests.post(f"{base_url}/sequence-detector", data=form_data, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Sequence detector endpoint: PASSED")
            print(f"   Success: {data.get('success', False)}")
            if data.get('success'):
                result_data = data.get('data', {})
                print(f"   Sequence: {result_data.get('sequence', 'N/A')}")
                print(f"   Detections: {result_data.get('detections', [])}")
        else:
            print(f"❌ Sequence detector endpoint: FAILED (Status: {response.status_code})")
    except requests.exceptions.RequestException as e:
        print(f"❌ Sequence detector endpoint: FAILED (Error: {e})")
    
    print("-" * 50)
    print("✅ Backend connection test completed!")
    print("\nTo start the application:")
    print("1. Run: start_backend.bat")
    print("2. Open browser to: http://localhost:8000/improved.html")
    print("3. Test the 'Test Backend Connection' button in the UI")
    
    return True

if __name__ == "__main__":
    try:
        test_backend_connection()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        sys.exit(1)