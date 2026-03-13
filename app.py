from flask import Flask, request, jsonify, send_file, render_template, redirect, session
import sqlite3
import io
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import uuid

app = Flask(__name__)
app.secret_key = "il4_secret_key"

DATABASE = "players.db"


# -----------------------------
# DATABASE
# -----------------------------

def connect_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def create_database():

    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS players(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        application_id TEXT UNIQUE,

        firstname TEXT NOT NULL,
        middlename TEXT,
        lastname TEXT NOT NULL,

        email TEXT,
        phone TEXT,

        dob TEXT,
        age INTEGER,

        state TEXT,
        sport TEXT,

        photo TEXT,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


# create database automatically
create_database()


# -----------------------------
# PAGE ROUTES
# -----------------------------

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/sports")
def sports():
    return render_template("sports.html")


@app.route("/schedule")
def schedule():
    return render_template("schedule.html")


@app.route("/registration")
def registration():
    return render_template("registration.html")


@app.route("/preview")
def preview():
    return render_template("preview.html")


@app.route("/status")
def status():
    return render_template("status.html")


@app.route("/thankyou")
def thankyou():
    return render_template("thankyou.html")


# -----------------------------
# ADMIN LOGIN
# -----------------------------

ADMIN_PASSWORD = "il4admin"


@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        password = request.form.get("password")

        if password == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect("/admin")

        return render_template("admin_login.html", error="Invalid password")

    return render_template("admin_login.html")


# -----------------------------
# ADMIN PAGE
# -----------------------------

@app.route("/admin")
def admin():

    if not session.get("admin"):
        return redirect("/admin_login")

    return render_template("admin.html")


@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect("/")


# -----------------------------
# REGISTER PLAYER
# -----------------------------

@app.route("/register", methods=["POST"])
def register():

    application_id = "IL4-" + str(uuid.uuid4())[:8].upper()

    try:
        data = request.json

        conn = connect_db()
        cur = conn.cursor()

        # exact duplicate check
        cur.execute("""
        SELECT id FROM players
        WHERE firstname=? AND lastname=? AND phone=? AND state=? AND sport=?
        """,(
        data["firstname"],
        data["lastname"],
        data["phone"],
        data["state"],
        data["sport"]
        ))

        if cur.fetchone():
            conn.close()
            return jsonify({"status":"duplicate"})


        # email limit
        cur.execute("SELECT COUNT(*) as total FROM players WHERE email=?",(data["email"],))
        if cur.fetchone()["total"] >= 10:
            conn.close()
            return jsonify({"status":"email_limit"})


        # phone limit
        cur.execute("SELECT COUNT(*) as total FROM players WHERE phone=?",(data["phone"],))
        if cur.fetchone()["total"] >= 10:
            conn.close()
            return jsonify({"status":"phone_limit"})


        # insert player
        cur.execute("""
        INSERT INTO players
        (application_id,firstname,middlename,lastname,email,phone,dob,age,state,sport,photo)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """,(
        application_id,
        data["firstname"],
        data["middlename"],
        data["lastname"],
        data["email"],
        data["phone"],
        data["dob"],
        data["age"],
        data["state"],
        data["sport"],
        data["photo"]
        ))

        conn.commit()
        conn.close()

        return jsonify({
        "status":"success",
        "application_id":application_id
        })

    except Exception as e:
        print("REGISTER ERROR:", e)
        return jsonify({"status":"error"})

# -----------------------------
# CHECK STATUS
# -----------------------------

@app.route("/check_status", methods=["POST"])
def check_status():

    data = request.json
    phone = data.get("phone")

    if not phone:
        return {"status": "error"}

    conn = connect_db()
    cur = conn.cursor()

    cur.execute(
        "SELECT id FROM players WHERE phone=?",
        (phone,)
    )

    user = cur.fetchone()
    conn.close()

    if user:
        return {"status": "registered", "id": user["id"]}

    return {"status": "not_registered"}


# -----------------------------
# DOWNLOAD APPLICATION PDF
# -----------------------------

@app.route("/download/<int:user_id>")
def download(user_id):

    import base64
    from reportlab.lib.utils import ImageReader

    conn = connect_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM players WHERE id=?", (user_id,))
    user = cur.fetchone()

    conn.close()

    if not user:
        return "User not found"

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)

    # Header
    c.setFont("Helvetica-Bold",18)
    c.drawString(200,800,"INDIAN LEAGUE 4")

    c.setFont("Helvetica",12)
    c.drawString(200,780,"Goa & Pondicherry 2026")

    # Application ID
    c.drawString(50,740,f"Application ID: {user['application_id']}")

    # Player Details
    c.drawString(50,700,f"First Name: {user['firstname']}")
    c.drawString(50,680,f"Middle Name: {user['middlename']}")
    c.drawString(50,660,f"Last Name: {user['lastname']}")

    c.drawString(50,640,f"Email: {user['email']}")
    c.drawString(50,620,f"Phone: {user['phone']}")

    c.drawString(50,600,f"DOB: {user['dob']}")
    c.drawString(50,580,f"Age: {user['age']}")

    c.drawString(50,560,f"State: {user['state']}")
    c.drawString(50,540,f"Sport: {user['sport']}")

    # Player Photo
    if user["photo"]:
        try:
            img_data = base64.b64decode(user["photo"].split(",")[1])
            img = ImageReader(io.BytesIO(img_data))
            c.drawImage(img,450,650,width=100,height=120)
        except:
            pass

    # Rules
    c.setFont("Helvetica-Bold",12)
    c.drawString(50,500,"Rules & Regulations")

    c.setFont("Helvetica",10)

    rules = [
        "1. Please carry Aadhaar card.",
        "2. Selection for Cricket, Football, Kabaddi at state level.",
        "3. Above age 30 bring fitness certificate.",
        "4. Date and venue will be sent via email.",
        "5. Follow official website for updates."
    ]

    y = 480

    for r in rules:
        c.drawString(50,y,r)
        y -= 15

    # Signature
    try:
        c.drawImage("static/images/sign.jpeg",420,120,width=120,height=50)
    except:
        pass

    c.drawString(420,100,"Mr. Shakthi")
    c.drawString(420,85,"President")

    # Save PDF
    c.save()

    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"application_{user_id}.pdf",
        mimetype="application/pdf"
    )


# -----------------------------
# ADMIN API
# -----------------------------

@app.route("/get_players")
def get_players():

    if not session.get("admin"):
        return {"players": []}

    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, firstname, lastname, phone, state, sport
        FROM players
        ORDER BY id DESC
    """)

    players = cur.fetchall()
    conn.close()

    data = []

    for p in players:
        data.append({
            "id": p["id"],
            "name": f"{p['firstname']} {p['lastname']}",
            "phone": p["phone"],
            "state": p["state"],
            "sport": p["sport"]
        })

    return {"players": data}


# -----------------------------
# RUN APP
# -----------------------------

if __name__ == "__main__":
    app.run(debug=True)