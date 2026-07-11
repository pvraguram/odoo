#!/usr/bin/env python3
"""
Integration validation script for Digital Logic Platform
Validates the setup without requiring a running server
"""

import os
import sys
from pathlib import Path

def check_file_exists(filepath, description):
    """Check if a file exists and report status"""
    if os.path.exists(filepath):
        print(f"[OK] {description}: {filepath}")
        return True
    else:
        print(f"[MISSING] {description}: {filepath}")
        return False

def check_python_imports():
    """Check if all required Python packages can be imported"""
    print("\nChecking Python dependencies...")
    required_packages = [
        ('fastapi', 'FastAPI web framework'),
        ('uvicorn', 'ASGI server'),
        ('sympy', 'Symbolic mathematics'),
        ('matplotlib', 'Plotting library'),
        ('graphviz', 'Graph visualization'),
        ('requests', 'HTTP library'),
        ('numpy', 'Numerical computing')
    ]
    
    all_good = True
    for package, description in required_packages:
        try:
            __import__(package)
            print(f"[OK] {description} ({package})")
        except ImportError:
            print(f"[MISSING] {description} ({package})")
            all_good = False
    
    return all_good

def validate_backend_structure():
    """Validate backend file structure and imports"""
    print("\nValidating backend structure...")
    
    # Check main files
    files_to_check = [
        ('main.py', 'Main FastAPI server'),
        ('logic.py', 'Boolean logic operations'),
        ('sequence.py', 'Sequence detector logic'),
        ('requirements.txt', 'Python dependencies'),
        ('start_server.py', 'Python startup script'),
        ('start_backend.bat', 'Windows startup script'),
        ('test_backend.py', 'Backend test script'),
        ('README.md', 'Documentation')
    ]
    
    all_files_exist = True
    for filename, description in files_to_check:
        if not check_file_exists(filename, description):
            all_files_exist = False
    
    # Check if outputs directory exists or can be created
    outputs_dir = "outputs"
    if not os.path.exists(outputs_dir):
        try:
            os.makedirs(outputs_dir)
            print(f"[CREATED] Output directory: {outputs_dir}")
        except Exception as e:
            print(f"[ERROR] Cannot create output directory: {e}")
            all_files_exist = False
    else:
        print(f"[OK] Output directory exists: {outputs_dir}")
    
    return all_files_exist

def validate_frontend_structure():
    """Validate frontend file structure"""
    print("\nValidating frontend structure...")
    
    frontend_file = 'improved.html'
    if not check_file_exists(frontend_file, 'Main frontend application'):
        return False
    
    # Check if the HTML file contains key integration points
    try:
        with open(frontend_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        checks = [
            ('API_BASE_URL', 'API base URL configuration'),
            ('callAPI', 'API calling function'),
            ('generateKMap', 'K-Map generation'),
            ('analyzeSequence', 'Sequence detector'),
            ('cache-busting', 'Image cache-busting'),
            ('workspaceManager', 'Workspace management')
        ]
        
        all_checks_pass = True
        for check, description in checks:
            if check in content:
                print(f"[OK] {description} found")
            else:
                print(f"[MISSING] {description} not found")
                all_checks_pass = False
        
        return all_checks_pass
        
    except Exception as e:
        print(f"[ERROR] Cannot read frontend file: {e}")
        return False

def validate_api_endpoints():
    """Validate that all API endpoints are defined in main.py"""
    print("\nValidating API endpoints...")
    
    try:
        with open('main.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        expected_endpoints = [
            ('/truth-table', 'Truth table generation'),
            ('/kmap', 'K-Map generation'),
            ('/circuit', 'Circuit analysis'),
            ('/simplify', 'Boolean simplification'),
            ('/sequence-detector', 'Sequence detector'),
            ('/compare-sequences', 'Sequence comparison'),
            ('/flipflops', 'Flip-flop analysis'),
            ('/health', 'Health check')
        ]
        
        all_endpoints_found = True
        for endpoint, description in expected_endpoints:
            if endpoint in content:
                print(f"[OK] {description} endpoint: {endpoint}")
            else:
                print(f"[MISSING] {description} endpoint: {endpoint}")
                all_endpoints_found = False
        
        return all_endpoints_found
        
    except Exception as e:
        print(f"[ERROR] Cannot read main.py: {e}")
        return False

def validate_integration_fixes():
    """Validate that key integration fixes are in place"""
    print("\nValidating integration fixes...")
    
    fixes_to_check = []
    
    # Check main.py for cache-busting
    try:
        with open('main.py', 'r', encoding='utf-8') as f:
            main_content = f.read()
        
        if 'timestamp' in main_content and 'cache-busting' in main_content.lower():
            print("[OK] Cache-busting implementation found in backend")
            fixes_to_check.append(True)
        else:
            print("[MISSING] Cache-busting implementation in backend")
            fixes_to_check.append(False)
            
        if '/outputs/{filename}' in main_content:
            print("[OK] Output file serving endpoint found")
            fixes_to_check.append(True)
        else:
            print("[MISSING] Output file serving endpoint")
            fixes_to_check.append(False)
            
    except Exception as e:
        print(f"[ERROR] Cannot validate main.py fixes: {e}")
        fixes_to_check.append(False)
    
    # Check improved.html for cache-busting
    try:
        with open('improved.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        if 'timestamp' in html_content and 'cache-busting' in html_content.lower():
            print("[OK] Cache-busting implementation found in frontend")
            fixes_to_check.append(True)
        else:
            print("[MISSING] Cache-busting implementation in frontend")
            fixes_to_check.append(False)
            
        if 'image_url' in html_content:
            print("[OK] Image URL handling found in frontend")
            fixes_to_check.append(True)
        else:
            print("[MISSING] Image URL handling in frontend")
            fixes_to_check.append(False)
            
    except Exception as e:
        print(f"[ERROR] Cannot validate improved.html fixes: {e}")
        fixes_to_check.append(False)
    
    return all(fixes_to_check)

def main():
    """Main validation function"""
    print("=" * 60)
    print("Digital Logic Platform - Integration Validation")
    print("=" * 60)
    
    # Change to the script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    print(f"Working directory: {os.getcwd()}")
    
    validation_results = []
    
    # Run all validations
    validation_results.append(check_python_imports())
    validation_results.append(validate_backend_structure())
    validation_results.append(validate_frontend_structure())
    validation_results.append(validate_api_endpoints())
    validation_results.append(validate_integration_fixes())
    
    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    
    if all(validation_results):
        print("[SUCCESS] All validations passed!")
        print("\nYour integration is ready. To start the server:")
        print("  Option 1: Double-click 'start_backend.bat' (Windows)")
        print("  Option 2: Run 'python start_server.py'")
        print("  Option 3: Run 'python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload'")
        print("\nThen open: http://localhost:8000/improved.html")
        return True
    else:
        print("[FAILURE] Some validations failed!")
        print("Please fix the issues above before running the server.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)