#!/usr/bin/env python3
"""
Streamlit App Launcher for Digital Persona Survey System
"""

import subprocess
import sys
import os

def check_requirements():
    """Check if required packages are installed"""
    try:
        import streamlit
        import plotly
        import pandas
        print("✅ All required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("Please install requirements: pip install -r requirements.txt")
        return False

def setup_environment():
    """Setup environment and directories"""
    try:
        # Create necessary directories
        os.makedirs("data", exist_ok=True)
        os.makedirs("output", exist_ok=True)
        os.makedirs("output/personas", exist_ok=True)
        
        print("✅ Environment setup complete")
        return True
    except Exception as e:
        print(f"❌ Environment setup failed: {e}")
        return False

def main():
    """Launch Streamlit app"""
    print("🎭 Digital Persona Survey System - Streamlit Launcher")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        return
    
    # Setup environment
    if not setup_environment():
        return
    
    # Check for API key
    if not os.path.exists("config/.env"):
        print("⚠️  No .env file found. You can set your OpenAI API key in the app settings.")
    
    print("\n🚀 Launching Streamlit app...")
    print("The app will open in your default web browser.")
    print("If it doesn't open automatically, go to: http://localhost:8501")
    print("\nPress Ctrl+C to stop the app.")
    print("=" * 50)
    
    # Launch Streamlit
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
    except KeyboardInterrupt:
        print("\n👋 Streamlit app stopped.")
    except Exception as e:
        print(f"❌ Failed to launch Streamlit: {e}")

if __name__ == "__main__":
    main()