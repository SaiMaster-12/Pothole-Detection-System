import cv2
import os
import base64  # For base64 encoding
from ultralytics import YOLO
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition

# Path to your trained YOLO model (ensure this is your pothole detection model)
MlModel = "/Users/saimaster/Desktop/Programs/Major/ML_Model/best.pt"

# Your SendGrid API Key
SENDGRID_API_KEY = "" # Replace with your SendGrid API Key

# Function to send an email with attachments
def send_email(location, files):
    message = Mail(
        from_email="",  # Replace with your verified SendGrid sender email
        to_emails="",  # Recipient's email
        subject="Pothole Detected",
        html_content=f"""
        <p><b>Pothole Detected!</b></p>
        <p>Location details:</p>
        <ul>
            <li><b>Latitude:</b> {location[0]}</li>
            <li><b>Longitude:</b> {location[1]}</li>
        </ul>
        """
    )

    for file_path in files:
        with open(file_path, 'rb') as f:
            file_data = f.read()
            encoded_file_data = base64.b64encode(file_data).decode()  # Base64 encode and convert to string
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

# Load the trained YOLOv8 model
model = YOLO(MlModel)

# Open webcam feed
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Unable to access the webcam.")
    exit()

frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(cap.get(cv2.CAP_PROP_FPS))

output_dir = "C:\\Users\\dines\\Downloads\\Out_vid\\frames"
frames_dir = os.path.join(output_dir, "frames")
os.makedirs(frames_dir, exist_ok=True)

video_output_path = os.path.join(output_dir, "pothole_detection.avi")
fourcc = cv2.VideoWriter_fourcc(*'XVID')
video_writer = cv2.VideoWriter(video_output_path, fourcc, fps, (frame_width, frame_height))

print("Real-Time Pothole Detection Initialized. Press 'q' to quit.")

frame_count = 0
while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Unable to capture frame.")
        break

    # Run YOLOv8 on the frame
    results = model.predict(
        source=frame,
        save=True,
        project=output_dir,
        name="video_results"
    )

    annotated_frame = results[0].plot() if hasattr(results[0], "plot") else frame

    frame_output_path = os.path.join(frames_dir, f"frame_{frame_count}.jpg")
    cv2.imwrite(frame_output_path, annotated_frame)

    video_writer.write(annotated_frame)
    cv2.imshow('Pothole Detection', annotated_frame)
    frame_count += 1

    # Dummy GPS location for demonstration
    location = (12.9716, 77.5946)  # Replace with actual GPS coordinates from a GPS module

    # Send email if pothole is detected
    if len(results[0].boxes) > 0:  # Assuming boxes attribute holds detections
        send_email(location, [frame_output_path])

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
video_writer.release()
cv2.destroyAllWindows()

print(f"Pothole detection completed.")
print(f"Annotated video saved to: {video_output_path}")
print(f"Annotated frames saved to: {frames_dir}")
