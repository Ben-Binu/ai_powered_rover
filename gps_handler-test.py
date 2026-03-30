def parse_arduino_data(line):
    """Parses GPS:LAT,LON,DIST from Arduino Serial."""
    try:
        if line.startswith("GPS:"):
            parts = line.replace("GPS:", "").strip().split(",")
            return float(parts[0]), float(parts[1]), float(parts[2])
    except:
        pass
    return None, None, 0.0
