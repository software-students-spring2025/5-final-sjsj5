from flask import Flask, render_template, request, redirect, url_for, session, flash
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongodb:27017")
client = MongoClient(MONGO_URI)

db = client["gameDB"]
users = db["users"]

#jime fix change for app 
@app.route('/')
def home():
    if 'username' in session:
        return f"Welcome {session['username']}! <a href='/logout'>Logout</a>" #welcome for each specific user
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if users.find_one({"username": username}): #no repeats 
            flash('Username already exists!', 'error')
        else:
            hashed_pw = generate_password_hash(password)
            users.insert_one({
                "username": username,
                "password": hashed_pw
            })
            return redirect(url_for('login')) #hodl

    return render_template('register.html', error=error)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = users.find_one({"username": username})
        if user and check_password_hash(user['password'], password):
            session['username'] = username
            return redirect(url_for('home'))

        flash('Invalid username or password', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))
#end session
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)