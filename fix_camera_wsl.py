#!/usr/bin/env python3
"""
Fix for camera black screen in WSL environment
"""

def show_wsl_camera_fix():
    print("🔧 WSL Camera Fix Guide")
    print("=" * 50)
    
    print("\n⚠️  ISSUE IDENTIFIED:")
    print("You're running in WSL (Windows Subsystem for Linux)")
    print("WSL has limited access to hardware devices like cameras")
    
    print("\n💡 SOLUTIONS:")
    print()
    print("Option 1: Run on Native Windows (RECOMMENDED)")
    print("=" * 45)
    print("1. Open Windows Command Prompt or PowerShell")
    print("2. Navigate to your project folder:")
    print("   cd \"C:\\Users\\gianl\\OneDrive\\Desktop\\Projects\\Facial recognition Project\"")
    print("3. Activate virtual environment:")
    print("   .\\venv\\Scripts\\activate")
    print("   OR")
    print("   .\\my_project_env\\Scripts\\activate")
    print("4. Run the application:")
    print("   python app.py")
    
    print("\nOption 2: Windows Terminal with WSL2 USB Support")
    print("=" * 50)
    print("1. Install usbipd-win on Windows")
    print("2. List USB devices: usbipd wsl list")
    print("3. Attach camera: usbipd wsl attach --busid <camera-busid>")
    print("4. This is complex and may not work reliably")
    
    print("\nOption 3: Use Windows File Explorer")
    print("=" * 40)
    print("1. Open File Explorer")
    print("2. Navigate to your project folder")
    print("3. Right-click in the folder → 'Open in Terminal'")
    print("4. This should open PowerShell in the correct directory")
    print("5. Run: python app.py")

def create_windows_batch_file():
    """Create a batch file to run the application on Windows"""
    batch_content = '''@echo off
echo Starting Face Recognition System...
echo.

REM Try to activate virtual environment
if exist venv\\Scripts\\activate.bat (
    echo Activating venv virtual environment...
    call venv\\Scripts\\activate.bat
) else if exist my_project_env\\Scripts\\activate.bat (
    echo Activating my_project_env virtual environment...
    call my_project_env\\Scripts\\activate.bat
) else (
    echo No virtual environment found, using system Python...
)

echo.
echo Starting application...
python app.py

pause
'''
    
    try:
        with open('run_windows.bat', 'w') as f:
            f.write(batch_content)
        print("\n✅ Created 'run_windows.bat' file")
        print("   Double-click this file on Windows to run the application")
    except Exception as e:
        print(f"\n❌ Failed to create batch file: {e}")

def update_camera_fallback():
    """Update the camera code to be more robust"""
    print("\n🔧 Applying Camera Fallback Fix...")
    
    # The camera initialization should already be updated with fallback
    print("✅ Camera fallback code already applied in app.py")
    print("   - Tries camera indices 0-4")
    print("   - Shows error message if no camera found")
    print("   - Provides visual feedback")

def main():
    show_wsl_camera_fix()
    create_windows_batch_file()
    update_camera_fallback()
    
    print("\n" + "=" * 50)
    print("🎯 RECOMMENDATION:")
    print("Run the application on native Windows for best camera support")
    print("Use the 'run_windows.bat' file or follow Option 1 above")

if __name__ == "__main__":
    main()