#!/usr/bin/env python3
"""
Test script to verify file permissions and paths
"""
import os
import json
from datetime import datetime

def test_permissions():
    print("🔍 Testing File System Permissions")
    print("=" * 50)
    
    # Test face_images directory
    face_dir = "face_images"
    print(f"\n📁 Testing {face_dir}/:")
    
    if os.path.exists(face_dir):
        print(f"✅ Directory exists")
        
        # Check if it's actually a directory
        if os.path.isdir(face_dir):
            print(f"✅ Is a directory")
        else:
            print(f"❌ Not a directory!")
            return False
        
        # Test write permissions
        test_file = os.path.join(face_dir, "test_write.txt")
        try:
            with open(test_file, 'w') as f:
                f.write("test write")
            print(f"✅ Write test successful")
            
            # Read it back
            with open(test_file, 'r') as f:
                content = f.read()
            print(f"✅ Read test successful: '{content}'")
            
            # Delete test file
            os.remove(test_file)
            print(f"✅ Delete test successful")
            
        except Exception as e:
            print(f"❌ Permission test failed: {e}")
            return False
    else:
        print(f"❌ Directory does not exist")
        # Try to create it
        try:
            os.makedirs(face_dir, exist_ok=True)
            print(f"✅ Created directory successfully")
        except Exception as e:
            print(f"❌ Failed to create directory: {e}")
            return False
    
    # List existing files
    print(f"\n📋 Existing files in {face_dir}/:")
    try:
        files = os.listdir(face_dir)
        for f in files:
            filepath = os.path.join(face_dir, f)
            size = os.path.getsize(filepath) if os.path.isfile(filepath) else 0
            print(f"  • {f} ({size} bytes)")
    except Exception as e:
        print(f"❌ Failed to list files: {e}")
    
    return True

def test_config():
    print("\n⚙️  Testing Configuration")
    print("=" * 50)
    
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        # Check camera settings
        camera = config.get('camera', {})
        print(f"\n🎥 Camera Settings:")
        print(f"  • Resolution: {camera.get('width', 'default')}x{camera.get('height', 'default')}")
        print(f"  • FPS: {camera.get('fps', 'default')}")
        
        # Check performance settings
        perf = config.get('performance', {})
        print(f"\n⚡ Performance Settings:")
        print(f"  • Process every N frames: {perf.get('process_every_n_frames', 'default')}")
        print(f"  • JPEG quality: {perf.get('jpeg_quality', 'default')}%")
        
        return True
        
    except Exception as e:
        print(f"❌ Config test failed: {e}")
        return False

def test_paths():
    print("\n📂 Testing Path Resolution")
    print("=" * 50)
    
    # Current working directory
    cwd = os.getcwd()
    print(f"Current directory: {cwd}")
    
    # Test relative vs absolute paths
    rel_path = "face_images"
    abs_path = os.path.abspath(rel_path)
    print(f"\nRelative path: {rel_path}")
    print(f"Absolute path: {abs_path}")
    
    # Check if Windows path handling might be an issue
    if os.name == 'nt' or 'microsoft' in os.uname().release.lower():
        print("\n⚠️  Windows/WSL environment detected")
        print("  • Path handling may differ from native Linux")
        print("  • Case sensitivity might be an issue")
    
    return True

def suggest_fixes():
    print("\n💡 Suggested Fixes for Image Saving Issues:")
    print("=" * 50)
    print("\n1. Camera Tint Fix:")
    print("   • Reset camera to default settings")
    print("   • Enabled auto white balance")
    print("   • Removed manual brightness/contrast adjustments")
    print("\n2. Image Save Fix:")
    print("   • Added explicit JPEG quality parameter")
    print("   • Better error handling with detailed logging")
    print("   • File existence and size verification")
    print("   • Proper filename sanitization")
    print("\n3. If issues persist:")
    print("   • Check antivirus/Windows Defender settings")
    print("   • Ensure Python has file write permissions")
    print("   • Try running as administrator (on Windows)")
    print("   • Check disk space availability")

def main():
    print("🚀 Face Recognition System - Permission & Path Test")
    print("=" * 60)
    
    all_passed = True
    all_passed &= test_permissions()
    all_passed &= test_config()
    all_passed &= test_paths()
    
    suggest_fixes()
    
    if all_passed:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed - check the errors above")

if __name__ == "__main__":
    main()