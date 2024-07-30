from flask import Blueprint, request, jsonify
import yaml
from Services.HashingService import HashingService
from Services.JWTService import JWTService
from models import db, Users

_hash = HashingService()
auth_bp = Blueprint('auth_bp', __name__)

with open("../config/config.yaml") as f:
    yaml_dict = yaml.safe_load(f)
    jwt_secret = yaml_dict["jwt_service"]['jwt_secret']
    
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

@auth_bp.route('auth/is_logged_in', methods=['GET'])
def is_logged_in():
    # If this controller is reached this means the
    # Auth middleware recognizes the passed token
    return jsonify({"message": "Token is valid"}), 201
