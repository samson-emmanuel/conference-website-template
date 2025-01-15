from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime
import sqlite3
import os
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import secrets
import pandas as pd

app = Flask(__name__)

# Configuration
DATABASE_FILE = "contact_messages.db"
UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
# app.secret_key = "super_secret_key"  # Required for flash messages
app.secret_key = secrets.token_hex(16)  # Required for flash messages

# Ensure the uploads folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# Load the data once at the start
file_path = 'static/2025_LC_DELEGATE_PROFILE.xlsx'
df = pd.read_excel(file_path, sheet_name='Getting to Know the Delegates')



@app.route('/know_your_delegates')
def know_your_delegates():
    profiles = df.head(30).to_dict(orient='records')
    print(f'{profiles}')
    return render_template('know_your_delegates.html', profiles=profiles)


@app.route('/load_more', methods=['POST'])
def load_more():
    start = int(request.form.get('start', 0))
    end = start + 10
    profiles = df.iloc[start:end].to_dict(orient='records')
    print(profiles)  # Debugging output
    return jsonify(profiles)


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


# from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
# from datetime import datetime
# import os
# from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
# import secrets
# import mysql.connector
# import pandas as pd

# app = Flask(__name__)

# # Configuration
# DATABASE_CONFIG = {
#     'host': 'localhost',
#     'user': 'root',
#     'password': 'Oungbogbololese100%',
#     'database': 'lafargeConferenceSite'
# }
# UPLOAD_FOLDER = "static/uploads"
# ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif"}
# app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
# app.secret_key = secrets.token_hex(16)

# # Ensure the uploads folder exists
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# # Initialize Flask-Login
# login_manager = LoginManager()
# login_manager.init_app(app)
# login_manager.login_view = "login"

# # Load the data once at the start
# file_path = '/Users/samson/Desktop/lafarge web project/conference/static/2025_LC_DELEGATE_PROFILE.xlsx'
# df = pd.read_excel(file_path, sheet_name='Getting to Know the Delegates')



# @app.route('/know_your_delegates')
# def know_your_delegates():
#     profiles = df.head(30).to_dict(orient='records')
#     print(f'{profiles}')
#     return render_template('know_your_delegates.html', profiles=profiles)


# @app.route('/load_more', methods=['POST'])
# def load_more():
#     start = int(request.form.get('start', 0))
#     end = start + 10
#     profiles = df.iloc[start:end].to_dict(orient='records')
#     print(profiles)  # Debugging output
#     return jsonify(profiles)



# # Initialize the database and create tables if they don't exist
# def initialize_database():
#     connection = mysql.connector.connect(**DATABASE_CONFIG)
#     cursor = connection.cursor()

#     # Admins table
#     cursor.execute(
#         """
#         CREATE TABLE IF NOT EXISTS admins (
#             id INT AUTO_INCREMENT PRIMARY KEY,
#             email VARCHAR(255) NOT NULL UNIQUE,
#             password VARCHAR(255) NOT NULL
#         )
#         """
#     )

#     # Insert demo admin user if the table is empty
#     cursor.execute("SELECT COUNT(*) FROM admins")
#     if cursor.fetchone()[0] == 0:
#         cursor.execute(
#             "INSERT INTO admins (email, password) VALUES (%s, %s)",
#             ("demo@example.com", "demo_password"),
#         )

#     # Messages table
#     cursor.execute(
#         """
#         CREATE TABLE IF NOT EXISTS messages (
#             id INT AUTO_INCREMENT PRIMARY KEY,
#             name VARCHAR(255) NOT NULL,
#             email VARCHAR(255) NOT NULL,
#             number VARCHAR(50) NOT NULL,
#             subject VARCHAR(255) NOT NULL,
#             message TEXT NOT NULL
#         )
#         """
#     )

#     # Questions table
#     cursor.execute(
#         """
#         CREATE TABLE IF NOT EXISTS questions (
#             id INT AUTO_INCREMENT PRIMARY KEY,
#             question TEXT NOT NULL
#         )
#         """
#     )

#     # Speakers table
#     cursor.execute(
#         """
#         CREATE TABLE IF NOT EXISTS speakers (
#             id INT AUTO_INCREMENT PRIMARY KEY,
#             name VARCHAR(255) NOT NULL,
#             position VARCHAR(255) NOT NULL,
#             bio TEXT NOT NULL,
#             image_url VARCHAR(255) NOT NULL,
#             facebook_url VARCHAR(255),
#             twitter_url VARCHAR(255),
#             linkedin_url VARCHAR(255)
#         )
#         """
#     )

#     cursor.execute("SELECT COUNT(*) FROM speakers")
#     if cursor.fetchone()[0] == 0:
#         demo_speakers = [
#             (
#                 "Segun Ogunsanya",
#                 "Pushing Boundaries",
#                 "Segun Ogunsanya was the managing director and chief executive officer of Airtel Nigeria, subsidiary of the Indian telecommunications conglomerate, represented in 14 Sub-Saharan African countries. Ogunsanya holds a Bachelor's degree in Electrical and Electronic Engineering obtained from the University of Ife (now Obafemi Awolowo University), in 1987. He is also a Chartered Accountant, recognized by the Institute of Chartered Accountants of Nigeria. In 1999, he served as general manager and chief executive of Coca-Cola Ghana and later as the chief executive officer of Coca-Cola Sabco, Kenya, in 2010. He was managing director and head of retail banking operations of Ecobank Transnational Inc. from 2008 to 2009. Ogunsanya was the managing director at Nigerian Bottling Company Plc from September 2011, to December 2012. He was appointed CEO of the Nigerian operation of Bharti Airtel, on 26 November 2012. In April 2021, Ogunsanya was appointed as the designated chief executive officer of Airtel Africa, the African subsidiary that includes all the 14 sub-Saharan African markets. His appointment to this position took effect from 1 October 2021. His retirement was announced effective from 01 July 2024.",
#                 "static/images/segunOgunsaya.png",
#                 "https://facebook.com/",
#                 "https://twitter.com/",
#                 "https://linkedin.com/",
#             ),
#             (
#                 "Folusho Philips",
#                 "Growth",
#                 "Folusho Philips is a distinguished Nigerian professional and entrepreneur known for his significant contributions to management consulting and economic development in Africa. He is the founder and chairman of Phillips Consulting Limited, a management consulting firm with offices in Nigeria, South Africa, and the UK. The firm specializes in organizational development and corporate transformation. A Chartered Management Accountant (UK) and Chartered Accountant (Nigeria), Phillips earned a degree in Industrial Economics from the University of Wales' Institute of Science & Technology. His professional career includes roles in financial management and consulting with Coopers & Lybrand International (now PwC), and as the Group General Manager of Finance at the SCOA Group. He has held influential positions, such as the Chairman of the Nigeria Economic Summit Group and the Nigeria-South Africa Chamber of Commerce. Additionally, he serves as a director of several companies and non-profit organizations, including Special Olympics Nigeria and the African Business Roundtable. Phillips is recognized for his commitment to fostering economic growth and business leadership across Africa",
#                 "static/images/folusoPhilip.png",
#                 "https://facebook.com/",
#                 "https://twitter.com/",
#                 "https://linkedin.com/",
#             )
#             (
#                 "Omobola Olubusola",
#                 "Pushing Boundaries",
#                 "Omobola Olubusola Johnson (born 28 June 1963) is a Nigerian technocrat and the Honorary Chairperson of the global Alliance for Affordable Internet (A4AI). She is also a former and first Minister of Communication Technology in the cabinet of President Goodluck Jonathan. She was educated at the International School Ibadan and the University of Manchester (BEng, Electrical and Electronic Engineering) and King's College London (MSc, Digital Electronics). She has a Doctor of Business Administration (DBA) from Cranfield University. Prior to her Ministerial appointment she was country managing director for Accenture, Nigeria. She had worked with Accenture since 1985 when it was Andersen Consulting. Johnson is the pioneer head of the country's communication technology ministry, which was created as part of the transformation agenda of the Nigerian government. Johnson co-founded a women's organization, WIMBIZ in 2001. She has earned several public commendations since taking up her first government assignment as minister in 2011. This is following the numerous achievements of her ministry notably among which is the launch of the NigComSat-IR Satellite. This has helped to complement the country's efforts at fibre connectivity and the provision of greater bandwidth. The ministry under her watch has also deployed more than 700 personal computers to secondary schools in the first phase of School Access Programme (SAP) while about 193 tertiary institutions in the country now have internet access in the Tertiary Institution Access Programme (TIAP) and 146 communities have access to Community Communication Centers deployed around the country. Omobola is currently a non-executive director of Guinness Nigeria PLC, MTN and Chairperson of Custodian and Allied Insurance Limited. She is also a senior partner with the Venture Capital Firm TLCOM.",
#                 "static/images/omobolaJohnson.png",
#                 "https://twitter.com/",
#                 "https://linkedin.com/",
#             )
#         ]

#         cursor.executemany(
#             """
#             INSERT INTO speakers (name, position, bio, image_url, facebook_url, twitter_url, linkedin_url)
#             VALUES (%s, %s, %s, %s, %s, %s, %s)
#             """,
#             demo_speakers
#         )

    

#     connection.commit()
#     cursor.close()
#     connection.close()

# initialize_database()

# # Admin User Model
# class Admin(UserMixin):
#     """Model for admin users"""
#     def __init__(self, id, email):
#         self.id = id
#         self.email = email

# @login_manager.user_loader
# def load_user(user_id):
#     """Load admin user by ID"""
#     connection = mysql.connector.connect(**DATABASE_CONFIG)
#     cursor = connection.cursor()
#     cursor.execute("SELECT * FROM admins WHERE id = %s", (user_id,))
#     user = cursor.fetchone()
#     cursor.close()
#     connection.close()
#     if user:
#         return Admin(user[0], user[1])
#     return None

# # Helper function to check allowed file types
# def allowed_file(filename):
#     """Check if a file has an allowed extension"""
#     return "." in filename and os.path.splitext(filename)[1].lower() in ALLOWED_EXTENSIONS

# # Helper function to fetch speaker details by ID
# def get_speaker_by_id(speaker_id):
#     """Retrieve speaker details by their ID"""
#     connection = mysql.connector.connect(**DATABASE_CONFIG)
#     cursor = connection.cursor(dictionary=True)
#     cursor.execute("SELECT * FROM speakers WHERE id = %s", (speaker_id,))
#     speaker = cursor.fetchone()
#     cursor.close()
#     connection.close()
#     return speaker

# @app.route("/")
# def index():
#     """Home Page - Display list of speakers"""
#     connection = mysql.connector.connect(**DATABASE_CONFIG)
#     cursor = connection.cursor(dictionary=True)
#     cursor.execute("SELECT id, name, position, image_url, facebook_url, twitter_url, linkedin_url FROM speakers")
#     speakers = cursor.fetchall()
#     cursor.close()
#     connection.close()
#     return render_template("index.html", speakers=speakers)

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

# @app.route("/ask")
# def ask():
#     """Ask Questions Page"""
#     return render_template("ask.html")

# @app.route("/ask-question", methods=["POST"])
# def ask_question():
#     """Endpoint to handle question submission"""
#     data = request.get_json()
#     question = data.get("question")

#     if question:
#         # Insert the question into the database
#         connection = mysql.connector.connect(**DATABASE_CONFIG)
#         cursor = connection.cursor()
#         cursor.execute("INSERT INTO questions (question) VALUES (%s)", (question,))
#         connection.commit()
#         cursor.close()
#         connection.close()
#         return jsonify(
#             {"status": "success", "message": "Question submitted successfully!"}
#         )
#     return jsonify({"status": "error", "message": "Question is required"}), 400

# @app.route("/about")
# def about():
#     """About Page"""
#     return render_template("about.html")

# @app.route("/speaker/<int:speaker_id>")
# def speaker_page(speaker_id):
#     """Speaker Details Page"""
#     speaker = get_speaker_by_id(speaker_id)
#     if not speaker:
#         return "Speaker not found", 404
#     return render_template("speaker.html", speaker=speaker)

# @app.route("/login", methods=["GET", "POST"])
# def login():
#     """Login route to authenticate admin"""
#     if request.method == "POST":
#         email = request.form.get("email")
#         password = request.form.get("password")

#         connection = mysql.connector.connect(**DATABASE_CONFIG)
#         cursor = connection.cursor()
#         cursor.execute("SELECT * FROM admins WHERE email = %s", (email,))
#         admin = cursor.fetchone()
#         cursor.close()
#         connection.close()
#         if admin and admin[2] == password:
#             user = Admin(admin[0], admin[1])
#             login_user(user)
#             return redirect(url_for("admin_dashboard"))

#         flash("Invalid credentials. Please try again.", "danger")
#         return redirect(url_for("login"))

#     return render_template("login.html")

# @app.route("/logout")
# @login_required
# def logout():
#     """Logout route to log out the admin"""
#     logout_user()
#     return redirect(url_for("login"))

# @app.route("/admin-dashboard")
# @login_required
# def admin_dashboard():
#     """Admin Dashboard to manage the project"""
#     connection = mysql.connector.connect(**DATABASE_CONFIG)
#     cursor = connection.cursor(dictionary=True)
#     cursor.execute("SELECT * FROM messages")
#     messages = cursor.fetchall()

#     cursor.execute("SELECT * FROM questions")
#     questions = cursor.fetchall()

#     # Retrieve uploaded images
#     gallery_images = [
#         file
#         for file in os.listdir(app.config["UPLOAD_FOLDER"])
#         if os.path.isfile(os.path.join(app.config["UPLOAD_FOLDER"], file))
#     ]

#     cursor.close()
#     connection.close()

#     return render_template(
#         "admin_dashboard.html",
#         messages=messages,
#         questions=questions,
#         gallery_images=gallery_images,
#     )

# # delete messages
# @app.route("/delete-message/<int:message_id>", methods=["POST"])
# @login_required
# def delete_message(message_id):
#     """Delete a message by ID"""
#     connection = mysql.connector.connect(**DATABASE_CONFIG)
#     cursor = connection.cursor()
#     cursor.execute("DELETE FROM messages WHERE id = %s", (message_id,))
#     connection.commit()
#     cursor.close()
#     connection.close()
#     flash("Message deleted successfully!", "success")
#     return redirect(url_for("admin_dashboard"))

# # delete questions
# @app.route("/delete-question/<int:question_id>", methods=["POST"])
# @login_required
# def delete_question(question_id):
#     """Delete a question by ID"""
#     connection = mysql.connector.connect(**DATABASE_CONFIG)
#     cursor = connection.cursor()
#     cursor.execute("DELETE FROM questions WHERE id = %s", (question_id,))
#     connection.commit()
#     cursor.close()
#     connection.close()
#     flash("Question deleted successfully!", "success")
#     return redirect(url_for("admin_dashboard"))

# @app.route("/delete-image/<filename>", methods=["POST"])
# @login_required
# def delete_image(filename):
#     """Route to delete an uploaded image"""
#     file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
#     try:
#         if os.path.exists(file_path):
#             os.remove(file_path)
#             flash("Image deleted successfully!", "success")
#         else:
#             flash("Image not found.", "danger")
#     except Exception as e:
#         flash(f"An error occurred: {e}", "danger")

#     return redirect(url_for("admin_dashboard"))

# @app.route("/add-admin", methods=["GET", "POST"])
# @login_required
# def add_admin():
#     """Route to add new admin"""
#     if request.method == "POST":
#         email = request.form.get("email")
#         password = request.form.get("password")

#         connection = mysql.connector.connect(**DATABASE_CONFIG)
#         cursor = connection.cursor()
#         cursor.execute("INSERT INTO admins (email, password) VALUES (%s, %s)", (email, password))
#         connection.commit()
#         cursor.close()
#         connection.close()

#         flash("New admin added successfully!", "success")
#         return redirect(url_for("admin_dashboard"))

#     return render_template("add_admin.html")

# # manage admins
# @app.route("/admins", methods=["GET", "POST"])
# @login_required
# def manage_admins():
#     """View and manage admin accounts"""
#     connection = mysql.connector.connect(**DATABASE_CONFIG)
#     cursor = connection.cursor(dictionary=True)
#     cursor.execute("SELECT id, email FROM admins")
#     admins = cursor.fetchall()
#     cursor.close()
#     connection.close()

#     return render_template("manage_admins.html", admins=admins)

# @app.route("/delete-admin/<int:admin_id>", methods=["POST"])
# @login_required
# def delete_admin(admin_id):
#     """Delete an admin account"""
#     connection = mysql.connector.connect(**DATABASE_CONFIG)
#     cursor = connection.cursor()
#     cursor.execute("DELETE FROM admins WHERE id = %s", (admin_id,))
#     connection.commit()
#     cursor.close()
#     connection.close()
#     flash("Admin account deleted successfully!", "success")
#     return redirect(url_for("manage_admins"))

# @app.route("/contact", methods=["GET", "POST"])
# def contact():
#     """Contact Page - Handles Messages with Database"""
#     if request.method == "POST":
#         name = request.form.get("name")
#         email = request.form.get("email")
#         number = request.form.get("number")
#         subject = request.form.get("subject")
#         message = request.form.get("message")

#         if not all([name, email, number, subject, message]):
#             flash("All fields are required. Please fill in the form completely.", "danger")
#             return redirect(url_for("contact"))

#         connection = mysql.connector.connect(**DATABASE_CONFIG)
#         cursor = connection.cursor()
#         cursor.execute(
#             """
#             INSERT INTO messages (name, email, number, subject, message)
#             VALUES (%s, %s, %s, %s, %s)
#             """,
#             (name, email, number, subject, message),
#         )
#         connection.commit()
#         cursor.close()
#         connection.close()

#         flash("Message sent successfully!", "success")

#     connection = mysql.connector.connect(**DATABASE_CONFIG)
#     cursor = connection.cursor(dictionary=True)
#     cursor.execute("SELECT name, email, number, subject, message FROM messages")
#     messages = cursor.fetchall()
#     cursor.close()
#     connection.close()

#     return render_template("contact.html", messages=messages)

# if __name__ == "__main__":
#     app.run(debug=True)
