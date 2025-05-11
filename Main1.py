import cv2
import os
import base64
import requests
import re
import serial
from ultralytics import YOLO
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition

# API keys
SENDGRID_API_KEY = ""

# Path to your trained YOLO model
MlModel = "/home/sai/Documents/best.pt"

# Email credentials
FROM_EMAIL = ""
TO_EMAIL = ""

# Serial port setup for GPS (Arduino)
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
pattern = r"Latitude:\s*(-?\d+\.\d+),\s*Longitude:\s*(-?\d+\.\d+)"

def get_gps_coordinates():
    try:
        while True:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            match = re.search(pattern, line)
            if match:
                latitude = float(match.group(1))
                longitude = float(match.group(2))
                return latitude, longitude
    except Exception as e:
        print(f"Error reading GPS data: {e}")
    return None, None

def send_email(coordinates, files, pothole_data):
    latitude, longitude = coordinates
    severity_summary = "".join(
        f"<li>Pothole {idx + 1}: {info['severity']} - {info['repair_suggestion']}</li>"
        for idx, info in enumerate(pothole_data)
    )

    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=TO_EMAIL,
        subject="Pothole Detection Report",
        html_content=f"""
        <p><b>Pothole Detection Summary</b></p>
        <p><b>Location Details:</b></p>
        <ul>
            <li>Latitude: {latitude}</li>
            <li>Longitude: {longitude}</li>
        </ul>
        <p><b>Total Potholes Detected:</b> {len(pothole_data)}</p>
        <p><b>Pothole Details:</b></p>
        <ul>
            {severity_summary}
        </ul>
        """
    )

    for file_path in files:
        with open(file_path, 'rb') as f:
            file_data = f.read()
            encoded_file_data = base64.b64encode(file_data).decode()
            file_name = os.path.basename(file_path)

            encoded_file = Attachment(
                FileContent(encoded_file_data),
                FileName(file_name),
                FileType("image/jpeg"),
                Disposition("attachment")
            )

            message.add_attachment(encoded_file)

    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"Email sent! Status Code: {response.status_code}")
    except Exception as e:
        print(f"Error sending email: {e}")

# Load YOLO model
model = YOLO(MlModel)

# Capture from webcam instead of video file
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Unable to access camera.")
    exit()

frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = 20

output_dir = "/home/sai/Documents/pothole_detection"
frames_dir = os.path.join(output_dir, "frames")
os.makedirs(frames_dir, exist_ok=True)

video_output_path = os.path.join(output_dir, "pothole_detection.avi")
fourcc = cv2.VideoWriter_fourcc(*'XVID')
video_writer = cv2.VideoWriter(video_output_path, fourcc, fps, (frame_width, frame_height))

print("Real-Time Pothole Detection from Camera Initialized. Press 'q' to quit.")

frame_count = 0
pothole_data = []

while True:
    ret, frame = cap.read()
    if not ret:
        print("Camera feed failed.")
        break

    results = model.predict(frame, conf=0.1)
    annotated_frame = results[0].plot() if hasattr(results[0], "plot") else frame
    frame_output_path = os.path.join(frames_dir, f"frame_{frame_count}.jpg")
    cv2.imwrite(frame_output_path, annotated_frame)

    video_writer.write(annotated_frame)
    cv2.imshow('Pothole Detection', annotated_frame)

    for bbox in results[0].boxes.xyxy:
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
        area = width * height

        if area < 5000:
            severity = "Minor"
            suggestion = "Cold Mix Asphalt repair recommended."
        elif 5000 <= area < 20000:
            severity = "Moderate"
            suggestion = "Hot Mix Asphalt repair recommended."
        else:
            severity = "Severe"
            suggestion = "Full Depth Repair required."

        pothole_data.append({
            "severity": severity,
            "repair_suggestion": suggestion
        })

    latlng = get_gps_coordinates()
    if latlng and all(latlng):
        send_email(latlng, [frame_output_path], pothole_data)

    frame_count += 1

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
video_writer.release()
cv2.destroyAllWindows()

print(f"Pothole detection completed.")
print(f"Annotated video saved to: {video_output_path}")
print(f"Annotated frames saved to: {frames_dir}")
