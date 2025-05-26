#!/usr/bin/env python3
"""
Setup script for Digital Persona Survey System
Creates virtual environment and installs dependencies
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return False

def main():
    """Main setup process"""
    print("🎭 Digital Persona Survey System - Setup")
    print("=" * 50)
    
    # Check if we're on Windows
    is_windows = os.name == 'nt'
    venv_activate = "venv\\Scripts\\activate" if is_windows else "source venv/bin/activate"
    pip_command = "venv\\Scripts\\pip" if is_windows else "venv/bin/pip"
    python_command = "venv\\Scripts\\python" if is_windows else "venv/bin/python"
    
    # Create virtual environment
    if not os.path.exists("venv"):
        if not run_command("python -m venv venv", "Creating virtual environment"):
            return False
    else:
        print("✅ Virtual environment already exists")
    
    # Install requirements
    if not run_command(f"{pip_command} install -r requirements.txt", "Installing requirements"):
        return False
    
    # Create necessary directories
    print("🔄 Creating directories...")
    directories = ["data", "output", "output/personas"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    print("✅ Directories created")
    
    # Check if .env file exists
    if not os.path.exists("config/.env"):
        print("⚠️  Creating .env file from template...")
        if os.path.exists("config/.env.example"):
            import shutil
            shutil.copy("config/.env.example", "config/.env")
            print("✅ .env file created from template")
            print("📝 Please edit config/.env and add your OpenAI API key")
        else:
            print("❌ .env.example not found")
    else:
        print("✅ .env file already exists")
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Edit config/.env and add your OpenAI API key")
    print("2. Activate virtual environment:")
    if is_windows:
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    print("3. Run the Streamlit app:")
    print(f"   {python_command} run_streamlit.py")
    print("   OR")
    print(f"   {python_command} -m streamlit run streamlit_app.py")
    print("\nAlternatively, use the launcher:")
    print(f"   {python_command} run_streamlit.py")

if __name__ == "__main__":
    main()