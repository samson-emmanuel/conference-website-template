from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime
import sqlite3
import os

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.secret_key = "super_secret_key"  # Required for flash messages

# Ensure the uploads folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Database Configuration
DATABASE_FILE = "contact_messages.db"

# Initialize the database and create tables if they don't exist
if not os.path.exists(DATABASE_FILE):
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()

        # Table for contact messages
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        number TEXT NOT NULL,
        subject TEXT NOT NULL,
        message TEXT NOT NULL
            )
        ''')

        # Table for questions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL
            )
        ''')
        conn.commit()


# Helper function to check allowed file types
def allowed_file(filename):
    return "." in filename and os.path.splitext(filename)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    """Home Page"""
    return render_template("index.html")


@app.route("/ask-question", methods=["POST"])
def ask_question():
    """Endpoint to handle question submission"""
    data = request.get_json()
    question = data.get("question")

    if question:
        # Insert the question into the database
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO questions (question) VALUES (?)", (question,))
            conn.commit()
        return jsonify({"status": "success", "message": "Question submitted successfully!"})
    return jsonify({"status": "error", "message": "Question is required"}), 400


@app.route("/about")
def about():
    """About Page"""
    return render_template("about.html")


@app.route('/previous_year_images')
def previous_year_images():
    image_folder = os.path.join(app.static_folder, 'conference2024')
    images = [f for f in os.listdir(image_folder) if os.path.isfile(os.path.join(image_folder, f))]
    return render_template('previous_year_images.html', images=images)

@app.route("/gallery", methods=["GET", "POST"])
def gallery():
    """Gallery Page - Handles Image Upload and Display"""
    if request.method == "POST":
        uploaded_file = request.files.get("image")
        if uploaded_file and uploaded_file.filename and allowed_file(uploaded_file.filename):
            # Generate a unique filename using a timestamp
            filename, extension = os.path.splitext(uploaded_file.filename)
            unique_filename = f"{filename}_{datetime.now().strftime('%Y%m%d%H%M%S')}{extension}"
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_filename)
            uploaded_file.save(file_path)
            flash("Image uploaded successfully!", "success")
            return redirect(url_for("gallery"))

    # Retrieve all images from the uploads folder
    gallery_images = [
        file
        for file in os.listdir(app.config["UPLOAD_FOLDER"])
        if os.path.isfile(os.path.join(app.config["UPLOAD_FOLDER"], file))
        and allowed_file(file)
    ]
    return render_template("gallery.html", images=gallery_images)


# @app.route("/schedule")
# def schedule():
#     """Schedule Page"""
#     events = [
#         {"time": "10:00 AM", "title": "Opening Ceremony", "description": "Welcoming guests."},
#         {"time": "11:00 AM", "title": "Keynote Speech", "description": "Speech by a renowned speaker."},
#         {"time": "1:00 PM", "title": "Lunch Break", "description": "Buffet lunch for attendees."},
#     ]
#     return render_template("schedule.html", events=events)

@app.route("/contact", methods=["GET", "POST"])
def contact():
    """Contact Page - Handles Messages with Database"""
    if request.method == "POST":
        # Get form data
        name = request.form.get("name")
        email = request.form.get("email")
        number = request.form.get("number")
        subject = request.form.get("subject")
        message = request.form.get("message")

        # Validate inputs
        if not all([name, email, number, subject, message]):
            flash("All fields are required. Please fill in the form completely.", "danger")
            return redirect(url_for("contact"))

        try:
            # Insert the message into the database
            with sqlite3.connect(DATABASE_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO messages (name, email, number, subject, message) 
                    VALUES (?, ?, ?, ?, ?)
                """, (name, email, number, subject, message))
                conn.commit()
            flash("Message sent successfully!", "success")
        except Exception as e:
            flash(f"An error occurred: {e}", "danger")
            return redirect(url_for("contact"))

    # Retrieve all messages (optional, for admin view/debugging)
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name, email, number, subject, message FROM messages")
        messages = [
            {
                "name": row[0],
                "email": row[1],
                "number": row[2],
                "subject": row[3],
                "message": row[4],
            }
            for row in cursor.fetchall()
        ]

    return render_template("contact.html", messages=messages)



if __name__ == "__main__":
    app.run(debug=True)

