# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Flask-based facial recognition system designed to run on a Raspberry Pi with a Pi Camera. It performs real-time face detection and recognition against a database of known faces stored as images.

## Key Commands

### Setup and Installation
```bash
# Create/activate virtual environment
python -m venv my_project_env
source my_project_env/bin/activate  # On Windows: my_project_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Application
```bash
# Start the Flask server
python app.py
```
The application will be accessible at `http://localhost:5000` or `http://<pi-ip-address>:5000`

## Architecture

### Core Components
- **app.py**: Main Flask application handling:
  - Pi Camera initialization using Picamera2
  - Face encoding loading from `face_images/` directory
  - Video stream generation with face detection/recognition
  - Web routes for UI and video feed

### Directory Structure
- **face_images/**: Store reference images for known faces (JPEG format, named as "PersonName_1.jpeg")
- **templates/**: HTML templates for the web interface
- **database/**: SQLite database (facial_recognition.db) - currently present but not actively used in the code

### Face Recognition Flow
1. Known faces are loaded from `face_images/` at startup
2. Pi Camera captures frames at 640x480 resolution
3. Each frame is processed to detect faces and compare against known encodings
4. Recognized faces are labeled with names, unknown faces marked as "Unknown"
5. Processed frames are streamed to the web interface via MJPEG

### Key Technical Details
- Uses face_recognition library (dlib-based) for face detection and encoding
- Camera runs continuously with error handling for resilience
- Web interface uses MJPEG streaming for real-time video display
- Debug mode is enabled for development