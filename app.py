import datetime
from flask import Flask, render_template, request
from pymongo import MongoClient
import certifi

# Specify the CA certificate using certifi for SSL connection
ca = certifi.where()

# Initialize MongoClient with the certifi CA certificate for secure connection
client = MongoClient("", tlsCAFile=ca)

app = Flask(__name__)
# Ensure that we don't reinitialize MongoClient without certifi
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

# Run the app
if __name__ == '__main__':
    app.run()