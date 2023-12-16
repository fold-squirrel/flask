from flask import Flask, session, jsonify, request
from flask_mail import Mail, Message

from database import *
from utils import *

from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

import os

from flask_bcrypt import Bcrypt

app = Flask(__name__)
bcrypt = Bcrypt(app)

app = Flask(__name__)
connection = create_sqlite_connection()

# Set the SECRET_KEY value in Flask application configuration settings.
app.config['SECRET_KEY'] = 'aedaed0ec5d5e92996c709064501944c670d86fa1ccc5ed2'

app.config['JWT_SECRET_KEY'] = 'aedaed0ec5d5e92996c709064501944c670d86fa1ccc5ed2'  # Replace with a strong, random secret key
jwt = JWTManager(app)

@app.route("/")
def hello_world():
    return "Hello, World!"


@app.route("/api/auth/signup", methods=["POST"])
def signup():
    data = request.get_json()
    customer = {
        "name": data.get("name"),
        "email": data.get("email"),
        "password": bcrypt.generate_password_hash(data.get("password")).decode("utf-8"),
        "gender": data.get("gender"),
        "birthdate": data.get("birthdate"),
    }

    if add_customer_to_db(customer):
        return jsonify({
                "status": 200,
                "msg": "success"
            })
    else:
        return jsonify({
                "status": 401,
                "msg": "failed"
            })

@app.route("/api/auth/signin", methods=["POST"])
def login():
    data = request.get_json()
    credentials = {
        "email": data.get("email"),
        "password": data.get("password"),
    }

    password_hash = get_password_hash(credentials)
    if bcrypt.check_password_hash(password_hash, credentials['password']):
        customer = get_user_data_from_db(credentials['email'])
        session['id'] = customer[0]
        session['email'] = customer[2]
        access_token = create_access_token(identity=customer[2])
        return jsonify({
                "status": 200,
                "msg": "success",
                "customer": {
                        "name": customer[1],
                        "email": customer[2],
                        "gender": customer[4],
                        "birthdate": customer[5]
                    },
                "token": access_token  
            })
    else:
        return jsonify({
                "status": 401,
                "msg": "failed"
            })

@app.route("/api/user/info", methods=["GET"])
@jwt_required()
def user_info():
    email = get_jwt_identity()
    customer = get_user_data_from_db(email)

    if customer:
        return jsonify({
                "status": 200,
                "msg": "success",
                "customer": {
                        "name": customer[1],
                        "email": customer[2],
                        "gender": customer[4],
                        "birthdate": customer[5]
                    }
            })
    else:
        return jsonify({
                "status": 401,
                "msg": "failed"
            })


@app.route("/api/product/search", methods=["POST"])
def get_products():
    data = request.get_json()
    name = data['name']

    products = search_products(name)
    print(products)
    return jsonify({
            "products": products,
            "status": 200,
            "msg": "success"
        })


@app.route("/api/auth/recover", methods=["POST"])
def send_recovery_email():
    data = request.get_json()
    email = data.get("email")

    token = create_reset_token(email)
    # send email !!!!!!!!!!!!!!!!!!!! 
    if token:
        return jsonify({
                "status": 200,
                "msg": "success",
            })
    else:
        return jsonify({
                "status": 401,
                "msg": "failed"
            })

@app.route("/api/auth/check_recovery_token", methods=["POST"])
def check_token():
    data = request.get_json()
    email = data.get("email")
    user_provided_recovery_token = data.get("recovery_token")

    recovery_token = get_customer_recovery_token(email)
    if recovery_token and recovery_token[1] == user_provided_recovery_token and is_within_3_hours(recovery_token[3]):
        session['change_password'] = True
        session['email'] = email
        delete_recovery_token(recovery_token[0])
        access_token = create_access_token(identity=email)
        return jsonify({
                "status": 200,
                "msg": "success",
                "token": access_token
            })
    else:
        return jsonify({
                "status": 401,
                "msg": "failed"
            })

@app.route("/api/auth/change_password", methods=["POST"])
@jwt_required()
def change_password():
    data = request.get_json()
    new_password = data.get("password")

    if session['email'] and session['change_password']:
        password_hash = bcrypt.generate_password_hash(data.get("password")).decode("utf-8")
        update_password(session['email'], password_hash)
        return jsonify({
                "status": 200,
                "msg": "success",
            })
    else:
        return jsonify({
                "status": 401,
                "msg": "failed"
            })

@app.route("/api/user/cart/add", methods=["POST"])
@jwt_required()
def add_to_cart():
    data = request.get_json()
    email = get_jwt_identity()
    
    quantity = get_product_quantity(data['product_id'])
    if data['quantity'] > 0 and quantity > data['quantity']:
        add_product_to_cart_items(email, data['product_id'], data['quantity'])
        return jsonify({
                "status": 200,
                "msg": "success",
            })
    else:
        return jsonify({
                "status": 401,
                "msg": "failed"
            })

if __name__ == "__main__":
    init_db(connection)
    app.run(debug=True)
