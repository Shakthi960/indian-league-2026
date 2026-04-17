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

    # ✅ TEAMS TABLE (NEW)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS teams(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        matches INTEGER DEFAULT 0,
        wins INTEGER DEFAULT 0,
        loss INTEGER DEFAULT 0,
        points INTEGER DEFAULT 0,
        nrr REAL DEFAULT 0
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

    cur.execute("SELECT id FROM players WHERE phone=?", (phone,))
    user = cur.fetchone()

    conn.close()

    if user:
        return {"status": "registered", "id": user["id"]}

    return {"status": "not_registered"}


# -----------------------------
# POINTS SYSTEM (NEW)
# -----------------------------

@app.route("/save_match", methods=["POST"])
def save_match():
    data = request.json

    teamA = data["teamA"]
    teamB = data["teamB"]
    runsA = float(data["runsA"])
    runsB = float(data["runsB"])
    oversA = float(data["oversA"])
    oversB = float(data["oversB"])

    conn = connect_db()
    cur = conn.cursor()

    def update_team(name, runs_for, overs_for, runs_against, overs_against, win):
        cur.execute("SELECT * FROM teams WHERE name=?", (name,))
        team = cur.fetchone()

        if not team:
            cur.execute("INSERT INTO teams (name) VALUES (?)", (name,))
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

    if runsA > runsB:
        update_team(teamA, runsA, oversA, runsB, oversB, True)
        update_team(teamB, runsB, oversB, runsA, oversA, False)
    else:
        update_team(teamB, runsB, oversB, runsA, oversA, True)
        update_team(teamA, runsA, oversA, runsB, oversB, False)

    conn.commit()
    conn.close()

    return {"status": "success"}


@app.route("/get_points")
def get_points():
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT * FROM teams
        ORDER BY points DESC, nrr DESC
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