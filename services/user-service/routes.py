from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
from db import users_collection
from models import User
from bson import ObjectId
import os
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

user_bp = Blueprint('user', __name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            if token.startswith("Bearer "):
                token = token.split("Bearer ")[1]


            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

            current_user = users_collection.find_one(
                {"_id": ObjectId(data["user_id"])})

            if not current_user:
                return jsonify({'message': 'Invalid token!'}), 401

        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)
    return decorated

@user_bp.route('/register', methods=['POST'])
def register():
    data = request.json

    if not data.get("email") or not data.get("password"):
        return jsonify({"error": "Email and password are required"}), 400

    if users_collection.find_one({"email": data["email"]}):
        return jsonify({"error": "User already exists"}), 400

    hashed_password = generate_password_hash(
        data["password"], method='pbkdf2:sha256')

    new_user = User(
        email=data["email"],
        password=hashed_password,
        created_at=datetime.datetime.utcnow().isoformat()
    )

    users_collection.insert_one(new_user.to_dict())

    return jsonify({"message": "User registered successfully!"}), 201

@user_bp.route('/login', methods=['POST'])
def login():
    data = request.json

    if not data.get("email") or not data.get("password"):
        return jsonify({"error": "Email and password are required"}), 400

    # Find user
    user = users_collection.find_one({"email": data["email"]})
    if not user or not check_password_hash(user["password"], data["password"]):
        return jsonify({"error": "Invalid email or password"}), 401

    token = jwt.encode({"user_id": str(user["_id"]), "exp": datetime.datetime.utcnow(
    ) + datetime.timedelta(hours=12)}, SECRET_KEY, algorithm="HS256")

    return jsonify({"message": "Login successful", "token": token}), 200

@user_bp.route('/profile', methods=['GET'])
@token_required
def profile(current_user):
    user_data = {
        "id": str(current_user["_id"]),
        "email": current_user["email"],
        "created_at": current_user["created_at"]
    }
    return jsonify(user_data), 200