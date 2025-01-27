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
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf.csrf import CSRFProtect, validate_csrf
from wtforms import ValidationError
# from flask_limiter import Limiter
# from flask_limiter.util import get_remote_address
# import logging
import cloudinary
import cloudinary.uploader
import cloudinary.api
from cloudinary.utils import cloudinary_url
from config import Config
from PIL import Image
from io import BytesIO

app = Flask(__name__)

# Configuration
DATABASE_CONFIG = {
    'host': Config.DATABASE_HOST,
    'user': Config.DATABASE_USER,
    'password': Config.DATABASE_PASSWORD,
    'database': Config.DATABASE_NAME,
    'auth_plugin': 'mysql_native_password'  # Explicitly specify the plugin
}
UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.secret_key = secrets.token_hex(32)  # Strong secret key

# Flask-Mail Configuration
app.config.update(
    MAIL_SERVER=os.getenv('MAIL_SERVER', 'smtp.gmail.com'),
    MAIL_PORT=int(os.getenv('MAIL_PORT', 587)),
    MAIL_USE_TLS=os.getenv('MAIL_USE_TLS', 'True').lower() == 'true',
    MAIL_USE_SSL=os.getenv('MAIL_USE_SSL', 'False').lower() == 'false',
    MAIL_USERNAME=os.getenv('MAIL_USERNAME'),
    MAIL_PASSWORD=os.getenv('MAIL_PASSWORD'),
    MAIL_DEFAULT_SENDER=os.getenv('MAIL_DEFAULT_SENDER', 'uploading@example.com')
)


cloudinary.config(
    cloud_name = 'dacopk5b3',
    api_key = '966134237713365',
    api_secret = 'B40Jh6p02w0cKiiW-jMomI5M0Ys'
)
# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Initialize Flask-Mail
mail = Mail(app)

# Initialize CSRF Protection
csrf = CSRFProtect(app)

# Initialize Rate Limiting
# limiter = Limiter(app=app, key_func=get_remote_address)

# Load the data from the Excel file
file_path = "static/2025_LC_DELEGATE_PROFILE.xlsx"
df = pd.read_excel(file_path, sheet_name="Getting to Know the Delegates")

# Database Connection
def connect_to_database():
    try:
        conn = mysql.connector.connect(**DATABASE_CONFIG)
        return conn
    except Exception as e:
        app.logger.error(f"Database connection failed: {e}")
        return None

# Initialize Database
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
                approved BOOLEAN DEFAULT 0,
                cloudinary_public_id VARCHAR(255) NOT NULL,
                cloudinary_url VARCHAR(255) NOT NULL
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
            hashed_password = generate_password_hash("samson112233!!")
            app.logger.debug(f"Hashed password: {hashed_password}")  # Log the hashed password
            cursor.execute(
                "INSERT INTO admins (email, password) VALUES (%s, %s)",
                ("samson.emmanuel.ext@lafarge.com", hashed_password),
            )
            app.logger.debug("Demo admin inserted successfully.")
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
    ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif"}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# admin dashboard    
@app.route("/admin-dashboard", methods=["GET", "POST"])
@login_required
def admin_dashboard():
    conn = connect_to_database()
    if conn:
        cursor = conn.cursor(dictionary=True)

        # Fetch images
        cursor.execute("SELECT id, filename, approved, cloudinary_url FROM images")
        images = cursor.fetchall()

        # Fetch messages
        cursor.execute("SELECT id, name, email, number, subject, message FROM messages")
        messages = cursor.fetchall()

        # Fetch questions
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
    else:
        flash("Database connection failed. Please try again later.", "danger")
        return redirect(url_for("login"))
    

# images approval
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


# Routes
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
        app.logger.error(f"Error in /load_more: {e}")
        return jsonify({"error": "Failed to load more profiles."}), 500


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email").lower()  # Convert email to lowercase
        password = request.form.get("password")

        conn = connect_to_database()
        if not conn:
            flash("System error. Please try again later.", "danger")
            return redirect(url_for("login"))

        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM admins WHERE email = %s", (email,))
            admin = cursor.fetchone()
            app.logger.debug(f"Admin fetched: {admin}")  # Log the fetched admin

            if admin:
                stored_password = admin["password"]
                app.logger.debug(f"Stored password: {stored_password}")  # Log the stored password

                # Check if the stored password is hashed
                if stored_password.startswith("pbkdf2:sha256:"):
                    # Verify hashed password
                    if check_password_hash(stored_password, password):
                        user = Admin(admin["id"], admin["email"])
                        login_user(user)
                        return redirect(url_for("admin_dashboard"))
                    else:
                        app.logger.debug("Hashed password mismatch")  # Log password mismatch
                        flash("Invalid credentials. Please try again.", "danger")
                else:
                    # Compare plaintext passwords
                    if stored_password == password:
                        user = Admin(admin["id"], admin["email"])
                        login_user(user)
                        return redirect(url_for("admin_dashboard"))
                    else:
                        app.logger.debug("Plaintext password mismatch")  # Log password mismatch
                        flash("Invalid credentials. Please try again.", "danger")
            else:
                app.logger.debug("Admin not found")  # Log admin not found
                flash("Invalid credentials. Please try again.", "danger")
        except Exception as e:
            app.logger.error(f"Login error: {e}")
            flash("System error. Please try again later.", "danger")
        finally:
            cursor.close()
            conn.close()

    return render_template("login.html")



@app.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))


def validate_image(file):
    try:
        img = Image.open(file)
        img.verify()  # Ensure the file is a valid image
        file.seek(0)  # Reset file pointer after verification
        return True
    except Exception as e:
        app.logger.error(f"Image validation error: {e}")
        return False

@app.route("/gallery", methods=["GET", "POST"])
def gallery():
    if request.method == "POST":
        uploaded_file = request.files.get("image")

        # Ensure a file is selected
        if not uploaded_file:
            flash("No file selected. Please choose an image to upload.", "danger")
            return redirect(url_for("gallery"))

        # Validate file extension and MIME type
        if not allowed_file(uploaded_file.filename):
            flash("Invalid file type. Please upload an image (jpg, jpeg, png, gif).", "danger")
            return redirect(url_for("gallery"))

        # Validate image content (optional)
        if not validate_image(uploaded_file):
            flash("Invalid image file. Please upload a valid image (jpg, jpeg, png, gif).", "danger")
            return redirect(url_for("gallery"))

        # Upload to Cloudinary
        try:
            upload_result = cloudinary.uploader.upload(uploaded_file)
            public_id = upload_result["public_id"]
            secure_url = upload_result["secure_url"]

            # Save to database
            conn = connect_to_database()
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO images (filename, upload_time, approved, cloudinary_public_id, cloudinary_url)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (uploaded_file.filename, datetime.now(), 0, public_id, secure_url),
            )
            conn.commit()
            cursor.close()
            conn.close()

            flash("Image uploaded successfully and is awaiting approval.", "success")
        except Exception as e:
            app.logger.error(f"Error uploading to Cloudinary: {e}")
            flash("Failed to upload image. Please try again later.", "danger")

    # Fetch and display approved images
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute("SELECT cloudinary_url FROM images WHERE approved = 1")
    gallery_images = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()

    return render_template("gallery.html", images=gallery_images)




@app.route("/delete-image/<int:image_id>", methods=["POST"])
@login_required
def delete_image(image_id):
    conn = connect_to_database()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT cloudinary_public_id FROM images WHERE id = %s", (image_id,))
        image = cursor.fetchone()
        if image:
            # Delete the image from Cloudinary
            try:
                cloudinary.uploader.destroy(image["cloudinary_public_id"])
            except Exception as cloudinary_error:
                flash(f"Failed to delete image from Cloudinary: {cloudinary_error}", "danger")

            # Delete the image record from the database
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
        try:
            # Validate CSRF token
            validate_csrf(request.form.get('csrf_token'))
        except ValidationError:
            flash("Invalid CSRF token. Please try again.", "danger")
            return redirect(url_for("add_admin"))

        # Process the form data
        email = request.form.get("email")
        password = request.form.get("password")
        hashed_password = generate_password_hash(password)

        conn = connect_to_database()
        if conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO admins (email, password) VALUES (%s, %s)",
                (email, hashed_password),
            )
            conn.commit()
            cursor.close()
            conn.close()
            flash("New admin added successfully!", "success")
            return redirect(url_for("manage_admins"))

    return render_template("add_admin.html")

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

@app.route("/previous_year_images")
def previous_year_images():
    image_folder = os.path.join(app.static_folder, "conference2024")
    images = [
        f
        for f in os.listdir(image_folder)
        if os.path.isfile(os.path.join(image_folder, f))
    ]
    return render_template("previous_year_images.html", images=images)

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


# Function to get a speaker by ID
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

@app.route('/search_profiles', methods=['GET'])
def search_profiles():
    try:
        # Load the Excel file and sheet dynamically
        df = pd.read_excel(file_path, sheet_name="Getting to Know the Delegates")
        
        query = request.args.get('query', '').strip().lower()
        if not query:
            return jsonify({'results': df.to_dict(orient='records')})

        # Perform case-insensitive substring search in the 'NAME' column
        if 'NAME' in df.columns:
            results = df[df['NAME'].str.contains(query, case=False, na=False)].to_dict(orient='records')
        else:
            return jsonify({'error': "'NAME' column not found in the file"}), 400

        return jsonify({'results': results})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "False").lower() == "true")
    print("Pillow version:", Image.__version__)