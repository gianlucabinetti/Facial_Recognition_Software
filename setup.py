#!/usr/bin/env python
"""
Setup script for Face Recognition System
This script helps ensure proper installation of all dependencies
"""

import sys
import subprocess
import os
import platform

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("ERROR: Python 3.8 or higher is required!")
        return False
    return True

def create_virtual_environment():
    """Create a virtual environment if it doesn't exist"""
    venv_name = "venv"
    
    if not os.path.exists(venv_name):
        print(f"Creating virtual environment '{venv_name}'...")
        subprocess.run([sys.executable, "-m", "venv", venv_name])
        print(f"Virtual environment created!")
    else:
        print(f"Virtual environment '{venv_name}' already exists.")
    
    # Get activation command based on OS
    if platform.system() == "Windows":
        activate_cmd = f"{venv_name}\\Scripts\\activate"
        python_path = f"{venv_name}\\Scripts\\python.exe"
    else:
        activate_cmd = f"source {venv_name}/bin/activate"
        python_path = f"{venv_name}/bin/python"
    
    return activate_cmd, python_path

def install_requirements(python_path):
    """Install requirements using the virtual environment's pip"""
    print("\nInstalling requirements...")
    
    # Upgrade pip first
    print("Upgrading pip...")
    subprocess.run([python_path, "-m", "pip", "install", "--upgrade", "pip"])
    
    # Install requirements
    print("\nInstalling packages...")
    result = subprocess.run([python_path, "-m", "pip", "install", "-r", "requirements.txt"])
    
    if result.returncode != 0:
        print("\nERROR: Failed to install some packages.")
        print("Trying alternative installation method...")
        
        # Try installing packages one by one
        packages = [
            "flask==2.3.3",
            "opencv-python==4.8.1.78",
            "numpy==1.24.3",
            "werkzeug==2.3.7",
            "Pillow==10.0.1"
        ]
        
        for package in packages:
            print(f"Installing {package}...")
            subprocess.run([python_path, "-m", "pip", "install", package])
        
        # Try installing dlib and face-recognition separately
        print("\nInstalling dlib (this may take a while)...")
        dlib_result = subprocess.run([python_path, "-m", "pip", "install", "dlib"])
        
        if dlib_result.returncode == 0:
            print("Installing face-recognition...")
            subprocess.run([python_path, "-m", "pip", "install", "face-recognition"])
        else:
            print("\nWARNING: Could not install dlib. Make sure you have:")
            print("- Visual Studio Build Tools with C++ development tools")
            print("- CMake installed")
            print("\nThe application will run with limited functionality.")
    
    return result.returncode == 0

def verify_installation(python_path):
    """Verify that all packages are installed correctly"""
    print("\nVerifying installation...")
    
    packages_to_check = [
        ("flask", "Flask"),
        ("cv2", "OpenCV"),
        ("numpy", "NumPy"),
        ("PIL", "Pillow"),
        ("werkzeug", "Werkzeug")
    ]
    
    all_good = True
    
    for module_name, display_name in packages_to_check:
        try:
            result = subprocess.run(
                [python_path, "-c", f"import {module_name}"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print(f"✓ {display_name} is installed")
            else:
                print(f"✗ {display_name} is NOT installed")
                all_good = False
        except Exception as e:
            print(f"✗ {display_name} check failed: {e}")
            all_good = False
    
    # Check for face_recognition separately
    try:
        result = subprocess.run(
            [python_path, "-c", "import face_recognition"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"✓ face_recognition is installed (full features available)")
        else:
            print(f"⚠ face_recognition is NOT installed (limited functionality)")
    except:
        print(f"⚠ face_recognition is NOT installed (limited functionality)")
    
    return all_good

def create_directories():
    """Create necessary directories"""
    directories = ["face_images", "database"]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")

def main():
    print("="*50)
    print("Face Recognition System - Setup Script")
    print("="*50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create virtual environment
    activate_cmd, python_path = create_virtual_environment()
    
    print(f"\nIMPORTANT: To activate the virtual environment, run:")
    print(f"  {activate_cmd}")
    
    # Install requirements
    install_requirements(python_path)
    
    # Verify installation
    if verify_installation(python_path):
        print("\n✓ All core packages installed successfully!")
    else:
        print("\n⚠ Some packages are missing. Please check the errors above.")
    
    # Create directories
    create_directories()
    
    print("\n" + "="*50)
    print("Setup complete!")
    print("="*50)
    print("\nTo run the application:")
    print(f"1. Activate the virtual environment: {activate_cmd}")
    print(f"2. Run the application: python app.py")
    print("\nOr run directly with: {} app.py".format(python_path.replace('\\', '\\\\')))

if __name__ == "__main__":
    main()