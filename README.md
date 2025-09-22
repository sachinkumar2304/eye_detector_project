# Eye-Tracking Virtual Keyboard 🖥️👁️

A computer vision-based virtual keyboard that allows users to type using eye movements and blinks. This innovative application uses facial landmark detection to track eye movements and blinks, enabling hands-free text input.

## 🎯 Overview

This project implements a complete eye-tracking virtual keyboard system that:
- **Detects facial landmarks** using MediaPipe Face Mesh
- **Tracks eye blinks** for character selection
- **Monitors nose position** for cursor movement
- **Provides real-time virtual keyboard** interface
- **Displays typed text** with live feedback

## ✨ Features

- **Real-time face detection** and landmark tracking
- **Eye blink detection** for character selection
- **Smooth cursor control** using nose position tracking
- **Virtual QWERTY keyboard** with visual feedback
- **Live camera feed** with overlay information
- **Text input and display** with character limits
- **Special keys support** (Space, Delete, Shift, Enter)
- **Movement stabilization** to prevent jittery cursor movement
- **Configurable sensitivity** and timing parameters

## 🛠️ Technology Stack

- **Python 3.x**
- **OpenCV** - Computer vision and camera handling
- **MediaPipe** - Facial landmark detection
- **NumPy** - Mathematical operations and arrays

## 📋 Prerequisites

Before running this application, ensure you have:

1. **Python 3.7 or higher** installed
2. **Webcam** or camera device
3. **Well-lit environment** for optimal face detection
4. **Stable head position** during use

## 🚀 Installation

### Step 1: Clone or Download the Project

```bash
# If using git (recommended)
git clone <your-repository-url>
cd eye_detector1

# Or download and extract the files to a folder
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv eye_keyboard_env

# Activate virtual environment
# On Windows:
eye_keyboard_env\Scripts\activate
# On macOS/Linux:
source eye_keyboard_env/bin/activate
```

### Step 3: Install Required Dependencies

```bash
pip install opencv-python
pip install mediapipe
pip install numpy
```

**Alternative: Install all at once**
```bash
pip install opencv-python mediapipe numpy
```

## 🎮 How to Run

### Basic Usage

1. **Navigate to the project directory:**
   ```bash
   cd c:/eye_detector1
   ```

2. **Activate virtual environment (if using one):**
   ```bash
   eye_keyboard_env\Scripts\activate
   ```

3. **Run the application:**
   ```bash
   python eye_detector.py
   ```

### What Happens Next

1. The application will start and attempt to access your camera
2. Two windows will open:
   - **"Camera"** - Live camera feed with facial landmark detection
   - **"Keyboard"** - Virtual keyboard interface
3. The system will automatically detect your face and start tracking

## 📖 How to Use

### Initial Setup
1. **Position yourself** approximately 2-3 feet from the camera
2. **Ensure good lighting** - avoid harsh shadows on your face
3. **Keep your head relatively stable** during typing
4. **Look directly at the camera** initially for face detection

### Cursor Control
- **Move your nose slightly** to control the cursor position
- **Left/Right movement** - Move nose horizontally
- **Up/Down movement** - Move nose vertically
- **Cursor sensitivity** can be adjusted in the code (`threshold` variable)

### Character Selection
- **Navigate** to the desired character using nose movements
- **Blink firmly** to select the highlighted character
- **Selected character** will be added to your text

### Special Keys
- **Space** - Inserts a space character
- **Delete** - Removes the last character
- **Shift** - Toggles between uppercase/lowercase (affects next character only)
- **Enter** - Inserts a newline character

### Text Display
- **Current selection** is highlighted in cyan/green
- **Typed text** appears at the bottom of the keyboard window
- **Recent text** is shown in the camera feed overlay

## ⚙️ Configuration

You can modify the following parameters in `eye_detector.py`:

```python
# Movement sensitivity (adjust based on your setup)
threshold = 0.04  # Lower = more sensitive

# Movement delay (prevents rapid cursor jumping)
move_delay = 0.5  # Seconds between movements

# Blink detection parameters
min_blink_duration = 0.3  # Minimum blink time (seconds)
max_blink_duration = 1.5  # Maximum blink time (seconds)

# Camera resolution
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
```

## 🛠️ Troubleshooting

### Common Issues

**1. Camera not opening**
```bash
# Check if camera is available
python -c "import cv2; print(cv2.VideoCapture(0).isOpened())"
```
- Ensure no other application is using the camera
- Try restarting your computer
- Check camera permissions in your OS settings

**2. Face not detected**
- Ensure adequate lighting
- Position yourself directly in front of the camera
- Check that your face is clearly visible
- Try adjusting `min_detection_confidence` in the code

**3. Cursor not responding**
- Check camera resolution and lighting
- Adjust `threshold` value (try 0.02-0.06 range)
- Ensure stable head position
- Try reducing `move_delay` if cursor feels sluggish

**4. Blink detection issues**
- Ensure you're blinking firmly enough
- Check lighting conditions
- Adjust `min_blink_duration` and `max_blink_duration`
- Try different eye aspect ratio thresholds

**5. Poor performance**
- Close other applications
- Reduce camera resolution in the code
- Ensure adequate system resources
- Try using a different camera if available

### Performance Tips

- **Use in well-lit environments** for best detection
- **Avoid direct light sources** behind you
- **Keep consistent distance** from camera
- **Minimize background movement** for better tracking
- **Use a high-quality webcam** for better results

## 📝 Usage Examples

### Basic Text Input
1. Start the application
2. Look at letters to move cursor
3. Blink to select letters
4. Type simple messages like "HELLO WORLD"

### Writing Longer Text
1. Use nose movements to navigate efficiently
2. Use "Space" key for word separation
3. Use "Enter" for new lines
4. Use "Delete" to correct mistakes

### Special Characters
- Navigate to "Shift" and blink to toggle case
- Use "Space" for word separation
- Use "Enter" for line breaks

## 🔧 Development

### Project Structure
```
eye_detector1/
├── eye_detector.py  # Main application file
└── README.md       # This documentation
```

### Key Components

1. **Face Detection**: Uses MediaPipe FaceMesh for 468 facial landmarks
2. **Eye Tracking**: Calculates eye aspect ratio for blink detection
3. **Cursor Control**: Tracks nose position for navigation
4. **UI Rendering**: OpenCV for camera feed and keyboard display
5. **Text Management**: Handles input, display, and special key functions

### Extending the Project

**Adding new features:**
- Implement predictive text
- Add more keyboard layouts
- Support for special characters
- Voice feedback integration
- Save/load text functionality

**Performance improvements:**
- Multi-threading for better responsiveness
- GPU acceleration for MediaPipe
- Advanced filtering for smoother tracking
- Machine learning-based calibration

## 🤝 Contributing

Feel free to contribute to this project by:
- Reporting bugs and issues
- Suggesting new features
- Improving documentation
- Optimizing performance
- Adding new keyboard layouts

## 📄 License

This project is open source. Please check the license file for details.

## 🙏 Acknowledgments

- **MediaPipe** by Google for facial landmark detection
- **OpenCV** community for computer vision tools
- Contributors and testers who helped improve the application

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Ensure all dependencies are correctly installed
3. Try adjusting the configuration parameters
4. Check that your camera works with other applications

For additional help, please refer to the documentation or create an issue in the project repository.

---

**Happy typing with your eyes! 👀✨**
## Sachinkumar
