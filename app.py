from flask import Flask, request, jsonify, send_file, render_template, redirect, session
import sqlite3
import io
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import uuid

app = Flask(__name__)
app.secret_key = "il4_secret_key"

DATABASE = "players.db"


@app.route("/points")
def points():
    return render_template("points.html")


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

    # PLAYERS TABLE
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

    # ✅ TEAMS TABLE WITH REGION
    cur.execute("""
    CREATE TABLE IF NOT EXISTS teams(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        region TEXT,
        matches INTEGER DEFAULT 0,
        wins INTEGER DEFAULT 0,
        loss INTEGER DEFAULT 0,
        points INTEGER DEFAULT 0,
        nrr REAL DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()


create_database()


# -----------------------------
# REGION LOGIC
# -----------------------------

REGIONS = {
    "north": ["Jammu and Kashmir","Ladakh","Himachal Pradesh","Uttar Pradesh","Haryana","Delhi","Chandigarh"],
    "south": ["Tamil Nadu","Kerala","Karnataka","Andhra Pradesh","Telangana","Puducherry","Lakshadweep"],
    "east": ["West Bengal","Tripura","Mizoram","Nagaland","Sikkim","Andaman and Nicobar Islands","Assam"],
    "west": ["Rajasthan","Gujarat","Maharashtra","Goa","Dadra and Nagar Haveli and Daman and Diu","Madhya Pradesh","Chhattisgarh","Punjab"],
    "center": ["Jharkhand","Uttarakhand","Arunachal Pradesh","Manipur","Bihar","Odisha","Meghalaya"]
}

def get_region(state):
    for region, states in REGIONS.items():
        if state in states:
            return region
    return "unknown"


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


@app.route("/preview/<app_id>")
def preview(app_id):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM players WHERE application_id=?", (app_id,))
    user = cur.fetchone()

    conn.close()

    if not user:
        return "Invalid Application ID"

    return render_template("preview.html", user=user)


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

        # duplicate check
        cur.execute("""
        SELECT id FROM players
        WHERE firstname=? AND lastname=? AND phone=? AND state=? AND sport=?
        """, (
            data["firstname"],
            data["lastname"],
            data["phone"],
            data["state"],
            data["sport"]
        ))

        if cur.fetchone():
            conn.close()
            return jsonify({"status": "duplicate"})

        # email limit
        cur.execute("SELECT COUNT(*) as total FROM players WHERE email=?", (data["email"],))
        if cur.fetchone()["total"] >= 10:
            conn.close()
            return jsonify({"status": "email_limit"})

        # phone limit
        cur.execute("SELECT COUNT(*) as total FROM players WHERE phone=?", (data["phone"],))
        if cur.fetchone()["total"] >= 10:
            conn.close()
            return jsonify({"status": "phone_limit"})

        # insert
        cur.execute("""
        INSERT INTO players
        (application_id,firstname,middlename,lastname,email,phone,dob,age,state,sport,photo)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """, (
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
            "status": "success",
            "application_id": application_id
        })

    except Exception as e:
        print("REGISTER ERROR:", e)
        return jsonify({"status": "error"})


# -----------------------------
# SAVE MATCH (NRR + REGION)
# -----------------------------
def convert_overs(overs):
    overs = str(overs)

    if "." in overs:
        o, balls = overs.split(".")
        return int(o) + (int(balls) / 6)
    
    return float(overs)


@app.route("/save_match", methods=["POST"])
def save_match():
    try:
        data = request.json

        teamA = data["teamA"]
        teamB = data["teamB"]

        stateA = data["stateA"]
        stateB = data["stateB"]

        runsA = float(data["runsA"])
        runsB = float(data["runsB"])
        try:
            oversA = convert_overs(data["oversA"])
            oversB = convert_overs(data["oversB"])
        except:
            return {"status": "error", "message": "Invalid overs format"}

        # ✅ Prevent crash
        if oversA == 0 or oversB == 0:
            return {"status": "error", "message": "Overs cannot be 0"}

        regionA = get_region(stateA)
        regionB = get_region(stateB)

        conn = connect_db()
        cur = conn.cursor()

        def update_team(name, region, runs_for, overs_for, runs_against, overs_against, win):

            cur.execute("SELECT * FROM teams WHERE name=?", (name,))
            team = cur.fetchone()

            if not team:
                cur.execute(
                    "INSERT INTO teams (name, region) VALUES (?,?)",
                    (name, region)
                )
                conn.commit()

                cur.execute("SELECT * FROM teams WHERE name=?", (name,))
                team = cur.fetchone()

            matches = team["matches"] + 1
            wins = team["wins"] + (1 if win else 0)
            loss = team["loss"] + (0 if win else 1)
            points = team["points"] + (2 if win else 0)

            nrr = (runs_for / overs_for) - (runs_against / overs_against)

            cur.execute("""
                UPDATE teams
                SET matches=?, wins=?, loss=?, points=?, nrr=nrr+?
                WHERE name=?
            """, (matches, wins, loss, points, nrr, name))

        # ✅ Match result
        if runsA > runsB:
            update_team(teamA, regionA, runsA, oversA, runsB, oversB, True)
            update_team(teamB, regionB, runsB, oversB, runsA, oversA, False)
        else:
            update_team(teamB, regionB, runsB, oversB, runsA, oversA, True)
            update_team(teamA, regionA, runsA, oversA, runsB, oversB, False)

        conn.commit()
        conn.close()

        return {"status": "success"}

    except Exception as e:   # 🔥 VERY IMPORTANT
        print("SAVE MATCH ERROR:", e)
        return {"status": "error", "message": str(e)}

# -----------------------------
# GET POINTS
# -----------------------------

@app.route("/get_points")
def get_points():
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT * FROM teams
        ORDER BY region, points DESC, nrr DESC
    """)

    teams = cur.fetchall()
    conn.close()

    return {"teams": [dict(t) for t in teams]}


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