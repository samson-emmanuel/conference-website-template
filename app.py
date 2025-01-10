# from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
# from datetime import datetime
# import sqlite3
# import os

# app = Flask(__name__)

# # Configuration
# UPLOAD_FOLDER = "static/uploads"
# ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif"}
# app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
# app.secret_key = "super_secret_key"  # Required for flash messages

# # Ensure the uploads folder exists
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# # Database Configuration
# DATABASE_FILE = "contact_messages.db"

# # Initialize the database and create tables if they don't exist
# if not os.path.exists(DATABASE_FILE):
#     with sqlite3.connect(DATABASE_FILE) as conn:
#         cursor = conn.cursor()

#         # Table for contact messages
#         cursor.execute(
#             """
#             CREATE TABLE IF NOT EXISTS messages (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         name TEXT NOT NULL,
#         email TEXT NOT NULL,
#         number TEXT NOT NULL,
#         subject TEXT NOT NULL,
#         message TEXT NOT NULL
#             )
#         """
#         )

#         # Table for questions
#         cursor.execute(
#             """
#             CREATE TABLE IF NOT EXISTS questions (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 question TEXT NOT NULL
#             )
#         """
#         )
#         conn.commit()


# # Helper function to check allowed file types
# def allowed_file(filename):
#     return (
#         "." in filename and os.path.splitext(filename)[1].lower() in ALLOWED_EXTENSIONS
#     )


# @app.route("/")
# def index():
#     """Home Page"""
#     return render_template("index.html")


# @app.route("/ask-question", methods=["POST"])
# def ask_question():
#     """Endpoint to handle question submission"""
#     data = request.get_json()
#     question = data.get("question")

#     if question:
#         # Insert the question into the database
#         with sqlite3.connect(DATABASE_FILE) as conn:
#             cursor = conn.cursor()
#             cursor.execute("INSERT INTO questions (question) VALUES (?)", (question,))
#             conn.commit()
#         return jsonify(
#             {"status": "success", "message": "Question submitted successfully!"}
#         )
#     return jsonify({"status": "error", "message": "Question is required"}), 400


# @app.route("/about")
# def about():
#     """About Page"""
#     return render_template("about.html")


# @app.route("/previous_year_images")
# def previous_year_images():
#     image_folder = os.path.join(app.static_folder, "conference2024")
#     images = [
#         f
#         for f in os.listdir(image_folder)
#         if os.path.isfile(os.path.join(image_folder, f))
#     ]
#     return render_template("previous_year_images.html", images=images)


# @app.route("/gallery", methods=["GET", "POST"])
# def gallery():
#     """Gallery Page - Handles Image Upload and Display"""
#     if request.method == "POST":
#         uploaded_file = request.files.get("image")
#         if (
#             uploaded_file
#             and uploaded_file.filename
#             and allowed_file(uploaded_file.filename)
#         ):
#             # Generate a unique filename using a timestamp
#             filename, extension = os.path.splitext(uploaded_file.filename)
#             unique_filename = (
#                 f"{filename}_{datetime.now().strftime('%Y%m%d%H%M%S')}{extension}"
#             )
#             file_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_filename)
#             uploaded_file.save(file_path)
#             flash("Image uploaded successfully!", "success")
#             return redirect(url_for("gallery"))

#     # Retrieve all images from the uploads folder
#     gallery_images = [
#         file
#         for file in os.listdir(app.config["UPLOAD_FOLDER"])
#         if os.path.isfile(os.path.join(app.config["UPLOAD_FOLDER"], file))
#         and allowed_file(file)
#     ]
#     return render_template("gallery.html", images=gallery_images)


# @app.route('/speaker/<int:speaker_id>')
# def speaker_page(speaker_id):
#     speaker = get_speaker_by_id(speaker_id)  # Fetch speaker details from database or predefined data
#     return render_template('speaker.html', speaker=speaker)


# @app.route("/contact", methods=["GET", "POST"])
# def contact():
#     """Contact Page - Handles Messages with Database"""
#     if request.method == "POST":
#         # Get form data
#         name = request.form.get("name")
#         email = request.form.get("email")
#         number = request.form.get("number")
#         subject = request.form.get("subject")
#         message = request.form.get("message")

#         # Validate inputs
#         if not all([name, email, number, subject, message]):
#             flash(
#                 "All fields are required. Please fill in the form completely.", "danger"
#             )
#             return redirect(url_for("contact"))

#         try:
#             # Insert the message into the database
#             with sqlite3.connect(DATABASE_FILE) as conn:
#                 cursor = conn.cursor()
#                 cursor.execute(
#                     """
#                     INSERT INTO messages (name, email, number, subject, message) 
#                     VALUES (?, ?, ?, ?, ?)
#                 """,
#                     (name, email, number, subject, message),
#                 )
#                 conn.commit()
#             flash("Message sent successfully!", "success")
#         except Exception as e:
#             flash(f"An error occurred: {e}", "danger")
#             return redirect(url_for("contact"))

#     # Retrieve all messages (optional, for admin view/debugging)
#     with sqlite3.connect(DATABASE_FILE) as conn:
#         cursor = conn.cursor()
#         cursor.execute("SELECT name, email, number, subject, message FROM messages")
#         messages = [
#             {
#                 "name": row[0],
#                 "email": row[1],
#                 "number": row[2],
#                 "subject": row[3],
#                 "message": row[4],
#             }
#             for row in cursor.fetchall()
#         ]

#     return render_template("contact.html", messages=messages)


# if __name__ == "__main__":
#     app.run()


from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime
import sqlite3
import os
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)

# Configuration
DATABASE_FILE = "contact_messages.db"
UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.secret_key = "super_secret_key"  # Required for flash messages

# Ensure the uploads folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Initialize the database and create tables if they don't exist
with sqlite3.connect(DATABASE_FILE) as conn:
    cursor = conn.cursor()

    # Admins table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
        """
    )

    # Insert demo admin user if the table is empty
    cursor.execute("SELECT COUNT(*) FROM admins")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO admins (email, password) VALUES (?, ?)",
            ("demo@example.com", "demo_password"),
        )

    # Messages table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            number TEXT NOT NULL,
            subject TEXT NOT NULL,
            message TEXT NOT NULL
        )
        """
    )

    # Questions table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL
        )
        """
    )

    # Speakers table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS speakers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            position TEXT NOT NULL,
            bio TEXT NOT NULL,
            image_url TEXT NOT NULL,
            facebook_url TEXT,
            twitter_url TEXT,
            linkedin_url TEXT
        )
        """
    )

# Admin User Model
class Admin(UserMixin):
    """Model for admin users"""
    def __init__(self, id, email):
        self.id = id
        self.email = email

@login_manager.user_loader
def load_user(user_id):
    """Load admin user by ID"""
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM admins WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        if user:
            return Admin(user[0], user[1])
    return None

# Helper function to check allowed file types
def allowed_file(filename):
    """Check if a file has an allowed extension"""
    return "." in filename and os.path.splitext(filename)[1].lower() in ALLOWED_EXTENSIONS

# Helper function to fetch speaker details by ID
def get_speaker_by_id(speaker_id):
    """Retrieve speaker details by their ID"""
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM speakers WHERE id = ?", (speaker_id,))
        row = cursor.fetchone()
        if row:
            return {
                "id": row[0],
                "name": row[1],
                "position": row[2],
                "bio": row[3],
                "image_url": row[4],
                "facebook_url": row[5],
                "twitter_url": row[6],
                "linkedin_url": row[7],
            }
    return None

@app.route("/")
def index():
    """Home Page - Display list of speakers"""
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, position, image_url, facebook_url, twitter_url, linkedin_url FROM speakers")
        speakers = [
            {
                "id": row[0],
                "name": row[1],
                "position": row[2],
                "image_url": row[3],
                "facebook_url": row[4],
                "twitter_url": row[5],
                "linkedin_url": row[6],
            }
            for row in cursor.fetchall()
        ]
    return render_template("index.html", speakers=speakers)

@app.route("/gallery", methods=["GET", "POST"])
def gallery():
    """Gallery Page - Handles Image Upload and Display"""
    if request.method == "POST":
        uploaded_file = request.files.get("image")
        if (
            uploaded_file
            and uploaded_file.filename
            and allowed_file(uploaded_file.filename)
        ):
            # Generate a unique filename using a timestamp
            filename, extension = os.path.splitext(uploaded_file.filename)
            unique_filename = (
                f"{filename}_{datetime.now().strftime('%Y%m%d%H%M%S')}{extension}"
            )
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

@app.route("/previous_year_images")
def previous_year_images():
    """Page to display previous year images"""
    image_folder = os.path.join(app.static_folder, "conference2024")
    images = [
        f
        for f in os.listdir(image_folder)
        if os.path.isfile(os.path.join(image_folder, f))
    ]
    return render_template("previous_year_images.html", images=images)

@app.route("/ask")
def ask():
    """Ask Questions Page"""
    return render_template("ask.html")

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
        return jsonify(
            {"status": "success", "message": "Question submitted successfully!"}
        )
    return jsonify({"status": "error", "message": "Question is required"}), 400

@app.route("/about")
def about():
    """About Page"""
    return render_template("about.html")

@app.route("/speaker/<int:speaker_id>")
def speaker_page(speaker_id):
    """Speaker Details Page"""
    speaker = get_speaker_by_id(speaker_id)
    if not speaker:
        return "Speaker not found", 404
    return render_template("speaker.html", speaker=speaker)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Login route to authenticate admin"""
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM admins WHERE email = ?", (email,))
            admin = cursor.fetchone()
            if admin and admin[2] == password:
                user = Admin(admin[0], admin[1])
                login_user(user)
                return redirect(url_for("admin_dashboard"))

            flash("Invalid credentials. Please try again.", "danger")
            return redirect(url_for("login"))

    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    """Logout route to log out the admin"""
    logout_user()
    return redirect(url_for("login"))

# @app.route("/admin-dashboard")
# @login_required
# def admin_dashboard():
#     """Admin Dashboard where admins can manage speakers, messages, and images"""
#     with sqlite3.connect(DATABASE_FILE) as conn:
#         cursor = conn.cursor()
#         cursor.execute("SELECT * FROM messages")
#         messages = cursor.fetchall()

#     # Retrieve uploaded images
#     gallery_images = [
#         file
#         for file in os.listdir(app.config["UPLOAD_FOLDER"])
#         if os.path.isfile(os.path.join(app.config["UPLOAD_FOLDER"], file))
#     ]

#     return render_template("admin_dashboard.html", messages=messages, gallery_images=gallery_images)

@app.route("/admin-dashboard")
@login_required
def admin_dashboard():
    """Admin Dashboard to manage the project"""
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM messages")
        messages = cursor.fetchall()

        cursor.execute("SELECT * FROM questions")
        questions = cursor.fetchall()

    # Retrieve uploaded images
    gallery_images = [
        file
        for file in os.listdir(app.config["UPLOAD_FOLDER"])
        if os.path.isfile(os.path.join(app.config["UPLOAD_FOLDER"], file))
    ]

    return render_template(
        "admin_dashboard.html",
        messages=messages,
        questions=questions,
        gallery_images=gallery_images,
    )


# delete messages
@app.route("/delete-message/<int:message_id>", methods=["POST"])
@login_required
def delete_message(message_id):
    """Delete a message by ID"""
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM messages WHERE id = ?", (message_id,))
        conn.commit()
    flash("Message deleted successfully!", "success")
    return redirect(url_for("admin_dashboard"))


# delete questions
@app.route("/delete-question/<int:question_id>", methods=["POST"])
@login_required
def delete_question(question_id):
    """Delete a question by ID"""
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM questions WHERE id = ?", (question_id,))
        conn.commit()
    flash("Question deleted successfully!", "success")
    return redirect(url_for("admin_dashboard"))



@app.route("/delete-image/<filename>", methods=["POST"])
@login_required
def delete_image(filename):
    """Route to delete an uploaded image"""
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            flash("Image deleted successfully!", "success")
        else:
            flash("Image not found.", "danger")
    except Exception as e:
        flash(f"An error occurred: {e}", "danger")

    return redirect(url_for("admin_dashboard"))

@app.route("/add-admin", methods=["GET", "POST"])
@login_required
def add_admin():
    """Route to add new admin"""
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO admins (email, password) VALUES (?, ?)", (email, password))
            conn.commit()

        flash("New admin added successfully!", "success")
        return redirect(url_for("admin_dashboard"))

    return render_template("add_admin.html")


# manage admins
@app.route("/admins", methods=["GET", "POST"])
@login_required
def manage_admins():
    """View and manage admin accounts"""
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, email FROM admins")
        admins = cursor.fetchall()

    return render_template("manage_admins.html", admins=admins)

@app.route("/delete-admin/<int:admin_id>", methods=["POST"])
@login_required
def delete_admin(admin_id):
    """Delete an admin account"""
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM admins WHERE id = ?", (admin_id,))
        conn.commit()
    flash("Admin account deleted successfully!", "success")
    return redirect(url_for("manage_admins"))


@app.route("/contact", methods=["GET", "POST"])
def contact():
    """Contact Page - Handles Messages with Database"""
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        number = request.form.get("number")
        subject = request.form.get("subject")
        message = request.form.get("message")

        if not all([name, email, number, subject, message]):
            flash("All fields are required. Please fill in the form completely.", "danger")
            return redirect(url_for("contact"))

        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO messages (name, email, number, subject, message)
                VALUES (?, ?, ?, ?, ?)
                """,
                (name, email, number, subject, message),
            )
            conn.commit()

        flash("Message sent successfully!", "success")

    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name, email, number, subject, message FROM messages")
        messages = cursor.fetchall()

    return render_template("contact.html", messages=messages)

if __name__ == "__main__":
    app.run(debug=True)
