#!/usr/bin/env python3
"""
Setup script for Public Grievance & Digital Governance Portal
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    print("Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ All packages installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing packages: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    directories = [
        "static/uploads",
        "static/css",
        "static/js",
        "templates"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def main():
    """Main setup function"""
    print("🚀 Setting up Public Grievance & Digital Governance Portal...")
    print("=" * 60)
    
    # Create directories
    print("\n📁 Creating directories...")
    create_directories()
    
    # Install requirements
    print("\n📦 Installing requirements...")
    if install_requirements():
        print("\n🎉 Setup completed successfully!")
        print("\n📋 Next steps:")
        print("1. Run: python app.py")
        print("2. Open: http://localhost:5000")
        print("3. Use demo credentials:")
        print("   - Citizen: citizen / citizen123")
        print("   - Admin: admin / admin123")
        print("\n🌟 Happy coding!")
    else:
        print("\n❌ Setup failed. Please check the error messages above.")

if __name__ == "__main__":
    main()

