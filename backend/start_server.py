#!/usr/bin/env python3
"""
Startup script for the Digital Logic Backend Server
"""

import subprocess
import sys
import os
import time
import webbrowser
from pathlib import Path

def check_requirements():
    """Check if all required packages are installed"""
    try:
        import fastapi
        import uvicorn
        import sympy
        import matplotlib
        import graphviz
        print("✅ All required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("Please install requirements: pip install -r requirements.txt")
        return False

def start_server():
    """Start the FastAPI server"""
    if not check_requirements():
        return False
    
    print("🚀 Starting Digital Logic Backend Server...")
    print("=" * 50)
    
    # Change to the DIGITAL/backend/app directory
    os.chdir(Path(__file__).parent / "app")
    
    try:
        # Start the server
        print("📡 Server starting on http://localhost:8000")
        print("🌐 Frontend available at http://localhost:8000/improved.html")
        print("📊 API documentation at http://localhost:8000/docs")
        print("💡 Press Ctrl+C to stop the server")
        print("=" * 50)
        
        # Open browser after a short delay
        def open_browser():
            time.sleep(2)
            try:
                webbrowser.open("http://localhost:8000/improved.html")
                print("🌐 Opened frontend in browser")
            except:
                print("⚠️  Could not open browser automatically")
        
        import threading
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        # Start uvicorn server
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ])
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🔧 Digital Logic Backend Server Startup")
    print("=" * 50)
    
    if start_server():
        print("✅ Server started successfully")
    else:
        print("❌ Failed to start server")
        sys.exit(1)