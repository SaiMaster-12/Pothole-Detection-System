# Pothole Detection System

## Overview
The **Pothole Detection System** is a real-time computer vision-based solution that detects potholes on roads using the YOLOv8 object detection model. It leverages a Raspberry Pi 4 for on-device processing and automatically sends **email notifications to the road authority manager** upon detecting a pothole.

---

## Features

- Real-time pothole detection using YOLOv8
- Lightweight deployment using Raspberry Pi 4
- Automated email alert system to notify road inspectors
- High accuracy object detection in varying lighting and weather conditions
- Scalable and cost-effective solution for urban infrastructure monitoring

---

## Tech Stack

| Component        | Technology Used            |
|------------------|----------------------------|
| Object Detection | YOLOv8                     |
| Hardware         | Raspberry Pi 4             |
| Programming      | Python                     |
| Email Service    | SendGrid API               |
| Notifications    | Email to road authority    |

---

## How It Works

1. The Raspberry Pi captures live video using a connected camera module.
2. YOLOv8 processes each frame to detect potholes in real time.
3. If potholes are detected:
   - The total count is calculated.
   - Severity is assessed (Minor, Moderate, Severe).
   - Suggestions are generated based on severity.
   - The current location is obtained using the **Neo 6M GPS module**.
   - An email is sent to the designated road authority with all the above info and an image of the pothole(s).
4. The system continuously monitors the road and sends updates as necessary.
5. The road authority can use this information to prioritize maintenance and repairs.

---

## Setup Instructions

### 1. Raspberry Pi 4 Setup

- Install Raspberry Pi OS (32-bit Lite or Desktop) using the [Raspberry Pi Imager](https://www.raspberrypi.com/software/)
- Boot and connect to Wi-Fi
- Update packages:

```bash
sudo apt update && sudo apt upgrade -y
```

- Enable camera module using:

```bash
sudo raspi-config
# Navigate to Interfaces > Camera > Enable
```

- Install Python and pip:

```bash
sudo apt install python3 python3-pip -y
```
- enable SSH for remote access:

```bash
sudo systemctl enable ssh
sudo systemctl start ssh
```

### 2. Install Required Software

- Install `git`:

```bash
sudo apt install git -y
```

### 3. Clone the Repository

```bash
git clone https://github.com/saimaster-12/pothole-detection-system.git
cd pothole-detection-system
```

### 4. Install Dependencies

```bash
pip3 install -r requirements.txt
```

Requirements include:
- `ultralytics`
- `opencv-python`
- `sendgrid`
- `email` (built-in)
- `geopy`
- `serial` (for GPS communication)

### 5. Load the YOLOv8 Model

A pre-trained YOLOv8 model (.pt file) for pothole detection is already included and available in the project directory. You can use this model or replace it with your own.

### 6. Configure Email Settings

Edit `Main1.py`:

```python
SENDGRID_API_KEY=''
TO_EMAIL=''
FROM_EMAIL=''
```

Ensure you use an app-specific password if you're using Gmail with 2FA.

### 7. Run the Detection Script

```bash
python Main1.py
```

---

## Email Notification Format

When a pothole is detected, the system sends an email with:
1. Subject: `Pothole Detected Alert`
2. Body:
   - Number of potholes detected
   - Severity (Minor, Moderate, Severe)
   - Suggestions based on severity
   - GPS coordinates (latitude, longitude)
3. Attachment: Captured image of the pothole(s)

---

## GPS Integration

1. The system uses a Neo 6M GPS module to fetch real-time location data.
2. GPS data (latitude and longitude) is extracted using pyserial or similar libraries.
3. Ensure the GPS module is connected via UART (e.g., /dev/ttyS0 on Raspberry Pi) and has a clear view of the sky for accurate readings.
4. The GPS module's baud rate and other settings should be configured in the code.
5. The system will send the GPS coordinates along with the email notification.

---

