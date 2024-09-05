from flask import Flask, render_template, request, redirect, session, make_response, url_for, flash
from pymongo import MongoClient
import certifi
from urllib.parse import quote_plus
import datetime
import pytz
import firebase_admin
from firebase_admin import credentials, auth
import requests

app = Flask(__name__)
app.secret_key = ''  

# Initialize Firebase Admin
cred = credentials.Certificate('')
firebase_admin.initialize_app(cred)

# MongoDB configuration
username = quote_plus("")
password = quote_plus("")
ca = certifi.where()
client = MongoClient(f"mongodb+srv://{'username'}:{'password'}@hblogs.ehja4vl.mongodb.net/", tlsCAFile=ca)
db = client.microblog



    
@app.route("/", methods=["GET", "POST"])
def home():
    if 'user_id' not in session:
        flash("You must be logged in to view this page.", category="error")
        return redirect(url_for("login"))
    
    if request.method == "POST":
        title = request.form.get("title")
        content = request.form.get("content")
        if title and content:
            formatted_datetime = datetime.datetime.now(pytz.utc).isoformat()
            db.entries.insert_one({"title": title, "content": content, "date": formatted_datetime})
        else:
            flash("Both title and content are required.", category="error")

    entries = list(db.entries.find().sort("date", -1))
    entries_with_date = [{
        'title': entry.get('title', 'No Title'),
        'content': entry['content'],
        'date': datetime.datetime.fromisoformat(entry['date']).strftime("%b %d"),
        'time': datetime.datetime.fromisoformat(entry['date']).strftime("%H:%M:%S")
    } for entry in entries]

    return render_template("home.html", entries=entries_with_date)


@app.after_request
def set_coop_header(response):
    response.headers['Cross-Origin-Opener-Policy'] = 'same-origin' 
    return response



@app.route("/verifyToken", methods=["POST"])
def verify_token():
    token = request.json.get('token')
    try:
        decoded_token = auth.verify_id_token(token)
        uid = decoded_token['uid']

        session['user_id'] = uid
        session['user_email'] = decoded_token['email']
        return {'status': 'success', 'uid': uid}, 200
    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 401
    


@app.route("/route")
def function():
    user_email = session.get('user_email', 'No Email')
    return render_template("your_template.html", user_email=user_email)



@app.route("/login", methods=["GET", "POST"])
def login():
    if 'user_id' in session:
        return redirect(url_for('home'))
    return render_template("login.html")



@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        try:
            user = auth.create_user(email=email, password=password)
            return redirect("/login")
        except firebase_admin.exceptions.FirebaseError as e:
            return render_template("register.html", error=str(e))
    return render_template("register.html")



@app.route("/logout")
def logout():
    session.clear()  # Clear the session
    return redirect(url_for('login'))

@app.route("/source_code/")
def source_code():
    return render_template("source_code.html")

@app.route("/recent/")
def recent():
    entries = list(db.entries.find().sort("date", -1))
    entries_with_date = [{
        'title': entry.get('title', 'No Title'),
        'content': entry['content'],
        'date': datetime.datetime.fromisoformat(entry['date']).strftime("%b %d"),
        'time': datetime.datetime.fromisoformat(entry['date']).strftime("%H:%M:%S")
    } for entry in entries]
    return render_template("recent.html", entries=entries_with_date)

if __name__ == '__main__':
    app.run(debug=True)
