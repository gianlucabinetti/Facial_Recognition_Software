#!/usr/bin/env python
"""
Performance test script for Face Recognition System
Tests the application with different settings to find optimal performance
"""

import time
import cv2
import face_recognition
import json
import os

def test_performance():
    print("="*60)
    print("Face Recognition System - Performance Test")
    print("="*60)
    
    # Test camera access
    print("\n1. Testing camera access...")
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        print("❌ Could not open camera")
        return
    
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    print("✅ Camera access OK")
    
    # Test frame capture rate
    print("\n2. Testing frame capture rate...")
    start_time = time.time()
    frame_count = 0
    
    for i in range(30):  # Test 30 frames
        ret, frame = camera.read()
        if ret:
            frame_count += 1
    
    duration = time.time() - start_time
    fps = frame_count / duration
    print(f"✅ Camera FPS: {fps:.1f}")
    
    # Test face detection performance
    print("\n3. Testing face detection performance...")
    
    # Test with different resize factors
    resize_factors = [0.25, 0.4, 0.5]
    
    for resize_factor in resize_factors:
        print(f"\nTesting resize factor: {resize_factor}")
        
        start_time = time.time()
        detection_count = 0
        
        for i in range(10):  # Test 10 frames
            ret, frame = camera.read()
            if not ret:
                continue
                
            # Resize frame
            small_frame = cv2.resize(frame, (0, 0), fx=resize_factor, fy=resize_factor)
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
            
            # Detect faces
            face_locations = face_recognition.face_locations(rgb_small_frame, model='hog')
            detection_count += len(face_locations)
        
        duration = time.time() - start_time
        avg_time = duration / 10
        print(f"  Average time per frame: {avg_time:.3f}s")
        print(f"  Faces detected: {detection_count}")
        print(f"  Effective FPS: {1/avg_time:.1f}")
    
    camera.release()
    
    # Recommend settings
    print("\n" + "="*60)
    print("RECOMMENDATIONS:")
    print("="*60)
    
    if fps > 20:
        print("✅ Camera performance is good")
        rec_resize = 0.4
        rec_frames = 2
    elif fps > 15:
        print("⚠️  Camera performance is moderate")
        rec_resize = 0.5
        rec_frames = 3
    else:
        print("❌ Camera performance is poor")
        rec_resize = 0.5
        rec_frames = 5
    
    print(f"\nRecommended settings:")
    print(f"- resize_factor: {rec_resize}")
    print(f"- process_every_n_frames: {rec_frames}")
    print(f"- jpeg_quality: 70-80")
    
    # Update config.json with recommendations
    config_file = "config.json"
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            config['face_recognition']['resize_factor'] = rec_resize
            config['performance']['process_every_n_frames'] = rec_frames
            config['performance']['jpeg_quality'] = 75
            config['camera']['fps'] = min(15, int(fps))
            
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=4)
            
            print(f"\n✅ Updated {config_file} with recommended settings")
        except Exception as e:
            print(f"\n❌ Could not update config.json: {e}")
    
    print("\nRun 'python app.py' to test the optimized settings!")

if __name__ == "__main__":
    test_performance()