from flask import Flask, session, jsonify, request
from database import *

from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

import os

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
        "password": data.get("password").encode("utf-8"),
        "gender": data.get("gender"),
        "birthdate": data.get("birthdate"),
    }

    if add_customer_to_db(customer):
        return jsonify({
                "status": 200,
                "message": "success"
            })
    else:
        return jsonify({
                "status": 401,
                "message": "failed"
            })

@app.route("/api/auth/signin", methods=["POST"])
def login():
    data = request.get_json()
    credentials = {
        "email": data.get("email"),
        "password": data.get("password").encode("utf-8"),
    }

    if check_password(credentials):
        customer = get_user_data_from_db(credentials['email'])
        print(customer)
        session['id'] = customer[0]
        session['email'] = customer[2]
        access_token = create_access_token(identity=customer[2])
        return jsonify({
                "status": 200,
                "message": "success",
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
                "message": "failed"
            })


if __name__ == "__main__":
    init_db(connection)
    app.run(debug=True)

