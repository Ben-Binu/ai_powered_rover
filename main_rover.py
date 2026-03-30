"""
================================================================================
PROJECT: AUTONOMOUS POTHOLE DETECTION ROVER (HIGH-SENSITIVITY EDITION)
LOGIC: 
1. Road Mask (HSV) -> 2. Contrast Boost (CLAHE) -> 3. RANSAC Outlier Analysis
================================================================================
"""

import cv2
import numpy as np
from picamera2 import Picamera2
import serial
import time
from sklearn.linear_model import RANSACRegressor

# --- MASTER SWITCHES ---
USE_HUB = False  # Set to True for Arduino
USE_GPS = False  

# --- INITIALIZE HARDWARE ---
hub = None
if USE_HUB:
    try:
        hub = serial.Serial('/dev/ttyACM0', 9600, timeout=0.1)
        time.sleep(2)
    except:
        USE_HUB = False

picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"format": "RGB888", "size": (640, 480)})
picam2.configure(config)
picam2.start()

# --- VISION FUNCTIONS ---

def get_full_road_mask(frame):
    """Detects Black Asphalt and turns it WHITE in the mask."""
    hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
    # Range for Dark Surfaces (Value 0-85)
    lower_dark = np.array([0, 0, 0])
    upper_dark = np.array([180, 255, 85]) 
    
    mask = cv2.inRange(hsv, lower_dark, upper_dark)
    kernel = np.ones((5,5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    
    coverage = np.sum(mask == 255) / mask.size
    return coverage > 0.20, mask

def detect_potholes_latest(frame, road_mask):
    """
    ADVANCED POTHOLE LOGIC:
    Uses CLAHE for depth and RANSAC for outlier isolation.
    """
    # 1. CONTRAST BOOSTING
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    enhanced = clahe.apply(gray)
    
    # 2. EDGE DETECTION (Low thresholds to catch depth)
    blurred = cv2.medianBlur(enhanced, 5)
    edges = cv2.Canny(blurred, 30, 80)
    
    # 3. BITWISE MASKING (Only edges on the road)
    road_edges = cv2.bitwise_and(edges, road_mask)
    
    y_coords, x_coords = np.where(road_edges == 255)
    if len(x_coords) < 100: 
        return False, road_edges, np.zeros_like(road_mask)

    try:
        # 4. RANSAC (Sensitivity set to 5.0)
        ransac = RANSACRegressor(residual_threshold=5.0)
        ransac.fit(x_coords.reshape(-1, 1), y_coords)
        
        # 5. ISOLATE OUTLIERS (The actual pothole)
        outlier_mask = np.zeros_like(road_edges)
        outlier_idx = np.logical_not(ransac.inlier_mask_)
        outlier_mask[y_coords[outlier_idx], x_coords[outlier_idx]] = 255
        
        # 6. BLOB DETECTION (Fills the 'Red Border' area)
        kernel = np.ones((7,7), np.uint8)
        outlier_mask = cv2.dilate(outlier_mask, kernel, iterations=1)
        
        contours, _ = cv2.findContours(outlier_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        found = False
        for cnt in contours:
            if cv2.contourArea(cnt) > 300: # Smaller threshold for better detection
                x, y, w, h = cv2.boundingRect(cnt)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 3) # RED BORDER
                cv2.putText(frame, "POTHOLE", (x, y - 10), 2, 0.6, (0, 0, 255), 2)
                found = True
        return found, road_edges, outlier_mask
    except:
        return False, road_edges, np.zeros_like(road_mask)

# --- MAIN LOOP ---

try:
    print("System Running: Sequential Road -> Pothole Analysis")
    while True:
        frame = picam2.capture_array()
        
        # STAGE 1: Road Mask
        is_road, road_mask = get_full_road_mask(frame)

        if is_road:
            # STAGE 2: Pothole & Border Logic
            pothole_found, edges_v, outliers_v = detect_potholes_latest(frame, road_mask)
            
            if pothole_found:
                status, color = "POTHOLE DETECTED", (0, 0, 255)
                if USE_HUB: hub.write(b'S')
            else:
                status, color = "ROAD CLEAR", (0, 255, 0)
                if USE_HUB: hub.write(b'F')
        else:
            status, color = "SEARCHING FOR ROAD...", (255, 255, 255)
            edges_v = outliers_v = np.zeros_like(road_mask)

        # HUD DISPLAY
        cv2.putText(frame, status, (20, 40), 2, 0.7, color, 2)
        cv2.imshow("1. Main Vision (Borders)", frame)
        cv2.imshow("2. Road Mask (Must be White)", road_mask)
        cv2.imshow("3. Outlier Debug (Pothole Pixels)", outliers_v)
        
        if cv2.waitKey(1) == ord('q'): break

finally:
    if USE_HUB and hub: hub.write(b'S')
    picam2.stop()
    cv2.destroyAllWindows()
