from flask import Flask
from pymongo import MongoClient
import os

app = Flask(__name__)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongodb:27017")
client = MongoClient(MONGO_URI)
db = client["gameDB"]
users = db["users"]

@app.route("/")
def home():
    return "Card Game Simulator is running! MongoDB connected."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)