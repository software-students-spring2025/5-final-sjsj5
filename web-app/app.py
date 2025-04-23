from pymongo import MongoClient
from flask import Flask, render_template, request, redirect, url_for, flash, session

import os

app = Flask(__name__)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongodb:27017")
client = MongoClient(MONGO_URI)
db = client["gameDB"]
users = db["users"]

# ROUTES
@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username in users:
            error = "Username already exists"
        elif not username or not password:
            error = "Username or password left blank"
        else:
            users[username] = {"password": password}
            db.register_user(username, password)
            return redirect(url_for('login'))

    return render_template("register.html", error=error)

# FUNCTIONS
def get_users():
    client = MongoClient("mongodb://db:27017/")
    print("Connected to MongoDB successfully.")
    
    collect = client["gameDB"]["users"]
    dbUsers = collect.find()
    userDict = {}
    for u in dbUsers:
        userDict[u["username"]] = {"password": u["password"]}
    return userDict

def register_user(username, password):
    client = MongoClient("mongodb://db:27017/")
    print("Connected to MongoDB successfully.")
    
    collect = client["gameDB"]["users"]
    collect.insert_one({
        "username": username,
        "password": password
    })




if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)