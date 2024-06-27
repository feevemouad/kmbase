from flask import Blueprint, request, jsonify
import yaml
from Services.HashingService import HashingService
from Services.JWTService import JWTService
from models import db, Users

_hash = HashingService()
auth_bp = Blueprint('auth_bp', __name__)

with open("../secrets.yaml") as f:
    yaml_dict = yaml.safe_load(f)
    register_key = yaml_dict['register_key']
    jwt_secret = yaml_dict['jwt_secret']
    
jwt_service = JWTService(jwt_secret)

@auth_bp.route('/auth/login', methods=['POST'])
def log_in():
    username, password = request.json['username'], request.json['password']
    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400
    user = Users.query.filter_by(username=username).first()
    if user is None:
        # Username doesn't exist, but we don't inform the client to prevent username enumeration
        return jsonify({"error": "Incorrect username/password combination"}), 401
    is_password_correct = _hash.check_bcrypt(password, user.password_hash)
    if not is_password_correct:
        return jsonify({"error": "Incorrect username/password combination"}), 401
    
    token_payload = {"username": username, "user_id": user.id}
    token = jwt_service.generate(data = token_payload)

    if token is None:
        return jsonify({"error": "Login failed"}), 500

    return jsonify({"token": token}), 200


@auth_bp.route('/auth/register', methods=["POST"])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    email = data.get('email')
    role = data.get('role')

    # Check if all required fields are provided
    if not all([username, password, first_name, last_name, email, role]):
        return jsonify({"error": "All fields are required"}), 400

    # Check if the registration key is correct
    if request.headers.get("register_key") != register_key:
        return jsonify({"error": "Unauthorized registration attempt"}), 401

    # Check if the username already exists
    existing_user = Users.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({"error": "Username already exists"}), 409

    # Hash the password
    password_hash = _hash.hash_bcrypt(password)

    # Create new user
    new_user = Users(
        username=username,
        password_hash=password_hash,
        first_name=first_name,
        last_name=last_name,
        email=email,
        role=role
    )

    # Add and commit the new user to the database
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "User account created successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to create user account"}), 500

@auth_bp.route('auth/is_logged_in', methods=['GET'])
def is_logged_in():
    # If this controller is reached this means the
    # Auth middleware recognizes the passed token
    return jsonify({"message": "Token is valid"}), 201
