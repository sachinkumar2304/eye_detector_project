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

- **Mode selection** at startup (Virtual Keyboard or Desktop Cursor)
- **Real-time face detection** and landmark tracking
- **Eye blink detection** for character selection and mouse clicks
- **Smooth cursor control** using nose position tracking
- **Virtual QWERTY keyboard** with visual feedback (on-screen or floating OS-integrated)
- **Desktop cursor navigation** with scroll and click via eye blinks
- **Floating keyboard** in cursor mode (triggered by 5s eye closure, types to OS)
- **Live camera feed** with overlay information
- **Text input and display** with character limits
- **Special keys support** (Space, Delete, Shift, Enter, Close Keyboard)
- **Text-to-speech feedback** for actions and selections
- **Movement stabilization** to prevent jittery cursor movement
- **Configurable sensitivity** and timing parameters

## 🛠️ Technology Stack

- **Python 3.x**
- **OpenCV** - Computer vision and camera handling
- **MediaPipe** - Facial landmark detection
- **NumPy** - Mathematical operations and arrays
- **pyttsx3** - Text-to-speech feedback
- **pynput** - Mouse and keyboard simulation for OS integration
- **screeninfo** - Screen resolution detection

## 📋 Prerequisites

Before running this application, ensure you have:

1. **Python 3.7 or higher** installed
2. **Webcam** or camera device
3. **Well-lit environment** for optimal face detection
4. **Stable head position** during use
5. **Speakers or audio output** (optional, for text-to-speech feedback)

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
pip install pyttsx3
pip install pynput
pip install screeninfo
```

**Alternative: Install all at once**
```bash
pip install opencv-python mediapipe numpy pyttsx3 pynput screeninfo
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

1. The application will start and display a **mode selection menu**:
   - Use nose up/down to navigate between "Virtual Keyboard" and "Desktop Cursor"
   - Blink to select your preferred mode
2. After selection, the application will access your camera
3. Windows will open based on the selected mode:
   - **"Camera"** - Live camera feed with facial landmark detection
   - **"Keyboard"** (Virtual Keyboard mode) - On-screen virtual keyboard interface
   - **"Floating Keyboard"** (Desktop Cursor mode, when triggered) - OS-integrated keyboard
4. The system will automatically detect your face and start tracking

## 📖 How to Use

### Initial Setup
1. **Position yourself** approximately 2-3 feet from the camera
2. **Ensure good lighting** - avoid harsh shadows on your face
3. **Keep your head relatively stable** during typing
4. **Look directly at the camera** initially for face detection

### Mode Selection
- At startup, use **nose up/down** to navigate between modes
- **Blink** to select "Virtual Keyboard" (on-screen typing) or "Desktop Cursor" (mouse control with optional typing)

### Virtual Keyboard Mode (On-Screen Typing)
#### Cursor Control
- **Move your nose slightly** to control the keyboard cursor
- **Left/Right movement** - Move nose horizontally
- **Up/Down movement** - Move nose vertically
- **Cursor sensitivity** can be adjusted in the code (`MOVE_THRESHOLD` variable)

#### Character Selection
- **Navigate** to the desired character using nose movements
- **Blink firmly** to select the highlighted character
- **Selected character** will be added to your text (displayed on-screen)

#### Special Keys
- **Space** - Inserts a space character
- **Delete** - Removes the last character
- **Shift** - Toggles between uppercase/lowercase (affects next character only)
- **Enter** - Inserts a newline character

#### Text Display
- **Current selection** is highlighted in cyan/green
- **Typed text** appears at the bottom of the keyboard window
- **Recent text** is shown in the camera feed overlay

### Desktop Cursor Mode (Mouse Navigation)
#### Cursor Control
- **Move your nose** to control the desktop mouse cursor
- **Left/Right movement** - Move cursor horizontally across screen
- **Up/Down movement** - Move cursor vertically across screen
- **Cursor sensitivity** can be adjusted in the code (`MOVE_THRESHOLD` variable)

#### Scrolling
- **Close left eye** to scroll up
- **Close right eye** to scroll down
- Keep eye closed for continuous scrolling

#### Clicking
- **Blink both eyes** firmly to perform left mouse click
- Audio feedback ("Click") confirms the action

#### Floating Keyboard (OS Typing)
- **Close both eyes for 5 seconds** to trigger the floating keyboard
- A small keyboard window appears, positioned at bottom-right of screen
- **Use nose movements** to navigate keys on the floating keyboard
- **Blink** to type characters directly into the active OS application
- **Select "CLOSE_KB"** to hide the floating keyboard
- **Close eyes for 10+ seconds** to get a warning (resting too long)

#### Audio Feedback
- **Text-to-speech** announces selections, actions, and mode changes
- Examples: "A", "Space", "Click", "Keyboard is on", "Shift On"

### General Controls
- **ESC key** on physical keyboard to quit the application
- **'c' key** in Virtual Keyboard mode to clear typed text

## ⚙️ Configuration

You can modify the following parameters in `eye_detector.py`:

```python
# Movement sensitivity (adjust based on your setup)
MOVE_THRESHOLD = 0.003  # Lower = more sensitive

# Movement delay (prevents rapid cursor jumping)
move_delay = 0.2  # Seconds between movements (keyboard mode)
KB_NAVIGATION_DELAY = 0.4  # Slower delay for keyboard navigation

# Blink detection parameters
min_blink_duration = 0.3  # Minimum blink time (seconds)
max_blink_duration = 1.5  # Maximum blink time (seconds)

# Eye blink ratios for detection
CLICK_RATIO = 4.0  # Both eyes for click/select
SCROLL_RATIO = 4.5  # Single eye for scroll

# Timing parameters
KEYBOARD_TRIGGER_TIME = 5.0  # Seconds to trigger floating KB
MAX_EYE_CLOSE_TIME = 10.0  # Seconds for warning
BLINK_CLICK_DELAY = 0.5  # Delay between clicks

# Camera resolution
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Stabilization
stabilization_frames = 5  # Frames for averaging nose position
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
- Adjust `MOVE_THRESHOLD` value (try 0.001-0.01 range)
- Ensure stable head position
- Try reducing `move_delay` if cursor feels sluggish

**4. Blink detection issues**
- Ensure you're blinking firmly enough
- Check lighting conditions
- Adjust `min_blink_duration` and `max_blink_duration`
- Try different eye aspect ratio thresholds (`CLICK_RATIO`, `SCROLL_RATIO`)

**5. Mode selection not working**
- Ensure good lighting for initial face detection
- Keep head stable during mode selection
- Blink firmly to select mode
- Try restarting if selection fails

**6. pynput permissions error (Windows)**
- Run the application as administrator
- Check Windows accessibility settings
- Ensure no other applications are controlling mouse/keyboard

**7. Text-to-speech not working**
- Check audio devices and speakers
- Ensure pyttsx3 is installed correctly
- Try adjusting system audio settings
- Some systems may require additional TTS engines

**8. Floating keyboard not appearing**
- Ensure you're in Desktop Cursor mode
- Close both eyes for exactly 5 seconds
- Check `KEYBOARD_TRIGGER_TIME` value
- Ensure screeninfo detects screen resolution correctly

**9. Poor performance**
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

### Virtual Keyboard Mode (On-Screen Typing)

#### Basic Text Input
1. Start the application and select "Virtual Keyboard" mode
2. Use nose movements to navigate to letters on the on-screen keyboard
3. Blink to select letters and build words
4. Type simple messages like "HELLO WORLD"

#### Writing Longer Text
1. Use efficient nose movements to navigate between rows and keys
2. Select "Space" key for word separation
3. Use "Enter" for new lines in multi-line text
4. Use "Delete" to correct mistakes
5. Press 'c' on physical keyboard to clear all text

#### Using Special Characters
- Navigate to "Shift" and blink to toggle uppercase mode (affects next character)
- Select numbers and symbols from the top row
- Use "Space" for word separation
- Use "Enter" for line breaks

### Desktop Cursor Mode (Mouse Navigation + OS Typing)

#### Basic Desktop Navigation
1. Start the application and select "Desktop Cursor" mode
2. Move your nose to control the mouse cursor across your desktop
3. Blink both eyes to left-click on icons, buttons, or text fields
4. Use left eye closure to scroll up in documents or web pages
5. Use right eye closure to scroll down

#### Typing in Applications
1. Navigate cursor to a text field (e.g., in Notepad, browser search)
2. Blink to click and focus the text field
3. Close both eyes for 5 seconds to trigger the floating keyboard
4. Use nose movements to select keys on the floating keyboard
5. Blink to type characters directly into the OS application
6. Select "CLOSE_KB" to hide the floating keyboard

#### Web Browsing Example
1. Navigate to browser window and click address bar
2. Type "google.com" using floating keyboard
3. Press Enter on floating keyboard to search
4. Navigate to search results and click links with blinks
5. Scroll through results using single eye closures

#### Rest and Warnings
- If eyes are closed for 10+ seconds, audio warning plays
- Use this time to rest without triggering unwanted actions

### General Tips
- Audio feedback announces all selections and actions
- Keep consistent distance (2-3 feet) from camera for best tracking
- Adjust configuration parameters if sensitivity needs fine-tuning

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
