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

app = Flask(__name__)

DATABASE_FILE = "contact_messages.db"

with sqlite3.connect(DATABASE_FILE) as conn:
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS speakers")
    conn.commit()

print("Table 'speakers' deleted successfully.")

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

# Always check and create necessary tables
with sqlite3.connect(DATABASE_FILE) as conn:
    cursor = conn.cursor()

    # Ensure `messages` table exists
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

    # Ensure `questions` table exists
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL
        )
        """
    )

    # Ensure `speakers` table exists
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

    

    # Insert dummy data into the `speakers` table if it's empty
    cursor.execute("SELECT COUNT(*) FROM speakers")
    if cursor.fetchone()[0] == 0:  # If no data exists
        cursor.executemany(
            """
            INSERT INTO speakers (name, position, bio, image_url, facebook_url, twitter_url, linkedin_url)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            [
                ("Lolu Alade-Akinyemi", "CEO", "Mr. Lolu Alade-Akinyemi was appointed as GMD/CEO of Lafarge Africa Plc on 1st July 2023. Prior to this appointment, Mr. Alade-Akinyemi was the Chief Financial Officer (CFO) and the supply chain director of the Company. He was appointed an Executive Director to the Board on the 8th of April 2020. Mr. Lolu Alade-Akinyemi has over 20 years of cross-functional experience in finance, supply chain, business development, and sales. Lolu is a seasoned business executive with multifaceted international experience and accomplishments in turnaround situations, transforming processes to improve business performance, fostering growth in challenging business environments, and Profit & Loss oversight. Prior to joining Lafarge in 2014, he was Finance Director, PZ Cussons Nigeria Plc for 4 years and he was at the Coca-Cola Company for 16 years where he worked in the UK, Belgium, Ghana, and Nigeria taking increased responsibilities in finance, business development, supply chain and sales. He started his career as a trainee at ExxonMobil. Mr. Lolu Alade-Akinyemi is a certified accountant with a Bachelor’s degree in Economics from the University of Essex, and an MBA from the Edinburgh Business School, UK.  ", "/static/images/ceo.jpg", "https://facebook.com/lolu", "https://twitter.com/lolu", "https://linkedin.com/in/lolu"),
                ("Osazemen Aghatise", "Logistics Director", "Osaze has over 12 years of combined hands-on and leadership experience in Logistics management, procurement, health and safety, auditing, and project management in all facets of oil and gas, services, and manufacturing industries across Europe, the Middle East, Asia, and Africa. He is a concept-to-implementation strategist with demonstrated success in controlling multiple projects that elevate organizational efficiency while optimizing resources to achieve corporate goals and objectives. A thought leader working with key stakeholders focused on resource utilization, business development, and compliance, Osaze holds a master's degree from the University of Cardiff, UK, and he is an award recipient from IOSH on health and safety contribution.", "/static/images/osaze-logistics-director.png", "https://facebook.com/osazemen", "https://twitter.com/osazemen", "https://linkedin.com/in/osazemen"),
                ("Saeed Ande", "Procurement Director", "Handles procurement strategies.", "/static/images/saeed-ande.png", "https://facebook.com/saeed", "https://twitter.com/saeed", "https://linkedin.com/in/saeed"),
            ]
        )
        conn.commit()


# Helper function to check allowed file types
def allowed_file(filename):
    return (
        "." in filename and os.path.splitext(filename)[1].lower() in ALLOWED_EXTENSIONS
    )


# Helper function to fetch speaker details by ID
def get_speaker_by_id(speaker_id):
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
    """Home Page"""
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

@app.route('/ask')
def ask():
    return render_template('ask.html')

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
    # print(speaker.id)
    if not speaker:
        return "Speaker not found", 404
    print(speaker) 
    return render_template("speaker.html", speaker=speaker)


# Gallery route
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
    image_folder = os.path.join(app.static_folder, "conference2024")
    images = [
        f
        for f in os.listdir(image_folder)
        if os.path.isfile(os.path.join(image_folder, f))
    ]
    return render_template("previous_year_images.html", images=images)



@app.route('/event-highlights')
def event_highlights():
    # Render the 'event_highlight.html' template
    return render_template('event_highlight.html')

if __name__ == '__main__':
    app.run(debug=True)




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
            flash(
                "All fields are required. Please fill in the form completely.", "danger"
            )
            return redirect(url_for("contact"))

        try:
            # Insert the message into the database
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
    app.run()
