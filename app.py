from flask import Flask, render_template, request, redirect, send_from_directory, send_file, session
import os
import sqlite3
import uuid
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

from networking.client import send_farm_data
from analysis.algorithm import analyze_farm
from ml.model import predict_risk
from ml.poultry_detector import detect_poultry_signs
from analysis.sympy_calculator import calculate_farm_projection
from data.disease_info import get_disease_info
from report_generator import generate_farm_report

app = Flask(__name__)
app.secret_key = "smart-poultry-farm-secret-key"

UPLOAD_FOLDER = "uploads"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def init_db():
    conn = sqlite3.connect("farm.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS farm_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            birds INTEGER,
            eggs INTEGER,
            feed REAL,
            performance INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


init_db()

DATABASE = "farm.db"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn




def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS farm_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            birds INTEGER NOT NULL,
            eggs INTEGER NOT NULL,
            feed REAL NOT NULL,
            water REAL NOT NULL,
            temperature REAL NOT NULL,
            humidity REAL NOT NULL,
            mortality INTEGER NOT NULL,
            performance REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            farmer_name TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            farm_name TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# =========================================================
# CURRENT FARM DATA
# =========================================================

birds = 1000
eggs = 850
feed = 125.0
performance = 85


# =========================================================
# FARM HISTORY
# =========================================================

farm_history = []


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    # If farmer is not logged in, show login page
    if "user_id" not in session:
        return redirect("/login")

    # If farmer is logged in, open the existing dashboard
    return render_template(
        "dashboard.html",
        farmer_name=session.get("farmer_name"),
        username=session.get("username"),
        farm_name=session.get("farm_name")
    )


# =========================================================
# ANALYSIS DASHBOARD
# =========================================================

@app.route("/analysis")
def analysis():

    if "user_id" not in session:
        return redirect("/login")

    print("1. Analysis route started")

    conn = get_db()


    print("2. Database connected")

    history = conn.execute("""
        SELECT *
        FROM farm_records
        ORDER BY id DESC
    """).fetchall()

    print("3. Database query finished")

    conn.close()

    print("4. Database closed")

    # =========================================
    # RUN ALGORITHM ON LATEST FARM RECORD
    # =========================================

    latest_analysis = None

    if history:

        latest = history[0]

        farm_data = {
            "birds": latest["birds"],
            "eggs": latest["eggs"],
            "feed": latest["feed"],
            "water": latest["water"],
            "temperature": latest["temperature"],
            "humidity": latest["humidity"],
            "mortality": latest["mortality"],
            "performance": latest["performance"]
        }

        latest_analysis = analyze_farm(farm_data)

        print("LATEST ANALYSIS:", latest_analysis)

        print("================================")
        print("ALGORITHM RESULT")
        print("================================")
        print("Egg Rate:", latest_analysis["egg_rate"])
        print("Mortality Rate:", latest_analysis["mortality_rate"])
        print("Feed Efficiency:", latest_analysis["feed_efficiency"])
        print("Environmental Risk:", latest_analysis["environmental_risk"])
        print("Overall Risk:", latest_analysis["overall_risk"])
        print("================================")

        # =========================================
    # CHART DATA
    # =========================================

    chart_data = []

    for record in reversed(history):
        chart_data.append({
            "id": record["id"],
            "eggs": record["eggs"],
            "mortality": record["mortality"],
            "feed": record["feed"]
        })

    return render_template(
    "analysis.html",

    # Logged-in farmer information
    farmer_name=session.get("farmer_name"),
    username=session.get("username"),
    farm_name=session.get("farm_name"),

    # Existing dashboard data
    birds=birds,
    eggs=eggs,
    feed=feed,
    performance=performance,
    history=history,
    latest_analysis=latest_analysis,
    chart_data=chart_data
)


# =========================================================
# ADD FARM DATA
# =========================================================

@app.route("/add_data", methods=["POST"])
def add_data():

    global birds
    global eggs
    global feed
    global performance

    try:

        # -------------------------------------------------
        # Get data from HTML form
        # -------------------------------------------------

        birds = int(request.form["birds"])

        eggs = int(request.form["eggs"])

        feed = float(request.form["feed"])

        performance = int(request.form["performance"])

        water = float(request.form["water"])

        temperature = float(request.form["temperature"])

        humidity = float(request.form["humidity"])

        mortality = int(request.form["mortality"])


        # -------------------------------------------------
        # Create farm data object
        # -------------------------------------------------

        farm_data = {

            "birds": birds,

            "eggs": eggs,

            "feed": feed,

            "water": water,

            "temperature": temperature,

            "humidity": humidity,

            "mortality": mortality,

            "performance": performance
        }
        conn = get_db()

        conn.execute("""
            INSERT INTO farm_records
            (birds, eggs, feed, water, temperature, humidity, mortality, performance)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            birds,
            eggs,
            feed,
            water,
            temperature,
            humidity,
            mortality,
            performance
        ))

        conn.commit()
        conn.close()


        # -------------------------------------------------
        # RUN FARM ANALYSIS ALGORITHM
        analysis_result = analyze_farm(farm_data)
        print("ALGORITHM RESULT:", analysis_result)

        # RUN MACHINE LEARNING PREDICTION
        ml_prediction = predict_risk(farm_data)

        # Add ML result to analysis
        analysis_result["ml_risk"] = ml_prediction

        # Store complete analysis
        farm_data["analysis"] = analysis_result


        # -------------------------------------------------
        # SAVE DATA IN HISTORY
        # -------------------------------------------------

        farm_history.append(farm_data)


        # -------------------------------------------------
        # SEND DATA THROUGH SOCKET
        # -------------------------------------------------

        try:

            socket_result = send_farm_data(farm_data)

            print("\n================================")
            print("SOCKET RESULT")
            print("================================")
            print(socket_result)

        except Exception as socket_error:

            print("\nSocket connection error:")
            print(socket_error)


        # -------------------------------------------------
        # PRINT ANALYSIS IN TERMINAL
        # -------------------------------------------------

        print("\n================================")
        print("SMART POULTRY FARM ANALYSIS")
        print("================================")

        print("Birds:", birds)

        print("Eggs:", eggs)

        print("Feed:", feed, "kg")

        print("Water:", water, "L")

        print("Temperature:", temperature, "°C")

        print("Humidity:", humidity, "%")

        print("Mortality:", mortality)

        print("Performance:", performance, "%")

        print("--------------------------------")

        print(
            "Egg Production Rate:",
            analysis_result["egg_rate"],
            "%"
        )

        print(
            "Mortality Rate:",
            analysis_result["mortality_rate"],
            "%"
        )

        print(
            "Feed Efficiency:",
            analysis_result["feed_efficiency"],
            "eggs/kg"
        )

        print(
            "Environmental Risk:",
            analysis_result["environmental_risk"]
        )

        print(
            "Overall Farm Risk:",
            analysis_result["overall_risk"]
        )

        print("================================\n")


        # -------------------------------------------------
        # RETURN TO DASHBOARD
        # -------------------------------------------------

        return redirect("/analysis")


    except ValueError:

        print("ERROR: Invalid data entered.")

        return redirect("/analysis")


    except KeyError as error:

        print("ERROR: Missing form field:", error)

        return redirect("/analysis")
    # =========================================================
# SYMPY WHAT-IF FARM CALCULATOR
# =========================================================

@app.route("/what_if", methods=["GET", "POST"])
def what_if():

    projection = None

    if request.method == "POST":

        try:

            birds_input = float(request.form["birds"])
            eggs_per_bird = float(request.form["eggs_per_bird"])
            feed_per_bird = float(request.form["feed_per_bird"])
            feed_price = float(request.form["feed_price"])

            projection = calculate_farm_projection(
                birds_input,
                eggs_per_bird,
                feed_per_bird,
                feed_price
            )

        except (ValueError, KeyError):

            projection = None

    return render_template(
        "what_if.html",
        projection=projection
    )


# =========================================================
# DELETE FARM DATA
# =========================================================

@app.route("/delete_data/<int:index>", methods=["POST"])
def delete_data(index):

    conn = get_db()

    try:

        conn.execute(
            "DELETE FROM farm_records WHERE id = ?",
            (index,)
        )

        conn.commit()

        print("Deleted farm record ID:", index)

    except Exception as e:

        print("ERROR deleting record:", e)

    finally:

        conn.close()

    return redirect("/analysis")

# =========================================================
# SERVE UPLOADED IMAGES
# =========================================================

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        filename
    )

# =========================================================
# CHICKEN DISEASE IMAGE DETECTION
# =========================================================

@app.route("/detect", methods=["GET", "POST"])
def detect():

    results = None
    image_name = None
    disease_details = []

    if request.method == "POST":

        if "chicken_image" not in request.files:
            return "ERROR: No image was selected."

        image = request.files["chicken_image"]

        if image.filename == "":
            return "ERROR: No image was selected."

        # Secure original filename
        original_name = secure_filename(image.filename)

        # Create unique filename
        image_name = str(uuid.uuid4()) + "_" + original_name

        image_path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            image_name
        )

        # Save uploaded image
        image.save(image_path)

        print("\n================================")
        print("IMAGE UPLOADED")
        print("File:", image_name)
        print("================================")

        try:

            # -------------------------------------------------
            # RUN CHICKEN DISEASE DETECTION
            # -------------------------------------------------

            results = detect_poultry_signs(image_path)

            disease_details = []

            for result in results:

                class_name = result["class_name"]

                info = get_disease_info(class_name)

                disease_details.append({
                    "class_name": class_name,
                    "confidence": result["confidence"],
                    "info": info
                })

            print("\n================================")
            print("POULTRY DISEASE DETECTION")
            print("================================")
            print(results)
            print("================================\n")

        except Exception as e:

            return f"ERROR during disease detection: {e}"

    # =========================================================
    # LOAD FARM HISTORY
    # =========================================================

    conn = get_db()

    history = conn.execute("""
        SELECT *
        FROM farm_records
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    # =========================================================
    # RUN ALGORITHM ON LATEST FARM RECORD
    # =========================================================

    latest_analysis = None

    if history:

        latest = history[0]

        farm_data = {
            "birds": latest["birds"],
            "eggs": latest["eggs"],
            "feed": latest["feed"],
            "water": latest["water"],
            "temperature": latest["temperature"],
            "humidity": latest["humidity"],
            "mortality": latest["mortality"],
            "performance": latest["performance"]
        }

        latest_analysis = analyze_farm(farm_data)

        print("================================")
        print("ALGORITHM RESULT")
        print("================================")
        print("Egg Rate:", latest_analysis["egg_rate"])
        print("Mortality Rate:", latest_analysis["mortality_rate"])
        print("Feed Efficiency:", latest_analysis["feed_efficiency"])
        print("Environmental Risk:", latest_analysis["environmental_risk"])
        print("Overall Risk:", latest_analysis["overall_risk"])
        print("================================")

    # ============================================================
    # CHART DATA
    # ============================================================

    chart_data = []

    for record in reversed(history):
        chart_data.append({
            "id": record["id"],
            "eggs": record["eggs"],
            "mortality": record["mortality"],
            "feed": record["feed"]
        })

    # ============================================================
    # SHOW EVERYTHING TOGETHER
    # ============================================================

    return render_template(
        "analysis.html",
        birds=birds,
        eggs=eggs,
        feed=feed,
        performance=performance,
        history=history,
        latest_analysis=latest_analysis,
        detection_results=results,
        disease_details=disease_details,
        image_name=image_name,
        chart_data=chart_data
    )
# =========================================================
# AUTOMATIC FARM REPORT
# =========================================================

@app.route("/generate_report")
def generate_report():

    # Get farm history from database
    conn = get_db()

    history = conn.execute("""
        SELECT *
        FROM farm_records
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    # Check if there is any farm data
    if not history:
        return redirect("/analysis")

    # Get latest farm record
    latest = history[0]

    # Create farm data dictionary
    farm_data = {

        "birds": latest["birds"],

        "eggs": latest["eggs"],

        "feed": latest["feed"],

        "water": latest["water"],

        "temperature": latest["temperature"],

        "humidity": latest["humidity"],

        "mortality": latest["mortality"],

        "performance": latest["performance"]

    }

    # Run existing farm analysis algorithm
    analysis_result = analyze_farm(farm_data)

    # Run existing machine learning prediction
    ml_risk = predict_risk(farm_data)

    # Create report folder
    report_folder = os.path.join(
        app.config["UPLOAD_FOLDER"],
        "reports"
    )

    os.makedirs(
        report_folder,
        exist_ok=True
    )

    # Report file location
    report_path = os.path.join(
        report_folder,
        "smart_poultry_farm_report.pdf"
    )

    # Generate PDF report
    generate_farm_report(
        report_path,
        latest,
        analysis_result,
        ml_risk,
        history
    )

    print("\n================================")
    print("FARM REPORT GENERATED")
    print("================================")
    print("Report:", report_path)
    print("================================\n")

    # Download PDF
    return send_file(
        report_path,
        as_attachment=True,
        download_name="smart_poultry_farm_report.pdf",
        mimetype="application/pdf"
    )

# =========================================================
# RUN FLASK SERVER
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        conn = get_db()

        user = conn.execute("""
            SELECT * FROM users
            WHERE username = ?
        """, (username,)).fetchone()

        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["farmer_name"] = user["farmer_name"]
            session["username"] = user["username"]
            session["farm_name"] = user["farm_name"]

            return redirect("/analysis")

        return render_template(
            "login.html",
            error="Invalid username or password."
        )

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        farmer_name = request.form["farmer_name"].strip()
        username = request.form["username"].strip()
        password = request.form["password"]
        farm_name = request.form["farm_name"].strip()

        if not farmer_name or not username or not password or not farm_name:
            return render_template(
                "register.html",
                error="All fields are required."
            )

        password_hash = generate_password_hash(password)

        conn = get_db()

        try:
            conn.execute("""
                INSERT INTO users
                (farmer_name, username, password, farm_name)
                VALUES (?, ?, ?, ?)
            """, (
                farmer_name,
                username,
                password_hash,
                farm_name
            ))

            conn.commit()
            conn.close()

            return redirect("/login")

        except sqlite3.IntegrityError:
            conn.close()
            return render_template(
                "register.html",
                error="Username already exists."
            )

    return render_template("register.html")
    

if __name__ == "__main__":

    init_db()

    print("\n======================================")
    print("SMART POULTRY FARM SYSTEM")
    print("======================================")
    print("Flask server starting...")
    print("Dashboard: http://127.0.0.1:5000/analysis")
    print("======================================\n")

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )