from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from pymongo import MongoClient
import requests

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'super-secret'  # Replace this with a secret key
jwt = JWTManager(app)
bcrypt = Bcrypt(app)

client = MongoClient('mongodb://localhost:27017/')
db = client['crypto_tracker']
users = db['users']

@app.route('/register', methods=['POST'])
def register_user():
    username = request.json.get('username')
    password = request.json.get('password')
    balance = request.json.get('balance', 0)
    portfolio = request.json.get('portfolio', {})

    if not username or not password:
        return jsonify({'error': 'Missing username or password'}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    user = {'username': username, 'password': hashed_password, 'balance': balance, 'portfolio': portfolio}
    users.insert_one(user)

    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/login', methods=['POST'])
def login_user():
    username = request.json.get('username')
    password = request.json.get('password')

    if not username or not password:
        return jsonify({'error': 'Missing username or password'}), 400

    user = users.find_one({'username': username})

    if not user or not bcrypt.check_password_hash(user['password'], password):
        return jsonify({'error': 'Invalid username or password'}), 401

    access_token = create_access_token(identity=username)
    return jsonify({'access_token': access_token}), 200

@app.route('/prices', methods=['GET'])
def get_prices():
    response = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin%2Cethereum%2Clitecoin&vs_currencies=usd')
    prices = response.json()

    return jsonify(prices), 200

@app.route('/purchase', methods=['POST'])
@jwt_required()
def purchase_crypto():
    username = get_jwt_identity()
    user = users.find_one({'username': username})

    if not user:
        return jsonify({'error': 'User not found'}), 404

    coin = request.json.get('coin')
    quantity = request.json.get('quantity', 0)
    price = request.json.get('price', 0)

    if not coin or not quantity or not price:
        return jsonify({'error': 'Missing coin, quantity, or price'}), 400

    total_cost = quantity * price

    if user['balance'] < total_cost:
        return jsonify({'error': 'Insufficient funds'}), 400

    user['balance'] -= total_cost
    user['portfolio'][coin] = user['portfolio'].get(coin, 0) + quantity

    users.update_one({'username': username}, {'$set': {'balance': user['balance'], 'portfolio': user['portfolio']}})

    return jsonify({'message': 'Purchase successful'}), 200

@app.route('/portfolio', methods=['GET'])
@jwt_required()
def get_user_portfolio():
    username = get_jwt_identity()
    user = users.find_one({'username': username})

    if not user:
        return jsonify({'error': 'User not found'}), 404

    return jsonify({'portfolio': user['portfolio']}), 200

if __name__ == '__main__':
    app.run(debug=True)
