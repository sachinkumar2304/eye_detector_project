import cv2
import mediapipe as mp # type: ignore
import numpy as np
import time
import warnings
import pyttsx3 
import screeninfo 
from pynput.mouse import Controller, Button 
from pynput.keyboard import Controller as K_Controller, Key 
import threading 

warnings.filterwarnings("ignore")

# --- INITIAL SETUP ---
mouse = Controller() 
keyboard_os = K_Controller() 

tts_engine = pyttsx3.init()
tts_engine.setProperty('rate', 180) 

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
NOSE_TIP = 1 

# Keyboard layout (CLOSE_KB se keyboard band hoga)
keyboard = [
    list("QWERTYUIOP"),
    list("ASDFGHJKL"),
    list("ZXCVBNM"),
    ["Space", "Delete", "Shift", "Enter", "CLOSE_KB"] 
]
rows = len(keyboard)

# --- GLOBAL VARIABLES ---
selected_mode = None 
selected_row = 0
selected_col = 0
typed_text = ""
shift_on = False
blink_detected = False

# Movement, Scroll & Blink thresholds (Aapki final tuning)
MOVE_THRESHOLD = 0.003   
SCROLL_RATIO = 4.5      
CLICK_RATIO = 4.0       
SCROLL_AMOUNT = 2       
MAX_EYE_CLOSE_TIME = 10.0   
KEYBOARD_TRIGGER_TIME = 5.0 
BLINK_CLICK_DELAY = 0.5 
FLOATING_KB_ACTIVE = False 

# Additional variables
os_cursor_lock_pos = (0, 0) 

# Blink detection variables (Common to all modes)
blink_state = "open"
blink_start_time = 0
min_blink_duration = 0.3
max_blink_duration = 1.5

# Cursor Mode variables
both_eyes_closed_start_time = 0 
last_blink_click_time = time.time() 

# Keyboard Navigation Variables 
last_move_time = time.time()
move_delay = 0.2 
# NEW DELAY: Keyboard Mode Selection ko slow karne ke liye (0.4s)
KB_NAVIGATION_DELAY = 0.4
nose_history = []
stable_nose_position = None
stabilization_frames = 5 
min_movement_frames = 1
left_counter = right_counter = up_counter = down_counter = 0

# --- CORE FUNCTIONS ---

def blink_ratio(landmarks, eye_points):
    """Calculates the ratio of horizontal to vertical eye distance."""
    coords = [(landmarks[p].x, landmarks[p].y) for p in eye_points]
    horizontal = np.linalg.norm(np.array(coords[0]) - np.array(coords[3]))
    vertical = (np.linalg.norm(np.array(coords[1]) - np.array(coords[5])) +
                np.linalg.norm(np.array(coords[2]) - np.array(coords[4]))) / 2
    return horizontal / vertical if vertical != 0 else 0

def speak_non_blocking(text):
    """Speaks the text in a separate thread to prevent main loop from freezing."""
    def run_speech(t):
        try:
            tts_engine.say(t) 
            tts_engine.runAndWait()
        except:
            pass 
    
    if text:
        thread = threading.Thread(target=run_speech, args=(text,), daemon=True) 
        thread.start()

def handle_keyboard_input(key, shift_status):
    """
    Takes the selected key and types it into the OS using pynput.
    Returns: (updated_shift_status, text_to-speak)
    """
    text_to_speak = ""
    updated_shift_status = shift_status
    
    if key == "Space":
        keyboard_os.tap(Key.space)
        text_to_speak = "Space"
    elif key == "Delete":
        keyboard_os.tap(Key.backspace)
        text_to_speak = "Deleted"
    elif key == "Shift":
        updated_shift_status = not shift_status
        text_to_speak = "Shift On" if updated_shift_status else "Shift Off"
    elif key == "Enter":
        keyboard_os.tap(Key.enter)
        text_to_speak = "Enter"
    elif key == "CLOSE_KB": 
        global FLOATING_KB_ACTIVE
        FLOATING_KB_ACTIVE = False
        text_to_speak = "Keyboard Closed"
    else:
        char = key if shift_status else key.lower()
        keyboard_os.tap(char)
        text_to_speak = char
    
    return updated_shift_status, text_to_speak


# --- CAMERA & SCREEN SETUP ---
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open camera")
    exit()

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
CAM_W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
CAM_H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

try:
    screen = screeninfo.get_monitors()[0]
    SCREEN_W, SCREEN_H = screen.width, screen.height
except Exception:
    SCREEN_W, SCREEN_H = 1920, 1080 

# --- MODE SELECTION LOGIC (Restored) ---

def draw_mode_menu(img, selected):
    """Draws the startup menu with mode options."""
    h, w, _ = img.shape
    cv2.putText(img, "SELECT MODE (Blink to choose)", (w//2 - 250, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
    
    modes = ["1: Virtual Keyboard (Typing)", "2: Desktop Cursor (Navigation)"]
    
    for i, mode in enumerate(modes):
        color = (0, 255, 0) if i == selected else (255, 255, 255) 
        bg_color = (0, 100, 0) if i == selected else (0, 0, 0)
        
        cv2.rectangle(img, (w//2 - 200, 100 + i*150), (w//2 + 200, 200 + i*150), bg_color, -1)
        cv2.rectangle(img, (w//2 - 200, 100 + i*150), (w//2 + 200, 200 + i*150), color, 3)
        cv2.putText(img, mode, (w//2 - 190, 160 + i*150), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

def handle_mode_selection():
    """Manages the mode selection loop before the main application starts."""
    global selected_mode, both_eyes_closed_start_time, selected_row, selected_col, blink_state
    
    current_selection = 0 # 0 for Keyboard, 1 for Cursor
    blink_state_select = "open"
    
    while selected_mode is None:
        ret, frame = cap.read()
        if not ret: break
        
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb_frame)
        
        temp_frame = frame.copy()
        draw_mode_menu(temp_frame, current_selection)

        if results.multi_face_landmarks:
            face = results.multi_face_landmarks[0]
            nose = face.landmark[NOSE_TIP]
            current_time = time.time()
            
            # Simple nose movement for menu navigation (Up/Down)
            if nose.y < 0.35 and current_selection == 1:
                current_selection = 0
            elif nose.y > 0.65 and current_selection == 0:
                current_selection = 1
                
            # Blink detection for selection
            left_blink = blink_ratio(face.landmark, LEFT_EYE)
            right_blink = blink_ratio(face.landmark, RIGHT_EYE)
            eyes_closed = (left_blink > CLICK_RATIO and right_blink > CLICK_RATIO)
            
            if blink_state_select == "open" and eyes_closed:
                blink_state_select = "closed"
                both_eyes_closed_start_time = current_time
            
            elif blink_state_select == "closed" and not eyes_closed:
                blink_duration = current_time - both_eyes_closed_start_time
                if min_blink_duration <= blink_duration <= max_blink_duration:
                    if current_selection == 0:
                        selected_mode = "KEYBOARD"
                        speak_non_blocking("Keyboard Mode Selected")
                    elif current_selection == 1:
                        selected_mode = "CURSOR"
                        speak_non_blocking("Cursor Mode Selected")
                
                blink_state_select = "open"
            
            elif not eyes_closed and blink_state_select != "open":
                blink_state_select = "open"
                
        cv2.imshow("Mode Selection", temp_frame)
        
        if cv2.waitKey(1) & 0xFF == 27: # ESC key to quit
            break
            
    cv2.destroyWindow("Mode Selection")
    
# --- EXECUTE MODE SELECTION ---
handle_mode_selection()

# Agar user ne ESC press kiya toh exit
if selected_mode is None:
    cap.release()
    cv2.destroyAllWindows()
    exit()

# --- MAIN APPLICATION LOOP ---
try:
    print(f"Starting in {selected_mode} Mode...")
    
    while True:
        ret, frame = cap.read()
        if not ret: break
            
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb_frame)

        current_time = time.time()
        blink_detected = False
        
        if results.multi_face_landmarks:
            face = results.multi_face_landmarks[0]
            
            left_blink_ratio = blink_ratio(face.landmark, LEFT_EYE)
            right_blink_ratio = blink_ratio(face.landmark, RIGHT_EYE)
            nose = face.landmark[NOSE_TIP]
            
            # --- CURSOR MODE LOGIC (Integrated Floating KB) ---
            if selected_mode == "CURSOR":
                
                # --- A. Floating KB Trigger/Warning ---
                eyes_closed_now = (left_blink_ratio > SCROLL_RATIO and right_blink_ratio > SCROLL_RATIO)
                
                if eyes_closed_now:
                    if both_eyes_closed_start_time == 0:
                        both_eyes_closed_start_time = current_time
                    
                    elapsed_time = current_time - both_eyes_closed_start_time

                    if not FLOATING_KB_ACTIVE and elapsed_time >= KEYBOARD_TRIGGER_TIME and elapsed_time < MAX_EYE_CLOSE_TIME:
                        # 5 seconds: KEYBOARD OPEN TOGGLE
                        
                        # FIX 1: Current OS cursor position lock kiya
                        os_cursor_lock_pos = mouse.position 

                        FLOATING_KB_ACTIVE = True
                        # FIX: Voice confirmation for KB ON (Already present, confirming its existence)
                        speak_non_blocking("Keyboard is on") 
                        selected_row = 0
                        selected_col = 0
                        
                    elif elapsed_time >= MAX_EYE_CLOSE_TIME:
                        # 10 seconds: Warning dena
                        cv2.putText(frame, "⚠️ OPEN YOUR EYES! (Resting too long) ⚠️", (10, CAM_H - 10), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
                        FLOATING_KB_ACTIVE = False 
                        
                    elif not FLOATING_KB_ACTIVE:
                         # 0 se 5 seconds ke beech ka feedback
                         cv2.putText(frame, f"Triggering KB in: {KEYBOARD_TRIGGER_TIME - elapsed_time:.1f}s", (10, CAM_H - 10), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 165, 255), 2)
                        
                else:
                    # FIX: Aankh khulne par sirf timer reset hoga, KB off nahi hoga.
                    both_eyes_closed_start_time = 0 
                
                # --- B. Control Logic based on KB status ---
                if FLOATING_KB_ACTIVE:
                    
                    # FIX 1: OS Cursor ko lock position par rakha
                    mouse.position = os_cursor_lock_pos 

                    # Keyboard Navigation (Nose movement)
                    current_nose_pos = (nose.x, nose.y)
                    
                    if stable_nose_position is None: stable_nose_position = current_nose_pos
                    nose_history.append(current_nose_pos)
                    if len(nose_history) > stabilization_frames: nose_history.pop(0)
                    
                    # KEYBOARD MOVEMENT LOGIC (KB Selection)
                    if len(nose_history) >= stabilization_frames:
                        avg_nose_x = np.mean([n[0] for n in nose_history])
                        avg_nose_y = np.mean([n[1] for n in nose_history])
                        
                        delta_x = avg_nose_x - stable_nose_position[0]
                        delta_y = avg_nose_y - stable_nose_position[1]
                        
                        if current_time - last_move_time > move_delay:
                            moved = False
                            # Horizontal movement
                            if abs(delta_x) > MOVE_THRESHOLD:
                                if delta_x < -MOVE_THRESHOLD:  # Left
                                    selected_col = (selected_col - 1) % len(keyboard[selected_row])
                                    moved = True
                                elif delta_x > MOVE_THRESHOLD: # Right
                                    selected_col = (selected_col + 1) % len(keyboard[selected_row])
                                    moved = True
                            
                            # Vertical movement
                            if abs(delta_y) > MOVE_THRESHOLD:
                                if delta_y < -MOVE_THRESHOLD:  # Up
                                    new_row = (selected_row - 1) % rows
                                    selected_row = new_row
                                    selected_col = min(selected_col, len(keyboard[selected_row]) - 1)
                                    moved = True
                                elif delta_y > MOVE_THRESHOLD: # Down
                                    new_row = (selected_row + 1) % rows
                                    selected_row = new_row
                                    selected_col = min(selected_col, len(keyboard[selected_row]) - 1)
                                    moved = True
                                    
                            if moved:
                                last_move_time = current_time
                                stable_nose_position = (avg_nose_x, avg_nose_y)

                    # Blink Detection for Typing (OS Input)
                    eyes_closed_for_click = (left_blink_ratio > CLICK_RATIO and right_blink_ratio > CLICK_RATIO)
                    
                    if blink_state == "open" and eyes_closed_for_click:
                        blink_state = "closed"
                        blink_start_time = current_time
                    
                    elif blink_state == "closed" and not eyes_closed_for_click:
                        blink_duration = current_time - blink_start_time
                        
                        if min_blink_duration <= blink_duration <= max_blink_duration and current_time - last_blink_click_time > BLINK_CLICK_DELAY:
                            
                            key = keyboard[selected_row][selected_col]
                            
                            # OS Typing Function Call
                            shift_on, text_to_speak = handle_keyboard_input(key, shift_on)
                            
                            if text_to_speak: speak_non_blocking(text_to_speak) 
                            
                            blink_detected = True
                            last_blink_click_time = current_time 
                            
                        blink_state = "open"
                    
                    elif not eyes_closed_for_click and blink_state != "open":
                        blink_state = "open"

                else: # FLOATING_KB_ACTIVE == False (Normal Cursor Mode)
                    # 1. Cursor Movement
                    cursor_x = int(nose.x * SCREEN_W)
                    cursor_y = int(nose.y * SCREEN_H)
                    mouse.position = (cursor_x, cursor_y) 

                    # 2. Scrolling Logic
                    if left_blink_ratio > SCROLL_RATIO and right_blink_ratio < SCROLL_RATIO:
                        mouse.scroll(0, SCROLL_AMOUNT) 
                        cv2.putText(frame, "⬆️ SCROLLING UP", (CAM_W - 200, CAM_H - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
                    
                    elif right_blink_ratio > SCROLL_RATIO and left_blink_ratio < SCROLL_RATIO:
                        mouse.scroll(0, -SCROLL_AMOUNT) 
                        cv2.putText(frame, "⬇️ SCROLLING DOWN", (CAM_W - 200, CAM_H - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

                    # 3. Blink for Click (OS Mouse Click)
                    eyes_closed_for_click = (left_blink_ratio > CLICK_RATIO and right_blink_ratio > CLICK_RATIO)
                    
                    if blink_state == "open" and eyes_closed_for_click:
                        blink_state = "closed"
                        blink_start_time = current_time
                    
                    elif blink_state == "closed" and not eyes_closed_for_click:
                        blink_duration = current_time - blink_start_time
                        
                        if 0.1 < blink_duration < 0.5 and current_time - last_blink_click_time > BLINK_CLICK_DELAY:
                            mouse.click(Button.left) 
                            speak_non_blocking("Click")
                            last_blink_click_time = current_time 
                            cv2.putText(frame, "CLICK!", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                        
                        blink_state = "open"
            
            # --- KEYBOARD MODE LOGIC (Original Functionality) ---
            elif selected_mode == "KEYBOARD":
                
                # Get nose position for cursor control
                current_nose_pos = (nose.x, nose.y)
                
                if stable_nose_position is None: stable_nose_position = current_nose_pos
                
                # Smooth nose position
                nose_history.append(current_nose_pos)
                if len(nose_history) > stabilization_frames: nose_history.pop(0)
                
                # KEYBOARD NAVIGATION LOGIC
                if len(nose_history) >= stabilization_frames:
                    avg_nose_x = np.mean([n[0] for n in nose_history])
                    avg_nose_y = np.mean([n[1] for n in nose_history])
                    
                    delta_x = avg_nose_x - stable_nose_position[0]
                    delta_y = avg_nose_y - stable_nose_position[1]
                    
                    # FIX: Keyboard Mode ke liye slower delay use kiya
                    if current_time - last_move_time > KB_NAVIGATION_DELAY:
                        moved = False
                        # Horizontal movement
                        if abs(delta_x) > MOVE_THRESHOLD:
                            if delta_x < -MOVE_THRESHOLD:  # Left
                                selected_col = (selected_col - 1) % len(keyboard[selected_row])
                                moved = True
                            elif delta_x > MOVE_THRESHOLD: # Right
                                selected_col = (selected_col + 1) % len(keyboard[selected_row])
                                moved = True
                        
                        # Vertical movement
                        if abs(delta_y) > MOVE_THRESHOLD:
                            if delta_y < -MOVE_THRESHOLD:  # Up
                                new_row = (selected_row - 1) % rows
                                selected_row = new_row
                                selected_col = min(selected_col, len(keyboard[selected_row]) - 1)
                                moved = True
                            elif delta_y > MOVE_THRESHOLD: # Down
                                new_row = (selected_row + 1) % rows
                                selected_row = new_row
                                selected_col = min(selected_col, len(keyboard[selected_row]) - 1)
                                moved = True
                                
                        if moved:
                            last_move_time = current_time
                            stable_nose_position = (avg_nose_x, avg_nose_y)

                # Blink Detection for Typing (On-screen Keyboard)
                eyes_closed_for_click = (left_blink_ratio > CLICK_RATIO and right_blink_ratio > CLICK_RATIO)
                
                if blink_state == "open" and eyes_closed_for_click:
                    blink_state = "closed"
                    blink_start_time = current_time
                
                elif blink_state == "closed" and not eyes_closed_for_click:
                    blink_duration = current_time - blink_start_time
                    
                    if min_blink_duration <= blink_duration <= max_blink_duration:
                        # Valid blink detected
                        key = keyboard[selected_row][selected_col]
                        text_to_speak = ""
                        
                        if key == "Space":
                            typed_text += " "
                            text_to_speak = "Space"
                        elif key == "Delete":
                            typed_text = typed_text[:-1]
                            text_to_speak = "Deleted"
                        elif key == "Shift":
                            shift_on = not shift_on
                            text_to_speak = "Shift On" if shift_on else "Shift Off"
                        elif key == "Enter":
                            typed_text += "\n"
                            text_to_speak = "Enter"
                        else:
                            char = key if shift_on else key.lower()
                            typed_text += char
                            text_to_speak = char
                        
                        if text_to_speak: speak_non_blocking(text_to_speak) 
                            
                        blink_detected = True
                        
                    blink_state = "open"
                
                elif not eyes_closed_for_click and blink_state != "open":
                    blink_state = "open"
        
        # --- DISPLAY OUTPUT ---
        
        cv2.putText(frame, f"MODE: {selected_mode} | KB: {'ON' if FLOATING_KB_ACTIVE else 'OFF'}", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

        # Floating Keyboard (Visible only in CURSOR mode when active)
        if selected_mode == "CURSOR" and FLOATING_KB_ACTIVE:
            key_w, key_h = 45, 30 
            kb_w = max(len(r) for r in keyboard) * key_w + 30
            kb_h = rows * key_h + 40
            kb_img = np.zeros((kb_h, kb_w, 3), dtype=np.uint8)

            for r in range(rows):
                for c in range(len(keyboard[r])):
                    x = 10 + c * key_w
                    y = 10 + r * key_h
                    if r == selected_row and c == selected_col:
                        color = (0, 255, 0) if blink_detected else (0, 255, 255)
                        cv2.rectangle(kb_img, (x, y), (x + key_w, y + key_h), color, -1)
                        cv2.putText(kb_img, keyboard[r][c][:5], (x + 5, y + 20),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
                    else:
                        color = (255, 100, 100) if keyboard[r][c] == "CLOSE_KB" else (255, 255, 255)
                        cv2.rectangle(kb_img, (x, y), (x + key_w, y + key_h), color, 1)
                        cv2.putText(kb_img, keyboard[r][c][:5], (x + 5, y + 20),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

            cv2.imshow("Floating Keyboard", kb_img)
            
            # FIX: Window position aur always-on-top set kiya
            try:
                cv2.setWindowProperty("Floating Keyboard", cv2.WND_PROP_TOPMOST, 1)
                kb_x = SCREEN_W - kb_w - 10 
                kb_y = SCREEN_H - kb_h - 10
                cv2.moveWindow("Floating Keyboard", kb_x, kb_y)
            except cv2.error:
                pass

        elif FLOATING_KB_ACTIVE == False:
            # FIX: Only attempt to destroy if the window *might* exist
            try:
                cv2.destroyWindow("Floating Keyboard")
            except cv2.error:
                pass
        
        # Original Keyboard Window (Visible only in KEYBOARD mode)
        if selected_mode == "KEYBOARD":
            info_text = [
                f"Selected: {keyboard[selected_row][selected_col]}",
                f"Shift: {'ON' if shift_on else 'OFF'}",
                f"Text: {typed_text[-25:]}"
            ]
            
            for i, text in enumerate(info_text):
                cv2.putText(frame, text, (10, 60 + i * 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            
            if blink_detected:
                cv2.putText(frame, "BLINK DETECTED!", (10, CAM_H - 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

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
                        cv2.putText(kb_img, keyboard[r][c][:8], (x + 10, y + 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
                    else:
                        cv2.rectangle(kb_img, (x, y), (x + key_w, y + key_h), (255, 255, 255), 2)
                        cv2.putText(kb_img, keyboard[r][c][:8], (x + 10, y + 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

            # Display typed text
            cv2.putText(kb_img, "Typed:", (25, kb_h - 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            max_chars = 30
            lines = [typed_text[i:i+max_chars] for i in range(0, len(typed_text), max_chars)]
            for i, line in enumerate(lines[-3:]):
                cv2.putText(kb_img, line, (25, kb_h - 70 + i * 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)

            cv2.putText(kb_img, "Blink firmly to select | ESC to quit", (25, kb_h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            cv2.imshow("Keyboard", kb_img)
            
        else:
            # Agar KEYBOARD mode nahi hai toh Original KB window ko destroy karo
            try:
                cv2.destroyWindow("Keyboard")
            except cv2.error:
                pass


        cv2.imshow("Camera", frame)

        key_press = cv2.waitKey(1) & 0xFF
        if key_press == 27:  # ESC
            break
        elif key_press == ord('c') and selected_mode == "KEYBOARD":  # Clear text
            typed_text = ""
            speak_non_blocking("Text cleared")

except KeyboardInterrupt:
    print("\nProgram interrupted by user")
except Exception as e:
    print(f"Error occurred: {e}")
finally:
    cap.release()
    cv2.destroyAllWindows()
    print("Program ended safely")