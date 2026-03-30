# ai_powered_rover
An AI-powered rover using Raspberry Pi 5 and YOLOv8n for real-time pothole detection. It features a dual-layer navigation system: HSV color masking for road-boundary protection and autonomous steering logic to dodge hazards. The Pi 5 processes high-speed vision data, sending precise move commands to an Arduino Uno for agile motor control.

# Autonomous Pothole Detection Rover (Pi 5 Edition)

An intelligent, computer-vision-based rover built on **Raspberry Pi 5** and **Arduino Uno**. The system uses **YOLOv8n** for real-time pothole detection and **HSV Color Masking** for autonomous road-keeping.

## 🚀 Key Features
* **AI Detection:** Replaced traditional RANSAC math with a **YOLOv8 Nano** model for superior pattern recognition.
* **Road Boundary Guard:** Uses a real-time HSV road mask to ensure the rover stays on the dark asphalt and never drives off-road.
* **Precision Avoidance:** Logic-based steering (Left/Right) that calculates the widest path of available road to dodge detected holes.
* **Serial Bridge:** High-speed communication between Python (Pi 5) and C++ (Arduino Uno) via USB Serial.



## 🛠️ Hardware Stack
* **Processor:** Raspberry Pi 5 (8GB RAM)
* **Microcontroller:** Arduino Uno (Motor Control)
* **Camera:** Raspberry Pi Camera Module (ov5647)
* **Chassis:** 4WD Rover Platform with L298N Motor Driver

## 🧠 Software Logic
1. **HSV Masking:** Converts dark asphalt into a "White" driveable area.
2. **Zone Analysis:** Splits the road into Left/Right sectors to determine steering space.
3. **YOLO Inference:** Identifies potholes with a confidence threshold of 0.5.
4. **Size Filtering:** Ignores giant "ghost" boxes (noise) to maintain steering accuracy.

## 📦 Installation
1. Clone the repository:
   ```bash
   git clone [https://github.com/Ben-Binu/pothole-rover.git](https://github.com/yourusername/pothole-rover.git)
   cd pothole-rover
