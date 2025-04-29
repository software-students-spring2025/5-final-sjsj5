import pytest
from app import app, BlackjackGame
from unittest.mock import patch, MagicMock

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.secret_key = 'test_secret'
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['username'] = 'testuser'  
        yield client

@patch('app.users')
def test_register_success(mock_users, client):
    mock_users.find_one.return_value = None  

    response = client.post('/register', data={
        'username': 'newuser',
        'password': 'newpassword'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Login' in response.data  
    mock_users.insert_one.assert_called_once()

@patch('app.users')
def test_register_existing_user(mock_users, client):
    mock_users.find_one.return_value = {'username': 'existinguser'}

    response = client.post('/register', data={
        'username': 'existinguser',
        'password': 'password'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Username already exists' in response.data

@patch('app.users')
def test_login_success(mock_users, client):
    from werkzeug.security import generate_password_hash
    hashed_pw = generate_password_hash('correctpassword')

    mock_users.find_one.return_value = {'username': 'testuser', 'password': hashed_pw}

    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'correctpassword'
    }, follow_redirects=True)

    assert response.status_code == 200

@patch('app.users')
def test_login_invalid_credentials(mock_users, client):
    mock_users.find_one.return_value = None 

    response = client.post('/login', data={
        'username': 'wronguser',
        'password': 'wrongpassword'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Login' in response.data

def test_logout(client):
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'Login' in response.data

def test_blackjack_redirect_if_not_logged_in():
    with app.test_client() as client:
        response = client.get('/blackjack', follow_redirects=True)
        assert b'Login' in response.data

def test_blackjack_deal_action(client):
    response = client.post('/blackjack', data={'action': 'deal'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Your Hand' in response.data or b'Hit' in response.data

def test_new_deck():
    deck = BlackjackGame.new_deck()
    assert len(deck) == 52
    assert all(card in BlackjackGame.ranks for card in deck)

def test_calculate_hand_no_ace():
    hand = ['10', '9']
    total = BlackjackGame.calculate_hand(hand)
    assert total == 19

def test_calculate_hand_with_ace():
    hand = ['A', '8']
    total = BlackjackGame.calculate_hand(hand)
    assert total == 19

def test_calculate_hand_multiple_aces():
    hand = ['A', 'A', '8']
    total = BlackjackGame.calculate_hand(hand)
    assert total == 20

def test_blackjack_hit_action(client):
    with client.session_transaction() as sess:
        sess['deck'] = ['10', '5', '2']
        sess['player_hand'] = ['3', '5']
    response = client.post('/blackjack', data={'action': 'hit'}, follow_redirects=True)
    assert response.status_code == 200

def test_blackjack_hit_bust(client):
    with client.session_transaction() as sess:
        sess['deck'] = ['K']
        sess['player_hand'] = ['10', '9']
    response = client.post('/blackjack', data={'action': 'hit'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Result' in response.data or b'Bust' in response.data

def test_blackjack_stand_action(client):
    with client.session_transaction() as sess:
        sess['deck'] = ['2', '3', '4']
        sess['player_hand'] = ['10', '7']
        sess['dealer_hand'] = ['8', '7']
    response = client.post('/blackjack', data={'action': 'stand'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Result' in response.data

def test_blackjack_result_redirect_if_no_game_state(client):
    response = client.get('/blackjack/result', follow_redirects=True)
    assert b'Login' not in response.data

def test_blackjack_result_player_bust(client):
    with client.session_transaction() as sess:
        sess['game_state'] = 'player_bust'
        sess['player_hand'] = ['10', '9', '5']
        sess['dealer_hand'] = ['10', '7']
    response = client.get('/blackjack/result')
    assert response.status_code == 200
