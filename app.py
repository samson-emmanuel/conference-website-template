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
                ("Segun Ogunsansay", "Pushing Boundaries", "Segun Ogunsanya was the managing director and chief executive officer of Airtel Nigeria, subsidiary of the Indian telecommunications conglomerate, represented in 14 Sub-Saharan African countries. Ogunsanya holds a Bachelor's degree in Electrical and Electronic Engineering obtained from the University of Ife (now Obafemi Awolowo University), in 1987. He is also a Chartered Accountant, recognized by the Institute of Chartered Accountants of Nigeria. In 1999, he served as general manager and chief executive of Coca-Cola Ghana and later as the chief executive officer of Coca-Cola Sabco, Kenya, in 2010. He was managing director and head of retail banking operations of Ecobank Transnational Inc. from 2008 to 2009. Ogunsanya was the managing director at Nigerian Bottling Company Plc from September 2011, to December 2012. He was appointed CEO of the Nigerian operation of Bharti Airtel, on 26 November 2012. In April 2021, Ogunsanya was appointed as the designated chief executive officer of Airtel Africa, the African subsidiary that includes all the 14 sub-Saharan African markets. His appointment to this position took effect from 1 October 2021. His retirement was announced effective from 01 July 2024.  ", "/static/images/segunOgunsanya.png", "https://facebook.com/lolu", "https://twitter.com/lolu", "https://linkedin.com/in/lolu"),

                ("Foluso Philip", "Growth", "Foluso Phillips is a distinguished Nigerian professional and entrepreneur known for his significant contributions to management consulting and economic development in Africa. He is the founder and chairman of Phillips Consulting Limited, a management consulting firm with offices in Nigeria, South Africa, and the UK. The firm specializes in organizational development and corporate transformation. A Chartered Management Accountant (UK) and Chartered Accountant (Nigeria), Phillips earned a degree in Industrial Economics from the University of Wales' Institute of Science & Technology. His professional career includes roles in financial management and consulting with Coopers & Lybrand International (now PwC), and as the Group General Manager of Finance at the SCOA Group. He has held influential positions, such as the Chairman of the Nigeria Economic Summit Group and the Nigeria-South Africa Chamber of Commerce. Additionally, he serves as a director of several companies and non-profit organizations, including Special Olympics Nigeria and the African Business Roundtable. Phillips is recognized for his commitment to fostering economic growth and business leadership across Africa", "/static/images/folusoPhilip.png", "https://facebook.com/osazemen", "https://twitter.com/osazemen", "https://linkedin.com/in/osazemen"),

                ("Omobola Johnson", "Pushing Boundaries", "Omobola Olubusola Johnson (born 28 June 1963) is a Nigerian technocrat and the Honorary Chairperson of the global Alliance for Affordable Internet (A4AI). She is also a former and first Minister of Communication Technology in the cabinet of President Goodluck Jonathan. She was educated at the International School Ibadan and the University of Manchester (BEng, Electrical and Electronic Engineering) and King's College London (MSc, Digital Electronics). She has a Doctor of Business Administration (DBA) from Cranfield University. Prior to her Ministerial appointment she was country managing director for Accenture, Nigeria. She had worked with Accenture since 1985 when it was Andersen Consulting. Johnson is the pioneer head of the country's communication technology ministry, which was created as part of the transformation agenda of the Nigerian government. Johnson co-founded a women's organization, WIMBIZ in 2001. She has earned several public commendations since taking up her first government assignment as minister in 2011. This is following the numerous achievements of her ministry notably among which is the launch of the NigComSat-IR Satellite. This has helped to complement the country's efforts at fibre connectivity and the provision of greater bandwidth. The ministry under her watch has also deployed more than 700 personal computers to secondary schools in the first phase of School Access Programme (SAP) while about 193 tertiary institutions in the country now have internet access in the Tertiary Institution Access Programme (TIAP) and 146 communities have access to Community Communication Centers deployed around the country. Omobola is currently a non-executive director of Guinness Nigeria PLC, MTN and Chairperson of Custodian and Allied Insurance Limited. She is also a senior partner with the Venture Capital Firm TLCOM.", "/static/images/omobolaJohnson.png", "https://facebook.com/saeed", "https://twitter.com/saeed", "https://linkedin.com/in/saeed"),
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
