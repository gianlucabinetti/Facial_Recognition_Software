from flask import Flask, render_template, Response, request, jsonify, redirect, url_for, send_from_directory
import cv2
import face_recognition
import numpy as np
import os
import time
import sqlite3
from datetime import datetime
import base64
import json
import logging
from werkzeug.utils import secure_filename
import threading
import queue

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'face_images'

# Setup initial logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load configuration
def load_config():
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning("config.json not found, using defaults")
        return {}

config = load_config()

# Apply configuration
app.config['MAX_CONTENT_LENGTH'] = config.get('ui', {}).get('max_upload_size_mb', 16) * 1024 * 1024

# Update logging level from config
log_level = getattr(logging, config.get('logging', {}).get('level', 'INFO'))
logger.setLevel(log_level)

# Thread-safe camera manager
class CameraManager:
    def __init__(self):
        self.camera = None
        self.lock = threading.Lock()
        self.current_frame = None
        self.frame_lock = threading.Lock()
        self.is_running = False
        self.last_init_time = 0
        self.init_cooldown = 2  # seconds between reinit attempts
        self.initialize_camera()
        
    def initialize_camera(self):
        camera_config = config.get('camera', {})
        # Simple camera initialization - avoid DirectShow which can cause issues
        try:
            self.camera = cv2.VideoCapture(camera_config.get('index', 0))
            
            # Check if camera opened successfully
            if not self.camera.isOpened():
                logger.error("Failed to open camera at index 0")
                # Try alternative camera indices
                for i in range(1, 5):
                    logger.info(f"Trying camera index {i}")
                    self.camera = cv2.VideoCapture(i)
                    if self.camera is not None and self.camera.isOpened():
                        logger.info(f"Camera opened successfully with index {i}")
                        break
        except Exception as e:
            logger.error(f"Error initializing camera: {e}")
            self.camera = None
        
        if self.camera is not None and self.camera.isOpened():
            # Optimize for performance with lower resolution
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, camera_config.get('width', 640))
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, camera_config.get('height', 480))
            self.camera.set(cv2.CAP_PROP_FPS, camera_config.get('fps', 30))
            
            # Ultra-low latency settings
            self.camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            # Don't force MJPEG - let camera use default codec
            
            # Skip advanced camera settings to avoid conflicts
            # Most cameras work better with default settings
            
            logger.info("Camera initialized successfully")
        else:
            logger.error("Failed to initialize any camera")
        
    def get_frame(self):
        with self.lock:
            if self.camera is None or not self.camera.isOpened():
                # Try to reinitialize camera if enough time has passed
                current_time = time.time()
                if current_time - self.last_init_time > self.init_cooldown:
                    logger.info("Attempting to reinitialize camera...")
                    self.initialize_camera()
                    self.last_init_time = current_time
                else:
                    return False, None
            
            if self.camera is None:
                return False, None
                
            try:
                ret, frame = self.camera.read()
                if ret and frame is not None and frame.size > 0:
                    with self.frame_lock:
                        self.current_frame = frame.copy()
                    return ret, frame
                else:
                    logger.error("Failed to read valid frame from camera")
                    # Mark camera as needing reinitialization
                    if self.camera:
                        self.camera.release()
                        self.camera = None
                    return False, None
            except Exception as e:
                logger.error(f"Error reading from camera: {e}")
                # Release camera on error
                if self.camera:
                    self.camera.release()
                    self.camera = None
                return False, None
    
    def get_current_frame(self):
        with self.frame_lock:
            if self.current_frame is not None:
                try:
                    return True, self.current_frame.copy()
                except Exception as e:
                    logger.error(f"Error copying current frame: {e}")
                    return False, None
            return False, None
    
    def release(self):
        with self.lock:
            if self.camera:
                self.camera.release()
                self.camera = None

# Initialize camera manager
camera_manager = CameraManager()

# Face recognition settings
face_config = config.get('face_recognition', {})

# Load known face encodings
known_face_encodings = []
known_face_names = []

# Performance optimization variables
frame_count = 0
perf_config = config.get('performance', {})
process_every_n_frames = perf_config.get('process_every_n_frames', 3)
max_faces_per_frame = perf_config.get('max_faces_per_frame', 5)
jpeg_quality = perf_config.get('jpeg_quality', 80)
log_throttle_seconds = perf_config.get('log_throttle_seconds', 5)
last_log_time = {}  # Track last time each person was logged to prevent spam

# Global variables for real-time stats
current_faces_detected = 0
current_known_faces_active = 0

# Capture lock to prevent conflicts
capture_in_progress = False
capture_lock = threading.Lock()

def load_known_faces():
    global known_face_encodings, known_face_names
    face_images_dir = "face_images"
    if not os.path.exists(face_images_dir):
        os.makedirs(face_images_dir)
        return
    
    # Clear existing faces to reload
    known_face_encodings = []
    known_face_names = []
        
    for filename in os.listdir(face_images_dir):
        if filename.endswith((".jpg", ".jpeg", ".png")):
            # Skip debug and full frame images
            if "_debug" in filename or "_full" in filename:
                continue
                
            path = os.path.join(face_images_dir, filename)
            # Clean up the name - remove timestamps and normalize
            base_name = os.path.splitext(filename)[0]
            import re
            name = re.sub(r'_\d{8}_\d{6}$', '', base_name)
            name = name.replace('_', ' ')  # Replace underscores with spaces
            
            try:
                image = face_recognition.load_image_file(path)
                encoding = face_recognition.face_encodings(image)
                if encoding:
                    known_face_encodings.append(encoding[0])
                    known_face_names.append(name)
                    logger.info(f"Loaded face: {name}")
                else:
                    logger.warning(f"No face found in {filename} - consider deleting this file")
            except Exception as e:
                logger.error(f"Error loading {filename}: {e}")

def init_database():
    """Initialize the SQLite database"""
    conn = sqlite3.connect('database/facial_recognition.db')
    c = conn.cursor()
    
    # Create faces table
    c.execute('''CREATE TABLE IF NOT EXISTS faces
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  encoding TEXT NOT NULL,
                  image_path TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Create recognition logs table
    c.execute('''CREATE TABLE IF NOT EXISTS recognition_logs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  confidence REAL,
                  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  screenshot TEXT)''')
    
    conn.commit()
    conn.close()

def generate_frames():
    global frame_count, process_every_n_frames, current_faces_detected, current_known_faces_active
    
    # Store face locations and names between frames for smoother display
    stored_faces = []
    
    # Frame timing for consistent FPS
    target_fps = 25  # Target frame rate
    frame_time = 1.0 / target_fps
    last_frame_time = time.time()
    
    while True:
        try:
            success, frame = camera_manager.get_frame()
            if not success or frame is None:
                logger.error("Failed to read from camera - camera may not be available")
                # Create a simple error image
                error_frame = np.zeros((480, 640, 3), dtype=np.uint8)
                cv2.putText(error_frame, "Camera Error", (200, 240), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)
                cv2.putText(error_frame, "Check camera connection", (150, 280), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                frame = error_frame
            
            frame_count += 1
            
            # Process face recognition on every Nth frame
            should_process = frame_count % process_every_n_frames == 0
            
            if should_process:
                try:
                    # Resize frame for faster face recognition processing
                    resize_factor = 0.25  # Fixed resize factor
                    small_frame = cv2.resize(frame, (0, 0), fx=resize_factor, fy=resize_factor)
                    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
                    
                    # Find faces with simple parameters
                    face_locations = face_recognition.face_locations(rgb_small_frame, model='hog')
                    
                    # Debug: log face detection
                    if frame_count % 30 == 0:  # Log every 30 frames
                        logger.info(f"Face detection: found {len(face_locations)} faces, known faces: {len(known_face_encodings)}")
                    
                    # Simple face filtering - just limit number
                    if len(face_locations) > 3:  # Max 3 faces for performance
                        face_locations = face_locations[:3]
                    
                    # Clear stored faces and process new ones
                    stored_faces = []
                    
                    if face_locations:
                        if known_face_encodings:
                            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

                            # Scale back up face locations
                            scale_factor = int(1 / resize_factor)
                            face_locations = [(top*scale_factor, right*scale_factor, bottom*scale_factor, left*scale_factor) 
                                            for (top, right, bottom, left) in face_locations]

                            # Loop through each face in this frame
                            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                                matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.6)
                                name = "Unknown"
                                confidence = 0.0

                                if matches and any(matches):
                                    face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                                    best_match_index = np.argmin(face_distances)
                                    if matches[best_match_index]:
                                        name = known_face_names[best_match_index]
                                        confidence = 1 - face_distances[best_match_index]
                                        
                                        # Only log high-confidence recognitions
                                        if confidence > 0.65:
                                            log_recognition_throttled(name, confidence)

                                # Store face info for drawing
                                stored_faces.append({
                                    'location': (top, right, bottom, left),
                                    'name': name,
                                    'confidence': confidence
                                })
                        else:
                            # Just detect faces without recognition if no known faces
                            scale_factor = int(1 / resize_factor)
                            for (top, right, bottom, left) in face_locations:
                                scaled_location = (top*scale_factor, right*scale_factor, 
                                               bottom*scale_factor, left*scale_factor)
                                stored_faces.append({
                                    'location': scaled_location,
                                    'name': 'Unknown',
                                    'confidence': 0.0
                                })
                        
                except Exception as face_error:
                    logger.error(f"Error in face recognition processing: {str(face_error)}")
                    stored_faces = []

            # Update global stats based on current frame - only count valid detections
            valid_faces = [face for face in stored_faces if face.get('confidence', 0) > 0.4 or face['name'] == 'Unknown']
            current_faces_detected = len(valid_faces)
            current_known_faces_active = len([face for face in valid_faces if face['name'] != 'Unknown' and face.get('confidence', 0) > 0.5])

            # Draw all stored faces on the current frame
            for face_info in stored_faces:
                top, right, bottom, left = face_info['location']
                name = face_info['name']
                confidence = face_info['confidence']
                
                # Choose color based on recognition
                if name != "Unknown":
                    color = (0, 255, 0)  # Green for known faces
                else:
                    color = (0, 0, 255)  # Red for unknown faces
                
                # Draw rectangle and name
                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
                
                # Format text
                if confidence > 0:
                    text = f"{name} ({confidence:.2f})"
                else:
                    text = name
                
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, text, (left + 6, bottom - 6), font, 0.6, (255, 255, 255), 1)

            # Convert frame to jpg with fast encoding
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality]
            ret, buffer = cv2.imencode('.jpg', frame, encode_param)
            if not ret:
                logger.error("Failed to encode frame")
                continue
                
            frame = buffer.tobytes()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            
            # Frame rate limiting for smooth playback
            current_time = time.time()
            elapsed = current_time - last_frame_time
            if elapsed < frame_time:
                time.sleep(frame_time - elapsed)
            last_frame_time = time.time()

        except Exception as e:
            logger.error(f"Error in generate_frames: {str(e)}")
            continue

def log_recognition_throttled(name, confidence):
    """Log face recognition event to database with throttling to prevent spam"""
    global last_log_time
    
    current_time = time.time()
    
    # Only log if we haven't logged this person recently (more aggressive throttling)
    throttle_time = max(log_throttle_seconds, 3)  # Minimum 3 seconds between logs
    if name not in last_log_time or (current_time - last_log_time[name]) > throttle_time:
        try:
            conn = sqlite3.connect('database/facial_recognition.db', timeout=1.0)
            c = conn.cursor()
            c.execute("INSERT INTO recognition_logs (name, confidence) VALUES (?, ?)", 
                      (name, confidence))
            conn.commit()
            conn.close()
            last_log_time[name] = current_time
            logger.debug(f"Logged recognition: {name} ({confidence:.2f})")
        except Exception as e:
            logger.error(f"Error logging recognition: {str(e)}")

def log_recognition(name, confidence):
    """Legacy function - redirect to throttled version"""
    log_recognition_throttled(name, confidence)

def load_faces_from_db():
    """Load face encodings from database"""
    try:
        conn = sqlite3.connect('database/facial_recognition.db')
        c = conn.cursor()
        c.execute("SELECT name, encoding FROM faces")
        for row in c.fetchall():
            name, encoding_str = row
            encoding = np.array(json.loads(encoding_str))
            known_face_encodings.append(encoding)
            known_face_names.append(name)
        conn.close()
        logger.info(f"Loaded {len(known_face_names)} faces from database")
    except Exception as e:
        logger.error(f"Error loading faces from database: {str(e)}")
    
    # Clean up known faces list to remove duplicates
    unique_names = set()
    clean_encodings = []
    clean_names = []
    
    for encoding, name in zip(known_face_encodings, known_face_names):
        if name not in unique_names:
            unique_names.add(name)
            clean_encodings.append(encoding)
            clean_names.append(name)
    
    known_face_encodings[:] = clean_encodings
    known_face_names[:] = clean_names
    logger.info(f"Total unique faces loaded: {len(known_face_names)}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
def admin():
    """Admin page for managing faces"""
    try:
        conn = sqlite3.connect('database/facial_recognition.db', timeout=2.0)
        c = conn.cursor()
        c.execute("SELECT id, name, image_path, created_at FROM faces ORDER BY created_at DESC")
        faces = c.fetchall()
        
        # Get recognition stats for each face
        face_stats = {}
        for face in faces:
            face_id, name = face[0], face[1]
            c.execute("""SELECT COUNT(*), AVG(confidence), MAX(timestamp) 
                        FROM recognition_logs 
                        WHERE name = ? AND timestamp > datetime('now', '-7 days')""", (name,))
            stats = c.fetchone()
            face_stats[face_id] = {
                'recognitions': stats[0] or 0,
                'avg_confidence': stats[1] or 0,
                'last_seen': stats[2] or 'Never'
            }
        
        conn.close()
        
        return render_template('admin.html', faces=faces, face_stats=face_stats)
        
    except Exception as e:
        logger.error(f"Error loading admin page: {str(e)}")
        return render_template('admin.html', faces=[], face_stats={}, error=str(e))

@app.route('/logs')
def logs():
    """View recognition logs"""
    conn = sqlite3.connect('database/facial_recognition.db')
    c = conn.cursor()
    c.execute("""SELECT name, confidence, timestamp 
                 FROM recognition_logs 
                 ORDER BY timestamp DESC 
                 LIMIT 100""")
    logs = c.fetchall()
    conn.close()
    return render_template('logs.html', logs=logs)

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/stats')
def get_stats():
    """Get current statistics"""
    try:
        conn = sqlite3.connect('database/facial_recognition.db', timeout=2.0)
        c = conn.cursor()
        
        # Get total known faces
        c.execute("SELECT COUNT(DISTINCT name) FROM faces")
        result = c.fetchone()
        known_faces = result[0] if result else 0
        
        # Use real-time face detection data from the video stream
        global current_faces_detected
        faces_currently_detected = current_faces_detected
        
        # Calculate recognition rate from last hour (lowered threshold)
        c.execute("""SELECT 
                     COUNT(CASE WHEN confidence > 0.5 THEN 1 END) as high_conf,
                     COUNT(*) as total
                     FROM recognition_logs 
                     WHERE timestamp > datetime('now', '-1 hour')""")
        result = c.fetchone()
        
        if result and result[1] > 0:
            recognition_rate = (result[0] * 100.0) / result[1]
        else:
            recognition_rate = 0
        
        conn.close()
        
        # Ensure all values are numbers and not None
        return jsonify({
            'known_faces': int(known_faces or 0),
            'faces_detected': int(faces_currently_detected or 0),
            'recognition_rate': round(float(recognition_rate or 0), 1)
        })
        
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        return jsonify({
            'known_faces': 0,
            'faces_detected': 0,
            'recognition_rate': 0.0
        }), 200

@app.route('/api/recent_detections')
def get_recent_detections():
    """Get recent face detections for live updates"""
    try:
        conn = sqlite3.connect('database/facial_recognition.db', timeout=2.0)
        c = conn.cursor()
        
        # Get recent detections (last 30 seconds)
        c.execute("""SELECT name, confidence, timestamp 
                     FROM recognition_logs 
                     WHERE timestamp > datetime('now', '-30 seconds')
                     ORDER BY timestamp DESC 
                     LIMIT 10""")
        recent = c.fetchall()
        
        # Get current active faces (last 10 seconds) with better confidence filtering
        c.execute("""SELECT name, MAX(confidence) as max_conf, COUNT(*) as count
                     FROM recognition_logs 
                     WHERE timestamp > datetime('now', '-10 seconds')
                     AND confidence > 0.6
                     GROUP BY name
                     ORDER BY MAX(confidence) DESC""")
        active = c.fetchall()
        
        # Use real-time data if available
        global current_known_faces_active
        if current_known_faces_active > len(active):
            # Supplement with current real-time data
            active = active[:current_known_faces_active]
        
        conn.close()
        
        return jsonify({
            'recent_detections': recent,
            'active_faces': active,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting recent detections: {str(e)}")
        return jsonify({
            'recent_detections': [],
            'active_faces': [],
            'timestamp': datetime.now().isoformat()
        }), 200

@app.route('/api/recent_logs')
def get_recent_logs():
    """Get recent logs for auto-refresh"""
    try:
        conn = sqlite3.connect('database/facial_recognition.db', timeout=2.0)
        c = conn.cursor()
        c.execute("""SELECT name, confidence, timestamp 
                     FROM recognition_logs 
                     ORDER BY timestamp DESC 
                     LIMIT 50""")
        logs = c.fetchall()
        conn.close()
        
        # Convert to format expected by frontend
        formatted_logs = []
        for log in logs:
            formatted_logs.append({
                'name': log[0],
                'confidence': log[1],
                'timestamp': log[2],
                'timestampDate': log[2]
            })
        
        return jsonify({'logs': formatted_logs})
        
    except Exception as e:
        logger.error(f"Error getting recent logs: {str(e)}")
        return jsonify({'logs': []}), 200

@app.route('/<path:filename>')
def serve_static_files(filename):
    """Serve face images and other static files"""
    try:
        logger.info(f"Requesting file: {filename}")
        # Serve from face_images directory
        if filename.startswith('face_images/'):
            file_path = os.path.join('.', filename)
            if os.path.exists(file_path):
                logger.info(f"Serving file: {file_path}")
                return send_from_directory('.', filename)
            else:
                logger.error(f"File not found: {file_path}")
        return send_from_directory('.', filename)
    except Exception as e:
        logger.error(f"Error serving file {filename}: {e}")
        return "File not found", 404

@app.route('/api/admin_stats')
def get_admin_stats():
    """Get admin dashboard statistics"""
    try:
        conn = sqlite3.connect('database/facial_recognition.db', timeout=2.0)
        c = conn.cursor()
        
        # Active today (recognized in last 24 hours)
        c.execute("""SELECT COUNT(DISTINCT name) FROM recognition_logs 
                     WHERE timestamp > datetime('now', '-1 day')""")
        active_today = c.fetchone()[0] or 0
        
        # Total recognitions
        c.execute("SELECT COUNT(*) FROM recognition_logs")
        total_recognitions = c.fetchone()[0] or 0
        
        # Average confidence
        c.execute("SELECT AVG(confidence) FROM recognition_logs WHERE confidence > 0")
        avg_confidence = c.fetchone()[0] or 0
        
        conn.close()
        
        return jsonify({
            'active_today': active_today,
            'total_recognitions': total_recognitions,
            'avg_confidence': (avg_confidence * 100) if avg_confidence else 0
        })
        
    except Exception as e:
        logger.error(f"Error getting admin stats: {str(e)}")
        return jsonify({
            'active_today': 0,
            'total_recognitions': 0,
            'avg_confidence': 0
        }), 200

@app.route('/rename_face/<int:face_id>', methods=['POST'])
def rename_face(face_id):
    """Rename a face"""
    try:
        data = request.json
        new_name = data.get('name', '').strip()
        
        if not new_name:
            return jsonify({'success': False, 'error': 'Name is required'}), 400
        
        conn = sqlite3.connect('database/facial_recognition.db', timeout=5.0)
        c = conn.cursor()
        
        # Get old name
        c.execute("SELECT name FROM faces WHERE id = ?", (face_id,))
        result = c.fetchone()
        if not result:
            return jsonify({'success': False, 'error': 'Face not found'}), 404
        
        old_name = result[0]
        
        # Update face name
        c.execute("UPDATE faces SET name = ? WHERE id = ?", (new_name, face_id))
        
        # Update recognition logs
        c.execute("UPDATE recognition_logs SET name = ? WHERE name = ?", (new_name, old_name))
        
        conn.commit()
        conn.close()
        
        # Update known faces in memory
        global known_face_names
        for i, name in enumerate(known_face_names):
            if name == old_name:
                known_face_names[i] = new_name
        
        return jsonify({'success': True, 'message': f'Renamed {old_name} to {new_name}'})
        
    except Exception as e:
        logger.error(f"Error renaming face: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/bulk_delete_faces', methods=['POST'])
def bulk_delete_faces():
    """Delete multiple faces"""
    try:
        data = request.json
        face_ids = data.get('face_ids', [])
        
        if not face_ids:
            return jsonify({'success': False, 'error': 'No faces selected'}), 400
        
        conn = sqlite3.connect('database/facial_recognition.db', timeout=5.0)
        c = conn.cursor()
        
        deleted_names = []
        
        for face_id in face_ids:
            # Get face info
            c.execute("SELECT name, image_path FROM faces WHERE id = ?", (face_id,))
            result = c.fetchone()
            
            if result:
                name, image_path = result
                deleted_names.append(name)
                
                # Delete image file
                if image_path and os.path.exists(image_path):
                    os.remove(image_path)
                
                # Delete from database
                c.execute("DELETE FROM faces WHERE id = ?", (face_id,))
                c.execute("DELETE FROM recognition_logs WHERE name = ?", (name,))
        
        conn.commit()
        conn.close()
        
        # Update known faces in memory
        global known_face_encodings, known_face_names
        new_encodings = []
        new_names = []
        
        for i, name in enumerate(known_face_names):
            if name not in deleted_names:
                new_encodings.append(known_face_encodings[i])
                new_names.append(name)
        
        known_face_encodings = new_encodings
        known_face_names = new_names
        
        return jsonify({'success': True, 'message': f'Deleted {len(face_ids)} faces'})
        
    except Exception as e:
        logger.error(f"Error bulk deleting faces: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/capture', methods=['POST'])
def capture_face():
    """Capture a face from the current video frame"""
    global capture_in_progress, capture_lock
    
    # Check if request has JSON data
    if not request.is_json:
        logger.error("Request is not JSON")
        return jsonify({'success': False, 'error': 'Invalid request format'}), 400
    
    data = request.get_json()
    if not data:
        logger.error("No JSON data received")
        return jsonify({'success': False, 'error': 'No data received'}), 400
    
    name = data.get('name', '').strip()
    logger.info(f"Capture request received for name: '{name}'")
    
    if not name:
        logger.warning("Empty name provided")
        return jsonify({'success': False, 'error': 'Name is required'}), 400
    
    # Check if another capture is in progress
    with capture_lock:
        if capture_in_progress:
            logger.warning("Capture already in progress")
            return jsonify({'success': False, 'error': 'Another capture is in progress. Please wait.'}), 429
        
        capture_in_progress = True
        logger.info("Capture lock acquired")
    
    try:
        # Sanitize name for filename
        safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        if not safe_name:
            return jsonify({'success': False, 'error': 'Invalid name format'}), 400
        
        # Simple frame capture to avoid camera conflicts
        logger.info("Attempting frame capture for face registration")
        
        # Try current frame first (from video stream)
        success, frame = camera_manager.get_current_frame()
        if not success or frame is None:
            # If no current frame, get a fresh one
            success, frame = camera_manager.get_frame()
        
        if not success or frame is None:
            return jsonify({'success': False, 'error': 'Failed to capture frame from camera'}), 500
        
        # Basic frame validation
        if frame.size == 0:
            logger.error("Captured frame is empty")
            return jsonify({'success': False, 'error': 'Captured frame is empty'}), 500
        
        # Create a safe copy of the frame
        try:
            frame_copy = frame.copy()
            logger.info(f"Frame copied successfully, shape: {frame_copy.shape}")
        except Exception as e:
            logger.error(f"Failed to copy frame: {e}")
            return jsonify({'success': False, 'error': 'Failed to process captured frame'}), 500
        
        # Find faces in the frame with error handling
        try:
            rgb_frame = cv2.cvtColor(frame_copy, cv2.COLOR_BGR2RGB)
            logger.info("Frame converted to RGB successfully")
        except Exception as e:
            logger.error(f"Failed to convert frame to RGB: {e}")
            return jsonify({'success': False, 'error': 'Failed to process frame format'}), 500
        
        # Use simpler face detection for capture with timeout protection
        try:
            logger.info("Starting face detection...")
            face_locations = face_recognition.face_locations(rgb_frame, model='hog', number_of_times_to_upsample=0)
            logger.info(f"Face detection completed, found {len(face_locations)} faces")
        except Exception as e:
            logger.error(f"Face detection failed: {e}")
            return jsonify({'success': False, 'error': 'Face detection failed. Please try again.'}), 500
        
        if not face_locations:
            logger.warning("No faces detected in frame")
            return jsonify({'success': False, 'error': 'No face detected. Please position your face clearly in the camera and ensure good lighting.'}), 400
        
        if len(face_locations) > 1:
            logger.warning(f"Multiple faces detected: {len(face_locations)}")
            return jsonify({'success': False, 'error': f'Multiple faces detected ({len(face_locations)}). Please ensure only one face is visible.'}), 400
        
        # Get face encoding
        try:
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
            if not face_encodings:
                return jsonify({'success': False, 'error': 'Could not encode face. Please try again with better lighting.'}), 500
            
            face_encoding = face_encodings[0]
        except Exception as encoding_error:
            logger.error(f"Face encoding error: {encoding_error}")
            return jsonify({'success': False, 'error': 'Face encoding failed. Please try again.'}), 500
        
        # Create face_images directory if it doesn't exist
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        # Save face image - ensure Windows compatibility
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{safe_name}_{timestamp}.jpg"
        # Use forward slashes for path compatibility
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename).replace('\\', '/')
        
        # Crop face from frame with more padding for better visibility
        top, right, bottom, left = face_locations[0]
        # Increase padding for better face capture
        padding = 50
        top = max(0, top - padding)
        bottom = min(frame_copy.shape[0], bottom + padding)
        left = max(0, left - padding)
        right = min(frame_copy.shape[1], right + padding)
        
        face_image = frame_copy[top:bottom, left:right]
        
        # Validate the cropped face image
        if face_image.size == 0 or face_image.shape[0] < 20 or face_image.shape[1] < 20:
            logger.error(f"Face crop too small: {face_image.shape}")
            return jsonify({'success': False, 'error': 'Face crop too small. Please get closer to camera.'}), 500
        
        # Verify face is still detectable in cropped image
        rgb_face = cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB)
        face_check = face_recognition.face_locations(rgb_face)
        if not face_check:
            logger.warning("Face not detectable in cropped image, using larger padding")
            # Try with larger padding
            padding = 100
            top = max(0, face_locations[0][0] - padding)
            bottom = min(frame_copy.shape[0], face_locations[0][2] + padding)
            left = max(0, face_locations[0][3] - padding)
            right = min(frame_copy.shape[1], face_locations[0][1] + padding)
            face_image = frame_copy[top:bottom, left:right]
        
        # Draw rectangle on full frame for debugging
        debug_frame = frame_copy.copy()
        cv2.rectangle(debug_frame, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.putText(debug_frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        
        # Save image with error handling and debugging
        try:
            # Ensure the face image is valid
            if face_image.size == 0:
                return jsonify({'success': False, 'error': 'Invalid face crop - face too close to edge'}), 500
            
            # Save with explicit parameters
            success_save = cv2.imwrite(filepath, face_image, [cv2.IMWRITE_JPEG_QUALITY, 95])
            
            if not success_save:
                logger.error(f"cv2.imwrite returned False for {filepath}")
                return jsonify({'success': False, 'error': 'OpenCV failed to write image'}), 500
                
            if not os.path.exists(filepath):
                logger.error(f"File not found after save: {filepath}")
                return jsonify({'success': False, 'error': 'Image file not created'}), 500
                
            # Verify file size
            file_size = os.path.getsize(filepath)
            if file_size == 0:
                logger.error(f"Empty file created: {filepath}")
                os.remove(filepath)
                return jsonify({'success': False, 'error': 'Empty image file created'}), 500
                
            logger.info(f"Successfully saved face image: {filepath} ({file_size} bytes)")
            
            # Save debug frame with bounding box
            debug_filename = f"{safe_name}_{timestamp}_debug.jpg"
            debug_path = os.path.join(app.config['UPLOAD_FOLDER'], debug_filename)
            cv2.imwrite(debug_path, debug_frame)
            logger.info(f"Saved debug frame to: {debug_path}")
            
        except Exception as save_error:
            logger.error(f"Image save error: {save_error}, filepath: {filepath}")
            return jsonify({'success': False, 'error': f'Failed to save image: {str(save_error)}'}), 500
        
        # Save to database with error handling
        conn = None
        try:
            logger.info("Connecting to database...")
            conn = sqlite3.connect('database/facial_recognition.db', timeout=10.0)
            c = conn.cursor()
            
            # Convert encoding to string safely
            try:
                encoding_str = json.dumps(face_encoding.tolist())
                logger.info("Face encoding serialized successfully")
            except Exception as e:
                logger.error(f"Failed to serialize face encoding: {e}")
                raise ValueError("Failed to process face encoding")
            
            # Insert into database
            logger.info("Inserting face into database...")
            c.execute("INSERT INTO faces (name, encoding, image_path) VALUES (?, ?, ?)",
                      (name, encoding_str, filepath))
            conn.commit()
            logger.info("Database insert successful")
            
        except sqlite3.Error as e:
            logger.error(f"Database error: {e}")
            if conn:
                conn.rollback()
            # Clean up image file if database save failed
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                    logger.info("Cleaned up image file after database error")
                except:
                    pass
            return jsonify({'success': False, 'error': f'Database error: {str(e)}'}), 500
        except Exception as e:
            logger.error(f"Unexpected error during database save: {e}")
            if conn:
                conn.rollback()
            # Clean up image file
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                except:
                    pass
            return jsonify({'success': False, 'error': f'Failed to save to database: {str(e)}'}), 500
        finally:
            if conn:
                conn.close()
                logger.info("Database connection closed")
        
        # Update known faces in memory safely
        try:
            global known_face_encodings, known_face_names
            known_face_encodings.append(face_encoding)
            known_face_names.append(name)
            logger.info(f"Updated in-memory face data for {name}")
        except Exception as e:
            logger.warning(f"Failed to update in-memory data: {e}")
            # This is not critical, face is saved to database
        
        logger.info(f"Successfully completed face capture for {name}")
        
        # Reload faces to include the new one
        load_known_faces()
        
        # Return the image path so it can be displayed
        response = jsonify({
            'success': True, 
            'message': f'Face captured and saved for {name}!',
            'image_path': filepath,
            'face_id': conn.lastrowid if conn else None
        })
        
        # Add CORS headers to prevent network errors
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
        
        return response
        
    except Exception as e:
        logger.error(f"Unexpected error in capture_face: {str(e)}")
        return jsonify({'success': False, 'error': f'Capture failed: {str(e)}'}), 500
        
    finally:
        # Always release the capture lock
        with capture_lock:
            capture_in_progress = False
            logger.info("Capture lock released")

@app.route('/test_image/<filename>')
def test_image(filename):
    """Test route to display captured images"""
    try:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(filepath):
            return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
        else:
            return f"File not found: {filepath}", 404
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route('/restart_camera', methods=['POST'])
def restart_camera():
    """Restart camera connection to fix black screen issues"""
    try:
        global camera_manager
        logger.info("Restarting camera...")
        camera_manager.release()
        time.sleep(1)
        camera_manager = CameraManager()
        time.sleep(0.5)
        
        # Test if camera works
        success, frame = camera_manager.get_frame()
        if success and frame is not None:
            return jsonify({'success': True, 'message': 'Camera restarted successfully'})
        else:
            return jsonify({'success': False, 'error': 'Camera restart failed'}), 500
    except Exception as e:
        logger.error(f"Error restarting camera: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/delete_face/<int:face_id>', methods=['POST'])
def delete_face(face_id):
    """Delete a face from the database"""
    try:
        conn = sqlite3.connect('database/facial_recognition.db')
        c = conn.cursor()
        
        # Get image path before deleting
        c.execute("SELECT image_path FROM faces WHERE id = ?", (face_id,))
        result = c.fetchone()
        
        if result and result[0] and os.path.exists(result[0]):
            os.remove(result[0])
        
        c.execute("DELETE FROM faces WHERE id = ?", (face_id,))
        conn.commit()
        conn.close()
        
        # Reload faces
        global known_face_encodings, known_face_names
        known_face_encodings = []
        known_face_names = []
        load_known_faces()
        load_faces_from_db()
        
        return redirect(url_for('admin'))
        
    except Exception as e:
        logger.error(f"Error deleting face: {str(e)}")
        return redirect(url_for('admin'))

@app.route('/upload_face', methods=['POST'])
def upload_face():
    """Upload a face image"""
    try:
        if 'face_image' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'}), 400
        
        file = request.files['face_image']
        name = request.form.get('name', '').strip()
        
        if not name:
            return jsonify({'success': False, 'error': 'Name is required'}), 400
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        # Ensure upload folder exists
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        # Save file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        # Sanitize the filename properly
        safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        original_filename = secure_filename(file.filename)
        filename = f"{safe_name}_{timestamp}_{original_filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        try:
            file.save(filepath)
            if not os.path.exists(filepath):
                return jsonify({'success': False, 'error': 'Failed to save uploaded file'}), 500
        except Exception as e:
            logger.error(f"Failed to save uploaded file: {e}")
            return jsonify({'success': False, 'error': f'Failed to save file: {str(e)}'}), 500
        
        # Load image and get face encoding
        image = face_recognition.load_image_file(filepath)
        face_encodings = face_recognition.face_encodings(image)
        
        if not face_encodings:
            os.remove(filepath)
            return jsonify({'success': False, 'error': 'No face found in image'}), 400
        
        if len(face_encodings) > 1:
            os.remove(filepath)
            return jsonify({'success': False, 'error': 'Multiple faces found in image'}), 400
        
        # Save to database
        face_encoding = face_encodings[0]
        conn = sqlite3.connect('database/facial_recognition.db')
        c = conn.cursor()
        encoding_str = json.dumps(face_encoding.tolist())
        c.execute("INSERT INTO faces (name, encoding, image_path) VALUES (?, ?, ?)",
                  (name, encoding_str, filepath))
        conn.commit()
        conn.close()
        
        # Update known faces
        known_face_encodings.append(face_encoding)
        known_face_names.append(name)
        
        return redirect(url_for('admin'))
        
    except Exception as e:
        logger.error(f"Error uploading face: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    try:
        init_database()
        logger.info("Loading known faces from files...")
        load_known_faces()
        logger.info("Loading faces from database...")
        load_faces_from_db()
        print("\n" + "="*50)
        print("🎥 Face Recognition System Started!")
        print("📱 Open: http://localhost:5000")
        print("👥 Features: Live detection, face capture, logging")
        print("⚡ Press Ctrl+C to stop")
        print("="*50 + "\n")
        app.run(host='0.0.0.0', port=5000, debug=True)
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down Face Recognition System...")
        camera_manager.release()
        print("✅ Camera released. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error starting application: {e}")
        camera_manager.release() 