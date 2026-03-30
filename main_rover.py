import cv2
import numpy as np
from picamera2 import Picamera2
import motor_driver as motors
import gps_helper as gps

# Setup Hardware
motors.setup_motors()
picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"format": "RGB888", "size": (640, 480)})
picam2.configure(config)
picam2.start()

# Variables
pothole_lat, pothole_lon = None, None
is_tracking = False

try:
    print("Rover Autonomous Mode Active...")
    while True:
        frame = picam2.capture_array()
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blur, 70, 150)

        # Zone Analysis (Bottom 40% of screen)
        height, width = edges.shape
        roi = edges[int(height*0.6):, :]
        center_zone = roi[:, width//3 : 2*width//3]

        curr_lat, curr_lon = gps.get_coords()

        # Decision Logic
        if np.sum(center_zone) > 5000: # Threshold for pothole border
            if not is_tracking and curr_lat:
                pothole_lat, pothole_lon = curr_lat, curr_lon
                is_tracking = True
            
            # Action: Turn to avoid (Modify based on space)
            motors.turn_left()
            status = "POTHOLE DETECTED - TURNING"
        else:
            motors.move_forward()
            status = "ROAD CLEAR"

        # UI Data Display for VNC
        cv2.putText(frame, status, (20, 40), 2, 0.7, (0, 0, 255), 2)
        if is_tracking and curr_lat:
            d = gps.calculate_dist(curr_lat, curr_lon, pothole_lat, pothole_lon)
            cv2.putText(frame, f"Dist to Hole: {d:.2f}m", (20, 80), 2, 0.7, (0, 255, 0), 2)

        cv2.imshow("Pi 5 Rover Feed", frame)
        if cv2.waitKey(1) == ord('q'):
            break

finally:
    motors.cleanup()
    picam2.stop()
    cv2.destroyAllWindows()