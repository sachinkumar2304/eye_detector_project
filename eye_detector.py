import cv2
import mediapipe as mp  # type: ignore
import numpy as np
import time
import warnings

warnings.filterwarnings("ignore")

# Mediapipe setup
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# Eye & nose landmarks
LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]
NOSE_TIP = 1  # approximate nose tip

# Keyboard layout
keyboard = [
    list("QWERTYUIOP"),
    list("ASDFGHJKL"),
    list("ZXCVBNM"),
    ["Space", "Delete", "Shift", "Enter"]
]

rows = len(keyboard)
selected_row = 0
selected_col = 0
typed_text = ""
shift_on = False
blink_detected = False

# Blink ratio calculation
def blink_ratio(landmarks, eye_points):
    coords = [(landmarks[p].x, landmarks[p].y) for p in eye_points]
    horizontal = np.linalg.norm(np.array(coords[0]) - np.array(coords[3]))
    vertical = (np.linalg.norm(np.array(coords[1]) - np.array(coords[5])) +
                np.linalg.norm(np.array(coords[2]) - np.array(coords[4]))) / 2
    return horizontal / vertical if vertical != 0 else 0

# Initialize camera
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open camera")
    exit()

# Set camera properties
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Initialize variables
last_blink_time = time.time()
blink_confirm_time = 0
last_move_time = time.time()
move_delay = 0.5  # Delay between cursor movements
nose_history = []
stable_nose_position = None

# Movement thresholds
threshold = 0.04  # Movement sensitivity
stabilization_frames = 8  # Frames for position smoothing
min_movement_frames = 2  # Minimum frames for movement detection

# Movement counters
left_counter = 0
right_counter = 0
up_counter = 0
down_counter = 0

# Blink detection variables
blink_state = "open"  # "open", "closing", "closed"
blink_start_time = 0
min_blink_duration = 0.3  # Minimum blink duration
max_blink_duration = 1.5  # Maximum blink duration

try:
    print("Starting eye detector...")
    print("Keep your head stable and look at the keyboard")
    print("Blink firmly to select letters")
    print("Move nose slightly to control cursor")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame")
            break
            
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb_frame)

        blink_detected = False
        
        if results.multi_face_landmarks:
            face = results.multi_face_landmarks[0]

            # Get nose position for cursor control
            nose = face.landmark[NOSE_TIP]
            current_nose_pos = (nose.x, nose.y)
            
            # Initialize stable position
            if stable_nose_position is None:
                stable_nose_position = current_nose_pos
            
            # Smooth nose position
            nose_history.append(current_nose_pos)
            if len(nose_history) > stabilization_frames:
                nose_history.pop(0)
            
            if len(nose_history) >= stabilization_frames:
                avg_nose_x = np.mean([n[0] for n in nose_history])
                avg_nose_y = np.mean([n[1] for n in nose_history])
                
                delta_x = avg_nose_x - stable_nose_position[0]
                delta_y = avg_nose_y - stable_nose_position[1]
                
                # Cursor movement with stability
                if time.time() - last_move_time > move_delay:
                    moved = False
                    
                    # Horizontal movement
                    if abs(delta_x) > threshold:
                        if delta_x < -threshold:  # Left
                            left_counter += 1
                            if left_counter >= min_movement_frames:
                                selected_col = (selected_col - 1) % len(keyboard[selected_row])
                                moved = True
                                left_counter = 0
                        elif delta_x > threshold:  # Right
                            right_counter += 1
                            if right_counter >= min_movement_frames:
                                selected_col = (selected_col + 1) % len(keyboard[selected_row])
                                moved = True
                                right_counter = 0
                    
                    # Vertical movement
                    if abs(delta_y) > threshold:
                        if delta_y < -threshold:  # Up
                            up_counter += 1
                            if up_counter >= min_movement_frames:
                                new_row = (selected_row - 1) % rows
                                selected_row = new_row
                                selected_col = min(selected_col, len(keyboard[selected_row]) - 1)
                                moved = True
                                up_counter = 0
                        elif delta_y > threshold:  # Down
                            down_counter += 1
                            if down_counter >= min_movement_frames:
                                new_row = (selected_row + 1) % rows
                                selected_row = new_row
                                selected_col = min(selected_col, len(keyboard[selected_row]) - 1)
                                moved = True
                                down_counter = 0
                    
                    if moved:
                        last_move_time = time.time()
                        stable_nose_position = (avg_nose_x, avg_nose_y)
                        nose_history.clear()
                        left_counter = right_counter = up_counter = down_counter = 0

            # Enhanced blink detection
            left_blink = blink_ratio(face.landmark, LEFT_EYE)
            right_blink = blink_ratio(face.landmark, RIGHT_EYE)
            
            # Calculate eye openness
            left_eye_openness = abs(face.landmark[LEFT_EYE[1]].y - face.landmark[LEFT_EYE[5]].y)
            right_eye_openness = abs(face.landmark[RIGHT_EYE[1]].y - face.landmark[RIGHT_EYE[5]].y)
            
            # Blink detection state machine
            current_time = time.time()
            
            # Check if eyes are closed
            eyes_closed = (left_blink > 4.0 and right_blink > 4.0) or \
                         (left_eye_openness < 0.015 and right_eye_openness < 0.015)
            
            if blink_state == "open" and eyes_closed:
                blink_state = "closing"
                blink_start_time = current_time
            elif blink_state == "closing" and eyes_closed:
                blink_state = "closed"
            elif blink_state == "closed" and not eyes_closed:
                # Blink completed
                blink_duration = current_time - blink_start_time
                
                if min_blink_duration <= blink_duration <= max_blink_duration:
                    # Valid blink detected
                    key = keyboard[selected_row][selected_col]
                    if key == "Space":
                        typed_text += " "
                    elif key == "Delete":
                        typed_text = typed_text[:-1]
                    elif key == "Shift":
                        shift_on = not shift_on
                    elif key == "Enter":
                        typed_text += "\n"
                    else:
                        typed_text += key if shift_on else key.lower()
                    
                    print(f"✓ Typed: '{key}' | Current: '{typed_text}'")
                    blink_detected = True
                
                blink_state = "open"
            elif not eyes_closed and blink_state != "open":
                blink_state = "open"

        # Display camera feed with info
        info_text = [
            f"Selected: {keyboard[selected_row][selected_col]}",
            f"Shift: {'ON' if shift_on else 'OFF'}",
            f"Text: {typed_text[-25:]}"
        ]
        
        for i, text in enumerate(info_text):
            cv2.putText(frame, text, (10, 30 + i * 25), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        if blink_detected:
            cv2.putText(frame, "BLINK DETECTED!", (10, frame.shape[0] - 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        cv2.imshow("Camera", frame)

        # Draw keyboard
        key_w, key_h = 80, 60
        kb_w = max(len(r) for r in keyboard) * key_w + 50
        kb_h = rows * key_h + 150
        kb_img = np.zeros((kb_h, kb_w, 3), dtype=np.uint8)

        for r in range(rows):
            for c in range(len(keyboard[r])):
                x = 25 + c * key_w
                y = 25 + r * key_h
                if r == selected_row and c == selected_col:
                    color = (0, 255, 0) if blink_detected else (0, 255, 255)
                    cv2.rectangle(kb_img, (x, y), (x + key_w, y + key_h), color, -1)
                    cv2.putText(kb_img, keyboard[r][c], (x + 10, y + 40),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
                else:
                    cv2.rectangle(kb_img, (x, y), (x + key_w, y + key_h), (255, 255, 255), 2)
                    cv2.putText(kb_img, keyboard[r][c], (x + 10, y + 40),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        # Display typed text
        cv2.putText(kb_img, "Typed:", (25, kb_h - 100), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        max_chars = 30
        lines = [typed_text[i:i+max_chars] for i in range(0, len(typed_text), max_chars)]
        for i, line in enumerate(lines[-3:]):
            cv2.putText(kb_img, line, (25, kb_h - 70 + i * 20), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)

        # Instructions
        cv2.putText(kb_img, "Blink firmly to select | ESC to quit", (25, kb_h - 20), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        cv2.imshow("Keyboard", kb_img)

        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC
            break
        elif key == ord('c'):  # Clear text
            typed_text = ""
            print("Text cleared")

except KeyboardInterrupt:
    print("\nProgram interrupted by user")
except Exception as e:
    print(f"Error occurred: {e}")
finally:
    cap.release()
    cv2.destroyAllWindows()
    print("Program ended safely")
    print(f"Final typed text: {typed_text}")
