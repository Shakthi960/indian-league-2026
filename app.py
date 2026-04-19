from flask import Flask, request, jsonify, send_file, render_template, redirect, session
import io
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import uuid
from supabase import create_client

app = Flask(__name__)
app.secret_key = "il4_secret_key"

# ✅ SUPABASE CONFIG
SUPABASE_URL = "https://djpxzczgkzsfcdohkagb.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRqcHh6Y3pna3pzZmNkb2hrYWdiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzY1Njg5NTYsImV4cCI6MjA5MjE0NDk1Nn0.iRLSdDBquFIrx6m0nMKh4_FKTN2ltbOWGlr55WkSqKA"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


@app.route("/points")
def points():
    return render_template("points.html")


# -----------------------------
# REGION LOGIC (UNCHANGED)
# -----------------------------
REGIONS = {
    "north": ["Jammu and Kashmir","Ladakh","Himachal Pradesh","Uttar Pradesh","Haryana","Delhi","Chandigarh"],
    "south": ["Tamil Nadu","Kerala","Karnataka","Andhra Pradesh","Telangana","Puducherry","Lakshadweep"],
    "east": ["West Bengal","Tripura","Mizoram","Nagaland","Sikkim","Andaman and Nicobar Islands","Assam"],
    "west": ["Rajasthan","Gujarat","Maharashtra","Goa","Dadra and Nagar Haveli and Daman and Daman and Diu","Madhya Pradesh","Chhattisgarh","Punjab"],
    "center": ["Jharkhand","Uttarakhand","Arunachal Pradesh","Manipur","Bihar","Odisha","Meghalaya"]
}

def get_region(state):
    for region, states in REGIONS.items():
        if state in states:
            return region
    return "unknown"


# -----------------------------
# PAGE ROUTES (UNCHANGED)
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
    res = supabase.table("players").select("*").eq("application_id", app_id).execute()
    if len(res.data) == 0:
        return "Invalid Application ID"
    return render_template("preview.html", user=res.data[0])


@app.route("/status")
def status():
    return render_template("status.html")

@app.route("/thankyou")
def thankyou():
    return render_template("thankyou.html")


# -----------------------------
# ADMIN LOGIN (UNCHANGED)
# -----------------------------
ADMIN_PASSWORD = "il4admin"

@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if request.form.get("password") == ADMIN_PASSWORD:
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
# REGISTER PLAYER (SUPABASE)
# -----------------------------
@app.route("/register", methods=["POST"])
def register():

    application_id = "IL4-" + str(uuid.uuid4())[:8].upper()

    try:
        data = request.json

        # duplicate check
        res = supabase.table("players").select("*")\
            .eq("firstname", data["firstname"])\
            .eq("lastname", data["lastname"])\
            .eq("phone", data["phone"])\
            .eq("state", data["state"])\
            .eq("sport", data["sport"])\
            .execute()

        if len(res.data) > 0:
            return jsonify({"status": "duplicate"})

        # insert
        supabase.table("players").insert({
            "application_id": application_id,
            "firstname": data.get("firstname"),
            "middlename": data.get("middlename"),
            "lastname": data.get("lastname"),
            "email": data.get("email"),
            "phone": data.get("phone"),
            "dob": data.get("dob"),
            "age": data.get("age"),
            "state": data.get("state"),
            "sport": data.get("sport"),
            "photo": data.get("photo")
        }).execute()

        return jsonify({
            "status": "success",
            "application_id": application_id
        })

    except Exception as e:
        print("REGISTER ERROR:", e)
        return jsonify({"status": "error"})

@app.route("/delete_team", methods=["POST"])
def delete_team():
    if not session.get("admin"):
        return {"status": "unauthorized"}

    try:
        data = request.json
        team_name = data["name"]

        supabase.table("teams").delete().eq("name", team_name).execute()

        return {"status": "success"}

    except Exception as e:
        print("DELETE ERROR:", e)
        return {"status": "error"}


# -----------------------------
# SAVE MATCH (SUPABASE)
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

        oversA = convert_overs(data["oversA"])
        oversB = convert_overs(data["oversB"])

        if oversA == 0 or oversB == 0:
            return {"status": "error"}

        regionA = get_region(stateA)
        regionB = get_region(stateB)

        def update_team(name, region, runs_for, overs_for, runs_against, overs_against, win):

            res = supabase.table("teams").select("*").eq("name", name).execute()

            if len(res.data) == 0:
                supabase.table("teams").insert({
                    "name": name,
                    "region": region,
                    "matches": 0,
                    "wins": 0,
                    "loss": 0,
                    "points": 0,
                    "nrr": 0
                }).execute()

                res = supabase.table("teams").select("*").eq("name", name).execute()

            team = res.data[0]

            supabase.table("teams").update({
                "matches": team["matches"] + 1,
                "wins": team["wins"] + (1 if win else 0),
                "loss": team["loss"] + (0 if win else 1),
                "points": team["points"] + (2 if win else 0),
                "nrr": team["nrr"] + ((runs_for/overs_for) - (runs_against/overs_against))
            }).eq("name", name).execute()

        if runsA > runsB:
            update_team(teamA, regionA, runsA, oversA, runsB, oversB, True)
            update_team(teamB, regionB, runsB, oversB, runsA, oversA, False)
        else:
            update_team(teamB, regionB, runsB, oversB, runsA, oversA, True)
            update_team(teamA, regionA, runsA, oversA, runsB, oversB, False)

        return {"status": "success"}

    except Exception as e:
        print("SAVE MATCH ERROR:", e)
        return {"status": "error"}


# -----------------------------
# GET POINTS (SUPABASE)
# -----------------------------
@app.route("/get_points")
def get_points():
    res = supabase.table("teams").select("*").execute()
    return {"teams": res.data}


# -----------------------------
# ADMIN API (SUPABASE)
# -----------------------------
@app.route("/get_players")
def get_players():

    if not session.get("admin"):
        return {"players": []}

    res = supabase.table("players")\
        .select("id, firstname, lastname, phone, state, sport")\
        .order("id", desc=True)\
        .execute()

    data = []
    for p in res.data:
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