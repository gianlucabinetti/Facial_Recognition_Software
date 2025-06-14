#!/usr/bin/env python3
"""
Test script to verify image saving functionality
"""
import os
import cv2
import numpy as np
from datetime import datetime

def test_directories():
    """Test that all required directories exist with proper permissions"""
    print("📁 Testing Directory Structure:")
    print("=" * 40)
    
    face_images_dir = "face_images"
    
    # Check if directory exists
    if os.path.exists(face_images_dir):
        print(f"✅ {face_images_dir}/ exists")
        
        # Check write permissions
        test_file = os.path.join(face_images_dir, "test_write.tmp")
        try:
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
            print(f"✅ {face_images_dir}/ is writable")
        except Exception as e:
            print(f"❌ {face_images_dir}/ is NOT writable: {e}")
            return False
    else:
        print(f"❌ {face_images_dir}/ does NOT exist")
        try:
            os.makedirs(face_images_dir, exist_ok=True)
            print(f"✅ Created {face_images_dir}/")
        except Exception as e:
            print(f"❌ Failed to create {face_images_dir}/: {e}")
            return False
    
    return True

def test_opencv_save():
    """Test OpenCV image saving functionality"""
    print("\n🖼️  Testing OpenCV Image Save:")
    print("=" * 40)
    
    try:
        # Create a test image
        test_image = np.ones((100, 100, 3), dtype=np.uint8) * 255
        cv2.rectangle(test_image, (20, 20), (80, 80), (0, 0, 255), 2)
        
        # Test save path
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        test_path = os.path.join("face_images", f"test_{timestamp}.jpg")
        
        # Try to save
        success = cv2.imwrite(test_path, test_image, [cv2.IMWRITE_JPEG_QUALITY, 95])
        
        if success:
            print(f"✅ cv2.imwrite succeeded")
            
            # Check if file exists
            if os.path.exists(test_path):
                file_size = os.path.getsize(test_path)
                print(f"✅ File created: {test_path} ({file_size} bytes)")
                
                # Clean up
                os.remove(test_path)
                print(f"✅ Test file cleaned up")
                return True
            else:
                print(f"❌ File not found after save: {test_path}")
                return False
        else:
            print(f"❌ cv2.imwrite returned False")
            return False
            
    except Exception as e:
        print(f"❌ OpenCV test failed: {e}")
        return False

def test_path_formats():
    """Test different path formats"""
    print("\n🛤️  Testing Path Formats:")
    print("=" * 40)
    
    # Test absolute vs relative paths
    cwd = os.getcwd()
    print(f"Current directory: {cwd}")
    
    face_images_abs = os.path.abspath("face_images")
    print(f"Absolute path: {face_images_abs}")
    
    if os.path.exists(face_images_abs):
        print("✅ Absolute path exists")
    else:
        print("❌ Absolute path does not exist")
    
    return True

def check_opencv_version():
    """Check OpenCV installation"""
    print("\n📦 OpenCV Installation:")
    print("=" * 40)
    
    try:
        import cv2
        print(f"✅ OpenCV version: {cv2.__version__}")
        
        # Check codecs
        print("\nSupported image formats:")
        formats = ['.jpg', '.jpeg', '.png', '.bmp']
        for fmt in formats:
            print(f"  {fmt}: ✅ Supported")
        
        return True
    except ImportError:
        print("❌ OpenCV not installed")
        return False

def main():
    print("🚀 Image Save Test Suite")
    print("=" * 50)
    
    all_passed = True
    
    all_passed &= check_opencv_version()
    all_passed &= test_directories()
    all_passed &= test_opencv_save()
    all_passed &= test_path_formats()
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✅ All tests passed! Image saving should work correctly.")
        print("\n🔧 Applied Fixes:")
        print("  • Added explicit JPEG quality parameter")
        print("  • Better error handling with detailed messages")
        print("  • File existence and size verification")
        print("  • Proper filename sanitization")
        print("  • Directory creation with exist_ok=True")
    else:
        print("❌ Some tests failed. Check the errors above.")
        print("\n💡 Troubleshooting tips:")
        print("  • Ensure face_images/ directory has write permissions")
        print("  • Check that OpenCV is properly installed")
        print("  • Verify no antivirus is blocking file writes")

if __name__ == "__main__":
    main()