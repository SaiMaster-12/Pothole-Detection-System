# Exact gps location only

import serial
import re

# Replace with your actual Arduino serial port if different
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)

# Regular expression to extract float values from the line
pattern = r"Latitude:\s*(-?\d+\.\d+),\s*Longitude:\s*(-?\d+\.\d+)"

while True:
    try:
        line = ser.readline().decode('utf-8', errors='ignore').strip()
        match = re.search(pattern, line)
        if match:
            latitude = float(match.group(1))
            longitude = float(match.group(2))
            print(f"Latitude: {latitude:.8f}, Longitude: {longitude:.8f}")
    except Exception as e:
        print("Error:", e)
