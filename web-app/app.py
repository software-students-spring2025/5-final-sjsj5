from flask import Flask, render_template, request, redirect, url_for, session, flash
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
import os
import random

app = Flask(__name__)
app.secret_key = os.urandom(24)

# MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongodb:27017")
# client = MongoClient(MONGO_URI)

# db = client["gameDB"]
# users = db["users"]

#Jimenas Changes
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://jkm8294:password2121@jackblack.bfh9bb1.mongodb.net/gameDB?retryWrites=true&w=majority&appName=JackBlack")
client = MongoClient(MONGO_URI)
db = client['gameDB']
users = db["gameUser"]
#Jimenas Changes

#jime fix change for app 
@app.route('/')
def home():
    if 'username' in session:
        return f"Welcome {session['username']}! <a href='/logout'>Logout</a>" #welcome for each specific user
    return redirect(url_for('blackjack'))

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
            return redirect(url_for('blackjack'))

        flash('Invalid username or password', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

# Blackjack
class BlackjackGame:
    ranks = ('2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A')
    values = {'2':2, '3':3, '4':4, '5':5, '6':6, '7':7, '8':8, 
              '9':9, '10':10, 'J':10, 'Q':10, 'K':10, 'A':11}

    @staticmethod
    def new_deck():
        deck = [rank for rank in BlackjackGame.ranks for _ in range(4)]
        random.shuffle(deck)
        return deck

    @staticmethod
    def calculate_hand(hand):
        total = sum(BlackjackGame.values[card] for card in hand)
        aces = hand.count('A')
        while total > 21 and aces:
            total -= 10
            aces -= 1
        return total
    
@app.route('/blackjack', methods=['GET', 'POST'])
def blackjack():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'deal':
            session['deck'] = BlackjackGame.new_deck()
            session['player_hand'] = [session['deck'].pop(), session['deck'].pop()]
            session['dealer_hand'] = [session['deck'].pop(), session['deck'].pop()]
            session['game_state'] = 'playing'
            return redirect(url_for('blackjack'))
        
        elif action == 'hit':
            player_hand = session.get('player_hand', [])
            deck = session.get('deck', [])

            if deck:
                player_hand.append(deck.pop())
                session['player_hand'] = player_hand
                session['deck'] = deck

            if BlackjackGame.calculate_hand(player_hand) > 21:
                session['game_state'] = 'player_bust'
                return redirect(url_for('blackjack_result'))

            return redirect(url_for('blackjack'))

        elif action == 'stand':
            session['game_state'] = 'dealer_turn'
            return redirect(url_for('blackjack_result'))

    return render_template('blackjack.html',
                           game_state=session.get('game_state', 'start'),
                           player_hand=session.get('player_hand', []),
                           dealer_hand=session.get('dealer_hand', []),
                           player_total=BlackjackGame.calculate_hand(session.get('player_hand', [])),
                           dealer_total=BlackjackGame.calculate_hand(session.get('dealer_hand', []))
                               if session.get('game_state') != 'playing' else None)

@app.route('/blackjack/result') #new blakc jack result route 
def blackjack_result():
    if 'game_state' not in session:
        return redirect(url_for('blackjack'))

    player_hand = session.get('player_hand', [])
    dealer_hand = session.get('dealer_hand', [])

    player_total = BlackjackGame.calculate_hand(player_hand)
    dealer_total = BlackjackGame.calculate_hand(dealer_hand)

    if session['game_state'] == 'player_bust':
        session['result'] = 'player_bust'
        return render_template('result.html',
                               result=session['result'],
                               player_hand=player_hand,
                               dealer_hand=dealer_hand,
                               player_total=player_total,
                               dealer_total=dealer_total)

    if session['game_state'] == 'dealer_turn':
        while BlackjackGame.calculate_hand(dealer_hand) < 17:
            dealer_hand.append(session['deck'].pop())
        session['dealer_hand'] = dealer_hand 
        dealer_total = BlackjackGame.calculate_hand(dealer_hand)

        if dealer_total > 21:
            session['result'] = 'dealer_bust'
        elif player_total > dealer_total:
            session['result'] = 'player_win'
        elif player_total < dealer_total:
            session['result'] = 'dealer_win'
        else:
            session['result'] = 'push'

    return render_template('result.html',
                           result=session.get('result'),
                           player_hand=player_hand,
                           dealer_hand=dealer_hand,
                           player_total=player_total,
                           dealer_total=dealer_total)

#end session
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)