#!/usr/bin/env python3
"""
Prepare the project for GitHub push
"""
import os
import subprocess
import shutil

def check_git_status():
    """Check if this is a git repository"""
    print("🔍 Checking Git Status")
    print("=" * 40)
    
    if os.path.exists('.git'):
        print("✅ Git repository detected")
        return True
    else:
        print("❌ Not a git repository")
        return False

def initialize_git():
    """Initialize git repository"""
    print("\n🚀 Initializing Git Repository")
    print("=" * 40)
    
    try:
        subprocess.run(['git', 'init'], check=True, capture_output=True)
        print("✅ Git repository initialized")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to initialize git: {e}")
        return False

def create_gitignore():
    """Create .gitignore file"""
    print("\n📝 Creating .gitignore")
    print("=" * 40)
    
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environments
venv/
my_project_env/
ENV/
env/
.venv/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db
desktop.ini

# Project specific
database/*.db
*.log
*.tmp
temp/

# Don't ignore sample data but ignore large files
face_images/*.jpg
face_images/*.jpeg
face_images/*.png
!face_images/.gitkeep

# Windows
*.bat
run_windows.bat
"""
    
    try:
        with open('.gitignore', 'w') as f:
            f.write(gitignore_content)
        print("✅ .gitignore created")
        return True
    except Exception as e:
        print(f"❌ Failed to create .gitignore: {e}")
        return False

def update_readme():
    """Update README with latest information"""
    print("\n📚 Updating README")
    print("=" * 40)
    
    readme_content = """# Facial Recognition System

A modern, real-time facial recognition system built with Flask, OpenCV, and face_recognition library.

## 🌟 Features

- **Real-time Face Detection**: Live video feed with face recognition
- **Face Registration**: Capture faces directly from camera or upload images
- **Modern UI**: Dark-themed, responsive interface
- **Admin Panel**: Comprehensive face management with statistics
- **Logging System**: Detailed recognition logs with filtering and export
- **Performance Optimized**: Efficient processing for smooth real-time operation

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Webcam/Camera
- Windows (recommended) or Linux

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/Facial_Recognition_Software.git
   cd Facial_Recognition_Software
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\\Scripts\\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Open your browser**
   Navigate to `http://localhost:5000`

## 🖥️ System Requirements

- **RAM**: 4GB minimum, 8GB recommended
- **CPU**: Multi-core processor recommended
- **Camera**: USB webcam or built-in camera
- **OS**: Windows 10/11 (best performance), Linux, macOS

## 📁 Project Structure

```
Facial_Recognition_Software/
├── app.py                 # Main Flask application
├── config.json           # Configuration settings
├── requirements.txt       # Python dependencies
├── templates/            # HTML templates
│   ├── index.html        # Main dashboard
│   ├── admin.html        # Face management
│   └── logs.html         # Recognition logs
├── database/             # SQLite database
├── face_images/          # Stored face images
└── static/              # CSS, JS, images
```

## ⚙️ Configuration

Edit `config.json` to customize:

- **Camera settings**: Resolution, FPS
- **Performance**: Processing frequency, quality
- **Face recognition**: Tolerance, model type
- **Logging**: Level, retention

## 🎯 Usage

### Adding Faces
1. Enter a name in the "Add New Face" section
2. Click "Capture from Camera" or upload an image
3. Ensure good lighting and only one face visible

### Managing Faces
1. Go to Admin panel (`/admin`)
2. View, rename, or delete registered faces
3. Check recognition statistics

### Viewing Logs
1. Go to Logs page (`/logs`)
2. Filter by name, confidence, or time period
3. Export data to CSV

## 🔧 Troubleshooting

### Camera Issues
- **Black screen**: Run on native Windows (not WSL)
- **Permission denied**: Check camera privacy settings
- **Poor performance**: Close other camera applications

### Performance Issues
- Reduce camera resolution in `config.json`
- Increase `process_every_n_frames` setting
- Ensure adequate CPU resources

### Face Detection Issues
- Ensure good lighting
- Position face clearly in camera
- Check minimum/maximum face size settings

## 🛠️ Technical Details

### Performance Optimizations
- Frame processing throttling
- Efficient face size filtering
- Multi-threaded camera management
- Optimized JPEG encoding

### Security Features
- Input sanitization
- SQL injection prevention
- File path validation
- Thread-safe operations

## 📊 API Endpoints

- `GET /` - Main dashboard
- `GET /admin` - Face management
- `GET /logs` - Recognition logs
- `POST /capture` - Capture face from camera
- `GET /api/stats` - Real-time statistics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [face_recognition](https://github.com/ageitgey/face_recognition) library
- [OpenCV](https://opencv.org/) for computer vision
- [Flask](https://flask.palletsprojects.com/) web framework
- [Bootstrap](https://getbootstrap.com/) for UI components

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section
2. Review console logs for errors
3. Open an issue on GitHub
4. Provide system details and error messages

---

**Note**: This system is designed for educational and legitimate security purposes. Ensure compliance with privacy laws and obtain proper consent when deploying.
"""
    
    try:
        with open('README.md', 'w') as f:
            f.write(readme_content)
        print("✅ README.md updated")
        return True
    except Exception as e:
        print(f"❌ Failed to update README: {e}")
        return False

def add_files_to_git():
    """Add files to git"""
    print("\n📦 Adding Files to Git")
    print("=" * 40)
    
    try:
        # Add all files
        subprocess.run(['git', 'add', '.'], check=True, capture_output=True)
        print("✅ Files added to git")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to add files: {e}")
        return False

def commit_changes():
    """Commit changes"""
    print("\n💾 Committing Changes")
    print("=" * 40)
    
    commit_message = """Initial commit: Complete facial recognition system

✨ Features:
- Real-time face detection and recognition
- Modern web interface with dark theme
- Admin panel for face management
- Comprehensive logging system
- Performance optimizations for smooth operation

🔧 Technical improvements:
- Thread-safe camera management
- Robust error handling
- Cross-platform compatibility
- Optimized face detection algorithms

🚀 Ready for production deployment
"""
    
    try:
        subprocess.run(['git', 'commit', '-m', commit_message], check=True, capture_output=True)
        print("✅ Changes committed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to commit: {e}")
        return False

def show_push_instructions():
    """Show instructions for pushing to GitHub"""
    print("\n🚀 GitHub Push Instructions")
    print("=" * 50)
    
    print("1. Create a new repository on GitHub:")
    print("   - Go to https://github.com/new")
    print("   - Repository name: Facial_Recognition_Software")
    print("   - Make it public or private")
    print("   - Don't initialize with README (we have one)")
    print()
    print("2. Add the remote origin:")
    print("   git remote add origin https://github.com/YOUR_USERNAME/Facial_Recognition_Software.git")
    print()
    print("3. Push to GitHub:")
    print("   git branch -M main")
    print("   git push -u origin main")
    print()
    print("4. Your repository will be available at:")
    print("   https://github.com/YOUR_USERNAME/Facial_Recognition_Software")

def main():
    print("🚀 GitHub Preparation Tool")
    print("=" * 50)
    
    success = True
    
    # Check if git is already initialized
    if not check_git_status():
        success &= initialize_git()
    
    success &= create_gitignore()
    success &= update_readme()
    
    if success:
        success &= add_files_to_git()
        success &= commit_changes()
    
    if success:
        print("\n🎉 Repository prepared successfully!")
        show_push_instructions()
    else:
        print("\n❌ Some steps failed. Please check the errors above.")

if __name__ == "__main__":
    main()