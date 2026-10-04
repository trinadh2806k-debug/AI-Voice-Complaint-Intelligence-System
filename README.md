# AI Voice Complaint Intelligence System

An AI-based complaint management system built using Python Flask. Users can submit complaints using text or voice. The system automatically classifies the complaint department, detects customer emotion, assigns priority, and stores complaint records.

## Project Structure

ai_voice_complaint_intelligence/
│
├── app.py
├── requirements.txt
├── README.md
│
├── templates/
│   ├── index.html
│   ├── complaint.html
│   ├── success.html
│   └── dashboard.html
│
├── static/
│   └── css/
│       └── style.css
│
├── uploads/
└── data/
    └── complaints.csv

## Features

- Submit complaints using text
- Upload voice complaints in WAV, MP3, M4A, or OGG format
- Convert voice complaints to text using SpeechRecognition
- Automatically detect complaint department
- Automatically detect customer emotion
- Automatically assign complaint priority
- Generate unique complaint ID
- Store complaints in CSV file
- Admin dashboard with complaint statistics
- Department-wise complaint chart
- Customer emotion chart
- Update complaint status to Resolved
- Responsive Bootstrap design

## Supported Departments

- Electricity
- Water
- Road
- Garbage
- Internet
- General

## Supported Emotions

- Angry
- Sad
- Fear
- Happy
- Neutral

## Priority Levels

- High
- Medium
- Low

## Technologies Used

- Python
- Flask
- HTML
- CSS
- Bootstrap 5
- Bootstrap Icons
- Chart.js
- SpeechRecognition
- CSV file storage

## Installation

1. Install Python 3.10 or above.
2. Open the project folder in VS Code.
3. Open a terminal in VS Code.
4. Create a virtual environment:

```bash
python -m venv venv
```

5. Activate the virtual environment:

Windows:

```bash
venv\Scripts\activate
```

macOS/Linux:

```bash
source venv/bin/activate
```

6. Install requirements:

```bash
pip install -r requirements.txt
```

7. Run the application:

```bash
python app.py
```

8. Open the browser and visit:

```text
http://127.0.0.1:5000
```

## How to Use

1. Open the home page.
2. Click **Submit Complaint**.
3. Enter name and email.
4. Type a complaint or upload a voice complaint.
5. Click **Submit Complaint**.
6. The system creates a Complaint ID.
7. Open **Admin Dashboard** to view complaint details.
8. Click **Resolve** to change complaint status.

## Example Complaints

Electricity complaint:

```text
There is no electricity in my street since morning. Please solve this urgent problem.
```

Water complaint:

```text
Water pipeline is leaking near my house and causing drainage problems.
```

Road complaint:

```text
There is a large pothole on the main road which may cause accidents.
```

## Future Enhancements

- Login and admin authentication
- Cloud database integration
- Real-time voice recording
- AI-based speech emotion detection
- Complaint tracking using Complaint ID
- Email and SMS notifications
- Cloud deployment using AWS, Azure, or Google Cloud
