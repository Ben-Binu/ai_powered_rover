import serial
import pynmea2
import math

# Initialize Serial for NEO-6M
ser = serial.Serial('/dev/ttyS0', 9600, timeout=0.5)

def get_coords():
    try:
        line = ser.readline().decode('ascii', errors='replace')
        if "$GPRMC" in line or "$GPGGA" in line:
            msg = pynmea2.parse(line)
            if msg.latitude != 0:
                return msg.latitude, msg.longitude
    except:
        return None, None
    return None, None

def calculate_dist(lat1, lon1, lat2, lon2):
    R = 6371000 # Radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
