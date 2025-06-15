# Facial Recognition System

A real-time facial recognition system built with Flask and OpenCV that can detect, recognize, and manage faces through a web interface.

## Features

- 🎥 **Real-time face detection** and recognition via webcam
- 👤 **Face registration** through web interface capture
- 📊 **Live statistics** showing detection rates and active faces
- 🔧 **Admin panel** for managing registered faces
- 📝 **Recognition logging** with confidence scores
- 🌐 **Web-based interface** accessible from any browser

## Prerequisites

- Python 3.7+
- Webcam or camera device
- Modern web browser

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
   venv\Scripts\activate
   
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
