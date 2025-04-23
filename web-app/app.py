from flask import Flask
from pymongo import MongoClient
import os

app = Flask(__name__)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongodb:27017")
client = MongoClient(MONGO_URI)
db = client["gameDB"]
users = db["users"]

# ROUTE
@app.route("/")
def home():
    return "Card Game Simulator is running! MongoDB connected."

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