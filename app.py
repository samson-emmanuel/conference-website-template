from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime
import os
import secrets
import pandas as pd
import mysql.connector
from mysql.connector import errorcode
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user,
    current_user,
)
from flask_mail import Mail, Message
import psycopg2 

app = Flask(__name__)

# Configuration
DATABASE_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Oungbogbololese100%',
    'database': 'lafargeConferenceSite'
}
UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.secret_key = secrets.token_hex(16)



app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USE_SSL=False,
    MAIL_USERNAME='samson.emmanuel.ext@lafarge.com',
    MAIL_PASSWORD='Masterstickings100%',
    MAIL_DEFAULT_SENDER='uploading@example.com'
)

mail = Mail(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Load the data from the Excel file
file_path = "static/2025_LC_DELEGATE_PROFILE.xlsx"
df = pd.read_excel(file_path, sheet_name="Getting to Know the Delegates")


def connect_to_database():
    """Establish a MySQL database connection."""
    try:
        conn = mysql.connector.connect(**DATABASE_CONFIG)
        return conn
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Invalid credentials.")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist.")
        else:
            print(err)
        return None


# Initialize the database and create tables if they don't exist
def initialize_database():
    conn = connect_to_database()
    if conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS images (
                id INT AUTO_INCREMENT PRIMARY KEY,
                filename VARCHAR(255) NOT NULL,
                upload_time DATETIME NOT NULL,
                approved BOOLEAN DEFAULT 0
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS admins (
                id INT AUTO_INCREMENT PRIMARY KEY,
                email VARCHAR(255) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL,
                number VARCHAR(20) NOT NULL,
                subject VARCHAR(255) NOT NULL,
                message TEXT NOT NULL
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS questions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                question TEXT NOT NULL
            )
            """
        )
        # Insert demo admin user if not already present
        cursor.execute("SELECT COUNT(*) FROM admins")
        if cursor.fetchone()[0] == 0:
            cursor.execute(
                "INSERT INTO admins (email, password) VALUES (%s, %s)",
                ("demo@example.com", "demo_password"),
            )
        conn.commit()
        cursor.close()
        conn.close()


initialize_database()


# Admin User Model
class Admin(UserMixin):
    def __init__(self, id, email):
        self.id = id
        self.email = email


@login_manager.user_loader
def load_user(user_id):
    conn = connect_to_database()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM admins WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        if user:
            return Admin(user["id"], user["email"])
    return None


def allowed_file(filename):
    return (
        "." in filename and os.path.splitext(filename)[1].lower() in ALLOWED_EXTENSIONS
    )


@app.route("/know_your_delegates")
def know_your_delegates():
    profiles = df.head(30).to_dict(orient="records")
    return render_template("know_your_delegates.html", profiles=profiles)


@app.route("/load_more", methods=["POST"])
def load_more():
    try:
        start = int(request.form.get("start", 0))
        end = start + 10

        if start >= len(df):
            return jsonify([])

        profiles = df.iloc[start:end].fillna("").to_dict(orient="records")
        return jsonify(profiles)
    except Exception as e:
        print(f"Error in /load_more: {e}")
        return jsonify({"error": "Failed to load more profiles."}), 500


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        conn = connect_to_database()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM admins WHERE email = %s", (email,))
            admin = cursor.fetchone()
            cursor.close()
            conn.close()
            if admin and admin["password"] == password:
                user = Admin(admin["id"], admin["email"])
                login_user(user)
                return redirect(url_for("admin_dashboard"))

        flash("Invalid credentials. Please try again.", "danger")
        return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


# @app.route("/gallery", methods=["GET", "POST"])
# def gallery():
#     if request.method == "POST":
#         uploaded_file = request.files.get("image")
#         if (
#             uploaded_file
#             and uploaded_file.filename
#             and allowed_file(uploaded_file.filename)
#         ):
#             filename, extension = os.path.splitext(uploaded_file.filename)
#             unique_filename = (
#                 f"{filename}_{datetime.now().strftime('%Y%m%d%H%M%S')}{extension}"
#             )
#             file_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_filename)
#             uploaded_file.save(file_path)

#             conn = connect_to_database()
#             if conn:
#                 cursor = conn.cursor()
#                 cursor.execute(
#                     """
#                     INSERT INTO images (filename, upload_time, approved)
#                     VALUES (%s, %s, %s)
#                     """,
#                     (unique_filename, datetime.now(), 0),
#                 )
#                 conn.commit()
#                 cursor.close()
#                 conn.close()

#             flash("Image uploaded successfully and pending approval!", "success")
#             return redirect(url_for("gallery"))

#     conn = connect_to_database()
#     gallery_images = []
#     if conn:
#         cursor = conn.cursor()
#         cursor.execute("SELECT filename FROM images WHERE approved = 1")
#         gallery_images = [row[0] for row in cursor.fetchall()]
#         cursor.close()
#         conn.close()

#     return render_template("gallery.html", images=gallery_images)

@app.route("/gallery", methods=["GET", "POST"])
def gallery():
    if request.method == "POST":
        uploaded_file = request.files.get("image")
        if (
            uploaded_file
            and uploaded_file.filename
            and allowed_file(uploaded_file.filename)
        ):
            filename, extension = os.path.splitext(uploaded_file.filename)
            unique_filename = (
                f"{filename}_{datetime.now().strftime('%Y%m%d%H%M%S')}{extension}"
            )
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_filename)
            uploaded_file.save(file_path)

            conn = connect_to_database()
            if conn:
                try:
                    cursor = conn.cursor()
                    cursor.execute(
                        """
                        INSERT INTO images (filename, upload_time, approved)
                        VALUES (%s, %s, %s)
                        """,
                        (unique_filename, datetime.now(), 0),
                    )
                    conn.commit()
                    cursor.close()
                    
                    # Send email notification
                    try:
                        msg = Message(
                            "New Image Uploaded",
                            recipients=["samaiyex@gmail.com.com"]
                        )
                        msg.body = (
                            f"A new image has been uploaded and is awaiting approval.\n"
                            f"Filename: {unique_filename}\n"
                            f"Uploaded at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                        )
                        mail.send(msg)
                        flash("Image uploaded successfully and pending approval! Email notification sent.", "success")
                    except Exception as email_error:
                        flash(f"Image uploaded successfully, but email failed to send: {email_error}", "warning")

                except Exception as db_error:
                    flash(f"Failed to upload image: {db_error}", "danger")
                finally:
                    conn.close()
            else:
                flash("Database connection failed!", "danger")

            return redirect(url_for("gallery"))

    conn = connect_to_database()
    gallery_images = []
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT filename FROM images WHERE approved = 1")
            gallery_images = [row[0] for row in cursor.fetchall()]
            cursor.close()
        except Exception as db_error:
            flash(f"Error fetching images: {db_error}", "danger")
        finally:
            conn.close()

    return render_template("gallery.html", images=gallery_images)


@app.route("/admin-dashboard")
@login_required
def admin_dashboard():
    conn = connect_to_database()
    if conn:
        cursor = conn.cursor(dictionary=True)

        # Fetch images, messages, and questions
        cursor.execute("SELECT id, filename, approved FROM images")
        images = cursor.fetchall()

        cursor.execute("SELECT id, name, email, number, subject, message FROM messages")
        messages = cursor.fetchall()

        cursor.execute("SELECT id, question FROM questions")
        questions = cursor.fetchall()

        cursor.close()
        conn.close()

        # Separate images into approved and unapproved
        approved_images = [img for img in images if img["approved"]]
        unapproved_images = [img for img in images if not img["approved"]]

        return render_template(
            "admin_dashboard.html",
            approved_images=approved_images,
            unapproved_images=unapproved_images,
            messages=messages,
            questions=questions,
        )



@app.route("/approve-image/<int:image_id>", methods=["POST"])
@login_required
def approve_image(image_id):
    conn = connect_to_database()
    if conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE images SET approved = 1 WHERE id = %s", (image_id,))
        conn.commit()
        cursor.close()
        conn.close()
    flash("Image approved successfully!", "success")
    return redirect(url_for("admin_dashboard"))


@app.route("/delete-image/<int:image_id>", methods=["POST"])
@login_required
def delete_image(image_id):
    conn = connect_to_database()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT filename FROM images WHERE id = %s", (image_id,))
        image = cursor.fetchone()
        if image:
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], image["filename"])
            if os.path.exists(file_path):
                os.remove(file_path)
            cursor.execute("DELETE FROM images WHERE id = %s", (image_id,))
            conn.commit()
        cursor.close()
        conn.close()
    flash("Image deleted successfully!", "success")
    return redirect(url_for("admin_dashboard"))

@app.route("/add-admin", methods=["GET", "POST"])
@login_required
def add_admin():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        conn = connect_to_database()
        if conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO admins (email, password) VALUES (%s, %s)",
                (email, password),
            )
            conn.commit()
            cursor.close()
            conn.close()
        flash("New admin added successfully!", "success")
        return redirect(url_for("manage_admins"))
    return render_template("add_admin.html")

import logging
logging.basicConfig(level=logging.DEBUG)

@app.route("/admins", methods=["GET"])
@login_required
def manage_admins():
    conn = connect_to_database()
    admins = []
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, email FROM admins")
        admins = cursor.fetchall()
        cursor.close()
        conn.close()
    logging.debug(f"Admins fetched: {admins}")
    return render_template("manage_admins.html", admins=admins)



@app.route("/delete-admin/<int:admin_id>", methods=["POST"])
@login_required
def delete_admin(admin_id):
    conn = connect_to_database()
    if conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM admins WHERE id = %s", (admin_id,))
        conn.commit()
        cursor.close()
        conn.close()
    flash("Admin account deleted successfully!", "success")
    return redirect(url_for("manage_admins"))

@app.route("/delete-message/<int:message_id>", methods=["POST"])
@login_required
def delete_message(message_id):
    conn = connect_to_database()
    if conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM messages WHERE id = %s", (message_id,))
        conn.commit()
        cursor.close()
        conn.close()
    flash("Message deleted successfully!", "success")
    return redirect(url_for("admin_dashboard"))


@app.route("/delete-question/<int:question_id>", methods=["POST"])
@login_required
def delete_question(question_id):
    conn = connect_to_database()
    if conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM questions WHERE id = %s", (question_id,))
        conn.commit()
        cursor.close()
        conn.close()
    flash("Question deleted successfully!", "success")
    return redirect(url_for("admin_dashboard"))


def get_speaker_by_id(speaker_id):
    conn = connect_to_database()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM speakers WHERE id = %s", (speaker_id,))
        speaker = cursor.fetchone()
        cursor.close()
        conn.close()
        return speaker
    return None

@app.route("/previous_year_images")
def previous_year_images():
    image_folder = os.path.join(app.static_folder, "conference2024")
    images = [
        f
        for f in os.listdir(image_folder)
        if os.path.isfile(os.path.join(image_folder, f))
    ]
    return render_template("previous_year_images.html", images=images)

@app.route("/")
def index():
    conn = connect_to_database()
    speakers = []
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT id, name, position, image_url, facebook_url, twitter_url, linkedin_url
            FROM speakers
            """
        )
        speakers = cursor.fetchall()
        cursor.close()
        conn.close()
    return render_template("index.html", speakers=speakers)

@app.route("/ask")
def ask():
    return render_template("ask.html")


@app.route("/ask-question", methods=["POST"])
def ask_question():
    data = request.get_json()
    question = data.get("question")

    if question:
        conn = connect_to_database()
        if conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO questions (question) VALUES (%s)", (question,))
            conn.commit()
            cursor.close()
            conn.close()
        return jsonify({"status": "success", "message": "Question submitted successfully!"})
    return jsonify({"status": "error", "message": "Question is required"}), 400


@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/speaker/<int:speaker_id>")
def speaker_page(speaker_id):
    speaker = get_speaker_by_id(speaker_id)
    if not speaker:
        return "Speaker not found", 404

    # Ensure correct path for static images
    speaker['image_url'] = url_for('static', filename=f'images/{speaker["image_url"]}')
    return render_template("speaker.html", speaker=speaker)



@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        number = request.form.get("number")
        subject = request.form.get("subject")
        message = request.form.get("message")

        if not all([name, email, number, subject, message]):
            flash("All fields are required. Please fill in the form completely.", "danger")
            return redirect(url_for("contact"))

        conn = connect_to_database()
        if conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO messages (name, email, number, subject, message)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (name, email, number, subject, message),
            )
            conn.commit()
            cursor.close()
            conn.close()

        flash("Message sent successfully!", "success")
        return redirect(url_for("contact"))

    conn = connect_to_database()
    messages = []
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT name, email, number, subject, message FROM messages")
        messages = cursor.fetchall()
        cursor.close()
        conn.close()

    return render_template("contact.html", messages=messages)


@app.route('/event-highlights')
def event_highlights():
    return render_template('event_highlight.html')



if __name__ == "__main__":
    app.run(debug=True)
