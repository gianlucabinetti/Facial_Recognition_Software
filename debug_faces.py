#!/usr/bin/env python
"""
Debug script to test face recognition functionality
"""

import cv2
import face_recognition
import json
import sqlite3
import numpy as np

def debug_face_recognition():
    print("="*60)
    print("Face Recognition Debug Tool")
    print("="*60)
    
    # Test camera
    print("\n1. Testing camera...")
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        print("❌ Camera not accessible")
        return
    
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    print("✅ Camera OK")
    
    # Load known faces from database
    print("\n2. Loading known faces from database...")
    try:
        conn = sqlite3.connect('database/facial_recognition.db')
        c = conn.cursor()
        c.execute("SELECT name, encoding FROM faces")
        faces = c.fetchall()
        conn.close()
        
        known_face_encodings = []
        known_face_names = []
        
        for name, encoding_str in faces:
            encoding = np.array(json.loads(encoding_str))
            known_face_encodings.append(encoding)
            known_face_names.append(name)
        
        print(f"✅ Loaded {len(known_face_names)} known faces: {known_face_names}")
        
    except Exception as e:
        print(f"❌ Error loading faces: {e}")
        known_face_encodings = []
        known_face_names = []
    
    # Test face detection and recognition
    print("\n3. Testing live face detection...")
    print("Press 'q' to quit, 's' to save current frame info")
    
    frame_count = 0
    
    while True:
        ret, frame = camera.read()
        if not ret:
            print("Failed to read frame")
            break
        
        frame_count += 1
        
        # Only process every 10th frame for debug
        if frame_count % 10 == 0:
            # Convert to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Detect faces
            face_locations = face_recognition.face_locations(rgb_frame, model='hog')
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
            
            # Process each face
            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                name = "Unknown"
                confidence = 0.0
                
                if known_face_encodings:
                    matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.6)
                    if any(matches):
                        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                        best_match_index = np.argmin(face_distances)
                        if matches[best_match_index]:
                            name = known_face_names[best_match_index]
                            confidence = 1 - face_distances[best_match_index]
                
                # Draw rectangle and info
                color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                
                # Display name and confidence
                text = f"{name} ({confidence:.2f})" if confidence > 0 else name
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
                cv2.putText(frame, text, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)
                
                print(f"Detected: {name} with confidence {confidence:.3f}")
        
        # Show frame
        cv2.imshow('Face Recognition Debug', frame)
        
        # Handle keys
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            timestamp = frame_count
            cv2.imwrite(f'debug_frame_{timestamp}.jpg', frame)
            print(f"Saved debug_frame_{timestamp}.jpg")
    
    camera.release()
    cv2.destroyAllWindows()
    print("\nDebug session completed!")

if __name__ == "__main__":
    debug_face_recognition()