#!/usr/bin/env python3
"""
Quick camera test to diagnose black screen issue
"""
import os
import sys

def test_basic_camera():
    """Test basic camera access"""
    print("🎥 Testing Camera Access")
    print("=" * 40)
    
    try:
        import cv2
        print(f"✅ OpenCV imported successfully (version: {cv2.__version__})")
    except ImportError as e:
        print(f"❌ OpenCV import failed: {e}")
        return False
    
    # Test different camera indices
    for i in range(5):
        print(f"\nTesting camera index {i}:")
        try:
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                print(f"  ✅ Camera {i} opened successfully")
                
                # Try to read a frame
                ret, frame = cap.read()
                if ret and frame is not None:
                    print(f"  ✅ Frame captured: {frame.shape}")
                    
                    # Check if frame is not all black
                    if frame.mean() > 10:
                        print(f"  ✅ Frame has content (brightness: {frame.mean():.1f})")
                        cap.release()
                        return True, i
                    else:
                        print(f"  ⚠️  Frame appears black (brightness: {frame.mean():.1f})")
                else:
                    print(f"  ❌ Failed to capture frame")
                
                cap.release()
            else:
                print(f"  ❌ Camera {i} failed to open")
        except Exception as e:
            print(f"  ❌ Error testing camera {i}: {e}")
    
    return False, None

def test_camera_with_settings():
    """Test camera with various settings"""
    print("\n🔧 Testing Camera Settings")
    print("=" * 40)
    
    try:
        import cv2
        
        # Find working camera
        cap = None
        for i in range(5):
            test_cap = cv2.VideoCapture(i)
            if test_cap.isOpened():
                ret, frame = test_cap.read()
                if ret and frame is not None and frame.mean() > 10:
                    cap = test_cap
                    print(f"Using camera index {i}")
                    break
                test_cap.release()
        
        if cap is None:
            print("❌ No working camera found")
            return False
        
        # Test different resolutions
        resolutions = [(640, 480), (480, 360), (320, 240)]
        
        for width, height in resolutions:
            print(f"\nTesting {width}x{height}:")
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            
            ret, frame = cap.read()
            if ret and frame is not None:
                actual_shape = frame.shape
                print(f"  ✅ Success: {actual_shape[1]}x{actual_shape[0]} (requested: {width}x{height})")
            else:
                print(f"  ❌ Failed at {width}x{height}")
        
        cap.release()
        return True
        
    except Exception as e:
        print(f"❌ Camera settings test failed: {e}")
        return False

def check_system_info():
    """Check system information"""
    print("\n💻 System Information")
    print("=" * 40)
    
    import platform
    print(f"OS: {platform.system()} {platform.release()}")
    print(f"Python: {platform.python_version()}")
    
    # Check if WSL
    try:
        with open('/proc/version', 'r') as f:
            version = f.read()
            if 'microsoft' in version.lower():
                print("⚠️  WSL detected - camera access may be limited")
                print("   Consider running on native Windows if camera fails")
    except:
        pass

def suggest_fixes():
    """Suggest fixes for black screen"""
    print("\n💡 Fixes for Black Screen")
    print("=" * 40)
    
    print("1. Camera Permission Issues:")
    print("   • Check Windows camera privacy settings")
    print("   • Ensure camera isn't used by other apps")
    print("   • Try running as administrator")
    
    print("\n2. WSL Camera Issues:")
    print("   • WSL may not have camera access")
    print("   • Try running on Windows directly")
    print("   • Use Windows Terminal instead of WSL")
    
    print("\n3. Code Fixes Applied:")
    print("   • Removed DirectShow backend")
    print("   • Added camera index fallback (0-4)")
    print("   • Better error handling")
    print("   • Original resolution restored")
    
    print("\n4. Quick Test:")
    print("   • Open Windows Camera app")
    print("   • If that works, the issue is in our code")
    print("   • If that fails, it's a system issue")

def main():
    print("🚀 Camera Diagnostic Tool")
    print("=" * 50)
    
    check_system_info()
    
    working, camera_index = test_basic_camera()
    
    if working:
        print(f"\n🎉 Found working camera at index {camera_index}")
        test_camera_with_settings()
    else:
        print("\n❌ No working camera found")
        suggest_fixes()

if __name__ == "__main__":
    main()