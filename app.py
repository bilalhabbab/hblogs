import datetime
from flask import Flask, render_template, request
from pymongo import MongoClient
import certifi
from urllib.parse import quote_plus

# Specify your username and password here
username = quote_plus("")
password = quote_plus("")

ca = certifi.where()

# Initialize MongoClient with the certifi CA certificate for secure connection
client = MongoClient(f"", tlsCAFile=ca)

app = Flask(__name__)

db = client.microblog

entries = []

@app.route("/", methods=["GET", "POST"])
def home():    
    if request.method == "POST":
        entry_content = request.form.get("content")
        formatted_date = datetime.datetime.today().strftime("%Y-%m-%d")
        
        entries.append((entry_content, formatted_date))
        
        db.entries.insert_one({"content": entry_content, "date": formatted_date})
    
    entries_with_date = [
        (
            entry[0], 
            entry[1], 
            datetime.datetime.strptime(entry[1], "%Y-%m-%d").strftime("%b %d")
        )
        for entry in entries
    ]

    return render_template("home.html", entries=entries_with_date)

@app.route("/source_code")
def source_code():
    return render_template("source_code.html")

if __name__ == '__main__':
    app.run(debug=True)  
