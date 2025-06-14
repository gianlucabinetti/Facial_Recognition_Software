#!/usr/bin/env python
"""
Quick diagnostic script to check Python environment and package installation
"""

import sys
import subprocess
import os

def main():
    print("="*60)
    print("Face Recognition System - Installation Checker")
    print("="*60)
    
    # Check Python version and path
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print(f"Current working directory: {os.getcwd()}")
    
    print("\n" + "-"*60)
    print("Checking required packages...")
    print("-"*60)
    
    packages = [
        'flask',
        'cv2',
        'face_recognition',
        'numpy',
        'sqlite3',
        'PIL',
        'werkzeug'
    ]
    
    missing_packages = []
    
    for package in packages:
        try:
            __import__(package)
            print(f"✓ {package:<15} - OK")
        except ImportError as e:
            print(f"✗ {package:<15} - MISSING ({e})")
            missing_packages.append(package)
    
    print("\n" + "-"*60)
    
    if missing_packages:
        print(f"Missing packages: {', '.join(missing_packages)}")
        print("\nTo fix this issue:")
        print("1. Make sure you're in a virtual environment:")
        print("   venv\\Scripts\\activate  (Windows)")
        print("   source venv/bin/activate  (Linux/macOS)")
        print("\n2. Install missing packages:")
        for package in missing_packages:
            if package == 'cv2':
                print(f"   pip install opencv-python")
            elif package == 'PIL':
                print(f"   pip install Pillow")
            else:
                print(f"   pip install {package}")
        print("\n3. Or run the full setup:")
        print("   python setup.py")
    else:
        print("✓ All required packages are installed!")
        print("\nYou can now run the application with:")
        print("   python app.py")
    
    print("="*60)

if __name__ == "__main__":
    main()