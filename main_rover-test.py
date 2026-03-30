"""
================================================================================
PROJECT: AUTONOMOUS POTHOLE DETECTION ROVER (YOLO EDITION)
LOGIC: 
1. Road Mask (HSV) -> 2. Contrast Boost (CLAHE) -> 3. YOLO Object Detection
================================================================================
"""

import cv2
import numpy as np
from picamera2 import Picamera2
import serial
import time
from ultralytics import YOLO

# --- MASTER SWITCHES ---
USE_HUB = False  # Set to True for Arduino
USE_GPS = False  
CONFIDENCE_THRESHOLD = 0.5 # 50% certainty required

# --- INITIALIZE HARDWARE & AI ---
hub = None
if USE_HUB:
    try:
        hub = serial.Serial('/dev/ttyACM0', 9600, timeout=0.1)
        time.sleep(2)
    except:
        USE_HUB = False

# Load YOLO Model (This replaces the RANSAC Regressor)
model = YOLO('yolov8n.pt') 

picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"format": "RGB888", "size": (640, 480)})
picam2.configure(config)
picam2.start()

# --- VISION FUNCTIONS ---

def get_full_road_mask(frame):
    """Detects Black Asphalt and turns it WHITE in the mask."""
    hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
    lower_dark = np.array([0, 0, 0])
    upper_dark = np.array([180, 255, 85]) 
    
    mask = cv2.inRange(hsv, lower_dark, upper_dark)
    kernel = np.ones((5,5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    
    coverage = np.sum(mask == 255) / mask.size
    
    # Navigation Logic: Deciding steer direction based on road space
    w = mask.shape[1]
    left_side = np.sum(mask[:, :w//2] == 255)
    right_side = np.sum(mask[:, w//2:] == 255)
    steer_dir = 'L' if left_side > right_side else 'R'
    
    return coverage > 0.20, steer_dir, mask

def detect_potholes_latest(frame, road_mask):
    """
    REPLACED RANSAC WITH YOLO:
    Uses YOLO to identify the pothole pattern within the road area.
    """
    # 1. CONTRAST BOOSTING (Kept for better visual feed)
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    enhanced = clahe.apply(gray)
    
    # 2. EDGE DETECTION (Kept for the Outlier Debug window)
    blurred = cv2.medianBlur(enhanced, 5)
    edges = cv2.Canny(blurred, 30, 80)
    road_edges = cv2.bitwise_and(edges, road_mask)
    
    # 3. YOLO DETECTION (The new math replacement)
    results = model.predict(frame, conf=CONFIDENCE_THRESHOLD, verbose=False)
    
    found = False
    outlier_mask = np.zeros_like(road_edges)

    for r in results:
        for box in r.boxes:
            # Get Coordinates
            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            
            # Fill the 'Outlier Debug' window for you
            cv2.rectangle(outlier_mask, (x1, y1), (x2, y2), 255, -1)
            
            # Draw the RED BORDER on the main frame
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 3)
            cv2.putText(frame, "POTHOLE", (x1, y1 - 10), 2, 0.6, (0, 0, 255), 2)
            found = True
            
    return found, road_edges, outlier_mask

# --- MAIN LOOP ---

try:
    print("YOLO Rover System Running...")
    while True:
        frame = picam2.capture_array()
        
        # STAGE 1: Road Mask & Steering Decision
        is_road, steer_cmd, road_mask = get_full_road_mask(frame)

        if is_road:
            # STAGE 2: YOLO Pothole Detection
            pothole_found, edges_v, outliers_v = detect_potholes_latest(frame, road_mask)
            
            if pothole_found:
                status, color = f"POTHOLE! STEERING {steer_cmd}", (0, 0, 255)
                if USE_HUB: hub.write(steer_cmd.encode()) # Move Left or Right
            else:
                status, color = "ROAD CLEAR: FORWARD", (0, 255, 0)
                if USE_HUB: hub.write(b'F')
        else:
            status, color = "SEARCHING FOR ROAD...", (255, 255, 255)
            edges_v = outliers_v = np.zeros_like(road_mask)
            if USE_HUB: hub.write(b'S')

        # HUD DISPLAY
        cv2.putText(frame, status, (20, 40), 2, 0.7, color, 2)
        cv2.imshow("1. Main Vision (YOLO Borders)", frame)
        cv2.imshow("2. Road Mask (Navigation)", road_mask)
        cv2.imshow("3. YOLO Outlier Map", outliers_v)
        
        if cv2.waitKey(1) == ord('q'): break

finally:
    if USE_HUB and hub: hub.write(b'S')
    picam2.stop()
    cv2.destroyAllWindows()
