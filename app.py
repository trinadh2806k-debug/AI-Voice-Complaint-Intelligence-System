from flask import Flask, render_template, request, redirect, url_for, jsonify, send_from_directory
import os
import uuid
import csv
from datetime import datetime
from werkzeug.utils import secure_filename

try:
    import speech_recognition as sr
    SPEECH_SUPPORT = True
except ImportError:
    SPEECH_SUPPORT = False

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["DATA_FILE"] = "data/complaints.csv"

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
os.makedirs("data", exist_ok=True)

ALLOWED_EXTENSIONS = {"wav", "mp3", "m4a", "ogg"}

DEPARTMENTS = {
    "electricity": ["power", "electricity", "current", "transformer", "street light", "wire", "voltage"],
    "water": ["water", "tap", "pipeline", "drainage", "sewage", "leak", "borewell"],
    "road": ["road", "pothole", "street", "traffic", "signal", "footpath", "bridge"],
    "garbage": ["garbage", "waste", "trash", "dustbin", "cleaning", "sanitation", "dirty"],
    "internet": ["internet", "network", "wifi", "server", "website", "portal", "login"],
    "general": ["complaint", "problem", "issue", "help", "support"]
}

EMOTION_WORDS = {
    "Angry": ["angry", "anger", "furious", "irritated", "annoyed", "hate", "worst", "terrible", "pathetic", "useless"],
    "Sad": ["sad", "upset", "disappointed", "depressed", "unhappy", "poor", "helpless", "hopeless"],
    "Fear": ["afraid", "scared", "fear", "worried", "worry", "anxious", "panic", "unsafe", "danger"],
    "Happy": ["happy", "good", "great", "thanks", "thank you", "satisfied", "excellent", "appreciate"],
    "Neutral": []
}

PRIORITY_WORDS = {
    "High": ["urgent", "immediately", "emergency", "danger", "accident", "fire", "injury", "serious", "critical", "unsafe"],
    "Medium": ["delay", "pending", "problem", "issue", "complaint", "not working", "broken"],
    "Low": ["request", "suggestion", "improve", "minor", "later"]
}


def init_csv():
    if not os.path.exists(app.config["DATA_FILE"]):
        with open(app.config["DATA_FILE"], "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([
                "id", "date", "name", "email", "category",
                "priority", "emotion", "status", "complaint_text", "audio_file"
            ])


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def classify_department(text):
    text = text.lower()
    scores = {}

    for department, words in DEPARTMENTS.items():
        score = sum(1 for word in words if word in text)
        scores[department] = score

    best = max(scores, key=scores.get)

    if scores[best] == 0:
        return "General"

    return best.capitalize()


def detect_emotion(text):
    text = text.lower()
    scores = {}

    for emotion, words in EMOTION_WORDS.items():
        if emotion == "Neutral":
            continue
        scores[emotion] = sum(1 for word in words if word in text)

    best = max(scores, key=scores.get)

    if scores[best] == 0:
        return "Neutral"

    return best


def detect_priority(text):
    text = text.lower()

    for priority, words in PRIORITY_WORDS.items():
        if any(word in text for word in words):
            return priority

    return "Medium"


def transcribe_audio(file_path):
    if not SPEECH_SUPPORT:
        return "Speech recognition library is not installed."

    recognizer = sr.Recognizer()

    try:
        with sr.AudioFile(file_path) as source:
            audio = recognizer.record(source)

        return recognizer.recognize_google(audio)

    except sr.UnknownValueError:
        return "Sorry, the voice complaint could not be understood."

    except sr.RequestError:
        return "Speech recognition service is unavailable."

    except Exception:
        return "Unable to process the uploaded audio file."


def read_complaints():
    init_csv()

    with open(app.config["DATA_FILE"], "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        return list(reader)


def save_complaint(data):
    init_csv()

    with open(app.config["DATA_FILE"], "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(data)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/complaint")
def complaint():
    return render_template("complaint.html", speech_support=SPEECH_SUPPORT)


@app.route("/dashboard")
def dashboard():
    complaints = read_complaints()

    total = len(complaints)
    high = len([c for c in complaints if c["priority"] == "High"])
    pending = len([c for c in complaints if c["status"] == "Pending"])
    resolved = len([c for c in complaints if c["status"] == "Resolved"])

    categories = {}
    emotions = {}

    for complaint in complaints:
        categories[complaint["category"]] = categories.get(complaint["category"], 0) + 1
        emotions[complaint["emotion"]] = emotions.get(complaint["emotion"], 0) + 1

    return render_template(
        "dashboard.html",
        complaints=complaints,
        total=total,
        high=high,
        pending=pending,
        resolved=resolved,
        categories=categories,
        emotions=emotions
    )


@app.route("/submit_complaint", methods=["POST"])
def submit_complaint():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    complaint_text = request.form.get("complaint_text", "").strip()
    audio = request.files.get("audio")

    audio_filename = ""
    transcribed_text = ""

    if audio and audio.filename != "" and allowed_file(audio.filename):
        filename = secure_filename(audio.filename)
        unique_name = str(uuid.uuid4()) + "_" + filename
        audio_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_name)
        audio.save(audio_path)

        audio_filename = unique_name
        transcribed_text = transcribe_audio(audio_path)

    final_text = complaint_text or transcribed_text

    if not final_text:
        return render_template(
            "complaint.html",
            speech_support=SPEECH_SUPPORT,
            error="Please enter a complaint or upload a voice complaint."
        )

    category = classify_department(final_text)
    emotion = detect_emotion(final_text)
    priority = detect_priority(final_text)

    complaint_id = "CMP" + str(uuid.uuid4())[:8].upper()

    data = [
        complaint_id,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        name,
        email,
        category,
        priority,
        emotion,
        "Pending",
        final_text,
        audio_filename
    ]

    save_complaint(data)

    return redirect(url_for("success", complaint_id=complaint_id))


@app.route("/success")
def success():
    complaint_id = request.args.get("complaint_id", "")
    return render_template("success.html", complaint_id=complaint_id)


@app.route("/update_status/<complaint_id>/<status>")
def update_status(complaint_id, status):
    complaints = read_complaints()

    for complaint in complaints:
        if complaint["id"] == complaint_id:
            complaint["status"] = status

    with open(app.config["DATA_FILE"], "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "id", "date", "name", "email", "category",
                "priority", "emotion", "status", "complaint_text", "audio_file"
            ]
        )
        writer.writeheader()
        writer.writerows(complaints)

    return redirect(url_for("dashboard"))


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


if __name__ == "__main__":
    init_csv()
    app.run(debug=True)
